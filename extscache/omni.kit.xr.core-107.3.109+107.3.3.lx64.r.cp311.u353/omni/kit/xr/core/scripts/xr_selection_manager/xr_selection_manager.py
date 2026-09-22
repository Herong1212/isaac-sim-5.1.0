# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

from typing import Iterable, Optional, Union

import carb
import omni.usd
from pxr import Gf

from ..xr_class_wrappers import XRCore, XRTargetInfo, XRToken, XRUsdLayer
from ..xr_singleton import XRSingleton, XRSingletonType
from .xr_selection_beam import XRSelectionBeam

# Define event that are triggered when the selection beam moves through the stage
# PRESS: event when the user triggers a button while pointing the beam at a prim
# RELEASE: event when user release the button that finishes the release
# UPDATE: sent between PRESS and RELEASE every frame, to allow for UI to be updated
# HOVER: sent when hoovering over a specific prim
# HOVER_ENTER: sent when starting to hoover over a specific prim
# HOVER_LEAVE: sent when stopping to hoover over a specific prim


class XRSelectionEventType:
    PRESS: str = "press"
    RELEASE: str = "release"
    UPDATE: str = "update"
    HOVER: str = "hover"
    HOVER_ENTER: str = "hover_enter"
    HOVER_LEAVE: str = "hover_leave"


# Class for automatically removing subscription when deleted
class XRSelectionEventGeneratorSubscription:
    def __init__(self, disconnect_fcn):
        self.__disconnect_fcn = disconnect_fcn

    def __del__(self):
        self.__disconnect_fcn()


class XRSelectionEventGenerators:
    def __init__(self):

        # List of allowable event types
        self.__event_types: list[str] = [
            XRSelectionEventType.PRESS,
            XRSelectionEventType.RELEASE,
            XRSelectionEventType.UPDATE,
            XRSelectionEventType.HOVER,
            XRSelectionEventType.HOVER_ENTER,
            XRSelectionEventType.HOVER_LEAVE,
        ]

        # For each type we keep a list of callbacks that need to
        # be executed
        self.__event_generator: dict[str, list] = dict()
        for event_type in self.__event_types:
            self.__event_generator[event_type] = []

        self.__subscription_id: int = 0
        self.__xr_core: XRCore = XRCore.get_singleton()

    def bind_event_generator(
        self,
        usd_path: str,
        priority: int,
        event_name: str,
        event_types: Union[str, Iterable[str]],
    ) -> XRSelectionEventGeneratorSubscription:
        """
        Bind a set of event generators. This will record a set of events that need to be
        send out for a given prim.

        Args:
            usd_path:       the base usd path for which to record an event. Events normally bubble up and the
                            global scope is indicated by '/'
            priority:       priority of handling this event. If event handling is stopped, handlers of a lower
                            priority will not be called.
            event_name:     base event name. Event names on the message bus are of format <event_name>.<event.type>
            event_types:    list of event types for which events need to be generated.

        Return:
            XRSelectionEventGeneratorSubscription - object with subscription information
        """

        # Insure that event_types is a list
        if isinstance(event_types, str):
            event_types = [event_types]

        # Key is used to find events belonging to a subscription
        self.__subscription_id = self.__subscription_id + 1

        # Add the events to the list
        for event_type in event_types:
            if event_type not in self.__event_types:
                raise Exception("Invalid event type " + event_type)
            self.__event_generator[event_type].append(
                (usd_path, priority, event_name + "." + event_type, self.__subscription_id)
            )
            self.__event_generator[event_type].sort(key=lambda x: f"{x[0]}//{x[1]:03d}{x[3]:03d}", reverse=True)

        # Bind number into local variable to avoid having self inside the lambda function
        subscription_id = self.__subscription_id
        return XRSelectionEventGeneratorSubscription(lambda: self.unbind_event_generator(subscription_id))

    def unbind_event_generator(self, subscription_id: int):
        """
        Unbind an event genator based on the key in the subscription. This function is called
        by the subscription to delete the events connected to a subscription. Do not use directly.

        Args:
            subscription_id:  subscription_id of the subscription
        """

        # find the event generator that needs to be removed
        for event_type in self.__event_types:
            idx_to_remove: Optional[int] = None
            for idx in range(len(self.__event_generator[event_type])):
                if self.__event_generator[event_type][idx][3] == subscription_id:
                    idx_to_remove = idx
                    break

            if idx_to_remove is not None:
                self.__event_generator[event_type].pop(idx_to_remove)

    def execute(
        self, event_type: str, selected_path: Optional[str], beam: XRSelectionBeam, button_changed: str = ""
    ) -> None:
        """
        Execute triggering an event to be injected into the message bus system.
        Events that are registered to the usd_path or its parents are called in order starting with
        usd_path itself and then bubbling up to the parents, until it is consumed or the global scope
        is reached.

        Args:
            event_type:      the event type to generate
            selected_path:   the usd path for which to generate an event
            beam:            beam that is triggering the execution
            button_changed:  the button this execution is connected to
        """

        # Initialize the data sent with the event to default values
        hit_point: Gf.Vec3d = Gf.Vec3d(0.0, 0.0, 0.0)
        hit_normal: Gf.Vec3d = Gf.Vec3d(0.0, 0.0, 0.0)
        hit_valid: bool = False

        # We use "/" to indicate the entire stage, usd does not have a root to all
        enclosing_model: str = "/"

        if selected_path is None:
            selected_path = "/"
        else:
            enclosing_model = XRCore.get_singleton().get_enclosing_model(selected_path)

        # Get latest point that the beam is known to point at
        # this data maybe 1 or 2 frames old, as we usd the GPU
        # to resolve these
        target_info: Optional[XRTargetInfo] = beam.get_target_info()

        if target_info is not None and target_info.valid:
            hit_point = target_info.position
            hit_normal = target_info.normal
            hit_valid = True

        # TODO: This needs to run through USD eventually
        idx: int = 0
        while idx < len(self.__event_generator[event_type]):
            if selected_path.startswith(self.__event_generator[event_type][idx][0]):
                if self.__event_generator[event_type][idx][2] is not None:
                    # The following function is a special dispatch function missing in carb
                    # that returns whether the event was consumed.
                    # Since we are stringing multiple dispatches together we need to know if
                    # event was consumed. This special function returns True if the event was
                    # consumed.

                    if self.__xr_core.dispatch_message_bus_and_check_consume(
                        self.__event_generator[event_type][idx][2],
                        {
                            "hand": beam.get_hand(),
                            "selected_path": selected_path,
                            "enclosing_model": enclosing_model,
                            "hit_valid": hit_valid,
                            "hit_point": (hit_point[0], hit_point[1], hit_point[2]),
                            "hit_normal": (hit_normal[0], hit_normal[1], hit_normal[2]),
                            "button_changed": button_changed,
                        },
                    ):
                        return

            idx = idx + 1

        return


@XRSingleton()
class XRSelectionManager(XRSingletonType):
    """
    XRSelectionManager:

    Selection manager takes input from the selection tool and posts the
    selected objects onto an event queue, so other tools can listen to it

    """

    def __init__(self):
        self.__event_generators: XRSelectionEventGenerators = XRSelectionEventGenerators()
        self.__prev_hover = {}
        self.__beams = {}

    def set_selection(self, selection: Union[str, Iterable[str], None]) -> None:
        """
        Set selected prims in the current stage.

        Args:
            selection:     the path(s) that need to be selected
        """

        # If no selection is made, we should clear out all selections
        if selection is None:
            omni.usd.get_context().get_selection().clear_selected_prim_paths()
            return

        # Convert the selection into a list if it is not a list already
        if isinstance(selection, str):
            if selection == "":
                omni.usd.get_context().get_selection().clear_selected_prim_paths()
                return
            selection = [selection]

        # We are making a new selection, so clear the old one
        omni.usd.get_context().get_selection().clear_selected_prim_paths()

        # Add each path in the selection to the set of selected prims
        for sel in selection:
            enclosing_selection = XRCore.get_singleton().get_enclosing_model(sel)
            omni.usd.get_context().get_selection().set_prim_path_selected(enclosing_selection, True, True, True, False)

    def toggle_selection(self, selection: Union[str, None]) -> None:
        """
        Toggle selection:
            if model is selected, unselect
            if not selected make it the selected model

        Args:
            selection:   usd prim path to toggle selection of
        """

        if selection is None:
            omni.usd.get_context().get_selection().clear_selected_prim_paths()
            return

        if selection == "":
            omni.usd.get_context().get_selection().clear_selected_prim_paths()
            return

        # Get the enclosing model. This will help do the right behavior by selecting to model
        # instead of one of its components.
        enclosing_selection = XRCore.get_singleton().get_enclosing_model(selection)

        # Do the actual toggle
        if omni.usd.get_context().get_selection().is_prim_path_selected(enclosing_selection):
            omni.usd.get_context().get_selection().clear_selected_prim_paths()
        else:
            if carb.settings.get_settings().get("/app/viewport/outline/enabled") is False:
                carb.settings.get_settings().set("/app/viewport/outline/enabled", True)

            omni.usd.get_context().get_selection().set_prim_path_selected(enclosing_selection, True, True, True, False)

    def clear_selection(self) -> None:
        """
        Clear selection.
        """
        omni.usd.get_context().get_selection().clear_selected_prim_paths()

    def bind_event_generator(
        self, path: Union[str, None], priority: int, event_name: str, event_types: Union[str, Iterable[str]]
    ) -> XRSelectionEventGeneratorSubscription:
        """
        Bind an event generator for a given prim path.

        Args:
            path:           path of prim that needs an event generator (can be a scope)
            priority:       priority of the event
            event_name:     name of tbe event to send
            event_types:    event types that need to be generated

        Return:
            subscription to selection manager (destroy subscription to unregister event generator)
        """

        # Handle multiple ways of setting global scope
        # We make global scope "/" so it is properly sorted in the list
        if path is None:
            path = "/"

        if len(path) == 0:
            path = "/"

        return self.__event_generators.bind_event_generator(path, priority, event_name, event_types)

    def create_beam(
        self,
        usd_layer: XRUsdLayer,
        hand: Union[XRToken, str],
        attachment_point: str,
        material: str,
        max_length: float = 10000,
        tube_radius: float = 0.5,
    ) -> XRSelectionBeam:
        """
        Create a new beam

        Args:
            usd_layer:          usd layer to use for the beam
            hand:               hand connected to the beam
            attachment_point:   where to construct the beam
            material:           material to use for the beam
            max_length:         maximum length of beam (cm)
            tube_radius:        radius of the beam (cm)

        Return:
            newly created beam
        """

        self.__beams[str(hand)] = XRSelectionBeam(usd_layer, hand, attachment_point, material, max_length, tube_radius)
        return self.__beams[str(hand)]

    def destroy_beam(self, hand: Union[XRToken, str]) -> None:
        """
        Destroy beam

        Args:
            hand:   hand connected to the beam
        """

        self.__beams.pop(str(hand), None)

    def get_beam(self, hand: Union[XRToken, str]) -> Optional[XRSelectionBeam]:
        """
        Get beam for selection manager registry.

        Args:
            hand:   hand connected to the beam

        Return:
            beam
        """

        if str(hand) in self.__beams:
            return self.__beams[str(hand)]

        return None

    def dispatch_release(self, hand: Union[XRToken, str], button_changed: str) -> None:
        """
        Dispatch a selection release event onto the event stream, meaning user pressed and then released
        the trigger.

        Args:
            hand:           hand connected to the beam
            button_changed: the button that triggered the release event
        """

        beam: Optional[XRSelectionBeam] = self.get_beam(hand)
        if beam is None:
            return

        usd_path: Optional[str] = None

        # We cache the target info on button press, to lock down the usd prim
        # This ensures that press and release are triggered with the same usd_path
        # The actual location in the event will be different and will indicate
        # where the beam currently points. We only use the usd prim path cached
        # at press.
        target_info: Optional[XRTargetInfo] = beam.get_button_target_info()

        if target_info is not None:
            usd_path = target_info.get_target_usd_path()

        # Remove button from the list of buttons that are pressed on the beam
        beam.remove_pressed_button(button_changed)

        # Figure out which callbacks to call
        self.__event_generators.execute(XRSelectionEventType.RELEASE, usd_path, beam, button_changed)

    def dispatch_press(self, hand: Union[XRToken, str], button_changed: str) -> None:
        """
        Dispatch a selection press event onto the event stream, meaning user pressed the trigger.

        Args:
            hand:           hand connected to the beam
            button_changed: the button that triggered the press event
        """

        beam: Optional[XRSelectionBeam] = self.get_beam(hand)
        if beam is None:
            return

        beam.update_target_info()

        selected_path: Optional[str] = None

        # If this is the second button the press we use the prim of the first prim
        # where the button was pressed as the focus.
        # the get_button_target_info returns the target_info on first button press.
        target_info: Optional[XRTargetInfo] = beam.get_button_target_info()
        if target_info is not None:
            selected_path = target_info.get_target_usd_path()

        beam.add_pressed_button(button_changed)

        # Figure out which callbacks to call
        self.__event_generators.execute(XRSelectionEventType.PRESS, selected_path, beam, button_changed)

    def dispatch_update(self, hand: Union[XRToken, str]) -> None:
        """
        Dispatch a selection update event onto the event stream, meaning user is still holding the trigger

        Args:
            hand:           hand connected to the beam
        """

        beam: Optional[XRSelectionBeam] = self.get_beam(hand)
        if beam is None:
            return

        # Read out what the beam is pointing at and update the beam
        beam.update_target_info()

        selected_path: Optional[str] = None

        # When sending updates grab the usd prim path of prim path when first
        # button was pressed.
        target_info: Optional[XRTargetInfo] = beam.get_button_target_info()
        if target_info is not None:
            selected_path = target_info.get_target_usd_path()

        # Figure out which callbacks to call
        self.__event_generators.execute(XRSelectionEventType.UPDATE, selected_path, beam)

    def process_hover(self, hand: Union[XRToken, str]) -> None:
        """
        Process hover events for a given beam. This will figure out what was send last time
        and create a proper enter or leave event, as well trigger an hover event for the
        prim that is currently being hovered by the beam.

        Args:
            hand:           hand connected to the beam
        """

        beam: Optional[XRSelectionBeam] = self.get_beam(hand)
        if beam is None:
            return

        # Update the hoover information: which prim is the beam pointing at
        beam.update_target_info()

        # Read the information from the beam
        # If a button is pressed we get the hoover position of when the
        # button was pressed. So hoover events are essentially frozen until
        # the button is released. So highlighting will show the focus
        # of a current action.
        target_info: Optional[XRTargetInfo] = beam.get_button_target_info()

        selected_path: Optional[str] = None
        if target_info is not None:
            selected_path = target_info.get_target_usd_path()

        # ensure that __prev_hover has a field for current hand
        if beam.get_hand() not in self.__prev_hover:
            self.__prev_hover[beam.get_hand()] = None

        prev_hover = self.__prev_hover[beam.get_hand()]
        if selected_path is None:
            if prev_hover is not None:
                # No longer selected, but was selected previously
                # Send leave event for previous hover.
                # No enter is needed as the beam is not pointing at anything
                self.__event_generators.execute(XRSelectionEventType.HOVER_LEAVE, prev_hover, beam)
            self.__prev_hover[beam.get_hand()] = None
            return

        if selected_path != prev_hover:
            # Something new is being pointed at
            # First send leave for previous one
            if prev_hover is not None:
                self.__event_generators.execute(XRSelectionEventType.HOVER_LEAVE, prev_hover, beam)

            # Send an enter event
            if selected_path is not None:
                self.__event_generators.execute(XRSelectionEventType.HOVER_ENTER, selected_path, beam)

            # record for which prim we sent an enter event
            self.__prev_hover[beam.get_hand()] = selected_path

        # The beam is hoovering a prim, so a Hoover event needs to be sent
        self.__event_generators.execute(XRSelectionEventType.HOVER, selected_path, beam)
