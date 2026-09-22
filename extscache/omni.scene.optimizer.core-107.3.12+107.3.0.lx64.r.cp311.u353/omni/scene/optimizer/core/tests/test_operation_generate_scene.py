__copyright__ = "Copyright (c) 2022-2025, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

import math

from omni.scene.optimizer.core import ExecutionContext
from pxr import UsdGeom, UsdUtils

from .test_utils import Test_Operation

# Default arguments for the command
DEFAULT_ARGS = {
    "seed": 12345,
    "referenceMeshPaths": ["/referenceGeo"],
    "generatedMeshPath": "/World/mesh",
    "meshCount": 32,
    "uniformLayout": False,
    "2DLayout": False,
    "layoutSpacing": 12.0,
    "uniqueMeshPercentage": 0.75,
    "scaleUniqueMeshes": True,
    "clusteredPercent": 0.75,
    "numClusters": 4,
    "materialPaths": ["/Looks"],
}


def _get_meshes(stage):
    """Return all meshes in the stage"""
    return [x for x in stage.TraverseAll() if x.IsA(UsdGeom.Mesh)]


def _get_worldspace_points(prim, xformCache):
    """Returns points in worldspace"""
    # Get the points and local to world transform matrix.
    points = UsdGeom.PointBased(prim).GetPointsAttr().Get()
    matrix = xformCache.GetLocalToWorldTransform(prim)

    # Return the points with the matrix applied.
    return [matrix.Transform(x) for x in points]


class Test_Operation_Generate_Scene(Test_Operation):

    OPERATION = "generateScene"

    async def test_generate_scene_unclustered(self):
        """Tests generating a scene with geometry that is not clustered"""

        stage = self._open_stage("generateSceneSimple.usda")

        # setup args
        args = DEFAULT_ARGS.copy()
        args["clusteredPercent"] = 0.0
        args["numClusters"] = 0

        # Custom execution context
        context = ExecutionContext()
        context.usdStageId = UsdUtils.StageCache().Get().Insert(stage).ToLongInt()

        # Verify there are 3 original mesh
        meshes = _get_meshes(stage)
        self.assertEqual(len(meshes), 3)

        # Run the operation
        self._execute_command(args, context)

        # Verify that an additional 32 meshes have been produced
        meshes = _get_meshes(stage)
        self.assertEqual(len(meshes), 35)
        # note: we could check the geometry itself, but this is challenging since its randomly produced and probably not
        #       super important since this op is intended to be a developer tool

    async def test_generate_scene_clustered(self):
        """Tests a generating a scene with geometry that is clustered"""

        stage = self._open_stage("generateSceneSimple.usda")

        # setup args
        args = DEFAULT_ARGS.copy()

        # Custom execution context
        context = ExecutionContext()
        context.usdStageId = UsdUtils.StageCache().Get().Insert(stage).ToLongInt()

        # Run the operation
        self._execute_command(args, context)

        # hard to test: but ensure there are more than the original number of meshes (3) but less than one mesh per
        # disjoint geometry (35)
        meshes = _get_meshes(stage)
        self.assertGreater(len(meshes), 3)
        self.assertLess(len(meshes), 35)

    async def test_generate_scene_seed(self):
        """Tests that running the op with the same seed produces the same scene"""
        args = DEFAULT_ARGS.copy()
        args["clusteredPercent"] = 0.0
        args["numClusters"] = 0

        xformCache = UsdGeom.XformCache()

        # Run the operation the first time
        stage1 = self._open_stage("generateSceneSimple.usda")
        context = ExecutionContext()
        context.usdStageId = UsdUtils.StageCache().Get().Insert(stage1).ToLongInt()
        self._execute_command(args, context)
        mesh_points1 = [_get_worldspace_points(m, xformCache) for m in _get_meshes(stage1)]

        # Run the operation the second time
        stage2 = self._open_stage("generateSceneSimple.usda")
        context = ExecutionContext()
        context.usdStageId = UsdUtils.StageCache().Get().Insert(stage2).ToLongInt()
        self._execute_command(args, context)
        mesh_points2 = [_get_worldspace_points(m, xformCache) for m in _get_meshes(stage2)]

        # same number of meshes
        self.assertEqual(len(mesh_points1), len(mesh_points2))
        # check meshes are the same
        for points1, points2 in zip(mesh_points1, mesh_points2):
            for a, b in zip(points1, points2):
                for i in range(3):
                    self.assertAlmostEqual(a[i], b[i], places=4)

        # Run the operation a third time but with a different seed
        stage3 = self._open_stage("generateSceneSimple.usda")
        args["seed"] = 54321
        context = ExecutionContext()
        context.usdStageId = UsdUtils.StageCache().Get().Insert(stage3).ToLongInt()
        self._execute_command(args, context)
        mesh_points3 = [_get_worldspace_points(m, xformCache) for m in _get_meshes(stage3)]

        # still expect the same number of meshes after changing the seed (since clustering is off)
        self.assertEqual(len(mesh_points1), len(mesh_points3))
        # but expect at least one of the mesh geometries to be different
        geo_different = False
        for points1, points2 in zip(mesh_points1, mesh_points3):
            for a, b in zip(points1, points2):
                for i in range(3):
                    if not math.isclose(a[i], b[i]):
                        geo_different = True
        # fail if geometry was not different
        self.assertTrue(geo_different)
