"""
omni.kit.window.property PropertyExtension class.
"""

# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["get_window", "PropertyExtension", "PropertyWindow"]

import weakref
from pathlib import Path

import omni.ext
import omni.ui as ui
from omni.kit.menu.utils import MenuHelperExtension

from .templates.header_context_menu import GroupHeaderContextMenu
from .window import PropertyWindow

_property_window_instance = None
TEST_DATA_PATH = ""


def get_window():
    """Get property window."""
    return _property_window_instance if not _property_window_instance else _property_window_instance()


class PropertyExtension(omni.ext.IExt, MenuHelperExtension):
    """Property window extension class."""

    WINDOW_NAME = "Property"
    """Property window name"""
    MENU_GROUP = "Window"
    """Property menu group"""

    def __init__(self):
        """Initialize PropertyExtension"""
        super().__init__()
        self._window = None
        self._header_context_menu = GroupHeaderContextMenu()

    def on_startup(self, ext_id):
        """Startup function

        Args:
            ext_id (str): Extension id.
        """
        ui.Workspace.set_show_window_fn(PropertyExtension.WINDOW_NAME, self.show_window)
        ui.Workspace.show_window(PropertyExtension.WINDOW_NAME)

        self.menu_startup(PropertyExtension.WINDOW_NAME, PropertyExtension.WINDOW_NAME, PropertyExtension.MENU_GROUP)

        manager = omni.kit.app.get_app().get_extension_manager()
        extension_path = manager.get_extension_path(ext_id)
        global TEST_DATA_PATH
        TEST_DATA_PATH = Path(extension_path).joinpath("data").joinpath("tests")

    def on_shutdown(self):
        """Shutdown function"""
        self.menu_shutdown()

        if self._window:
            self._window.destroy()
            self._window = None

        if self._header_context_menu:
            self._header_context_menu.destroy()
            self._header_context_menu = None

        ui.Workspace.set_show_window_fn(PropertyExtension.WINDOW_NAME, None)

    def _visiblity_changed_fn(self, visible):
        self.menu_refresh()

    def show_window(self, value: bool):
        """Show/hide property window function

        Args:
            value (bool): True if window will be shown or False if window will be hidden.
        """
        global _property_window_instance

        if value:
            if self._window is None:
                self._window = PropertyWindow()
                self._window.set_visibility_changed_listener(self._visiblity_changed_fn)
                _property_window_instance = weakref.ref(self._window)
            self._window.set_visible(value)

        elif self._window:
            self._window.set_visible(value)
