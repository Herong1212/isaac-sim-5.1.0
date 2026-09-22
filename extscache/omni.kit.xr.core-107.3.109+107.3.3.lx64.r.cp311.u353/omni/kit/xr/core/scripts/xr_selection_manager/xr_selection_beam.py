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

from typing import Optional, Set, Union

import carb
from pxr import Gf

from ..xr_class_wrappers import XROrientationAlignment, XRTargetInfo, XRToken, XRTransformType, XRUsdLayer


class XRSelectionBeam:

    def __init__(
        self,
        usd_layer: XRUsdLayer,
        hand: Union[XRToken, str],
        attachment_point: str,
        material: str,
        max_length: float = 10000,
        tube_radius: float = 0.5,
    ):

        self.__hand: str = str(hand)
        self.__usd_layer: XRUsdLayer = usd_layer
        self.__group = "SELECTION_BEAM_" + self.__hand
        self.__attachment_point = attachment_point

        # Record path of where to put the beam
        self.__beam_path = self.__attachment_point + "/selection_beam"

        # Create the actual beam
        self.__usd_layer.add_beam(
            path=self.__beam_path,
            material_reference=material,
            max_length=max_length,
            tube_radius=tube_radius,
            group=self.__group,
            visible=False,
        )

        # At the end we put a reorient so one can attach markers and objects to the
        # beam.
        self.__end_path = self.__usd_layer.get_end_prim_path(self.__beam_path)
        self.__reorient_path = self.__end_path + "/reorient"

        # Create the reorient so pose always points up
        self.__usd_layer.add_reorient(
            path=self.__reorient_path,
            group=self.__group,
            alignment=XROrientationAlignment.device_up_right,
            input_device=hand,
        )

        # Optional turn table that can be added for remote grab
        self.__turn_table_path: Optional[str] = None
        self.__link_path: Optional[str] = None

        # When pointing at a menu, the beam automatically becomes visible
        self.__pointing_at_ui: bool = False

        # Whether the beam is current visible
        self.__visible: bool = False

        # Whether aim button has been pressed to extend the beam
        self.__active: bool = False

        # Current target info containing prim and positions of what the beam
        # is pointing at.
        self.__target_info: Optional[XRTargetInfo] = None

        # Target info of when a button was first pressed
        self.__button_target_info: Optional[XRTargetInfo] = None

        # State of buttons being pressed (set of the names of the buttons)
        self.__buttons: Set[str] = set()

    def __del__(self):
        self.__usd_layer.remove_group(self.__group)

    def get_turn_table_path(self) -> Optional[str]:
        """
        Get the path of where the turn table is located.

        Return:
            path of the turn table prim
        """

        return self.__turn_table_path

    def get_link_path(self) -> Optional[str]:
        """
        Get the path of where the link is located.
        Link connects to the object being manipulated.

        Return:
            path of the link prim
        """

        return self.__link_path

    def create_turn_table_and_link(self, target_usd_path: str) -> None:
        """
        Create the turn table prim and link prim at the end of the beam.
        The link beam is connected to the target_usd_path. This essentially
        grabs an object with the beam.

        Args:
            target_usd_path:        usd prim path to target
        """

        if self.__link_path is not None or self.__turn_table_path is not None:
            carb.log_warn("Turn table was already created")
            return

        self.__turn_table_path = self.__reorient_path + "/turn_table"
        self.__usd_layer.add_transform(self.__turn_table_path, group=self.__group)

        self.__link_path = self.__turn_table_path + "/link"
        self.__usd_layer.add_link(path=self.__link_path, group=self.__group, link_path=target_usd_path)

    def remove_turn_table_and_link(self, commit: bool = True) -> None:
        """
        Remove the turn_table and the link prim. If commit is true, commit
        the pose of the link to the object it targets. This will move the
        prim to that location.

        Args:
            commit: whether to commit the pose in the link to targetted prim
        """
        if self.__usd_layer.is_managed_prim(self.__link_path):
            self.__usd_layer.commit_link_transform(self.__link_path)
            self.__usd_layer.remove(self.__link_path)

        if self.__usd_layer.is_managed_prim(self.__turn_table_path):
            self.__usd_layer.remove(self.__turn_table_path)

        self.__turn_table_path = None
        self.__link_path = None

    def get_length(self) -> float:
        """
        Get the length of the selection beam.

        Return:
            length of selection beam.
        """
        return self.__usd_layer.get_length(self.__beam_path)

    def set_length(self, length: float) -> None:
        """
        Set length of the selection beam. If this is set to -1.0
        the beam adjust the length to the nearest prim.

        Args:
            length:     length of the beam
        """

        self.__usd_layer.set_length(self.__beam_path, length)

    def get_hand(self) -> str:
        """
        Get the hand this beam is connected to. The hand is the name of the
        input device, e.g. /user/hand/left or /user/hand/right

        Return:
            name of input device
        """

        return self.__hand

    def get_target_info(self) -> Optional[XRTargetInfo]:
        """
        Get the target information on what the beam is currently pointing at.
        This includes the prim name, the beam insection point with prim, and the
        normal at that location.

        Return:
            the target information
        """
        return self.__target_info

    def get_button_target_info(self) -> Optional[XRTargetInfo]:
        """
        Get the target information on what the beam was pointing at when the first
        button was pressed. If no button is pressed it will return the current
        target info of what is currently being pointed at.
        This includes the prim name, the beam insection point with prim, and the
        normal at that location.

        Return:
            the target information
        """

        if self.__button_target_info is not None:
            return self.__button_target_info
        else:
            return self.__target_info

    def update_target_info(self) -> None:
        """
        Cache the target information that is available on the beam with the
        latest values.
        """
        self.__target_info = self.__usd_layer.get_target_info(self.__beam_path)

    def add_pressed_button(self, button: str) -> None:
        """
        Indicate that an additional button is pressed.

        Args:
            button: name of the button
        """

        # remember which target to use for button:
        # so button click and release are targetted from the same prim
        if len(self.__buttons) == 0:
            self.__button_target_info = self.__target_info

        self.__buttons.add(button)

    def remove_pressed_button(self, button: str) -> None:
        """
        Indicate that a button was released.

        Args:
            button: name of the button
        """
        self.__buttons.discard(button)

        if len(self.__buttons) == 0:
            self.__button_target_info = None

    def check_button_is_pressed(self, button: str) -> bool:
        """
        Check if button is pressed.

        Args:
            button: name of the button

        Return:
            True if button is pressed
        """

        return button in self.__buttons

    def get_pressed_buttons(self) -> Set[str]:
        """
        Get the list of pressed buttons.

        Return:
            set of pressed buttons
        """

        return self.__buttons

    def check_if_buttons_are_pressed(self) -> bool:
        """
        Check if any buttons are pressed on the beam.

        Return:
            True if any buttons are pressed
        """

        if len(self.__buttons) > 0:
            return True
        return False

    def update_visibility(self) -> None:
        """
        Update the visibility of the beam.
        """

        visible = self.__pointing_at_ui or self.__active

        if visible != self.__visible:
            self.__visible = visible
            if not visible:
                self.__usd_layer.hide(self.__beam_path)
            else:
                self.__usd_layer.show(self.__beam_path)

    def set_active(self, active: bool) -> None:
        """
        Set whether the beam is active (always visible) or deactivated (only visible for ui elements).

        Args:
            active:     True if active
        """

        self.__active = active
        self.update_visibility()

    def set_pointing_at_ui(self, pointing_at_ui: bool) -> None:
        """
        Set whether the beam is currently pointing at an ui element.

        Args:
            pointing_at_ui:     True if pointing at ui
        """

        self.__pointing_at_ui = pointing_at_ui
        self.update_visibility()

    def is_active(self) -> bool:
        """
        Check whether the beam is active (always visible and ready to select).

        Return:
            True if active
        """

        return self.__active

    def is_pointing_at_ui(self) -> bool:
        """
        Check if beam is pointing at ui elements.

        Return:
            True if pointing at ui elements
        """

        return self.__pointing_at_ui

    def is_visible(self) -> bool:
        """
        Check if the beam is visible current.

        Return:
            True if pointing at ui elements
        """

        return self.__visible

    def get_beam_pose(self) -> Gf.Matrix4d:
        """
        Get the pose of the beam.
        """
        return self.__usd_layer.get_transform(self.__beam_path, XRTransformType.stage)

    def get_beam_end_pose(self) -> Gf.Matrix4d:
        """
        Get the pose of the end of the beam.
        """
        return self.__usd_layer.get_transform(self.__end_path, XRTransformType.stage)
