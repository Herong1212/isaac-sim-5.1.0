__copyright__ = "Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

import filecmp
import os
import platform

from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade, UsdUtils, Vt

from .test_utils import Test_Operation, _get_test_data_file_path

DEFAULT_ARGS = {
    "paths": [],
    "gradation": 0,
    "maxError": 0.1,
    "gpuVertexCountThreshold": 500000,
}


def _get_meshes(stage):
    return [x for x in stage.TraverseAll() if x.IsA(UsdGeom.Mesh)]


class Test_Operation_RemeshMeshes(Test_Operation):

    OPERATION = "remeshMeshes"
    WRITE_TEST_RESULTS = False

    async def test_remesh(self):
        """Test remesh function"""
        stage = self._open_stage("simpleCube.usda")
        before_meshes = _get_meshes(stage)
        self.assertEqual(len(before_meshes), 1)

        old_face_counts = []
        old_corner_counts = []
        old_vertex_counts = []
        for prim in before_meshes:
            mesh = UsdGeom.Mesh(prim)
            old_face_counts.append(len(mesh.GetFaceVertexCountsAttr().Get()))
            old_corner_counts.append(len(mesh.GetFaceVertexIndicesAttr().Get()))
            old_vertex_counts.append(len(mesh.GetPointsAttr().Get()))

        args = DEFAULT_ARGS.copy()
        args["gradation"] = 0.1
        success, result = self._execute_command(args)

        # The operation should execute successfully.
        self.assertTrue(success)

        # Assert that the mesh reduction has taken place
        for i in range(0, len(before_meshes)):
            mesh = UsdGeom.Mesh(before_meshes[i])
            self.assertLess(old_face_counts[i], len(mesh.GetFaceVertexCountsAttr().Get()))
            self.assertLess(old_corner_counts[i], len(mesh.GetFaceVertexIndicesAttr().Get()))
            self.assertLess(old_vertex_counts[i], len(mesh.GetPointsAttr().Get()))

    async def test_remesh_gpu(self):
        """Test remesh function"""
        stage = self._open_stage("simpleCube.usda")
        before_meshes = _get_meshes(stage)
        self.assertEqual(len(before_meshes), 1)

        mesh = UsdGeom.Mesh(prim=stage.GetPrimAtPath("/World/Cube"))
        self.assertEqual(len(mesh.GetFaceVertexCountsAttr().Get()), 6)
        self.assertEqual(len(mesh.GetFaceVertexIndicesAttr().Get()), 24)
        self.assertEqual(len(mesh.GetPointsAttr().Get()), 8)

        # Execute operation, on CPU
        args = DEFAULT_ARGS.copy()
        args["gradation"] = 0.1
        success, result = self._execute_command(args)

        # The operation should execute successfully.
        self.assertTrue(success)

        # Assert remeshed values
        if platform.machine() == "aarch64":
            self.assertEqual(len(mesh.GetFaceVertexCountsAttr().Get()), 1032)
            self.assertEqual(len(mesh.GetFaceVertexIndicesAttr().Get()), 3096)
            self.assertEqual(len(mesh.GetPointsAttr().Get()), 518)
        else:
            self.assertEqual(len(mesh.GetFaceVertexCountsAttr().Get()), 1024)
            self.assertEqual(len(mesh.GetFaceVertexIndicesAttr().Get()), 3072)
            self.assertEqual(len(mesh.GetPointsAttr().Get()), 514)

        # reopen stage
        stage = self._open_stage("simpleCube.usda")

        # execute on GPU
        args["gpuVertexCountThreshold"] = 0
        success, result = self._execute_command(args)

        # The operation should execute successfully.
        self.assertTrue(success)

        mesh = UsdGeom.Mesh(prim=stage.GetPrimAtPath("/World/Cube"))

        # Assert remeshed values
        self.assertEqual(len(mesh.GetFaceVertexCountsAttr().Get()), 1024)
        self.assertEqual(len(mesh.GetFaceVertexIndicesAttr().Get()), 3072)
        self.assertEqual(len(mesh.GetPointsAttr().Get()), 514)
