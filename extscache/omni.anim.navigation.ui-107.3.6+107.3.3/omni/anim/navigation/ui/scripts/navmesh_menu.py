# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from .navmesh_window import NavMeshWindow

import carb.settings
import omni.kit.app
import omni.kit.ui
import omni.ui as ui
from omni.kit.viewport.menubar.core import SelectableMenuItem
from omni.kit.viewport.menubar.core.model.category_model import CategoryCustomItem, CategoryStateItem

import asyncio
from functools import partial
from typing import List


class NavMeshMenu:
    WINDOW_NAME = "NavMesh"
    MENU_PATH = f"Window/Navigation/{WINDOW_NAME}"

    def __init__(self):
        self._window = None
        ui.Workspace.set_show_window_fn(NavMeshMenu.WINDOW_NAME, partial(self._on_show_window, None))
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu = editor_menu.add_item(NavMeshMenu.MENU_PATH, self._on_show_window, toggle=True, value=False)

    def destroy(self):
        self._menu = None
        if self._window:
            self._window.destroy()
            self._window = None
        ui.Workspace.set_show_window_fn(NavMeshMenu.WINDOW_NAME, None)

    def __del__(self):
        self.destroy()

    def _set_menu(self, value):
        """Set the menu to create this window on and off"""
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            editor_menu.set_value(NavMeshMenu.MENU_PATH, value)

    async def _destroy_window_async(self):
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._window:
            self._window.destroy()
            self._window = None

    def _visibility_changed_fn(self, visible):
        self._set_menu(visible)
        if not visible:
            # destroy the window, since we are creating new window in show_window
            asyncio.ensure_future(self._destroy_window_async())

    def _on_show_window(self, menu, value):
        if value:
            self._window = NavMeshWindow()
            self._window.set_visibility_changed_listener(self._visibility_changed_fn)
        elif self._window:
            self._window.visible = False

    def show_window(self):
        if self._window:
            self._window.show_current_frame()
            self._window.focus()
        else:
            self._window = NavMeshWindow()
            self._window.set_visibility_changed_listener(self._visibility_changed_fn)
            ui.Workspace.show_window(NavMeshMenu.WINDOW_NAME, True)

    def add_exclusion(self, prim_paths: List[str]):
        if self._window is not None:
            self._window.add_exclusion(prim_paths)

    def remove_exclusion(self, prim_paths: List[str]):
        if self._window is not None:
            self._window.remove_exclusion(prim_paths)


class NavMeshViewportMenu():
    CATEGORY = "Show By Type"
    VIEW_NAV_MESH_PATH = "/persistent/exts/omni.anim.navigation.core/navMesh/viewNavMesh"

    def __init__(self):
        self._display_instance = None
        self._menu = None

    def _add_setting(self, label, setting_path) -> CategoryStateItem:
        item = SelectableMenuItem(label, ui.SimpleBoolModel(self._settings.get_as_bool(setting_path)))
        item.model.add_value_changed_fn(lambda *_: self._settings.set(setting_path, item.model.get_value_as_bool()))
        self._subscribe_to_setting_change(item, setting_path)
        return item

    def _build_menu(self):
        return self._add_setting("NavMesh", NavMeshViewportMenu.VIEW_NAV_MESH_PATH)

    def _subscribe_to_setting_change(self, item, setting_path):
        if setting_path in self._subscriptions:
            self._settings.unsubscribe_to_change_events(self._subscriptions[setting_path])
            del self._subscriptions[setting_path]
            item.model.set_value(self._settings.get_as_bool(setting_path))
        self._subscriptions[setting_path] = self._settings.subscribe_to_node_change_events(
            setting_path, lambda *_: self._subscribe_to_setting_change(item, setting_path))

    def register_with_viewport(self):
        self._display_instance = omni.kit.viewport.menubar.display.get_instance()
        self._settings = carb.settings.acquire_settings_interface()
        self._subscriptions = {}
        self._viewport_menu = CategoryCustomItem("", lambda: self._build_menu())
        self._display_instance.register_custom_category_item(NavMeshViewportMenu.CATEGORY, self._viewport_menu)

    def unregister_from_viewport(self):
        if self._display_instance:
            try:
                self._display_instance.deregister_custom_category_item(
                    NavMeshViewportMenu.CATEGORY,
                    self._viewport_menu
                )
            except Exception:
                # TODO: This fails the repo test
                # AttributeError: 'DisplayMenuContainer' object has no attribute '_category_models''
                pass
        for setting_path in self._subscriptions:
            self._settings.unsubscribe_to_change_events(self._subscriptions[setting_path])
        self._display_instance = None
        self._viewport_menu = None
        self._settings = None
        self._subscriptions = {}
