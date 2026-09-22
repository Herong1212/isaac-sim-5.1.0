__copyright__ = "Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

import os

from omni.scene.optimizer.core import ExecutionContext
from pxr import Usd, UsdGeom, UsdUtils

from .test_utils import Test_Operation, _get_test_data_file_path

DEFAULT_ARGS = {
    "paths": [],
    "binding": 0,
    "replaceExisting": True,
    "weightMode": 0,
    "sharpnessAngle": 60.0,
    "gpuThreshold": 500000,
}


def _get_meshes(stage):
    return [x for x in stage.TraverseAll() if x.IsA(UsdGeom.Mesh)]


class Test_Operation_Generate_Normals(Test_Operation):

    OPERATION = "generateNormals"

    async def test_generate_corner_normals(self):
        """Test generate corner normals"""
        stage = self._open_stage("normalsTest.usda")
        mesh_prims = _get_meshes(stage)
        self.assertEqual(len(mesh_prims), 2)

        old_name = []
        old_interpolation = []
        for i, prim in enumerate(mesh_prims):
            mesh = UsdGeom.Mesh(prim)
            normals_attr = mesh.GetNormalsAttr()
            primvar = UsdGeom.Primvar(prim.GetAttribute("primvars:normals"))
            if primvar:
                old_name.append("primvars:normals")
                old_interpolation.append(primvar.GetInterpolation())
            elif prim.GetAttibute("normals"):
                old_name.append("normals")
                old_interpolation.append(mesh.GetNormalsInterpolation())
            else:
                old_name(None)
                old_interpolation.append(None)

        context = ExecutionContext()
        context.usdStageId = UsdUtils.StageCache().Get().Insert(stage).ToLongInt()

        # Execute the command and assert success
        args = DEFAULT_ARGS.copy()
        success, result = self._execute_command(args, context)
        self.assertTrue(success)

        expected_interpolation = UsdGeom.Tokens.faceVarying

        for i, prim in enumerate(mesh_prims):
            mesh = UsdGeom.Mesh(prim)
            normals_attr = mesh.GetNormalsAttr()
            primvar = UsdGeom.Primvar(prim.GetAttribute("primvars:normals"))
            if primvar:
                self.assertEqual(old_name[i], "primvars:normals")
                interpolation = primvar.GetInterpolation()
                normals = primvar.Get()
                if primvar.IsIndexed():
                    normals_len = len(primvar.GetIndicesAttr().Get())
                else:
                    normals_len = len(normals)
            elif normals_attr:
                self.assertEqual(old_name[i], "normals")
                interpolation = mesh.GetNormalsInterpolation()
                normals_len = len(normals_attr.Get())
            else:
                self.fail("Expected either normals or primvars:normals")
            self.assertEqual(interpolation, expected_interpolation)
            self.assertEqual(normals_len, len(mesh.GetFaceVertexIndicesAttr().Get()))

    async def test_generate_face_normals(self):
        stage = self._open_stage("normalsTest.usda")
        mesh_prims = _get_meshes(stage)
        self.assertEqual(len(mesh_prims), 2)

        old_name = []
        old_interpolation = []
        for i, prim in enumerate(mesh_prims):
            mesh = UsdGeom.Mesh(prim)
            normals_attr = mesh.GetNormalsAttr()
            primvar = UsdGeom.Primvar(prim.GetAttribute("primvars:normals"))
            if primvar:
                old_name.append("primvars:normals")
                old_interpolation.append(primvar.GetInterpolation())
            elif prim.GetAttibute("normals"):
                old_name.append("normals")
                old_interpolation.append(mesh.GetNormalsInterpolation())
            else:
                old_name(None)
                old_interpolation.append(None)

        context = ExecutionContext()
        context.usdStageId = UsdUtils.StageCache().Get().Insert(stage).ToLongInt()

        # Execute the command and assert success
        args = DEFAULT_ARGS.copy()
        args["binding"] = 1
        success, result = self._execute_command(args, context)
        self.assertTrue(success)

        expected_interpolation = UsdGeom.Tokens.uniform

        for i, prim in enumerate(mesh_prims):
            mesh = UsdGeom.Mesh(prim)
            normals_attr = mesh.GetNormalsAttr()
            primvar = UsdGeom.Primvar(prim.GetAttribute("primvars:normals"))
            if primvar:
                self.assertEqual(old_name[i], "primvars:normals")
                interpolation = primvar.GetInterpolation()
                normals = primvar.Get()
                if primvar.IsIndexed():
                    normals_len = len(primvar.GetIndicesAttr().Get())
                else:
                    normals_len = len(normals)
            elif normals_attr:
                self.assertEqual(old_name[i], "normals")
                interpolation = mesh.GetNormalsInterpolation()
                normals_len = len(normals_attr.Get())
            else:
                self.fail("Expected either normals or primvars:normals")
            self.assertEqual(interpolation, expected_interpolation)
            self.assertEqual(normals_len, len(mesh.GetFaceVertexCountsAttr().Get()))

    async def test_generate_vertex_normals(self):
        stage = self._open_stage("normals_options.usda")
        mesh_prims = _get_meshes(stage)
        self.assertEqual(len(mesh_prims), 10)

        old_name = []
        old_interpolation = []
        for i, prim in enumerate(mesh_prims):
            mesh = UsdGeom.Mesh(prim)
            normals_attr = mesh.GetNormalsAttr()
            primvar = UsdGeom.Primvar(prim.GetAttribute("primvars:normals"))
            if primvar:
                old_name.append("primvars:normals")
                old_interpolation.append(primvar.GetInterpolation())
            elif normals_attr.IsAuthored():
                old_name.append("normals")
                old_interpolation.append(mesh.GetNormalsInterpolation())
            else:
                old_name.append(None)
                old_interpolation.append(None)

        context = ExecutionContext()
        context.usdStageId = UsdUtils.StageCache().Get().Insert(stage).ToLongInt()

        # Execute the command and assert success
        args = DEFAULT_ARGS.copy()
        args["binding"] = 2
        success, result = self._execute_command(args, context)
        self.assertTrue(success)

        expected_interpolation = UsdGeom.Tokens.varying

        for i, prim in enumerate(mesh_prims):
            mesh = UsdGeom.Mesh(prim)
            normals_attr = mesh.GetNormalsAttr()
            primvar = UsdGeom.Primvar(prim.GetAttribute("primvars:normals"))
            if primvar:
                if old_name[i] is not None:
                    self.assertEqual(old_name[i], "primvars:normals")
                interpolation = primvar.GetInterpolation()
                if primvar.IsIndexed():
                    normals_len = len(primvar.GetIndicesAttr().Get())
                else:
                    normals_len = len(primvar.Get())
            elif normals_attr:
                self.assertEqual(old_name[i], "normals")
                interpolation = mesh.GetNormalsInterpolation()
                normals_len = len(normals_attr.Get())
            else:
                self.fail("Expected either normals or primvars:normals")
            self.assertEqual(interpolation, expected_interpolation)
            self.assertEqual(normals_len, len(mesh.GetPointsAttr().Get()))

    async def test_generate_vertex_normals_no_replace(self):
        stage = self._open_stage("normals_options.usda")
        mesh_prims = _get_meshes(stage)
        self.assertEqual(len(mesh_prims), 10)

        old_name = []
        old_size = []
        old_interpolation = []
        for i, prim in enumerate(mesh_prims):
            mesh = UsdGeom.Mesh(prim)
            normals_attr = mesh.GetNormalsAttr()
            primvar = UsdGeom.Primvar(prim.GetAttribute("primvars:normals"))
            if primvar:
                old_name.append("primvars:normals")
                old_interpolation.append(primvar.GetInterpolation())
                if primvar.IsIndexed():
                    old_size.append(len(primvar.GetIndicesAttr().Get()))
                else:
                    old_size.append(len(primvar.Get()))
            elif normals_attr.IsAuthored():
                old_name.append("normals")
                normals_attr_values = normals_attr.Get()
                old_interpolation.append(mesh.GetNormalsInterpolation())
                if normals_attr_values:
                    old_size.append(len(normals_attr_values))
                else:
                    old_size.append(0)
            else:
                old_name.append(None)
                old_interpolation.append(None)
                old_size.append(0)

        context = ExecutionContext()
        context.usdStageId = UsdUtils.StageCache().Get().Insert(stage).ToLongInt()

        expected_interpolation = UsdGeom.Tokens.varying

        # Execute the command and assert success
        args = DEFAULT_ARGS.copy()
        args["binding"] = 2
        args["replaceExisting"] = False
        success, result = self._execute_command(args, context)
        self.assertTrue(success)

        for i, prim in enumerate(mesh_prims):
            mesh = UsdGeom.Mesh(prim)
            normals_attr = mesh.GetNormalsAttr()
            primvar = UsdGeom.Primvar(prim.GetAttribute("primvars:normals"))
            if primvar:
                if old_name[i] is not None:
                    self.assertEqual(old_name[i], "primvars:normals")
                interpolation = primvar.GetInterpolation()
                if primvar.IsIndexed():
                    size = len(primvar.GetIndicesAttr().Get())
                else:
                    size = len(primvar.Get())
                if old_name[i] is None:
                    self.assertEqual(size, len(mesh.GetPointsAttr().Get()))
                    self.assertEqual(interpolation, expected_interpolation)
                else:
                    self.assertEqual(old_size[i], size)
                    self.assertEqual(old_interpolation[i], interpolation)
            elif normals_attr:
                self.assertEqual(old_name[i], "normals")
                normals_attr_values = normals_attr.Get()
                interpolation = mesh.GetNormalsInterpolation()
                size = len(normals_attr_values)
                self.assertEqual(old_size[i], size)
                self.assertEqual(old_interpolation[i], interpolation)
            else:
                self.fail("Expected either normals or primvars:normals")

    async def test_generate_corner_normals_gpu(self):
        stage = self._open_stage("normals_options.usda")
        mesh_prims = _get_meshes(stage)
        self.assertEqual(len(mesh_prims), 10)

        old_name = []
        old_size = []
        old_interpolation = []
        for i, prim in enumerate(mesh_prims):
            mesh = UsdGeom.Mesh(prim)
            normals_attr = mesh.GetNormalsAttr()
            primvar = UsdGeom.Primvar(prim.GetAttribute("primvars:normals"))
            if primvar:
                old_name.append("primvars:normals")
                old_interpolation.append(primvar.GetInterpolation())
                if primvar.IsIndexed():
                    old_size.append(len(primvar.GetIndicesAttr().Get()))
                else:
                    old_size.append(len(primvar.Get()))
            elif normals_attr.IsAuthored():
                old_name.append("normals")
                normals_attr_values = normals_attr.Get()
                old_interpolation.append(mesh.GetNormalsInterpolation())
                if normals_attr_values:
                    old_size.append(len(normals_attr_values))
                else:
                    old_size.append(0)
            else:
                old_name.append(None)
                old_interpolation.append(None)
                old_size.append(0)

        context = ExecutionContext()
        context.usdStageId = UsdUtils.StageCache().Get().Insert(stage).ToLongInt()

        expected_interpolation = UsdGeom.Tokens.faceVarying

        # Execute the command and assert success
        args = DEFAULT_ARGS.copy()
        args["binding"] = 0
        args["gpuThreshold"] = 0
        success, result = self._execute_command(args, context)
        self.assertTrue(success)

        for i, prim in enumerate(mesh_prims):
            mesh = UsdGeom.Mesh(prim)
            normals_attr = mesh.GetNormalsAttr()
            primvar = UsdGeom.Primvar(prim.GetAttribute("primvars:normals"))
            if primvar:
                if old_name[i] is not None:
                    self.assertEqual(old_name[i], "primvars:normals")
                interpolation = primvar.GetInterpolation()
                if primvar.IsIndexed():
                    size = len(primvar.GetIndicesAttr().Get())
                else:
                    size = len(primvar.Get())
                self.assertEqual(size, len(mesh.GetFaceVertexIndicesAttr().Get()))
                self.assertEqual(interpolation, expected_interpolation)
            elif normals_attr:
                self.assertEqual(old_name[i], "normals")
                normals_attr_values = normals_attr.Get()
                interpolation = mesh.GetNormalsInterpolation()
                size = len(normals_attr_values)
                self.assertEqual(size, len(mesh.GetFaceVertexIndicesAttr().Get()))
                self.assertEqual(interpolation, expected_interpolation)
            else:
                self.fail("Expected either normals or primvars:normals")
