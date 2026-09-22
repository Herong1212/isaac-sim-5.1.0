# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["Toolbar"]

import asyncio
import typing
from typing import Callable

import carb
import carb.settings
import omni.kit.app
import omni.ui as ui
import omni.usd
from omni.ui import color as cl

from .builtin_tools.builtin_tools import BuiltinTools
from .commands import *
from .context_menu import *
from .widget_group import WidgetGroup  # backward compatible

if typing.TYPE_CHECKING:
    import weakref

GRAB_ENABLED_SETTING_PATH = "/exts/omni.kit.widget.toolbar/Grab/enabled"


class Toolbar:
    """
    Main Toolbar class.
    """
    WINDOW_NAME = "Main ToolBar"
    DEFAULT_CONTEXT = ""
    DEFAULT_CONTEXT_TOKEN = 0
    DEFAULT_SIZE = 38

    def __init__(self):
        self._settings = carb.settings.get_settings()
        self.__root_frame = None
        self._toolbar_widget_groups: list[WidgetGroup] = []
        self._toolbar_widgets = {}
        self._toolbar_dirty = False
        self._axis = ui.ToolBarAxis.X
        self._rebuild_task = None
        self._grab_stack = None
        self._context_menu = ContextMenu()
        self._context_token_pool = 1
        self._context = Toolbar.DEFAULT_CONTEXT
        self._context_token = Toolbar.DEFAULT_CONTEXT_TOKEN
        self._context_token_owner_count = 0
        self.__init_shades()

        self._builtin_tools = BuiltinTools(self)

    def __init_shades(self):
        """Style colors"""
        cl.toolbar_button_background = cl.shade(0x0)
        cl.toolbar_button_background_checked = cl.shade(0xFF1F2123)
        cl.toolbar_button_background_pressed = cl.shade(0xFF4B4B4B)
        cl.toolbar_button_background_hovered = cl.shade(0xFF383838)

    @property
    def context_menu(self):
        return self._context_menu

    def destroy(self):
        if self._rebuild_task is not None:
            self._rebuild_task.cancel()

        self._toolbar_widgets = {}
        if self._builtin_tools:
            self._builtin_tools.destroy()
            self._builtin_tools = None

        self._toolbar_widget_groups = []

    def add_widget(self, widget_group: WidgetGroup, priority: int, context: str = ""):
        """
        Adds a WidgetGroup instance to the Toolbar.

        Args:
            widget_group (WidgetGroup): The WidgetGroup instance to be added to the Toolbar.
            priority (int): priority of the WidgetGroup. With a smaller number the WidgetGroup will be shown on Toolbar first.
            context (str): A context the WidgetGroup is associated with.
        """
        self._toolbar_widget_groups.append((priority, widget_group))
        widget_group.on_added(context)
        self._set_toolbar_dirty()

    def remove_widget(self, widget_group: WidgetGroup):
        """
        Removes a WidgetGroup instance from the Toolbar.

        Args:
            widget_group (WidgetGroup): The WidgetGroup instance to be removed from the Toolbar.
        """
        for widget in self._toolbar_widget_groups:
            if widget[1] == widget_group:
                self._toolbar_widget_groups.remove(widget)
                widget_group.on_removed()
                self._set_toolbar_dirty()
                break

    def get_widget(self, name: str) -> ui.Widget:
        """
        Gets a ui.Widget item by its name.

        Args:
            name (str): The name of widget to fetch.

        Returns:
            The ui.Widget associated with such name. None if not found.
        """
        return self._toolbar_widgets.get(name, None)

    def acquire_toolbar_context(self, context: str):
        """
        Request toolbar to switch to given context.
        It takes the context preemptively even if previous context owner has not release the context.

        Args:
            context (str): Context to switch to.

        Returns:
            A token to be used to release_toolbar_context
        """

        if self._context == context:
            self._context_token_owner_count += 1
            return self._context_token

        # preemptively take current context, regardless of previous owner/count
        self._context = context
        if context == Toolbar.DEFAULT_CONTEXT:
            self._context_token = Toolbar.DEFAULT_CONTEXT_TOKEN
        else:
            self._context_token_pool += 1
            self._context_token = self._context_token_pool
        self._context_token_owner_count = 1
        for widget in self._toolbar_widget_groups:
            widget[1].on_toolbar_context_changed(context)

        return self._context_token

    def release_toolbar_context(self, token: int):
        """
        Request toolbar to release context associated with token.
        If token is expired (already released or context ownership taken by others), this function does nothing.

        Args:
            token (int): Context token to release.
        """

        if token == self._context_token:
            self._context_token_owner_count -= 1
        else:
            carb.log_info("Releasing expired context token, ignoring")
            return

        if self._context_token_owner_count <= 0:
            self._context = Toolbar.DEFAULT_CONTEXT
            self._context_token = Toolbar.DEFAULT_CONTEXT_TOKEN
            self._context_token_owner_count = 0
            for widget in self._toolbar_widget_groups:
                widget[1].on_toolbar_context_changed(self._context)

    def get_context(self):
        """
        Gets the current context of the Toolbar.
        """
        return self._context

    def _set_toolbar_dirty(self):
        self._toolbar_dirty = True
        if self._rebuild_task is None:
            self._rebuild_task = asyncio.ensure_future(self._delayed_rebuild())

    def set_axis(self, axis: ui.ToolBarAxis):
        """
        Sets the axis direction of the Toolbar

        Args:
            axis (ui.ToolBarAxis). ui.ToolBarAxis.X for horizontal toolbar and ui.ToolBarAxis.Y for vertical.
        """
        self._axis = axis

    # delay rebuild so widgets added within one frame are rebuilt together
    @omni.usd.handle_exception
    async def _delayed_rebuild(self):
        await omni.kit.app.get_app().next_update_async()
        if self._toolbar_dirty:
            self.rebuild_toolbar()
            self._toolbar_dirty = False

        self._rebuild_task = None

    def rebuild_toolbar(self, root_frame=None):
        if root_frame:
            self.__root_frame = root_frame
        if not self.__root_frame:
            carb.log_warn("No root frame specified. Please specify a root frame for this widget")
            return

        axis = self._axis
        self._toolbar_widgets = {}
        self._toolbar_widget_groups.sort(key=lambda x: x[0])  # sort by priority
        with self.__root_frame:
            stack = None
            style = {
                "Button": {"background_color": cl.toolbar_button_background, "border_radius": 4, "margin": 2, "padding": 3},
                "Button:checked": {"background_color": cl.toolbar_button_background_checked},
                "Button:pressed": {"background_color": cl.toolbar_button_background_pressed},
                "Button:hovered": {"background_color": cl.toolbar_button_background_hovered},
                "Button.Image::disabled": {"color": 0x608A8777},
                "Line::grab": {"color": 0xFF2E2E2E, "border_width": 2, "margin": 2},
                "Line::separator": {"color": 0xFF555555},
                "Tooltip": {
                    "background_color": 0xFFC7F5FC,
                    "color": 0xFF4B493B,
                    "border_width": 1,
                    "margin_width": 2,
                    "margin_height": 1,
                    "padding": 1,
                },
            }

            for widget in self._toolbar_widget_groups:
                style.update(widget[1].get_style())

            default_size = self.DEFAULT_SIZE
            if axis == ui.ToolBarAxis.X:
                stack = ui.HStack(style=style, height=default_size, width=ui.Percent(100))
            else:
                stack = ui.VStack(style=style, height=ui.Percent(100), width=default_size)

            with stack:
                if self._settings.get(GRAB_ENABLED_SETTING_PATH):
                    self._create_grab(axis)
                    ui.Spacer(width=3, height=3)

                last_priority = None
                for widget in self._toolbar_widget_groups:
                    this_priority = widget[0]
                    if last_priority is not None and this_priority - last_priority >= 10:
                        self._create_separator(axis)
                    public_widgets = widget[1].create(default_size=default_size)
                    if public_widgets is not None:
                        self._toolbar_widgets.update(public_widgets)
                    last_priority = this_priority

    def _create_separator(self, axis):
        if axis == ui.ToolBarAxis.X:
            ui.Line(width=1, name="separator", alignment=ui.Alignment.LEFT)
        else:
            ui.Line(height=1, name="separator", alignment=ui.Alignment.TOP)

    def subscribe_grab_mouse_pressed(self, function: Callable[[int, "weakref.ref"], None]):
        if self._grab_stack:
            self._grab_stack.set_mouse_pressed_fn(function)

    def _create_grab(self, axis):
        grab_area_size = 20

        if axis == ui.ToolBarAxis.X:
            self._grab_stack = ui.HStack(width=grab_area_size)
        else:
            self._grab_stack = ui.VStack(height=grab_area_size)

        with self._grab_stack:
            if axis == ui.ToolBarAxis.X:
                ui.Spacer(width=5)
                ui.Line(name="grab", width=5, alignment=ui.Alignment.LEFT)
                ui.Line(name="grab", width=5, alignment=ui.Alignment.LEFT)
                ui.Line(name="grab", width=5, alignment=ui.Alignment.LEFT)
                ui.Spacer(width=3)
            else:
                ui.Spacer(height=5)
                ui.Line(name="grab", height=5, alignment=ui.Alignment.TOP)
                ui.Line(name="grab", height=5, alignment=ui.Alignment.TOP)
                ui.Line(name="grab", height=5, alignment=ui.Alignment.TOP)
                ui.Spacer(height=3)

    def add_custom_select_type(self, entry_name: str, selection_types: list):
        self._builtin_tools.add_custom_select_type(entry_name, selection_types)

    def remove_custom_select(self, entry_name):
        self._builtin_tools.remove_custom_select(entry_name)

    def add_custom_move_type(self, entry_name: str, move_type: str):
        self._builtin_tools.add_custom_move_type(entry_name, move_type)

    def remove_custom_move(self, entry_name: str):
        self._builtin_tools.remove_custom_move(entry_name)
