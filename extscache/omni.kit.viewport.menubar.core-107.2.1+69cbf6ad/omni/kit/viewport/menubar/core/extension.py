# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ViewportMenuBarExtension"]

from typing import List, Optional

import omni.ext
from omni.kit.viewport.registry import RegisterViewportLayer
from omni.kit.window.preferences import register_page, unregister_page
from omni.ui import color as cl
from omni.ui import constant as fl

from .menu_item.viewport_menu_spacer import ViewportMenuSpacer
from .menu_item.viewport_menubar_item import ViewportMenubar
from .preference.menubar_page import ViewportMenubarPage
from .style import DEFAULT_MENUBAR_NAME
from .utils.usd_watch import start as usd_watch_start
from .utils.usd_watch import stop as usd_watch_stop
from .viewport_layer import MenuBarViewportLayer
from .viewport_menu_model import AbstractViewportMenubarItem, ViewportMenuModel
from .viewport_menu_model import destroy as destroy_menu_model

_extension_instance = None


class ViewportMenuBarExtension(omni.ext.IExt):
    """Manages the lifecycle of the viewport menu bar and its items."""
    def __init__(self):
        """Constructor"""
        self._model: Optional[ViewportMenuModel] = None
        self._top_bar_item: Optional[ViewportMenubar] = None
        self._page: Optional[ViewportMenubarPage] = None
        self.__viewport_layer = None
        super().__init__()

    def init_shades(self):
        """Style colors"""
        # https://confluence.nvidia.com/pages/viewpage.action?spaceKey=OMNIVERSE&title=Viewport+Toolbar
        cl.viewport_menubar_title = cl.shade(cl("#25282A"))
        cl.viewport_menubar_title_background = cl.shade(cl("#191A1B"))
        cl.viewport_menubar_background = cl.shade(cl("#25282ACC"))
        cl.viewport_menubar_medium = cl.shade(cl("#6E6E6E"))
        cl.viewport_menubar_light = cl.shade(cl("#D6D6D6"))
        cl.viewport_menubar_selection = cl.shade(cl("#34C7FF3B"))
        cl.viewport_menubar_selection_border = cl.shade(cl("#34C7FF"))
        cl.viewport_menubar_selection_border_button = cl.shade(cl("#2B87AA"))
        fl.viewport_menubar_item_margin = fl.shade(5)
        fl.viewport_menubar_item_margin_height = fl.shade(3)
        fl.viewport_menubar_height = fl.shade(30)
        fl.viewport_menubar_icon_size = fl.shade(30)
        fl.viewport_menubar_control_height = fl.shade(18)
        fl.viewport_menubar_border_radius = fl.shade(6)

    def on_startup(self):
        """Callback when extension startup"""
        self._model = ViewportMenuModel()

        # Default menubar
        self._top_bar_item = ViewportMenubar(DEFAULT_MENUBAR_NAME)

        # Preference page
        self._page = ViewportMenubarPage(self._model)
        register_page(self._page)

        # Start USD Watch
        usd_watch_start()

        self.init_shades()

        # And then the viewport-layer itself (what will build all the menu-items / widgets above)
        # Entry point for the custom widget in the viewport
        self.__viewport_layer = RegisterViewportLayer(MenuBarViewportLayer, "omni.kit.viewport.menubar.MenuBarLayer")

        # Register the menus
        ViewportMenuSpacer()

        global _extension_instance
        _extension_instance = self

    def on_shutdown(self):
        """Callback when extension shut down"""
        global _extension_instance
        _extension_instance = None

        self._top_bar_item.destroy()
        self._page.destroy()
        unregister_page(self._page)
        self._page = None

        self._model.destroy()

        # Destroy every item in the model and release them
        destroy_menu_model()

        self.__viewport_layer.destroy()
        self.__viewport_layer = None

        # Stop USD Watch
        usd_watch_stop()

    def get_menubars(self) -> List[AbstractViewportMenubarItem]:
        """
        Retrieve all menu bars in viewport.
        """
        return self._model.get_item_children()

    def get_menubar(self, name: str) -> Optional[AbstractViewportMenubarItem]:
        """
        Retrieve menu bar in viewport by name.

        Args:
            name (str): Name of menu bar
        """
        for item in self.get_menubars():
            if item.name == name:
                return item
        return None


def get_instance() -> Optional[ViewportMenuBarExtension]:
    """
    Retrieves the singleton instance of the viewport menu bar core extension.
    """
    return _extension_instance
