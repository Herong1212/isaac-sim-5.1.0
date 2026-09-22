import os
import string
import random
import unittest
import carb
import omni
import omni.kit.test
import omni.usd
import omni.client
import omni.kit.widget.layers
from pathlib import Path
from omni.kit.usd.layers import LayerUtils
from pxr import Sdf, Usd, UsdGeom
from .base import TestLayerNonUIBase


class TestLayerMisc(TestLayerNonUIBase):

    def get_random_string(self):
        return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

    async def test_layer_release(self):
        # Test fix for https://nvidia-omniverse.atlassian.net/browse/OM-18672
        current_path = Path(__file__).parent
        test_data_path = current_path.parent.parent.parent.parent.parent.joinpath("data")
        sublayer_path = str(test_data_path.joinpath("sublayer.usd"))

        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        stage = usd_context.get_stage()
        root_layer = stage.GetRootLayer()
        sublayer = LayerUtils.insert_sublayer(root_layer, 0, sublayer_path)
        identifier = sublayer.identifier
        self.assertTrue(sublayer != None)
        sublayer = None  # Release the ref count
        # Remove sublayer to remove it from layer stack and also its reference from Layer Window
        LayerUtils.remove_sublayer(root_layer, 0)
        sublayer = Sdf.Find(identifier)
        self.assertTrue(sublayer == None)

        sublayer = LayerUtils.insert_sublayer(root_layer, 0, sublayer_path)
        identifier = sublayer.identifier
        self.assertTrue(sublayer != None)
        sublayer = None  # Release the ref count

        # Reopen stage to see if the sublayer has been released
        await usd_context.new_stage_async()
        sublayer = Sdf.Find(identifier)
        self.assertTrue(sublayer == None)

    async def test_layer_dirtiness_after_save(self):
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()

        # Manually set current edit target identifier
        self.layers_instance = omni.kit.widget.layers.get_instance()
        layer_model = self.layers_instance.get_layer_model()
        layer_model._edit_target_identifier = usd_context.get_stage_url()

        token = carb.tokens.get_tokens_interface()
        temp_dir = token.resolve("${temp}")
        temp_usd = os.path.join(temp_dir, f"{self.get_random_string()}.usd")
        temp_usd = omni.client.normalize_url(temp_usd)

        success, _, saved_layers = await usd_context.save_layers_async(temp_usd, [])
        self.assertTrue(success)
        self.assertEqual(len(saved_layers), 0)

        # Wait two frames to wait update event of layer_model to authoring edit target.
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # Manually trigger on update to try to update edit target into root layer.
        layer_model._pending_changed_edit_target = temp_usd
        layer_model._on_update(0.0)

        # Check dirtiness to make sure it's not dirty.
        stage = usd_context.get_stage()
        root_layer = stage.GetRootLayer()
        self.assertFalse(root_layer.dirty)

    async def test_create_sublayer_with_stage_axis(self):
        usd_context = omni.usd.get_context()
        for axis in [UsdGeom.Tokens.y, UsdGeom.Tokens.z]:
            await usd_context.new_stage_async()

            stage = usd_context.get_stage()
            UsdGeom.SetStageUpAxis(stage, axis)

            sublayer = Sdf.Layer.CreateAnonymous()
            omni.kit.commands.execute(
                "CreateSublayer",
                layer_identifier=stage.GetRootLayer().identifier,
                sublayer_position=0,
                new_layer_path=sublayer.identifier,
                transfer_root_content=False,
                create_or_insert=True,
            )

            sublayer_stage = Usd.Stage.Open(sublayer)
            self.assertEqual(UsdGeom.GetStageUpAxis(sublayer_stage), axis)
