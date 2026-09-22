# noqa: too-many-lines
# pylint: disable=too-many-nested-blocks

# cSpell:disable
"""Action Graph Node Tests, Part 2"""

import random
from contextlib import suppress
from functools import partial
from typing import List

import carb
import carb.input
import numpy as np
import omni.client
import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.graph.tools.ogn as ogn
import omni.kit.app
import omni.kit.test

# These are only used by the 'with_window' tests.
with suppress(ModuleNotFoundError):
    import omni.kit.ui_test as ui_test
    import omni.usd

from carb.input import GamepadInput, KeyboardEventType, KeyboardInput
from omni.graph.core import ThreadsafetyTestUtils

# These are only used by the 'with_window' tests.
with suppress(ModuleNotFoundError):
    from omni.kit.test_suite.helpers import select_prims

from pxr import Sdf


# ======================================================================
class TestActionGraphNodes(ogts.OmniGraphTestCase):
    """Tests action graph node functionality"""

    TEST_GRAPH_PATH = "/World/TestGraph"
    keys = og.Controller.Keys
    E = og.ExecutionAttributeState.ENABLED
    D = og.ExecutionAttributeState.DISABLED

    async def setUp(self):
        """Set up  test environment, to be torn down when done"""
        await super().setUp()

    # ----------------------------------------------------------------------
    @ThreadsafetyTestUtils.make_threading_test
    def test_ongamepadinput_node(self, test_instance_id: int = 0):
        """Test OnGamepadInput node"""
        # Obtain an interface to a few gamepads and carb input provider.
        input_provider = ThreadsafetyTestUtils.add_to_threading_cache(
            test_instance_id, carb.input.acquire_input_provider()
        )
        gamepad_list = ThreadsafetyTestUtils.add_to_threading_cache(
            test_instance_id,
            [
                input_provider.create_gamepad("Gamepad 0", "0"),
                input_provider.create_gamepad("Gamepad 1", "1"),
                input_provider.create_gamepad("Gamepad 2", "2"),
            ],
        )

        # Connect the gamepads.
        for gamepad in gamepad_list:
            self.assertIsNotNone(gamepad)
            ThreadsafetyTestUtils.single_evaluation_first_test_instance(
                test_instance_id, partial(input_provider.set_gamepad_connected, gamepad, True)
            )
            yield ThreadsafetyTestUtils.EVALUATION_WAIT_FRAME  # Yielding to compute by waiting for the next app frame.

        # Instance a test graph setup. Note that we append the graph path with the test_instance_id
        # so that the graph can be uniquely identified in the thread-safety test!
        graph_path = self.TEST_GRAPH_PATH + str(test_instance_id)
        og.Controller.create_graph({"graph_path": graph_path, "evaluator_name": "execution"})
        (_, (on_gamepad_input_node,), _, _) = og.Controller.edit(
            graph_path, {self.keys.CREATE_NODES: ("OnGamepadInput", "omni.graph.action.OnGamepadInput")}
        )

        # Obtain necessary attributes.
        in_onlyplayback_attr = on_gamepad_input_node.get_attribute("inputs:onlyPlayback")
        in_gamepadid_attr = on_gamepad_input_node.get_attribute("inputs:gamepadId")
        in_gamepad_element_attr = on_gamepad_input_node.get_attribute("inputs:gamepadElementIn")
        out_pressed_attr = on_gamepad_input_node.get_attribute("outputs:pressed")
        out_released_attr = on_gamepad_input_node.get_attribute("outputs:released")
        out_ispressed_attr = on_gamepad_input_node.get_attribute("outputs:isPressed")

        # Define a list of all possible gamepad inputs.
        # FIXME: Note that the commented-out gamepad inputs produce errors in the OnGamepadInput's
        # compute method because those specific inputs are not being considered. Maybe change to
        # include these inputs and/or not spit out scary-looking error messages to users?
        possible_gamepad_inputs = ThreadsafetyTestUtils.add_to_threading_cache(
            test_instance_id,
            [
                GamepadInput.A,
                GamepadInput.B,
                # GamepadInput.COUNT,
                GamepadInput.DPAD_DOWN,
                GamepadInput.DPAD_LEFT,
                GamepadInput.DPAD_RIGHT,
                GamepadInput.DPAD_UP,
                GamepadInput.LEFT_SHOULDER,
                GamepadInput.LEFT_STICK,
                # GamepadInput.LEFT_STICK_DOWN,
                # GamepadInput.LEFT_STICK_LEFT,
                # GamepadInput.LEFT_STICK_RIGHT,
                # GamepadInput.LEFT_STICK_UP,
                # GamepadInput.LEFT_TRIGGER,
                GamepadInput.MENU1,
                GamepadInput.MENU2,
                GamepadInput.RIGHT_SHOULDER,
                GamepadInput.RIGHT_STICK,
                # GamepadInput.RIGHT_STICK_DOWN,
                # GamepadInput.RIGHT_STICK_LEFT,
                # GamepadInput.RIGHT_STICK_RIGHT,
                # GamepadInput.RIGHT_STICK_UP,
                # GamepadInput.RIGHT_TRIGGER,
                GamepadInput.X,
                GamepadInput.Y,
            ],
        )

        # Define a dict of all valid inputs:gamepadElementIn tokens, along with
        # their corresponding gamepad input. NOTE: The node's allowed token names
        # are a bit different from the carb.input.GamepadInput values, might make
        # sense to have them be the same?
        allowed_gamepad_element_tokens = ThreadsafetyTestUtils.add_to_threading_cache(
            test_instance_id,
            {
                "Face Button Bottom": GamepadInput.A,
                "Face Button Right": GamepadInput.B,
                "Face Button Left": GamepadInput.X,
                "Face Button Top": GamepadInput.Y,
                "Left Shoulder": GamepadInput.LEFT_SHOULDER,
                "Right Shoulder": GamepadInput.RIGHT_SHOULDER,
                "Special Left": GamepadInput.MENU1,
                "Special Right": GamepadInput.MENU2,
                "Left Stick Button": GamepadInput.LEFT_STICK,
                "Right Stick Button": GamepadInput.RIGHT_STICK,
                "D-Pad Up": GamepadInput.DPAD_UP,
                "D-Pad Right": GamepadInput.DPAD_RIGHT,
                "D-Pad Down": GamepadInput.DPAD_DOWN,
                "D-Pad Left": GamepadInput.DPAD_LEFT,
            },
        )

        # Wrap main driver code in the following generator (in order to leverage
        # the ThreadsafetyTestUtils.make_threading_test decorator). Note that for simplicity's sake the
        # fake gamepad IDs correspond directly with their index in the gamepad_list.
        def _test_ongamepadinput_node(quick_run: bool = True, num_inputs_to_test: int = 5):
            _possible_gamepad_inputs = []
            _allowed_gamepad_element_tokens = {}

            # Codepath for accelerated test (won't take as long and still provide some code coverage).
            if quick_run:
                # Make sure that the input flags make sense.
                if num_inputs_to_test < 1:
                    num_inputs_to_test = 1
                elif num_inputs_to_test > 14:
                    num_inputs_to_test = 14

                # Define two sets of random indices that'll determine the combination of inputs:gamepadElementIn
                # tokens and emulated key inputs that we'll test for the current function call. Note that the
                # inputs:gamepadElementIn tokens we choose and the emulated keys need not coincide, resulting
                # in no output being generated by the OnGamepadInput node. Also note that because we want to
                # use the same set of random indices in each test instance (so that all test graph instances
                # run their tests/comparisons using the same combination of buttons/inputs), we add said indices
                # (or more specifically an internal method that's used to create those indices, so that they're
                # only created once for all test instances) to the overall threading cache.
                def create_random_indices():
                    rand_indices_0 = set()
                    while len(rand_indices_0) < num_inputs_to_test:
                        rand_indices_0.add(random.randrange(len(possible_gamepad_inputs)))
                    rand_indices_1 = set()
                    while len(rand_indices_1) < num_inputs_to_test:
                        rand_indices_1.add(random.randrange(len(allowed_gamepad_element_tokens)))
                    return rand_indices_0, rand_indices_1

                rand_indices_0, rand_indices_1 = ThreadsafetyTestUtils.add_to_threading_cache(
                    test_instance_id, create_random_indices()
                )

                # Convert the sets into lists so that their elements can be accessible by index.
                rand_indices_0 = list(rand_indices_0)
                rand_indices_1 = list(rand_indices_1)

                # Create an abbreviated list of possible gamepad input elements.
                for r_i in rand_indices_0:
                    _possible_gamepad_inputs.append(possible_gamepad_inputs[r_i])

                # Create an abbreviated dict of allowed token-key input pairs.
                temp_keys_list = list(allowed_gamepad_element_tokens)
                temp_values_list = list(allowed_gamepad_element_tokens.values())
                for r_i in rand_indices_1:
                    _allowed_gamepad_element_tokens[temp_keys_list[r_i]] = temp_values_list[r_i]
            # Codepath for full test.
            else:
                _possible_gamepad_inputs = possible_gamepad_inputs
                _allowed_gamepad_element_tokens = allowed_gamepad_element_tokens

            # Set the gamepad id on each OnGamepadInput node. Note that multiple gamepad nodes are set to
            # track the same gamepad to look for potential concurrency issues.
            # for on_gamepad_input_node in on_gamepad_input_nodes:
            in_gamepadid_attr.set(test_instance_id % len(gamepad_list))  # noqa S001

            # Loop through each allowed gamepad element token, and set it on the OnGamepadInput nodes'
            # corresponding input attributes.
            for allowed_token, allowed_input in _allowed_gamepad_element_tokens.items():
                in_gamepad_element_attr.set(allowed_token)
                # Loop through each possible gamepad input, which we will emulate.
                for emulated_input in _possible_gamepad_inputs:
                    # Loop through each possible input event type (0 == key is released, 1 == key is pressed)
                    for event_type in [1, 0]:
                        # Trigger each gamepad input.
                        input_provider.buffer_gamepad_event(
                            gamepad_list[test_instance_id % len(gamepad_list)], emulated_input, event_type  # noqa S001
                        )
                        yield ThreadsafetyTestUtils.EVALUATION_WAIT_FRAME  # Yielding to compute by waiting for the next app frame.
                        # If the current emulated input matches the inputs:gamepadElementsIn attribute setting,
                        # check that the nodes reacted appropriately. Otherwise check that the nodes did not
                        # register the input.
                        try:
                            if emulated_input == allowed_input:
                                if event_type == 1:
                                    self.assertEqual(out_pressed_attr.get(), self.E)
                                    self.assertEqual(out_released_attr.get(), self.D)
                                    self.assertTrue(out_ispressed_attr.get())
                                elif event_type == 0:
                                    self.assertEqual(out_pressed_attr.get(), self.D)
                                    self.assertEqual(out_released_attr.get(), self.E)
                                    self.assertFalse(out_ispressed_attr.get())
                            else:
                                self.assertEqual(out_pressed_attr.get(), self.D)
                                self.assertEqual(out_released_attr.get(), self.D)
                                self.assertFalse(out_ispressed_attr.get())
                        except AssertionError as e:
                            raise AssertionError(f"When testing {allowed_token}") from e

        # Test that the OnGamepadInput nodes works correctly when the onlyPlayback input is disabled.
        in_onlyplayback_attr.set(False)
        for _ in _test_ongamepadinput_node():
            yield ThreadsafetyTestUtils.EVALUATION_WAIT_FRAME  # Yielding to compute by waiting for the next app frame.

        # Test that the OnGamepadInput nodes works correctly when the onlyPlayback input is enabled.
        in_onlyplayback_attr.set(True)
        timeline = omni.timeline.get_timeline_interface()
        timeline.set_target_framerate(timeline.get_time_codes_per_seconds())
        timeline.play()
        for _ in _test_ongamepadinput_node():
            yield ThreadsafetyTestUtils.EVALUATION_WAIT_FRAME  # Yielding to compute by waiting for the next app frame.
        timeline.stop()

        # Delete the gamepad node before destroying the gamepads themselves so that the nodes don't throw
        # any warnings about having invalid gamepadIds.
        og.Controller.delete_node(on_gamepad_input_node)

        # Disconnect and destroy the gamepads.
        for gamepad in gamepad_list:
            ThreadsafetyTestUtils.single_evaluation_last_test_instance(
                test_instance_id, partial(input_provider.set_gamepad_connected, gamepad, False)
            )
            yield ThreadsafetyTestUtils.EVALUATION_WAIT_FRAME  # Yielding to compute by waiting for the next app frame.
            ThreadsafetyTestUtils.single_evaluation_last_test_instance(
                test_instance_id, partial(input_provider.destroy_gamepad, gamepad)
            )
            yield ThreadsafetyTestUtils.EVALUATION_WAIT_FRAME  # Yielding to compute by waiting for the next app frame.

    # ----------------------------------------------------------------------
    # The OnImpulseEvent node ALSO has a built-in test construct in its .ogn file located
    # at ../../nodes/OgnOnImpulseEvent.ogn (relative to the source location of the currently-
    # opened testing script).
    @ThreadsafetyTestUtils.make_threading_test
    def test_onimpulseevent_node(self, test_instance_id: int = 0):
        """Test OnImpulseEvent node"""

        # Instance a test graph setup. Note that we append the graph path with the test_instance_id
        # so that the graph can be uniquely identified in the thread-safety test!
        graph_path = self.TEST_GRAPH_PATH + str(test_instance_id)
        og.Controller.create_graph({"graph_path": graph_path, "evaluator_name": "execution"})
        (
            _,
            (_, counter_node),
            _,
            _,
        ) = og.Controller.edit(
            graph_path,
            {
                self.keys.CREATE_NODES: [
                    ("OnImpulse", "omni.graph.action.OnImpulseEvent"),
                    ("Counter", "omni.graph.action.Counter"),
                ],
                self.keys.SET_VALUES: [("OnImpulse.inputs:onlyPlayback", False)],
                self.keys.CONNECT: (
                    "OnImpulse.outputs:execOut",
                    "Counter.inputs:execIn",
                ),
            },
        )
        counter_controller = og.Controller(og.Controller.attribute("outputs:count", counter_node))

        # After several updates, there should have been no compute calls.
        yield  # Yielding to wait for compute to happen across all graph instances before continuing the test.
        yield  # Yielding to wait for compute to happen across all graph instances before continuing the test.
        yield  # Yielding to wait for compute to happen across all graph instances before continuing the test.
        self.assertEqual(counter_controller.get(), 0)

        # Change the OnImpulse node's state attribute. The node should now request compute.
        og.Controller.edit(graph_path, {self.keys.SET_VALUES: (graph_path + "/OnImpulse.state:enableImpulse", True)})
        yield  # Yielding to wait for compute to happen across all graph instances before continuing the test.
        self.assertEqual(counter_controller.get(), 1)

        # More updates should not result in more computes.
        yield  # Yielding to wait for compute to happen across all graph instances before continuing the test.
        yield  # Yielding to wait for compute to happen across all graph instances before continuing the test.
        yield  # Yielding to wait for compute to happen across all graph instances before continuing the test.
        self.assertEqual(counter_controller.get(), 1)

    # ----------------------------------------------------------------------
    async def test_onimpulseevent_node_ui(self):
        """Test OnImpulseEvent node's UI"""
        og.Controller.create_graph({"graph_path": self.TEST_GRAPH_PATH, "evaluator_name": "execution"})
        (
            _,
            (on_impulse_node, counter_node),
            _,
            _,
        ) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                self.keys.CREATE_NODES: [
                    ("OnImpulse", "omni.graph.action.OnImpulseEvent"),
                    ("Counter", "omni.graph.action.Counter"),
                ],
                self.keys.SET_VALUES: [("OnImpulse.inputs:onlyPlayback", False)],
                self.keys.CONNECT: (
                    "OnImpulse.outputs:execOut",
                    "Counter.inputs:execIn",
                ),
            },
        )
        counter_controller = og.Controller(og.Controller.attribute("outputs:count", counter_node))

        # Select the OnImpulseEvent node and give the UI some time to update.
        await select_prims([on_impulse_node.get_prim_path()])
        await ui_test.wait_n_updates(5)

        # Counter should be zero.
        self.assertEqual(counter_controller.get(), 0)

        # Find the 'Send Impulse' button.
        button_ref = ui_test.find(
            "Property//Frame/**/CollapsableFrame/**/CollapsableFrame/**/Button[*].text=='Send Impulse'"
        )
        self.assertIsNotNone(button_ref, "Could not find 'Send Impulse' button.")

        # Click it, let the graph evaluate, then check the counter.
        await button_ref.click()
        await ui_test.wait_n_updates(2)
        self.assertEqual(counter_controller.get(), 1)

        # Wait a bit longer. The counter shouldn't change.
        await ui_test.wait_n_updates(10)
        self.assertEqual(counter_controller.get(), 1)

        # Click it again. The counter should increment.
        await button_ref.click()
        await ui_test.wait_n_updates(2)
        self.assertEqual(counter_controller.get(), 2)

    # ----------------------------------------------------------------------
    async def test_onkeyboardinput_node(self):
        """Test OnKeyboardInput node"""
        app = omni.kit.app.get_app()

        og.Controller.create_graph({"graph_path": self.TEST_GRAPH_PATH, "evaluator_name": "execution"})
        (_, (on_keyboard_input_node,), _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {self.keys.CREATE_NODES: ("OnKeyboardInput", "omni.graph.action.OnKeyboardInput")},
        )

        # Obtain necessary attributes.
        in_keyin_attr = on_keyboard_input_node.get_attribute("inputs:keyIn")
        in_playbackonly_attr = on_keyboard_input_node.get_attribute("inputs:onlyPlayback")
        out_keyout_attr = on_keyboard_input_node.get_attribute("outputs:keyOut")
        out_pressed_attr = on_keyboard_input_node.get_attribute("outputs:pressed")
        out_released_attr = on_keyboard_input_node.get_attribute("outputs:released")
        out_ispressed_attr = on_keyboard_input_node.get_attribute("outputs:isPressed")

        # Obtain an interface to the keyboard and carb input provider.
        keyboard = omni.appwindow.get_default_app_window().get_keyboard()
        input_provider = carb.input.acquire_input_provider()
        self.assertIsNotNone(keyboard)

        # Define a list of all possible carb.input.KeyboardInput inputs. Note that not all possible
        # keys are necessarily detectable by the OnKeyboardInput node (this list also includes the
        # UNKNOWN key).
        possible_key_inputs = [
            KeyboardInput.A,
            KeyboardInput.APOSTROPHE,
            KeyboardInput.B,
            KeyboardInput.BACKSLASH,
            KeyboardInput.BACKSPACE,
            KeyboardInput.C,
            KeyboardInput.CAPS_LOCK,
            KeyboardInput.COMMA,
            KeyboardInput.D,
            KeyboardInput.DEL,
            KeyboardInput.DOWN,
            KeyboardInput.E,
            KeyboardInput.END,
            KeyboardInput.ENTER,
            KeyboardInput.EQUAL,
            KeyboardInput.ESCAPE,
            KeyboardInput.F,
            KeyboardInput.F1,
            KeyboardInput.F10,
            KeyboardInput.F11,
            KeyboardInput.F12,
            KeyboardInput.F2,
            KeyboardInput.F3,
            KeyboardInput.F4,
            KeyboardInput.F5,
            KeyboardInput.F6,
            KeyboardInput.F7,
            KeyboardInput.F8,
            KeyboardInput.F9,
            KeyboardInput.G,
            KeyboardInput.GRAVE_ACCENT,
            KeyboardInput.H,
            KeyboardInput.HOME,
            KeyboardInput.I,
            KeyboardInput.INSERT,
            KeyboardInput.J,
            KeyboardInput.K,
            KeyboardInput.KEY_0,
            KeyboardInput.KEY_1,
            KeyboardInput.KEY_2,
            KeyboardInput.KEY_3,
            KeyboardInput.KEY_4,
            KeyboardInput.KEY_5,
            KeyboardInput.KEY_6,
            KeyboardInput.KEY_7,
            KeyboardInput.KEY_8,
            KeyboardInput.KEY_9,
            KeyboardInput.L,
            KeyboardInput.LEFT,
            KeyboardInput.LEFT_ALT,
            KeyboardInput.LEFT_BRACKET,
            KeyboardInput.LEFT_CONTROL,
            KeyboardInput.LEFT_SHIFT,
            KeyboardInput.LEFT_SUPER,
            KeyboardInput.M,
            KeyboardInput.MENU,
            KeyboardInput.MINUS,
            KeyboardInput.N,
            KeyboardInput.NUMPAD_0,
            KeyboardInput.NUMPAD_1,
            KeyboardInput.NUMPAD_2,
            KeyboardInput.NUMPAD_3,
            KeyboardInput.NUMPAD_4,
            KeyboardInput.NUMPAD_5,
            KeyboardInput.NUMPAD_6,
            KeyboardInput.NUMPAD_7,
            KeyboardInput.NUMPAD_8,
            KeyboardInput.NUMPAD_9,
            KeyboardInput.NUMPAD_ADD,
            KeyboardInput.NUMPAD_DEL,
            KeyboardInput.NUMPAD_DIVIDE,
            KeyboardInput.NUMPAD_ENTER,
            KeyboardInput.NUMPAD_EQUAL,
            KeyboardInput.NUMPAD_MULTIPLY,
            KeyboardInput.NUMPAD_SUBTRACT,
            KeyboardInput.NUM_LOCK,
            KeyboardInput.O,
            KeyboardInput.P,
            KeyboardInput.PAGE_DOWN,
            KeyboardInput.PAGE_UP,
            KeyboardInput.PAUSE,
            KeyboardInput.PERIOD,
            KeyboardInput.PRINT_SCREEN,
            KeyboardInput.Q,
            KeyboardInput.R,
            KeyboardInput.RIGHT,
            KeyboardInput.RIGHT_ALT,
            KeyboardInput.RIGHT_BRACKET,
            KeyboardInput.RIGHT_CONTROL,
            KeyboardInput.RIGHT_SHIFT,
            KeyboardInput.RIGHT_SUPER,
            KeyboardInput.S,
            KeyboardInput.SCROLL_LOCK,
            KeyboardInput.SEMICOLON,
            KeyboardInput.SLASH,
            KeyboardInput.SPACE,
            KeyboardInput.T,
            # KeyboardInput.TAB, -- This causes problems in the test
            KeyboardInput.U,
            KeyboardInput.UNKNOWN,
            KeyboardInput.UP,
            KeyboardInput.V,
            KeyboardInput.W,
            KeyboardInput.X,
            KeyboardInput.Y,
            KeyboardInput.Z,
        ]

        # Define a dictionary of token keys representing the possible inputs to the OnKeyboardInput node's
        # "keyIn" attribute, and values representing the corresponding carb.input.KeyboardInput. Note that
        # not all possible keys are necessarily allowed for detection by the OnKeyboardInput node (e.g.
        # "Unknown")
        allowed_token_key_inputs = {
            "A": KeyboardInput.A,
            "B": KeyboardInput.B,
            "C": KeyboardInput.C,
            "D": KeyboardInput.D,
            "E": KeyboardInput.E,
            "F": KeyboardInput.F,
            "G": KeyboardInput.G,
            "H": KeyboardInput.H,
            "I": KeyboardInput.I,
            "J": KeyboardInput.J,
            "K": KeyboardInput.K,
            "L": KeyboardInput.L,
            "M": KeyboardInput.M,
            "N": KeyboardInput.N,
            "O": KeyboardInput.O,
            "P": KeyboardInput.P,
            "Q": KeyboardInput.Q,
            "R": KeyboardInput.R,
            "S": KeyboardInput.S,
            "T": KeyboardInput.T,
            "U": KeyboardInput.U,
            "V": KeyboardInput.V,
            "W": KeyboardInput.W,
            "X": KeyboardInput.X,
            "Y": KeyboardInput.Y,
            "Z": KeyboardInput.Z,
            "Apostrophe": KeyboardInput.APOSTROPHE,
            "Backslash": KeyboardInput.BACKSLASH,
            "Backspace": KeyboardInput.BACKSPACE,
            "CapsLock": KeyboardInput.CAPS_LOCK,
            "Comma": KeyboardInput.COMMA,
            "Del": KeyboardInput.DEL,
            "Down": KeyboardInput.DOWN,
            "End": KeyboardInput.END,
            "Enter": KeyboardInput.ENTER,
            "Equal": KeyboardInput.EQUAL,
            "Escape": KeyboardInput.ESCAPE,
            "F1": KeyboardInput.F1,
            "F10": KeyboardInput.F10,
            "F11": KeyboardInput.F11,
            "F12": KeyboardInput.F12,
            "F2": KeyboardInput.F2,
            "F3": KeyboardInput.F3,
            "F4": KeyboardInput.F4,
            "F5": KeyboardInput.F5,
            "F6": KeyboardInput.F6,
            "F7": KeyboardInput.F7,
            "F8": KeyboardInput.F8,
            "F9": KeyboardInput.F9,
            "GraveAccent": KeyboardInput.GRAVE_ACCENT,
            "Home": KeyboardInput.HOME,
            "Insert": KeyboardInput.INSERT,
            "Key0": KeyboardInput.KEY_0,
            "Key1": KeyboardInput.KEY_1,
            "Key2": KeyboardInput.KEY_2,
            "Key3": KeyboardInput.KEY_3,
            "Key4": KeyboardInput.KEY_4,
            "Key5": KeyboardInput.KEY_5,
            "Key6": KeyboardInput.KEY_6,
            "Key7": KeyboardInput.KEY_7,
            "Key8": KeyboardInput.KEY_8,
            "Key9": KeyboardInput.KEY_9,
            "Left": KeyboardInput.LEFT,
            "LeftAlt": KeyboardInput.LEFT_ALT,
            "LeftBracket": KeyboardInput.LEFT_BRACKET,
            "LeftControl": KeyboardInput.LEFT_CONTROL,
            "LeftShift": KeyboardInput.LEFT_SHIFT,
            "LeftSuper": KeyboardInput.LEFT_SUPER,
            "Menu": KeyboardInput.MENU,
            "Minus": KeyboardInput.MINUS,
            "NumLock": KeyboardInput.NUM_LOCK,
            "Numpad0": KeyboardInput.NUMPAD_0,
            "Numpad1": KeyboardInput.NUMPAD_1,
            "Numpad2": KeyboardInput.NUMPAD_2,
            "Numpad3": KeyboardInput.NUMPAD_3,
            "Numpad4": KeyboardInput.NUMPAD_4,
            "Numpad5": KeyboardInput.NUMPAD_5,
            "Numpad6": KeyboardInput.NUMPAD_6,
            "Numpad7": KeyboardInput.NUMPAD_7,
            "Numpad8": KeyboardInput.NUMPAD_8,
            "Numpad9": KeyboardInput.NUMPAD_9,
            "NumpadAdd": KeyboardInput.NUMPAD_ADD,
            "NumpadDel": KeyboardInput.NUMPAD_DEL,
            "NumpadDivide": KeyboardInput.NUMPAD_DIVIDE,
            "NumpadEnter": KeyboardInput.NUMPAD_ENTER,
            "NumpadEqual": KeyboardInput.NUMPAD_EQUAL,
            "NumpadMultiply": KeyboardInput.NUMPAD_MULTIPLY,
            "NumpadSubtract": KeyboardInput.NUMPAD_SUBTRACT,
            "PageDown": KeyboardInput.PAGE_DOWN,
            "PageUp": KeyboardInput.PAGE_UP,
            "Pause": KeyboardInput.PAUSE,
            "Period": KeyboardInput.PERIOD,
            "PrintScreen": KeyboardInput.PRINT_SCREEN,
            "Right": KeyboardInput.RIGHT,
            "RightAlt": KeyboardInput.RIGHT_ALT,
            "RightBracket": KeyboardInput.RIGHT_BRACKET,
            "RightControl": KeyboardInput.RIGHT_CONTROL,
            "RightShift": KeyboardInput.RIGHT_SHIFT,
            "RightSuper": KeyboardInput.RIGHT_SUPER,
            "ScrollLock": KeyboardInput.SCROLL_LOCK,
            "Semicolon": KeyboardInput.SEMICOLON,
            "Slash": KeyboardInput.SLASH,
            "Space": KeyboardInput.SPACE,
            # "Tab": KeyboardInput.TAB, -- this causes problems in the test
            "Up": KeyboardInput.UP,
        }

        # Define a list of all possible keyboard event types (for convenience).
        # We won't consider KEY_REPEAT and CHAR events here.
        keyboard_event_types = [
            KeyboardEventType.KEY_PRESS,
            KeyboardEventType.KEY_RELEASE,
        ]

        # Create a list of all possible keyboard modifier combinations. Don't need permutations
        # since bitwise OR operator is commutative and associative.
        modifier_combinations = [
            0,  # 0
            carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT,  # 1
            carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL,  # 2
            carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT | carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL,  # 3
            carb.input.KEYBOARD_MODIFIER_FLAG_ALT,  # 4
            carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT | carb.input.KEYBOARD_MODIFIER_FLAG_ALT,  # 5
            carb.input.KEYBOARD_MODIFIER_FLAG_ALT | carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL,  # 6
            carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT
            | carb.input.KEYBOARD_MODIFIER_FLAG_ALT
            | carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL,  # 7
        ]

        # Create a list of tuples of lists of tuples and indices of all possible input key modifier
        # settings on the OnKeyboardInput node.
        node_input_modifier_attribute_combinations = [
            ([("inputs:shiftIn", False), ("inputs:altIn", False), ("inputs:ctrlIn", False)], 0),
            ([("inputs:shiftIn", True), ("inputs:altIn", False), ("inputs:ctrlIn", False)], 1),
            ([("inputs:shiftIn", False), ("inputs:altIn", False), ("inputs:ctrlIn", True)], 2),
            ([("inputs:shiftIn", True), ("inputs:altIn", False), ("inputs:ctrlIn", True)], 3),
            ([("inputs:shiftIn", False), ("inputs:altIn", True), ("inputs:ctrlIn", False)], 4),
            ([("inputs:shiftIn", True), ("inputs:altIn", True), ("inputs:ctrlIn", False)], 5),
            ([("inputs:shiftIn", False), ("inputs:altIn", True), ("inputs:ctrlIn", True)], 6),
            ([("inputs:shiftIn", True), ("inputs:altIn", True), ("inputs:ctrlIn", True)], 7),
        ]

        # NOTE: Although the below test confirms that the OnKeyboardInput node works for all
        # input combinations, it takes a while to run and times out the test (which is typically
        # set to automatically crash after 300s). To account for this, each time we run the test
        # a random subset of allowed input tokens and input keys are chosen with which
        # we perform the test; this cuts down on computation time and still provides some
        # decent code coverage.

        # Wrap main test driver code in the following method. Note that in addition to testing
        # whether specific buttons activate their corresponding code path, we also check that
        # no other buttons can activate code paths they don't belong to. Check for all possible
        # key + special modifier press/release permutations.
        async def _test_onkeyboardinput_node(
            quick_run: bool = True, num_keys_to_test: int = 10, num_modifiers_to_test: int = 1
        ):
            _possible_key_inputs = []
            _allowed_token_key_inputs = {}
            _modifier_combinations = []
            _node_input_modifier_attribute_combinations = []

            # Codepath for accelerated test (won't time out and still provide some code coverage).
            if quick_run:
                # Make sure that the input flags make sense.
                if num_keys_to_test < 1:
                    num_keys_to_test = 1
                elif num_keys_to_test > 105:
                    num_keys_to_test = 105
                if num_modifiers_to_test < 1:
                    num_modifiers_to_test = 1
                elif num_modifiers_to_test > 8:
                    num_modifiers_to_test = 8

                # Define three sets of random indices that'll determine the combination of inputs:keyIn
                # tokens, emulated key inputs, and modifier values that we'll test for the current function call.
                # Note that the inputs:keyIn tokens we choose and the emulated keys need not coincide, resulting
                # in no output being generated by the OnKeyboardInput node.
                rand_indices_0 = set()
                while len(rand_indices_0) < num_keys_to_test:
                    rand_indices_0.add(random.randrange(len(possible_key_inputs)))
                rand_indices_1 = set()
                while len(rand_indices_1) < num_keys_to_test:
                    rand_indices_1.add(random.randrange(len(allowed_token_key_inputs)))
                rand_indices_2 = set()
                while len(rand_indices_2) < num_modifiers_to_test:
                    rand_indices_2.add(random.randrange(len(modifier_combinations)))

                # Convert the sets into lists so that their elements can be accessible by index.
                rand_indices_0 = list(rand_indices_0)
                rand_indices_1 = list(rand_indices_1)
                rand_indices_2 = list(rand_indices_2)

                # Create an abbreviated list of possible key inputs.
                for i in range(0, num_keys_to_test):
                    _possible_key_inputs.append(possible_key_inputs[rand_indices_0[i]])

                # Create an abbreviated dict of allowed token-key input pairs.
                temp_keys_list = list(allowed_token_key_inputs)
                temp_values_list = list(allowed_token_key_inputs.values())
                for i in range(0, num_keys_to_test):
                    _allowed_token_key_inputs[temp_keys_list[rand_indices_1[i]]] = temp_values_list[rand_indices_1[i]]

                # Create abbreviated lists of modifier values and corresponing input attribute-value pairs.
                for rand_idx in rand_indices_2:
                    _modifier_combinations.append(modifier_combinations[rand_idx])
                    _node_input_modifier_attribute_combinations.append(
                        node_input_modifier_attribute_combinations[rand_idx]
                    )
            # Codepath for full test.
            else:
                _possible_key_inputs = possible_key_inputs
                _allowed_token_key_inputs = allowed_token_key_inputs
                _modifier_combinations = modifier_combinations
                _node_input_modifier_attribute_combinations = node_input_modifier_attribute_combinations

            # Loop through each possible inputs:keyIn token, and the set the inputs:keyIn attribute on the
            # OnKeyboardInput node.
            for token, _ in _allowed_token_key_inputs.items():  # noqa PLR1702
                in_keyin_attr.set(token)
                # Loop through each possible modification combination, and set the corresponding input attributes
                # on the OnKeyboardInput node. Also store an index to represent the current modification state.
                for node_input_modifier_attribute_tuple in _node_input_modifier_attribute_combinations:
                    node_input_modifier_attribute_list_in_tuple = node_input_modifier_attribute_tuple[0]
                    for input_attr_value_modifier_pair in node_input_modifier_attribute_list_in_tuple:
                        og.Controller.set(
                            og.Controller.attribute(input_attr_value_modifier_pair[0], on_keyboard_input_node),
                            input_attr_value_modifier_pair[1],
                        )
                    # Loop through each possible input key.
                    for key in _possible_key_inputs:
                        # Loop through all possible modification combinations.
                        for modifier in _modifier_combinations:
                            # Loop through each possible keyboard event type.
                            for event_type in keyboard_event_types:
                                # Trigger the current keyboard event.
                                input_provider.buffer_keyboard_key_event(keyboard, event_type, key, modifier)
                                # Occasionally it may take more than one update_async calls for the key event to
                                # be pushed, so wait twice
                                await app.next_update_async()
                                await app.next_update_async()
                                # If the currently-pressed key matches the currently-set inputs:keyIn token's
                                # corresponding KeyboardInput + modifiers, check that the OnKeyboardInput node gets
                                # correctly activated.
                                try:
                                    if (
                                        _allowed_token_key_inputs[token] == key  # noqa PLR1733
                                        and node_input_modifier_attribute_tuple[1] == modifier
                                    ):
                                        # If the key has been pressed, check for the corresponding expected conditions.
                                        if event_type == KeyboardEventType.KEY_PRESS:
                                            self.assertEqual(out_keyout_attr.get(), token)
                                            self.assertEqual(out_pressed_attr.get(), self.E)
                                            self.assertEqual(out_released_attr.get(), self.D)
                                            self.assertTrue(out_ispressed_attr.get())
                                        # If the key has been released, check for the corresponding expected conditions.
                                        elif event_type == KeyboardEventType.KEY_RELEASE:
                                            self.assertEqual(out_keyout_attr.get(), token)
                                            self.assertEqual(out_pressed_attr.get(), self.D)
                                            self.assertEqual(out_released_attr.get(), self.E)
                                            self.assertFalse(out_ispressed_attr.get())
                                    else:
                                        self.assertEqual(out_pressed_attr.get(), self.D)
                                        self.assertEqual(out_released_attr.get(), self.D)
                                        self.assertFalse(out_ispressed_attr.get())
                                except AssertionError as e:
                                    raise AssertionError(f"When testing {(key, modifier, event_type)}") from e

        # Test that the OnKeyboardInput node works correctly when its onlyPlayback input is disabled.
        in_playbackonly_attr.set(False)
        await _test_onkeyboardinput_node()

        # Test that the OnKeyboardInput node works correctly when its onlyPlayback input is enabled.
        in_playbackonly_attr.set(True)
        timeline = omni.timeline.get_timeline_interface()
        timeline.set_target_framerate(timeline.get_time_codes_per_seconds())
        timeline.play()
        await _test_onkeyboardinput_node()
        timeline.stop()

    # ----------------------------------------------------------------------
    # NOTE: Even though the OnLoaded node is threadsafe (its compute method is very simple),
    # we don't adapt the below test to check for thread-safety conditions because it relies
    # on other nodes (omni.graph.action.SendCustomEvent) which are NOT threadsafe.
    async def test_onloaded_node(self):
        """Test OnLoaded node"""

        def registered_event_name(event_name):
            """Returns the internal name used for the given custom event name"""
            name = "omni.graph.action." + event_name
            return carb.events.type_from_string(name)

        events = []

        def on_event(event):
            events.append(event.payload["!path"])

        reg_event_name = registered_event_name("foo")
        message_bus = omni.kit.app.get_app().get_message_bus_event_stream()
        sub = message_bus.create_subscription_to_push_by_type(reg_event_name, on_event)
        self.assertIsNotNone(sub)

        og.Controller.create_graph({"graph_path": self.TEST_GRAPH_PATH, "evaluator_name": "execution"})
        og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                self.keys.CREATE_NODES: [
                    ("OnTick", "omni.graph.action.OnTick"),
                    ("OnLoaded", "omni.graph.action.OnLoaded"),
                    ("Send1", "omni.graph.action.SendCustomEvent"),
                    ("Send2", "omni.graph.action.SendCustomEvent"),
                ],
                self.keys.CONNECT: [
                    ("OnLoaded.outputs:execOut", "Send1.inputs:execIn"),
                    ("OnTick.outputs:tick", "Send2.inputs:execIn"),
                ],
                self.keys.SET_VALUES: [
                    ("OnTick.inputs:onlyPlayback", False),
                    ("Send1.inputs:eventName", "foo"),
                    ("Send2.inputs:eventName", "foo"),
                    ("Send1.inputs:path", "Loaded"),
                    ("Send2.inputs:path", "Tick"),
                ],
            },
        )
        # Evaluate once so that graph is in steady state.
        await og.Controller.evaluate()

        # Verify Loaded came before OnTick.
        self.assertListEqual(events, ["Loaded", "Tick"])

    # ----------------------------------------------------------------------
    async def test_messagebusevent_nodes(self):
        """Test OnMessageBusEvent and SendMessageBusEvent nodes"""

        og.Controller.create_graph({"graph_path": self.TEST_GRAPH_PATH, "evaluator_name": "execution"})
        (
            _,
            (on_message_bus_event, counter_1, on_impulse_event, send_message_bus_event),
            _,
            _,
        ) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                self.keys.CREATE_NODES: [
                    ("OnMessageBusEvent", "omni.graph.action.OnMessageBusEvent"),
                    ("Counter1", "omni.graph.action.Counter"),
                    ("OnImpulseEvent", "omni.graph.action.OnImpulseEvent"),
                    ("SendMessageBusEvent", "omni.graph.action.SendMessageBusEvent"),
                ],
                self.keys.CONNECT: [
                    ("OnMessageBusEvent.outputs:execOut", "Counter1.inputs:execIn"),
                    ("OnImpulseEvent.outputs:execOut", "SendMessageBusEvent.inputs:execIn"),
                ],
                self.keys.SET_VALUES: [
                    ("OnMessageBusEvent.inputs:onlyPlayback", False),
                    ("OnImpulseEvent.inputs:onlyPlayback", False),
                    ("OnMessageBusEvent.inputs:eventName", "testEvent"),
                    ("SendMessageBusEvent.inputs:eventName", "testEvent"),
                ],
            },
        )
        # One compute for the first-time subscribe.
        await omni.kit.app.get_app().next_update_async()

        def get_all_supported_types() -> List[str]:
            """Helper to get all the types supported by the node"""
            types = []
            for attr_type in ogn.supported_attribute_type_names():
                if (
                    attr_type in ("any", "bundle", "execution", "target", "path")
                    or attr_type.startswith("objectId")
                    or attr_type.startswith("frame")
                ):
                    continue
                types.append(attr_type)
            return types

        def assert_are_equal(expected_val, val):
            """Helper to assert two values are equal, sequence container type need not match"""
            if isinstance(expected_val, (list, tuple, np.ndarray)):
                for left, right in zip(expected_val, val):
                    return assert_are_equal(left, right)
            if isinstance(val, np.ndarray):
                self.assertListEqual(expected_val, list(val))
            else:
                self.assertEqual(expected_val, val)
            return True

        def flatten(val, og_type):
            is_array = og_type.array_depth > 0
            is_tuple = og_type.tuple_count > 1
            is_matrix = is_tuple and (
                og_type.role in (og.AttributeRole.FRAME, og.AttributeRole.MATRIX, og.AttributeRole.TRANSFORM)
            )
            if is_array:
                if is_matrix:
                    val = np.array(val).flatten().flatten().tolist()
                elif is_tuple:
                    val = np.array(val).flatten().tolist()
                else:
                    val = np.array(val).tolist()
            elif is_matrix:
                val = np.array(val).flatten().tolist()
            return val

        msg = carb.events.type_from_string("testEvent")
        payload = {"extra_junk": 42}
        expected_vals = []

        def add_attributes(name, sup_type):
            out_attrib = og.Controller.create_attribute(
                on_message_bus_event, f"outputs:{name}", sup_type, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
            )
            # Create a dynamic input attribute on the node which matches the type of the test payload.
            in_attrib = og.Controller.create_attribute(
                send_message_bus_event, f"inputs:{name}", sup_type, og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            )
            return (out_attrib, in_attrib)

        for sup_type in sorted(get_all_supported_types()):
            name = sup_type.replace("[", "_").replace("]", "_") + "_"
            manager = ogn.get_attribute_manager_type(sup_type)

            # Create a dynamic output attribute on the node which matches the type of the test payload.
            og_type = og.AttributeType.type_from_ogn_type_name(sup_type)

            out_attrib, in_attrib = add_attributes(name, sup_type)

            # Get a sample value in python format (nested tuples/lists).
            sample_val = manager.sample_values()[0]

            empty_val = manager.empty_base_value()

            # Flatten the sample value for use with event dict.
            payload_val = flatten(sample_val, og_type)

            og.Controller.set(in_attrib, sample_val)
            payload[name] = payload_val
            expected_vals.append((out_attrib, sample_val, payload_val, og_type, empty_val))

        # special treatment for target because we want to test single and multi
        # target case, but the type name is the same for both
        target_type = og.AttributeType.type_from_ogn_type_name("target")
        # single target
        out_attrib, in_attrib = add_attributes("target_", target_type)
        sample_val = Sdf.Path(self.TEST_GRAPH_PATH)
        payload_val = str(sample_val)
        og.Controller.set(in_attrib, payload_val)
        payload["target_"] = payload_val
        # multi-target
        out_attrib, in_attrib = add_attributes("target_multi_", target_type)
        sample_val = [Sdf.Path(self.TEST_GRAPH_PATH), Sdf.Path(on_message_bus_event.get_prim_path())]
        payload_val = [str(p) for p in sample_val]
        og.Controller.set(in_attrib, payload_val)
        payload["target_multi_"] = payload_val
        expected_vals.append((out_attrib, sample_val, payload_val, og_type, []))

        # Verify that the node is not triggered initially
        compute_count = og.Controller.attribute("outputs:count", counter_1).get()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(compute_count, og.Controller.attribute("outputs:count", counter_1).get())

        # Push the message to kit message bus.
        omni.kit.app.get_app().get_message_bus_event_stream().push(msg, payload=payload)

        # Wait for one kit update to allow the event-push mechanism to trigger the node callback.
        await omni.kit.app.get_app().next_update_async()

        def verify(expected_val_list):
            for out_attrib, _, payload_val, og_type, _ in expected_val_list:
                # Verify the value.
                out_val = og.Controller.get(out_attrib)
                try:
                    out_val = flatten(out_val, og_type)
                    assert_are_equal(out_val, payload_val)
                except AssertionError as exc:
                    raise AssertionError(f"{out_val} != {payload_val} for {out_attrib.get_name()}") from exc

        verify(expected_vals)

        def clear_outputs(expected_val_list):
            for out_attrib, _, _, og_type, empty_val in expected_val_list:
                if og_type.array_depth > 0:
                    og.Controller.set(out_attrib, [])
                elif og_type.tuple_count > 1:
                    og.Controller.set(out_attrib, [empty_val] * og_type.tuple_count)
                else:
                    og.Controller.set(out_attrib, empty_val)

        # ---------------------
        # Now verify again, but using the send node instead of manual push
        # Clear an output
        clear_outputs(expected_vals)
        og.Controller.set(og.Controller.attribute("state:enableImpulse", on_impulse_event), True)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        verify(expected_vals)

        # ---------------------
        # change the event name and verify again
        clear_outputs(expected_vals)
        new_type = carb.events.type_from_string("testEvent2")
        og.Controller.attribute("inputs:eventName", on_message_bus_event).set("testEvent2")
        og.Controller.attribute("inputs:eventName", send_message_bus_event).set("testEvent2")
        await omni.kit.app.get_app().next_update_async()
        omni.kit.app.get_app().get_message_bus_event_stream().push(new_type, payload=payload)
        await omni.kit.app.get_app().next_update_async()
        verify(expected_vals)

        # ---------------------
        # test really huge array
        clear_outputs(expected_vals)
        payload = {"float___": np.zeros(2**31, dtype=float)}
        omni.kit.app.get_app().get_message_bus_event_stream().push(new_type, payload=payload)
        await omni.kit.app.get_app().next_update_async()

        # ---------------------
        # test sending empty arrays
        # FIXME: carb IDictionary python binding doesn't support empty values, so this doesn't
        # work from python OVCC-1407
        # array_test = []
        # for out_attrib, _, _, og_type, _ in expected_vals:
        #     name = out_attrib.remove_port_type_from_name(out_attrib.get_name(), False)
        #     if (og_type.base_type == og.BaseDataType.RELATIONSHIP) or \
        #         (og_type.array_depth > 0 and og_type.role != og.AttributeRole.TEXT):
        #         array_test.append((out_attrib, [], [], og_type))
        #         og.Controller.set(og.Controller.attribute(f"inputs:{name}", send_message_bus_event), [])
        #     else:
        #         send_message_bus_event.remove_attribute(f"inputs:{name}")
        # og.Controller.set(og.Controller.attribute("state:enableImpulse", on_impulse_event), True)
        # await omni.kit.app.get_app().next_update_async()
        # verify(array_test)

        # ---------------------
        # exercise removing an attribute from the node
        in_attrib = og.Controller.remove_attribute("outputs:float_", on_message_bus_event)
        await omni.kit.app.get_app().next_update_async()

        # ---------------------
        # delete the node and send another event to verify the cleanup
        og.Controller.delete_node(on_message_bus_event)
        await omni.kit.app.get_app().next_update_async()
        omni.kit.app.get_app().get_message_bus_event_stream().push(new_type, payload=payload)
        await omni.kit.app.get_app().next_update_async()
