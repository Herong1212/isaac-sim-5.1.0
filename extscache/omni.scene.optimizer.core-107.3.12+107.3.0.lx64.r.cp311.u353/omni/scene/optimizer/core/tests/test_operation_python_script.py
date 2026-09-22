__copyright__ = "Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

import base64

from omni.scene.optimizer.core import ExecutionContext
from pxr import Usd, UsdUtils

from .test_utils import Test_Operation

# Default arguments for the command
DEFAULT_ARGS = {
    "python": "",
}


def encode_base64_script(value):
    return base64.b64encode(value.encode("ascii")).decode("ascii")


class Test_Operation_Python_Script(Test_Operation):

    OPERATION = "pythonScript"

    async def test_basic(self):
        """Ensure that empty, single line, and multi line python script execution is supported"""
        # Get a copy of the default args.
        args = DEFAULT_ARGS.copy()

        # Executing an empty string should be successful but have no result
        _, result = self._execute_command(args)
        self.assertTrue(result[0])

        # Passing in an un-encoded script will cause the command to return false
        args["python"] = "print(12)"
        _, result = self._execute_command(args)
        self.assertFalse(result[0])

        # Executing a single line string should be successful
        args["python"] = encode_base64_script("print(12)")
        _, result = self._execute_command(args)
        self.assertTrue(result[0])

        # Executing a multi line string with new line characters should be successful
        args["python"] = encode_base64_script("x=12\nprint(x)")
        _, result = self._execute_command(args)
        self.assertTrue(result[0])

    async def test_stage_access(self):
        """Ensure that the stage variable is defined and represents the appropriate pxr.Usd.Stage object"""
        # Get a copy of the default args.
        args = DEFAULT_ARGS.copy()

        # Accessing the "stage" variable should not throw an error
        script = "print(type(stage))"
        args["python"] = encode_base64_script(script)
        _, result = self._execute_command(args)
        self.assertTrue(result[0])

        # Defining a new prim on the stage within the script should be reflected on the stage afterwards.
        new_path = "/World/NewPrim"
        script = "stage.DefinePrim('{}')".format(new_path)
        args["python"] = encode_base64_script(script)

        # Open a very basic scene containing a single cube and get all prim paths before and after execution.
        stage = self._open_stage("simpleCube.usda")
        paths_before = [str(x.GetPath()) for x in stage.Traverse()]
        _, result = self._execute_command(args)
        paths_after = [str(x.GetPath()) for x in stage.Traverse()]

        # The command should succeed and the new prim should exist after, but not before.
        self.assertTrue(result[0])
        self.assertNotIn(new_path, paths_before)
        self.assertIn(new_path, paths_after)

        # The same test should be possible with a stage that is not the omni context
        # Create an in memory stage and get all prim paths before and after execution.
        stage = Usd.Stage.CreateInMemory()
        paths_before = [str(x.GetPath()) for x in stage.Traverse()]
        context = ExecutionContext()
        context.usdStageId = UsdUtils.StageCache().Get().Insert(stage).ToLongInt()
        _, result = self._execute_command(args, context=context)
        paths_after = [str(x.GetPath()) for x in stage.Traverse()]

        # The command should succeed and the new prim should exist after, but not before.
        self.assertTrue(result[0])
        self.assertNotIn(new_path, paths_before)
        self.assertIn(new_path, paths_after)
