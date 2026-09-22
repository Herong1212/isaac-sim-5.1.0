__copyright__ = "Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

from omni.scene.optimizer.core import ExecutionContext
from pxr import Sdf, UsdUtils

from .test_utils import Test_Operation

# Default arguments for the command
DEFAULT_ARGS = {
    "meshPrimPaths": [],
    "tolerance": 0.001,
}


class Test_Command_Find_Coinciding_Meshes(Test_Operation):

    OPERATION = "findCoincidingMeshes"

    async def test_basic_result(self):
        """Check that the return result matches expectation"""
        # Open the stage and get all the prims
        stage = self._open_stage("coinciding_meshes.usda")

        context = ExecutionContext()
        context.usdStageId = UsdUtils.StageCache().Get().Insert(stage).ToLongInt()
        context.generateReport = 1

        # Execute the command and assert success
        args = DEFAULT_ARGS.copy()
        args["tolerance"] = 0.5
        success, opResult = self._execute_command(args, context)

        self.assertTrue(success)

        result = opResult[2]

        # With we should have a single set of coinciding prims
        self.assertEqual(len(result), 1)

        # Ensure that the currently expected cases are covered.
        expected = [
            Sdf.Path("/World/CoincidingMesh1"),
            Sdf.Path("/World/CoincidingMesh2"),
            Sdf.Path("/World/CoincidingMesh3DiffNormals"),
        ]
        returned = result[0]
        self.assertEqual(expected, returned)

        # We expect Meshes that have coinciding points but different normals to be considered coincidental.
        self.assertIn(Sdf.Path("/World/CoincidingMesh3DiffNormals"), returned)

        # Increasing the tolerance value should result in meshes whos points are within that distance being considered
        # conincidental. In this case an identical Mesh with a transform of 1.0 is returned that was not before.
        args["tolerance"] = 1.0
        success, opResult = self._execute_command(args)
        self.assertTrue(success)

        result = opResult[2]

        # Ensure that the currently expected cases are covered.
        expected = [
            Sdf.Path("/World/CoincidingMesh1"),
            Sdf.Path("/World/CoincidingMesh2"),
            Sdf.Path("/World/CoincidingMesh3DiffNormals"),
            Sdf.Path("/World/NotCoinciding"),
        ]
        returned = result[0]
        self.assertEqual(expected, returned)

        # Test with a recursive path
        args["meshPrimPaths"] = ["/World//"]

        success, opResult = self._execute_command(args)
        self.assertTrue(success)

        result = opResult[2]

        # Ensure that the currently expected cases are covered.
        # Same as above, but a different order from resolving
        expected = [
            Sdf.Path("/World/NotCoinciding"),
            Sdf.Path("/World/CoincidingMesh3DiffNormals"),
            Sdf.Path("/World/CoincidingMesh2"),
            Sdf.Path("/World/CoincidingMesh1"),
        ]
        returned = result[0]
        self.assertEqual(expected, returned)

    async def test_time_varying_meshes(self):
        """Test coincident meshes operation on meshes with authored time varying attributes"""
        # Get a copy of the default arguments for this command
        args = DEFAULT_ARGS.copy()
        # Open the stage
        stage = self._open_stage("time_varying_meshes.usd")
        # run command
        success, result = self._execute_command(args)

        # asserts success of execution
        self.assertTrue(success)
