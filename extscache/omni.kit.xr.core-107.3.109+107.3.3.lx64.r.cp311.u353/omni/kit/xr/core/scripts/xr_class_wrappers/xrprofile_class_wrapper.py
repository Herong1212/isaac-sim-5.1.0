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


from typing import Any, Iterable, Optional, Union

import carb
from omni.kit.app import deprecated
from pxr import Gf

from ..._xrcore import XRProfile_Internal
from .xrprofile_ar_mode import XRProfileARMode

# =================================================
# This file constructs a shim for the C++
# functionality exposed into python and adds
# types, type conversions, documentation, and
# improved python integration for these functions.
# =================================================

# ================================================
# XRProfile class extensions
# ================================================


# pylint: disable=protected-access
# noinspection PyProtectedMember


class XRProfileInternalData:
    def __init__(self):
        self.ar_mode = XRProfileARMode()
        self.persistence_prefix = "/xr"

        if carb.settings.get_settings().get("/xr/persistence/enabled") is True:
            self.persistence_prefix = "/persistent/xr"

        self.config = {}


class XRProfile:
    _internal_data: dict[str, Any] = {}

    def __init__(self, internal: XRProfile_Internal = None):
        if internal is None:
            self.__internal: XRProfile_Internal = XRProfile_Internal()
        else:
            self.__internal = internal

        if internal.get_name() in XRProfile._internal_data:
            self.__internal_data = XRProfile._internal_data[internal.get_name()]
        else:
            self.__internal_data = XRProfileInternalData()
            XRProfile._internal_data[internal.get_name()] = self.__internal_data

    def __eq__(self, other):
        if isinstance(other, XRProfile):
            return self.__internal == other.__internal
        return False

    def __hash__(self):
        return self.__internal.__hash__()

    def _get_internal(self) -> XRProfile_Internal:
        return self.__internal

    def get_name(self) -> str:
        """
        This function gets the name of this XRProfile.

        Return:
            name of this XRProfile as string
        """
        return self.__internal.get_name()

    def request_enable_profile(self) -> None:
        """
        This function requests that this XRProfile is switched to active.
        """
        self.__internal.request_enable_profile()

    def is_enabled(self) -> bool:
        """
        This function checks if this XRProfile is currently active.

        Return:
             True if this profile is active, else False
        """
        return self.__internal.is_enabled()

    def get_persistent_path(self) -> str:
        """
        This function returns the persistent settings path to the profile.

        Return:
                Settings path to location of persistent parameters
        """
        return self.__internal_data.persistence_prefix + "/profile/" + self.__internal.get_name() + "/"

    def get_non_persistent_path(self) -> str:
        """
        This function returns the non-persistent settings path to the profile.

        Return:
            Settings path to location of persistent parameters
        """
        return "/xr/profile/" + self.__internal.get_name() + "/"

    def get_scene_persistent_path(self) -> str:
        """
        This function returns the scene-persistent settings path to the profile.

        Return:
            Settings path to location of persistent parameter
        """
        return "/xrstage/profile/" + self.__internal.get_name() + "/"

    def get_temp_path(self) -> str:
        """
        This function returns the runtime temp settings path to the profile.

        Return:
            Settings path to location of persistent parameters
        """
        return "/tmp/xr/profile/" + self.__internal.get_name() + "/"

    def get_ar_mode(self) -> bool:
        """
        This function gets current AR mode.
        """
        return self.__internal_data.ar_mode.get_ar_mode()

    def set_ar_mode(self, ar_mode) -> None:
        """
        This function sets AR mode.
        """
        self.__internal_data.ar_mode.set_ar_mode(ar_mode, self)

    def _update_settings_ar(self) -> None:
        """
        Called on activation
        """
        self.__internal_data.ar_mode.update_settings_ar(self)

    def _reset_settings_ar(self) -> None:
        self.__internal_data.ar_mode.reset_settings_ar()

    def set_config(self, config: Any) -> None:
        """
        Set configuration for the menu of this profile.

        Args:
            config:    configuration of the menu
        """
        self.__internal_data.config = config

    def get_config(self) -> Any:
        """
        Get configuration for the menu of this profile.

        Return:
            configuration
        """

        return self.__internal_data.config

    @deprecated("Please use XRCore.get_singleton().schedule_set_space_origin instead. Function to be removed.")
    def teleport(self, transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]]) -> None:
        """
        This function created to maintain backwards compatibility with earlier api.
        It will eventually be deprecated. Please convert to using XRCore.get_singleton().schedule_set_space_origin instead.
        """
        from .xrcore_class_wrapper import XRCore

        XRCore.get_singleton().schedule_set_space_origin(transform)
