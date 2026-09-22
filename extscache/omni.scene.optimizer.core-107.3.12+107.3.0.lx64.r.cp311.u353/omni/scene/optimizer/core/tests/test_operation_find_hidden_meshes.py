__copyright__ = "Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

from pxr import UsdGeom

from .test_utils import Test_Operation, _get_test_data_file_path

# Default arguments for the command
DEFAULT_ARGS = {
    "paths": [],
    "gridResolution": 20.0,
    "action": 2,  # set custom bool attribute "hidden"
    "useGpu": False,
}


class Test_Operation_FindHiddenMeshes(Test_Operation):

    OPERATION = "findHiddenMeshes"

    async def test_find_hidden_meshes(self):
        """Test find hidden meshes"""

        for testCase in range(2):

            args = None

            if testCase == 0:

                args = {
                    "paths": [],
                    "gridResolution": 20.0,
                    "action": 2,  # set custom bool attribute "hidden"
                    "useGpu": False,
                }

            elif testCase == 1:

                args = {
                    "paths": [],
                    "gridResolution": 20.0,
                    "action": 2,  # set custom bool attribute "hidden"
                    "useGpu": True,
                }

            stage = self._open_stage("hiddenMesh.usda")

            # run the command

            success, result = self._execute_command(args)

            self.assertTrue(success)

            # check whether all meshes have a hidden attribute
            # with the expected value

            for prim in stage.TraverseAll():
                if prim.IsA(UsdGeom.Mesh):

                    attrHidden = prim.GetAttribute("hidden")
                    self.assertTrue(attrHidden)

                    if attrHidden:
                        # if hidden is contained in the path, the mesh should be hidden

                        should_be_hidden = "hidden" in prim.GetPath().pathString
                        self.assertTrue(attrHidden.Get() == should_be_hidden)

    async def test_time_varying_meshes(self):
        """Test find hidden meshes operation on meshes with authored time varying attributes"""
        # Get a copy of the default arguments for this command
        args = DEFAULT_ARGS.copy()
        # Open the stage
        stage = self._open_stage("time_varying_meshes.usd")
        # run command
        success, result = self._execute_command(args)

        # asserts success of execution
        self.assertTrue(success)
