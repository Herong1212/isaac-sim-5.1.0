# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["create_viewport_window_menu"]

import carb
import omni.ext
from omni.ui import Workspace
from .window import ViewportWindow
from .viewport_actions import register_actions, deregister_actions


# Normalize a setting value to a dict object to support coming in as list or dict
def _setting_to_dict(key: str, settings):
    value = settings.get(key)
    if value and isinstance(value, list):
        return {str(i): value[i] for i in range(len(value))}
    return value or {}


# Helper class for building a Window name and menu-entry label from an index
class _ViewportLabeling:
    def __init__(self, settings):
        # Grab settings and fallback to sensible defaults when not provided
        self.__default_name = settings.get("/exts/omni.kit.viewport.window/startup/windowName") or "Viewport"
        # Settings as lists for individual Window and menu-entries
        self.__window_names = _setting_to_dict("/exts/omni.kit.viewport.window/startup/windowNames", settings)
        self.__menu_labels = _setting_to_dict("/exts/omni.kit.viewport.window/windowMenu/entryLabels", settings)
        self.__num_entries = int(settings.get("/exts/omni.kit.viewport.window/windowMenu/entryCount") or 0)

    def __format_str(self, vp_str: str, index: str):
        # Format string labels using variables. index and index_1 variables are provided as the default scheme
        # is: "Viewport", "Viewport 2" for Window names; and "Viewport 1", "Viewport 2" for menu entries
        index_1 = index + 1
        return vp_str.format(window_name=self.__default_name, index=index, index_1=index_1)

    def window_name(self, i: int):
        # Pull the Window name from list of names, or fallback to default name if no list or entry is empty
        dflt_str: str = "{window_name} {index_1}" if i > 0 else self.__default_name
        return self.__format_str(self.__window_names.get(str(i), dflt_str) if self.__window_names else dflt_str, i)

    def menu_label(self, i: int):
        # Pull menu entry label from list of labels, or fallback to f"{default_name} {index}"
        dflt_str: str = "{window_name}"
        if self.__num_entries > 1:
            dflt_str += " {index_1}"
        return self.__format_str(self.__menu_labels.get(str(i), dflt_str) if self.__menu_labels else dflt_str, i)


class _DockingDelegate:
    @staticmethod
    def get_delegate():
        return _DockingDelegate()

    async def wait_for_window(self, window_name: str, dock_name: str, position: omni.ui.DockPosition, ratio: float, wait_frames: int):
        app = omni.kit.app.get_app()
        dockspace = Workspace.get_window(dock_name)
        window = Workspace.get_window(window_name)
        if (window is None) or (dockspace is None):
            frames = 3
            while ((window is None) or (dockspace is None)) and frames:
                await app.next_update_async()
                dockspace = Workspace.get_window(dock_name)
                window = Workspace.get_window(window_name)
                frames = frames - 1

        if window and dockspace:
            # When docking to existing Viewport, preserve tab-visibility for both, otherwise defer to setting
            if position == omni.ui.DockPosition.SAME:
                settings = carb.settings.get_settings()
                dock_tab_bar_visible = not bool(settings.get("/exts/omni.kit.viewport.window/startup/dockTabInvisible"))
            else:
                dock_tab_bar_visible = dockspace.dock_tab_bar_visible

            window.deferred_dock_in(dock_name)
            # Split the tab to the right
            if position != omni.ui.DockPosition.SAME:
                for _ in range(wait_frames):
                    await app.next_update_async()
                window.dock_in(dockspace, position, ratio)

            # This generally works in a variety of cases from load, re-load, and save extension .py file reload
            # But it depends on a call order in omni.ui and registered selected_in_dock and dock_changed callbacks.
            await app.next_update_async()
            updates_enabled = window.selected_in_dock if window.docked else window.visible
            window.viewport_api.updates_enabled = updates_enabled
            # Set the dock-tab visible to the state of the default Viewport
            await app.next_update_async()
            window.dock_tab_bar_visible = dock_tab_bar_visible
            dockspace.dock_tab_bar_visible = dock_tab_bar_visible

    def dock_viewport(self, window_name: str, viewport_index: int, default_window_name: str, number_of_entries: int):
        settings = carb.settings.get_settings()
        if bool(settings.get("/app/docks/disabled")):
            return

        # For more than two Viewports,
        single_tab_group = settings.get("/exts/omni.kit.viewport.window/startup/singleTabGroup")
        wait_frames = 2 if ((number_of_entries < 2) or single_tab_group) else 4
        vp_labeling = _ViewportLabeling(settings)
        import asyncio
        if single_tab_group or (window_name == default_window_name):
            asyncio.ensure_future(self.wait_for_window(window_name, default_window_name, omni.ui.DockPosition.SAME, 1.0, wait_frames))
        elif window_name == vp_labeling.window_name(1):
            asyncio.ensure_future(self.wait_for_window(window_name, default_window_name, omni.ui.DockPosition.RIGHT, 0.5, wait_frames))
        else:
            # TODO: Works well for a quad-layout, but will continually subdivide last entries past that
            asyncio.ensure_future(self.wait_for_window(window_name,
                                                       vp_labeling.window_name(viewport_index - 2),
                                                       omni.ui.DockPosition.BOTTOM,
                                                       0.5,
                                                       wait_frames))


class _MenuEntry:
    __DEFAULT_VIEWPORT = None
    __NUMBER_OF_ENTRIES = 0

    def __init__(self, window_name: str, menu_label: str, open_window: bool, index: int, settings):
        self.__window_name = window_name
        self.__window = None
        self.__menu_entry = None
        self.__action_name = None
        self.__index = index

        _MenuEntry.__NUMBER_OF_ENTRIES = _MenuEntry.__NUMBER_OF_ENTRIES + 1
        # Layout needs to mark one viewport as 'default', so use first one set to auto-open
        if _MenuEntry.__DEFAULT_VIEWPORT is None and open_window:
            _MenuEntry.__DEFAULT_VIEWPORT = window_name

        carb.log_info(f"Creating Viewport menu-entry: '{menu_label}' to show '{window_name}' with visibility: {open_window} as default: {self.__DEFAULT_VIEWPORT == window_name}")

        Workspace.set_show_window_fn(self.__window_name, lambda b: self.__show_window(None, b))
        if open_window:
            Workspace.show_window(self.__window_name)

        # add actions
        self.__action_name = register_actions("omni.kit.viewport.window", index, self.__show_window, self.__is_window_visible)

        # add menu
        if self.__action_name:
            try:
                from omni.kit.menu.utils import MenuItemDescription

                top_level_name = settings.get("/exts/omni.kit.viewport.window/windowMenu/label")
                menu_entry = MenuItemDescription(name=menu_label,
                                                 ticked=True,
                                                 ticked_fn=self.__is_window_visible,
                                                 onclick_action=(
                                                     "omni.kit.viewport.window",
                                                     self.__action_name),
                                                 )
                if bool(top_level_name):
                    self.__menu_entry = MenuItemDescription(name=top_level_name, sub_menu=[menu_entry])

                else:
                    self.__menu_entry = menu_entry

                # "Window" menus still uses editor_menu helper, so menu items have priority
                self.__menu_entry.priority = -99
                omni.kit.menu.utils.add_menu_items([self.__menu_entry], name="Window")
            except ImportError:
                pass

    def __del__(self):
        self.destroy()

    def destroy(self):
        window, self.__window = self.__window, None
        menu_entry, self.__menu_entry = self.__menu_entry, None
        if window:
            window.set_visibility_changed_fn(None)
            window.destroy()
        Workspace.set_show_window_fn(self.__window_name, None)

        # remove menu
        if menu_entry:
            try:
                import omni.kit.menu.utils

                omni.kit.menu.utils.remove_menu_items([menu_entry], name="Window")
            except ImportError:
                pass

        # remove actions
        if self.__action_name:
            deregister_actions("omni.kit.viewport.window", self.__action_name)

    def __show_window(self, menu, visible):
        if visible:
            if not self.__window:
                def visiblity_changed(visible):
                    if not visible:
                        self.__show_window(None, False)
                settings = carb.settings.get_settings()
                dock_tab_bar_visible = not bool(settings.get("/exts/omni.kit.viewport.window/startup/dockTabInvisible"))
                self.__window = ViewportWindow(self.__window_name, dock_tab_bar_visible=dock_tab_bar_visible)
                self.__window.set_visibility_changed_fn(visiblity_changed)
                _DockingDelegate.get_delegate().dock_viewport(
                    self.__window_name, self.__index, self.__DEFAULT_VIEWPORT, self.__NUMBER_OF_ENTRIES
                )
            self.__window.visible = True
        elif self.__window:
            # For now just hide the Window. May want to add a setting for a full destroy-rebuild cycle, but now
            # that won't work well with the get_frame API.
            if True:  # noqa PLW0125
                self.__window.visible = False
            else:
                self.__window.set_visibility_changed_fn(None)
                self.__window.destroy()
                self.__window = None

            try:
                import omni.kit.menu.utils

                omni.kit.menu.utils.refresh_menu_items("Window")
            except ImportError:
                pass

    def __is_window_visible(self) -> bool:
        return False if self.__window is None else self.__window.visible


def create_viewport_window_menu(num_entries: int | None = None):
    settings = carb.settings.get_settings()
    if num_entries is None:
        num_entries = int(settings.get("/exts/omni.kit.viewport.window/windowMenu/entryCount") or 0)
        if num_entries == 0:
            return None

    # Grab settings and fallback to sensible defaults when not provided
    disable_show = bool(settings.get("/exts/omni.kit.viewport.window/startup/disableWindowOnLoad"))
    # Setting for individual Window and menu-entries
    show_windows = settings.get("/exts/omni.kit.viewport.window/startup/showOnLaunch")
    # Support single bool as setting for all, list from toml, or possible sparse list / dict
    if isinstance(show_windows, bool):
        show_windows = {str(i): show_windows for i in range(num_entries)}
    elif isinstance(show_windows, list):
        show_windows = {str(i): show_windows[i] for i in range(len(show_windows))}

    # Build the ViewportWindow menu entry to show a Viewport with proper name
    vp_labeling = _ViewportLabeling(settings)
    return [
        _MenuEntry(
            vp_labeling.window_name(i),
            vp_labeling.menu_label(i),
            False if disable_show else (show_windows.get(str(i), False) if show_windows else (i == 0)),
            i,
            settings,
        ) for i in range(num_entries)
    ]
