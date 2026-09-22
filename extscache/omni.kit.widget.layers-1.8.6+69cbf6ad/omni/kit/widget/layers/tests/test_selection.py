import omni.kit.test
import os
import uuid
import omni.client
import omni.kit.commands
from .base import TestLayerUIBase
from omni.kit.widget.layers import LayerUtils
from pxr import Sdf, Usd


class TestLayerSelection(TestLayerUIBase):
    async def setUp(self):
        await super().setUp()
        self.stage = await self.prepare_empty_stage()

    async def tearDown(self):
        self.layers_instance.show_window(True)
        await self.usd_context.close_stage_async()
        await super().tearDown()

    async def _wait(self, frames=4):
        for i in range(frames):
            await self.app.next_update_async()

    async def test_layer_selection(self):
        layer1 = Sdf.Layer.CreateAnonymous()
        layer2 = Sdf.Layer.CreateAnonymous()
        self.stage.GetRootLayer().subLayerPaths.append(layer1.identifier)
        self.stage.GetRootLayer().subLayerPaths.append(layer2.identifier)
        await self._wait()

        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item
        self.assertEqual(len(root_layer_item.sublayers), 2)

        selected_item = None

        def on_selected(item):
            nonlocal selected_item
            selected_item = item

        self.layers_instance.add_layer_selection_changed_fn(on_selected)

        # Select two layers by simulating UI clicks.
        layer_window = self.layers_instance._window
        layer_tree_view = layer_window._layer_view
        layer_tree_view.selection = root_layer_item.sublayers
        await self._wait()

        # get_current_focused_layer_item returns none for multiple selection.
        self.assertEqual(self.layers_instance.get_current_focused_layer_item(), None)
        self.assertEqual(self.layers_instance.get_selected_items(), root_layer_item.sublayers)
        self.assertEqual(selected_item, None)

        layer_tree_view.selection = [root_layer_item.sublayers[0]]
        await self._wait()
        self.assertEqual(self.layers_instance.get_current_focused_layer_item(), root_layer_item.sublayers[0])
        self.assertEqual(self.layers_instance.get_selected_items(), [root_layer_item.sublayers[0]])
        self.assertEqual(selected_item, root_layer_item.sublayers[0])

        layer_tree_view.selection = []
        await self._wait()
        self.assertEqual(self.layers_instance.get_current_focused_layer_item(), None)
        self.assertEqual(self.layers_instance.get_selected_items(), [])
        self.assertEqual(selected_item, None)

        # Manually set focused layer item.
        self.layers_instance.set_current_focused_layer_item(root_layer_item.sublayers[0].identifier)
        await self._wait()
        self.assertEqual(self.layers_instance.get_current_focused_layer_item(), root_layer_item.sublayers[0])
        self.assertEqual(layer_tree_view.selection, [root_layer_item.sublayers[0]])
        self.assertEqual(self.layers_instance.get_selected_items(), [root_layer_item.sublayers[0]])
        self.assertEqual(selected_item, root_layer_item.sublayers[0])

        # After listener is removed, it should not receive changed event anymore.
        selected_item = None
        self.layers_instance.remove_layer_selection_changed_fn(on_selected)
        self.layers_instance.set_current_focused_layer_item(root_layer_item.sublayers[0].identifier)
        await self._wait()
        self.assertEqual(selected_item, None)

        self.layers_instance.add_layer_selection_changed_fn(on_selected)
        self.layers_instance.show_window(False)
        await self._wait()

        # When window is hidden, it cannot focus any layer item.
        self.assertEqual(root_layer_item.sublayers, [])
        self.layers_instance.set_current_focused_layer_item(root_layer_item)
        await self._wait()
        self.assertEqual(selected_item, None)

        self.layers_instance.show_window(True)
        await self._wait()
        layer_model = self.layers_instance.get_layer_model()
        # Old items are released after window is hidden, re-fetching it.
        root_layer_item = layer_model.root_layer_item
        self.layers_instance.set_current_focused_layer_item(root_layer_item.sublayers[0].identifier)
        await self._wait()
        self.assertEqual(selected_item, root_layer_item.sublayers[0])

    async def test_prim_selection(self):
        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item

        prim_spec_paths = self.create_prim_specs(self.stage, Sdf.Path.absoluteRootPath, [10, 5, 4, 2])
        await self._wait()

        self.check_prim_spec_tree(root_layer_item.absolute_root_spec, prim_spec_paths)
        omni.kit.commands.execute("SelectAll")
        await self._wait()

        all_prim_paths = []
        for prim in self.stage.TraverseAll():
            all_prim_paths.append(prim.GetPath())

        all_root_specs = root_layer_item.absolute_root_spec.children
        layer_window = self.layers_instance._window
        layer_tree_view = layer_window._layer_view
        selections = layer_tree_view.selection
        self.assertTrue(len(selections) != 0)
        self.assertEqual(set(all_root_specs), set(selections))
        omni.kit.undo.undo()
        await self._wait()

        selections = layer_tree_view.selection
        self.assertEqual(len(selections), 0)

        selection_api = self.usd_context.get_selection()
        selection_api.set_selected_prim_paths([str(path) for path in all_prim_paths[10:20]], False)
        await self._wait()

        selections = layer_tree_view.selection
        all_selected_paths = []
        for selection in selections:
            all_selected_paths.append(selection.path)
        self.assertEqual(set(all_prim_paths[10:20]), set(all_selected_paths))

    async def test_prim_selection_with_ui(self):
        layer_model = self.layers_instance.get_layer_model()
        root_layer_item = layer_model.root_layer_item

        prim_spec_paths = self.create_prim_specs(self.stage, Sdf.Path.absoluteRootPath, [10])
        await self._wait()

        all_root_specs = root_layer_item.absolute_root_spec.children
        layer_window = self.layers_instance._window
        layer_tree_view = layer_window._layer_view
        # Select item one by one
        layer_tree_view.selection = [all_root_specs[0]]
        layer_tree_view.selection = [all_root_specs[1]]
        layer_tree_view.selection = [all_root_specs[2]]

        # Return back to item 1
        omni.kit.undo.undo()
        await self._wait()
        selections = layer_tree_view.selection
        self.assertTrue(len(selections) != 0)
        self.assertEqual(set([all_root_specs[1]]), set(selections))

        # Return back to item 0
        omni.kit.undo.undo()
        await self._wait()
        selections = layer_tree_view.selection
        self.assertTrue(len(selections) != 0)
        self.assertEqual(set([all_root_specs[0]]), set(selections))

        # Empty selection as startup
        omni.kit.undo.undo()
        await self._wait()
        selections = layer_tree_view.selection
        self.assertTrue(len(selections) == 0)

        # Select all and undo
        layer_tree_view.selection = all_root_specs
        omni.kit.undo.undo()
        await self._wait()
        selections = layer_tree_view.selection
        self.assertTrue(len(selections) == 0)

        # OM-45941: Select one item and remove it will not trigger new command.
        layer_tree_view.selection = [all_root_specs[0]]
        layer_tree_view.selection = [all_root_specs[1]]

        stage = omni.usd.get_context().get_stage()
        LayerUtils.remove_prim_spec(stage.GetRootLayer(), all_root_specs[1].path)
        await self._wait()
        omni.kit.undo.undo()
        await self._wait()
        selections = layer_tree_view.selection
        self.assertTrue(len(selections) != 0)
        self.assertEqual(set([all_root_specs[0]]), set(selections))
