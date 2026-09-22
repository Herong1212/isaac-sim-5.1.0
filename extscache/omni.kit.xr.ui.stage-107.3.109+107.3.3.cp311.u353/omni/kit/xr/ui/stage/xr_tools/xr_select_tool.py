# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

from typing import Optional

import carb
from omni.kit.xr.core import (
    XRInputDeviceGeneratorEvent,
    XRSelectionBeam,
    XRSelectionEvent,
    XRToolComponentBase,
    XRTooltip,
    XRUsdLayer,
)
from omni.kit.xr.scene_view.core import InputButtonMap, XRSceneView
from omni.kit.xr.scene_view.utils import SceneViewUtils, UiInput, UiInputMotion, UiInputToggle

XR_USER_HAND_LEFT = "/user/hand/left"
XR_USER_HAND_RIGHT = "/user/hand/right"

XR_SCENEVIEW_FILTER = "_scene_view_"

XR_GUI_LAYER_GROUP = "select_tool"
XR_GUI_LAYER = "controllers"


# State of the select tool per controller
class XRSelectToolState:

    def __init__(self):
        # Whether select beam is active
        self.select_activated: bool = False

        # Subscription for trigger button, we only assign that button if the beam is active
        # or isppointing at a menu
        self.subs = []


class XRSelectTool(XRToolComponentBase):

    def __init__(self):

        # Initialize parent class
        super().__init__("select")

        # TODO: File bug
        # Deal with problem in Omni Scene UI not able to process
        # multiple input devices at the same time
        self.__ui_focused_hand: Optional[str] = None
        self.__ui_focused_count: int = 0
        self.__usd_layer: Optional[XRUsdLayer] = None

        self.__state: dict[str, XRSelectToolState] = {}
        self.__state[XR_USER_HAND_LEFT] = XRSelectToolState()
        self.__state[XR_USER_HAND_RIGHT] = XRSelectToolState()

        # Define tooltips for triggering and enabling selection beam
        # Tooltips are stored in the tooltip manager and are looked up by key on the event generator
        self.get_tooltip_manager().define_tooltip("select_toggle_beam", XRTooltip(text="Selection beam"))
        self.get_tooltip_manager().define_tooltip("select_object", XRTooltip(text="Select object"))

        # To construct teleporters we need to have a controller model loaded
        # TODO: In the future just depend on positions coming from OpenXR

        # The first two subscriptions listen to when the controllers layer is enabled (priority 10 is after) and
        # when it is disabled (before priority is -10)
        # The second set of subscriptions list to when the model is changed and re enable after models are changed
        # TODO: should move this to its own message on the message bus
        self.__controller_subs = [
            self.register_message_bus_event_handler("xr_gui.controllers.enable", self.update_beam, 10),
            self.register_message_bus_event_handler("xr_gui.controllers.disable", self.on_disable, -10),
            self.register_message_bus_event_handler("xr_input.user_hand_left.attachments_change", self.update_beam),
            self.register_message_bus_event_handler("xr_input.user_hand_right.attachments_change", self.update_beam),
        ]

        # If the tool was already enabled, ensure on_enable is called
        self.run_enable_if_enabled()

    def on_enable(self) -> None:
        """
        This function is called when tool is enabled.
        """

        self.update_beam()

    def update_beam(self) -> None:
        """
        This function is called when the tool is enabled.
        """

        if not self.is_enabled():
            return

        # Get the usd layer with the XR controllers on it as the
        # ui component layer
        if self.has_usd_layer(XR_GUI_LAYER):
            self.__usd_layer = self.get_usd_layer(XR_GUI_LAYER)

        self.__menu_path = XRSceneView.get_base_path()

        if self.__usd_layer is None:
            return

        self.remove_beams()

        # Clear all previous subscriptions
        self.__subs = []

        # The aim attachment point is required
        if (self.__usd_layer.get_meta_data(XR_USER_HAND_LEFT + "/attachments/aim") is None) and (
            self.__usd_layer.get_meta_data(XR_USER_HAND_RIGHT + "/attachments/aim") is None
        ):
            return

        # Ensure that the beam materials are loaded into the scene
        self.__beam_material = (
            self.__usd_layer.load_asset("{generic.materials}/selection_emissive_material.usd")
            + "/Looks/selection_emissive_material"
        )

        self.get_xr_core().set_pickable_path(self.__menu_path, True)

        # The XR ui system needs two things:
        # 1) It needs events sent to the message bus to be enacted upon
        # 2) It needs to be setup to send the right events to the message bus

        # Register callback points for input events and register event generators

        # This list contains event generators for both controller input buttons,
        # and event generators for when stage elements are pointed at.

        self.__subs = [
            self.register_message_bus_event_handler("xr_left_toggle_beam.release", self.toggle_beam_enable),
            self.register_message_bus_event_handler("xr_right_toggle_beam.release", self.toggle_beam_enable),
            self.register_message_bus_event_handler("xr_left_select_beam.press", self.beam_select_press),
            self.register_message_bus_event_handler("xr_left_select_beam.release", self.beam_select_release),
            self.register_message_bus_event_handler("xr_right_select_beam.press", self.beam_select_press),
            self.register_message_bus_event_handler("xr_right_select_beam.release", self.beam_select_release),
            self.register_message_bus_event_handler("xr_selection_default.release", self.default_action_select_object),
            self.register_message_bus_event_handler("xr_selection_gui.hover", self.action_gui_hover),
            self.register_message_bus_event_handler("xr_selection_gui.hover_enter", self.action_gui_hover_enter),
            self.register_message_bus_event_handler("xr_selection_gui.hover_leave", self.action_gui_hover_leave),
            self.register_message_bus_event_handler("xr_selection_gui.release", self.action_gui_release),
            self.register_message_bus_event_handler("xr_selection_gui.press", self.action_gui_press),
            self.register_message_bus_event_handler("xr_selection_gui.update", self.action_gui_update),
            self.bind_input_event_generator(
                "xr_left_toggle_beam", ("release"), {"tooltip_button": "select_toggle_beam"}
            ),
            self.bind_input_event_generator(
                "xr_right_toggle_beam", ("release"), {"tooltip_button": "select_toggle_beam"}
            ),
            # The next one is the default option for when a selection beam is triggered on any prim
            self.bind_selection_event_generator("xr_selection_default", ("release"), "/", 1),
            # If the selection beam hits a ui menu, this event generator will send events for that case
            self.bind_selection_event_generator(
                "xr_selection_gui",
                ("hover", "hover_enter", "hover_leave", "release", "press", "update"),
                self.__menu_path,
                30,
            ),
        ]

        # Link the beam
        self.setup_beam(XR_USER_HAND_LEFT)
        self.setup_beam(XR_USER_HAND_RIGHT)

    def on_disable(self) -> None:
        """
        This function is called when the tool is disabled.
        """

        # Remove all the beams in use
        self.remove_beams()

        # Remove all callbacks and event generators
        self.__subs = []

        # Clear our pointer to the controller layer
        self.__usd_layer = None

    def on_update(self) -> None:
        """
        This function is called each frame when the tool is active.
        """

        # Update beams and apply hoovering
        # This is not triggered by any input just by what the
        # controller is hoovering over

        for hand in [XR_USER_HAND_LEFT, XR_USER_HAND_RIGHT]:

            # What is the beam pointing at; the hover information is updated by this call
            self.get_selection_manager().process_hover(hand)

            beam: Optional[XRSelectionBeam] = self.get_selection_manager().get_beam(hand)

            if beam is None:
                continue

            if beam.is_visible() and not self.__state[hand].select_activated:

                # Only override the buttons for selection if we need them
                if hand == XR_USER_HAND_LEFT:
                    self.__state[hand].subs = [
                        self.bind_input_event_generator(
                            "xr_left_select_beam", ("press", "release"), {"tooltip_button": "select_object"}
                        )
                    ]
                elif hand == XR_USER_HAND_RIGHT:
                    self.__state[hand].subs = [
                        self.bind_input_event_generator(
                            "xr_right_select_beam", ("press", "release"), {"tooltip_button": "select_object"}
                        )
                    ]

                self.__state[hand].select_activated = True

            elif not beam.is_visible() and self.__state[hand].select_activated:
                self.__state[hand].subs = []
                self.__state[hand].select_activated = False

            # Beam can be made visible by a different component
            beam.update_visibility()

            # send an update to what ever is listening if a button
            # is pressed.
            if beam.check_if_buttons_are_pressed():
                self.get_selection_manager().dispatch_update(hand)

    def setup_beam(self, hand: str) -> None:
        """
        Setup a single beam
        """

        if self.__usd_layer is None:
            return

        attachment_point_path: Optional[str] = self.__usd_layer.get_meta_data(hand + "/attachments/aim")
        if attachment_point_path is None:
            return

        # Need to make a proper beam object
        self.get_selection_manager().create_beam(self.__usd_layer, hand, attachment_point_path, self.__beam_material)

    def remove_beams(self) -> None:
        """
        Remove the beams from selection manager and usd layer.
        """
        self.get_selection_manager().destroy_beam(XR_USER_HAND_LEFT)
        self.get_selection_manager().destroy_beam(XR_USER_HAND_RIGHT)

    def toggle_beam_enable(self, event: XRInputDeviceGeneratorEvent) -> None:
        """
        This function is called when user releases beam toggle button on controller.
        """

        hand: str = event.input_device
        beam: Optional[XRSelectionBeam] = self.get_selection_manager().get_beam(hand)
        if beam is not None:
            beam.set_active(not beam.is_active())

    def beam_select_press(self, event: XRInputDeviceGeneratorEvent) -> None:
        """
        This function is called when user presses select button on the controller.
        """

        hand: str = event.input_device
        self.get_selection_manager().dispatch_press(hand, "select")

    def beam_select_release(self, event: XRInputDeviceGeneratorEvent) -> None:
        """
        This function is called when user releases select button on the controller.
        """

        hand: str = event.input_device
        self.get_selection_manager().dispatch_release(hand, "select")

    def default_action_select_object(self, ev: XRSelectionEvent) -> None:
        """
        This function is called when selecting an object and no other
        component consumes the event
        """
        beam: Optional[XRSelectionBeam] = self.get_selection_manager().get_beam(ev.hand)
        if beam is None:
            return

        usd_path: str = ev.selected_path

        if not beam.is_active():
            # when aim is not active, clear selection on trigger
            self.get_selection_manager().clear_selection()
            ev.consume()
            return

        if usd_path == "/":
            # If nothing selected: clear selection
            self.get_selection_manager().clear_selection()
            ev.consume()
            return

        self.get_selection_manager().toggle_selection(usd_path)

        ev.consume()

    def action_gui_press(self, event: XRSelectionEvent) -> None:
        """
        Called when trigger is pressed with selection beam pointing at a ui element.
        """

        event.consume()

        if self.__ui_focused_hand != event.hand:
            return

        if event.selected_path is not None and self.__menu_path not in event.selected_path:
            return

        # Send an input event to the the SceneView
        button_event: UiInput
        if "select" in event.button_changed:
            button_event = UiInputToggle(InputButtonMap.LeftButton, True)
        elif "grab" in event.button_changed:
            button_event = UiInputToggle(InputButtonMap.RightButton, True)
        else:
            return

        hit_scene_view = SceneViewUtils.find_scene_view(event.selected_path)
        if hit_scene_view is not None:
            button_event.push_input(hit_scene_view)

    def action_gui_release(self, event: XRSelectionEvent) -> None:
        """
        Called when trigger is released with selection beam pointing at a ui element.
        """

        # ensure the default selection action is not triggered
        event.consume()

        if self.__ui_focused_hand != event.hand:
            return

        if event.selected_path is not None and self.__menu_path not in event.selected_path:
            return

        button_event: UiInput
        if "select" in event.button_changed:
            button_event = UiInputToggle(InputButtonMap.LeftButton, False)
        elif "grab" in event.button_changed:
            button_event = UiInputToggle(InputButtonMap.RightButton, False)
        else:
            return

        hit_scene_view = SceneViewUtils.find_scene_view(event.selected_path)
        if hit_scene_view is not None:
            button_event.push_input(hit_scene_view)

    def action_gui_hover_enter(self, event: XRSelectionEvent) -> None:
        """
        Called when the beam starts hovering over an ui element
        """

        # ensure the default selection action is not triggered
        event.consume()

        # TODO: Check if this is still needed
        if event.selected_path is not None and self.__menu_path not in event.selected_path:
            return

        # Check if another beam is already hovering.
        # Right now the UI system has a limitation that it can only deal with one input
        # device, if another beam already has focus do not active this beam.
        if self.__ui_focused_hand is None:

            # Get the beam, so we can annotate that it is pointing at the ui
            beam = self.get_selection_manager().get_beam(event.hand)
            if beam is None:
                carb.log_warn("[XR] Beam not found despite hover enter event being triggered")
                return

            self.__ui_focused_hand = beam.get_hand()
            beam.set_pointing_at_ui(True)

    def action_gui_hover_leave(self, event: XRSelectionEvent) -> None:
        """
        Called when the beam stops hovering over an ui element
        """

        # ensure the default selection action is not triggered
        event.consume()

        if event.selected_path is not None and self.__menu_path not in event.selected_path:
            return

        # If it is not the focused hand, nothing needs to be done
        if self.__ui_focused_hand != event.hand:
            return

        # Mark the selection beam as not pointing at ui
        beam = self.get_selection_manager().get_beam(event.hand)
        assert beam is not None

        beam.set_pointing_at_ui(False)
        self.__ui_focused_hand = None

    def action_gui_hover(self, event: XRSelectionEvent) -> None:
        """
        Called when the beam is hovering over an ui element
        """

        event.consume()
        beam = self.get_selection_manager().get_beam(event.hand)
        assert beam is not None

        # GUI movement calls do not distinguish between "tracked while pressed" and "hovering"
        # TODO: File bug on how omni sceneview works

        # UI system cannot deal with hover information if a button is pressed
        if beam.check_if_buttons_are_pressed():
            return

        if self.__ui_focused_hand != beam.get_hand():
            return

        if event.selected_path is not None and self.__menu_path not in event.selected_path:
            return

        if self.__usd_layer is None:
            return

        origin = beam.get_beam_pose()[3]
        end = beam.get_beam_end_pose()[3]
        direction = end - origin
        motion_event = UiInputMotion([origin[0], origin[1], origin[2]], [direction[0], direction[1], direction[2]])

        hit_scene_view = SceneViewUtils.find_scene_view(event.selected_path)
        if hit_scene_view is not None:
            motion_event.push_input(hit_scene_view)

    def action_gui_update(self, event: XRSelectionEvent) -> None:
        """
        Called when the beam is moving while a button is pressed
        """

        event.consume()

        if self.__ui_focused_hand != event.hand:
            return

        if event.selected_path is not None and self.__menu_path not in event.selected_path:
            return

        if self.__usd_layer is None:
            return

        beam = self.get_selection_manager().get_beam(event.hand)
        assert beam is not None

        origin = beam.get_beam_pose()[3]
        end = beam.get_beam_end_pose()[3]
        direction = end - origin
        motion_event = UiInputMotion([origin[0], origin[1], origin[2]], [direction[0], direction[1], direction[2]])

        hit_scene_view = SceneViewUtils.find_scene_view(event.selected_path)
        if hit_scene_view is not None:
            motion_event.push_input(hit_scene_view)
