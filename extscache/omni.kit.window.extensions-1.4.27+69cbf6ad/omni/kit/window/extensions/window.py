# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides the ExtsWindow class for managing and displaying extensions alongside additional UI components for visualization of extension information, dependencies, and properties."""

__all__ = ["PageSwitcher", "ExtsWindow"]

import asyncio
from typing import Callable

import omni.ui as ui

from .ext_info_widget import ExtInfoWidget
from .ext_status_bar import ExtStatusBar
from .exts_dependency_window import ExtsDependenciesWindow
from .exts_list_widget import ExtsListWidget
from .exts_properties_widget import ExtsPropertiesWidget
from .styles import get_style


class PageSwitcher:
    """A class to manage the visibility of different pages in a UI environment.

    The class maintains a collection of pages, allowing only one to be visible at a time. It provides methods to add new pages, select a page to be visible, and remove all pages upon destruction.
    """

    def __init__(self):
        """Initializes a new instance of the PageSwitcher, which manages switching between UI pages."""
        self._main_pages = {}
        self._selected_page = None

    def add_page(self, name, widget):
        """Adds a new page to the PageSwitcher.

        Args:
            name (str): The unique name of the page to add.
            widget (:obj:`ui.Widget`): The UI widget that represents the page content."""
        widget.set_visible(False)
        self._main_pages[name] = widget

    def select_page(self, name, force=False):
        """Selects a page to be displayed in the PageSwitcher.

        Args:
            name (str): The name of the page to select.
            force (bool): If True, forces the page to be selected even if it is already selected."""
        if self._selected_page == name and not force:
            return
        # Set previous invisible
        selected_page = self._main_pages.get(self._selected_page, None)
        if selected_page:
            selected_page.set_visible(False)

        # Set new and make visible
        self._selected_page = name
        selected_page = self._main_pages.get(self._selected_page, None)
        if selected_page:
            selected_page.set_visible(True)

    def destroy(self):
        """Destroys all pages managed by the PageSwitcher and resets its state."""
        self._main_pages = {}


PAGE_DEPENDENCIES = "dependencies"
PAGE_INFO = "info"
PAGE_PROPERTIES = "properties"


class ExtsWindow:
    """Extensions window

    Args:
        on_visibility_changed_fn (Callable): Function called when window visibility changes."""

    def __init__(self, on_visibility_changed_fn: Callable):
        """Initializes the ExtsWindow with UI components and callback functions."""
        self._exts_dependencies = None
        self._ext_info_widget = None
        self._exts_list_widget = None
        self._exts_properties = None
        self._page_switcher = None
        self._status_bar = None
        self._window = ui.Window("Extensions", width=1300, height=800, flags=ui.WINDOW_FLAGS_NO_SCROLLBAR)
        self._window.set_visibility_changed_fn(on_visibility_changed_fn)
        self.rebuild()

    def rebuild(self):
        # Tree view style
        self._exts_list_widget = ExtsListWidget()
        self._page_switcher = PageSwitcher()

        # Build UI
        with self._window.frame:
            with ui.HStack(style=get_style(self)):
                with ui.ZStack(width=0):
                    # Draggable splitter
                    with ui.Placer(offset_x=392, draggable=True, drag_axis=ui.Axis.X):
                        ui.Rectangle(width=10, name="Splitter")
                    with ui.HStack():
                        with ui.VStack():
                            # Extensions List Widget (on the left)
                            self._exts_list_widget.build()
                            # Status bar
                            self._status_bar = ExtStatusBar()
                        ui.Spacer(width=10)

                with ui.ScrollingFrame(vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF):
                    with ui.HStack():
                        # Selected Extension info
                        self._ext_info_widget = ExtInfoWidget()
                        self._page_switcher.add_page(PAGE_INFO, self._ext_info_widget)
                        # Dependencies
                        self._exts_dependencies = ExtsDependenciesWindow()
                        self._page_switcher.add_page(PAGE_DEPENDENCIES, self._exts_dependencies)
                        # Properties
                        self._exts_properties = ExtsPropertiesWidget()
                        self._page_switcher.add_page(PAGE_PROPERTIES, self._exts_properties)

        # Setup show dependencies callback
        self._exts_list_widget.set_show_dependencies_fn(lambda: self._show_dependencies(None))
        self._exts_list_widget.set_show_properties_fn(self._show_properties)
        self._exts_list_widget.set_ext_selected_fn(self._select_ext)
        self._ext_info_widget.set_show_dependencies_fn(self._show_dependencies)

        self._select_ext(None)

        # expand groups to default
        asyncio.ensure_future(self._exts_list_widget.get_model().delayed_expand())

    def _show_dependencies(self, ext_id: str):
        self._exts_list_widget.clear_selection()
        self._exts_dependencies.select_ext(ext_id)
        self._page_switcher.select_page(PAGE_DEPENDENCIES, force=True)

    def _show_properties(self):
        self._exts_list_widget.clear_selection()
        self._page_switcher.select_page(PAGE_PROPERTIES)

    def _select_ext(self, ext_summary):
        self._page_switcher.select_page(PAGE_INFO)
        self._ext_info_widget.select_ext(ext_summary)

    def destroy(self):
        """
        Called by extension before destroying this object. It doesn't happen automatically.
        Without this hot reloading doesn't work.
        """
        self._exts_dependencies.destroy()
        self._exts_dependencies = None
        self._ext_info_widget.destroy()
        self._ext_info_widget = None
        self._exts_list_widget.destroy()
        self._exts_list_widget = None
        self._exts_properties.destroy()
        self._exts_properties = None
        self._page_switcher.destroy()
        self._page_switcher = None
        self._status_bar.destroy()
        self._status_bar = None
        self._window.destroy()
        self._window = None
