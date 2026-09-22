"""
Simple helper class for adding/removing "Window" menu to your extension. ui.Window creation/show/hide is still down to user to provide functionally.
"""

# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
# pylint: disable=redefined-outer-name
import carb
import omni.ext
import omni.kit.menu.utils
import omni.ui as ui

from .builder_utils import MenuItemDescription
from .extension_window_helper_full import registered_windows


# only handle menus, window show/hide is done by extension
class MenuHelperExtension:
    """
    Simple helper class for adding/removing "Window" menu to your extension. ui.Window creation/show/hide is still down to user to provide functionally.
    """

    def __init__(self):
        super().__init__()
        self._verbose = False
        self._window_name = None
        self._menu_desc = None
        self._menu_group = None
        self._menu_entry = None
        self.__extension_id = None
        self.__action_name = None

    def __get_action_name(self, menu_path):
        import re

        action = (
            re.sub(r"[^\x00-\x7F]", "", menu_path)
            .lower()
            .strip()
            .replace("/", "_")
            .replace(" ", "_")
            .replace("__", "_")
        )
        return (self.__class__.__module__, f"menu_toggle_window_helper_{action}")

    def __register_window(self, window_name):
        if window_name in registered_windows:
            carb.log_error(
                f'menu_startup: window "{window_name}" already registered by {registered_windows[window_name]}'
            )
            return False

        registered_windows[window_name] = "unknown"
        return True

    def __unregister_window(self, window_name):
        if window_name in registered_windows:
            del registered_windows[window_name]

    # setup menu
    def menu_startup(self, window_name, menu_desc, menu_group, appear_after="", header=None, verbose=False) -> bool:
        import omni.kit.actions.core

        if verbose:
            print("[MenuHelperWindow] menu_startup")

        if hasattr(self, "_menu_entry") and self._menu_entry is not None:
            carb.log_warn("[MenuHelperWindow] menu_startup already called")
            return False

        if not self.__register_window(window_name):
            return False

        self._verbose = verbose
        self._window_name = window_name
        self._menu_desc = menu_desc
        self._menu_group = menu_group
        self._menu_entry = None

        # setup action
        self.__extension_id, self.__action_name = self.__get_action_name(self._menu_desc)

        if omni.kit.actions.core.get_action_registry().get_action(self.__extension_id, self.__action_name):
            carb.log_error(
                f"[MenuHelperWindow] menu_startup action already registered. {self.__extension_id} {self.__action_name}"
            )
        else:
            self.__extension_id, self.__action_name = self.__get_action_name(self._menu_desc)
            omni.kit.actions.core.get_action_registry().register_action(
                self.__extension_id,
                self.__action_name,
                lambda v=verbose, w=window_name: MenuHelperExtension._toggle_window(v, w),
                display_name=self.__action_name,
                description=self.__action_name,
                tag=self.__action_name,
            )
        # setup menu
        self._menu_entry = [
            MenuItemDescription(
                name=self._menu_desc,
                ticked=True,  # menu item is ticked
                ticked_fn=lambda v=verbose, w=window_name: MenuHelperExtension._is_visible(
                    v, w
                ),  # gets called when the menu needs to get the state of the ticked menu
                appear_after=appear_after,
                onclick_action=(self.__extension_id, self.__action_name),
                header=header,
            )
        ]
        omni.kit.menu.utils.add_menu_items(self._menu_entry, name=self._menu_group)
        return True

    # remove menu
    def menu_shutdown(self) -> bool:
        if self._verbose:
            print("[MenuHelperWindow] on_shutdown")

        if not hasattr(self, "_menu_entry") or self._menu_entry is None:
            return False

        # destroy action
        omni.kit.actions.core.get_action_registry().deregister_action(self.__extension_id, self.__action_name)

        # unregister window
        self.__unregister_window(self._window_name)

        # destroy menu
        omni.kit.menu.utils.remove_menu_items(self._menu_entry, name=self._menu_group)
        self._menu_entry = None

        return True

    # window was open/closed, refresh_menu_items
    def menu_refresh(self):
        if self._menu_entry:
            # this only tags test menu to update when menu is opening, so it
            # doesn't matter that is called before window has been destroyed
            omni.kit.menu.utils.refresh_menu_items(self._menu_group)

    # is window visible
    @staticmethod
    def _is_visible(verbose, window_name) -> bool:
        if verbose:
            print("[ExtensionMenuHelper] _is_visible")
        window = ui.Workspace.get_window(window_name)
        if window is None or type(window) == ui.WindowHandle:  # pylint: disable=unidiomatic-typecheck
            return False
        return window.visible

    # toggle window visibility
    @staticmethod
    def _toggle_window(verbose, window_name):
        if verbose:
            print("[ExtensionMenuHelper] _toggle_window")

        ui.Workspace.show_window(window_name, not MenuHelperExtension._is_visible(verbose, window_name))
