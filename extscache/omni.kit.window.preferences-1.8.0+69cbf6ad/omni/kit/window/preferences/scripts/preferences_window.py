# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
"""
preference window class
"""

__all__ = ['PreferenceBuilder', 'PreferenceBuilderUI', 'register_actions', 'deregister_actions', 'PERSISTENT_SETTINGS_PREFIX', 'DEVELOPER_PREFERENCE_PATH', 'GLOBAL_PREFERENCES_PATH', 'RENDERING_PREFERENCES_PATH', 'PreferencesExtension', 'get_instance', 'show_preferences_window', 'hide_preferences_window', 'get_page_list', 'get_shown_page_list', 'register_page', 'select_page', 'rebuild_pages', 'unregister_page', 'show_file_importer', 'restart_kit']

from typing import Callable

import asyncio
import carb
import omni.ext
from enum import IntFlag
from .preference_builder import PreferenceBuilder, PreferenceBuilderUI, SettingType
from .preferences_actions import register_actions, deregister_actions
from carb.eventdispatcher import get_eventdispatcher

_extension_instance = None
_preferences_page_list = []

PERSISTENT_SETTINGS_PREFIX = "/persistent"
DEVELOPER_PREFERENCE_PATH = "/app/show_developer_preference_section"
GLOBAL_PREFERENCES_PATH = "/exts/omni.kit.window.preferences/show_globals"
RENDERING_PREFERENCES_PATH = "/exts/omni.kit.window.preferences/show_rendering"
LINUX_TERMINAL_LIST = "/exts/omni.kit.window.preferences/linux_terminal"

class PreferencesExtension(omni.ext.IExt):
    """
    Preference window class.
    """
    class PreferencesState(IntFlag):
        """
        Preference startup state, either Invalid or Created.
        """
        Invalid = 0
        Created = 1

    def on_startup(self, ext_id):
        global _extension_instance
        _extension_instance = self

        self._ext_name = omni.ext.get_extension_name(ext_id)
        register_actions(self._ext_name, PreferencesExtension, lambda: _extension_instance)

        self._hooks = []
        self._ready_state = PreferencesExtension.PreferencesState.Invalid
        self._window = PreferenceBuilderUI(self._on_visibility_changed_fn)
        self._window.update_page_list(get_page_list())
        self._window.create_window()
        self._window_is_visible = False
        self._create_menu()
        self._register_pages()

        self._resourcemonitor_preferences = None
        manager = omni.kit.app.get_app().get_extension_manager()

        # set app started trigger. refresh_menu_items & rebuild_menus won't do anything until self._ready_state is MenuState.Created
        app = omni.kit.app.get_app()
        if app.is_app_ready():
           self._rebuild_after_loading(None)
        else:
            self._app_ready_sub = (
               get_eventdispatcher()
                .observe_event(
                    event_name=omni.kit.app.GLOBAL_EVENT_APP_READY, on_event=self._rebuild_after_loading, observer_name="omni.kit.window.preferences"
                )
            )

    def on_shutdown(self): # pragma: no cover
        self._hooks = None

        deregister_actions(self._ext_name)

        self._window.destroy()
        del self._window
        self._window = None

        self._remove_menu()

        self._unregister_resourcemonitor_preferences()
        for page in self._created_preferences:
            unregister_page(page, rebuild=False)
        self._created_preferences = None

        # clear globals
        global _preferences_page_list
        _preferences_page_list = None
        global _extension_instance
        _extension_instance = None

    def _rebuild_after_loading(self, _):
        self._ready_state = PreferencesExtension.PreferencesState.Created
        self.rebuild_pages()

    def _register_pages(self):
        from .pages.stage_page import StagePreferences
        from .pages.rendering_page import RenderingPreferences
        from .pages.datetime_format_page import DatetimeFormatPreferences
        from .pages.globals import GlobalPreferences
        from .pages.developer_page import DeveloperPreferences
        from .pages.viewport_page import ViewportPreferences

        self._developer_preferences = None
        self._created_preferences = []
        for page in [
            StagePreferences(),
            DatetimeFormatPreferences(),
            ViewportPreferences(),
            DeveloperPreferences(),
        ]:
            self._created_preferences.append(register_page(page))

        if carb.settings.get_settings().get(GLOBAL_PREFERENCES_PATH):
            self._created_preferences.append(register_page(GlobalPreferences()))
        if carb.settings.get_settings().get(RENDERING_PREFERENCES_PATH):
            self._created_preferences.append(register_page(RenderingPreferences()))

        # developer options
        self._hooks.append(omni.kit.app.SettingChangeSubscription(
            DEVELOPER_PREFERENCE_PATH, self._on_developer_preference_section_changed
        ))

    def _on_developer_preference_section_changed(self, item, event_type):
        omni.kit.window.preferences.rebuild_pages()

    def _register_resourcemonitor_preferences(self):
        from .pages.resourcemonitor_page import ResourceMonitorPreferences
        self._resourcemonitor_preferences = register_page(ResourceMonitorPreferences())

    def _unregister_resourcemonitor_preferences(self): # pragma: no cover
        if self._resourcemonitor_preferences:
            unregister_page(self._resourcemonitor_preferences)
            self._resourcemonitor_preferences = None

    def rebuild_pages(self):
        """
        Rebuild UI.
        """
        if self._ready_state == PreferencesExtension.PreferencesState.Invalid:
            return

        if self._window:
            self._window.update_page_list(get_page_list())
            self._window.rebuild_pages()

    def select_page(self, page):
        """
        Select page to display and refresh.
        """
        if self._window:
            if self._window.select_page(page):
                return True
        return False

    async def _refresh_menu_async(self):
        omni.kit.menu.utils.refresh_menu_items("Edit")
        self._refresh_menu_task = None

    def _on_visibility_changed_fn(self, visible):
        self._window_is_visible = visible
        if visible:
            self._window.show_window()
        else:
            self._window.hide_window()

    def _create_menu(self):
        from omni.kit.menu.utils import MenuItemDescription, MenuItemOrder

        self._edit_menu_list = None
        self._refresh_menu_task = None

        self._edit_menu_list = [
            MenuItemDescription(
                name="Preferences",
                glyph="cog.svg",
                appear_after=["Capture Screenshot", MenuItemOrder.LAST],
                ticked=True,
                ticked_fn=lambda: self._window_is_visible,
                onclick_action=("omni.kit.window.preferences", "toggle_preferences_window"),
            ),
            MenuItemDescription(
                appear_after=["Capture Screenshot", MenuItemOrder.LAST],
            ),

        ]
        omni.kit.menu.utils.add_menu_items(self._edit_menu_list, "Edit", -9)

    def _remove_menu(self): # pragma: no cover
        if self._refresh_menu_task:
            self._refresh_menu_task.cancel()
            self._refresh_menu_task = None

        # remove menu
        omni.kit.menu.utils.remove_menu_items(self._edit_menu_list, "Edit")

    def _toggle_preferences_window(self):
        self._window_is_visible = not self._window_is_visible

        async def show_windows():
            if self._window_is_visible:
                self._window.show_window()
            else:
                self._window.hide_window()

        asyncio.ensure_future(show_windows())
        asyncio.ensure_future(self._refresh_menu_async())

    def show_preferences_window(self):
        """Show the Preferences window to the User."""
        if not self._window_is_visible:
            self._toggle_preferences_window()

    def hide_preferences_window(self):
        """Hide the Preferences window from the User."""
        if self._window_is_visible:
            self._toggle_preferences_window()


def get_instance():
    """
    Get instance of preference window class.
    """
    global _extension_instance

    return _extension_instance


def show_preferences_window():
    """
    Show the Preferences window to the User.
    """
    get_instance().show_preferences_window()


def hide_preferences_window():
    """
    Hide the Preferences window from the User.
    """
    get_instance().hide_preferences_window()


def get_page_list():
    """
    Get list of all available pages.
    """
    global _preferences_page_list

    return _preferences_page_list


def get_shown_page_list():
    """
    Gets list of pages that are visible. IE list of pages that PreferenceBuilder.show_page() returned True.
    """
    instance = get_instance()
    if instance and instance._window and instance._window._pages_model:
        return instance._window._pages_model.get_item_children(None)

    return []

def register_page(page):
    """
    Add new custom page to preference window list.
    """
    global _preferences_page_list

    _preferences_page_list.append(page)
    _preferences_page_list = sorted(_preferences_page_list, key=lambda page: page._title)

    instance = get_instance()
    if instance:
        instance.rebuild_pages()

    return page


def select_page(page):
    """
    Select page to display and refresh.
    """
    return get_instance().select_page(page)


def rebuild_pages():
    """
    rebuild UI
    """
    get_instance().rebuild_pages()


def unregister_page(page, rebuild: bool=True): # pragma: no cover
    """
    Remove custom page from preference window list.
    """
    global _preferences_page_list

    if hasattr(page, 'destroy'):
        page.destroy()
    # Explicitly clear properties, that helps to release some C++ objects
    page.__dict__.clear()

    if _preferences_page_list:
        _preferences_page_list.remove(page)
        preferences = get_instance()
        if preferences and rebuild:
            preferences.rebuild_pages()


def show_file_importer(
    title: str,
    file_exts: list = [("All Files(*)", "")],
    filename_url: str = None,
    click_apply_fn: Callable = None,
    show_only_folders: bool = False,
):
    """
    Shows file importer.
    """
    def on_import(click_fn: Callable, filename: str, dirname: str, selections=[]):
        dirname = dirname.strip()
        if dirname and not dirname.endswith("/"):
            dirname += "/"
        fullpath = f"{dirname}{filename}"
        if click_fn:
            click_fn(fullpath)

    try:
        from functools import partial
        from omni.kit.window.file_importer import get_file_importer

        file_importer = get_file_importer()
        if file_importer:
            file_importer.show_window(
                title=title,
                import_button_label="Select",
                import_handler=partial(on_import, click_apply_fn),
                file_extension_types=file_exts,
                filename_url=filename_url,
                # OM-96626: Add show_only_folders option to file importer
                show_only_folders=show_only_folders,
            )
    except ImportError:
        carb.log_warn("show_file_importer: omni.kit.window.file_importer not found")

def restart_kit(args):
    import subprocess
    import platform

    kwargs = {"close_fds": False}

    match platform.system().lower():
        case "windows":
            kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP

        case "linux":
            from shutil import which

            for cmd in carb.settings.get_settings().get(LINUX_TERMINAL_LIST):
                if which(cmd[0]):
                    carb.log_info(f"restart_kit: Using {cmd} to restart kit")
                    args = list(cmd) + args
                    break

    subprocess.Popen(args, **kwargs)  # pylint: disable=consider-using-with}
