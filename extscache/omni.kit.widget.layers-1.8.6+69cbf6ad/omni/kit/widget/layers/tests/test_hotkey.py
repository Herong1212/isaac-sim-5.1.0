import carb
import omni.kit.app

from .base import TestLayerUIBase
from omni.kit.test_suite.helpers import arrange_windows


class TestHotkey(TestLayerUIBase):

    # Before running each test
    async def setUp(self):
        await super().setUp()

        await arrange_windows("Layer", 800, 600)
        self.stage = self.usd_context.get_stage()

    async def tearDown(self):
        await super().tearDown()

    async def _wait(self, frames=4):
        for i in range(frames):
            await self.app.next_update_async()

    async def test_remove_prim_with_hot_key(self):
        self.stage.DefinePrim("/cube", "Cube")
        self.stage.DefinePrim("/cube2", "Cube")
        await self._wait()

        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item

        layer_window = self.layers_instance._window
        layer_tree_view = layer_window._layer_view
        all_root_specs = root_layer_item.absolute_root_spec.children
        self.assertTrue(len(all_root_specs) != 0)
        layer_tree_view.selection = all_root_specs
        await self._wait()
        self.assertEqual(len(self.layers_instance.get_selected_items()), 2)

        # FIXME: Not sure why there are two dangling windows that are visible underlying.
        import omni.kit.ui_test as ui_test
        window = ui_test.find("Create Sublayer")
        if window:
            window.window.visible = False

        window = ui_test.find("Insert Sublayer")
        if window:
            window.window.visible = False

        window = ui_test.find("Save Layer As")
        if window:
            window.window.visible = False

        window = ui_test.find("Layer")
        await window.bring_to_front()
        await ui_test.emulate_mouse_move(ui_test.Vec2(-100, -100))
        await ui_test.emulate_mouse_move(window.center)

        await omni.kit.ui_test.emulate_keyboard_press(carb.input.KeyboardInput.DEL)
        await self._wait()
        self.assertFalse(self.stage.GetPrimAtPath("/cube"))
        self.assertFalse(self.stage.GetPrimAtPath("/cube2"))
