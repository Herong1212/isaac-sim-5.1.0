# cSpell:disable
"""Basic tests of the OnStageEvent node"""

import omni.client
import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.graph.tools.ogn as ogn
import omni.kit.app
import omni.kit.test
import omni.usd
from pxr import Sdf


# ======================================================================
class TestOnStageEventNode(ogts.OmniGraphTestCase):
    """Tests OnStageEvent node functionality"""

    TEST_GRAPH_PATH = "/World/TestGraph"

    async def setUp(self):
        """Set up  test environment, to be torn down when done"""
        await super().setUp()
        og.Controller.edit({"graph_path": self.TEST_GRAPH_PATH, "evaluator_name": "execution"})

    async def test_backward_compatibility_v3(self):
        """Validate backward compatibility for legacy versions of OnStageEvent node."""
        # load the test scene which contains a OnStageEvent V2 node
        (result, error) = await ogts.load_test_file("TestOnStageEventNode_v2.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)

        action_graph_path = "/World/ActionGraph"
        action_graph = og.get_graph_by_path(action_graph_path)
        on_stage_event_node = action_graph.get_node(action_graph_path + "/on_stage_event")
        self.assertTrue(on_stage_event_node.is_valid())

        # The "Hierarchy Changed" event has been introduced since V3. Validate that it is
        # automatically included by the list of allowed tokens after loading V2.
        attr = on_stage_event_node.get_attribute("inputs:eventName")
        allowed_tokens = attr.get_metadata(ogn.MetadataKeys.ALLOWED_TOKENS)
        self.assertTrue(isinstance(allowed_tokens, str))
        self.assertTrue("Hierarchy Changed" in allowed_tokens.split(","))

    async def test_stage_events(self):
        """Test OnStageEvent"""
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            _,
            (on_stage_node, _, _, counter_sel_node, counter_stop_node, counter_start_node),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("OnStageEvent", "omni.graph.action.OnStageEvent"),
                    ("OnStageEvent2", "omni.graph.action.OnStageEvent"),
                    ("OnStageEvent3", "omni.graph.action.OnStageEvent"),
                    ("Counter", "omni.graph.action.Counter"),
                    ("Counter2", "omni.graph.action.Counter"),
                    ("Counter3", "omni.graph.action.Counter"),
                ],
                keys.CONNECT: [
                    ("OnStageEvent.outputs:execOut", "Counter.inputs:execIn"),
                    ("OnStageEvent2.outputs:execOut", "Counter2.inputs:execIn"),
                    ("OnStageEvent3.outputs:execOut", "Counter3.inputs:execIn"),
                ],
                keys.SET_VALUES: [
                    ("OnStageEvent.inputs:eventName", "Selection Changed"),
                    ("OnStageEvent.inputs:onlyPlayback", False),
                    ("OnStageEvent2.inputs:eventName", "Animation Stop Play"),
                    ("OnStageEvent2.inputs:onlyPlayback", True),
                    ("OnStageEvent3.inputs:eventName", "Animation Start Play"),
                    ("OnStageEvent3.inputs:onlyPlayback", True),
                ],
            },
        )

        async def _wait_for_compute():
            # There is at most a 1 frame delay between the event push and the corresponding graph execution
            await omni.kit.app.get_app().next_update_async()

        def get_start_count():
            return og.Controller.get(controller.attribute("outputs:count", counter_start_node))

        def get_stop_count():
            return og.Controller.get(controller.attribute("outputs:count", counter_stop_node))

        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(og.Controller.get(controller.attribute("outputs:count", counter_sel_node)), 0)
        self.assertEqual(get_stop_count(), 0)
        self.assertEqual(get_start_count(), 0)

        selection = omni.usd.get_context().get_selection()
        selection.set_selected_prim_paths([self.TEST_GRAPH_PATH + "/OnStageEvent"], False)
        await _wait_for_compute()
        self.assertEqual(og.Controller.get(controller.attribute("outputs:count", counter_sel_node)), 1)
        self.assertEqual(get_stop_count(), 0)
        self.assertEqual(get_start_count(), 0)

        # change the tracked event, verify selection doesn't fire
        og.Controller.set(controller.attribute("inputs:eventName", on_stage_node), "Saved")
        selection.set_selected_prim_paths([self.TEST_GRAPH_PATH + "/OnStageEvent2"], False)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(og.Controller.get(controller.attribute("outputs:count", counter_sel_node)), 1)
        await omni.kit.app.get_app().next_update_async()
        # change it back, verify it does fire when selection changes again
        og.Controller.set(controller.attribute("inputs:eventName", on_stage_node), "Selection Changed")
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(og.Controller.get(controller.attribute("outputs:count", counter_sel_node)), 1)

        selection.set_selected_prim_paths([self.TEST_GRAPH_PATH + "/OnStageEvent"], False)
        await _wait_for_compute()
        self.assertEqual(og.Controller.get(controller.attribute("outputs:count", counter_sel_node)), 2)

        # Verify that start/stop events work when only-playback is true
        timeline = omni.timeline.get_timeline_interface()

        timeline.set_start_time(1.0)
        timeline.set_end_time(10.0)
        timeline.set_target_framerate(timeline.get_time_codes_per_seconds())
        timeline.play()
        await _wait_for_compute()
        self.assertEqual(get_stop_count(), 0)
        self.assertEqual(get_start_count(), 1)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(get_stop_count(), 0)
        self.assertEqual(get_start_count(), 1)

        # Check that pausing / resuming does not trigger
        timeline.pause()
        await _wait_for_compute()
        self.assertEqual(get_stop_count(), 0)
        self.assertEqual(get_start_count(), 1)
        timeline.play()
        await _wait_for_compute()
        self.assertEqual(get_stop_count(), 0)
        self.assertEqual(get_start_count(), 1)
        timeline.stop()
        await _wait_for_compute()
        self.assertEqual(get_stop_count(), 1)
        self.assertEqual(get_start_count(), 1)
        await controller.evaluate()
        self.assertEqual(get_stop_count(), 1)
        self.assertEqual(get_start_count(), 1)

        # Verify that stopping while paused triggers the event
        timeline.play()
        await _wait_for_compute()
        self.assertEqual(get_stop_count(), 1)
        self.assertEqual(get_start_count(), 2)
        timeline.pause()
        await _wait_for_compute()
        self.assertEqual(get_stop_count(), 1)
        self.assertEqual(get_start_count(), 2)
        timeline.stop()
        await _wait_for_compute()
        self.assertEqual(get_stop_count(), 2)
        self.assertEqual(get_start_count(), 2)

    # ----------------------------------------------------------------------
    async def test_stage_hierarchy_changed_event(self):
        """Test the Hierarchy Changed event"""
        app = omni.kit.app.get_app()
        controller = og.Controller()
        keys = og.Controller.Keys
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        root_path = Sdf.Path.absoluteRootPath

        # Create Xform
        omni.kit.commands.execute("CreatePrim", prim_type="Xform")
        xform_path = root_path.AppendChild("Xform")
        xform = stage.GetPrimAtPath(xform_path)
        self.assertTrue(xform)

        # Create Material
        omni.kit.commands.execute("CreatePrim", prim_type="Material")
        material_path = root_path.AppendChild("Material")
        material = stage.GetPrimAtPath(material_path)
        self.assertTrue(material)

        # Create action graph
        (
            _,
            (on_stage_node, counter_node),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("OnStageEvent", "omni.graph.action.OnStageEvent"),
                    ("Counter", "omni.graph.action.Counter"),
                ],
                keys.CONNECT: [
                    ("OnStageEvent.outputs:execOut", "Counter.inputs:execIn"),
                ],
                keys.SET_VALUES: [
                    ("OnStageEvent.inputs:eventName", "Hierarchy Changed"),
                    ("OnStageEvent.inputs:onlyPlayback", False),
                ],
            },
        )

        outputs_count_attr = controller.attribute("outputs:count", counter_node)
        expected_hierarchy_changed_event_count = 0

        await app.next_update_async()
        self.assertEqual(og.Controller.get(outputs_count_attr), expected_hierarchy_changed_event_count)

        ###########################################################

        # Create cube
        omni.kit.commands.execute("CreatePrim", prim_type="Cube")
        cube_path = root_path.AppendChild("Cube")
        cube = stage.GetPrimAtPath(cube_path)
        self.assertTrue(cube)

        # 1 frame delay on the pop, 1 frame delay on the compute
        await app.next_update_async()
        await app.next_update_async()

        expected_hierarchy_changed_event_count += 1
        self.assertEqual(og.Controller.get(outputs_count_attr), expected_hierarchy_changed_event_count)

        ###########################################################

        # Reparent cube
        cube_path_reparented = xform_path.AppendChild("Cube")
        omni.kit.commands.execute("MovePrim", path_from=cube_path, path_to=cube_path_reparented)

        await app.next_update_async()
        await app.next_update_async()

        expected_hierarchy_changed_event_count += 1
        self.assertEqual(og.Controller.get(outputs_count_attr), expected_hierarchy_changed_event_count)

        ###########################################################

        # Rename cube to lowercase
        cube_path_lowercase = xform_path.AppendChild("cube")
        omni.kit.commands.execute("MovePrim", path_from=cube_path_reparented, path_to=cube_path_lowercase)

        await app.next_update_async()
        await app.next_update_async()

        expected_hierarchy_changed_event_count += 1
        self.assertEqual(og.Controller.get(outputs_count_attr), expected_hierarchy_changed_event_count)

        ###########################################################

        # Modify size attribute.
        cube = stage.GetPrimAtPath(cube_path_lowercase)
        self.assertTrue(cube)

        cube.GetAttribute("size").Set(1.0)

        await app.next_update_async()
        await app.next_update_async()

        # The "Hierarchy Changed" event is not expected for attribute change.
        self.assertEqual(og.Controller.get(outputs_count_attr), expected_hierarchy_changed_event_count)

        ###########################################################

        # Modify material binding.
        rel = cube.CreateRelationship("material:binding", False)
        rel.SetTargets([material_path])

        await app.next_update_async()
        await app.next_update_async()

        # The "Hierarchy Changed" event is not expected for relationship change.
        self.assertEqual(og.Controller.get(outputs_count_attr), expected_hierarchy_changed_event_count)

        ###########################################################

        # Change the tracked event
        og.Controller.set(controller.attribute("inputs:eventName", on_stage_node), "Saved")
        await og.Controller.evaluate()

        omni.kit.commands.execute("MovePrim", path_from=cube_path_lowercase, path_to=cube_path)

        await app.next_update_async()
        await app.next_update_async()

        # verify hierarchy changed event doesn't fire
        self.assertEqual(og.Controller.get(outputs_count_attr), expected_hierarchy_changed_event_count)

        ###########################################################

        # Change it back, verify it does fire when hierarchy changes again
        og.Controller.set(controller.attribute("inputs:eventName", on_stage_node), "Hierarchy Changed")
        await og.Controller.evaluate()

        # Remove cube
        omni.kit.commands.execute("DeletePrims", paths=[cube_path])

        await app.next_update_async()
        await app.next_update_async()

        expected_hierarchy_changed_event_count += 1
        self.assertEqual(og.Controller.get(outputs_count_attr), expected_hierarchy_changed_event_count)
