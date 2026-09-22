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

__all__ = ["XRSystem"]

from typing import Any

from ..._xrcore import XRSystem_Internal

# =================================================
# This file constructs a shim for the C++
# functionality exposed into python and adds
# types, type conversions, documentation, and
# improved python integration for these functions.
# =================================================

# ================================================
# XRSystem class wrapper
# ================================================

# pylint: disable=protected-access
# noinspection PyProtectedMember


class XRSystem:
    def __init__(self, internal: XRSystem_Internal):
        self.__internal: XRSystem_Internal = internal

    def __eq__(self, other) -> bool:
        if isinstance(other, XRSystem):
            return self.__internal == other.__internal
        return False

    def __hash__(self):
        return self.__internal.__hash__()

    def _get_internal(self) -> XRSystem_Internal:
        return self.__internal

    def get_name(self) -> str:
        """
        Get the name of the system.

        Return:
            name of the system
        """
        return self.__internal.get_name()

    def get_modes(self) -> list[str]:
        """
        Get the list of modes supported by a given system.
        A mode is specific way of running a system, e.g. HmdVR or HmdAR

        Return:
            List of modes
        """
        return self.__internal.get_modes()

    def has_mode(self, modeName: str) -> bool:
        """
        Check if a given mode is supported by a system.
        A mode is specific way of running a system, e.g. HmdVR or HmdAR

        Args:
        modeName    name of the mode

        Return:
            True if mode is supported
        """
        return self.__internal.get_mode(modeName)

    def get_meta_data(self, key: str, default: Any) -> Any:
        """
        Get an entry out of the meta data

        Args:
        modeName    name of the mode

        Return:
            True if mode is supported
        """

        dict = self.__internal.get_meta_data_dictionary()
        return dict.get(key, default)
