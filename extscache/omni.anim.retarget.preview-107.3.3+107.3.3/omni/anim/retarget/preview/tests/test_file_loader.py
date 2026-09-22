# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


import omni.kit.app
import omni.kit.test
import pathlib
from omni.kit.test_suite.helpers import wait_stage_loading
from ..file_loader import FileLoader


EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)
TEST_DATA_PATH = EXTENSION_FOLDER_PATH.joinpath("data/tests")


class TestFileLoader(omni.kit.test.AsyncTestCase):
    async def test_file_loading(self):
        self._loaded = False

        context_prefix = 'test'
        file_loader = FileLoader(context_name_prefix=context_prefix)

        self.assertIsNone(file_loader.get_stage())

        self.assertTrue(file_loader.is_supported_file('test.usd'))
        self.assertTrue(file_loader.is_supported_file('test.usda'))
        self.assertTrue(file_loader.is_supported_file('test.usdc'))

        self.assertFalse(file_loader.is_supported_file(''))
        self.assertFalse(file_loader.is_supported_file('test'))
        self.assertFalse(file_loader.is_supported_file('test.jpg'))
        self.assertFalse(file_loader.is_supported_file('test.fbx'))

        await wait_stage_loading()
        usd_path = TEST_DATA_PATH.absolute()
        self.test_file_path = str(usd_path.joinpath("file_loader_tests.usda").absolute())
        file_loader.load_file_async(self.test_file_path, callback=self._on_file_loaded)

        # loading is async
        self.assertFalse(self._loaded)

        await self._wait_file_load()

        stage = file_loader.get_stage()
        self.assertIsNotNone(stage)
        self.assertTrue(stage.GetPrimAtPath('/World/dummy').IsValid())

    async def _wait_file_load(self):
        while not self._loaded:
            await omni.kit.app.get_app().next_update_async()

    def _on_file_loaded(self, external_url: str, success: bool, root: str):
        self._loaded = True

        self.assertEqual(self.test_file_path, external_url)
        self.assertTrue(success)
