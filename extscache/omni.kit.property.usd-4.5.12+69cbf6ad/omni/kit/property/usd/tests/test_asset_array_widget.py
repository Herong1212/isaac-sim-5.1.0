# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-overridden-method, attribute-defined-outside-init


from pathlib import Path
from typing import List

import carb.input
import carb.settings
import omni.client
import omni.kit.app
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.kit.undo
import omni.kit.window.property.managed_frame
import omni.usd
from omni.kit.test_suite.helpers import arrange_windows
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
from omni.kit.window.file_importer.test_helper import FileImporterTestHelper

TEST_DATA_PATH_OV = (
    "omniverse://kit-test-content.ov.nvidia.com/Projects/omni.kit.property.usd/data/tests/usd/asset_array/"
)


ASSIGN_PATH_SETTINGS = "/persistent/app/material/dragDropMaterialPath"
ADD_ASSET_BUTTON_QUERY = "Property//Frame/**/Button[*].identifier=='sdf_asset_array_asset_array.add_asset'"


class TestAssetArray(omni.kit.test.AsyncTestCase):  # pragma: no cover
    async def setUp(self):
        self._test_data_path = Path(
            f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/tests/usd/asset_array/"
        )
        self._context = omni.usd.get_context()
        self._settings = carb.settings.get_settings()
        await arrange_windows("Stage", 1)
        omni.kit.window.property.managed_frame.reset_collapsed_state()
        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Raw USD Properties", False)
        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.set_config_menu_settings(
                {"hide_unknown": False, "hide_thumbnails": True, "show_details": False, "show_udim_sequence": False}
            )

    async def tearDown(self):
        omni.kit.window.property.managed_frame.reset_collapsed_state()

    async def _add_asset(self, dir_url: str, asset_names: List[str]):
        await self._browse_and_select_asset(dir_url, ADD_ASSET_BUTTON_QUERY, asset_names)

    async def _browse_and_select_asset(self, dir_url: str, browse_button_identifier: str, asset_names: List[str]):
        browse_button = ui_test.find(browse_button_identifier)
        await browse_button.click()

        async with FileImporterTestHelper() as file_importer:
            await file_importer.wait_for_popup()
            await file_importer.select_items_async(dir_url, [])  # for whatever reason needs an extra wait for OV test
            await ui_test.human_delay()
            await file_importer.select_items_async(dir_url, asset_names)
            await file_importer.click_apply_async(filename_url=None)

    async def test_asset_array_widget_local_relative(self):
        dir_url = str(self._test_data_path.absolute().resolve()) + "/"
        await self._test_asset_array_widget_impl(dir_url, "relative")

    async def test_asset_array_widget_local_absolute(self):
        dir_url = str(self._test_data_path.absolute().resolve()) + "/"
        await self._test_asset_array_widget_impl(dir_url, "absolute")

    # this test fail as url requires a user login
    async def test_asset_array_widget_ov_relative(self):
        await self._test_asset_array_widget_impl(self._test_data_path_OV, "relative")

    # this test fail as url requires a user login
    async def test_asset_array_widget_ov_absolute(self):
        await self._test_asset_array_widget_impl(self._test_data_path_OV, "absolute")

    async def _test_asset_array_widget_impl(self, dir_url: str, resolve_path_setting: str):
        dir_url = dir_url.replace("\\", "/")
        usd_path = omni.client.combine_urls(dir_url, "main.usda")
        success, error = await self._context.open_stage_async(usd_path)
        self.assertTrue(success, error)

        self._context.get_selection().set_selected_prim_paths(["/Test"], True)
        asset_array_attr = self._context.get_stage().GetAttributeAtPath("/Test.asset_array")

        dummy0_path = "./dummy0.txt"
        dummy1_path = "./dummy1.txt"

        if resolve_path_setting == "absolute":
            dummy0_path = omni.client.combine_urls(dir_url, dummy0_path)
            dummy1_path = omni.client.combine_urls(dir_url, dummy1_path)

        self._prev_path_setting = self._settings.get(ASSIGN_PATH_SETTINGS)
        try:
            self._settings.set(ASSIGN_PATH_SETTINGS, resolve_path_setting)

            await ui_test.human_delay(10)

            # Add first asset
            await self._add_asset(dir_url, ["dummy0.txt"])
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], [dummy0_path])

            # Add second asset
            await self._add_asset(dir_url, ["dummy1.txt"])
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], [dummy0_path, dummy1_path])

            # Reorder assets
            reorder_grab = ui_test.find(
                "Property//Frame/**/HStack[*].identifier=='sdf_asset_array_asset_array[0].reorder_grab'"
            )
            reorder_target_grab = ui_test.find(
                "Property//Frame/**/HStack[*].identifier=='sdf_asset_array_asset_array[1].reorder_grab'"
            )
            drag_target = reorder_target_grab.position + reorder_target_grab.size
            await reorder_grab.drag_and_drop(drag_target)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], [dummy1_path, dummy0_path])
            await ui_test.human_delay(10)

            # Clear the first asset
            clear_asset = ui_test.find("Property//Frame/**/Button[*].identifier=='sdf_clear_asset_asset_array[0]'")
            await clear_asset.click()
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], ["", dummy0_path])

            # Readd the first asset from file picker
            await self._browse_and_select_asset(
                dir_url, "Property//Frame/**/Button[*].identifier=='sdf_browse_asset_asset_array[0]'", ["dummy1.txt"]
            )
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], [dummy1_path, dummy0_path])

            # Remove the first asset
            remove_asset = ui_test.find(
                "Property//Frame/**/Button[*].identifier=='sdf_asset_array_asset_array[0].remove'"
            )
            await remove_asset.click()
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], [dummy0_path])

            # Add 2 assets from file picker
            await self._add_asset(dir_url, ["dummy0.txt", "dummy1.txt"])
            await ui_test.human_delay(10)
            self.assertEqual(
                [asset_path.path for asset_path in asset_array_attr.Get()], [dummy0_path, dummy0_path, dummy1_path]
            )

            # drag drop 2 assets from content window
            await ui_test.find("Content").focus()
            await ui_test.find("Property").focus()
            await ui_test.human_delay(10)

            async with ContentBrowserTestHelper() as content_browser_helper:
                # await content_browser_helper.navigate_to_async(str(usd_path.parent))
                browse_button = ui_test.find(ADD_ASSET_BUTTON_QUERY)
                await content_browser_helper.drag_and_drop_tree_view(
                    dir_url, ["dummy0.txt", "dummy1.txt"], browse_button.center, focus_treeview_items=False
                )
            await ui_test.human_delay(10)
            self.assertEqual(
                [asset_path.path for asset_path in asset_array_attr.Get()],
                [dummy0_path, dummy0_path, dummy1_path, dummy0_path, dummy1_path],
            )

            # test copy to clipboard
            if omni.kit.test.gitlab.is_running_in_gitlab():
                frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Raw USD Properties'")
                await frame.find("**/Label[*].text=='asset_array'").click(right_click=True)
                await ui_test.select_context_menu("Copy", offset=ui_test.Vec2(10, 10))
                await ui_test.human_delay(10)
                await frame.find("**/Label[*].text=='asset_array'").click(right_click=True)
                await ui_test.select_context_menu("Copy Property Path", offset=ui_test.Vec2(10, 10))

            # test remove
            frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Raw USD Properties'")
            await frame.find("**/StringField[*].identifier=='sdf_asset_asset_array[0]'").click(right_click=True)
            await ui_test.human_delay(10)
            await ui_test.select_context_menu("Remove", offset=ui_test.Vec2(10, 10))
            self.assertFalse(asset_array_attr.IsValid())
            omni.kit.undo.undo()
            await ui_test.human_delay(10)

            # Test undo
            omni.kit.undo.undo()
            await ui_test.human_delay(10)
            self.assertEqual(
                [asset_path.path for asset_path in asset_array_attr.Get()], [dummy0_path, dummy0_path, dummy1_path]
            )

            omni.kit.undo.undo()
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], [dummy0_path])

            omni.kit.undo.undo()
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], [dummy1_path, dummy0_path])

            omni.kit.undo.undo()
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], ["", dummy0_path])

            omni.kit.undo.undo()
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], [dummy1_path, dummy0_path])

            omni.kit.undo.undo()
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], [dummy0_path, dummy1_path])

            omni.kit.undo.undo()
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], [dummy0_path])

            omni.kit.undo.undo()
            await ui_test.human_delay(10)
            self.assertEqual(asset_array_attr.Get(), None)

            # Test redo
            omni.kit.undo.redo()
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], [dummy0_path])

            omni.kit.undo.redo()
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], [dummy0_path, dummy1_path])

            omni.kit.undo.redo()
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], [dummy1_path, dummy0_path])

            omni.kit.undo.redo()
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], ["", dummy0_path])

            omni.kit.undo.redo()
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], [dummy1_path, dummy0_path])

            omni.kit.undo.redo()
            await ui_test.human_delay(10)
            self.assertEqual([asset_path.path for asset_path in asset_array_attr.Get()], [dummy0_path])

            omni.kit.undo.redo()
            await ui_test.human_delay(10)
            self.assertEqual(
                [asset_path.path for asset_path in asset_array_attr.Get()], [dummy0_path, dummy0_path, dummy1_path]
            )

            omni.kit.undo.redo()
            await ui_test.human_delay(10)
            self.assertEqual(
                [asset_path.path for asset_path in asset_array_attr.Get()],
                [dummy0_path, dummy0_path, dummy1_path, dummy0_path, dummy1_path],
            )
        finally:
            self._settings.set(ASSIGN_PATH_SETTINGS, self._prev_path_setting)
