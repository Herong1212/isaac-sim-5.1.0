## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest
from pathlib import Path

import carb
import omni.kit.app
import omni.ui as ui
import omni.usd
import omni.kit.commands
from omni.kit import ui_test
from unittest.mock import Mock, patch, ANY
from ..stage_window import StageWindow

CURRENT_PATH = Path(__file__).parent.joinpath("../../../../../data")


class TestStageWindow(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = CURRENT_PATH.absolute().resolve().joinpath("tests")
        self._w = ui.Workspace.get_window("Stage")
        self._usd_context = omni.usd.get_context()

    # After running each test
    async def tearDown(self):
        self._w = None
        self._golden_img_dir = None
        await super().tearDown()

    async def test_general(self):
        # New stage with a sphere
        await self._usd_context.new_stage_async()
        omni.kit.commands.execute("CreatePrim", prim_path="/Sphere", prim_type="Sphere", select_new_prim=False)

        # Loading icon takes time.
        # TODO: We need a mode that blocks UI until icons are loaded
        await self.wait(10)

        await self.docked_test_window(
            window=self._w,
            width=450,
            height=100,
            restore_window=ui.Workspace.get_window("Layer"),
            restore_position=ui.DockPosition.SAME,
        )

        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def test_multi_visibility_change(self):
        """Testing visibility of StageWidget"""
        await self.docked_test_window(
            window=self._w,
            width=450,
            height=200,
        )

        # New stage with three prims
        await self._usd_context.new_stage_async()
        omni.kit.commands.execute("CreatePrim", prim_path="/A", prim_type="Sphere", select_new_prim=False)
        omni.kit.commands.execute("CreatePrim", prim_path="/B", prim_type="Sphere", select_new_prim=False)
        omni.kit.commands.execute("CreatePrim", prim_path="/C", prim_type="Sphere", select_new_prim=False)

        await ui_test.wait_n_updates(5)
        # select both A and C
        self._usd_context.get_selection().set_selected_prim_paths(["/A", "/C"], True)

        # make A invisible
        await ui_test.wait_n_updates(5)
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        eye_icon = stage_widget.find_all("**/ToolButton[*]")[0]
        await eye_icon.click()

        await ui_test.wait_n_updates(5)
        # check C will also be invisible
        await self.finalize_test(golden_img_dir=self._golden_img_dir)

    async def wait(self, n=100):
        for i in range(n):
            await omni.kit.app.get_app().next_update_async()

    async def test_header_columns(self):
        from omni.kit import ui_test
        await ui_test.find("Stage").focus()

        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")

        name_column = stage_widget.find("**/Label[*].text=='Name (Old to New)'")
        self.assertTrue(name_column)
        await ui_test.emulate_mouse_move(name_column.center)
        await name_column.right_click()
        with self.assertRaises(Exception):
            await ui_test.select_context_menu("Create")

        await self.wait()

        await name_column.click()
        await self.wait()
        name_column = stage_widget.find("**/Label[*].text=='Name (A to Z)'")
        self.assertTrue(name_column)

        await name_column.click()
        await self.wait()
        name_column = stage_widget.find("**/Label[*].text=='Name (Z to A)'")
        self.assertTrue(name_column)

        await name_column.click()
        await self.wait()
        name_column = stage_widget.find("**/Label[*].text=='Name (New to Old)'")
        self.assertTrue(name_column)

        await name_column.click()
        await self.wait()
        name_column = stage_widget.find("**/Label[*].text=='Name (Old to New)'")
        self.assertTrue(name_column)
        await self.finalize_test_no_image()

    async def test_rename_with_context_menu(self):
        from omni.kit import ui_test
        await ui_test.find("Stage").focus()

        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")

        # New stage with three prims
        await self._usd_context.new_stage_async()
        stage = omni.usd.get_context().get_stage()
        stage.GetRootLayer().Clear()
        await ui_test.wait_n_updates(5)

        prim = stage.DefinePrim("/test", "Xform")

        await ui_test.wait_n_updates(5)
        prim_item = stage_widget.find("**/Label[*].text=='test'")
        self.assertTrue(prim_item)
        prim_name_field = stage_widget.find("**/StringField[*].identifier=='rename_field'")
        self.assertTrue(prim_name_field)
        await prim_item.double_click()
        self.assertTrue(prim_name_field.widget.selected)
        prim_name_field.model.set_value("")
        await prim_name_field.input("test2")
        await ui_test.input.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)

        await ui_test.wait_n_updates(5)
        old_prim = stage.GetPrimAtPath("/test")
        self.assertFalse(old_prim)

        new_prim = stage.GetPrimAtPath("/test2")
        self.assertTrue(new_prim)

        # Rename with context menu
        prim_item = stage_widget.find("**/Label[*].text=='test2'")
        self.assertTrue(prim_item)
        prim_name_field = stage_widget.find("**/StringField[*].identifier=='rename_field'")
        self.assertTrue(prim_name_field)
        await prim_item.right_click()
        await ui_test.select_context_menu("Rename")
        self.assertTrue(prim_name_field.widget.selected)

        await prim_name_field.input("test3")
        await ui_test.input.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)

        await ui_test.wait_n_updates(5)
        old_prim = stage.GetPrimAtPath("/test")
        self.assertFalse(old_prim)

        new_prim = stage.GetPrimAtPath("/test2test3")
        self.assertTrue(new_prim)
        await self.finalize_test_no_image()

    async def test_window_destroyed_when_hidden(self):
        """Test that hiding stage window destroys it, and showing creates a new instance."""
        ui.Workspace.show_window("Stage")
        self.assertTrue(ui.Workspace.get_window("Stage").visible)
        with patch.object(StageWindow, "destroy", autospec=True) as mock_destroy_dialog:
            ui.Workspace.show_window("Stage", False)
            await ui_test.wait_n_updates(5)
            mock_destroy_dialog.assert_called()
            self.assertFalse(ui.Workspace.get_window("Stage").visible)
        await self.finalize_test_no_image()
