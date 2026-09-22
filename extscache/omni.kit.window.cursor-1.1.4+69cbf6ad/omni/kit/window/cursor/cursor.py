# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides functionalities to manage custom cursor shapes within the main application window, including registering and unregistering custom cursor shapes, overriding cursor shapes, and resolving icon paths."""


import os
import carb
import carb.settings
from pathlib import Path
from carb import windowing, log_warn
from carb.eventdispatcher import get_eventdispatcher
import omni.ext
import weakref
from typing import Optional

main_window_cursor = None


class WindowCursor(omni.ext.IExt):
    """A class responsible for managing custom cursor shapes within the main application window.

    This extension class interacts with the application's window and the imgui renderer to register, unregister, override, and retrieve cursor shapes. It maintains a mapping of custom cursor names to their respective image paths. On startup, it initializes this mapping and registers any additional cursor shapes provided. On shutdown, it unregisters these cursor shapes and cleans up resources.

    If the application or imgui renderer is not ready, the methods will fail gracefully.
    """
    
    def on_startup(self, ext_id):
        """Initializes cursor shapes on startup.

        Args:
            ext_id (str): Extension ID."""
        self._imgui_renderer = None
        self._app_window = None
        global main_window_cursor
        main_window_cursor = weakref.proxy(self)

        try:
            import omni.kit.imgui_renderer
            import omni.appwindow

            self._imgui_renderer = omni.kit.imgui_renderer.acquire_imgui_renderer_interface()
            self._app_window = omni.appwindow.get_default_app_window()
        except Exception:
            # Currently need both of these for further API usage, which can't happen now; so clear them both out
            self._imgui_renderer, self._app_window = None, None
            log_warn("omni.kit.window.cursor failed to initialize properly, changing cursor with it will not work")

        self._cursor_shapes = {}
        settings = carb.settings.get_settings()
        for name, path in settings.get_settings_dictionary("/exts/omni.kit.window.cursor/cursors").get_dict().items():
            self._cursor_shapes[name] = carb.tokens.get_tokens_interface().resolve(path)

        app = omni.kit.app.get_app()
        if not app.is_app_ready():
            self._app_ready_sub = get_eventdispatcher().observe_event(
                event_name=omni.kit.app.GLOBAL_EVENT_APP_READY,
                on_event=lambda _: self._register_extra_cursors(),
                observer_name="omni.kit.window.cursor"
            )
        else:
            self._register_extra_cursors()

    def on_shutdown(self):
        """Cleans up resources on shutdown."""
        if self._imgui_renderer:
            for name in self._cursor_shapes.keys():
                self.unregister_cursor_shape_extend(name)

        global main_window_cursor
        main_window_cursor = None

        self._imgui_renderer = None
        self._app_window = None
        self._app_ready_sub = None

    def _register_extra_cursors(self):
        if self._imgui_renderer:
            for name, path in self._cursor_shapes.items():
                self.register_cursor_shape_extend(name, path)

    def register_cursor_shape_extend(self, shape_name: str, path: str) -> bool:
        """Registers an extended cursor shape with its file path. If the shape is already registered, unregister the previous one before registering again.

        Args:
            shape_name (str): The name of the cursor shape to register.
            path (str): The file path to the cursor image.
            
        Returns:
            bool: True if the operation succeeded."""
        if self._imgui_renderer:
            self._imgui_renderer.register_cursor_shape_extend(shape_name, path)
            return True
        return False

    def unregister_cursor_shape_extend(self, shape_name: str) -> bool:
        """Unregisters an extended cursor shape. If the shape is being set as the current cursor, restore to default, otherwise if not registered, nothing is done.

        Args:
            shape_name (str): The name of the cursor shape to unregister.

        Returns:
            bool: True if the operation succeeded"""
        if self._imgui_renderer:
            self._imgui_renderer.unregister_cursor_shape_extend(shape_name)
            return True
        return False

    def override_cursor_shape_extend(self, shape_name: str) -> bool:
        """Overrides the current cursor shape with an extended shape.

        Args:
            shape_name (str): The name of the extended cursor shape.

        Returns:
            bool: True if the operation succeeded"""
        if self._app_window and self._imgui_renderer:
            self._imgui_renderer.set_cursor_shape_override_extend(self._app_window, shape_name)
            return True
        return False

    def override_cursor_shape(self, shape: windowing.CursorStandardShape) -> bool:
        """Overrides the current cursor shape with a standard shape.

        Args:
            shape (windowing.CursorStandardShape): The standard cursor shape.
                    
        Returns:
            bool: True if the operation succeeded"""
        if self._app_window and self._imgui_renderer:
            self._imgui_renderer.set_cursor_shape_override(self._app_window, shape)
            return True
        return False

    def clear_overridden_cursor_shape(self) -> bool:
        """Clears any overridden cursor shape, reverting to default.

        Returns:
            bool: True if the operation succeeded"""
        if self._app_window and self._imgui_renderer:
            self._imgui_renderer.clear_cursor_shape_override(self._app_window)
            return True
        return False

    def get_cursor_shape_override_extend(self) -> Optional[str]:
        """Gets the current extended cursor shape override.

        Returns:
            Optional[str]: The name of the overridden cursor shape or None if not overridden."""
        if self._app_window and self._imgui_renderer:
            return self._imgui_renderer.get_cursor_shape_override_extend(self._app_window)
        return None

    def get_cursor_shape_override(self) -> Optional[windowing.CursorStandardShape]:
        """Gets the current standard cursor shape override.

        Returns:
            Optional[windowing.CursorStandardShape]: The overridden cursor shape or None if not overridden."""
        if self._app_window and self._imgui_renderer:
            return self._imgui_renderer.get_cursor_shape_override(self._app_window)
        return None
    
def get_main_window_cursor() -> weakref.CallableProxyType:
    """Returns the WindowCursor extension instance."""
    return main_window_cursor
