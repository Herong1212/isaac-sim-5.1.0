# noqa: PLC0302
import asyncio
import unittest
from pathlib import Path
from typing import Any, Dict, List

import carb
import carb.settings
import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.test
import omni.usd
from omni.kit import ui_test
from omni.kit.ui_test.input import (
    emulate_mouse_drag_and_drop,
    emulate_mouse_move,
    emulate_mouse_move_and_click,
    emulate_mouse_scroll,
)
from omni.kit.ui_test.vec2 import Vec2
from omni.ui.tests.test_base import OmniUiTest


async def wait_for_streaming(usd_context, wait_frames: int = 10, max_loops: int = 1000) -> bool:
    """
    Waits until the stage is done streaming, or the maximum number of loops is reached.

    Args:
        usd_context: The USD context object.
        wait_frames: The number of frames to wait after the stage streaming is complete.
        max_loops: The maximum number of loops to try.

    Return:
        Returns True if streaming finished before max_loops was reached, otherwise returns False.
    """
    # NOTE: this is a copy of the function from omni.rtx.tests
    # https://gitlab-master.nvidia.com/omniverse/rtxdev/kit/-/blob/master/kit/source/extensions/omni.rtx.tests/omni/rtx/tests/test_common.py#L107

    wait_success = True
    while True:
        is_busy = usd_context.get_stage_streaming_status()
        if is_busy:
            await omni.kit.app.get_app().next_update_async()
            max_loops -= 1
            if max_loops == 0:
                carb.log_warn("Waiting for stage streaming timeout")
                wait_success = False
                break
            continue
        carb.log_info("Waiting for stage streaming done")
        break

    usd_context.reset_renderer_accumulation()

    frame_count = 0
    while frame_count < wait_frames:
        await omni.kit.app.get_app().next_update_async()
        frame_count += 1
        continue

    return wait_success


class TestUINodes(OmniUiTest):
    def __init__(self, tests=()):
        super().__init__(tests)
        self.settings = carb.settings.get_settings()

        # The first value for each setting is what we want to set it to, the second is where we will store
        # its original value.
        self.viewport_settings: Dict[str, List[Any, Any]] = {
            "/persistent/app/viewport/displayOptions": [0, None],
            "/app/viewport/grid/enabled": [False, None],
            "/persistent/app/viewport/{vp_id}/guide/grid/visible": [False, None],
            "/persistent/app/viewport/{vp_id}/guide/axis/visible": [False, None],
            # This doesn't currently work while the test is running so we set it in the test args instead.
            # "/persistent/app/viewport/{vp_id}/hud/visible": [False, None],
        }

        self.TEST_GRAPH_PATH = "/World/TestGraph"
        self.wait_frames_for_visual_update = 5

        # It takes 6 frames for the nodes and connections to all draw in their proper positions.
        self.wait_frames_for_graph_draw = 6

        # Wait 10 frames for commands to execute and the graph to update
        self.wait_frames_for_commands = 10

    async def setUp(self):
        """Set up test environment, to be torn down when done"""
        await super().setUp()
        self.viewport_name, self.viewport_id = self.get_viewport_name_and_id()
        self._golden_img_dir = Path(__file__).parent / "data" / "golden_images"

        # Make sure the viewport looks the same as when we generated the golden images.
        for setting, values in self.viewport_settings.items():
            key = setting.format(vp_id=self.viewport_id)
            values[1] = self.settings.get(key)
            self.settings.set(key, values[0])

        await omni.usd.get_context().new_stage_async()
        self.stage = omni.usd.get_context().get_stage()

    async def tearDown(self):
        self._golden_img_dir = None
        await super().tearDown()

        # Restore viewport settings.
        for setting, (values) in self.viewport_settings.items():
            key = setting.format(vp_id=self.viewport_id)
            if values[1] is None:
                self.settings.destroy_item(key)
            else:
                self.settings.set(key, values[1])
                values[1] = None

        omni.usd.get_context().close_stage()  # Activate OnClosing node

    def get_viewport_name_and_id(self):
        try:
            import omni.kit.viewport.window as vp

            viewport = next(vp.get_viewport_window_instances())
            return (viewport.name, viewport.viewport_api.id)
        except StopIteration as exc:
            raise og.OmniGraphError("Legacy viewport not supported for UI nodes.") from exc

    def create_graph(self) -> og.Graph:
        """Create an execution graph."""
        return og.Controller.create_graph({"graph_path": self.TEST_GRAPH_PATH, "evaluator_name": "execution"})

    async def edit_ui_execution_graph(self, graph_path: str, graph_node_data: dict, error_thrown=False):
        """Edit graph with nodes, connections and values common to all tests."""

        keys = og.Controller.Keys
        data = og.Controller.edit(
            graph_path,
            {
                keys.CREATE_NODES: [
                    ("onLoaded", "omni.graph.action.OnLoaded"),
                    ("viewport", "omni.graph.ui_nodes.SetViewportMode"),
                    ("viewportClose", "omni.graph.ui_nodes.SetViewportMode"),
                    ("onClosing", "omni.graph.action.OnClosing"),
                ]
                + graph_node_data.get(keys.CREATE_NODES, []),
                keys.CONNECT: [
                    ("onLoaded.outputs:execOut", "viewport.inputs:execIn"),
                    ("onClosing.outputs:execOut", "viewportClose.inputs:execIn"),
                ]
                + graph_node_data.get(keys.CONNECT, []),
                keys.SET_VALUES: [
                    ("viewport.inputs:viewport", self.viewport_name),
                    ("viewportClose.inputs:viewport", self.viewport_name),
                    ("viewport.inputs:mode", 1),
                    ("viewport.inputs:enablePicking", True),
                ]
                + graph_node_data.get(keys.SET_VALUES, []),
            },
        )

        # There's no graph window so we're not actually waiting for it to draw, but we still need
        # to give some time for all the connections to resolve.
        if error_thrown:
            with ogts.ExpectedError():
                await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)
        else:
            await ui_test.wait_n_updates(self.wait_frames_for_graph_draw)

        return data

    def get_attribute(self, attribute, node):
        return og.Controller.get(og.Controller.attribute(attribute, node))

    def get_attribute_and_assert_equals(self, attribute, node, expected):
        attr = self.get_attribute(attribute, node)
        self.assertEquals(attr, expected)

    def get_attribute_and_assert_list_equals(self, attribute, node, expected):
        attr = self.get_attribute(attribute, node).tolist()
        self.assertListEqual(attr, expected)

    def get_attribute_and_assert_list_almost_equals(self, attribute, node, expected):
        attr = self.get_attribute(attribute, node).tolist()
        for a, e in zip(attr, expected):
            self.assertAlmostEquals(a, e)

    async def test_set_viewport_mode(self):
        """Test SetViewportMode UI node"""
        graph = self.create_graph()

        keys = og.Controller.Keys
        (_, (_, viewport, _, _), _, _) = await self.edit_ui_execution_graph(
            graph,
            {
                keys.SET_VALUES: [("viewport.inputs:mode", 0)],
            },
        )

        self.get_attribute_and_assert_equals("outputs:scriptedMode", viewport, 0)
        self.get_attribute_and_assert_equals("outputs:defaultMode", viewport, 1)

    async def test_set_viewport_mode_inputs(self):
        """Test SetViewportMode UI node's handling of invalid inputs"""
        graph = self.create_graph()
        keys = og.Controller.Keys
        (_, (trigger_node, mode_node, counter_node), *_) = og.Controller.edit(
            graph,
            {
                keys.CREATE_NODES: [
                    ("trigger", "omni.graph.action.OnImpulseEvent"),
                    ("viewport_mode", "omni.graph.ui_nodes.SetViewportMode"),
                    ("counter", "omni.graph.action.Counter"),
                ],
                keys.CONNECT: [
                    ("trigger.outputs:execOut", "viewport_mode.inputs:execIn"),
                    ("viewport_mode.outputs:scriptedMode", "counter.inputs:execIn"),
                ],
                keys.SET_VALUES: [
                    ("trigger.inputs:onlyPlayback", False),
                    ("viewport_mode.inputs:mode", 1),
                ],
            },
        )

        trigger_attr = trigger_node.get_attribute("state:enableImpulse")
        count_attr = counter_node.get_attribute("outputs:count")
        vp_name_attr = mode_node.get_attribute("inputs:viewport")

        # The count should start out 0.
        self.assertEqual(count_attr.get(), 0, "Starting count")

        # Set the viewport name to blank and trigger the graph. The count should remain 0.
        with self.CarbLogSuppressor():
            vp_name = vp_name_attr.get()
            vp_name_attr.set("")
            trigger_attr.set(True)
            await ui_test.wait_n_updates(2)
        self.assertEqual(count_attr.get(), 0, "Count with missing viewport name")

        # Set the viewport name to something invalid and trigger the graph. The count should remain 0.
        with self.CarbLogSuppressor():
            vp_name_attr.set("invalid")
            trigger_attr.set(True)
            await ui_test.wait_n_updates(2)
        self.assertEqual(count_attr.get(), 0, "Count with invalid viewport name")

        # Set the viewport name correctly and trigger the graph. The count should increment to 1.
        vp_name_attr.set(vp_name)
        trigger_attr.set(True)
        await ui_test.wait_n_updates(2)
        self.assertEqual(count_attr.get(), 1, "Count with valid viewport name")

        # Return the viewport default mode. The count should remain at 1.
        vp_mode_attr = mode_node.get_attribute("inputs:mode")
        vp_mode_attr.set(0)
        trigger_attr.set(True)
        await ui_test.wait_n_updates(2)
        self.assertEqual(count_attr.get(), 1, "Count after returning to default mode")

    async def test_on_viewport_clicked(self):
        """Test OnViewportClicked and ReadViewportClickState UI nodes"""
        graph = self.create_graph()

        keys = og.Controller.Keys
        (_, (_, _, _, _, on_viewport_clicked, viewport_click_state, _, _), _, _) = await self.edit_ui_execution_graph(
            graph,
            {
                keys.CREATE_NODES: [
                    ("on_viewport_clicked", "omni.graph.ui_nodes.OnViewportClicked"),
                    ("viewport_click_state", "omni.graph.ui_nodes.ReadViewportClickState"),
                    ("to_string", "omni.graph.nodes.ToString"),
                    ("print", "omni.graph.ui_nodes.PrintText"),
                ],
                keys.CONNECT: [
                    ("viewport_click_state.outputs:position", "to_string.inputs:value"),
                    ("to_string.outputs:converted", "print.inputs:text"),
                    ("on_viewport_clicked.outputs:clicked", "print.inputs:execIn"),
                ],
                keys.SET_VALUES: [
                    ("viewport.inputs:enableViewportMouseEvents", True),
                    ("on_viewport_clicked.inputs:viewport", self.viewport_name),
                    ("viewport_click_state.inputs:viewport", self.viewport_name),
                    ("on_viewport_clicked.inputs:onlyPlayback", False),
                ],
            },
        )

        # Click inside viewport
        await emulate_mouse_move_and_click(Vec2(85, 255))
        position = [72.40223463687151, 175.86592178770954]  # Translated (x, y) position of the mouse click

        self.get_attribute_and_assert_equals("inputs:gesture", on_viewport_clicked, "Left Mouse Click")
        self.get_attribute_and_assert_equals("inputs:gesture", viewport_click_state, "Left Mouse Click")
        self.get_attribute_and_assert_list_almost_equals("outputs:position", on_viewport_clicked, position)
        self.get_attribute_and_assert_list_almost_equals("outputs:position", viewport_click_state, position)
        self.get_attribute_and_assert_equals("outputs:isValid", viewport_click_state, True)

    async def test_on_viewport_pressed(self):
        """Test OnViewportPressed UI node"""
        graph = self.create_graph()

        keys = og.Controller.Keys
        (
            _,
            (_, _, _, _, on_viewport_pressed, viewport_press_state, _, _, _, _),
            _,
            _,
        ) = await self.edit_ui_execution_graph(
            graph,
            {
                keys.CREATE_NODES: [
                    ("on_viewport_pressed", "omni.graph.ui_nodes.OnViewportPressed"),
                    ("viewport_press_state", "omni.graph.ui_nodes.ReadViewportPressState"),
                    ("to_string", "omni.graph.nodes.ToString"),
                    ("to_string2", "omni.graph.nodes.ToString"),
                    ("print", "omni.graph.ui_nodes.PrintText"),
                    ("print2", "omni.graph.ui_nodes.PrintText"),
                ],
                keys.CONNECT: [
                    ("viewport_press_state.outputs:pressPosition", "to_string.inputs:value"),
                    ("viewport_press_state.outputs:releasePosition", "to_string2.inputs:value"),
                    ("to_string.outputs:converted", "print.inputs:text"),
                    ("to_string2.outputs:converted", "print2.inputs:text"),
                    ("on_viewport_pressed.outputs:pressed", "print.inputs:execIn"),
                    ("on_viewport_pressed.outputs:released", "print2.inputs:execIn"),
                ],
                keys.SET_VALUES: [
                    ("viewport.inputs:enableViewportMouseEvents", True),
                    ("on_viewport_pressed.inputs:viewport", self.viewport_name),
                    ("viewport_press_state.inputs:viewport", self.viewport_name),
                    ("on_viewport_pressed.inputs:onlyPlayback", False),
                ],
            },
        )

        # Click inside viewport
        await emulate_mouse_move_and_click(Vec2(85, 255))
        position = [72.40223463687151, 175.86592178770954]  # Translated (x, y) position of the mouse click

        self.get_attribute_and_assert_equals("inputs:gesture", on_viewport_pressed, "Left Mouse Press")
        self.get_attribute_and_assert_equals("inputs:gesture", viewport_press_state, "Left Mouse Press")
        self.get_attribute_and_assert_list_equals("outputs:pressPosition", on_viewport_pressed, position)
        self.get_attribute_and_assert_list_equals("outputs:releasePosition", on_viewport_pressed, position)
        self.get_attribute_and_assert_list_equals("outputs:pressPosition", viewport_press_state, position)
        self.get_attribute_and_assert_list_equals("outputs:releasePosition", viewport_press_state, position)
        self.get_attribute_and_assert_equals("outputs:isReleasePositionValid", viewport_press_state, True)
        self.get_attribute_and_assert_equals("outputs:isPressed", viewport_press_state, False)
        self.get_attribute_and_assert_equals("outputs:isValid", viewport_press_state, True)

    async def test_on_viewport_scrolled(self):
        """Test OnViewportScrolled UI node"""
        await self.create_test_area(width=1200, height=800, block_devices=False)

        graph = self.create_graph()

        keys = og.Controller.Keys
        (_, (_, _, _, _, on_viewport_scrolled, viewport_scroll_state, _, _), _, _) = await self.edit_ui_execution_graph(
            graph,
            {
                keys.CREATE_NODES: [
                    ("on_viewport_scrolled", "omni.graph.ui_nodes.OnViewportScrolled"),
                    ("viewport_scroll_state", "omni.graph.ui_nodes.ReadViewportScrollState"),
                    ("to_string", "omni.graph.nodes.ToString"),
                    ("print", "omni.graph.ui_nodes.PrintText"),
                ],
                keys.CONNECT: [
                    ("viewport_scroll_state.outputs:position", "to_string.inputs:value"),
                    ("to_string.outputs:converted", "print.inputs:text"),
                    ("on_viewport_scrolled.outputs:scrolled", "print.inputs:execIn"),
                ],
                keys.SET_VALUES: [
                    ("viewport.inputs:enableViewportMouseEvents", True),
                    ("on_viewport_scrolled.inputs:viewport", self.viewport_name),
                    ("viewport_scroll_state.inputs:viewport", self.viewport_name),
                    ("on_viewport_scrolled.inputs:onlyPlayback", False),
                ],
            },
        )

        # Click inside viewport
        await emulate_mouse_move(Vec2(85, 255))
        # As per OM-73671, scroll values are divided by screen size, so for a scrollValue of 1, need delta to be same as
        # the height
        await emulate_mouse_scroll(Vec2(0, 800))  # (x, y) make a variable
        position = [72.40223463687151, 175.86592178770954]

        self.get_attribute_and_assert_equals("outputs:scrolled", on_viewport_scrolled, 1)
        self.get_attribute_and_assert_list_equals("outputs:position", on_viewport_scrolled, position)
        self.get_attribute_and_assert_list_equals("outputs:position", viewport_scroll_state, position)
        self.get_attribute_and_assert_equals("outputs:scrollValue", on_viewport_scrolled, 1)
        self.get_attribute_and_assert_equals("outputs:scrollValue", viewport_scroll_state, 1)
        self.get_attribute_and_assert_equals("outputs:isValid", viewport_scroll_state, True)

        await self.finalize_test_no_image()

    async def test_on_viewport_hovered(self):
        """Test OnViewportHovered UI node"""
        graph = self.create_graph()
        await emulate_mouse_move(Vec2(0, 0))  # Move the cursor away from final position

        keys = og.Controller.Keys
        (_, (_, _, _, _, on_viewport_hover, viewport_hover_state, _, _), _, _) = await self.edit_ui_execution_graph(
            graph,
            {
                keys.CREATE_NODES: [
                    ("on_viewport_hover", "omni.graph.ui_nodes.OnViewportHovered"),
                    ("viewport_hover_state", "omni.graph.ui_nodes.ReadViewportHoverState"),
                    ("to_string", "omni.graph.nodes.ToString"),
                    ("print", "omni.graph.ui_nodes.PrintText"),
                ],
                keys.CONNECT: [
                    ("viewport_hover_state.outputs:position", "to_string.inputs:value"),
                    ("to_string.outputs:converted", "print.inputs:text"),
                    ("on_viewport_hover.outputs:began", "print.inputs:execIn"),
                ],
                keys.SET_VALUES: [
                    ("viewport.inputs:enableViewportMouseEvents", True),
                    ("on_viewport_hover.inputs:viewport", self.viewport_name),
                    ("viewport_hover_state.inputs:viewport", self.viewport_name),
                    ("on_viewport_hover.inputs:onlyPlayback", False),
                ],
            },
        )

        # Click inside viewport
        await emulate_mouse_move(Vec2(85, 255))
        position = [72.40223463687151, 175.86592178770954]

        self.get_attribute_and_assert_equals("outputs:began", on_viewport_hover, 1)
        self.get_attribute_and_assert_equals("outputs:isHovered", viewport_hover_state, True)
        self.get_attribute_and_assert_equals("outputs:isValid", viewport_hover_state, True)
        self.get_attribute_and_assert_list_equals("outputs:position", viewport_hover_state, position)

    async def test_on_viewport_dragged(self):
        """Test OnViewportDrag UI node"""
        graph = self.create_graph()

        keys = og.Controller.Keys
        (_, (_, _, _, _, on_viewport_dragged, viewport_drag_state, _, _), _, _) = await self.edit_ui_execution_graph(
            graph,
            {
                keys.CREATE_NODES: [
                    ("on_viewport_dragged", "omni.graph.ui_nodes.OnViewportDragged"),
                    ("viewport_drag_state", "omni.graph.ui_nodes.ReadViewportDragState"),
                    ("to_string", "omni.graph.nodes.ToString"),
                    ("print", "omni.graph.ui_nodes.PrintText"),
                ],
                keys.CONNECT: [
                    ("viewport_drag_state.outputs:currentPosition", "to_string.inputs:value"),
                    ("to_string.outputs:converted", "print.inputs:text"),
                    ("on_viewport_dragged.outputs:ended", "print.inputs:execIn"),
                ],
                keys.SET_VALUES: [
                    ("viewport.inputs:enableViewportMouseEvents", True),
                    ("on_viewport_dragged.inputs:viewport", self.viewport_name),
                    ("viewport_drag_state.inputs:viewport", self.viewport_name),
                    ("on_viewport_dragged.inputs:onlyPlayback", False),
                ],
            },
        )

        # Click inside viewport
        await emulate_mouse_drag_and_drop(Vec2(85, 255), Vec2(100, 455))
        start_position = [72.40223463687151, 175.86592178770954]
        end_position = [85.81005586592177, 354.6368715083799]

        self.get_attribute_and_assert_equals("inputs:gesture", on_viewport_dragged, "Left Mouse Drag")
        self.get_attribute_and_assert_list_equals("outputs:initialPosition", on_viewport_dragged, start_position)
        self.get_attribute_and_assert_list_equals("outputs:finalPosition", on_viewport_dragged, end_position)
        self.get_attribute_and_assert_list_equals("outputs:currentPosition", viewport_drag_state, end_position)
        self.get_attribute_and_assert_list_equals("outputs:initialPosition", viewport_drag_state, start_position)
        self.get_attribute_and_assert_list_equals("outputs:velocity", viewport_drag_state, [0, 0])
        self.get_attribute_and_assert_equals("outputs:isValid", viewport_drag_state, True)
        self.get_attribute_and_assert_equals("outputs:isDragInProgress", viewport_drag_state, False)

    async def test_on_viewport_dragged_began(self):
        """Test OnViewportDrag UI node where we begin the drag but don't complete it."""
        graph = self.create_graph()

        keys = og.Controller.Keys
        (_, (_, _, _, _, on_viewport_dragged, viewport_drag_state, _, _), _, _) = await self.edit_ui_execution_graph(
            graph,
            {
                keys.CREATE_NODES: [
                    ("on_viewport_dragged", "omni.graph.ui_nodes.OnViewportDragged"),
                    ("viewport_drag_state", "omni.graph.ui_nodes.ReadViewportDragState"),
                    ("to_string", "omni.graph.nodes.ToString"),
                    ("print", "omni.graph.ui_nodes.PrintText"),
                ],
                keys.CONNECT: [
                    ("viewport_drag_state.outputs:currentPosition", "to_string.inputs:value"),
                    ("to_string.outputs:converted", "print.inputs:text"),
                    ("on_viewport_dragged.outputs:began", "print.inputs:execIn"),
                ],
                keys.SET_VALUES: [
                    ("viewport.inputs:enableViewportMouseEvents", True),
                    ("on_viewport_dragged.inputs:viewport", self.viewport_name),
                    ("viewport_drag_state.inputs:viewport", self.viewport_name),
                    ("on_viewport_dragged.inputs:onlyPlayback", False),
                ],
            },
        )

        # Click inside viewport
        await emulate_mouse_drag_and_drop(Vec2(85, 255), Vec2(100, 455))
        start_position = [72.40223463687151, 175.86592178770954]
        velocity = [0.8938547486033599, 22.346368715083816]

        self.get_attribute_and_assert_equals("inputs:gesture", on_viewport_dragged, "Left Mouse Drag")
        self.get_attribute_and_assert_list_equals("outputs:initialPosition", on_viewport_dragged, start_position)
        self.get_attribute_and_assert_list_equals("outputs:initialPosition", viewport_drag_state, start_position)
        self.get_attribute_and_assert_list_equals("outputs:velocity", viewport_drag_state, velocity)
        self.get_attribute_and_assert_equals("outputs:isValid", viewport_drag_state, True)
        self.get_attribute_and_assert_equals("outputs:isDragInProgress", viewport_drag_state, True)

    async def test_get_set_active_viewport_camera(self):
        graph = self.create_graph()

        prim_path = "/OmniverseKit_Front"

        keys = og.Controller.Keys
        (_, (_, _, _, _, _, get_camera, _, _), _, _) = await self.edit_ui_execution_graph(
            graph,
            {
                keys.CREATE_NODES: [
                    ("set_camera", "omni.graph.ui_nodes.SetActiveViewportCamera"),
                    ("get_camera", "omni.graph.ui_nodes.GetActiveViewportCamera"),
                    ("to_string", "omni.graph.nodes.ToString"),
                    ("print", "omni.graph.ui_nodes.PrintText"),
                ],
                keys.CONNECT: [
                    ("viewport.outputs:scriptedMode", "set_camera.inputs:execIn"),
                    ("get_camera.outputs:camera", "to_string.inputs:value"),
                    ("set_camera.outputs:execOut", "print.inputs:execIn"),
                    ("to_string.outputs:converted", "print.inputs:text"),
                ],
                keys.SET_VALUES: [
                    ("set_camera.inputs:viewport", self.viewport_name),
                    ("set_camera.inputs:primPath", prim_path),
                ],
            },
        )

        self.get_attribute_and_assert_equals("outputs:camera", get_camera, prim_path)

    # Using emulate_mouse_move_and_click() doesn't trigger the OnPicked node, even when done through the
    # Script Editor in an interactive session.
    async def test_on_picked(self):
        graph = self.create_graph()
        keys = og.Controller.Keys
        (_, (_, _, _, _, _, counter), _, _) = await self.edit_ui_execution_graph(
            graph,
            {
                keys.CREATE_NODES: [
                    ("on_picked", "omni.graph.ui_nodes.OnPicked"),
                    ("counter", "omni.graph.action.Counter"),
                ],
                keys.CONNECT: [
                    ("on_picked.outputs:picked", "counter.inputs:execIn"),
                ],
                keys.SET_VALUES: [
                    ("on_picked.inputs:viewport", self.viewport_name),
                    ("on_picked.inputs:onlyPlayback", False),
                ],
            },
        )

        cube = ogts.create_cube(self.stage, "my_cube", (1, 1, 1))
        attr = cube.GetAttribute("size")
        attr.Set(10.0)

        # wait until the streaming of the stage completes
        self.assertTrue(await wait_for_streaming(omni.usd.get_context()))

        await emulate_mouse_move_and_click(Vec2(720, 450))
        await ui_test.wait_n_updates(5)

        self.get_attribute_and_assert_equals("outputs:count", counter, 1)

    @unittest.skip("Not working currently - selection not working")
    async def test_pass_clicks_thru(self):  # pragma: no cover
        selection: omni.usd.Selection = omni.usd.get_context().get_selection()

        # Load some geometry so that we have something which can be selected with a mouse click.
        # The pxr renderer (aka "Storm") has problems selecting implicit geometry such as that generated by
        # the Cube prim, so we need to use a mesh.
        (result, error) = await ogts.load_test_file("mesh-cube.usd", use_caller_subdirectory=True)
        self.assertTrue(result, error)

        cube_path = "/World/Cube"
        cube_pos = Vec2(700, 400)

        # Create an execution graph with a SetViewportMode node and a variable to control its passClicksThru.
        # An OnVariableChange node triggers the SetViewportMode node whenever the variable's value changes.
        graph = self.create_graph()
        keys = og.Controller.Keys

        controller = og.Controller()
        controller.edit(
            graph,
            {
                keys.CREATE_VARIABLES: [("passThruMode", "bool", False)],
                keys.CREATE_NODES: [
                    ("readVariable", "omni.graph.core.ReadVariable"),
                    ("viewportMode", "omni.graph.ui_nodes.SetViewportMode"),
                    ("variableChanged", "omni.graph.action.OnVariableChange"),
                    # These are needed to ensure that the viewport is set back to default mode when the test is done.
                    ("viewportClose", "omni.graph.ui_nodes.SetViewportMode"),
                    ("onClosing", "omni.graph.action.OnClosing"),
                ],
                keys.SET_VALUES: [
                    ("readVariable.inputs:variableName", "passThruMode"),
                    ("viewportMode.inputs:viewport", self.viewport_name),
                    ("viewportMode.inputs:mode", 1),
                    ("variableChanged.inputs:variableName", "passThruMode"),
                    ("variableChanged.inputs:onlyPlayback", False),
                    ("viewportClose.inputs:viewport", self.viewport_name),
                ],
                keys.CONNECT: [
                    ("readVariable.outputs:value", "viewportMode.inputs:passClicksThru"),
                    ("variableChanged.outputs:changed", "viewportMode.inputs:execIn"),
                    ("onClosing.outputs:execOut", "viewportClose.inputs:execIn"),
                ],
            },
        )

        variable = graph.find_variable("passThruMode")

        # Make sure nothing is selected and give the viewport some time to settle down.
        selection.clear_selected_prim_paths()
        await ui_test.wait_n_updates(2)

        # Enable passClicksThru and click on the cube. It should be selected.
        variable.set(graph.get_context(), True)
        await ui_test.wait_n_updates(2)

        await emulate_mouse_move_and_click(cube_pos)
        await ui_test.wait_n_updates(8)

        self.assertTrue(cube_path in selection.get_selected_prim_paths(), "Selection with passClicksThru True.")

        # Disable passClicksThru and click on the cube. It should not be selected.
        selection.clear_selected_prim_paths()
        variable.set(graph.get_context(), False)
        await ui_test.wait_n_updates(2)

        await emulate_mouse_move_and_click(cube_pos)
        await ui_test.wait_n_updates(8)

        self.assertFalse(cube_path in selection.get_selected_prim_paths(), "Selection with passClicksThru False.")

    # --------------------------------------------------------------------------------------------------------------
    @unittest.skip(
        "Works by itself, but causes other subsequent tests to fail, probably leaving things in a bad state."
    )
    async def test_omnigraph_ui_node_creation(self):  # pragma: no cover
        """Check that all of the registered omni.graph.ui nodes can be created without error."""
        graph_path = "/World/TestGraph"
        (graph, *_) = og.Controller.edit({"graph_path": graph_path, "evaluator_name": "push"})

        # Add one of every type of omni.graph.ui node to the graph.
        node_types = [t for t in og.get_registered_nodes() if t.startswith("omni.graph.ui")]
        prefix_len = len("omni.graph.ui_nodes.")
        node_names = [name[prefix_len:] for name in node_types]

        (_, nodes, _, _) = og.Controller.edit(
            graph, {og.Controller.Keys.CREATE_NODES: list(zip(node_names, node_types))}
        )
        self.assertEqual(len(nodes), len(node_types), "Check that all nodes were created.")

        for i, node in enumerate(nodes):
            self.assertEqual(
                node.get_prim_path(), graph_path + "/" + node_names[i], f"Check node type '{node_types[i]}'"
            )

    async def test_viewport_render_nodes(self):
        graph = self.create_graph()
        keys = og.Controller.Keys
        (_, _, _, node_dict) = og.Controller.edit(
            graph,
            {
                keys.CREATE_VARIABLES: [
                    ("fade_start", "double"),
                    ("fade_complete", "double"),
                    ("renderer", "token"),
                    ("resolution", "int[2]"),
                ],
                keys.CREATE_NODES: [
                    ("start_play", "omni.graph.action.OnStageEvent"),
                    ("stop_play", "omni.graph.action.OnStageEvent"),
                    ("lock_render", "omni.graph.ui_nodes.LockViewportRender"),
                    ("read_time", "omni.graph.nodes.ReadTime"),
                    ("write_start", "omni.graph.core.WriteVariable"),
                    ("write_complete", "omni.graph.core.WriteVariable"),
                    ("set_event", "omni.graph.action.OnImpulseEvent"),
                    ("get_event", "omni.graph.action.OnImpulseEvent"),
                    ("set_renderer", "omni.graph.ui_nodes.SetViewportRenderer"),
                    ("get_renderer", "omni.graph.ui_nodes.GetViewportRenderer"),
                    ("write_renderer", "omni.graph.core.WriteVariable"),
                    ("set_resolution", "omni.graph.ui_nodes.SetViewportResolution"),
                    ("get_resolution", "omni.graph.ui_nodes.GetViewportResolution"),
                    ("write_resolution", "omni.graph.core.WriteVariable"),
                ],
                keys.CONNECT: [
                    ("start_play.outputs:execOut", "lock_render.inputs:lock"),
                    ("stop_play.outputs:execOut", "lock_render.inputs:unlock"),
                    ("lock_render.outputs:fadeStarted", "write_start.inputs:execIn"),
                    ("lock_render.outputs:fadeComplete", "write_complete.inputs:execIn"),
                    ("read_time.outputs:absoluteSimTime", "write_start.inputs:value"),
                    ("read_time.outputs:absoluteSimTime", "write_complete.inputs:value"),
                    ("set_event.outputs:execOut", "set_renderer.inputs:exec"),
                    ("get_event.outputs:execOut", "write_renderer.inputs:execIn"),
                    ("get_renderer.outputs:renderer", "write_renderer.inputs:value"),
                    ("set_event.outputs:execOut", "set_resolution.inputs:exec"),
                    ("get_event.outputs:execOut", "write_resolution.inputs:execIn"),
                    ("get_resolution.outputs:resolution", "write_resolution.inputs:value"),
                ],
                keys.SET_VALUES: [
                    ("start_play.inputs:eventName", "OmniGraph Start Play"),
                    ("stop_play.inputs:eventName", "OmniGraph Stop Play"),
                    ("lock_render.inputs:fadeTime", 2.0),
                    ("write_start.inputs:variableName", "fade_start"),
                    ("write_complete.inputs:variableName", "fade_complete"),
                    ("set_event.inputs:onlyPlayback", False),
                    ("get_event.inputs:onlyPlayback", False),
                    ("write_renderer.inputs:variableName", "renderer"),
                    ("write_resolution.inputs:variableName", "resolution"),
                    ("set_resolution.inputs:resolution", (400, 300)),
                ],
            },
        )

        # Let the graph settle for a bit.
        await ui_test.wait_n_updates(4)

        # ---- Test viewport locking ----

        context = graph.get_context()
        fade_start_var = graph.find_variable("fade_start")
        fade_complete_var = graph.find_variable("fade_complete")

        # Both variables should be zero initially.
        self.assertEqual(fade_start_var.get(context), 0.0)
        self.assertEqual(fade_complete_var.get(context), 0.0)

        # Start and stop playing.
        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
        await ui_test.wait_n_updates(2)
        timeline.stop()

        # Wait more than 2 seconds for the fade to complete.
        await asyncio.sleep(4)

        # The difference between the start and complete values should be close to 2.0
        fade_delta = fade_complete_var.get(context) - fade_start_var.get(context)
        self.assertAlmostEqual(fade_delta, 2.0, places=1)

        # ---- Test changing viewport renderer ----

        # The current renderer should be the default: "RTX: Realtime"
        set_event_trigger = node_dict["set_event"].get_attribute("state:enableImpulse")
        get_event_trigger = node_dict["get_event"].get_attribute("state:enableImpulse")

        set_renderer_value = node_dict["set_renderer"].get_attribute("inputs:renderer")
        renderer_var = graph.find_variable("renderer")

        get_event_trigger.set(True)
        await ui_test.wait_n_updates(2)
        self.assertEqual(renderer_var.get(context), "RTX: Realtime")

        # Test the other supported renderers.
        for renderer in ("RTX: Path Tracing", "RTX: Iray", "RTX: Realtime"):
            set_renderer_value.set(renderer)
            set_event_trigger.set(True)
            await ui_test.wait_n_updates(2)

            get_event_trigger.set(True)
            await ui_test.wait_n_updates(2)
            self.assertEqual(renderer_var.get(context), renderer)

        # ---- Test changing viewport resolution ----

        set_resolution_value = node_dict["set_resolution"].get_attribute("inputs:resolution")
        resolution_var = graph.find_variable("resolution")

        for resolution in ((720, 480), (600, 400)):
            set_resolution_value.set(resolution)
            set_event_trigger.set(True)
            await ui_test.wait_n_updates(2)

            get_event_trigger.set(True)
            await ui_test.wait_n_updates(2)
            actual_resolution = resolution_var.get(context)
            self.assertEqual(actual_resolution[0], resolution[0])
            self.assertEqual(actual_resolution[1], resolution[1])

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
