import asyncio
import carb
import os
import tempfile
import omni.kit.test
import omni.usd
import omni.client
import omni.kit.usd.layers as layers

from omni.kit.usd.layers import get_layers, LayerEditMode, get_layer_event_payload, LayerEventType


class TestLayersInterface(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.usd_context = omni.usd.get_context()
        await omni.usd.get_context().new_stage_async()

    async def tearDown(self):
        if omni.usd.get_context().get_stage():
            await omni.usd.get_context().close_stage_async()

        layers = get_layers()
        layers.set_edit_mode(LayerEditMode.NORMAL)

    async def test_get_interfaces(self):
        self.assertTrue(layers.get_auto_authoring())
        self.assertFalse(layers.get_auto_authoring("__not_exist__"))

        self.assertTrue(layers.get_layers_state())
        self.assertFalse(layers.get_layers_state("__not_exist__"))

        self.assertTrue(layers.get_layers())
        self.assertFalse(layers.get_layers("__not_exist__"))

        self.assertTrue(layers.get_live_syncing())
        self.assertFalse(layers.get_live_syncing("__not_exist__"))

    async def test_active_context(self):
        with layers.active_authoring_layer_context(self.usd_context):
            stage = self.usd_context.get_stage()
            self.assertEqual(stage.GetEditTarget().GetLayer(), stage.GetRootLayer())

        layers_interface = get_layers()
        layers_interface.set_edit_mode(LayerEditMode.AUTO_AUTHORING)
        with layers.active_authoring_layer_context(self.usd_context):
            stage = self.usd_context.get_stage()
            self.assertEqual(stage.GetEditTarget().GetLayer(), stage.GetRootLayer())

    async def test_edit_mode_switch(self):
        layers = get_layers()
        event_stream = layers.get_event_stream()

        payload = None

        def _on_layer_event(event: carb.events.IEvent):
            nonlocal payload
            temp = get_layer_event_payload(event)
            if temp.event_type == LayerEventType.EDIT_MODE_CHANGED:
                payload = temp

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="Layers Interface Tests")

        self.assertEqual(layers.get_edit_mode(), LayerEditMode.NORMAL)

        def change_edit_mode_and_verify(edit_mode):
            nonlocal payload
            payload = None
            layers.set_edit_mode(edit_mode)
            self.assertIsNotNone(payload)
            self.assertEqual(payload.event_type, LayerEventType.EDIT_MODE_CHANGED)
            self.assertEqual(layers.get_edit_mode(), edit_mode)

        change_edit_mode_and_verify(LayerEditMode.AUTO_AUTHORING)
        change_edit_mode_and_verify(LayerEditMode.SPECS_LINKING)
        change_edit_mode_and_verify(LayerEditMode.NORMAL)
