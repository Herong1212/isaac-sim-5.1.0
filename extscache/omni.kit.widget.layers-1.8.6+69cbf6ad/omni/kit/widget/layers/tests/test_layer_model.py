import omni.kit.test
import os
import uuid
import omni.client
import tempfile

from .base import TestLayerUIBase
from pxr import Sdf, Usd
from omni.kit.usd.layers import LayerUtils


class TestLayerModelAPI(TestLayerUIBase):
    async def setUp(self):
        await super().setUp()
        self.test_folder = omni.client.combine_urls(self.temp_dir, str(uuid.uuid1()))
        self.test_folder += "/"
        await omni.client.create_folder_async(self.test_folder)

        self.stage = await self.prepare_empty_stage()

    async def tearDown(self):
        if self.usd_context.get_stage():
            await self.usd_context.close_stage_async()
        await omni.client.delete_async(self.test_folder)
        await super().tearDown()

    async def test_authoring_mode_switch(self):
        layer_model = self.layers_instance.get_layer_model()
        layer_model.auto_authoring_mode = True
        self.assertTrue(layer_model.auto_authoring_mode)
        self.assertFalse(layer_model.normal_mode)
        self.assertFalse(layer_model.spec_linking_mode)

        layer_model.auto_authoring_mode = False
        self.assertFalse(layer_model.auto_authoring_mode)
        self.assertFalse(layer_model.spec_linking_mode)
        self.assertTrue(layer_model.normal_mode)

        layer_model.spec_linking_mode = True
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        self.assertFalse(layer_model.auto_authoring_mode)
        self.assertTrue(layer_model.spec_linking_mode)
        self.assertFalse(layer_model.normal_mode)

        layer_model.spec_linking_mode = False
        self.assertFalse(layer_model.auto_authoring_mode)
        self.assertFalse(layer_model.spec_linking_mode)
        self.assertTrue(layer_model.normal_mode)

    async def test_api(self):
        layer_model = self.layers_instance.get_layer_model()
        # Test API call to make sure it does not throw errors.
        # It's simply called here without any checking since
        # test wrapper will catch console errors if it's failed.
        # For functionality tests, it's covered in test.command.py already.
        layer_model.flatten_all_layers()

        with tempfile.TemporaryDirectory() as tmpdirname:
            # save the file
            tmp_file_path = os.path.join(tmpdirname, "tmp.usda")
            tmp_file_path2 = os.path.join(tmpdirname, "tmp2.usda")
            result = await omni.usd.get_context().save_as_stage_async(tmp_file_path)
            self.assertTrue(result)

            new_sublayer = Sdf.Layer.CreateNew(tmp_file_path2)
            new_sublayer.Save()

            stage = omni.usd.get_context().get_stage()
            stage.GetRootLayer().subLayerPaths.append(new_sublayer.identifier)
            stage.SetEditTarget(stage.GetEditTargetForLocalLayer(new_sublayer))

            def on_save_done(success, error_str, saved_layers):
                self.assertTrue(success)
                self.assertEqual(saved_layers, [tmp_file_path])

            layer_model.save_layers([tmp_file_path])
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

            # Close stage and re-open it to see if edit target is saved correctly
            await omni.usd.get_context().close_stage_async()
            await omni.usd.get_context().open_stage_async(tmp_file_path)

            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            stage = omni.usd.get_context().get_stage()

            self.assertEqual(stage.GetEditTarget().GetLayer(), new_sublayer)

    async def _wait(self, frames=2):
        for i in range(frames):
            await omni.kit.app.get_app().next_update_async()

    async def test_layer_move_and_reload(self):
        usd_context = omni.usd.get_context()
        with tempfile.TemporaryDirectory() as tmpdirname:
            # save the file
            tmp_file_path = os.path.join(tmpdirname, "tmp.usd")
            result = await usd_context.save_as_stage_async(tmp_file_path)
            self.assertTrue(result)

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
            self.assertEqual(sublayer1_item.identifier, sublayer1.identifier)
            self.assertEqual(sublayer2_item.identifier, sublayer2.identifier)
            self.assertEqual(sublayer3_item.identifier, sublayer3.identifier)

            root_layer = stage.GetRootLayer()
            LayerUtils.move_layer(root_layer.identifier, 0, root_layer.identifier, 1, True)
            root_layer.Save()

            await self._wait()
            root_layer.Reload(True)
            root_layer = None
            stage = None

            root_layer_item = layer_model.root_layer_item
            sublayer1_item = root_layer_item.sublayers[0]
            sublayer2_item = root_layer_item.sublayers[1]
            sublayer3_item = root_layer_item.sublayers[2]
            self.assertEqual(sublayer1_item.identifier, sublayer2.identifier)
            self.assertEqual(sublayer2_item.identifier, sublayer1.identifier)
            self.assertEqual(sublayer3_item.identifier, sublayer3.identifier)

            await usd_context.close_stage_async()

    async def test_drag_and_drop_sublayer(self):
        layer_model = self.layers_instance.get_layer_model()
        stage = layer_model.usd_context.get_stage()
        Sdf.CreatePrimInLayer(stage.GetRootLayer(), '/test')
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
        self.assertFalse(layer_model.drop_accepted(sublayer1_item, sublayer1_item, -1))
        self.assertFalse(layer_model.drop_accepted(sublayer1_item, sublayer1_item, 0))
        self.assertTrue(layer_model.drop_accepted(sublayer1_item, sublayer2_item, -1))
        self.assertFalse(layer_model.drop_accepted(sublayer1_item, sublayer2_item, 0))
        self.assertTrue(layer_model.drop_accepted(sublayer2_item, sublayer1_item, -1))
        self.assertFalse(layer_model.drop_accepted(sublayer2_item, sublayer1_item, 0))
        LayerUtils.set_layer_lock_status(stage.GetRootLayer(), sublayer1_item.identifier, True)
        self.assertFalse(layer_model.drop_accepted(sublayer1_item, sublayer1_item, -1))
        self.assertFalse(layer_model.drop_accepted(sublayer1_item, sublayer1_item, 0))
        self.assertFalse(layer_model.drop_accepted(sublayer1_item, sublayer2_item, -1))
        self.assertFalse(layer_model.drop_accepted(sublayer1_item, sublayer2_item, 0))
        self.assertTrue(layer_model.drop_accepted(sublayer2_item, sublayer1_item, -1))
        self.assertFalse(layer_model.drop_accepted(sublayer2_item, sublayer1_item, 0))

        layer_model.drop(sublayer2_item, sublayer3_item, 2)
        await self._wait()
        sublayer1_item = root_layer_item.sublayers[0]
        sublayer2_item = root_layer_item.sublayers[1]
        sublayer3_item = root_layer_item.sublayers[2]
        self.assertEqual(sublayer1_item.identifier, sublayer1.identifier)
        self.assertEqual(sublayer2_item.identifier, sublayer3.identifier)
        self.assertEqual(sublayer3_item.identifier, sublayer2.identifier)

        layer_model.drop(sublayer2_item, sublayer1_item, 3)
        await self._wait()
        sublayer1_item = root_layer_item.sublayers[0]
        sublayer2_item = root_layer_item.sublayers[1]
        sublayer3_item = root_layer_item.sublayers[2]
        self.assertEqual(sublayer1_item.identifier, sublayer3.identifier)
        self.assertEqual(sublayer2_item.identifier, sublayer1.identifier)
        self.assertEqual(sublayer3_item.identifier, sublayer2.identifier)

        layer_model.drop(sublayer3_item, sublayer2_item, -1)
        await self._wait()
        self.assertEqual(len(root_layer_item.sublayers), 2)
        self.assertEqual(len(sublayer3_item.sublayers), 1)
        self.assertEqual(sublayer3_item.sublayers[0].identifier, sublayer2_item.identifier)
