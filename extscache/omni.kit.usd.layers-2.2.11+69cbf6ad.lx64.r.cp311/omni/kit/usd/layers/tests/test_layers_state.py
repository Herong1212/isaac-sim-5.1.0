import asyncio
import carb
import os
import tempfile
import omni.kit.test
import omni.usd
import omni.client
import unittest
import random

from stat import S_IREAD, S_IWRITE
from pxr import Sdf, Usd, UsdGeom, Gf
from .test_base import enable_server_tests
from omni.kit.usd.layers import get_layers, LayerUtils, get_layer_event_payload, LayerEventType


class TestLayersState(omni.kit.test.AsyncTestCase):

    # Before running each test
    async def setUp(self):
        self.__previous_retry_values = omni.client.set_retries(0, 0, 0)
        self.usd_context = omni.usd.get_context()
        await omni.usd.get_context().new_stage_async()

    async def tearDown(self):
        if omni.usd.get_context().get_stage():
            await omni.usd.get_context().close_stage_async()
        omni.client.set_retries(*self.__previous_retry_values)

    async def test_auto_reload_apis(self):
        layers = get_layers()
        layers_state = layers.get_layers_state()

        stage = omni.usd.get_context().get_stage()
        event_stream = layers.get_event_stream()

        payload = None

        def _on_layer_event(event: carb.events.IEvent):
            nonlocal payload
            event_payload = get_layer_event_payload(event)
            if event_payload.event_type == LayerEventType.AUTO_RELOAD_LAYERS_CHANGED:
                payload = event_payload

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")

        root_layer_id = stage.GetRootLayer().identifier

        success = layers_state.add_auto_reload_layer(root_layer_id)
        self.assertTrue(success)
        self.assertTrue(layers_state.is_auto_reload_layer(root_layer_id))
        await self._wait()

        self.assertTrue(payload)
        self.assertEqual(payload.event_type, LayerEventType.AUTO_RELOAD_LAYERS_CHANGED)
        self.assertEqual(payload.layer_identifier, root_layer_id)
        self.assertEqual(payload.identifiers_or_spec_paths, [root_layer_id])
        self.assertFalse(payload.is_layer_influenced(stage.GetSessionLayer().identifier))
        self.assertFalse(payload.is_layer_influenced(stage.GetSessionLayer()))
        self.assertTrue(payload.is_layer_influenced(stage.GetRootLayer()))
        self.assertTrue(payload.is_layer_influenced(root_layer_id))

        payload = None
        fail = layers_state.add_auto_reload_layer("xxxxx")
        self.assertFalse(fail)
        self.assertFalse(payload)

        layers_state.remove_auto_reload_layer(root_layer_id)
        self.assertFalse(layers_state.is_auto_reload_layer(root_layer_id))
        await self._wait()
        self.assertTrue(payload)
        self.assertEqual(payload.event_type, LayerEventType.AUTO_RELOAD_LAYERS_CHANGED)
        self.assertEqual(payload.layer_identifier, root_layer_id)
        self.assertEqual(payload.identifiers_or_spec_paths, [root_layer_id])
        self.assertFalse(payload.is_layer_influenced(stage.GetSessionLayer().identifier))
        self.assertFalse(payload.is_layer_influenced(stage.GetSessionLayer()))
        self.assertTrue(payload.is_layer_influenced(stage.GetRootLayer()))
        self.assertTrue(payload.is_layer_influenced(root_layer_id))

    async def test_layers_state_muteness_interfaces(self):
        layers = get_layers()
        layers_state = layers.get_layers_state()

        stage = omni.usd.get_context().get_stage()

        layer0 = Sdf.Layer.CreateAnonymous()
        layer1 = Sdf.Layer.CreateAnonymous()
        layer2 = Sdf.Layer.CreateAnonymous()
        stage.GetRootLayer().subLayerPaths.append(layer0.identifier)
        stage.GetRootLayer().subLayerPaths.append(layer1.identifier)
        stage.GetRootLayer().subLayerPaths.append(layer2.identifier)

        self.assertFalse(layers_state.is_muteness_global())

        stage.MuteLayer(layer0.identifier)
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(layers_state.is_layer_locally_muted(layer0.identifier))
        self.assertFalse(layers_state.is_layer_globally_muted(layer0.identifier))
        self.assertFalse(layers_state.is_layer_locally_muted(layer1.identifier))
        self.assertFalse(layers_state.is_layer_locally_muted(layer2.identifier))

        stage.UnmuteLayer(layer0.identifier)
        await omni.kit.app.get_app().next_update_async()
        self.assertFalse(layers_state.is_layer_locally_muted(layer0.identifier))

        # Mute layers before muteness scope switches.
        stage.MuteLayer(layer0.identifier)
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(layers_state.is_layer_locally_muted(layer0.identifier))
        layers_state.set_muteness_scope(True)
        self.assertTrue(layers_state.is_muteness_global())
        self.assertTrue(layers_state.is_layer_locally_muted(layer0.identifier))
        self.assertFalse(layers_state.is_layer_globally_muted(layer0.identifier))
        # Layer is not muted since it's muted in local mode.
        self.assertFalse(stage.IsLayerMuted(layer0.identifier))

        stage.MuteLayer(layer0.identifier)
        await omni.kit.app.get_app().next_update_async()
        # Local muteness flag is still true.
        self.assertTrue(layers_state.is_layer_locally_muted(layer0.identifier))
        self.assertTrue(layers_state.is_layer_globally_muted(layer0.identifier))
        self.assertTrue(stage.IsLayerMuted(layer0.identifier))
        stage.UnmuteLayer(layer0.identifier)
        await omni.kit.app.get_app().next_update_async()
        self.assertFalse(layers_state.is_layer_globally_muted(layer0.identifier))
        self.assertFalse(stage.IsLayerMuted(layer0.identifier))

        # Swiches back to local scope again.
        layers_state.set_muteness_scope(False)
        self.assertTrue(layers_state.is_layer_locally_muted(layer0.identifier))
        self.assertFalse(layers_state.is_layer_globally_muted(layer0.identifier))
        self.assertTrue(stage.IsLayerMuted(layer0.identifier))

        # Pass None for identifier will not cause any issues
        self.assertFalse(layers_state.is_layer_locally_muted(None))

    async def test_live_update_muteness(self):
        # The test is not to do real live update, but tries to simulate live update
        # by changing the custom data of muteness directly.
        layers = get_layers()
        layers_state = layers.get_layers_state()
        layers_state.set_muteness_scope(False)

        stage = omni.usd.get_context().get_stage()
        layer0 = Sdf.Layer.CreateAnonymous()
        stage.GetRootLayer().subLayerPaths.append(layer0.identifier)
        LayerUtils.set_layer_global_muteness(stage.GetRootLayer(), layer0.identifier, True)
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(layers_state.is_layer_globally_muted(layer0.identifier))
        self.assertFalse(stage.IsLayerMuted(layer0.identifier))

        layers_state.set_muteness_scope(True)
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(layers_state.is_layer_globally_muted(layer0.identifier))
        self.assertTrue(stage.IsLayerMuted(layer0.identifier))

    async def test_permissions_query_interface(self):
        layers = get_layers()
        layers_state = layers.get_layers_state()
        with tempfile.TemporaryDirectory() as tempdir:
            file = os.path.join(tempdir, "test.usd")
            layer = Sdf.Layer.CreateNew(file)
            layer.Save()
            layer = None
            os.chmod(file, S_IREAD)

            await omni.usd.get_context().open_stage_async(file)
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            is_writable = layers_state.is_layer_writable(file)
            is_read_only_on_disk = layers_state.is_layer_readonly_on_disk(file)
            is_savable = layers_state.is_layer_savable(file)
            await omni.usd.get_context().new_stage_async()

            os.chmod(file, S_IWRITE)

        self.assertFalse(is_writable)
        self.assertTrue(is_read_only_on_disk)
        self.assertFalse(is_savable)
        self.assertFalse(layers_state.is_layer_locked(file))

        stage = omni.usd.get_context().get_stage()
        root_layer = stage.GetRootLayer()
        LayerUtils.set_layer_lock_status(root_layer, root_layer.identifier, True)
        # Root layer cannot be locked
        self.assertTrue(layers_state.is_layer_writable(root_layer.identifier))
        # Anonymous layer cannot be saved.
        self.assertFalse(layers_state.is_layer_savable(root_layer.identifier))
        self.assertFalse(layers_state.is_layer_locked(file))

        with tempfile.TemporaryDirectory() as tempdir:
            file = os.path.join(tempdir, "test.usd")
            layer = Sdf.Layer.CreateNew(file)
            root_layer.subLayerPaths.append(file)
            LayerUtils.set_layer_lock_status(root_layer, file, True)

            # Locked layer cannot be writable or savable.
            self.assertFalse(layers_state.is_layer_writable(file))
            # Even it's locked, it's still not readonly on disk.
            self.assertFalse(layers_state.is_layer_readonly_on_disk(file))
            self.assertFalse(layers_state.is_layer_savable(file))
            self.assertTrue(layers_state.is_layer_locked(file))

            # Close stage to release temp file
            layer = None
            stage = None
            root_layer = None
            await omni.usd.get_context().close_stage_async()

    async def test_set_get_layer_names(self):
        layers = get_layers()
        layers_state = layers.get_layers_state()
        stage = omni.usd.get_context().get_stage()
        root_layer = stage.GetRootLayer()
        session_layer = stage.GetSessionLayer()

        self.assertEqual(layers_state.get_layer_name(root_layer.identifier), "Root Layer")
        self.assertEqual(layers_state.get_layer_name(session_layer.identifier), "Session Layer")

        sublayer = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(sublayer.identifier)
        layers_state.set_layer_name(sublayer.identifier, "test")
        self.assertEqual(layers_state.get_layer_name(sublayer.identifier), "test")

        self.assertEqual("abc.usd", layers_state.get_layer_name("c:/a/b/abc.usd"))
        self.assertEqual("abc.usda", layers_state.get_layer_name("c:/a/b/abc.usda"))
        self.assertEqual("abc.usda", layers_state.get_layer_name("omniverse://ov-invalid-fake-server/a/b/abc.usda"))
        layer = Sdf.Layer.CreateAnonymous()
        self.assertEqual(layer.identifier, layers_state.get_layer_name(layer.identifier))
        self.assertEqual("", layers_state.get_layer_name(""))
        self.assertEqual(
            "a b c.usda", layers_state.get_layer_name("omniverse://ov-invalid-fake-server/a/b/a%20b%20c.usda")
        )

    async def _wait(self, frames=3):
        for i in range(frames):
            await omni.kit.app.get_app().next_update_async()

    async def test_layers_check(self):
        stage = omni.usd.get_context().get_stage()
        layers = get_layers()
        layers_state = layers.get_layers_state()

        with tempfile.TemporaryDirectory() as tempdir:
            file = os.path.join(tempdir, "test.usd")
            file1 = os.path.join(tempdir, "test1.usd")
            layer = Sdf.Layer.CreateNew(file)
            layer1 = Sdf.Layer.CreateNew(file1)
            stage.GetRootLayer().subLayerPaths.append(file)

            prim = stage.DefinePrim("/root")
            prim.GetReferences().AddReference(file1)
            await self._wait(2)

            self.assertTrue(layers_state.has_local_layer(stage.GetRootLayer().identifier))
            self.assertTrue(layers_state.has_local_layer(stage.GetSessionLayer().identifier))
            self.assertFalse(layers_state.has_local_layer(layer1.identifier))
            self.assertTrue(layers_state.has_local_layer(layer.identifier))
            self.assertTrue(layers_state.has_used_layer(layer.identifier))
            self.assertTrue(layers_state.has_used_layer(layer1.identifier))
            self.assertTrue(layers_state.has_used_layer(stage.GetRootLayer().identifier))
            self.assertTrue(layers_state.has_used_layer(stage.GetSessionLayer().identifier))

            layer = None
            layer1 = None
            await omni.usd.get_context().close_stage_async()

    @unittest.skipIf(not enable_server_tests(), "")
    async def test_layer_auto_reload(self):  # pragma: no cover
        layers = get_layers()
        layers_state = layers.get_layers_state()
        stage = omni.usd.get_context().get_stage()

        all_layers = []
        for i in range(3):
            file = f"omniverse://localhost/Projects/tests/omni.kit.usd.layers/test_layer_refresh/test{i}.usd"
            layer = Sdf.Layer.FindOrOpen(file)
            if not layer:
                layer = Sdf.Layer.CreateNew(file)
                layer.Save()

            all_layers.append(layer)

        layer1 = all_layers[0]
        stage.GetRootLayer().subLayerPaths.append(layer1.identifier)
        await omni.kit.app.get_app().next_update_async()
        self.assertFalse(layers_state.is_layer_outdated(layer1.identifier))

        layer2 = all_layers[1]
        prim = stage.DefinePrim("/test")
        prim.GetReferences().AddReference(layer2.identifier)
        await omni.kit.app.get_app().next_update_async()
        self.assertFalse(layers_state.is_layer_outdated(layer2.identifier))

        layer3 = all_layers[2]
        prim = stage.DefinePrim("/test2")
        prim.GetPayloads().AddPayload(layer3.identifier)
        self.assertFalse(layers_state.is_layer_outdated(layer3.identifier))

        self.assertFalse(layers_state.is_auto_reload_layer(layer1.identifier))
        self.assertEqual(layers_state.get_auto_reload_layers(), [])
        layers_state.add_auto_reload_layer(layer1.identifier)
        self.assertTrue(layers_state.is_auto_reload_layer(layer1.identifier))
        self.assertEqual(layers_state.get_auto_reload_layers(), [layer1.identifier])
        layers_state.remove_auto_reload_layer(layer1.identifier)
        self.assertEqual(layers_state.get_auto_reload_layers(), [])
        layers_state.add_auto_reload_layer(layer1.identifier)

        for layer in all_layers:
            custom_data = layer.customLayerData
            custom_data['test'] = random.randint(0, 10000000)
            layer.customLayerData = custom_data
            layer.Save(True)
            await self._wait(100)

            # Save with USD layer interface will not make it outdated
            self.assertFalse(layers_state.is_layer_outdated(layer.identifier))

            result, _, content = await omni.client.read_file_async(layer.identifier)
            self.assertEqual(result, omni.client.Result.OK)
            # Simulates of multi-clients edits
            result = await omni.client.write_file_async(layer.identifier, content)
            self.assertEqual(result, omni.client.Result.OK)
            await asyncio.sleep(3.0)
            identifier = layer.identifier

            # Layer1 is auto-reloaded
            if layer == layer1:
                self.assertFalse(layers_state.is_layer_outdated(layer.identifier), identifier)
            else:
                self.assertTrue(layers_state.is_layer_outdated(layer.identifier), identifier)

    @unittest.skipIf(not enable_server_tests(), "")
    async def test_layer_refresh(self):  # pragma: no cover
        layers = get_layers()
        layers_state = layers.get_layers_state()
        stage = omni.usd.get_context().get_stage()
        event_stream = layers.get_event_stream()

        payload = None

        def _on_layer_event(event: carb.events.IEvent):
            nonlocal payload
            event_payload = get_layer_event_payload(event)
            if event_payload.event_type == LayerEventType.OUTDATE_STATE_CHANGED:
                payload = event_payload

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")

        all_layers = []
        for i in range(3):
            file = f"omniverse://localhost/Projects/tests/omni.kit.usd.layers/test_layer_refresh/test{i}.usd"
            layer = Sdf.Layer.FindOrOpen(file)
            if not layer:
                layer = Sdf.Layer.CreateNew(file)
                layer.Save()

            all_layers.append(layer)

        layer1 = all_layers[0]
        stage.GetRootLayer().subLayerPaths.append(layer1.identifier)
        await omni.kit.app.get_app().next_update_async()
        self.assertFalse(layers_state.is_layer_outdated(layer1.identifier))

        layer2 = all_layers[1]
        prim = stage.DefinePrim("/test")
        prim.GetReferences().AddReference(layer2.identifier)
        self.assertFalse(layers_state.is_layer_outdated(layer2.identifier))

        layer3 = all_layers[2]
        prim = stage.DefinePrim("/test2")
        prim.GetPayloads().AddPayload(layer3.identifier)
        self.assertFalse(layers_state.is_layer_outdated(layer3.identifier))

        for i in range(2):
            for layer in all_layers:
                payload = None
                custom_data = layer.customLayerData
                custom_data['test'] = random.randint(0, 10000000)
                layer.customLayerData = custom_data
                layer.Save(True)
                await self._wait(100)

                # Save with USD layer interface will not make it outdated
                self.assertFalse(layers_state.is_layer_outdated(layer.identifier))
                self.assertTrue(payload is None)

                result, _, content = await omni.client.read_file_async(layer.identifier)
                self.assertEqual(result, omni.client.Result.OK)
                # Simulates of multi-clients edits
                payload = None
                result = await omni.client.write_file_async(layer.identifier, content)
                self.assertEqual(result, omni.client.Result.OK)
                await asyncio.sleep(3.0)
                identifier = layer.identifier
                self.assertTrue(layers_state.is_layer_outdated(layer.identifier), identifier)
                self.assertTrue(payload)
                self.assertEqual(payload.identifiers_or_spec_paths, [layer.identifier])

            outdate_sublayers = layers_state.get_outdated_sublayer_identifiers()
            outdate_non_sublayers = layers_state.get_outdated_non_sublayer_identifiers()
            all_layers_identifiers = layers_state.get_all_outdated_layer_identifiers()
            self.assertEqual(outdate_sublayers, [layer1.identifier])
            self.assertEqual(set(outdate_non_sublayers), set([layer2.identifier, layer3.identifier]))
            self.assertEqual(set(all_layers_identifiers), set([layer1.identifier, layer2.identifier, layer3.identifier]))

            if i == 0:
                payload = None
                layers_state.reload_outdated_sublayers()
                self.assertFalse(layers_state.is_layer_outdated(layer1.identifier))
                self.assertTrue(layers_state.is_layer_outdated(layer2.identifier))
                self.assertTrue(layers_state.is_layer_outdated(layer3.identifier))
                await self._wait(2)
                self.assertTrue(payload)
                self.assertEqual(payload.identifiers_or_spec_paths, [layer1.identifier])

                payload = None
                layers_state.reload_outdated_non_sublayers()
                self.assertFalse(layers_state.is_layer_outdated(layer1.identifier))
                self.assertFalse(layers_state.is_layer_outdated(layer2.identifier))
                self.assertFalse(layers_state.is_layer_outdated(layer3.identifier))
                await self._wait(2)
                self.assertTrue(payload)
                self.assertEqual(set(payload.identifiers_or_spec_paths), set([layer2.identifier, layer3.identifier]))
            else:
                payload = None
                layers_state.reload_all_outdated_layers()
                await self._wait(2)
                self.assertFalse(layers_state.is_layer_outdated(layer1.identifier))
                self.assertFalse(layers_state.is_layer_outdated(layer2.identifier))
                self.assertFalse(layers_state.is_layer_outdated(layer3.identifier))
                await self._wait(2)
                self.assertTrue(payload)
                self.assertEqual(set(payload.identifiers_or_spec_paths), set([layer1.identifier, layer2.identifier, layer3.identifier]))

    async def test_layer_edit_target_changed(self):
        # Test layer edit target change if it's muted/locked/removed.
        layers = get_layers()
        layers_state = layers.get_layers_state()
        stage = omni.usd.get_context().get_stage()
        sublayer0 = Sdf.Layer.CreateAnonymous()
        root_layer = stage.GetRootLayer()
        LayerUtils.insert_sublayer(root_layer, 0, sublayer0.identifier, False)

        # Mute/lock/remove current edit target will change its edit target to root layer.
        LayerUtils.set_edit_target(stage, sublayer0.identifier)
        self.assertEqual(sublayer0.identifier, LayerUtils.get_edit_target(stage))
        stage.MuteLayer(sublayer0.identifier)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(root_layer.identifier, LayerUtils.get_edit_target(stage))

        stage.UnmuteLayer(sublayer0.identifier)
        LayerUtils.set_edit_target(stage, sublayer0.identifier)
        self.assertEqual(sublayer0.identifier, LayerUtils.get_edit_target(stage))
        layers_state.set_layer_lock_state(sublayer0.identifier, True)
        self.assertEqual(root_layer.identifier, LayerUtils.get_edit_target(stage))

        layers_state.set_layer_lock_state(sublayer0.identifier, False)
        LayerUtils.set_edit_target(stage, sublayer0.identifier)
        self.assertEqual(sublayer0.identifier, LayerUtils.get_edit_target(stage))
        LayerUtils.remove_sublayer(root_layer, 0)
        self.assertEqual(root_layer.identifier, LayerUtils.get_edit_target(stage))

    async def test_layer_muteness_events(self):
        layers = get_layers()
        layers_state = layers.get_layers_state()
        event_stream = layers.get_event_stream()

        payload = None

        def _on_layer_event(event: carb.events.IEvent):
            nonlocal payload
            payload = get_layer_event_payload(event)

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")
        layers_state = layers.get_layers_state()
        layers_state.set_muteness_scope(True)

        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.MUTENESS_SCOPE_CHANGED)

        stage = omni.usd.get_context().get_stage()
        sublayer0 = Sdf.Layer.CreateAnonymous()
        sublayer1 = Sdf.Layer.CreateAnonymous()
        root_layer = stage.GetRootLayer()
        LayerUtils.insert_sublayer(root_layer, 0, sublayer0.identifier, False)
        LayerUtils.insert_sublayer(root_layer, 1, sublayer1.identifier, False)
        await omni.kit.app.get_app().next_update_async()

        stage.MuteAndUnmuteLayers([sublayer0.identifier, sublayer1.identifier], [])
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.MUTENESS_STATE_CHANGED)
        self.assertEqual(set(payload.identifiers_or_spec_paths), set([sublayer0.identifier, sublayer1.identifier]))
        self.assertFalse(payload.is_layer_influenced(stage.GetSessionLayer()))
        self.assertTrue(payload.is_layer_influenced(sublayer0))
        self.assertTrue(payload.is_layer_influenced(sublayer1))

        stage.UnmuteLayer(sublayer1.identifier)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.MUTENESS_STATE_CHANGED)
        self.assertEqual(set(payload.identifiers_or_spec_paths), set([sublayer1.identifier]))
        self.assertFalse(payload.is_layer_influenced(stage.GetSessionLayer()))
        self.assertTrue(payload.is_layer_influenced(sublayer1))
        self.assertFalse(payload.is_layer_influenced(sublayer0))

        layers_state.set_muteness_scope(False)
        # Switch scope will load local muteness.
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.MUTENESS_STATE_CHANGED)
        # Since only sublayer0's state is changed.
        self.assertEqual(set(payload.identifiers_or_spec_paths), set([sublayer0.identifier]))
        self.assertFalse(payload.is_layer_influenced(stage.GetSessionLayer()))
        self.assertTrue(payload.is_layer_influenced(sublayer0))
        self.assertFalse(payload.is_layer_influenced(sublayer1))

    async def test_layer_lock_events(self):
        layers = get_layers()
        layers_state = layers.get_layers_state()
        event_stream = layers.get_event_stream()

        payload = None

        def _on_layer_event(event: carb.events.IEvent):
            nonlocal payload
            payload = get_layer_event_payload(event)

        stage = omni.usd.get_context().get_stage()
        sublayer0 = Sdf.Layer.CreateAnonymous()
        sublayer1 = Sdf.Layer.CreateAnonymous()
        root_layer = stage.GetRootLayer()
        LayerUtils.insert_sublayer(root_layer, 0, sublayer0.identifier, False)
        LayerUtils.insert_sublayer(root_layer, 1, sublayer1.identifier, False)

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")

        # Lock
        layers_state.set_layer_lock_state(sublayer0.identifier, True)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.LOCK_STATE_CHANGED)
        self.assertEqual(set(payload.identifiers_or_spec_paths), set([sublayer0.identifier]))
        self.assertFalse(payload.is_layer_influenced(stage.GetSessionLayer()))
        self.assertTrue(payload.is_layer_influenced(sublayer0))
        self.assertFalse(payload.is_layer_influenced(sublayer1))

        # Unlock
        payload = None
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        layers_state.set_layer_lock_state(sublayer0.identifier, False)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.LOCK_STATE_CHANGED)
        self.assertEqual(set(payload.identifiers_or_spec_paths), set([sublayer0.identifier]))
        self.assertFalse(payload.is_layer_influenced(stage.GetSessionLayer()))
        self.assertTrue(payload.is_layer_influenced(sublayer0))
        self.assertFalse(payload.is_layer_influenced(sublayer1))

        payload = None
        with Sdf.ChangeBlock():
            LayerUtils.set_layer_lock_status(root_layer, sublayer0.identifier, True)
            LayerUtils.set_layer_lock_status(root_layer, sublayer1.identifier, True)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.LOCK_STATE_CHANGED)
        self.assertEqual(set(payload.identifiers_or_spec_paths), set([sublayer0.identifier, sublayer1.identifier]))
        self.assertFalse(payload.is_layer_influenced(stage.GetSessionLayer()))
        self.assertTrue(payload.is_layer_influenced(sublayer0))
        self.assertTrue(payload.is_layer_influenced(sublayer1))

    async def test_layer_dirty_state_events(self):
        layers = get_layers()
        event_stream = layers.get_event_stream()

        payload = None

        def _on_layer_event(event: carb.events.IEvent):
            nonlocal payload
            temp = get_layer_event_payload(event)
            if temp.event_type == LayerEventType.DIRTY_STATE_CHANGED:
                payload = temp

        with tempfile.TemporaryDirectory() as tempdir:
            file = os.path.join(tempdir, "test.usd")
            file1 = os.path.join(tempdir, "test1.usd")
            layer = Sdf.Layer.CreateNew(file)
            layer.Save()

            layer1 = Sdf.Layer.CreateNew(file1)
            layer1.Save()

            stage = omni.usd.get_context().get_stage()
            root_layer = stage.GetRootLayer()
            LayerUtils.insert_sublayer(root_layer, 0, layer.identifier, False)
            LayerUtils.insert_sublayer(root_layer, 1, layer1.identifier, False)

            subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")

            # Change anonymous layer will not emit dirty event
            with Usd.EditContext(stage, stage.GetRootLayer()):
                stage.DefinePrim("/root/prim")
                await omni.kit.app.get_app().next_update_async()
                self.assertIsNone(payload)

            with Usd.EditContext(stage, layer):
                stage.DefinePrim("/root/prim2")
                await omni.kit.app.get_app().next_update_async()
                self.assertIsNotNone(payload)
                self.assertEqual(payload.event_type, LayerEventType.DIRTY_STATE_CHANGED)
                self.assertEqual(set(payload.identifiers_or_spec_paths), set([layer.identifier]))
                self.assertFalse(payload.is_layer_influenced(stage.GetSessionLayer()))
                self.assertTrue(payload.is_layer_influenced(layer))
                self.assertTrue(layer.dirty)

                # Change a dirty layer will not emit dirty event again
                payload = None
                stage.DefinePrim("/root/prim3")
                self.assertIsNone(payload)

            with Usd.EditContext(stage, layer1):
                stage.DefinePrim("/root/prim4")
                await omni.kit.app.get_app().next_update_async()

            # Save dirty layers will emit dirty change event
            payload = None
            stage.Save()
            await omni.kit.app.get_app().next_update_async()
            self.assertIsNotNone(payload)
            self.assertEqual(payload.event_type, LayerEventType.DIRTY_STATE_CHANGED)
            self.assertEqual(set(payload.identifiers_or_spec_paths), set([layer.identifier, layer1.identifier]))
            self.assertFalse(payload.is_layer_influenced(stage.GetSessionLayer()))
            self.assertTrue(payload.is_layer_influenced(layer))
            self.assertTrue(payload.is_layer_influenced(layer1))
            self.assertFalse(layer.dirty)
            self.assertFalse(layer1.dirty)

            layer = None
            layer1 = None
            root_layer = None
            await omni.usd.get_context().new_stage_async()

    async def test_layer_prim_specs_events(self):
        layers = get_layers()
        event_stream = layers.get_event_stream()

        payload = None

        def _on_layer_event(event: carb.events.IEvent):
            nonlocal payload
            temp = get_layer_event_payload(event)
            if temp.event_type == LayerEventType.PRIM_SPECS_CHANGED:
                payload = temp

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")

        stage = omni.usd.get_context().get_stage()
        all_prims = []
        for i in range(100):
            prim = stage.DefinePrim(f"/test_{i}")
            all_prims.append(str(prim.GetPath()))

        await omni.kit.app.get_app().next_update_async()
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.PRIM_SPECS_CHANGED)
        root_layer_identifier = stage.GetRootLayer().identifier
        self.assertIn(root_layer_identifier, payload.layer_spec_paths)
        self.assertEqual(set(payload.layer_spec_paths[root_layer_identifier]), set(all_prims))
        self.assertEqual(set(payload.identifiers_or_spec_paths), set([root_layer_identifier]))
        self.assertEqual(payload.layer_identifier, root_layer_identifier)
        self.assertFalse(payload.is_layer_influenced(stage.GetSessionLayer()))
        self.assertTrue(payload.is_layer_influenced(root_layer_identifier))

        stage.GetRootLayer().Clear()
        await omni.kit.app.get_app().next_update_async()
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.PRIM_SPECS_CHANGED)
        root_layer_identifier = stage.GetRootLayer().identifier
        self.assertIn(root_layer_identifier, payload.layer_spec_paths)
        self.assertEqual(set(payload.layer_spec_paths[root_layer_identifier]), set([str(Sdf.Path.absoluteRootPath)]))

    async def test_sublayers_changed_events(self):
        layers = get_layers()
        event_stream = layers.get_event_stream()

        payload = None

        def _on_layer_event(event: carb.events.IEvent):
            nonlocal payload
            temp = get_layer_event_payload(event)
            if temp.event_type == LayerEventType.SUBLAYERS_CHANGED:
                payload = temp

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")

        stage = omni.usd.get_context().get_stage()
        root_layer = stage.GetRootLayer()
        sublayer0 = Sdf.Layer.CreateAnonymous()
        sublayer1 = Sdf.Layer.CreateAnonymous()

        root_layer.subLayerPaths.append(sublayer0.identifier)
        await omni.kit.app.get_app().next_update_async()
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.SUBLAYERS_CHANGED)

        payload = None
        LayerUtils.remove_sublayer(root_layer, 0)
        await omni.kit.app.get_app().next_update_async()
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.SUBLAYERS_CHANGED)

        root_layer.subLayerPaths.append(sublayer0.identifier)
        root_layer.subLayerPaths.append(sublayer1.identifier)

        # Layer move
        payload = None
        LayerUtils.move_layer(root_layer.identifier, 0, sublayer1.identifier, 0, True)
        await omni.kit.app.get_app().next_update_async()
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.SUBLAYERS_CHANGED)

        # Not all edits will emit sublayer changes events.
        payload = None
        stage.DefinePrim("/root/test")
        self.assertIsNone(payload)

    async def test_layer_info_changed_events(self):
        layers = get_layers()
        event_stream = layers.get_event_stream()

        payload = None

        def _on_layer_event(event: carb.events.IEvent):
            nonlocal payload
            temp = get_layer_event_payload(event)
            if temp.event_type == LayerEventType.INFO_CHANGED:
                payload = temp

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")

        stage = omni.usd.get_context().get_stage()
        root_layer = stage.GetRootLayer()
        sublayer0 = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(sublayer0.identifier)
        root_layer.subLayerOffsets[0] = Sdf.LayerOffset(2.0, 3.0)

        up_axis = UsdGeom.GetStageUpAxis(stage)
        with Sdf.ChangeBlock():
            if up_axis == UsdGeom.Tokens.z:
                UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
            else:
                UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)

            root_layer.comment = "test"
            root_layer.documentation = "test2"

            UsdGeom.SetStageMetersPerUnit(stage, 100.0)

            stage.SetStartTimeCode(100.99)
            stage.SetEndTimeCode(1000.99)
            root_layer.framesPerSecond = 100
            stage.SetTimeCodesPerSecond(1000)

        await omni.kit.app.get_app().next_update_async()
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.INFO_CHANGED)
        self.assertIn(root_layer.identifier, payload.layer_info_data)
        expected_changes = (
            "documentation",
            "upAxis",
            "comment",
            "metersPerUnit",
            "startTimeCode",
            "framesPerSecond",
            "endTimeCode",
            "timeCodesPerSecond",
        )
        self.assertEqual(set(payload.layer_info_data[root_layer.identifier]), set(expected_changes))
        self.assertEqual(set(payload.identifiers_or_spec_paths), set([root_layer.identifier]))
        self.assertEqual(payload.layer_identifier, root_layer.identifier)
        self.assertFalse(payload.is_layer_influenced(stage.GetSessionLayer()))
        self.assertTrue(payload.is_layer_influenced(root_layer))

    async def test_edit_target_changed(self):
        layers = get_layers()
        event_stream = layers.get_event_stream()

        payload = None

        def _on_layer_event(event: carb.events.IEvent):
            nonlocal payload
            temp = get_layer_event_payload(event)
            if temp.event_type == LayerEventType.EDIT_TARGET_CHANGED:
                payload = temp

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")

        stage = omni.usd.get_context().get_stage()
        root_layer = stage.GetRootLayer()
        sublayer0 = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(sublayer0.identifier)

        edit_target = stage.GetEditTargetForLocalLayer(sublayer0)
        stage.SetEditTarget(edit_target)
        await omni.kit.app.get_app().next_update_async()
        self.assertIsNotNone(payload)
        self.assertEqual(payload.event_type, LayerEventType.EDIT_TARGET_CHANGED)

        # Set the same edit target will not trigger any events
        payload = None
        stage.SetEditTarget(edit_target)
        await omni.kit.app.get_app().next_update_async()
        self.assertIsNone(payload)

    def check_sublayers(self, sublayer_paths, expected_layer_identifiers):
        sublayer_paths = sorted(sublayer_paths)
        expected_layer_identifiers = sorted(expected_layer_identifiers)
        self.assertTrue(
            sublayer_paths == expected_layer_identifiers,
            f"Sublayers array does not match, got: {sublayer_paths}, expected: {expected_layer_identifiers}",
        )

    async def test_get_used_sublayers(self):
        layers = get_layers()
        stage = self.usd_context.get_stage()
        root_layer = stage.GetRootLayer()

        sublayers = layers.get_layers_state().get_local_layer_identifiers()
        self.check_sublayers(sublayers, [root_layer.identifier])
        layer0 = Sdf.Layer.CreateAnonymous()
        LayerUtils.insert_sublayer(root_layer, 0, layer0.identifier)
        sublayers = layers.get_layers_state().get_local_layer_identifiers()
        self.check_sublayers(sublayers, [root_layer.identifier, layer0.identifier])
        layer1 = Sdf.Layer.CreateAnonymous()
        LayerUtils.insert_sublayer(root_layer, 1, layer1.identifier)
        sublayers = layers.get_layers_state().get_local_layer_identifiers()
        self.check_sublayers(sublayers, [root_layer.identifier, layer0.identifier, layer1.identifier])

        layer2 = Sdf.Layer.CreateAnonymous()
        layer3 = Sdf.Layer.CreateAnonymous()
        layer4 = Sdf.Layer.CreateAnonymous()
        layer5 = Sdf.Layer.CreateAnonymous()
        LayerUtils.insert_sublayer(layer2, 0, layer3.identifier)
        LayerUtils.insert_sublayer(layer2, 1, layer4.identifier)
        LayerUtils.insert_sublayer(layer4, 0, layer5.identifier)

        LayerUtils.insert_sublayer(root_layer, 2, layer2.identifier)
        sublayers = layers.get_layers_state().get_local_layer_identifiers()
        self.check_sublayers(
            sublayers,
            [
                root_layer.identifier,
                layer0.identifier,
                layer1.identifier,
                layer2.identifier,
                layer3.identifier,
                layer4.identifier,
                layer5.identifier,
            ],
        )

        # Removes layer0
        LayerUtils.remove_sublayer(root_layer, 0)
        sublayers = layers.get_layers_state().get_local_layer_identifiers()
        self.check_sublayers(
            sublayers,
            [
                root_layer.identifier,
                layer1.identifier,
                layer2.identifier,
                layer3.identifier,
                layer4.identifier,
                layer5.identifier,
            ],
        )

        # Removes layer2 will remove layer2, layer3, layer4, layer5
        LayerUtils.remove_sublayer(root_layer, 1)
        sublayers = layers.get_layers_state().get_local_layer_identifiers()
        self.check_sublayers(sublayers, [root_layer.identifier, layer1.identifier])

    async def test_get_dirty_sublayers(self):
        layers = get_layers()
        stage = self.usd_context.get_stage()
        root_layer = stage.GetRootLayer()

        with tempfile.TemporaryDirectory() as tempdir:
            format = Sdf.FileFormat.FindByExtension(".usd")
            layer0 = Sdf.Layer.New(format, f"{tempdir}/1.usd")
            layer1 = Sdf.Layer.New(format, f"{tempdir}/2.usd")
            layer2 = Sdf.Layer.New(format, f"{tempdir}/3.usd")
            layer3 = Sdf.Layer.New(format, f"{tempdir}/4.usd")
            layer4 = Sdf.Layer.New(format, f"{tempdir}/5.usd")
            layer5 = Sdf.Layer.New(format, f"{tempdir}/6.usd")
            LayerUtils.insert_sublayer(root_layer, 0, layer0.identifier, False)
            LayerUtils.insert_sublayer(root_layer, 0, layer1.identifier, False)
            LayerUtils.insert_sublayer(layer2, 0, layer3.identifier, False)
            LayerUtils.insert_sublayer(layer2, 0, layer4.identifier, False)
            LayerUtils.insert_sublayer(layer4, 0, layer5.identifier, False)
            LayerUtils.insert_sublayer(root_layer, 0, layer2.identifier, False)
            sublayers = layers.get_layers_state().get_local_layer_identifiers()
            self.check_sublayers(
                sublayers,
                [
                    root_layer.identifier,
                    layer0.identifier,
                    layer1.identifier,
                    layer2.identifier,
                    layer3.identifier,
                    layer4.identifier,
                    layer5.identifier,
                ],
            )

            # Checks dirtiness of layers since layer2 and layer4 have been touched.
            # They should be dirty at this moment
            dirty_sublayers = layers.get_layers_state().get_dirty_layer_identifiers()
            self.check_sublayers(dirty_sublayers, [layer2.identifier, layer4.identifier])

            # Touches layer1
            LayerUtils.set_edit_target(stage, layer1.identifier)
            UsdGeom.Mesh.Define(stage, "/root/test")
            dirty_sublayers = layers.get_layers_state().get_dirty_layer_identifiers()
            self.check_sublayers(dirty_sublayers, [layer1.identifier, layer2.identifier, layer4.identifier])
