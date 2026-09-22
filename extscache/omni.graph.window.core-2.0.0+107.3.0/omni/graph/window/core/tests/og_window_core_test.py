# noqa: too-many-lines
import os
import unittest
from pathlib import Path
from typing import List, Tuple

import carb
import carb.settings
import omni.graph.core as og
import omni.graph.window.core as ogw
import omni.kit.commands as commands
import omni.kit.test
import omni.ui as ui
import omni.usd
from carb.input import KeyboardInput
from omni.graph.window.core.graph_config import Supports
from omni.graph.window.core.virtual_node_helper import VirtualNodeHelper
from omni.kit import ui_test
from omni.ui.tests.test_base import OmniUiTest
from pxr import Sdf, Usd, UsdUI

from ..graph_context_menu import OmniGraphEmptyPortContextMenu, OmniGraphPortContextMenuBase
from ..graph_operations import (
    can_promote_to_constant,
    can_promote_to_variable,
    get_compatible_variables,
    promote_to_constant,
    promote_to_existing_variable,
    promote_to_variable,
)
from . import graph_ui_test

EXT_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.graph.window.core}"))


class OgCoreTestCatalogModel(ogw.OmniGraphNodeTypeCatalogModel):
    def allow_node_type(self, node_type_name: str):
        # We don't want to have to change the golden images every time
        # a new category or node type is added (the number of node types
        # in each category is displayed on the catalog widget).
        # So we restrict the allowed node types to a static set.
        return node_type_name in (
            "omni.graph.nodes.Add",  # Math
            "omni.graph.nodes.ConstantFloat",  # Constants
            "omni.graph.nodes.ConstantInt",  # Constants
            "omni.graph.tutorials.SimpleData",  # Tutorials
        )


class OgCoreTestGraphWidget(ogw.OmniGraphWidget):
    def on_build_startup(self):
        pass

    def show_variables_tab(self):
        if self._catalog_selector:
            self._catalog_selector.model.set_value(1)


class OgCoreTestWindow(ogw.OmniGraphWindow):
    def on_build_window(self):
        self._main_widget = OgCoreTestGraphWidget(  # noqa: attribute-defined-outside-init
            catalog_model=OgCoreTestCatalogModel()
        )

    @property
    def model(self):
        return self._main_widget.model

    def show_variables_tab(self):
        self._main_widget.show_variables_tab()

    # This slightly simplifies access to OmniGraphWindow._import_prims() but its main purpose is to avoid all of
    # "protected-access" warnings from lint.
    def import_prims(self, prims: List[Usd.Prim], focus=True):
        return self._import_prims(None, prims, focus)


class TestOgWindowCoreUI(OmniUiTest):
    TEST_GRAPH_PATH = "/World/TestGraph"
    wait_frames_for_visual_update = 5

    # It takes 6 frames for the nodes and connections to all draw in their proper positions.
    wait_frames_for_graph_draw = 10

    # Wait 10 frames for commands to execute and the graph to update
    wait_frames_for_commands = 10

    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = EXT_PATH.absolute().resolve().joinpath("data/tests")

        self._window = None
        self._graph_window = None
        self._windows_to_destroy = []
        await self._reset_stage()

    async def tearDown(self):
        self._destroy_windows()
        self._golden_img_dir = None

        await super().tearDown()

    def _destroy_window_with_title(self, title) -> bool:
        """Destroy the window with the given title. Returns if the window was found and destroyed."""
        if not title:
            return False

        for window in ui.Workspace.get_windows():
            if isinstance(window, ui.Window) and window.title == title:
                window.destroy()
                window = None
                return True
        return False

    def _destroy_windows(self):
        for win in self._windows_to_destroy:
            self._destroy_window_with_title(win)

        if self._graph_window:
            self._graph_window.destroy()
        if self._window:
            self._window.destroy()
        self._window = None
        self._graph_window = None

    async def _reset_stage(self):
        self._destroy_windows()
        await omni.usd.get_context().new_stage_async()
        self.stage = omni.usd.get_context().get_stage()

    def create_graph_window(self, title, x=0, y=0, width=1200, height=800):
        graph_window = OgCoreTestWindow(
            title,
            flags=ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_RESIZE,
            position_x=x,
            position_y=y,
            width=width,
            height=height,
        )
        return graph_window

    def move_node(self, node: og.Node, pos: Tuple[float, float]):
        prim = self.stage.GetPrimAtPath(node.get_prim_path())
        UsdUI.NodeGraphNodeAPI.Apply(prim)
        UsdUI.NodeGraphNodeAPI(prim).GetPosAttr().Set(pos)

    async def test_simple_graph(self):
        """Verify if a simple graph renders correctly"""

        self._window = await self.create_test_window(width=1200, height=800)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        keys = og.Controller.Keys
        (graph, _, _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("constA", "omni.graph.nodes.ConstantFloat"),
                    ("add", "omni.graph.nodes.Add"),
                    ("simple", "omni.graph.tutorials.SimpleData"),
                ],
                keys.SET_VALUES: [("constA.inputs:value", 1.5)],
                keys.CONNECT: [
                    ("constA.inputs:value", "add.inputs:a"),
                    ("constA.inputs:value", "add.inputs:b"),
                    ("add.outputs:sum", "simple.inputs:a_float"),
                ],
            },
        )
        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_simple_graph.png",
        )

    async def test_dynamic_attributes(self):
        """Verify nodes are updated with new dynamic attributes"""

        self._window = await self.create_test_window(width=1200, height=800)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        keys = og.Controller.Keys
        (graph, (sequence, counter, text), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("sequence", "omni.graph.action.Multisequence"),
                    ("counter", "omni.graph.action.Counter"),
                    ("text", "omni.graph.ui.PrintText"),
                ],
                keys.CONNECT: [
                    ("sequence.outputs:output0", "counter.inputs:execIn"),
                ],
            },
        )

        # Create 2nd attribute for sequence and connect it
        output1_attr = og.Controller.create_attribute(
            sequence, "output1", "execution", og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
        )
        og.Controller.connect(output1_attr, og.Controller.attribute("inputs:execIn", text))

        # Fix position of nodes for Golden Image
        self.move_node(node=sequence, pos=(37.0, 55.0))
        self.move_node(node=text, pos=(344.0, 220.0))
        self.move_node(node=counter, pos=(346.0, 48.0))

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_dynamic_attributes.png",
        )

    async def test_delete_connection(self):
        """Test deleting a connection between 2 nodes with the right click menu"""

        await self.create_test_area(width=1200, height=800, block_devices=False)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        keys = og.Controller.Keys
        (graph, (_, _), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("sequence", "omni.graph.action.Multisequence"),
                    ("counter", "omni.graph.action.Counter"),
                ],
                keys.CONNECT: [
                    ("sequence.outputs:output0", "counter.inputs:execIn"),
                ],
            },
        )
        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # Mimic deleting a connection
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(582, 439), right_click=True, human_delay_speed=10)
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(594, 447), human_delay_speed=10)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_delete_connection.png",
        )

    async def test_delete_target_connection(self):
        """Test deleting a connection between 2 nodes with target inputs/outputs with the right click menu"""

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        await self.create_test_area(width=1200, height=800, block_devices=False)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        keys = og.Controller.Keys
        (graph, (_, _), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("getPrimPaths", "omni.graph.nodes.GetPrimPaths"),
                    ("constantTarget", "omni.graph.nodes.ConstantTarget"),
                ],
                keys.CONNECT: [
                    ("constantTarget.inputs:value", "getPrimPaths.inputs:prims"),
                ],
                keys.CREATE_PRIMS: [
                    ("/World/Cube1", {}, "Cube"),
                ],
            },
        )
        rel = stage.GetRelationshipAtPath(f"{self.TEST_GRAPH_PATH}/getPrimPaths.inputs:prims")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target="/World/Cube1")

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # Mimic deleting a connection
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(582, 439), right_click=True, human_delay_speed=10)
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(594, 447), human_delay_speed=10)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_delete_target_connection.png",
        )

    @unittest.skipIf(os.name == "posix" and os.getenv("ETM_ACTIVE"), "OM-79384: Skip test in Linux ETM")
    async def test_create_connection(self):
        """Test creating a connection between 2 nodes via mouse drag"""

        await self.create_test_area(width=1200, height=800, block_devices=False)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        keys = og.Controller.Keys
        (graph, (sequence, counter), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("sequence", "omni.graph.action.Multisequence"),
                    ("counter", "omni.graph.action.Counter"),
                ],
            },
        )

        # Fix position of nodes for Golden Image
        self.move_node(node=sequence, pos=(37.0, 55.0))
        self.move_node(node=counter, pos=(346.0, 48.0))

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # Mimic connecting a node's output to another node's input
        await ui_test.emulate_mouse_drag_and_drop(ui_test.Vec2(600.0, 450.0), ui_test.Vec2(845, 400))
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_create_connection.png",
        )

    @unittest.skipIf(os.name == "posix" and os.getenv("ETM_ACTIVE"), "OM-79384: Skip test in Linux ETM")
    async def test_create_multi_target_connection(self):
        """Test creating a connection between 3 target nodes via mouse drag"""

        await self.create_test_area(width=1200, height=800, block_devices=False)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        keys = og.Controller.Keys
        (graph, (get_prim_paths, get_prim_path, const_target01, const_target02), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("GetPrimPaths", "omni.graph.nodes.GetPrimPaths"),
                    ("GetPrimPath", "omni.graph.nodes.GetPrimPath"),
                    ("ConstantTarget_01", "omni.graph.nodes.ConstantTarget"),
                    ("ConstantTarget_02", "omni.graph.nodes.ConstantTarget"),
                ],
            },
        )

        # Fix position of nodes for Golden Image
        self.move_node(node=get_prim_paths, pos=(340.0, 0.0))
        self.move_node(node=get_prim_path, pos=(340.0, 100.0))
        self.move_node(node=const_target01, pos=(37.0, 55.0))
        self.move_node(node=const_target02, pos=(37.0, 150.0))

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        drag_const_target01 = ui_test.Vec2(603, 428)
        drag_const_target02 = ui_test.Vec2(603, 596)

        drop_get_prim_paths = ui_test.Vec2(855, 324)
        drop_get_prim_path = ui_test.Vec2(855, 511)

        # Mimic connecting a node's output to another node's input
        await ui_test.emulate_mouse_drag_and_drop(drag_const_target01, drop_get_prim_paths)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        await ui_test.emulate_mouse_drag_and_drop(drag_const_target02, drop_get_prim_paths)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        await ui_test.emulate_mouse_drag_and_drop(drag_const_target01, drop_get_prim_path)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        await ui_test.emulate_mouse_drag_and_drop(drag_const_target02, drop_get_prim_path)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_create_multi_target_connection.png",
        )

    @unittest.skipIf(os.name == "posix" and os.getenv("ETM_ACTIVE"), "OM-79384: Skip test in Linux ETM")
    async def test_create_multi_bundle_connection(self):
        """Test creating a connection between 3 bundle nodes via mouse drag"""

        await self.create_test_area(width=1200, height=800, block_devices=False)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        keys = og.Controller.Keys
        (graph, (extract_bundle, write_prims, bundle_const01, bundle_const02), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("ExtractBundle", "omni.graph.nodes.ExtractBundle"),
                    ("WritePrims", "omni.graph.nodes.WritePrimsV2"),
                    ("BundleConstruct_01", "omni.graph.nodes.ExtractBundle"),
                    ("BundleConstruct_02", "omni.graph.nodes.ExtractBundle"),
                ],
            },
        )

        # Fix position of nodes for Golden Image
        self.move_node(node=extract_bundle, pos=(340.0, 0.0))
        self.move_node(node=write_prims, pos=(340.0, 100.0))
        self.move_node(node=bundle_const01, pos=(37.0, 0.0))
        self.move_node(node=bundle_const02, pos=(37.0, 120.0))

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        drag_bundle_const01 = ui_test.Vec2(595, 253)
        drag_bundle_const02 = ui_test.Vec2(595, 463)

        drop_extract_bundle = ui_test.Vec2(820, 217)
        drop_write_prims = ui_test.Vec2(820, 705)

        # Mimic connecting a node's output to another node's input
        await ui_test.emulate_mouse_drag_and_drop(drag_bundle_const01, drop_extract_bundle)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        await ui_test.emulate_mouse_drag_and_drop(drag_bundle_const02, drop_extract_bundle)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        await ui_test.emulate_mouse_drag_and_drop(drag_bundle_const01, drop_write_prims)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        await ui_test.emulate_mouse_drag_and_drop(drag_bundle_const02, drop_write_prims)

        # Move the mouse away from the graph so that we don't get tooltips popping up.
        await ui_test.emulate_mouse_move(ui_test.Vec2(0, 0))
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_create_multi_bundle_connection.png",
        )

    @unittest.skipIf(os.name == "posix" and os.getenv("ETM_ACTIVE"), "OM-79384: Skip test in Linux ETM")
    async def test_create_node_drag_and_drop(self):
        """Test creating a node by dragging from the side bar"""

        await self.create_test_area(width=1200, height=800, block_devices=False)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        (graph, _, _, _) = og.Controller.edit(self.TEST_GRAPH_PATH)
        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # Mimic dragging a node from the sidebar (node list) into the graph
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(50, 120))
        await ui_test.emulate_mouse_drag_and_drop(ui_test.Vec2(50, 150), ui_test.Vec2(450, 175))
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_create_node_drag_and_drop.png",
        )

    async def test_delete_node_drag_and_drop(self):
        """Test deleting a single node by dragging it back to the side bar"""

        await self.create_test_area(width=1200, height=800, block_devices=False)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        keys = og.Controller.Keys
        (graph, (sequence, counter), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("sequence", "omni.graph.action.Multisequence"),
                    ("counter", "omni.graph.action.Counter"),
                ],
            },
        )

        # Fix position of nodes for Golden Image
        self.move_node(node=sequence, pos=(37.0, 55.0))
        self.move_node(node=counter, pos=(346.0, 48.0))

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        start = ui_test.Vec2(580.0, 450.0)
        end = ui_test.Vec2(200, 400)

        # Mimic deleting a node by dragging it back into the side bar
        await ui_test.emulate_mouse_move(start)
        await ui_test.emulate_mouse_drag_and_drop(start, end)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_delete_node_drag_and_drop.png",
        )

    async def test_delete_node_delete_key(self):
        """Test deleting a node with the delete key"""

        await self.create_test_area(width=1200, height=800, block_devices=False)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)
        await ui_test.emulate_mouse_move(pos=ui_test.Vec2(1100.0, 600.0))  # Place mouse in the window

        keys = og.Controller.Keys
        (graph, (sequence, counter), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("sequence", "omni.graph.action.Multisequence"),
                    ("counter", "omni.graph.action.Counter"),
                ],
            },
        )

        # Fix position of nodes for Golden Image
        self.move_node(node=sequence, pos=(37.0, 55.0))
        self.move_node(node=counter, pos=(346.0, 48.0))

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        position = ui_test.Vec2(560, 410)

        # Mimic deleting a node by clicking on it and pressing the DELETE key
        await ui_test.emulate_mouse_move_and_click(pos=position)
        await ui_test.emulate_keyboard_press(KeyboardInput.DEL)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_delete_node_delete_key.png",
        )

    async def test_delete_node_with_connections(self):
        """Test deleting a node with multiple connections"""

        await self.create_test_area(width=1200, height=800, block_devices=False)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        keys = og.Controller.Keys
        (graph, (const1, const2, add, increment), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("const1", "omni.graph.nodes.ConstantInt64"),
                    ("const2", "omni.graph.nodes.ConstantInt64"),
                    ("add", "omni.graph.nodes.Add"),
                    ("increment", "omni.graph.nodes.Increment"),
                ],
                keys.CONNECT: [
                    ("const1.inputs:value", "add.inputs:a"),
                    ("const2.inputs:value", "add.inputs:b"),
                    ("add.outputs:sum", "increment.inputs:value"),
                ],
            },
        )

        # Fix position of nodes for Golden Image
        self.move_node(node=const1, pos=(50, 50))
        self.move_node(node=const2, pos=(50, 250))
        self.move_node(node=add, pos=(350, 150))
        self.move_node(node=increment, pos=(650, 150))

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # Deleting 'add' node
        commands.execute("DeletePrims", paths=[add.get_prim_path()])
        await ui_test.wait_n_updates(self.wait_frames_for_commands)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_delete_node_with_connections.png",
        )

    async def test_promote_to_variable(self):
        """Tests "promote to variable" on various node attributes"""
        await self.create_test_area(width=1200, height=800, block_devices=False)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")
        keys = og.Controller.Keys
        (graph, (add, const, simple_data), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Add", "omni.graph.nodes.Add"),
                    ("Const", "omni.graph.nodes.ConstantFloat"),
                    ("SimpleData", "omni.graph.tutorials.SimpleData"),
                ],
            },
        )

        # position the nodes
        nodes = {add: (350, 0, 200), const: (750, 0, 200), simple_data: (350, 150, 350)}
        for node, pos in nodes.items():
            self.move_node(node=node, pos=(pos[0], pos[1]))

        # import so the model gets built
        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        self._graph_window.show_variables_tab()

        # walk through all the inputs and outputs and promote the valid inputs and outputs
        model = self._graph_window.model
        for node, pos in nodes.items():
            prim = self.stage.GetPrimAtPath(node.get_prim_path())
            input_count = 0
            output_count = 0
            for port in model[prim].ports:
                if can_promote_to_variable(model, port):
                    if model[port].inputs is not None:
                        next_pos = (pos[0] - 150, pos[1] + input_count * 50)
                        input_count = input_count + 1
                    else:
                        next_pos = (pos[0] + pos[2] + (output_count % 3) * 200, pos[1] + int(output_count / 3) * 150)
                        output_count = output_count + 1

                    promote_to_variable(model, port, next_pos)

        # validate the expected were generated
        graph = og.Controller.graph(self.TEST_GRAPH_PATH)
        expected_input_vars = [
            "a",
            "b",
            "sum",
            "value",
            "a_bool",
            "a_double",
            "a_float",
            "a_half",
            "a_int",
            "a_int64",
            "a_string",
            "a_token",
            "a_uchar",
            "a_uint",
            "a_uint64",
        ]
        expected_output_vars = [
            "a_constant_input",
            "a_bool_01",
            "a_double_01",
            "a_float_01",
            "a_half_01",
            "a_int_01",
            "a_int64_01",
            "a_string_01",
            "a_token_01",
            "a_uchar_01",
            "a_uint_01",
            "a_uint64_01",
        ]
        self.assertEquals(len(graph.get_variables()), len(expected_input_vars) + len(expected_output_vars))
        for var in expected_input_vars + expected_output_vars:
            self.assertIsNotNone(graph.find_variable(var))

        # validate the correct number of nodes where generated
        self.assertEquals(len(graph.get_nodes()), len(nodes) + len(graph.get_variables()))

        # reimport to reframe the graph
        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_promote_to_variable.png",
        )

    async def test_promote_to_constant(self):
        """Tests 'promote to constant' on various node attributes"""

        await self.create_test_area(width=1200, height=800, block_devices=False)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")
        keys = og.Controller.Keys
        (graph, (add, simple_data), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("Add", "omni.graph.nodes.Add"), ("SimpleData", "omni.graph.tutorials.SimpleData")],
            },
        )

        nodes = {add: (850, 0), simple_data: (850, 160)}
        for node, pos in nodes.items():
            self.move_node(node=node, pos=(pos[0], pos[1]))

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # walk all the ports and promote to constant where applicable
        model = self._graph_window.model
        for node, pos in nodes.items():
            prim = self.stage.GetPrimAtPath(node.get_prim_path())
            input_count = 0
            for port in model[prim].ports:
                if can_promote_to_constant(model, port):
                    next_pos = (250, pos[1] + input_count * 80)
                    input_count = input_count + 1
                    promote_to_constant(model, port, next_pos)

        # validate the expected number of constant nodes were generated
        graph = og.Controller.graph(self.TEST_GRAPH_PATH)
        self.assertEquals(len(graph.get_nodes()), len(nodes) + 14)

        # reimport to frame
        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_promote_to_const.png",
        )

    async def test_set_from_variable(self):
        """Tests the 'Set to/from variable' functionality on node ports."""
        await self.create_test_area(width=1200, height=800, block_devices=False)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")
        keys = og.Controller.Keys
        (graph, nodes, _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("SimpleData", "omni.graph.tutorials.SimpleData")],
                keys.CREATE_VARIABLES: [
                    ("var_float", og.Type(og.BaseDataType.FLOAT)),
                    ("var_str", og.Type(og.BaseDataType.TOKEN)),
                    ("var_str2", og.Type(og.BaseDataType.TOKEN)),
                    ("var_int", og.Type(og.BaseDataType.INT)),
                ],
            },
        )

        simple_data = nodes[0]
        self.move_node(node=simple_data, pos=(400, 150))
        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        self._graph_window.show_variables_tab()

        # walk all the ports and promote to constant where applicable
        model = self._graph_window.model
        prim = self.stage.GetPrimAtPath(simple_data.get_prim_path())
        input_count = 0
        output_count = 0
        for port in model[prim].ports:
            compatible_vars = get_compatible_variables(model, port)
            if not compatible_vars:
                continue
            if model[port].inputs is None:
                next_pos = (750, 150 + output_count * 150)
                output_count = output_count + 1
            else:
                next_pos = (250, 150 + input_count * 80)
                input_count = input_count + 1
            promote_to_existing_variable(model, port, compatible_vars[0].name, next_pos)

        # reimport to frame
        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # This test sometimes has tiny differences in aliasing around some of the
        # text which results in a difference significantly larger than the old default threshold.
        # New default threshold should be high enough now, though.
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_set_from_variable.png",
        )

    async def test_layout_nodes(self):
        """Verify that node layout, after the initial one, works."""

        self._window = await self.create_test_window(width=1200, height=800)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        # Create a graph with a ConstantFloat node connected to an Add node.
        keys = og.Controller.Keys
        (graph, (const_node, _), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("constA", "omni.graph.nodes.ConstantFloat"),
                    ("add", "omni.graph.nodes.Add"),
                ],
                keys.CONNECT: [
                    ("constA.inputs:value", "add.inputs:a"),
                ],
            },
        )
        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # Move the constant node away from its initial position.
        const_prim = og.Controller.prim(const_node)

        commands.execute(
            "UsdUINodeGraphNodeSetCommand",
            attribute=UsdUI.Tokens.uiNodegraphNodePos,
            prim_path=const_prim.GetPath(),
            value=(600, 400),
            prev=(0, 0),
        )
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # Force layout.
        self._graph_window._main_widget.on_layout_clicked()  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_layout_nodes.png",
        )

    async def test_convert_to_type_all(self):
        """Tests 'Convert to Type' menu shows the expected types"""

        await self.create_test_area(width=1200, height=800, block_devices=False)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")
        keys = og.Controller.Keys
        (graph, (add,), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("Add", "omni.graph.nodes.Add")],
            },
        )

        self.move_node(node=add, pos=(0, 0))

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # walk all the ports and promote to constant where applicable
        position_of_port_a = ui_test.Vec2(477, 431)
        position_of_convert_menu = ui_test.Vec2(550, 487)
        position_of_all_menu = ui_test.Vec2(665, 487)
        await ui_test.emulate_mouse_move_and_click(position_of_port_a, right_click=True, human_delay_speed=10)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        await ui_test.emulate_mouse_move_and_click(position_of_convert_menu, human_delay_speed=10)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        await ui_test.emulate_mouse_move_and_click(position_of_all_menu, human_delay_speed=10)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="omni.graph.window.core.test_convert_to_type_all.png"
        )

    async def test_convert_to_type(self):
        """Tests 'Convert to Type' menu works"""

        await self.create_test_area(width=1200, height=800, block_devices=False)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")
        keys = og.Controller.Keys
        (graph, (add,), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [("Add", "omni.graph.nodes.Add")],
            },
        )

        self.move_node(node=add, pos=(0, 0))

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # walk all the ports and promote to constant where applicable
        position_of_port_a = ui_test.Vec2(477, 431)
        position_of_convert_menu = ui_test.Vec2(550, 487)
        position_of_double = ui_test.Vec2(655, 514)
        await ui_test.emulate_mouse_move_and_click(position_of_port_a, right_click=True, human_delay_speed=10)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        await ui_test.emulate_mouse_move_and_click(position_of_convert_menu, human_delay_speed=10)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        await ui_test.emulate_mouse_move_and_click(position_of_double, human_delay_speed=10)
        await ui_test.wait_n_updates(10)
        self.assertEqual(add.get_attribute("inputs:a").get_resolved_type().base_type, og.BaseDataType.DOUBLE)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="omni.graph.window.core.test_convert_to_type.png"
        )

    async def _do_dialog_position(self, raster_setting):
        suffix = "-raster" if raster_setting else "-noraster"

        with og.Settings.temporary("/exts/omni.kit.widget.graph/raster_nodes", raster_setting):
            await self.create_test_area(width=1200, height=800, block_devices=False)
            await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
            self._graph_window = self.create_graph_window("OgWindowCoreTest")
            keys = og.Controller.Keys
            await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
            (graph, *_) = og.Controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.CREATE_VARIABLES: [
                        ("var_float", og.Type(og.BaseDataType.FLOAT)),
                    ]
                },
            )

            self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])  # noqa: protected-access
            await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

            # cleans up the window on failure
            title = "Create Variable Node"
            self._windows_to_destroy.append(title)

            self._graph_window.show_variables_tab()
            await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

            # Drag the variable and drop it into the graph so that Create Variable Node dialog pops up.
            variable_pos = ui_test.Vec2(44, 114)
            drop_pos = ui_test.Vec2(500, 200)
            await ui_test.emulate_mouse_drag_and_drop(variable_pos, drop_pos)

            # When a modal window pops up it dims the main Kit window. That dimming fades in over the course
            # of several frames. The amount of time required depends upon the speed of the machine. We need to
            # provide a long enough delay so that even the slowest machine will have completed the fade-in before
            # we take the snapshot, otherwise the image comparison will fail.
            await ui_test.wait_n_updates(30)

            await self.capture_and_compare(
                golden_img_dir=self._golden_img_dir,
                golden_img_name=f"omni.graph.window.core.test_dialog_position{suffix}.png",
            )

            # Close the popup window.
            #
            # For some reason emulated clicks on the dialog's close icon or Cancel button don't get detected
            # by the UI. We'll have to find the dialog and close it ourselves, otherwise it will still be there
            # when the next test runs.
            found_window = self._destroy_window_with_title(title)

            # Sooner or later someone will change the title of that window, not knowing that we depend on it
            # here. Let's provide an assert to let them know about it.
            self.assertTrue(found_window, f"Could not find window titled '{title}'.")
            await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

            await self.finalize_test_no_image()

    async def test_dialog_position_noraster(self):
        """Tests that dialogs initiated by mouse actions over the graph appear where the mouse is."""

        # If node rasterization is on, then we'll skip the noraster test under the assumption that once
        # it's enabled by default then we'll never be going back.
        if not carb.settings.get_settings().get("/exts/omni.kit.widget.graph/raster_nodes"):
            await self._do_dialog_position(False)

    async def test_dialog_position_raster(self):
        """Tests that dialogs initiated by mouse actions over the graph appear where the mouse is."""
        await self._do_dialog_position(True)

    async def _run_context_menu_test(self, img_name, node_to_select: str, action_fn):
        """Helper that sets up a graph with the node context menu running at the given node"""
        self._window = await self.create_test_window(width=1200, height=800)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        controller = og.Controller(update_usd=True)
        keys = controller.Keys
        (graph, _, _, nodes) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Add1", "omni.graph.nodes.Add"),
                    ("Add2", "omni.graph.nodes.Add"),
                    ("Add3", "omni.graph.nodes.Add"),
                    ("Add4", "omni.graph.nodes.Add"),
                ],
                keys.CONNECT: [("Add1.outputs:sum", "Add2.inputs:a"), ("Add3.outputs:sum", "Add4.inputs:a")],
            },
        )

        self.move_node(nodes["Add1"], (200, 0))
        self.move_node(nodes["Add2"], (400, 0))
        self.move_node(nodes["Add3"], (200, 200))
        self.move_node(nodes["Add4"], (400, 200))

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # grab the input node
        selected_node = og.Controller.prim(nodes[node_to_select]) if node_to_select else None
        self._graph_window._main_widget.show_context_menu(selected_node, (600, 400))  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await action_fn(graph, nodes)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name=f"omni.graph.window.core.{img_name}.png"
        )

    async def _do_nothing(*args):
        pass

    async def _run_compound_context_menu_test(self, img_name, node_to_select: str, action_fn):
        """Helper that sets up a compound graph with a context menu running"""
        if not Supports.compound_subgraphs():
            return

        self._window = await self.create_test_window(width=1200, height=800)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        controller = og.Controller(update_usd=True)
        keys = controller.Keys
        (graph, (compound,), _, nodes) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    (
                        "Compound",
                        {
                            keys.CREATE_NODES: [
                                ("Add1", "omni.graph.nodes.Add"),
                                ("Add2", "omni.graph.nodes.Add"),
                                ("Add3", "omni.graph.nodes.Add"),
                                ("Add4", "omni.graph.nodes.Add"),
                            ],
                            keys.CONNECT: [
                                ("Add1.outputs:sum", "Add2.inputs:a"),
                                ("Add3.outputs:sum", "Add4.inputs:a"),
                            ],
                            keys.PROMOTE_ATTRIBUTES: [
                                ("Add1.inputs:a", "inputs:in"),
                                ("Add4.outputs:sum", "outputs:out"),
                            ],
                        },
                    ),
                ]
            },
        )

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # set the position of the nodes, including input and output
        prim_path = Sdf.Path(compound.get_compound_graph_instance().get_path_to_graph())
        VirtualNodeHelper.set_virtual_node_position(prim_path.AppendProperty("inputs:in"), (0, 0))
        VirtualNodeHelper.set_virtual_node_position(prim_path.AppendProperty("outputs:outputs"), (600, 0))
        self.move_node(nodes["Add1"], (200, 0))
        self.move_node(nodes["Add2"], (400, 0))
        self.move_node(nodes["Add3"], (200, 200))
        self.move_node(nodes["Add4"], (400, 200))

        self._graph_window._main_widget.enter_compound(og.Controller.prim(compound))  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # grab the input node
        input_node = self._graph_window._main_widget._isolation_model._input_nodes[0]  # noqa: protected-access
        output_node = self._graph_window._main_widget._isolation_model._output_nodes[0]  # noqa: protected-access
        selected_node = None
        if node_to_select == "InputNode":
            selected_node = input_node
        elif node_to_select == "OutputNode":
            selected_node = output_node
        else:
            selected_node = og.Controller.prim(nodes[node_to_select]) if node_to_select else None
        self._graph_window._main_widget.show_context_menu(selected_node, (600, 400))  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await action_fn(graph, nodes, input_node, output_node)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name=f"omni.graph.window.core.{img_name}.png"
        )

    async def test_context_menu_node(self):
        """Test that compares the menu when display when a node is selected by context click"""
        await self._run_context_menu_test("context_menu_node", "Add1", self._do_nothing)

    async def test_context_menus(self):
        """Tests the various menu items on the context menu"""
        menu_item_name = None

        async def select_menu_item(_graph, _node_map):
            menu_root = await graph_ui_test.get_current_context_menu()
            await graph_ui_test.run_menu_item(menu_root, menu_item_name)
            await ui_test.wait_n_updates(self.wait_frames_for_commands)

        selections = ["Add1"]
        menu_commands = [
            "Select All",
            "Select None",
            "Select Downstream Nodes",
            "Select Upstream Nodes",
            "Frame",
            "Create Backdrop",
            "Delete Selection",
            "Duplicate Selection",
            "Disconnect",
            "Copy",
            "Paste",
        ]

        for selection in selections:
            for command in menu_commands:
                with self.subTest(f"Context {selection} {command}"):
                    menu_item_name = command
                    img_name = f"context_{selection.lower()}_{command.lower().replace(' ', '_')}"
                    await self._run_context_menu_test(img_name, selection, select_menu_item)
                await self._reset_stage()

        # add an extra test for upstream nodes, since add1 only has downstream
        with self.subTest("Context Add2 Select Upstream Nodes"):
            menu_item_name = "Select Upstream Nodes"
            await self._run_context_menu_test("context_add2_select_upstream_nodes", "Add2", select_menu_item)

    async def test_context_menu_empty_space(self):
        """Tests that the context menu on an empty space appears"""
        await self._run_context_menu_test("context_menu_empty_space", None, self._do_nothing)

    async def test_compound_context_menu_input(self):
        """Test that compares the menu when display when the input is selected"""
        await self._run_compound_context_menu_test("compound_context_menu_input", "InputNode", self._do_nothing)

    async def test_compound_context_menu_output(self):
        """Test that compares the menu when display when the output is selected"""
        await self._run_compound_context_menu_test("compound_context_menu_output", "OutputNode", self._do_nothing)

    async def test_compound_context_menu_node(self):
        """Test that compares the menu when display when the output is selected"""
        await self._run_compound_context_menu_test("compound_context_menu_node", "Add1", self._do_nothing)

    async def test_compound_context_menus(self):
        """Tests the various menu items on the compound context menu"""
        menu_item_name = None

        async def select_menu_item(_graph, _node_map, _input_node, _output_node):
            menu_root = await graph_ui_test.get_current_context_menu()
            await graph_ui_test.run_menu_item(menu_root, menu_item_name)
            await ui_test.wait_n_updates(self.wait_frames_for_commands)

        selections = ["InputNode", "OutputNode", "Add1"]
        menu_commands = [
            "Select All",
            "Select None",
            "Select Downstream Nodes",
            "Select Upstream Nodes",
            "Frame",
            "Create Backdrop",
        ]

        for selection in selections:
            for command in menu_commands:
                with self.subTest(f"Compound Context {selection} {command}"):
                    menu_item_name = command
                    img_name = f"compound_context_{selection.lower()}_{command.lower().replace(' ', '_')}"
                    await self._run_compound_context_menu_test(img_name, selection, select_menu_item)
                await self._reset_stage()

        node_only_commands = ["Delete Selection", "Disconnect", "Duplicate Selection"]
        for command in node_only_commands:
            with self.subTest(f"Compound Context Add2 {command}"):
                menu_item_name = command
                img_name = f"compound_context_node_add2_{command.lower().replace(' ', '_')}"
                await self._run_compound_context_menu_test(img_name, "Add2", select_menu_item)
            await self._reset_stage()

    async def test_create_empty_subgraph(self):
        """Tests that an empty subgraph can be created from the context menu when no nodes are selected"""

        self._window = await self.create_test_window(width=1200, height=800)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        # create an empty graph
        controller = og.Controller(update_usd=True)
        (graph, _, _, _) = controller.edit(self.TEST_GRAPH_PATH, {})

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # bring up the menu with no selection
        self._graph_window._main_widget.show_context_menu(None, (600, 400))  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # select the menu item
        menu_root = await graph_ui_test.get_current_context_menu()
        await graph_ui_test.run_menu_item(menu_root, "Compounds/Create Compound Subgraph")
        await ui_test.wait_n_updates(self.wait_frames_for_commands)

        # enter the compound created
        self._graph_window._main_widget.enter_compound(  # noqa: protected-access
            og.Controller.prim(graph.get_nodes()[0])
        )
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="omni.graph.window.core.test_create_empty_subgraph.png"
        )

    @unittest.skip("A bug with emulated mouse clicks in the Stage window (OM-103661) prevents this test from working.")
    async def test_drop_prim(self):
        """Verify that a prim can be dragged from the stage lister into the graph."""

        self._window = await self.create_test_window(width=1200, height=800)
        self._graph_window = self.create_graph_window("OgWindowCoreTest", x=600, width=600)

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        keys = og.Controller.Keys
        (graph, _, _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {keys.CREATE_PRIMS: [("/World/Cube", "Cube")]},
        )
        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # Find the treeview used by the stage lister.
        stage_win_ref = ui_test.find("Stage")
        stage_win = stage_win_ref.window
        stage_win.focus()
        treeview = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True").widget

        # Select /World and retrieve the corresponding item from the treeview.
        sel = omni.usd.get_context().get_selection()
        sel.set_selected_prim_paths(["/World"], True)
        await ui_test.wait_n_updates(4)
        selected_item = treeview.selection[0]

        # Expand the /World item so that /World/Cube is visible.
        treeview.set_expanded(selected_item, True, False)

        # Click on the /World/Cube item and drag it into the graph view.
        await ui_test.emulate_mouse_drag_and_drop(ui_test.Vec2(136, 183), ui_test.Vec2(896, 194))
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # The prim drop menu should now be displayed and the mouse pointer should already be over its
        # 'Read Attribute' item. Let's click it.
        await ui_test.emulate_mouse_click()
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # TODO: OM-103661
        #
        # The golden image given below doesn't exist. Once OM-103661 has been fixed the image file can be created and
        # added to the extension and the test enabled.
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="omni.graph.window.core.test_drop_prim.png"
        )

    async def test_import_prims_compound(self):
        """
        Tests that calling import_prims with a compound graph prim will import the parent graph,
        and navigate to the compound node.
        """
        if not Supports.compound_subgraphs():
            return

        self._window = await self.create_test_window(width=1200, height=800)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        controller = og.Controller(update_usd=True)
        keys = controller.Keys
        (_, (compound,), _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    (
                        "Compound",
                        {
                            keys.CREATE_NODES: [
                                ("Add1", "omni.graph.nodes.Add"),
                                ("Add2", "omni.graph.nodes.Add"),
                            ],
                            keys.CONNECT: [
                                ("Add1.outputs:sum", "Add2.inputs:a"),
                                ("Add1.outputs:sum", "Add2.inputs:b"),
                            ],
                            keys.PROMOTE_ATTRIBUTES: [
                                ("Add1.inputs:a", "inputs:a"),
                                ("Add1.inputs:b", "inputs:b"),
                                ("Add2.outputs:sum", "outputs:out"),
                            ],
                        },
                    ),
                ]
            },
        )

        # get the path to the compound graph and import it
        compound_graph_path = compound.get_compound_graph_instance().get_path_to_graph()
        self._graph_window.import_prims([og.Controller.prim(compound_graph_path)])  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # the final image should show
        # the proper navigation bar
        # the add nodes, the input and outputs nodes, framed
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="omni.graph.window.core.test_import_prims_compound.png"
        )

    async def test_create_empty_compound_port_test(self):
        """Test the ability to create an empty port type on a compound node"""

        self._window = await self.create_test_window(width=1200, height=800)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        controller = og.Controller(update_usd=True)
        keys = controller.Keys
        (graph, (compound,), _, nodes) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    (
                        "Compound",
                        {
                            keys.CREATE_NODES: [
                                ("Add1", "omni.graph.nodes.Add"),
                            ],
                        },
                    ),
                ]
            },
        )

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # set the position of the nodes, including input and output
        prim_path = Sdf.Path(compound.get_compound_graph_instance().get_path_to_graph())
        VirtualNodeHelper.set_virtual_node_position(prim_path.AppendProperty("inputs:in"), (0, -400))
        VirtualNodeHelper.set_virtual_node_position(prim_path.AppendProperty("outputs:outputs"), (550, -400))
        self.move_node(nodes["Add1"], (300, 0))

        self._graph_window._main_widget.enter_compound(og.Controller.prim(compound))  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # grab the input and output node
        input_node = self._graph_window._main_widget._isolation_model._input_nodes[0]  # noqa: protected-access
        output_node = self._graph_window._main_widget._isolation_model._output_nodes[0]  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        wait_for_menu_apply = 2

        # create a item for every listed type
        menu = OmniGraphEmptyPortContextMenu()
        OmniGraphPortContextMenuBase.build_type_tree()

        # just test the first in every type list
        types = ["any"] + [type_list[0] for _, type_list in OmniGraphPortContextMenuBase.type_tree.items() if type_list]
        types.sort()

        attr_count = len(compound.get_attributes())
        for type_name in types:
            menu.on_click(compound, type_name, is_input=False)
            await ui_test.wait_n_updates(wait_for_menu_apply)
            self.assertGreater(len(compound.get_attributes()), attr_count, f"Expected output {type_name} to be added")
            menu.on_click(compound, type_name, is_input=True)
            await ui_test.wait_n_updates(wait_for_menu_apply)
            self.assertGreater(len(compound.get_attributes()), attr_count, f"Expected input {type_name} to be added")

        # Force layout, since the input and output nodes should have become large!
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_empty_compound_port_types.png",
        )

    async def test_compound_with_self_connection(self):
        """
        Tests that self connection is corrected drawn when using compound nodes
        Self Connection means a connection between the 'input' and 'output' nodes
        """
        self._window = await self.create_test_window(width=1200, height=800)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        controller = og.Controller(update_usd=True)
        keys = controller.Keys
        (graph, (compound,), _, _) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Compound", {}),
                ],
                keys.CREATE_ATTRIBUTES: [
                    ("Compound.inputs:a_double", "double"),
                    ("Compound.inputs:a_union", ["double", "float"]),
                    ("Compound.inputs:a_exec", "execution"),
                    ("Compound.inputs:a_any", "any"),
                    ("Compound.outputs:a_double", "double"),
                    ("Compound.outputs:a_union", ["double", "float"]),
                    ("Compound.outputs:a_exec", "execution"),
                    ("Compound.outputs:a_any", "any"),
                ],
                # connect two prior to import
                keys.CONNECT: [
                    ("Compound.inputs:a_double", "Compound.outputs:a_double"),
                    ("Compound.inputs:a_union", "Compound.outputs:a_union"),
                ],
            },
        )

        # import the compound
        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        prim_path = Sdf.Path(compound.get_compound_graph_instance().get_path_to_graph())
        VirtualNodeHelper.set_virtual_node_position(prim_path.AppendProperty("inputs:in"), (0, -400))
        VirtualNodeHelper.set_virtual_node_position(prim_path.AppendProperty("outputs:outputs"), (550, -400))
        self._graph_window._main_widget.enter_compound(og.Controller.prim(compound))  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # connect the other two to validate they update while the graph is visible
        controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CONNECT: [
                    ("Compound.inputs:a_exec", "Compound.outputs:a_exec"),
                    ("Compound.inputs:a_any", "Compound.outputs:a_any"),
                ]
            },
        )

        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_compound_with_self_connection.png",
        )

    async def _set_up_variable_panel(self):
        usd_context = omni.usd.get_context()
        test_file_path = self._golden_img_dir.joinpath("test_variables.usda")
        await usd_context.open_stage_async(str(test_file_path))

        await self.create_test_area(width=1200, height=800, block_devices=False)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")
        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        self._graph_window.import_prims([og.Controller.prim("/World/PushGraph")])

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)
        self._graph_window.show_variables_tab()
        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

    async def test_variable_context_menu(self):
        """Test the context_menu of variable items"""
        await self._set_up_variable_panel()
        graph = og.get_graph_by_path("/World/PushGraph")

        # Right click on the first variable item(NewVariable), show context menu.
        var_item_pos = ui_test.Vec2(100, 115)
        await ui_test.emulate_mouse_move_and_click(var_item_pos, right_click=True, human_delay_speed=10)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        # click duplicate menu
        menu_root = await graph_ui_test.get_current_context_menu()
        await graph_ui_test.run_menu_item(menu_root, "Duplicate variable")
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        self.assertIsNotNone(graph.find_variable("NewVariable02"))

        # Right click on the first variable item(NewVariable), show context menu.
        await ui_test.emulate_mouse_move_and_click(var_item_pos, right_click=True, human_delay_speed=10)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # click delete menu
        menu_root = await graph_ui_test.get_current_context_menu()
        await graph_ui_test.run_menu_item(menu_root, "Delete variable")
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        self.assertIsNone(graph.find_variable("NewVariable"))

        # Right click on the first variable item(NewVariable01), show context menu.
        await ui_test.emulate_mouse_move_and_click(var_item_pos, right_click=True, human_delay_speed=10)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # click delete unused menu
        menu_root = await graph_ui_test.get_current_context_menu()
        await graph_ui_test.run_menu_item(menu_root, "Delete if unused")
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        self.assertIsNotNone(graph.find_variable("NewVariable01"))  # used variable not deleted

        # Right click on the variable item(NewVariable02), show context menu.
        new_variable_02_pos = ui_test.Vec2(100, 190)
        await ui_test.emulate_mouse_move_and_click(new_variable_02_pos, right_click=True, human_delay_speed=10)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # click delete unused menu
        menu_root = await graph_ui_test.get_current_context_menu()
        await graph_ui_test.run_menu_item(menu_root, "Delete if unused")
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        self.assertIsNone(graph.find_variable("NewVariable02"))  # unused variable is deleted

        # show Edit menu
        edit_menu_pos = ui_test.Vec2(160, 20)
        await ui_test.emulate_mouse_move_and_click(edit_menu_pos)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # click delete all unused menu
        menu_root = await graph_ui_test.get_current_context_menu()
        await graph_ui_test.run_menu_item(menu_root, "Delete all unused variables")
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        self.assertIsNotNone(graph.find_variable("NewVariable01"))
        self.assertIsNotNone(graph.find_variable("test0"))
        self.assertIsNotNone(graph.find_variable("test1"))
        self.assertIsNone(graph.find_variable("test101"))  # deleted

    async def test_variable_rename(self):
        await self._set_up_variable_panel()

        # select the variable item0,
        item0_pos = ui_test.Vec2(100, 150)
        await ui_test.emulate_mouse_move_and_click(item0_pos, double=True, human_delay_speed=10)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # input new name in name filed
        new_name = "new_name"
        item0_pos = ui_test.Vec2(100, 670)
        await ui_test.emulate_mouse_move_and_click(item0_pos, double=True, human_delay_speed=10)
        await ui_test.emulate_char_press(new_name)
        await ui_test.emulate_keyboard_press(KeyboardInput.ENTER)
        await ui_test.human_delay(self.wait_frames_for_graph_draw)

        # check the usd attributes
        node_names = [
            "read_variable_01",
            "read_variable_02",
            "read_variable_03",
            "write_variable_01",
            "write_variable_02",
        ]
        for node_name in node_names:
            node = og.get_node_by_path("/World/PushGraph/" + node_name)
            self.assertEqual(og.Controller.attribute("inputs:variableName", node).get(), new_name)

    async def test_variable_instances_window(self):
        await self._set_up_variable_panel()

        # open instances window of NewVariable01
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(230, 130), double=True, human_delay_speed=10)
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # drag and drop
        await ui_test.emulate_mouse_drag_and_drop(ui_test.Vec2(260, 140), ui_test.Vec2(400, 100))

        # select a instance
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(400, 130), human_delay_speed=10)

        await ui_test.human_delay(10)
        await self.finalize_test(
            threshold=self.MEAN_ERROR_THRESHOLD * 10.0,  # Title text is jumping around by one pixel
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_variable_instances_window.png",
        )

    async def test_exact_uiname(self):
        """OMREQ-487: If user has specified a uiName for an input/output, use it exactly, do not title case etc."""
        self._window = await self.create_test_window(width=1200, height=800)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        keys = og.Controller.Keys
        (graph, (test_node,), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("ui", "omni.graph.test.TestUI"),
                ],
            },
        )

        # Fix position of nodes for Golden Image
        self.move_node(node=test_node, pos=(37.0, 55.0))

        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_exact_uiname.png",
        )

    async def _build_renamed_compound_node(self):
        """Builds a graph with a compound node and renames it"""
        self._window = await self.create_test_window(width=1200, height=800)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        controller = og.Controller(update_usd=True)
        keys = controller.Keys
        (graph, _, _, nodes) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    (
                        "Compound",
                        {
                            keys.CREATE_NODES: [
                                ("Add1", "omni.graph.nodes.Add"),
                            ],
                            keys.PROMOTE_ATTRIBUTES: [
                                ("Add1.inputs:a", "inputs:a"),
                                ("Add1.inputs:b", "inputs:b"),
                                ("Add1.outputs:sum", "outputs:out"),
                            ],
                        },
                    ),
                    ("Add2", "omni.graph.nodes.Add"),
                    ("Add3", "omni.graph.nodes.Add"),
                    ("Add4", "omni.graph.nodes.Add"),
                ],
                keys.CONNECT: [
                    ("Add2.outputs:sum", "Compound.inputs:a"),
                    ("Add3.outputs:sum", "Compound.inputs:b"),
                    ("Compound.outputs:out", "Add4.inputs:a"),
                    ("Compound.outputs:out", "Add4.inputs:b"),
                ],
            },
        )

        # import the compound
        self.move_node(nodes["Add2"], (200, 0))
        self.move_node(nodes["Add3"], (400, 0))
        self.move_node(nodes["Compound"], (200, 200))
        self.move_node(nodes["Add4"], (400, 200))
        self._graph_window.import_prims([og.Controller.prim(graph.get_path_to_graph())])  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # rename the compound node
        compound = nodes["Compound"]
        old_compound_path = Sdf.Path(compound.get_prim_path())
        new_compound_path = old_compound_path.GetParentPath().AppendChild("renamed_compound")

        # Uses a move prim command which covers both the rename in editor, and from a different view
        # such as a property panel
        omni.kit.commands.execute("MovePrim", path_from=old_compound_path, path_to=new_compound_path)

        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        return (controller, new_compound_path)

    async def test_rename_compound_node(self):
        """Tests that compounds can be renamed and the name properly reflected in the UI"""

        (_, _) = await self._build_renamed_compound_node()
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_rename_compound_node.png",
        )

    async def test_can_enter_renamed_compound(self):
        """
        Tests the a renamed compound can still be entered via the UI. This is a visual test
        that helps validate the underlying structure of the compound remains in tact
        """
        (_, compound) = await self._build_renamed_compound_node()
        self._graph_window._main_widget.enter_compound(og.Controller.prim(compound))  # noqa: protected-access
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name="omni.graph.window.core.test_can_enter_renamed_compound.png",
        )
