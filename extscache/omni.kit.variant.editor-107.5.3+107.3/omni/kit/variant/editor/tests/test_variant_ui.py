# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
import os
import pathlib

import carb.input
import omni.kit.app
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.kit.undo
import omni.kit.variant.editor
import omni.usd
from omni.kit.variant.editor.core import VariantEditorCore
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
from omni.kit.window.file_importer.test_helper import FileImporterTestHelper
from omni.ui.tests.test_base import OmniUiTest

from ..extension import get_window

WINDOW_SIZE = 1024


# Having a test class dervived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class UITest(OmniUiTest):
    # SET-UP AND UTILITY
    async def setUp(self):
        await super().setUp()
        from omni.kit.variant.editor.extension import TEST_DATA_PATH

        self._usd_path = TEST_DATA_PATH.absolute()
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

    async def tearDown(self):
        await super().tearDown()

    async def bootstrap_stage(self, stage_path):
        test_file_path = self._usd_path.joinpath(stage_path).absolute()
        await omni.usd.get_context().open_stage_async(str(test_file_path))
        await omni.kit.app.get_app().next_update_async()

    # TESTS

    async def capture_golden_image(self, filename):
        import omni.renderer_capture

        capture_next_frame = omni.renderer_capture.acquire_renderer_capture_interface().capture_next_frame_swapchain
        wait_async_capture = omni.renderer_capture.acquire_renderer_capture_interface().wait_async_capture

        capture_next_frame(str(self._golden_img_dir.joinpath(filename)))

        await omni.kit.app.get_app().next_update_async()

        wait_async_capture()

    async def test_empty_window(self):
        await self.bootstrap_stage("test_core.usda")

        get_window().show()
        await self.docked_test_window(window=get_window()._window, width=WINDOW_SIZE, height=WINDOW_SIZE)

        # Adding in 4 delays so the UI has time to load
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # This is here to update the golden image.  NEVER CHECK IN WITH THE FOLLOWING LINE UNCOMMENTED
        # await self.capture_golden_image("test_window_empty.png")

        await self.finalize_test(
            threshold=120, use_log=True, golden_img_dir=self._golden_img_dir, golden_img_name="test_window_empty.png"
        )

    async def test_populated_window(self):
        await self.bootstrap_stage("test_core.usda")

        get_window().show()
        await self.docked_test_window(window=get_window()._window, width=WINDOW_SIZE, height=WINDOW_SIZE)

        variant_items = get_window()._variant_tree_view.model.get_item_children()[0].children

        get_window()._variant_tree_view.model.select_variant(variant_items[0])

        # Adding in 4 delays so the UI has time to load
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # This is here to update the golden image.  NEVER CHECK IN WITH THE FOLLOWING LINE UNCOMMENTED
        # await self.capture_golden_image("test_window_populated.png")

        await self.finalize_test(
            threshold=120,
            use_log=True,
            golden_img_dir=self._golden_img_dir,
            golden_img_name="test_window_populated.png",
        )

    async def test_variant_tree(self):
        # Tests basic operations of variant set and variant. Use different images for undo and redo to avoid tooltip difference.
        prop_window = ui_test.find("Property")
        prop_window.window.visible = False

        await self.bootstrap_stage("test_core.usda")

        get_window().hide()  # Hide first to avoid failure caused by CoreTest.test_get_variant_specs()
        get_window().show()

        await self.docked_test_window(
            window=get_window()._window, width=WINDOW_SIZE, height=WINDOW_SIZE, block_devices=False
        )

        # Add variant set
        add_variant_set_bn = ui_test.find("Variant Editor//Frame/**/Button[*].text=='Add New Variant Set'")
        await add_variant_set_bn.click()
        golden_img_dir = (
            pathlib.Path(__file__).parent.parent.parent.parent.parent.parent / "data" / "tests" / "golden_img"
        )
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_add_variant_set.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_org_variant_tree.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.redo()
        await asyncio.sleep(1)
        await self.capture_and_compare(golden_img_name="test_redo_add_variant_set.png", golden_img_dir=golden_img_dir)

        # Remove variant set
        variant_set_widget = ui_test.find(
            "Variant Editor//Frame/**/TreeView[*]/VStack[*]/**/Label[*].text=='TestChildren'"
        )
        await variant_set_widget.right_click()
        await ui_test.select_context_menu("Delete Variant Set")
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_remove_variant_set.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(
            golden_img_name="test_undo_remove_variant_set.png", golden_img_dir=golden_img_dir
        )

        omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(
            golden_img_name="test_redo_remove_variant_set.png", golden_img_dir=golden_img_dir
        )

        # Rename variant set
        variant_set_widget = ui_test.find(
            "Variant Editor//Frame/**/TreeView[*]/VStack[*]/**/Label[*].text=='TestDummy'"
        )
        await variant_set_widget.right_click()
        await ui_test.select_context_menu("Rename Variant Set")
        await ui_test.emulate_char_press("TestDummyNew*^^^(*&^(&^()))")
        await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)
        await asyncio.sleep(5)
        await self.capture_and_compare(
            golden_img_name="test_rename_variant_set_bad_name.png", golden_img_dir=golden_img_dir
        )
        omni.kit.undo.undo()

        await variant_set_widget.right_click()
        await ui_test.select_context_menu("Rename Variant Set")
        await ui_test.emulate_char_press("Variant_Set")
        await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)
        await asyncio.sleep(5)
        await self.capture_and_compare(
            golden_img_name="test_rename_variant_set_duplicated_name.png", golden_img_dir=golden_img_dir
        )

        await variant_set_widget.right_click()
        await ui_test.select_context_menu("Rename Variant Set")
        await variant_set_widget.click()
        await variant_set_widget.double_click()  # Select all text in the box
        await ui_test.emulate_char_press("TestDummyNew")
        await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)
        await ui_test.emulate_mouse_move(ui_test.Vec2(0, 0))  # Moves mouse away to remove tooltip
        await asyncio.sleep(5)
        await self.capture_and_compare(golden_img_name="test_rename_variant_set.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(
            golden_img_name="test_undo_rename_variant_set.png", golden_img_dir=golden_img_dir
        )

        omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_rename_variant_set.png", golden_img_dir=golden_img_dir)

        # Select variant
        variant_widget = ui_test.find("Variant Editor//Frame/**/Label[*].text=='Dummy1'")
        await variant_widget.click()
        await self.capture_and_compare(golden_img_name="test_select_variant.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_undo_select_variant.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_select_variant.png", golden_img_dir=golden_img_dir)

        # Clear variant selection
        await variant_set_widget.right_click()
        await ui_test.select_context_menu("Clear Variant Selection")
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(
            golden_img_name="test_clear_variant_selection.png", golden_img_dir=golden_img_dir
        )

        omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(
            golden_img_name="test_undo_clear_variant_selection.png", golden_img_dir=golden_img_dir
        )

        omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(
            golden_img_name="test_clear_variant_selection.png", golden_img_dir=golden_img_dir
        )

        # Copy Variant to All
        await self.bootstrap_stage("test_core.usda")

        variant_widget1 = ui_test.find(
            "Variant Editor//Frame/**/TreeView[0]/HStack[*]/**/Label[*].text=='TestChildren'"
        )
        variant_widget2 = ui_test.find(
            "Variant Editor//Frame/**/TreeView[0]/HStack[*]/**/Label[*].text=='TestChildren_1'"
        )
        await variant_widget1.click()
        await variant_widget2.click()
        await variant_widget2.right_click()
        await ui_test.select_context_menu("Copy Properties to All in Set")
        await variant_widget1.click()
        await omni.kit.app.get_app().next_update_async()
        widget = ui_test.find("Variant Editor//Frame/**/Label[*].text=='xformOp:rotateXYZ'")
        self.assertTrue(widget)

        omni.kit.undo.undo()
        omni.kit.undo.undo()
        omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        widget = ui_test.find("Variant Editor//Frame/**/Label[*].text=='xformOp:rotateXYZ'")
        self.assertFalse(widget)

        omni.kit.undo.redo()
        omni.kit.undo.redo()
        omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()
        widget = ui_test.find("Variant Editor//Frame/**/Label[*].text=='xformOp:rotateXYZ'")
        self.assertTrue(widget)

        # Remove variant
        await self.bootstrap_stage("test_core.usda")

        variant_widget = ui_test.find("Variant Editor//Frame/**/TreeView[0]/HStack[*]/**/Label[*].text=='TestChildren'")
        await variant_widget.right_click()
        await ui_test.select_context_menu("Remove Variant")
        await asyncio.sleep(5)
        await self.capture_and_compare(golden_img_name="test_remove_variant.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.undo()
        await asyncio.sleep(5)
        await self.capture_and_compare(golden_img_name="test_undo_remove_variant.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.redo()
        await asyncio.sleep(5)
        await self.capture_and_compare(golden_img_name="test_remove_variant.png", golden_img_dir=golden_img_dir)

        # Rename variant
        variant_widget = ui_test.find("Variant Editor//Frame/**/TreeView[0]/HStack[*]/**/Label[*].text=='Dummy1'")
        await variant_widget.right_click()
        await ui_test.select_context_menu("Rename Variant")
        await ui_test.emulate_char_press("Dummy2")
        await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)
        await asyncio.sleep(5)
        await self.capture_and_compare(
            golden_img_name="test_rename_variant_duplicated_name.png", golden_img_dir=golden_img_dir
        )

        await variant_widget.right_click()
        await ui_test.select_context_menu("Rename Variant")
        await ui_test.emulate_char_press("Dummy&^&(*^(*&))")
        await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)
        await asyncio.sleep(5)  # Wait for message bubble to disappear
        await self.capture_and_compare(
            golden_img_name="test_rename_variant_bad_name.png", golden_img_dir=golden_img_dir
        )
        omni.kit.undo.undo()

        variant_widget = ui_test.find(
            "Variant Editor//Frame/**/TreeView[0]/HStack[*]/**/Label[*].text=='TestChildren_1'"
        )
        await variant_widget.right_click()
        await ui_test.select_context_menu("Rename Variant")
        await ui_test.emulate_char_press("TestChildrenNew")
        await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_rename_variant.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_undo_rename_variant.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_rename_variant.png", golden_img_dir=golden_img_dir)

        # Duplicate variant
        variant_widget = ui_test.find(
            "Variant Editor//Frame/**/TreeView[0]/HStack[*]/**/Label[*].text=='TestChildrenNew'"
        )
        await variant_widget.right_click()
        await ui_test.select_context_menu("Duplicate Variant")
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_duplicate_variant.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_undo_duplicate_variant.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_duplicate_variant.png", golden_img_dir=golden_img_dir)

        # Select and clear selection
        await variant_widget.click()
        await variant_widget.right_click()
        await ui_test.select_context_menu("Clear Selection")
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_clear_selection.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        asset_path_widget = ui_test.find("Variant Editor//Frame/**/StringField[*].name=='layer_path'")
        self.assertTrue(asset_path_widget)
        self.assertEqual(os.path.basename(asset_path_widget.model.get_value_as_string()), "Rock_Small_01.usd")

        omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_clear_selection.png", golden_img_dir=golden_img_dir)

        # Add variant
        add_variant_button = ui_test.find("Variant Editor//Frame/**/TreeView[*]/VStack[1]/**/Button[*]")
        await add_variant_button.click()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_add_variant.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_undo_add_variant.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_add_variant.png", golden_img_dir=golden_img_dir)

        # Asset drag and drop
        # Docking doesn't work. So we manullay layout windows
        get_window()._window.height = WINDOW_SIZE / 2
        content_window = ui_test.find("Content").window
        content_window.position_x = get_window()._window.position_x
        content_window.position_y = get_window()._window.position_x + get_window()._window.height
        content_window.width = get_window()._window.width
        content_window.height = WINDOW_SIZE - get_window()._window.height

        await self.bootstrap_stage("test_core.usda")

        drag_target = ui_test.Vec2(100, 200)  # Somewhere in left variant tree pannel
        asset_folder = pathlib.Path(golden_img_dir).parent
        content_test_helper = ContentBrowserTestHelper()
        await content_test_helper.drag_and_drop_tree_view(
            str(asset_folder),
            ["Rock_Small_01.usd", "Rock_Small_02.usd", "Rock_Small_03.usd"],
            drag_target,
            focus_treeview_items=False,
        )

        await self.docked_test_window(
            window=get_window()._window,
            width=get_window()._window.width,
            height=get_window()._window.height,
            block_devices=False,
        )
        await asyncio.sleep(4)
        await self.capture_and_compare(
            golden_img_name="test_drag_and_drop_visiblility.png", golden_img_dir=golden_img_dir
        )

        omni.kit.undo.undo()
        await asyncio.sleep(4)
        await self.capture_and_compare(
            golden_img_name="test_undo_drag_and_drop_visiblility.png", golden_img_dir=golden_img_dir
        )

        omni.kit.undo.redo()
        await asyncio.sleep(1)
        await self.capture_and_compare(
            golden_img_name="test_redo_drag_and_drop_visiblility.png", golden_img_dir=golden_img_dir
        )

        await self.finalize_test_no_image()

        await self.bootstrap_stage("test_core.usda")

        option_button = ui_test.find("Variant Editor//Frame/**/HStack[*]/Button[*]")
        await option_button.click()
        await ui_test.select_context_menu("Drag and Drop Mode - Visibility")
        await content_test_helper.drag_and_drop_tree_view(
            str(asset_folder),
            ["Rock_Small_01.usd", "Rock_Small_02.usd", "Rock_Small_03.usd"],
            drag_target,
            focus_treeview_items=False,
        )
        await omni.kit.app.get_app().next_update_async()

        await self.docked_test_window(
            window=get_window()._window,
            width=get_window()._window.width,
            height=get_window()._window.height,
            block_devices=False,
        )

        threshold = 0.35  # Payload paths are different in different enviroment. So we allow some differences.

        await omni.kit.app.get_app().next_update_async()
        asset_path_widget = ui_test.find("Variant Editor//Frame/**/StringField[*].name=='layer_path'")
        self.assertTrue(asset_path_widget)
        self.assertEqual(os.path.basename(asset_path_widget.model.get_value_as_string()), "Rock_Small_03.usd")

        omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        asset_path_widget = ui_test.find("Variant Editor//Frame/**/StringField[*].name=='layer_path'")
        self.assertFalse(asset_path_widget)

        omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()
        asset_path_widget = ui_test.find("Variant Editor//Frame/**/StringField[*].name=='layer_path'")
        self.assertTrue(asset_path_widget)
        self.assertEqual(os.path.basename(asset_path_widget.model.get_value_as_string()), "Rock_Small_03.usd")

        await self.finalize_test_no_image()

    async def test_variant_content(self):
        await self.bootstrap_stage("test_core.usda")

        get_window().hide()  # Hide first to avoid failure caused by CoreTest.test_get_variant_specs()
        get_window().show()

        await self.docked_test_window(
            window=get_window()._window, width=WINDOW_SIZE, height=WINDOW_SIZE, block_devices=False
        )

        # Select prims
        variant_widget = ui_test.find("Variant Editor//Frame/**/Label[*].text=='Dummy1'")
        await variant_widget.click()
        add_prim_button = ui_test.find("Variant Editor//Frame/**/Button[*].text=='Add Prim'")
        await add_prim_button.click()
        select_prims_window = (
            get_window()._picker_button._StageWindowButton__window
        )  # This window is created multiple times, we must use the only valid one.
        select_prims_window.position_y = 0
        select_prims_window.height = WINDOW_SIZE
        prim_widget = ui_test.find("Select Prims//Frame/**/Label[*].text=='ReferenceXForm'")
        await prim_widget.click()
        select_button = ui_test.find("Select Prims//Frame/**/Button[*].text=='Select'")
        await select_button.click()

        await add_prim_button.click()
        select_prims_window = get_window()._picker_button._StageWindowButton__window
        select_prims_window.position_y = 0
        select_prims_window.height = WINDOW_SIZE
        prim_widget = ui_test.find("Select Prims//Frame/**/Label[*].text=='PayloadXForm'")
        await prim_widget.click()
        await select_button.click()

        await asyncio.sleep(4)  # Wait for UI animation to complete

        golden_img_dir = (
            pathlib.Path(__file__).parent.parent.parent.parent.parent.parent / "data" / "tests" / "golden_img"
        )
        await self.capture_and_compare(golden_img_name="test_select_prims.png", golden_img_dir=golden_img_dir)

        # Add variant property
        add_prop_button = ui_test.find(
            "Variant Editor//Frame/**/TreeView[0]/HStack[0]/**/Button[0].text=='Add Property'"
        )
        await add_prop_button.click()
        variant_prop_button = ui_test.find("Select Properties//Frame/**/Label[*].text=='VariantSet: PayloadRocks'")
        await variant_prop_button.click()
        add_button = ui_test.find("Select Properties//Frame/**/Button[*].text=='Add'")
        await add_button.click()

        # Add an attribute
        await add_prop_button.click()
        attr_prop_button = ui_test.find("Select Properties//Frame/**/Label[*].text=='visibility'")
        await attr_prop_button.click()
        await add_button.click()

        # Copies properties
        prim_button = ui_test.find("Variant Editor//Frame/**/Label[*].text=='/World/PayloadXForm'")
        await prim_button.click(right_click=True)
        await ui_test.select_context_menu("Copy All Properties")

        # Pastes properties
        prim_button = ui_test.find("Variant Editor//Frame/**/Label[*].text=='/World/ReferenceXForm'")
        await prim_button.click(right_click=True)
        await ui_test.select_context_menu("Paste Property")

        # Add and edit a relationship
        await add_prop_button.click()
        rel_prop_button = ui_test.find("Select Properties//Frame/**/Label[*].text=='proxyPrim'")
        await rel_prop_button.click()
        await add_button.click()
        add_rel_tgt = ui_test.find(
            "Variant Editor//Frame/**/Button[*].identifier=='sdf_relationship_array_proxyPrim.add_relationships'"
        )
        await add_rel_tgt.click()
        prim_button = ui_test.find("Select Targets//Frame/**/Label[*].text=='ParentCube'")
        await prim_button.click()
        select_button = ui_test.find("Select Targets//Frame/**/Button[*].text=='Select'")
        await select_button.click()
        await add_rel_tgt.click()
        prim_button = ui_test.find("Select Targets//Frame/**/Label[*].text=='ParentXForm'")
        await prim_button.click()
        await select_button.click()
        remove_rel_tgt = ui_test.find(
            "Variant Editor//Frame/**/Button[*].identifier=='sdf_relationship_proxyPrim[0].remove'"
        )
        await remove_rel_tgt.click()

        # Add a reference
        await add_prop_button.click()
        ref_prop_button = ui_test.find("Select Properties//Frame/**/Label[*].text=='Reference'")
        await ref_prop_button.click()
        await add_button.click()

        async with FileImporterTestHelper() as file_import_helper:
            dir = pathlib.Path(__file__).parent.parent.parent.parent.parent.parent / "data" / "tests"
            await file_import_helper.select_items_async(str(dir), ["Rock_Small_01.usd"])
            await file_import_helper.click_apply_async()

        # Add a payload
        await add_prop_button.click()
        payload_prop_button = ui_test.find("Select Properties//Frame/**/Label[*].text=='Payload'")
        await payload_prop_button.click()
        await add_button.click()

        async with FileImporterTestHelper() as file_import_helper:
            dir = pathlib.Path(__file__).parent.parent.parent.parent.parent.parent / "data" / "tests"
            await file_import_helper.select_items_async(str(dir), ["Rock_Small_01.usd"])
            await file_import_helper.click_apply_async()

        threshold = 0.264  # Threshold for path difference of references
        await ui_test.human_delay(1)
        asset_path_widgets = ui_test.find_all("Variant Editor//Frame/**/StringField[*].name=='layer_path'")
        self.assertEqual(len(asset_path_widgets), 2)
        self.assertEqual(os.path.basename(asset_path_widgets[0].model.get_value_as_string()), "Rock_Small_01.usd")
        self.assertEqual(os.path.basename(asset_path_widgets[1].model.get_value_as_string()), "Rock_Small_01.usd")

        omni.kit.undo.undo()
        omni.kit.undo.undo()
        omni.kit.undo.undo()
        omni.kit.undo.undo()
        omni.kit.undo.undo()
        omni.kit.undo.undo()
        omni.kit.undo.undo()
        omni.kit.undo.undo()
        omni.kit.undo.undo()
        await ui_test.human_delay(1)
        await self.capture_and_compare(
            golden_img_name="test_undo_add_variant_content.png", golden_img_dir=golden_img_dir
        )

        omni.kit.undo.redo()
        omni.kit.undo.redo()
        omni.kit.undo.redo()
        omni.kit.undo.redo()
        omni.kit.undo.redo()
        omni.kit.undo.redo()
        omni.kit.undo.redo()
        omni.kit.undo.redo()
        omni.kit.undo.redo()
        await ui_test.human_delay(1)
        asset_path_widgets = ui_test.find_all("Variant Editor//Frame/**/StringField[*].name=='layer_path'")
        self.assertEqual(len(asset_path_widgets), 2)
        self.assertEqual(os.path.basename(asset_path_widgets[0].model.get_value_as_string()), "Rock_Small_01.usd")
        self.assertEqual(os.path.basename(asset_path_widgets[1].model.get_value_as_string()), "Rock_Small_01.usd")

        # Remove prims
        prim_button = ui_test.find("Variant Editor//Frame/**/Label[*].text=='/World/PayloadXForm'")
        await prim_button.click(right_click=True)
        await ui_test.select_context_menu("Remove Item")
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_remove_prim.png", golden_img_dir=golden_img_dir)

        omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(
            golden_img_name="test_undo_remove_prim.png", golden_img_dir=golden_img_dir, threshold=threshold
        )

        omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_redo_remove_prim.png", golden_img_dir=golden_img_dir)

        await self.finalize_test_no_image()

    async def test_variant_in_ref(self):
        await self.bootstrap_stage("test_variant_in_ref.usda")

        get_window().hide()  # Hide first to avoid failure caused by CoreTest.test_get_variant_specs()
        get_window().show()

        await self.docked_test_window(
            window=get_window()._window, width=WINDOW_SIZE, height=WINDOW_SIZE, block_devices=False
        )

        # Select variant set and display variant content
        variant_widget = ui_test.find("Variant Editor//Frame/**/Label[*].text=='Variant_Set'")
        await variant_widget.click()

        # Tries to edit variant
        # Adds a prim
        add_prim_button = ui_test.find("Variant Editor//Frame/**/Button[*].text=='Add Prim'")
        await add_prim_button.click()

        # Adds property
        add_prop_button = ui_test.find(
            "Variant Editor//Frame/**/TreeView[0]/HStack[0]/**/Button[0].text=='Add Property'"
        )
        await add_prop_button.click()

        # Removes properties
        for index in range(1, 7):
            remove_prop_button = ui_test.find(
                f"Variant Editor//Frame/**/TreeView[*]/HStack[{index}]/**/VStack[*].identifier=='remove_prop_widget vstack'"
            )
            await remove_prop_button.click()

        # Removes local opinions
        for index in range(1, 7):
            local_opinion_button = ui_test.find(
                f"Variant Editor//Frame/**/TreeView[*]/HStack[{index}]/**/PropertyWatchButton[*]"
            )
            await local_opinion_button.click()

        # Adds payloads
        add_payload_button = ui_test.find("Variant Editor//Frame/**/Button[*].identifier=='Variant Add Payload'")
        await add_payload_button.click()
        add_reference_button = ui_test.find("Variant Editor//Frame/**/Button[*].identifier=='Variant Add Reference'")
        await add_reference_button.click()

        # Edits relationship
        rel_path_widget = ui_test.find("Variant Editor//Frame/**/sdf_relationship_array_proxyPrim/**/StringField[*]")
        await rel_path_widget.click()
        await ui_test.emulate_char_press("asdfasdf")

        rel_browse_button = ui_test.find(
            "Variant Editor//Frame/**/sdf_relationship_array_proxyPrim/**/Button[*].name!='remove'"
        )
        await rel_browse_button.click()
        rel_remove_button = ui_test.find(
            "Variant Editor//Frame/**/sdf_relationship_array_proxyPrim/**/Button[*].name=='remove'"
        )
        await rel_remove_button.click()

        rel_add_target_button = ui_test.find("Variant Editor//Frame/**/TreeView[0]/HStack[4]/**/ZStack[*]/Button[*]")
        await rel_add_target_button.click()

        # Edits token attribute
        vis_attr_widget = ui_test.find("Variant Editor//Frame/**/token_visibility")
        await vis_attr_widget.click()
        click_pos = vis_attr_widget.center
        click_pos.y += vis_attr_widget.size.y * 2
        await ui_test.emulate_mouse_move_and_click(click_pos)

        # Edits translate
        translate_x_widget = ui_test.find(
            "Variant Editor//Frame/**/drag_per_channel_xformOp:translate/HStack[0]/**/FloatDrag[*]"
        )

        await translate_x_widget.double_click()
        await ui_test.emulate_char_press("123")
        await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="test_variant_in_ref.png", golden_img_dir=self._golden_img_dir)

        self.assertFalse(omni.usd.get_context().get_stage().GetRootLayer().dirty)

        await self.finalize_test_no_image()

    async def test_create_variant_from_content_browser(self):
        # Creates a variant from assets
        await self.bootstrap_stage("test_picker.usda")

        get_window().hide()  # Hide first to avoid failure caused by CoreTest.test_get_variant_specs()
        get_window().show()

        await self.docked_test_window(
            window=get_window()._window, width=WINDOW_SIZE, height=WINDOW_SIZE, block_devices=False
        )

        get_window()._window.height = WINDOW_SIZE / 2
        content_window = ui_test.find("Content").window
        content_window.position_x = get_window()._window.position_x
        content_window.position_y = get_window()._window.position_x + get_window()._window.height
        content_window.width = get_window()._window.width
        content_window.height = WINDOW_SIZE - get_window()._window.height

        content_test_helper = ContentBrowserTestHelper()
        await content_test_helper.toggle_grid_view_async(True)

        async def pick_asset(file_name):
            asset_folder = pathlib.Path(self._golden_img_dir).parent
            await content_test_helper.select_items_async(str(asset_folder), [file_name])
            await content_test_helper.get_gridview_item_async(file_name)
            file_widget = ui_test.find(
                f"Content//Frame/**/content_browser_treeview_grid_view/**/Label[*].text=='{file_name}'"
            )
            await file_widget.right_click()
            await ui_test.select_context_menu("Create Variant Set")
            prim_widget = ui_test.find(
                "Select Target Prim//Frame/VStack[0]/Frame[0]/Frame[0]/VStack[0]/ScrollingFrame[0]/ZStack[0]/TreeView[0]/Frame[0]/ZStack[0]/HStack[0]/HStack[0]/Label[0]"
            )
            await prim_widget.click()
            select_button = ui_test.find("Select Target Prim//Frame/**/Button[*].text=='Select'")
            await select_button.click()

        await pick_asset("mdl.usda")
        await pick_asset("test.mdl")
        await pick_asset("Rock_Small_01.usd")
        await pick_asset("Rock_Small_01.usdc")
        await pick_asset("Rock_Small_01.usdz")

        await self.docked_test_window(
            window=get_window()._window,
            width=get_window()._window.width,
            height=get_window()._window.height,
            block_devices=False,
        )
        await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(
            golden_img_name="test_create_variant_from_content_browser.png", golden_img_dir=self._golden_img_dir
        )

        await self.finalize_test_no_image()
