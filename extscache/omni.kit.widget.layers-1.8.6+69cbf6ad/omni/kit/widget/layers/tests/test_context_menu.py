import omni.kit.test
import os
import tempfile
import shutil
import omni.client
import omni.kit.app

from .base import TestLayerUIBase
from pxr import Usd, Sdf
from stat import S_IREAD, S_IWRITE
from omni.kit.usd.layers import LayerUtils
from omni.kit.widget.prompt import PromptManager


class TestContextMenu(TestLayerUIBase):

    # Before running each test
    async def setUp(self):
        await super().setUp()

        self.stage = self.usd_context.get_stage()

        self._temp_dir = tempfile.TemporaryDirectory().name

        self._writable_layer_path = os.path.join(self._temp_dir, "writable.usd")
        self._writable_layer = Sdf.Layer.CreateNew(self._writable_layer_path)
        self._writable_layer.Save()

        self._readonly_layer_path = os.path.join(self._temp_dir, "readonly.usd")
        layer = Sdf.Layer.CreateNew(self._readonly_layer_path)
        layer.Save()
        layer = None
        os.chmod(self._readonly_layer_path, S_IREAD)

        self._readonly_layer = Sdf.Layer.FindOrOpen(self._readonly_layer_path)

        # Prepare stage
        root_layer = self.stage.GetRootLayer()
        root_layer.subLayerPaths.append(self._readonly_layer_path)
        root_layer.subLayerPaths.append(self._writable_layer_path)
        await self.wait()

        await self._hide_prompt()

        import omni.kit.ui_test as ui_test
        await ui_test.find("Layer").focus()

    async def tearDown(self):
        await super().tearDown()

        self._writable_layer = None
        self._readonly_layer = None
        self.stage = None

        os.chmod(self._readonly_layer_path, S_IWRITE)
        shutil.rmtree(self._temp_dir)

    async def wait(self, frames=10):
        for i in range(frames):
            await self.app.next_update_async()

    def _find_all_layer_items(self):
        import omni.kit.ui_test as ui_test
        writable_item = ui_test.find("Layer//Frame/**/Label[*].text=='writable.usd'")
        self.assertTrue(writable_item)

        readonly_item = ui_test.find("Layer//Frame/**/Label[*].text=='readonly.usd'")
        self.assertTrue(readonly_item)

        root_item = ui_test.find("Layer//Frame/**/Label[*].text=='Root Layer (Authoring Layer)'")
        self.assertTrue(root_item)

        return root_item, writable_item, readonly_item

    async def test_set_authoring_layer(self):
        import omni.kit.ui_test as ui_test
        root_item, writable_item, readonly_item = self._find_all_layer_items()

        await writable_item.right_click()
        await ui_test.select_context_menu("Set Authoring Layer")
        self.assertEqual(self._writable_layer.identifier, self.stage.GetEditTarget().GetLayer().identifier)

        await readonly_item.right_click()
        # Cannot found this menu item for readonly layer.
        with self.assertRaises(Exception) as context:
            await ui_test.select_context_menu("Set Authoring Layer")
        self.assertEqual(self._writable_layer.identifier, self.stage.GetEditTarget().GetLayer().identifier)

        # Double click to change authoring layer will fail also.
        await readonly_item.double_click()
        self.assertEqual(self._writable_layer.identifier, self.stage.GetEditTarget().GetLayer().identifier)

        # Switch back to root layer
        await root_item.double_click()
        self.assertEqual(self.stage.GetEditTarget().GetLayer().identifier, self.stage.GetEditTarget().GetLayer().identifier)

        # Mute layer and try to set it as authoring layer will fail also
        self.stage.MuteLayer(self._writable_layer.identifier)
        await self.wait()
        await writable_item.right_click()
        with self.assertRaises(Exception) as context:
            await ui_test.select_context_menu("Set Authoring Layer")
        self.assertEqual(self.stage.GetEditTarget().GetLayer().identifier, self.stage.GetEditTarget().GetLayer().identifier)

        self.stage.UnmuteLayer(self._writable_layer.identifier)
        await self.wait()

        # Lock layer and try to set it as authoring layer will fail also
        LayerUtils.set_layer_lock_status(self.stage.GetRootLayer(), self._writable_layer.identifier, True)
        await self.wait()
        await writable_item.right_click()
        with self.assertRaises(Exception) as context:
            await ui_test.select_context_menu("Set Authoring Layer")
        self.assertEqual(self.stage.GetEditTarget().GetLayer().identifier, self.stage.GetEditTarget().GetLayer().identifier)

        LayerUtils.set_layer_lock_status(self.stage.GetRootLayer(), self._writable_layer.identifier, False)
        await self.wait()

    async def _hide_prompt(self):
        prompt = PromptManager.query_prompt_by_title("Flatten All Layers")
        if prompt:
            prompt.visible = False

        prompt = PromptManager.query_prompt_by_title("Merge Layer Down")
        if prompt:
            prompt.visible = False

    async def _test_menu_item(
        self,
        item_name,
        file_picker_name=None,
        allow_read_only=False,
        allow_mute=False,
        allow_lock=False,
        select_multiple=False
    ):

        import omni.kit.ui_test as ui_test
        root_item, writable_item, readonly_item = self._find_all_layer_items()

        if select_multiple:
            layer_model = self.layers_instance.get_layer_model()
            root_layer_item = layer_model.root_layer_item
            layer_window = self.layers_instance._window
            layer_tree_view = layer_window._layer_view
            # Select two sublayers: writable and readonly sublayer of root.
            layer_tree_view.selection = root_layer_item.sublayers
            await self.wait()

            # Ensure they are selected.
            self.assertEqual(len(self.layers_instance.get_selected_items()), 2)

        await writable_item.right_click()
        await ui_test.select_context_menu(item_name)
        await ui_test.human_delay()
        if file_picker_name:
            await self.wait()
            file_picker = ui_test.find(file_picker_name)
            await file_picker.focus()
            self.assertTrue(file_picker)
            file_picker.window.visible = False

        # Special treatment for flatten sublayers
        await self._hide_prompt()

        await readonly_item.right_click()
        # Cannot found this menu item for readonly layer.
        if not allow_read_only:
            with self.assertRaises(Exception) as context:
                await ui_test.select_context_menu(item_name)
        else:
            await ui_test.select_context_menu(item_name)

        # Special treatment for flatten sublayers
        await self._hide_prompt()

        # Mute layer and try to create a sublayer for it will fail also
        self.stage.MuteLayer(self._writable_layer.identifier)
        await self.wait()
        await writable_item.right_click()
        if not allow_mute:
            with self.assertRaises(Exception) as context:
                await ui_test.select_context_menu(item_name)
        else:
            await ui_test.select_context_menu(item_name)

        # Special treatment for flatten sublayers
        await self._hide_prompt()

        self.stage.UnmuteLayer(self._writable_layer.identifier)
        await self.wait()

        # Lock layer and try to Create Sublayer will fail also
        LayerUtils.set_layer_lock_status(self.stage.GetRootLayer(), self._writable_layer.identifier, True)
        await self.wait()
        await writable_item.right_click()
        if not allow_lock:
            with self.assertRaises(Exception) as context:
                await ui_test.select_context_menu(item_name)
        else:
            await ui_test.select_context_menu(item_name)

        # Special treatment for flatten sublayers
        await self._hide_prompt()

        LayerUtils.set_layer_lock_status(self.stage.GetRootLayer(), self._writable_layer.identifier, False)
        await self.wait()

    async def test_copy_url_link(self):
        import omni.kit.ui_test as ui_test

        root_item, _, _ = self._find_all_layer_items()
        await root_item.right_click()
        await ui_test.select_context_menu("Copy URL Link")

        import omni.kit.clipboard
        url = omni.kit.clipboard.paste()
        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item
        self.assertEqual(url, root_layer_item.identifier)

    async def test_collapse_expand_tree(self):
        import omni.kit.ui_test as ui_test

        root_item, _, _ = self._find_all_layer_items()
        await root_item.right_click()
        await ui_test.select_context_menu("Collapse Tree")

        await root_item.right_click()
        await ui_test.select_context_menu("Expand Tree")

    async def test_set_edit_layer(self):
        import omni.kit.ui_test as ui_test
        menu_name = "Set Default Edit Layer"

        _, writable_item, readonly_item = self._find_all_layer_items()

        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item
        layer_model.auto_authoring_mode = True
        await self.wait()

        await writable_item.right_click()
        await ui_test.select_context_menu(menu_name)
        layer = Sdf.Find(layer_model.default_edit_layer)
        self.assertEqual(layer, self._writable_layer)

        await readonly_item.right_click()
        with self.assertRaises(Exception) as context:
            await ui_test.select_context_menu(menu_name)

    async def test_refresh_references_or_payloads(self):
        import omni.kit.ui_test as ui_test
        prim = self.stage.DefinePrim("/reference0", "Xform")
        prim.GetReferences().AddReference(self._writable_layer.identifier)

        prim = self.stage.DefinePrim("/payload0", "Xform")
        prim.GetPayloads().AddPayload(self._writable_layer.identifier)

        prim = self.stage.DefinePrim("/reference_and_payload0", "Xform")
        prim.GetReferences().AddReference(self._writable_layer.identifier)
        prim.GetPayloads().AddPayload(self._writable_layer.identifier)
        await self.wait()

        reference_widget = ui_test.find("Layer//Frame/**/Label[*].text=='reference0'")
        payload_widget = ui_test.find("Layer//Frame/**/Label[*].text=='payload0'")
        reference_and_payload_widget = ui_test.find("Layer//Frame/**/Label[*].text=='reference_and_payload0'")
        all_widgets = [reference_widget, payload_widget, reference_and_payload_widget]
        all_menu_names = ["Refresh Reference", "Refresh Payload", "Refresh Payload & Reference"]
        for prim_item, menu_name in zip(all_widgets, all_menu_names):
            await prim_item.right_click()
            import asyncio
            await asyncio.sleep(0.1)
            await ui_test.select_context_menu(menu_name)

    async def test_save_sublayer(self):
        import omni.kit.ui_test as ui_test
        menu_name = "Save"

        for layer in [self.stage.GetRootLayer(), self._writable_layer, self._readonly_layer]:
            Sdf.CreatePrimInLayer(layer, "/test")

        await self.wait()
        root_item, writable_item, readonly_item = self._find_all_layer_items()
        await writable_item.right_click()
        await ui_test.select_context_menu(menu_name)

        # When it's not dirty, the menu item is not shown.
        # Cannot save readonly layer
        # Cannot save anonymous layer
        for layer_item in [root_item, writable_item, readonly_item]:
            await layer_item.right_click()
            with self.assertRaises(Exception) as context:
                await ui_test.select_context_menu(menu_name)

    async def test_find_in_browser(self):
        import omni.kit.ui_test as ui_test
        menu_name = "Find in Content Browser"

        root_item, writable_item, readonly_item = self._find_all_layer_items()
        for layer_item in [writable_item, readonly_item]:
            await layer_item.right_click()
            await ui_test.select_context_menu(menu_name)

        # Cannot browse anonymous layer
        await root_item.right_click()
        with self.assertRaises(Exception) as context:
            await ui_test.select_context_menu(menu_name)

    async def test_move_selection(self):
        import omni.kit.ui_test as ui_test
        menu_name = "Move Selections To This Layer"

        _, writable_item, readonly_item = self._find_all_layer_items()

        prim0 = self.stage.DefinePrim("/reference0", "Xform")
        prim1 = self.stage.DefinePrim("/payload0", "Xform")
        await self.wait()

        self.usd_context.get_selection().set_selected_prim_paths([str(prim0.GetPath()), str(prim1.GetPath())], True)

        # Cannot modify readonly layer
        await readonly_item.right_click()
        with self.assertRaises(Exception) as context:
            await ui_test.select_context_menu(menu_name)

        await writable_item.right_click()
        await ui_test.select_context_menu(menu_name)
        await self.wait()

        root_layer = self.stage.GetRootLayer()
        self.assertFalse(root_layer.GetPrimAtPath(prim0.GetPath()))
        self.assertFalse(root_layer.GetPrimAtPath(prim1.GetPath()))
        self.assertTrue(self._writable_layer.GetPrimAtPath(prim0.GetPath()))
        self.assertTrue(self._writable_layer.GetPrimAtPath(prim1.GetPath()))

    async def _test_menu_without_selection(self, menu_name):
        """Right click on the empty area of layer window will pop up context menu also."""

        import omni.kit.ui_test as ui_test
        window = ui_test.find("Layer")
        await window.bring_to_front()
        await ui_test.emulate_mouse_move(ui_test.Vec2(-100, -100))
        await ui_test.emulate_mouse_move(window.center)

        await ui_test.emulate_mouse_click(right_click=True)
        await ui_test.select_context_menu(menu_name)

    async def test_create_sublayer_without_selection(self):
        await self._test_menu_without_selection("Create Sublayer")

    async def test_insert_sublayer_without_selection(self):
        await self._test_menu_without_selection("Insert Sublayer")

    async def test_create_sublayer(self):
        await self._test_menu_item("Create Sublayer", "Create Sublayer")

    async def test_insert_sublayer(self):
        await self._test_menu_item("Insert Sublayer", "Insert Sublayer")

    async def test_save_a_copy(self):
        await self._test_menu_item("Save a Copy", "Save Layer As", True, True, True)

    async def test_save_as(self):
        await self._test_menu_item("Save As", "Save Layer As", True, False, True)

    async def test_remove_sublayer(self):
        await self._test_menu_item("Remove Layer", None, True, False, False)

    async def test_remove_multiple_sublayers(self):
        await self._test_menu_item("Remove Layer", None, False, False, False, True)

    async def test_flatten_sublayers(self):
        await self._test_menu_item("Flatten Sublayers", None, True, True, False)

    async def test_reload_sublayer(self):
        await self._test_menu_item("Reload Layer", None, True, False, False)

    async def test_merge_layer_down(self):
        import omni.kit.ui_test as ui_test
        root_item, writable_item, readonly_item = self._find_all_layer_items()

        layer = Sdf.Layer.CreateAnonymous()
        self.stage.GetRootLayer().subLayerPaths.append(layer.identifier)

        await self._test_menu_item("Merge Down One", None, False, False, False)

        await writable_item.right_click()
        await ui_test.select_context_menu("Merge Down One")

    async def test_remove_prim(self):
        index = 0
        for layer in [self._writable_layer, self._readonly_layer]:
            with Usd.EditContext(self.stage, layer):
                self.stage.DefinePrim(f"/prim{index}")
                index += 1
                self.stage.DefinePrim(f"/prim{index}")
                index += 1

        await self.wait()

        self.assertTrue(self._writable_layer.GetPrimAtPath("/prim0"))
        self.assertTrue(self._writable_layer.GetPrimAtPath("/prim1"))
        self.assertTrue(self._readonly_layer.GetPrimAtPath("/prim2"))
        self.assertTrue(self._readonly_layer.GetPrimAtPath("/prim3"))

        import omni.kit.ui_test as ui_test

        # Select and delete single prim.
        LayerUtils.set_edit_target(self.stage, self._writable_layer.identifier)
        await self.wait()

        omni.kit.commands.execute(
            "SelectPrims",
            old_selected_paths=[],
            new_selected_paths=["/prim0"],
            expand_in_stage=True
        )
        await self.wait()

        prim0 = ui_test.find("Layer//Frame/**/Label[*].text=='prim0'")
        await prim0.right_click()
        await ui_test.select_context_menu("Delete")
        self.assertFalse(self._writable_layer.GetPrimAtPath("/prim0"))
        self.assertTrue(self._writable_layer.GetPrimAtPath("/prim1"))
        omni.kit.undo.undo()
        await self.wait()

        # Select and delete multiple prims.
        omni.kit.commands.execute(
            "SelectPrims",
            old_selected_paths=[],
            new_selected_paths=["/prim0", "/prim1"],
            expand_in_stage=True
        )
        await self.wait()
        prim0 = ui_test.find("Layer//Frame/**/Label[*].text=='prim0'")
        await prim0.right_click()
        await ui_test.select_context_menu("Delete")
        self.assertFalse(self._writable_layer.GetPrimAtPath("/prim0"))
        self.assertFalse(self._writable_layer.GetPrimAtPath("/prim1"))

        # Cannot remove prims in read-only layer.
        LayerUtils.set_edit_target(self.stage, self._readonly_layer.identifier)
        await self.wait()

        omni.kit.commands.execute(
            "SelectPrims",
            old_selected_paths=[],
            new_selected_paths=["/prim2"],
            expand_in_stage=True
        )
        await self.wait()
        prim2 = ui_test.find("Layer//Frame/**/Label[*].text=='prim2'")
        await prim2.right_click()
        with self.assertRaises(Exception) as context:
            await ui_test.select_context_menu("Delete")
