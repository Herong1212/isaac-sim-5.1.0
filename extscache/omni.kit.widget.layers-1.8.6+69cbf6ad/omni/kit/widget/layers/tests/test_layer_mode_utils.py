import omni.kit.test
import os
import uuid
import omni.client

from omni.kit.window.file_importer import get_file_importer
from omni.kit.window.file_exporter import get_file_exporter
from omni.kit.widget.layers.layer_settings import LayerSettings
from omni.kit.widget.layers.layer_model_utils import LayerModelUtils
from omni.kit.widget.prompt import PromptManager
from omni.kit.usd.layers import LayerUtils
from .base import TestLayerUIBase
from pxr import Sdf, Usd, UsdGeom, Gf


class TestLayerModelUtils(TestLayerUIBase):
    async def setUp(self):
        await super().setUp()
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        self.stage = await self.prepare_empty_stage()
        self.old_warning_enabled = LayerSettings().show_merge_or_flatten_warning

        self.test_folder = omni.client.combine_urls(self.temp_dir, str(uuid.uuid1()))
        self.test_folder += "/"
        await omni.client.create_folder_async(self.test_folder)

    async def tearDown(self):
        LayerSettings().show_merge_or_flatten_warning = self.old_warning_enabled
        await self.usd_context.close_stage_async()
        await omni.client.delete_async(self.test_folder)
        omni.client.set_retries(*self.previous_retry_values)
        await super().tearDown()

    async def _wait(self, frames=3):
        for i in range(frames):
            await omni.kit.app.get_app().next_update_async()

    async def test_merge_layers(self):
        layer_model = self.layers_instance.get_layer_model()
        stage = layer_model.usd_context.get_stage()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        stage.GetRootLayer().subLayerPaths.append(layer0.identifier)
        stage.GetRootLayer().subLayerPaths.append(layer1.identifier)

        await self._wait()

        # Enable prompt and try to merge with ok button.
        LayerSettings().show_merge_or_flatten_warning = True
        LayerModelUtils.merge_layer_down(layer_model.root_layer_item.sublayers[0])
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        prompt = PromptManager.query_prompt_by_title("Merge Layer Down")
        self.assertTrue(prompt)
        prompt._on_ok_button_fn()
        await self._wait()

        self.assertEqual(len(layer_model.root_layer_item.sublayers), 1)
        self.assertEqual(layer_model.root_layer_item.sublayers[0].identifier, layer1.identifier)
        omni.kit.undo.undo()
        await self._wait()

        # Enable prompt and cancel merge
        LayerModelUtils.merge_layer_down(layer_model.root_layer_item.sublayers[0])
        await self._wait()

        prompt = PromptManager.query_prompt_by_title("Merge Layer Down")
        self.assertTrue(prompt)
        prompt._on_cancel_button_fn()
        await self._wait()

        self.assertEqual(len(layer_model.root_layer_item.sublayers), 2)
        self.assertEqual(layer_model.root_layer_item.sublayers[0].identifier, layer0.identifier)
        self.assertEqual(layer_model.root_layer_item.sublayers[1].identifier, layer1.identifier)

        omni.kit.undo.undo()
        await self._wait()

        # Disable prompt and try to merge
        LayerSettings().show_merge_or_flatten_warning = False
        LayerModelUtils.merge_layer_down(layer_model.root_layer_item.sublayers[0])
        await self._wait()

        prompt = PromptManager.query_prompt_by_title("Merge Layer Down")
        self.assertFalse(prompt)
        await self._wait()

        self.assertEqual(len(layer_model.root_layer_item.sublayers), 1)
        self.assertEqual(layer_model.root_layer_item.sublayers[0].identifier, layer1.identifier)

        # Make sure that all prompts are released
        self.assertEqual(len(PromptManager._prompts), 0)

    async def test_flatten_layers(self):
        layer_model = self.layers_instance.get_layer_model()
        stage = layer_model.usd_context.get_stage()
        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        stage.GetRootLayer().subLayerPaths.append(layer0.identifier)
        stage.GetRootLayer().subLayerPaths.append(layer1.identifier)

        await self._wait()

        # Enable prompt and try to flatten with ok button.
        LayerSettings().show_merge_or_flatten_warning = True
        LayerModelUtils.flatten_all_layers(layer_model)
        await self._wait()

        prompt = PromptManager.query_prompt_by_title("Flatten All Layers")
        self.assertTrue(prompt)
        prompt._on_ok_button_fn()
        await self._wait()

        self.assertEqual(len(layer_model.root_layer_item.sublayers), 0)
        omni.kit.undo.undo()
        await self._wait()

        # Enable prompt and cancel flatten
        LayerModelUtils.flatten_all_layers(layer_model)
        await self._wait()

        prompt = PromptManager.query_prompt_by_title("Flatten All Layers")
        self.assertTrue(prompt)
        prompt._on_cancel_button_fn()
        await self._wait()

        self.assertEqual(len(layer_model.root_layer_item.sublayers), 2)
        self.assertEqual(layer_model.root_layer_item.sublayers[0].identifier, layer0.identifier)
        self.assertEqual(layer_model.root_layer_item.sublayers[1].identifier, layer1.identifier)

        omni.kit.undo.undo()
        await self._wait()

        # Disable prompt and try to merge
        LayerSettings().show_merge_or_flatten_warning = False
        LayerModelUtils.flatten_all_layers(layer_model)
        await self._wait()

        prompt = PromptManager.query_prompt_by_title("Flatten All Layers")
        self.assertFalse(prompt)
        await self._wait()

        self.assertEqual(len(layer_model.root_layer_item.sublayers), 0)

    async def test_layer_lock(self):
        layer_model = self.layers_instance.get_layer_model()
        stage = layer_model.usd_context.get_stage()
        format = Sdf.FileFormat.FindByExtension(".usd")
        layer0 = Sdf.Layer.New(format, "omniverse://omni-fake-invalid-server/test/test_layer_lock.usd")
        layer1 = Sdf.Layer.New(format, "omniverse://omni-fake-invalid-server/test/test_layer_lock2.usd")
        layer2 = Sdf.Layer.CreateAnonymous()
        stage.GetRootLayer().subLayerPaths.append(layer0.identifier)
        layer0.subLayerPaths.append(layer1.identifier)
        layer0.subLayerPaths.append(layer2.identifier)
        await self._wait(10)

        LayerModelUtils.lock_layer(layer_model.root_layer_item.sublayers[0], True)
        await self._wait()

        self.assertTrue(layer_model.root_layer_item.sublayers[0].locked)
        self.assertTrue(layer_model.root_layer_item.sublayers[0].sublayers[0].locked)

        # Anonymous layer cannot be locked.
        self.assertFalse(layer_model.root_layer_item.sublayers[0].sublayers[1].locked)

    async def test_move_sublayer(self):
        layer_model = self.layers_instance.get_layer_model()
        stage = layer_model.usd_context.get_stage()
        sublayer1 = Sdf.Layer.CreateAnonymous()
        sublayer2 = Sdf.Layer.CreateAnonymous()
        sublayer3 = Sdf.Layer.CreateAnonymous()
        stage.GetRootLayer().subLayerPaths.append(sublayer1.identifier)
        stage.GetRootLayer().subLayerPaths.append(sublayer2.identifier)
        stage.GetRootLayer().subLayerPaths.append(sublayer3.identifier)
        await self._wait()
        root_layer_item = layer_model.root_layer_item
        sublayer1_item = root_layer_item.sublayers[0]
        sublayer2_item = root_layer_item.sublayers[1]
        sublayer3_item = root_layer_item.sublayers[2]
        self.assertFalse(LayerModelUtils.can_move_layer(sublayer1_item, sublayer1_item, -1))
        self.assertFalse(LayerModelUtils.can_move_layer(sublayer1_item, sublayer1_item, 0))
        self.assertTrue(LayerModelUtils.can_move_layer(sublayer1_item, sublayer2_item, -1))
        self.assertTrue(LayerModelUtils.can_move_layer(sublayer1_item, sublayer2_item, 0))
        self.assertTrue(LayerModelUtils.can_move_layer(sublayer2_item, sublayer1_item, -1))
        self.assertTrue(LayerModelUtils.can_move_layer(sublayer2_item, sublayer1_item, 0))
        LayerUtils.set_layer_lock_status(stage.GetRootLayer(), sublayer1_item.identifier, True)
        self.assertFalse(LayerModelUtils.can_move_layer(sublayer1_item, sublayer1_item, -1))
        self.assertFalse(LayerModelUtils.can_move_layer(sublayer1_item, sublayer1_item, 0))
        self.assertFalse(LayerModelUtils.can_move_layer(sublayer1_item, sublayer2_item, -1))
        self.assertTrue(LayerModelUtils.can_move_layer(sublayer1_item, sublayer2_item, 0))
        self.assertTrue(LayerModelUtils.can_move_layer(sublayer2_item, sublayer1_item, -1))
        self.assertTrue(LayerModelUtils.can_move_layer(sublayer2_item, sublayer1_item, 0))

        # Cannot move it as sublayer1 is locked
        LayerModelUtils.move_layer(sublayer1_item, sublayer2_item, -1)
        await self._wait()
        self.assertEqual(len(sublayer1_item.sublayers), 0)

        LayerModelUtils.move_layer(root_layer_item, sublayer3_item, 1)
        await self._wait()
        sublayer1_item = root_layer_item.sublayers[0]
        sublayer2_item = root_layer_item.sublayers[1]
        sublayer3_item = root_layer_item.sublayers[2]
        self.assertEqual(sublayer1_item.identifier, sublayer1.identifier)
        self.assertEqual(sublayer2_item.identifier, sublayer3.identifier)
        self.assertEqual(sublayer3_item.identifier, sublayer2.identifier)

        LayerModelUtils.move_layer(root_layer_item, sublayer1_item, 2)
        await self._wait()
        sublayer1_item = root_layer_item.sublayers[0]
        sublayer2_item = root_layer_item.sublayers[1]
        sublayer3_item = root_layer_item.sublayers[2]
        self.assertEqual(sublayer1_item.identifier, sublayer3.identifier)
        self.assertEqual(sublayer2_item.identifier, sublayer1.identifier)
        self.assertEqual(sublayer3_item.identifier, sublayer2.identifier)

        LayerModelUtils.move_layer(sublayer3_item, sublayer2_item, -1)
        await self._wait()
        self.assertEqual(len(root_layer_item.sublayers), 2)
        self.assertEqual(len(sublayer3_item.sublayers), 1)
        self.assertEqual(sublayer3_item.sublayers[0].identifier, sublayer2_item.identifier)

    async def test_remove_sublayers(self):
        layer_model = self.layers_instance.get_layer_model()
        stage = layer_model.usd_context.get_stage()
        format = Sdf.FileFormat.FindByExtension(".usd")
        layer0 = Sdf.Layer.New(format, "omniverse://omni-fake-invalid-server/test/test_remove_sublayer.usd")
        layer1 = Sdf.Layer.New(format, "omniverse://omni-fake-invalid-server/test/test_remove_sublaye1.usd")
        stage.GetRootLayer().subLayerPaths.append(layer0.identifier)
        stage.GetRootLayer().subLayerPaths.append(layer1.identifier)
        layer0.customLayerData["abc"] = "test"
        with Usd.EditContext(stage, layer0):
            UsdGeom.Cube.Define(stage, "/prim/test")
        self.assertTrue(layer0.dirty)
        await self._wait()

        LayerModelUtils.remove_layers(layer_model.root_layer_item.sublayers)
        await self._wait()

        prompt = PromptManager.query_prompt_by_title(f'{omni.ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Removing Layer')
        self.assertTrue(prompt)
        prompt._on_ok_button_fn()
        await self._wait()

        self.assertEqual(len(layer_model.root_layer_item.sublayers), 0)
        omni.kit.undo.undo()
        await self._wait()

        LayerModelUtils.remove_layers(layer_model.root_layer_item.sublayers)
        await self._wait()

        prompt = PromptManager.query_prompt_by_title(f'{omni.ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Removing Layer')
        self.assertTrue(prompt)
        prompt._on_cancel_button_fn()
        await self._wait()

        self.assertEqual(len(layer_model.root_layer_item.sublayers), 2)
        omni.kit.undo.undo()
        await self._wait()

    def _skip_existing_file_prompt(self, click_yes=False):
        prompt = PromptManager.query_prompt_by_title(f'{omni.ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Overwrite')
        if prompt:
            if click_yes:
                prompt._on_ok_button_fn()
            else:
                prompt._on_cancel_button_fn()

    async def test_create_sublayer(self):
        layer_model = self.layers_instance.get_layer_model()
        stage = layer_model.usd_context.get_stage()

        def _skip_transfer_content_prompt():
            prompt = PromptManager.query_prompt_by_title("Transfer Content")
            if prompt:
                prompt._on_cancel_button_fn()

        # First create
        LayerModelUtils.create_sublayer(layer_model.root_layer_item, 0)
        await self._wait()

        file_picker = get_file_exporter()
        path = os.path.join(self.test_folder, "test.usd")
        file_picker.click_apply(filename_url=path)
        await self._wait()
        self._skip_existing_file_prompt(True)
        await self._wait()
        _skip_transfer_content_prompt()

        status, _ = await omni.client.stat_async(path)
        self.assertEqual(status, omni.client.Result.OK)

        await self._wait()
        self.assertEqual(len(layer_model.root_layer_item.sublayers), 1)

        # Change the content of it for further comparison
        with Usd.EditContext(stage, layer_model.root_layer_item.sublayers[0].layer):
            UsdGeom.Cube.Define(stage, "/world/test")
        stage.Save()

        omni.kit.undo.undo()
        await self._wait()
        self.assertEqual(len(layer_model.root_layer_item.sublayers), 0)

        def _check_content(old_content):
            # Make sure stage is saved and content is there for further comparison
            layer = Sdf.Layer.FindOrOpen(path)
            self.assertTrue(layer)
            prim = layer.GetPrimAtPath("/world/test")
            if old_content:
                self.assertTrue(prim)
            else:
                self.assertFalse(prim)
            layer = None

        _check_content(True)

        # Open create file dialog and cancel it
        LayerModelUtils.create_sublayer(layer_model.root_layer_item, 0)
        file_picker.click_cancel()
        await self._wait()

        _check_content(True)

        # Second create with override
        LayerModelUtils.create_sublayer(layer_model.root_layer_item, 0)
        file_picker.click_apply(filename_url=path)
        await self._wait()
        self._skip_existing_file_prompt(True)
        await self._wait()
        _skip_transfer_content_prompt()
        _check_content(False)

    def _create_layer(self, path):
        layer = Sdf.Layer.FindOrOpen(path)
        if not layer:
            layer = Sdf.Layer.CreateNew(path)

        return layer

    async def test_insert_sublayer(self):
        layer_model = self.layers_instance.get_layer_model()

        # Create layer to be inserted
        path = os.path.join(self.test_folder, "test.usd")
        self._create_layer(path)

        path2 = os.path.join(self.test_folder, "test2.usd")
        self._create_layer(path2)

        path3 = os.path.join(self.test_folder, "test3.usd")
        self._create_layer(path3)

        LayerModelUtils.insert_sublayer(layer_model.root_layer_item, 0)
        await self._wait()

        # Only the first one will be successfully.
        file_picker = get_file_importer()
        for i in range(3):
            file_picker.click_apply(filename_url=path)
            await self._wait()
            self.assertEqual(len(layer_model.root_layer_item.sublayers), 1)

        # Insert multiple layers at the same time
        LayerModelUtils.insert_sublayer(layer_model.root_layer_item, 0)
        await self._wait()
        await file_picker.select_items_async(url=self.test_folder, filenames=["test2.usd", "test3.usd"])
        file_picker.click_apply()
        await self._wait()
        self.assertEqual(len(layer_model.root_layer_item.sublayers), 3)
        all_sublayers = []
        for sublayer_item in layer_model.root_layer_item.sublayers:
            all_sublayers.append(os.path.normpath(sublayer_item.identifier))

        expected_sublayers = [os.path.normpath(path), os.path.normpath(path2), os.path.normpath(path3)]
        self.assertEqual(set(all_sublayers), set(expected_sublayers))

    async def test_move_prim_spec(self):
        layer_model = self.layers_instance.get_layer_model()
        stage = layer_model.usd_context.get_stage()
        layer0 = Sdf.Layer.CreateAnonymous()
        stage.GetRootLayer().subLayerPaths.append(layer0.identifier)
        await self._wait()

        cube_prim_path = "/World/test"
        root_item = layer_model.root_layer_item
        sublayer_item0 = layer_model.root_layer_item.sublayers[0]
        with Usd.EditContext(stage, root_item.layer):
            cube = UsdGeom.Cube.Define(stage, cube_prim_path)
            cube_prim = cube.GetPrim()
        await self._wait()

        # Move prim without conflict
        world_prim = root_item.absolute_root_spec.children[0]
        self.assertTrue(root_item.layer.GetPrimAtPath(cube_prim_path))
        LayerModelUtils.move_prim_spec(layer_model, sublayer_item0, world_prim)
        world_prim = None
        await self._wait()
        self.assertFalse(root_item.layer.GetPrimAtPath(cube_prim_path))
        omni.kit.undo.undo()
        await self._wait()
        self.assertTrue(root_item.layer.GetPrimAtPath(cube_prim_path))

        with Usd.EditContext(stage, sublayer_item0.layer):
            UsdGeom.XformCommonAPI(cube_prim).SetTranslate(Gf.Vec3d(0, 0, 0))
        await self._wait()
        self.assertTrue(sublayer_item0.layer.GetPrimAtPath(cube_prim_path))

        # Move prim with conflict
        world_prim = root_item.absolute_root_spec.children[0]
        LayerModelUtils.move_prim_spec(layer_model, sublayer_item0, world_prim)

        # It should have prompt to remind user
        prompt = PromptManager.query_prompt_by_title(
            f'{omni.ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Merge Prim Spec',
        )
        self.assertTrue(prompt)

        # Cancel it and make sure it's not moved
        prompt._on_cancel_button_fn()
        self.assertTrue(root_item.layer.GetPrimAtPath(cube_prim_path))

        LayerModelUtils.move_prim_spec(layer_model, sublayer_item0, world_prim)

        prompt = PromptManager.query_prompt_by_title(
            f'{omni.ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Merge Prim Spec',
        )
        self.assertTrue(prompt)

        # Confirm it and make sure it's moved
        prompt._on_ok_button_fn()
        self.assertFalse(root_item.layer.GetPrimAtPath(cube_prim_path))

    async def test_layer_save_as(self):
        # Test for https://nvidia-omniverse.atlassian.net/browse/OM-35016
        layer_model = self.layers_instance.get_layer_model()
        LayerModelUtils.save_layer_as(layer_model.root_layer_item)
        await self._wait(10)

        file_picker = get_file_exporter()
        saved_file = os.path.join(self.test_folder, "test_layer_save_as.usd")
        file_picker.click_apply(filename_url=saved_file)
        self._skip_existing_file_prompt(True)
        await self._wait()

        self.assertTrue(os.path.exists(saved_file))
