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

import omni.kit.menu.utils
from omni.kit.xr.core import XRCore, XRCoreEventType, XRSingleton, XRSingletonType, XRWeakMethod


@XRSingleton()
class XRDisableSave(XRSingletonType):
    _profiles: set

    def __init__(self) -> None:

        # Intercept menu creation to make save menu action check if XR is active
        omni.kit.menu.utils.add_hook(XRDisableSave._menu_disable_save_intercept_hook)

        # Subscribe to XR enable/disable events to refresh the menu so the "Save" items are properly enabled/disabled
        self.__subs: Optional[dict] = {}

        refresh_menu_fn = XRWeakMethod(self._refresh_menu)

        self.__subs["xr_profile_changed"] = (
            XRCore.get_singleton()
            .get_message_bus()
            .create_subscription_to_pop_by_type(XRCoreEventType.profile_changed, refresh_menu_fn)
        )

    def destroy(self) -> None:

        # Remove the save intercept hook
        omni.kit.menu.utils.remove_hook(XRDisableSave._menu_disable_save_intercept_hook)
        self.__subs = None

    def add_profile(self, name: str) -> None:
        XRDisableSave._add_profile(name)

    def remove_profile(self, name: str) -> None:
        XRDisableSave._remove_profile(name)

    @classmethod
    def _add_profile(cls, name: str) -> None:
        if not hasattr(cls, "_profiles"):
            cls._profiles = set()
        cls._profiles.add(name)

    @classmethod
    def _remove_profile(cls, name: str) -> None:
        if not hasattr(cls, "_profiles"):
            cls._profiles = set()
        cls._profiles.discard(name)

    @classmethod
    def _save_enable_check_fn(cls) -> bool:
        # Used by menu items and the wrapper function below to determine if saving is allowed
        xr_core = XRCore.get_singleton()
        if xr_core is None:
            return True

        if not hasattr(cls, "_profiles"):
            return True

        if xr_core.get_current_profile_name() in cls._profiles:
            return False

        return True

    @classmethod
    def _menu_disable_save_intercept_hook(cls, merged_menu):
        # Setup save menu items to be disabled when saving is not allowed
        # and wrap their actions in checks to prevent saving if not allowed

        save_items = ["Save", "Save With Options", "Save As...", "Save Flattened As..."]
        if "File" in merged_menu:
            for index, menu_entry in enumerate(merged_menu["File"]):
                if menu_entry.name in save_items:
                    if menu_entry.enable_fn is None:
                        menu_entry.enable_fn = []
                    if type(menu_entry.enable_fn) is not list:
                        menu_entry.enable_fn = [menu_entry.enable_fn]
                    if cls._save_enable_check_fn not in menu_entry.enable_fn:
                        menu_entry.enable_fn.append(cls._save_enable_check_fn)

    def _refresh_menu(self, ev):
        # Force menus to refresh on XR enable/disable
        omni.kit.menu.utils.rebuild_menus()
