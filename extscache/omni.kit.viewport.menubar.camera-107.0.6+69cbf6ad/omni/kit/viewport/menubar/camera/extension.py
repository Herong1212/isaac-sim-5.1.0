# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ViewportCameraMenuBarExtension", "get_instance"]

from typing import Callable, Optional

import omni.ext
import omni.ui as ui

from .camera_menu_container import CameraMenuContainer
from .commands import register_commands, unregister_commands
from .menu_item.single_camera_menu_item import SingleCameraMenuItemBase

_extension_instance = None


class ViewportCameraMenuBarExtension(omni.ext.IExt):
    """The main class that manages the camera settings integration into the viewport menu bar"""
    def __init__(self):
        """
        Construct the extension.
        """
        self._camera_menu = None
        self._cmds = None
        super().__init__()

    def on_startup(self, ext_id):
        """Callback when extension startup"""
        self._camera_menu = CameraMenuContainer()
        self._cmds = register_commands()

        global _extension_instance
        _extension_instance = self

    def on_shutdown(self):
        """Callback when extesion shutdown"""
        if self._camera_menu:
            self._camera_menu.destroy()
        self._camera_menu = None
        cmds, self._cmds = self._cmds, None
        unregister_commands(cmds)

        global _extension_instance
        _extension_instance = None

    def register_menu_item_type(self, menu_item_type: Callable[..., "SingleCameraMenuItemBase"]):
        """
        Register a custom menu type for the default created camera

        Args:
            menu_item_type: callable that will create the menu item
        """
        if self._camera_menu:
            self._camera_menu.set_menu_item_type(menu_item_type)

    def register_menu_item(self, create_menu_item_fn: Callable[["viewport_context", ui.Menu], None], order: int = 0):  # noqa: F821
        """
        Register a custom menu item.

        Args:
            create_menu_item_fn (Callable): Callback function to create custom menu item.
        Keyword args:
            order (int): Position to put custom menu item in popup menu window.
        """
        if self._camera_menu:
            self._camera_menu.register_menu_item(create_menu_item_fn, order=order)

    def deregister_menu_item(self, create_menu_item_fn: Callable[["viewport_context", ui.Menu], None]):  # noqa: F821
        """
        Deregister a custom menu item.

        Args:
            create_menu_item_fn (Callable): Callback function to create custom menu item.
        """
        if self._camera_menu:
            self._camera_menu.deregister_menu_item(create_menu_item_fn)


def get_instance() -> Optional[ViewportCameraMenuBarExtension]:
    """
    Retrieves the singleton instance of the viewport camera menu bar extension.
    """
    return _extension_instance
