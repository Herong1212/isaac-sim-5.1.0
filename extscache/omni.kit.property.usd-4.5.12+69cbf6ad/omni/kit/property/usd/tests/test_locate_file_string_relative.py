# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
# pylint: disable=missing-function-docstring, missing-class-docstring, protected-access, invalid-overridden-method
import os
from pathlib import Path

import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.kit.window.property.managed_frame
import omni.ui as ui
import omni.usd
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from omni.kit.window.content_browser import get_content_window
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
from omni.ui.tests.test_base import OmniUiTest

TEST_FILE_NAME = "usd/zlocate_file_string_relative.usda"  # WAR prefix filename with "z" so it does not affect other test such as the file list view in test_drag_drop_single_mdl_asset_path's drag and drop test


class TestLocateRelativeFileString(omni.kit.test.async_unittest.AsyncTestCase):  # pragma: no cover
    async def setUp(self):
        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.set_config_menu_settings(
                {"hide_unknown": True, "hide_thumbnails": True, "show_details": False, "show_udim_sequence": True}
            )

        await arrange_windows("Stage", 128)
        await open_stage(get_test_data_path(__name__, TEST_FILE_NAME))

        omni.kit.window.property.managed_frame.reset_collapsed_state()
        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Raw USD Properties", False)

    async def tearDown(self):
        await wait_stage_loading()
        omni.kit.window.property.managed_frame.reset_collapsed_state()

    async def test_locate_file_string_relative(self):
        await ui_test.find("Content").focus()

        await select_prims(["/Test"])

        # This attribute has a relative path "./asset_array/dummy0.txt"
        locate_button = ui_test.find("Property//Frame/**/.identifier=='sdf_locate_asset_filePath'")
        self.assertEqual(locate_button.widget.enabled, True)

        content_browser = get_content_window()
        content_browser.navigate_to(get_test_data_path(__name__, ""))

        await locate_button.click()
        await ui_test.human_delay(10)

        selected = [os.path.basename(path) for path in content_browser.get_current_selections()]

        # make sure it can jump to the asset in content window
        self.assertEqual(selected, ["dummy0.txt"])


class TestValidateRelativeFileString(OmniUiTest):  # pragma: no cover
    async def setUp(self):
        self._golden_img_dir = Path(
            f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/tests/golden_img"
        )

        await open_stage(get_test_data_path(__name__, TEST_FILE_NAME))
        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Raw USD Properties", False)

    async def tearDown(self):
        await wait_stage_loading()
        omni.kit.window.property.managed_frame.reset_collapsed_state()

    async def test_validate_file_string_relative(self):
        import omni.kit.window.property as p

        pw = p.get_window()

        await self.docked_test_window(
            window=pw._window,
            width=600,
            height=300,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
            block_devices=False,
        )

        stage = omni.usd.get_context().get_stage()
        await select_prims(["/Test"])
        await ui_test.human_delay(10)

        # when edit target is default, relative path validation should happen against root layer
        await self.capture_and_compare(
            golden_img_dir=self._golden_img_dir, golden_img_name="validate_relative_file_string.png"
        )

        # when edit target is session layer, relative path validation should happen still against root layer,
        # NOT against session layer.
        stage.SetEditTarget(stage.GetSessionLayer())

        pw.request_rebuild()
        await ui_test.human_delay(10)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="validate_relative_file_string.png", zero_mouse=True
        )
