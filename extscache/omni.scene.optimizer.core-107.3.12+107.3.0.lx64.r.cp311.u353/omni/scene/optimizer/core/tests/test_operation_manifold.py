__copyright__ = "Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""


from pxr import UsdGeom

from .test_utils import Test_Operation

DEFAULT_ARGS = {
    "paths": [],
}


def _get_meshes(stage):
    return [x for x in stage.TraverseAll() if x.IsA(UsdGeom.Mesh)]


class Test_Operation_Manifold(Test_Operation):

    OPERATION = "manifoldMeshes"

    async def test_manifold_host(self):
        """Test manifold"""
        stage = self._open_stage("two-cubes-nonmanifold.usda")
        mesh_prims = _get_meshes(stage)
        self.assertEqual(len(mesh_prims), 1)

        old_face_counts = []
        old_vertex_counts = []
        for prim in mesh_prims:
            mesh = UsdGeom.Mesh(prim)
            old_face_counts.append(len(mesh.GetFaceVertexCountsAttr().Get()))
            old_vertex_counts.append(len(mesh.GetPointsAttr().Get()))

        args = DEFAULT_ARGS.copy()
        success, result = self._execute_command(args)

        # The operation should execute successfully.
        self.assertTrue(success)

        # Assert that the manifold op has taken place
        for i, prim in enumerate(mesh_prims):
            mesh = UsdGeom.Mesh(prim)
            self.assertEqual(old_face_counts[i], len(mesh.GetFaceVertexCountsAttr().Get()))
            self.assertLess(old_vertex_counts[i], len(mesh.GetPointsAttr().Get()))
