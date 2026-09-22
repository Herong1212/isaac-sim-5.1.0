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

__all__ = ["XRActionMap"]

from ..._xrcore import XRActionMap_Internal, XRActionMapRecord, XRToken

# =================================================
# This file constructs a shim for the C++
# functionality exposed into python and adds
# types, type conversions, documentation, and
# improved python integration for these functions.
# =================================================

# ================================================
# XRActionMap class wrapper
# ================================================

# pylint: disable=protected-access
# noinspection PyProtectedMember


class XRActionMap:
    def __init__(self, internal: XRActionMap_Internal):
        self.__internal: XRActionMap_Internal = internal

    def __eq__(self, other) -> bool:
        if isinstance(other, XRActionMap):
            return self.__internal == other.__internal
        return False

    def __hash__(self):
        return self.__internal.__hash__()

    def _get_internal(self) -> XRActionMap_Internal:
        return self.__internal

    def get_name(self) -> XRToken:
        """
        Get the name of the action map.

        Return:
            XRToken with name
        """
        return self.__internal.get_name()

    def get_input_device_tags(self) -> tuple[XRToken]:
        """
        Get the input device tags.

        Return:
            Dictionary with acceptable input device tags per input device name
        """
        return self.__internal.get_input_device_tags()

    def get_tool_layout(self) -> XRToken:
        """
        Get the tool layout.

        Return:
            XRToken with controller layout name
        """
        return self.__internal.get_tool_layout()

    def get_dominant_hand(self) -> XRToken:
        """
        Get the dominant hand.

        Return:
            XRToken with dominant hand name
        """
        return self.__internal.get_dominant_hand()

    def get_tool_list(self) -> tuple[XRToken]:
        """
        Get list of tools for this action map.

        Return:
            List of tool names
        """
        return self.__internal.get_tool_list()

    def get_action_map(self) -> tuple[XRActionMapRecord]:
        """
        Get the action map records that map event name to input device components.

        Return:
            List of records
        """
        return self.__internal.get_action_map()
