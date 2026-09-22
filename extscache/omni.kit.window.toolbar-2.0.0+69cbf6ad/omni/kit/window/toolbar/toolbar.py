# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
import weakref
from functools import lru_cache, partial
from pathlib import Path

import omni.ext
import omni.kit.app
import omni.ui as ui

from omni.kit.widget.toolbar.builtin_tools.builtin_tools import BuiltinTools  # backward compatible
from omni.kit.widget.toolbar.commands import *  # backward compatible
from omni.kit.widget.toolbar.context_menu import *
from omni.kit.widget.toolbar.widget_group import WidgetGroup  # backward compatible
from omni.kit.widget.toolbar import get_instance as _get_widget_instance
from omni.kit.menu.utils import MenuHelperExtension

_toolbar_instance = None


def get_instance():
    return _toolbar_instance


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class Toolbar(omni.ext.IExt, MenuHelperExtension):
    WINDOW_NAME = "Main ToolBar"
    MENU_GROUP = "Window"

    def __init__(self):
        self._main_toolbar = None
        super().__init__()

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        ui.Workspace.set_show_window_fn(Toolbar.WINDOW_NAME, partial(self._show_hide_window, None))

        self._sub_grab_mouse_pressed = None
        self._show_hide_menu_entry = None
        self._widget_instance = _get_widget_instance()

        self._main_toolbar = None
        self._dock_task = None

        self.create_main_toolbar()
        self.menu_startup(Toolbar.WINDOW_NAME, Toolbar.WINDOW_NAME, Toolbar.MENU_GROUP)

        global _toolbar_instance
        _toolbar_instance = self

    def on_shutdown(self):
        global _toolbar_instance
        _toolbar_instance = None

        if self._dock_task is not None:
            self._dock_task.cancel()

        self.menu_shutdown()
        self._show_hide_menu_entry = None
        self._widget_instance = None

        if self._main_toolbar:
            self._main_toolbar.destroy()
        self._main_toolbar = None

        self._sub_grab_mouse_pressed = None

        ui.Workspace.set_show_window_fn(Toolbar.WINDOW_NAME, None)

    @property
    def context_menu(self):
        return self._widget_instance.context_menu

    def create_main_toolbar(self):
        # OM-96550: raster_policy=ui.RasterPolicy.NEVER was added to get around a bug in the rasterizer which caused icons to not display
        #   raster_policy argument should be removed when that bug is fixed.
        self._main_toolbar = ui.ToolBar(Toolbar.WINDOW_NAME, noTabBar=False, padding_x=3, padding_y=3, margin=5, raster_policy=ui.RasterPolicy.NEVER)
        self._main_toolbar.set_axis_changed_fn(self._on_axis_changed)
        self._rebuild_toolbar()
        self._register_context_menu()
        self._dock_task = asyncio.ensure_future(Toolbar._dock())

    def add_widget(self, widget_group: "WidgetGroup", priority: int, context: str = ""):
        self._widget_instance.add_widget(widget_group, priority, context=context)

    def remove_widget(self, widget_group: "WidgetGroup"):
        self._widget_instance.remove_widget(widget_group)

    def get_widget(self, name: str):
        return self._widget_instance.get_widget(name)

    def acquire_toolbar_context(self, context: str):
        """
        Request toolbar to switch to given context.
        It takes the context preemptively even if previous context owner has not release the context.

        Args:
            context (str): Context to switch to.

        Returns:
            A token to be used to release_toolbar_context
        """

        return self._widget_instance.acquire_toolbar_context(context)

    def release_toolbar_context(self, token: int):
        """
        Request toolbar to release context associated with token.
        If token is expired (already released or context ownership taken by others), this function does nothing.

        Args:
            token (int): Context token to release.
        """
        self._widget_instance.release_toolbar_context(token)

    def get_context(self):
        return self._widget_instance.get_context()

    def _on_axis_changed(self, axis):
        self._widget_instance.set_axis(axis)
        self._rebuild_toolbar()

    def _rebuild_toolbar(self):
        self._main_toolbar.frame.clear()
        self._widget_instance.rebuild_toolbar(root_frame=self._main_toolbar.frame)
        self._sub_grab_mouse_pressed = self._widget_instance.subscribe_grab_mouse_pressed(
            self.__on_grab_mouse_pressed
        )

        # Toolbar context menu on the grab area
    def __on_grab_mouse_pressed(self, x, y, button, *args, **kwargs):
        if button == 1:  # Right click, show immediately
            event = ContextMenuEvent()
            event.payload["widget_name"] = "grab"
            self.context_menu.on_mouse_event(event)

    def _register_context_menu(self):
        try:
            import omni.kit.context_menu

            context_menu = omni.kit.context_menu.get_instance()

            def is_button(objects: dict, button_name: str):
                return objects.get("widget_name", None) == button_name

            if context_menu:
                menu = {
                    "name": "Hide",
                    "show_fn": [lambda obj: is_button(obj, "grab")],
                    "onclick_fn": self._menu_hide_toolbar,
                }
                self._show_hide_menu_entry = omni.kit.context_menu.add_menu(menu, "grab", "omni.kit.window.toolbar")
        except ImportError:
            pass

    def _show_hide_window(self, menu, value):
        self._main_toolbar.visible = value

    @staticmethod
    async def _dock():
        frame = 3
        while frame > 0:
            viewport = ui.Workspace.get_window("Viewport")
            if viewport:
                await omni.kit.app.get_app().next_update_async()
                break
            await omni.kit.app.get_app().next_update_async()
            frame -= 1

        toolbar = ui.Workspace.get_window(Toolbar.WINDOW_NAME)
        if viewport and toolbar:
            toolbar.dock_in(viewport, ui.DockPosition.LEFT)
        _toolbar_instance._dock_task = None

    def _menu_hide_toolbar(self, objects):
        if self._main_toolbar is not None:
            self._main_toolbar.visible = False
            self.menu_refresh()

    def add_custom_select_type(self, entry_name: str, selection_types: list):
        self._widget_instance.add_custom_select_type(entry_name, selection_types)

    def remove_custom_select(self, entry_name):
        self._widget_instance.remove_custom_select(entry_name)
