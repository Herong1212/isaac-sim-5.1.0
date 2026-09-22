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

__all__ = ["XRInputDeviceModel"]

from ..._xrcore import XRInputDeviceModel_Internal, XRToken

# =================================================
# This file constructs a shim for the C++
# functionality exposed into python and adds
# types, type conversions, documentation, and
# improved python integration for these functions.
# =================================================

# ================================================
# XRInputDeviceModel class wrapper
# ================================================

# pylint: disable=protected-access
# noinspection PyProtectedMember


class XRInputDeviceModel:
    def __init__(self, internal: XRInputDeviceModel_Internal):
        self.__internal: XRInputDeviceModel_Internal = internal

    def __eq__(self, other) -> bool:
        if isinstance(other, XRInputDeviceModel):
            return self.__internal == other.__internal
        return False

    def __hash__(self):
        return self.__internal.__hash__()

    def _get_internal(self) -> XRInputDeviceModel_Internal:
        return self.__internal

    def get_name(self) -> XRToken:
        """
        Get the name of the input device model.

        Return:
            XRToken with name
        """
        return self.__internal.get_name()

    def get_asset(self) -> XRToken:
        """
        Get the asset name of the input device model.

        Return:
            XRToken with asset name
        """
        return self.__internal.get_asset()

    def get_input_device_tags(self) -> dict[str, int]:
        """
        Get the input device tags this model is connected to.

        Return:
            Dictionary with tags and their corresponding priority
        """
        return self.__internal.get_input_device_tags()

    def get_input_device_names(self) -> tuple[XRToken]:
        """
        Get the input device names this input device model is valid for.

        Return:
            List with XRTokens
        """
        return self.__internal.get_input_device_names()
