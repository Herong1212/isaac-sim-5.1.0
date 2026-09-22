# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui
import weakref
from .widget import ContentBrowserWidget
from .external_drag_drop_helper import setup_external_drag_drop, destroy_external_drag_drop


class ContentBrowserWindow:
    """The Content Browser window"""

    def __init__(self):
        self._title = "Content"
        self._window = None
        self._widget = None
        self._visiblity_changed_listener = None
        self._build_ui(self._title, 1000, 600)

    def _build_ui(self, title, width, height):
        window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR
        self._window = ui.Window(
            title, width=width, height=height, flags=window_flags, dockPreference=ui.DockPreference.LEFT_BOTTOM
        )
        self._window.set_visibility_changed_fn(self._visibility_changed_fn)

        # Dock it to the same space where Console is docked, make it the first tab and the active tab.
        self._window.deferred_dock_in("Console", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self._window.dock_order = 2

        with self._window.frame:
            # We are using `weakref.proxy` to avoid circular reference. The
            # circular reference is made when calling `set_width_changed_fn`.
            # `self._widget` is captured to the callable, and since the window
            # keeps the callable, it keeps self._widget. At the same time,
            # `self._widget` keeps the window because we pass it to the
            # constructor. To break circular referencing, we use
            # `weakref.proxy`.
            self._widget = ContentBrowserWidget(
                window=weakref.proxy(self._window),
                treeview_identifier="content_browser_treeview",
            )
            self._window.set_width_changed_fn(self._widget._on_window_width_changed)

        # External Drag & Drop
        setup_external_drag_drop(title, self._widget, self._window.frame)

    def _visibility_changed_fn(self, visible):
        if self._visiblity_changed_listener:
            self._visiblity_changed_listener(visible)

    @property
    def widget(self) -> ContentBrowserWidget:
        return self._widget

    def set_visibility_changed_listener(self, listener):
        self._visiblity_changed_listener = listener

    def destroy(self):
        if self._widget:
            self._widget.destroy()
            self._widget = None
        if self._window:
            self._window.destroy()
            self._window = None
        self._visiblity_changed_listener = None
        destroy_external_drag_drop()

    def set_visible(self, value):
        if self._window:
            self._window.visible = value

    def get_visible(self):
        if self._window:
            return self._window.visible
        return False
