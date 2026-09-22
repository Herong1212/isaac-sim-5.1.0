# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ConsoleExtension", "get_instance"]

import asyncio
from typing import Optional

import carb.settings
import omni.ext
import omni.ui as ui
from omni.kit.menu.utils import MenuHelperExtension

from .console_window import ConsoleWindow

_extension_instance = None

STARTUP_SHOW_WINDOW = "/exts/omni.kit.window.console/startup/show_window"


class ConsoleExtension(omni.ext.IExt, MenuHelperExtension):
    """The entry point for Console Window

    This class handles the initialization and management of the Console Window in the application. It integrates with the UI workspace to show or hide the window based on user actions and settings.
    """

    WINDOW_NAME = "Console"
    MENU_GROUP = "Window"

    def on_startup(self, ext_id):
        self.__ext_id = omni.ext.get_extension_name(ext_id)
        self._window: Optional[ConsoleWindow] = None

        """Handles tasks required during startup."""
        ui.Workspace.set_show_window_fn(ConsoleExtension.WINDOW_NAME, self.show_window)
        self.menu_startup(ConsoleExtension.WINDOW_NAME, ConsoleExtension.WINDOW_NAME, ConsoleExtension.MENU_GROUP)

        carb.settings.get_settings().set_default_bool(STARTUP_SHOW_WINDOW, True)
        if carb.settings.get_settings().get_as_bool(STARTUP_SHOW_WINDOW):
            ui.Workspace.show_window(ConsoleExtension.WINDOW_NAME)

        global _extension_instance
        _extension_instance = self

    def on_shutdown(self):
        self.menu_shutdown()
        if self._window:
            self._window.destroy()
            self._window = None

        ui.Workspace.set_show_window_fn(ConsoleExtension.WINDOW_NAME, None)

        global _extension_instance
        _extension_instance = None

    async def _destroy_window_async(self):
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._window:
            self._window.destroy()
            self._window = None

    def _visibility_changed_fn(self, visible):
        self.menu_refresh()
        if not visible:
            # Destroy the window, since we are creating new window
            # in show_window
            asyncio.ensure_future(self._destroy_window_async())

    def show_window(self, value):
        """Shows or hides the console window.

        Args:
            value (bool): Whether to show the window.
        """
        if value:
            self._window = ConsoleWindow()
            self._window.set_visibility_changed_listener(self._visibility_changed_fn)
        elif self._window:
            self._window.visible = False

def get_instance():
    global _extension_instance
    return _extension_instance
