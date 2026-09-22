# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# pylint: disable=attribute-defined-outside-init, protected-access

"""This module provides a user interface for managing and displaying extensions in an application, allowing users to list, select, and view details about extensions, including their associated dependencies and properties."""

import asyncio
import weakref
from typing import Callable

import omni.ext
import omni.kit.app
import omni.ui as ui
from carb.eventdispatcher import get_eventdispatcher
from omni.kit.menu.utils import MenuHelperExtension

from . import common, ext_controller, ext_info_widget
from .exts_list_widget import ExtsListWidget
from .utils import get_setting
from .window import ExtsWindow

WINDOW_NAME = "Extensions"
MENU_GROUP = "Window"

_ext_instance = None


def show_window(value: bool):  # pragma: no cover
    """Show/Hide Extensions window"""
    if _ext_instance:
        _ext_instance.show_window(value)


def get_instance() -> "weakref.ReferenceType[ExtsWindowExtension]":
    """Returns a weak reference to the singleton instance of ExtsWindowExtension.

    Returns:
        weakref.ReferenceType[:obj:`ExtsWindowExtension`]: A weak reference to the ExtsWindowExtension instance."""
    return weakref.ref(_ext_instance)


class ExtsWindowExtension(omni.ext.IExt, MenuHelperExtension):
    """The entry point exts 2.0 window

    This extension integrates into the omni.ext.IExt interface and provides a user interface for managing and interacting with extensions in the application. It features a window that lists available extensions and allows users to control their activation state, view detailed information, and manage extension-specific settings. Additionally, it offers a menu integration that allows easy access to the extensions window from the application's main menu.
    """

    def on_startup(self, ext_id):
        """Initializes the extension with the given extension ID."""
        global _ext_instance

        _ext_instance = self

        app = omni.kit.app.get_app()
        common.EXT_ROOT = app.get_extension_manager().get_extension_path(ext_id)

        self._window = None
        ui.Workspace.set_show_window_fn(WINDOW_NAME, self.show_window)

        self.menu_startup(WINDOW_NAME, WINDOW_NAME, MENU_GROUP, appear_after="everything")
        self._menu_entry[0].priority = 999
        self._menu_entry[0].header = ""

        # Start enabling auto-loadable extensions:
        asyncio.ensure_future(ext_controller.autoload_extensions())

        # Auto show window, for convenience
        show = get_setting("/exts/omni.kit.window.extensions/showWindow", False)
        if show:
            self.show_window(True)

        # Some events trigger rebuild of a whole window
        self._subs = []

        def on_rebuild(_):
            if self._window:
                self.show_window(False)
                self.show_window(True)

        self._subs.append(
            get_eventdispatcher().observe_event(
                event_name=common.COMMUNITY_TAB_TOGGLE_GLOBAL_EVENT, on_event=on_rebuild
            )
        )

    def on_shutdown(self):
        """Performs cleanup operations when the extension is shutting down."""
        global _ext_instance
        _ext_instance = None

        self.show_window(False)
        self.menu_shutdown()
        self._subs = None
        common.EXT_ROOT = None
        ui.Workspace.set_show_window_fn("Extensions", None)

    def show_window(self, value):
        """Controls the visibility of the window based on the given value.

        Args:
            value (bool): Determines whether to show or hide the window."""
        if value:
            if not self._window:

                def on_visibility_changed(visible):
                    self.menu_refresh()
                    if not visible:
                        self.show_window(False)

                # this could be called using ui.Workspace.show_window(WINDOW_NAME, visible)
                # so menu_refresh is needed here when new window is created.
                self.menu_refresh()
                self._window = ExtsWindow(on_visibility_changed)
        else:
            if self._window:
                self._window.destroy()
                self._window = None

    # --------------------------------------------------------------------------------------------------------------
    # API to add a new tab to the extension info pane
    @classmethod
    def refresh_extension_info_widget(cls):
        """Refreshes the contents of the extension information widget."""
        if _ext_instance._window and _ext_instance._window._ext_info_widget:
            _ext_instance._window._ext_info_widget.update_tabs()
            _ext_instance._window._ext_info_widget._refresh()

    @classmethod
    def add_tab_to_info_widget(cls, tab: ext_info_widget.PageBase):
        """Adds a new tab to the extension information widget.

        Args:
            tab (:obj:`ext_info_widget.PageBase`): The tab to add to the info widget."""
        ext_info_widget.ExtInfoWidget.pages.append(tab)
        cls.refresh_extension_info_widget()

    @classmethod
    def remove_tab_from_info_widget(cls, tab: ext_info_widget.PageBase):
        """Removes a tab from the extension information widget.

        Args:
            tab (:obj:`ext_info_widget.PageBase`): The tab to remove from the info widget."""
        if tab in ext_info_widget.ExtInfoWidget.pages:
            ext_info_widget.ExtInfoWidget.pages.remove(tab)
            ext_info_widget.ExtInfoWidget.current_page = 0
        cls.refresh_extension_info_widget()

    # --------------------------------------------------------------------------------------------------------------
    # API to add a menu
    @classmethod
    def refresh_menu_items(cls):
        """Refreshes the list of search items in the extension list widget."""
        if _ext_instance and _ext_instance._window and _ext_instance._window._exts_list_widget:
            _ext_instance._window.rebuild()

    @classmethod
    def add_menu_to_info_widget(cls, tab: ext_info_widget.PageBase):
        """Adds a new menu to the extension information widget.

        Args:
            tab (:obj:`ext_info_widget.PageBase`): The tab to add to the info widget."""
        ExtsListWidget.menus.append(tab)
        cls.refresh_menu_items()

    @classmethod
    def remove_menu_from_info_widget(cls, tab: ext_info_widget.PageBase):
        """Removes a menu from the extension information widget.

        Args:
            tab (:obj:`ext_info_widget.PageBase`): The tab to remove from the info widget."""
        if tab in ExtsListWidget.menus:
            ExtsListWidget.menus.remove(tab)
        cls.refresh_menu_items()

    # --------------------------------------------------------------------------------------------------------------
    # API to add a searchable keyword
    @classmethod
    def refresh_search_items(cls):
        """Refreshes the list of search items in the extension list widget."""
        if _ext_instance and _ext_instance._window and _ext_instance._window._exts_list_widget:
            _ext_instance._window._exts_list_widget.rebuild_filter_menu()
            _ext_instance._window._exts_list_widget._model.refresh_all()

    @classmethod
    def add_searchable_keyword(cls, keyword: str, description: str, filter_on_keyword: Callable, clear_cache: Callable):
        """Adds a new searchable keyword to the extensions list widget.

        Args:
            keyword (str): The keyword to be added.
            description (str): A brief description of the keyword.
            filter_on_keyword (Callable): The callback for filtering based on the keyword.
            clear_cache (Callable): The callback to clear the cache when needed."""
        ExtsListWidget.searches[keyword] = (description, filter_on_keyword, clear_cache)
        cls.refresh_search_items()

    @classmethod
    def remove_searchable_keyword(cls, keyword_to_remove: str):
        """Removes a searchable keyword from the extensions list widget.

        Args:
            keyword_to_remove (str): The keyword to be removed."""
        if keyword_to_remove in ExtsListWidget.searches:
            del ExtsListWidget.searches[keyword_to_remove]
        cls.refresh_search_items()
