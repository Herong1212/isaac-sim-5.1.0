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

__all__ = ["XREventGenerator"]

from ..._xrcore import XREventGenerator_Internal, XRToken

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


class XREventGenerator:
    def __init__(self, internal: XREventGenerator_Internal):
        self.__internal: XREventGenerator_Internal = internal

    def __eq__(self, other) -> bool:
        if isinstance(other, XREventGenerator):
            return self.__internal == other.__internal
        return False

    def __hash__(self):
        return self.__internal.__hash__()

    def _get_internal(self) -> XREventGenerator_Internal:
        return self.__internal

    def get_event_name(self) -> XRToken:
        """
        Get the event name of that this generator creates.

        Return:
            XRToken with event name
        """
        return self.__internal.get_event_name()

    def get_input_device_name(self) -> XRToken:
        """
        Get the name the input device that this generator creates events for.

        Return:
            XRToken with input device name
        """
        return self.__internal.get_input_device_name()

    def get_component_name(self) -> XRToken:
        """
        Get the name of the component on the input device that generator creates events for.

        Return:
            XRToken with component name
        """
        return self.__internal.get_component_name()

    def get_event_list(self) -> list[XRToken]:
        """
        Get the name of the component on the input device that generator creates events for.

        Return:
            list of tokens with events to generate
        """
        return self.__internal.get_event_list()

    def set_auto_unbind(self, auto_unbind: bool) -> None:
        """
        Set whether the destruction of this object causes the event generator to unbind.

        Args:
            auto_unbind   boolean indicating whether the event generator needs an automatic unbind.
        """
        self.__internal.set_auto_unbind(auto_unbind)
