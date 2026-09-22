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
# Use these at your own risk, and forward-compatability is not supported

__all__ = ["XRInputDevice", "XRPoseValidityFlags", "XRPoseDesc", "XR_INPUT_DEVICE_HAND_TRACKING_POSE_NAMES"]

import enum
from typing import Iterable, Optional, Union

from pxr import Gf

from ..._xrcore import XR_INPUT_DEVICE_HAND_TRACKING_POSE_NAMES, XRInputDevice_Internal, XRPoseDesc_Internal, XRToken
from .xreventgenerator_class_wrapper import XREventGenerator
from .xrinputdevicemodel_class_wrapper import XRInputDeviceModel

# =================================================
# This file constructs a shim for the C++
# functionality exposed into python and adds
# types, type conversions, documentation, and
# improved python integration for these functions.
# =================================================

# ================================================
# XRInputDevice class wrapper
# ================================================

# pylint: disable=protected-access
# noinspection PyProtectedMember


class XRPoseValidityFlags(enum.IntFlag):
    ORIENTATION_VALID = 0x00000001
    POSITION_VALID = 0x00000002
    ORIENTATION_TRACKED = 0x00000004
    POSITION_TRACKED = 0x00000008


class XRPoseDesc:
    pose_matrix: Gf.Matrix4d
    validity_flags: XRPoseValidityFlags

    def __init__(self, internal: XRPoseDesc_Internal):
        self.pose_matrix = Gf.Matrix4d(*internal.pose_matrix)
        self.validity_flags = XRPoseValidityFlags(internal.validity_flags)


class XRInputDevice:
    def __init__(self, internal: XRInputDevice_Internal):
        self.__internal: XRInputDevice_Internal = internal

    def __eq__(self, other) -> bool:
        if isinstance(other, XRInputDevice):
            return self.__internal == other.__internal
        return False

    def __hash__(self):
        return self.__internal.__hash__()

    def _get_internal(self) -> XRInputDevice_Internal:
        return self.__internal

    def get_name(self) -> XRToken:
        """
        Get the name of the input device.

        Return:
            XRToken with name
        """
        return self.__internal.get_name()

    def get_type(self) -> XRToken:
        """
        Get the type of the input device.

        Return:
            XRToken with type
        """
        return self.__internal.get_type()

    def ensure_pose(self, pose_name: Union[XRToken, str]) -> None:
        """
        Ensure that a pose with a given name is defined.

        Args:
            pose_name: name of the pose
        """
        self.__internal.ensure_pose(pose_name)

    def remove_pose(self, pose_name: Union[XRToken, str]) -> None:
        """
        Remove pose identified by name.

        Args:
            pose_name: name of the pose
        """
        self.__internal.remove_pose(pose_name)

    def has_pose(self, pose_name: Union[XRToken, str]) -> bool:
        """
        Check if input device has pose with given name.

        Args:
            pose_name: name of the pose
        """
        return self.__internal.has_pose(pose_name)

    def get_raw_pose(self, pose_name: Union[XRToken, str] = "") -> Gf.Matrix4d:
        """
        Get raw (unfiltered) pose of the input device.

        Args:
            pose_name: name of the pose

        Return:
            Matrix
        """
        return Gf.Matrix4d(*self.__internal.get_raw_pose(pose_name))

    def get_raw_pose_desc(self, pose_name: Union[XRToken, str] = "") -> XRPoseDesc:
        """
        Get raw (unfiltered) pose of the input device.

        Args:
            pose_name: name of the pose
        """
        return XRPoseDesc(self.__internal.get_raw_pose_desc(pose_name))

    def get_pose(self, pose_name: Union[XRToken, str] = "") -> Gf.Matrix4d:
        """
        Get pose of the input device (this may be smoothed).

        Args:
            pose_name: name of the pose

        Return:
            Matrix
        """
        return Gf.Matrix4d(*self.__internal.get_pose(pose_name))

    def get_pose_desc(self, pose_name: Union[XRToken, str] = "") -> XRPoseDesc:
        """
        Get full pose data for a pose on the input device.

        Args:
            pose_name: name of the pose

        Return:
            XRPoseDesc
        """
        return XRPoseDesc(self.__internal.get_pose_desc(pose_name))

    def set_pose_desc(self, pose_name: Union[XRToken, str], pose: XRPoseDesc) -> None:
        """
        Set full pose data for a pose on the input device.

        Args:
            pose_name: name of the pose
            pose: XRPoseDesc
        """
        pose_desc = XRPoseDesc_Internal(pose_name, pose.pose_matrix, pose.validity_flags)
        return self.__internal.set_pose_desc(pose_name, pose_desc)

    def set_pose(
        self, pose_name: Union[XRToken, str], pose: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]]
    ) -> None:
        """
        Set pose in physical device coordinates.

        Args:
            pose_name: name of the pose
            pose: pose of the component as a matrix
        """
        return self.__internal.set_pose(pose_name, pose)

    def get_virtual_world_pose(self, pose_name: Union[XRToken, str] = "") -> Gf.Matrix4d:
        """
        Get pose in the virtual world of the input device.

        Args:
            pose_name: name of the pose

        Return:
            Matrix
        """
        return Gf.Matrix4d(*self.__internal.get_virtual_world_pose(pose_name))

    def get_virtual_world_pose_desc(self, pose_name: Union[XRToken, str] = "") -> XRPoseDesc:
        """
        Get full pose data in the virtual world space.

        Args:
            pose_name: name of the pose
        """
        return XRPoseDesc(self.__internal.get_virtual_world_pose_desc(pose_name))

    def get_pose_names(self) -> list[XRToken]:
        """
        Get pose names available on this input device.

        Return:
            List of pose names
        """
        return self.__internal.get_pose_names()

    def get_all_poses(self) -> dict[str, XRPoseDesc]:
        """
        Get poses available on this input device.

        Return:
            Dictionary with pose names as keys and pose values as values
        """
        return {poseName: XRPoseDesc(pose) for poseName, pose in self.__internal.get_all_poses().items()}

    def get_all_raw_poses(self) -> dict[str, XRPoseDesc]:
        """
        Get raw poses available on this input device.

        Return:
            Dictionary with pose names as keys and pose values as values
        """
        return {poseName: XRPoseDesc(pose) for poseName, pose in self.__internal.get_all_raw_poses().items()}

    def get_all_virtual_world_poses(self) -> dict[str, XRPoseDesc]:
        """
        Get virtual world poses available on this input device.

        Return:
            Dictionary with pose names as keys and pose values as values
        """
        return {poseName: XRPoseDesc(pose) for poseName, pose in self.__internal.get_all_virtual_world_poses().items()}

    def ensure_input_gesture(
        self,
        input_name: Union[XRToken, str],
        gesture_name: Union[XRToken, str],
        source_name: Union[XRToken, str] = "",
    ) -> None:
        """
        Ensure that a gesture for a given input component is reserved.

        Args:
            input_name: name of the component
            gesture_name: name of the gesture
            source_name: name of the source managing the gesture values
        """
        self.__internal.ensure_gesture(gesture_name, input_name, source_name)

    def remove_input_gesture(self, input_name: Union[XRToken, str], gesture_name: Union[XRToken, str]) -> None:
        """
        Remove gesture identified by input component name and gesture name.

        Args:
            input_name: name of the input component
            gesture_name: name of the gesture
        """
        self.__internal.remove_input_gesture(input_name, gesture_name)

    def remove_input_gestures_by_source(self, source_name: Union[XRToken, str]) -> None:
        """
        Remove input gestures identified by source token.

        Args:
            source_name: name of the source managing the gesture values
        """
        self.__internal.remove_input_gestures_by_source(source_name)

    def get_input_gesture_source(self, input_name: Union[XRToken, str], gesture_name: Union[XRToken, str]) -> XRToken:
        """
        Get the source of a gesture of a input component.

        Args:
            input_name: name of the input component
            gesture_name: name of the gesture
        """
        return self.__internal.get_input_gesture_source(input_name, gesture_name)

    def has_input(self, input_name: Union[XRToken, str]) -> bool:
        """
        Check if input device has an input component.

        Args:
            input_name: name of the input component

        Return:
            True if input component is present in input device
        """
        return self.__internal.has_input(input_name)

    def has_input_gesture(self, input_name: Union[XRToken, str], gesture_name: Union[XRToken, str]) -> bool:
        """
        Check if input device has given input gesture.

        Args:
            input_name: name of the input component
            gesture_name: name of the input gesture

        Return:
            True if input component is present in input device
        """
        return self.__internal.has_input_gesture(input_name, gesture_name)

    def set_input_base(self, input_name: Union[XRToken, str], base_input_name: Union[XRToken, str]) -> None:
        """
        Set the base input component for an input component.

        Args:
            input_name: input component for which to set base input component
            base_input_name: the input component this one is based on
        """
        self.__internal.set_input_base(input_name, base_input_name)

    def get_input_base(self, input_name: Union[XRToken, str]) -> XRToken:
        """
        Get the base input component for an input component.

        Args:
            component_name: input component for which to get base input component

        Return:
            the base input component token
        """
        return self.__internal.get_input_base(input_name)

    def has_input_base(self, input_name: Union[XRToken, str]) -> bool:
        """
        Get the base component for an input component.

        Args:
            input_name: input component for which to get base input component

        Return:
            the base input component token
        """
        return self.__internal.has_input_base(input_name)

    def get_overlapping_inputs(self, input_name: Union[XRToken, str]) -> list[XRToken]:
        """
        Get the input components that overlap with a given input component.

        Args:
            input_name: the component for which to find overlapping inputs

        Return:
            list of overlapping inputs
        """
        return self.__internal.get_overlapping_inputs(input_name)

    def get_input_gesture_names(self, input_name: Union[XRToken, str]) -> list[XRToken]:
        """
        Get list of gesture names available on this input device for a specific input component.

        Return:
            List of input gesture names
        """
        return self.__internal.get_input_gesture_names(input_name)

    def get_input_names(self) -> list[XRToken]:
        """
        Get list of input component names on this input device.

        Return:
            List of input component names
        """
        return self.__internal.get_input_names()

    def set_input_gesture_value(
        self, input_name: Union[XRToken, str], gesture_name: Union[XRToken, str], value: float
    ) -> None:
        """
        Set the value of an input gesture.

        Args:
            gesture_name: token for the gesture
            value: value to set
        """
        self.__internal.set_input_gesture_value(input_name, gesture_name, value)

    def get_input_gesture_value(self, input_name: Union[XRToken, str], gesture_name: Union[XRToken, str]) -> float:
        """
        get the value of an input gesture.

        Args:
            gesture_name: token for the gesture

        Return:
            value of the gesture
        """
        return self.__internal.get_input_gesture_value(input_name, gesture_name)

    def get_hand_tracking_data_source(self) -> XRToken:
        """
        Get the hand tracking data source of the input device.  This will be empty if this is not a
        hand, or if hand tracking is not active.  If an unobstructed hand is being tracked, this
        will return "hand".  If the hand is holding a controller, this will return "controller".


        Return:
            XRToken with hand tracking data source
        """
        return self.__internal.get_hand_tracking_data_source()

    def get_model(self) -> Optional[XRInputDeviceModel]:
        """
        Get the model that is suggested to use for this input device.

        return:
            XRInputDeviceModel or None
        """
        model = self.__internal.get_model()
        if model is None:
            return None
        return XRInputDeviceModel(self.__internal.get_model())

    def ensure_output(self, output_name: Union[XRToken, str]) -> None:
        """
        Ensure that a given output component is available on the input device.

        Args:
            component_name: output token
        """
        self.__internal.ensure_output(output_name)

    def remove_output(self, output_name: Union[XRToken, str]) -> None:
        """
        Remove an output componentfrom the input device.

        Args:
            component_name: output token
        """
        self.__internal.remove_output(output_name)

    def has_output(self, output_name: Union[XRToken, str]) -> bool:
        """
        Check whether input device is a certain output component.

        Args:
            component_name: output token
        """
        return self.__internal.has_output(output_name)

    def set_output_value(self, output_name: Union[XRToken, str], value: float) -> None:
        """
        Set the value of an output (haptic feedback).

        Args:
            component_name: output token
            value: value of output
        """
        self.__internal.set_output_value(output_name, value)

    def get_output_value(self, output_name: Union[XRToken, str]) -> float:
        """
        Get the value of an output (haptic feedback).

        Args:
            component_name: output token

        Return:
            current value of output
        """
        return self.__internal.get_output_value(output_name)

    def get_output_names(self) -> list[XRToken]:
        """
        Get list of output names available for this input device.

        Return:
            List of output names
        """
        return self.__internal.get_output_names()

    def bind_event_generator(
        self,
        input_name: Union[XRToken, str],
        event_name: Union[XRToken, str],
        event_list: Iterable[Union[XRToken, str]],
        tooltips: Union[dict[str, str], str] = {},
    ) -> Optional[XREventGenerator]:
        """
        Bind an event generator to an input component. This returns a subscription that will ensure that
        you have an event stream until the subscription is deleted.

        Args:
            input_name: input component to bind the event generator to
            event_name: name of the event that needs to be generated
            event_list: tuple with names of events that need to be generated (e.g press, release, etc)

        Return:
            event generator object
        """

        if isinstance(tooltips, str):
            tooltips = {"click": tooltips}

        event_generator = self.__internal.bind_event_generator(input_name, event_name, event_list, tooltips)
        if event_generator is None:
            return None
        return XREventGenerator(event_generator)

    def unbind_event_generator(self, event_name: Union[XRToken, str]) -> None:
        """
        Unbind event generator.

        Args:
            event_name: name of the event that the event generator generates
        """
        self.__internal.unbind_event_generator(event_name)

    def has_event_generator(self, input_name: Union[XRToken, str]) -> bool:
        """
        Check if an event generator is bound to an input component.

        Args:
            input_name: input component to check

        Return:
            True if event generator is bound
        """
        return self.__internal.has_event_generator(input_name)

    def get_input_tooltips(self, input_name: Union[XRToken, str]) -> dict[str, str]:
        """
        Get the tooltips for a given input component.

        Args:
            input_name: input component to check

        Return:
            Dictionary with tooltips (description listed by sub component key)
        """
        return self.__internal.get_input_tooltips(input_name)
