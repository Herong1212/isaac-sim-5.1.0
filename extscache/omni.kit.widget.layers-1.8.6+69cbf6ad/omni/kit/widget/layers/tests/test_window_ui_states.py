import omni.kit.test
import os
import tempfile
import shutil
import omni.client
import omni.kit.app

from .base import TestLayerNonUIBase
from pxr import Usd, Sdf
from stat import S_IREAD, S_IWRITE
from omni.kit.usd.layers import LayerUtils, get_layers
from omni.kit.widget.prompt import PromptManager


class TestWindowUiStates(TestLayerNonUIBase):

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

        import omni.kit.ui_test as ui_test
        await ui_test.find("Layer").focus()

    async def tearDown(self):
        await super().tearDown()

        self._writable_layer = None
        self._readonly_layer = None
        self.stage = None

        os.chmod(self._readonly_layer_path, S_IWRITE)
        shutil.rmtree(self._temp_dir)

    async def test_mute(self):
        import omni.kit.ui_test as ui_test
        local_mute_items = ui_test.find_all("Layer//Frame/**/ToolButton[*].identifier=='local_mute'")
        global_mute_items = ui_test.find_all("Layer//Frame/**/ToolButton[*].identifier=='global_mute'")

        # Root layer has no mute button.
        self.assertEqual(len(local_mute_items), 2)
        self.assertEqual(len(global_mute_items), 2)

        for global_scope in [False, True]:
            layers = get_layers()
            layers_state = layers.get_layers_state()
            layers_state.set_muteness_scope(global_scope)

            # Local mute
            # Mute readonly layer
            await local_mute_items[0].click()
            self.assertEqual(self.stage.IsLayerMuted(self._readonly_layer.identifier), not global_scope)
            self.assertFalse(self.stage.IsLayerMuted(self._writable_layer.identifier))

            # Unmute
            await local_mute_items[0].click()
            self.assertFalse(self.stage.IsLayerMuted(self._readonly_layer.identifier))

            # Mute writable layer
            await local_mute_items[1].click()
            self.assertFalse(self.stage.IsLayerMuted(self._readonly_layer.identifier))
            self.assertEqual(self.stage.IsLayerMuted(self._writable_layer.identifier), not global_scope)

            # Unmute
            await local_mute_items[1].click()
            self.assertFalse(self.stage.IsLayerMuted(self._writable_layer.identifier))

            # global mute
            # Mute readonly layer
            await global_mute_items[0].click()
            self.assertEqual(self.stage.IsLayerMuted(self._readonly_layer.identifier), global_scope)
            self.assertFalse(self.stage.IsLayerMuted(self._writable_layer.identifier))

            # Unmute
            await global_mute_items[0].click()
            self.assertFalse(self.stage.IsLayerMuted(self._readonly_layer.identifier))

            # Mute writable layer
            await global_mute_items[1].click()
            self.assertFalse(self.stage.IsLayerMuted(self._readonly_layer.identifier))
            self.assertEqual(self.stage.IsLayerMuted(self._writable_layer.identifier), global_scope)

            # Unmute
            await global_mute_items[1].click()
            self.assertFalse(self.stage.IsLayerMuted(self._writable_layer.identifier))

    async def test_lock(self):
        import omni.kit.ui_test as ui_test
        lock_items = ui_test.find_all("Layer//Frame/**/ToolButton[*].identifier=='lock'")

        # Root or readonly layer has no lock button.
        self.assertEqual(len(lock_items), 1)

        layers = get_layers()
        layers_state = layers.get_layers_state()
        await lock_items[0].click()
        self.assertTrue(layers_state.is_layer_locked(self._writable_layer.identifier))

        await lock_items[0].click()
        self.assertFalse(layers_state.is_layer_locked(self._writable_layer.identifier))
