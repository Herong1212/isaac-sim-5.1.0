import unittest
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Callable, List, Tuple

import carb
import carb.events
import omni.graph.core as og
import omni.graph.window.core as ogw
import omni.kit.test
import omni.ui as ui
import omni.usd
from omni.kit import ui_test
from omni.ui.tests.test_base import OmniUiTest
from pxr import Sdf

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
    def graph_widget(self) -> OgCoreTestGraphWidget:
        return self._main_widget

    @property
    def model(self) -> ogw.OmniGraphModel:
        return self._main_widget.model

    def show_variables_tab(self):
        self._main_widget.show_variables_tab()


class TestGraphModel(OmniUiTest):
    """Test suite for the GraphModel class."""

    TEST_GRAPH_PATH = "/World/TestGraph"
    wait_frames_for_visual_update = 5

    # It takes 6 frames for the nodes and connections to all draw in their proper positions.
    wait_frames_for_graph_draw = 6

    # Wait 10 frames for commands to execute and the graph to update
    wait_frames_for_commands = 10

    def get_connections(self):
        # The sole purpose of this method is so that we only need to disable the lint warnings in one place.
        return self._model._connections  # noqa: protected-access

    async def setUp(self):
        await super().setUp()

        await omni.usd.get_context().new_stage_async()
        self.stage = omni.usd.get_context().get_stage()
        self._window = None
        self._graph_window = None
        self._model = None

    async def tearDown(self):

        # These tests do not rely on a golden image
        await self.finalize_test_no_image()

        if self._graph_window:
            self._graph_window.destroy()
        if self._window:
            self._window.destroy()
        self._window = None
        self._graph_window = None
        self._model = None

        await super().tearDown()

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

    async def setup_test_graph(self, create_graph_callback: Callable) -> Tuple[og.Graph, List[og.Node]]:
        """
        Sets up the graph window, the graph topology and gets the GraphModel from the view

        Args:
            create_graph_callback: the callback used to create the graph.
                                   It is expected to have the same return type as Controller.edit().

        Return:
            Returns a tuple with the graph and the list of nodes.
        """
        self._window = await self.create_test_window(width=1200, height=800)
        self._graph_window = self.create_graph_window("OgWindowCoreTest")

        await ui_test.wait_n_updates(self.wait_frames_for_visual_update)

        (graph, nodes, _, _) = create_graph_callback()

        self._graph_window._import_prims(  # noqa: protected-access
            None, [og.Controller.prim(graph.get_path_to_graph())]
        )
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        # get the model
        self._model = self._graph_window.graph_widget.model

        self.assertTrue(self._model)

        return (graph, nodes)

    async def test_graph_model__create_connections__data_ports__works(self):
        """Validate that creating connections between two compatible data attributes works"""

        # Set up the window and the initial graph state
        keys = og.Controller.Keys
        (_, (source_node, target_node)) = await self.setup_test_graph(
            lambda: og.Controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.CREATE_NODES: [
                        ("Source", "omni.graph.nodes.ConstantString"),
                        ("Target", "omni.graph.nodes.AppendString"),
                    ]
                },
            )
        )

        # set up the new connection
        source_path = Sdf.Path(og.Controller.attribute_path(("inputs:value", source_node)))
        target_path = Sdf.Path(og.Controller.attribute_path(("inputs:value", target_node)))

        self._model[target_path].inputs = [source_path]

        # must wait for the UI to update before checking the connection in the model
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        self.assertEqual(1, len(self.get_connections()), "Failed to create the connection")

    async def test_graph_model__create_connections__execution_ports__works(self):
        """Validate that execution inputs accept multiple incoming connections."""

        # Set up the window and the initial graph state
        keys = og.Controller.Keys
        (_, (on_tick_node, on_event_node, set_cam_node)) = await self.setup_test_graph(
            lambda: og.Controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.CREATE_NODES: [
                        ("OnTick", "omni.graph.action.OnTick"),
                        ("OnEvent", "omni.graph.action.OnCustomEvent"),
                        ("SetCam", "omni.graph.ui.SetActiveViewportCamera"),
                    ]
                },
            )
        )

        source_path1 = Sdf.Path(og.Controller.attribute_path(("outputs:tick", on_tick_node)))
        source_path2 = Sdf.Path(og.Controller.attribute_path(("outputs:execOut", on_event_node)))
        target_path = Sdf.Path(og.Controller.attribute_path(("inputs:execIn", set_cam_node)))

        # set up the new connection
        self._model[target_path].inputs = [source_path1]

        # must wait for the UI to update before checking the connection in the model
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        src = self.get_connections().get(target_path, None)
        self.assertEqual(src, {source_path1}, "The expected connection is not set")

        # set up a second connection
        self._model[target_path].inputs = [source_path2]

        # must wait for the UI to update before checking the connection in the model
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        src = self.get_connections().get(target_path, None)
        self.assertEqual(src, {source_path1, source_path2}, "The expected connection is not set")

    @unittest.skipIf(og.get_kit_version()[0] < 105, "ReadPrims node not available prior to Kit 105")
    async def test_graph_model__create_connections__bundle_ports__works(self):
        """Validate the expected behavior for bundle ports"""

        # Set up the window and the initial graph state
        def __create_graph_with_bundle():
            prim_cube = og.Controller.create_prim("/cube", {}, "Cube")
            (major, minor) = og.get_kit_version()

            return og.Controller.edit(
                "/World/TestGraph",
                {
                    og.Controller.Keys.CREATE_NODES: [
                        # Note: read prims should be used in 105.0 and v2 in 105.1. This node isn't available before 105
                        # so we can assume that major version will be 105 or higher
                        (
                            "read_prims",
                            (
                                "omni.graph.nodes.ReadPrimsV2"
                                if major > 105 or minor > 0
                                else "omni.graph.nodes.ReadPrims"
                            ),
                        ),
                        ("extract_prim", "omni.graph.nodes.ExtractPrim"),
                        ("extract_bundle", "omni.graph.nodes.ExtractBundle"),
                    ],
                    og.Controller.Keys.SET_VALUES: [
                        ("extract_prim.inputs:primPath", str(prim_cube.GetPath())),
                    ],
                },
            )

        (_, (read_prims_node, extract_prim_node, extract_bundle_node)) = await self.setup_test_graph(
            __create_graph_with_bundle
        )

        # As of kit 105.1/omni.graph.core 2.140.0, bundle paths have moved from prims to attributes.
        source_path1 = Sdf.Path(og.Controller.attribute_path(("outputs_primsBundle", read_prims_node)))
        source_path1_alt = source_path1.GetPrimPath().AppendProperty("outputs:primsBundle")
        target_path1 = Sdf.Path(og.Controller.attribute_path(("inputs:prims", extract_prim_node)))
        source_path2 = Sdf.Path(og.Controller.attribute_path(("outputs_primBundle", extract_prim_node)))
        source_path2_alt = source_path2.GetPrimPath().AppendProperty("outputs:primBundle")
        target_path2 = Sdf.Path(og.Controller.attribute_path(("inputs:bundle", extract_bundle_node)))

        # set up the new connections
        self._model[target_path1].inputs = [source_path1]
        self._model[target_path2].inputs = [source_path2]

        # must wait for the UI to update before checking the connection in the model
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        self.assertEqual(2, len(self.get_connections()))
        src1 = self.get_connections().get(target_path1, None)
        self.assertTrue(src1 in [{source_path1}, {source_path1_alt}], "The expected connection is not set")
        src2 = self.get_connections().get(target_path2, None)
        self.assertTrue(src2 in [{source_path2}, {source_path2_alt}], "The expected connection is not set")

    async def test_graph_model__set_inputs__empty_values__removes_existing_connections(self):
        """Validate that setting an empty set of inputs for a port results in the removal of the existing connections"""

        # Set up the window and the initial graph state
        keys = og.Controller.Keys
        (_, (source1, target)) = await self.setup_test_graph(
            lambda: og.Controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.CREATE_NODES: [
                        ("Source1", "omni.graph.nodes.ConstantString"),
                        ("Target", "omni.graph.nodes.AppendString"),
                    ],
                    keys.CONNECT: [
                        ("Source1.inputs:value", "Target.inputs:value"),
                    ],
                },
            )
        )

        # Ensure that the connection is registered in the UI
        original_source_path = Sdf.Path(og.Controller.attribute_path(("inputs:value", source1)))
        target_path = Sdf.Path(og.Controller.attribute_path(("inputs:value", target)))

        self.assertEqual(1, len(self.get_connections()), "The graph is not set up")
        src = self.get_connections().get(target_path, None)
        self.assertEqual(src, {original_source_path}, "The expected connection is not set")

        # Set an empty input list
        self._model[target_path].inputs = []

        # must wait for the UI to update before checking the connection in the model
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        self.assertEqual(0, len(self.get_connections()), "The existing connection was not removed")
        src = self.get_connections().get(target_path, None)
        self.assertIsNone(src, "The connection was not removed")

    async def test_graph_model__create_connections__data_ports__removes_previous_connections(self):
        """Validate that new connections on a regular port replaces existing connections"""

        # Set up the window and the initial graph state
        keys = og.Controller.Keys
        (_, (source1, source2, target)) = await self.setup_test_graph(
            lambda: og.Controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.CREATE_NODES: [
                        ("Source1", "omni.graph.nodes.ConstantString"),
                        ("Source2", "omni.graph.nodes.ConstantString"),
                        ("Target", "omni.graph.nodes.AppendString"),
                    ],
                    keys.CONNECT: [
                        ("Source1.inputs:value", "Target.inputs:value"),
                    ],
                },
            )
        )

        # Ensure that the connection is registered in the UI
        original_source_path = Sdf.Path(og.Controller.attribute_path(("inputs:value", source1)))
        new_source_path = Sdf.Path(og.Controller.attribute_path(("inputs:value", source2)))
        target_path = Sdf.Path(og.Controller.attribute_path(("inputs:value", target)))

        self.assertEqual(1, len(self.get_connections()), "The graph is not set up")
        src = self.get_connections().get(target_path, None)
        self.assertEqual(src, {original_source_path}, "The expected connection is not set")

        # Set up the new connection
        self._model[target_path].inputs = [new_source_path]

        # must wait for the UI to update before checking the connection in the model
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        self.assertEqual(1, len(self.get_connections()), "Failed to create the connection")
        src = self.get_connections().get(target_path, None)
        self.assertEqual(src, {new_source_path}, "The connection was not changed")

    @unittest.skipIf(og.get_kit_version() < (105, 1), "ReadPrimsV2 node not available prior to Kit 105.1")
    async def test_graph_model__create_connections__bundle_ports__removes_previous_connections(self):
        """Validate that new connections on bundle ports replace existing connections"""

        # Set up the window and the initial graph state
        def __create_graph_with_bundle():
            prim_cube = og.Controller.create_prim("/cube", {}, "Cube")
            prim_cone = og.Controller.create_prim("/cone", {}, "Cone")

            return og.Controller.edit(
                "/World/TestGraph",
                {
                    og.Controller.Keys.CREATE_NODES: [
                        ("read_prims1", "omni.graph.nodes.ReadPrimsV2"),
                        ("read_prims2", "omni.graph.nodes.ReadPrimsV2"),
                        ("extract_prim", "omni.graph.nodes.ExtractPrim"),
                    ],
                    og.Controller.Keys.CONNECT: [
                        ("read_prims1.outputs_primsBundle", "extract_prim.inputs:prims"),
                    ],
                    og.Controller.Keys.SET_VALUES: [
                        ("read_prims1.inputs:prims", prim_cube.GetPath()),
                        ("read_prims2.inputs:prims", prim_cone.GetPath()),
                        ("extract_prim.inputs:prim", prim_cube.GetPath()),
                    ],
                },
            )

        (_, (read_prims_node1, read_prims_node2, extract_prim_node)) = await self.setup_test_graph(
            __create_graph_with_bundle
        )

        source_path1 = Sdf.Path(og.Controller.attribute_path(("outputs_primsBundle", read_prims_node1)))
        source_path2 = Sdf.Path(og.Controller.attribute_path(("outputs_primsBundle", read_prims_node2)))
        target_path = Sdf.Path(og.Controller.attribute_path(("inputs:prims", extract_prim_node)))

        self.assertEqual(1, len(self.get_connections()))
        src = self.get_connections().get(target_path, None)
        self.assertEqual(src, {source_path1})

        # set up the new connections
        self._model[target_path].inputs = [source_path2]

        # must wait for the UI to update before checking the connection in the model
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        self.assertEqual(1, len(self.get_connections()))
        src = self.get_connections().get(target_path, None)
        self.assertEqual(src, {source_path2}, "The expected connection is not set")

    async def test_graph_model__create_connections__ports_with_incompatible_types__keeps_previous_connections(self):
        """Validate that when attempting to create connections between incompatible attributes, existing connections in the target port are preserved"""

        # Set up the window and the initial graph state
        keys = og.Controller.Keys
        (_, (source1, source2, target)) = await self.setup_test_graph(
            lambda: og.Controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.CREATE_NODES: [
                        ("Source1", "omni.graph.nodes.ConstantString"),
                        ("Source2", "omni.graph.nodes.ConstantFloat"),
                        ("Target", "omni.graph.nodes.AppendString"),
                    ],
                    keys.CONNECT: [
                        ("Source1.inputs:value", "Target.inputs:value"),
                    ],
                },
            )
        )

        # set up the new connection
        original_source_path = Sdf.Path(og.Controller.attribute_path(("inputs:value", source1)))
        new_source_path = Sdf.Path(og.Controller.attribute_path(("inputs:value", source2)))
        target_path = Sdf.Path(og.Controller.attribute_path(("inputs:value", target)))

        with self.CarbLogSuppressor():
            self._model[target_path].inputs = [new_source_path]

        # must wait for the UI to update before checking the connection in the model
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        self.assertEqual(1, len(self.get_connections()), "Failed to create the connection")
        src = self.get_connections().get(target_path, None)
        self.assertEqual(src, {original_source_path}, "The connection was not changed")

    async def test_graph_model__usd_notification_callback_test(self):
        """Tests the double-buffered notification callback mechanism inside the graph model"""

        def dirty_frame_index():
            """Returns the current 'dirty' frame index of the graph model"""
            return self._model._OmniGraphModel__dirty_frame_index  # noqa PLW0212

        # Set up the window and the initial graph state
        controller = og.Controller(update_usd=True)
        keys = og.Controller.Keys
        (_, (add1, add2)) = await self.setup_test_graph(
            lambda: controller.edit(
                self.TEST_GRAPH_PATH,
                {
                    keys.CREATE_NODES: [
                        ("Add1", "omni.graph.nodes.Add"),
                        ("Add2", "omni.graph.nodes.Add"),
                    ],
                    keys.CREATE_PRIMS: [
                        ("/World/Prim", "Xform"),
                    ],
                },
            )
        )

        await ui_test.wait_n_updates(1)
        index = dirty_frame_index()
        num_test_frames = 4

        # process frame should not advance prior to any changes
        for _ in range(0, num_test_frames):
            await ui_test.wait_n_updates(1)
            self.assertEqual(index, dirty_frame_index())

        # modifying a node prim should flip the dirty index
        for i in range(0, num_test_frames):
            self.stage.GetPrimAtPath(add1.get_prim_path()).CreateAttribute(f"test{i}", Sdf.ValueTypeNames.Int)
            await ui_test.wait_n_updates(1)
            self.assertNotEqual(index, dirty_frame_index())
            index = dirty_frame_index()

        # modifying a non-graph prim should not flip the dirty index
        for i in range(0, num_test_frames):
            self.stage.GetPrimAtPath("/World/Prim").CreateAttribute(f"test{i}", Sdf.ValueTypeNames.Int)
            await ui_test.wait_n_updates(1)
            self.assertEqual(index, dirty_frame_index())

        # modifying a graph prim should flip the dirty index
        for i in range(0, num_test_frames):
            self.stage.GetPrimAtPath(self.TEST_GRAPH_PATH).CreateAttribute(f"test{i}", Sdf.ValueTypeNames.Int)
            await ui_test.wait_n_updates(1)
            self.assertNotEqual(index, dirty_frame_index())
            index = dirty_frame_index()

        # updating an attribute should flip the dirty index
        for i in range(0, num_test_frames):
            self.stage.GetPrimAtPath(add1.get_prim_path()).GetAttribute(f"test{i}").Set(1)
            await ui_test.wait_n_updates(1)
            self.assertNotEqual(index, dirty_frame_index())
            index = dirty_frame_index()

        # removing an attribute should flip the dirty index
        for i in range(0, num_test_frames):
            self.stage.GetPrimAtPath(add1.get_prim_path()).RemoveProperty(f"test{i}")
            await ui_test.wait_n_updates(1)
            self.assertNotEqual(index, dirty_frame_index())
            index = dirty_frame_index()

        # no changes should not flip the dirty index
        for _ in range(0, num_test_frames):
            await ui_test.wait_n_updates(1)
            self.assertEqual(index, dirty_frame_index())

        # connect attributes via USD
        add1_output = self.stage.GetPrimAtPath(add1.get_prim_path()).GetAttribute("outputs:sum").GetPath()
        add2_input = self.stage.GetPrimAtPath(add2.get_prim_path()).GetAttribute("inputs:a").GetPath()
        self.stage.GetAttributeAtPath(add2_input).AddConnection(add1_output)
        # wait 2 frames - both the test and model have ui_tick updates methods, order is not guaranteed.
        await ui_test.wait_n_updates(2)
        self.assertNotEqual(index, dirty_frame_index())
        index = dirty_frame_index()
        self.assertEqual(self._model[self.stage.GetPrimAtPath(add1.get_prim_path())].connected_ports, {add1_output})

        # create a second graph - it should be ignored by the model
        other_graph_path = "/World/OtherGraph"
        og.Controller.edit(
            other_graph_path,
            {
                keys.CREATE_NODES: [
                    ("Add1", "omni.graph.nodes.Add"),
                ],
            },
        )
        await ui_test.wait_n_updates(1)
        self.assertEqual(index, dirty_frame_index())

        self.stage.GetPrimAtPath(other_graph_path).CreateAttribute("test0", Sdf.ValueTypeNames.Int)
        await ui_test.wait_n_updates(1)
        self.assertEqual(index, dirty_frame_index())

        # create a compound graph - it should be captured by the model
        controller.edit(
            self.TEST_GRAPH_PATH,
            {keys.CREATE_NODES: [("Compound", {keys.CREATE_NODES: [("Add3", "omni.graph.nodes.Add")]})]},
        )
        await ui_test.wait_n_updates(1)
        self.assertNotEqual(index, dirty_frame_index())

    async def test_events(self):
        graph, *_ = await self.setup_test_graph(lambda: og.Controller.edit(self.TEST_GRAPH_PATH))

        @dataclass
        class Results:
            item_added: bool = None
            event_src: str = None
            event_dst: str = None
            new_model: bool = None

        results = Results()

        def model_events(results: Results, event: carb.events.IEvent):
            results.item_added = None
            results.event_src = None
            results.event_dst = None

            if event.type == ogw.OmniGraphModel.EventType.NODE_REMOVED:
                results.item_added = False
                results.event_src = event.payload["path_str"]
            elif event.type == ogw.OmniGraphModel.EventType.NODE_ADDED:
                results.item_added = True
                results.event_src = event.payload["path_str"]

        model_sub = self._graph_window.model.get_event_stream().create_subscription_to_pop(
            partial(model_events, results)
        )

        def widget_events(results: Results, event: carb.events.IEvent):
            results.new_model = None

            if event.type == ogw.OmniGraphWidget.EventType.NEW_MODEL:
                results.new_model = True

        widget_sub = self._graph_window.graph_widget.get_event_stream().create_subscription_to_pop(
            partial(widget_events, results)
        )

        # Add node
        node_path_str = self.TEST_GRAPH_PATH + "/add"
        graph.create_node(node_path_str, "omni.graph.nodes.Add", True)
        await ui_test.wait_n_updates(2)
        self.assertEqual(results.item_added, True)
        self.assertEqual(results.event_src, node_path_str)
        self.assertTrue(results.event_dst is None)

        # Remove node
        graph.destroy_node(node_path_str, True)
        await ui_test.wait_n_updates(2)
        self.assertEqual(results.item_added, False)
        self.assertEqual(results.event_src, node_path_str)
        self.assertTrue(results.event_dst is None)

        # Change models by importing a different graph.
        old_model = self._graph_window.graph_widget.model
        graph2, *_ = og.Controller.edit("/World/TestGraph2")
        self._graph_window._import_prims(  # noqa: protected-access
            None, [og.Controller.prim(graph2.get_path_to_graph())]
        )
        await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        self.assertTrue(results.new_model)
        self.assertFalse(self._graph_window.graph_widget.model is None)
        self.assertNotEqual(self._graph_window.graph_widget.model, old_model)

        model_sub.unsubscribe()
        widget_sub.unsubscribe()

    class CarbLogSuppressor:
        def __init__(self):
            self.logging = carb.logging.acquire_logging()
            self.log_was_enabled = self.logging.is_log_enabled()

        def __enter__(self):
            # turn off carb logging so the error does not trigger test failure
            # og logging still works and logs node error message.
            self.logging.set_log_enabled(False)
            return self

        def __exit__(self, *_):
            # restore carb logging
            self.logging.set_log_enabled(self.log_was_enabled)
