# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ConsoleWindow"]

import asyncio
from typing import Optional

import omni.kit.app
import omni.ui as ui

from .command_input import CommandInput
from .console_command import CommandManager
from .console_toolbar import ConsoleToolbar
from .log_view import LogView
from .style import CONSOLE_WINDOW_STYLE


class ConsoleWindow(ui.Window):
    """The Console window

    This class represents a console window in the UI. It provides functionality for displaying and interacting with console output.
    """

    def __init__(self):
        """Initializes the ConsoleWindow class."""
        self._title = "Console"
        self._log_view: Optional[LogView] = None
        self._command_manager: Optional[CommandManager] = None
        self._toolbar: Optional[ConsoleToolbar] = None
        self._command_input: Optional[CommandInput] = None

        super().__init__(
            self._title,
            width=1000,
            height=600,
            dockPreference=ui.DockPreference.LEFT_BOTTOM,
            raster_policy=ui.RasterPolicy.NEVER,
        )

        # Dock it to the same space where Content is docked, make it the second tab and the active tab.
        self.deferred_dock_in("Content", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self.dock_order = 1

        self.set_visibility_changed_fn(self._visibility_changed_fn)
        self.frame.set_build_fn(self._build_ui)
        self.frame.set_style(CONSOLE_WINDOW_STYLE)

    def destroy(self):
        """Destroy window"""
        if self._toolbar:
            self._toolbar.destroy()
            self._toolbar = None
        if self._log_view:
            self._log_view.destroy()
            self._log_view = None
        if self._command_input:
            self._command_input.destroy()
            self._command_input = None

        super().destroy()

    def _build_ui(self):
        self._log_view = LogView()
        self._command_manager = CommandManager(self._log_view.clear)
        self.__show_command_model = ui.SimpleBoolModel(False)
        with self.frame:
            with ui.VStack(spacing=6):
                self._toolbar = ConsoleToolbar(self._log_view, self.__show_command_model)

                ui.Separator(height=0)

                self._log_view.build_widget()

                self._command_input = CommandInput(self._command_manager, self.__show_command_model)

    def _visibility_changed_fn(self, visible):
        if self._visiblity_changed_listener:
            self._visiblity_changed_listener(visible)

    def set_visibility_changed_listener(self, listener):
        """Sets the listener for visibility changes.

        Args:
            listener (function): Callback called when visibility changes.
        """
        self._visiblity_changed_listener = listener
