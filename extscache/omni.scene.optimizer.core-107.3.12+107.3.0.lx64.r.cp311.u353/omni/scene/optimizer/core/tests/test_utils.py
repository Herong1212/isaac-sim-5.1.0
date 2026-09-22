__copyright__ = "Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

import json
import pathlib
import time

import omni.kit.test
from omni.scene.optimizer.core.scripts import standalone


def _get_test_data_file_path(name):
    """Get the path for a file within the test data directory of this extension"""
    extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
    test_data_path = pathlib.Path(extension_path).joinpath("data")
    test_file_path = test_data_path.joinpath(name).absolute()
    return str(test_file_path)


def _open_stage_in_omni(file_path):
    """Open the stage in the omni usd context"""
    # Open the stage and return it if the open was successful.
    usd_context = omni.usd.get_context()
    if usd_context.open_stage(file_path):
        return usd_context.get_stage()


# Test classes derived from omni.kit.test.AsyncTestCase will be auto-discoverable by omni.kit.test
class Test_Operation(omni.kit.test.AsyncTestCase):

    # Classes inheriting for this must override this value for _execute_command to succeed.
    OPERATION = "Undefined"

    async def setUp(self):
        self._start_time = time.time()

    async def tearDown(self):
        context = omni.usd.get_context()
        if context.can_close_stage():
            await context.close_stage_async()
        print("Elapsed time: {:.3f}".format(time.time() - self._start_time))

    def _open_stage(self, name):
        """Convenience function to match older test style"""
        file_path = _get_test_data_file_path(name)
        stage = _open_stage_in_omni(file_path)
        self.assertIsNotNone(stage)
        return stage

    def _execute_command(self, args, context=None):
        """Executes the operation that this Test Case represents via the kit commands interface"""
        if self.OPERATION != "Undefined":
            args = json.dumps(args)
            return omni.kit.commands.execute(
                "SceneOptimizerOperation", operation=self.OPERATION, context=context, args=args
            )

    def _get_output_paths(self):
        """Return any output paths executing the operation may have set"""
        return standalone.get_output_paths(self.OPERATION)

    def _get_output_path_arrays(self):
        """Return any output path arrays executing the operation may have set"""
        return standalone.get_output_path_arrays(self.OPERATION)

    def _execute_json(self, stage, name):
        """Executes the operations described in a JSON file on the given stage and assert success"""
        file_path = _get_test_data_file_path(name)
        status = standalone.execute_commands_from_json(stage, file_path)
        self.assertTrue(status)
