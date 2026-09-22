## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import os
import random
import string
import carb
import omni.kit.app
import omni.usd
import asyncio
import omni.kit.ui_test as ui_test
import omni.client

from pathlib import Path

from omni.ui.tests.test_base import OmniUiTest
from ..file_window import get_file_utils_instance as get_window_file


TEST_DATA_PATH = Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
).resolve().absolute().joinpath("data", "tests")

class TestFileBase(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._usd_path = TEST_DATA_PATH.absolute()

        token = carb.tokens.get_tokens_interface()
        temp_dir = token.resolve("${temp}")

        def get_random_string():
            return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

        if temp_dir and temp_dir[-1] != '/':
            temp_dir += "/"
        self._temp_path = omni.client.make_absolute_url_if_possible(
            temp_dir, f"{get_random_string()}/test.usda"
        )
        self._temp_edit_path = omni.client.make_absolute_url_if_possible(
            temp_dir, f"{get_random_string()}/test_edit.usda"
        )
        self._dirname = os.path.dirname(self._temp_path).replace("\\", "/")
        self._filename = os.path.basename(self._temp_path)

        await omni.usd.get_context().new_stage_async()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def wait_for_update(self, usd_context=omni.usd.get_context(), wait_frames=20):
        await ui_test.human_delay(wait_frames)

    def remove_file(self, full_path: str):
        import stat
        try:
            os.chmod(full_path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
            os.remove(full_path)
        except Exception:
            # Don't know what's causing these errors: "PermissionError: [WinError 5] Access is denied", but don't want
            # to fail tests for this reason.
            pass

    async def click_file_existed_prompt(self, accept: bool = True):
        dialog = get_window_file()._file_existed_prompt
        button = 0 if accept else 1
        if dialog and dialog._button_list[button][1]:
            # If file exists, click accept at the prompt to continue
            dialog._button_list[button][1]()
            await ui_test.human_delay(20)

    async def click_save_stage_prompt(self, button: int = 0):
        dialog = get_window_file().ui_handler._save_stage_prompt
        if button == 0:
            dialog._on_save_fn()
        elif button == 1:
            dialog._on_dont_save_fn()
        elif button == 2:
            dialog._on_cacnel_fn()

    async def click_unsaved_stage_prompt(self, button: int = 0):
        dialog =  get_window_file()._unsaved_stage_prompt
        _, click_fn = dialog._button_list[button]
        if click_fn:
            click_fn()
        await ui_test.human_delay(20)
