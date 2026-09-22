# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module defines a ContentBrowserRegistryExtension class for monitoring and managing customizations in the Content Browser, including custom menus, selection handlers, and search delegates, and provides a mechanism to retrieve its singleton instance."""


import omni.ext
import omni.kit.app

from typing import Callable
from collections import OrderedDict

g_singleton = None


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class ContentBrowserRegistryExtension(omni.ext.IExt):
    """A registry extension that monitors functional customizations applied to the Content Browser.

    This class tracks custom menus, selection handlers, and search delegates, allowing them to be reapplied if the Content Browser is restarted.
    """

    def __init__(self):
        super().__init__()
        self._custom_menus = OrderedDict()
        self._selection_handlers = set()
        self._search_delegate = None

    def on_startup(self, ext_id):
        # Save away this instance as singleton
        global g_singleton
        g_singleton = self

    def on_shutdown(self):
        self._custom_menus.clear()
        self._selection_handlers.clear()
        self._search_delegate = None

        global g_singleton
        g_singleton = None

    def register_custom_menu(
        self, context: str, name: str, glyph: str, click_fn: Callable, show_fn: Callable, index: int = -1
    ):
        id = f"{context}::{name}"
        self._custom_menus[id] = {
            "name": name,
            "glyph": glyph,
            "click_fn": click_fn,
            "show_fn": show_fn,
            "index": index,
        }

    def deregister_custom_menu(self, context: str, name: str):
        id = f"{context}::{name}"
        if id in self._custom_menus:
            del self._custom_menus[id]

    def register_selection_handler(self, handler: Callable):
        self._selection_handlers.add(handler)

    def deregister_selection_handler(self, handler: Callable):
        if handler in self._selection_handlers:
            self._selection_handlers.remove(handler)

    def register_search_delegate(self, search_delegate: "SearchDelegate"):
        self._search_delegate = search_delegate

    def deregister_search_delegate(self, search_delegate: "SearchDelegate"):
        if self._search_delegate == search_delegate:
            self._search_delegate = None


def get_instance():
    """Retrieves the singleton instance of the ContentBrowserRegistryExtension.

    Returns:
        ContentBrowserRegistryExtension: The singleton instance if it exists, otherwise None."""
    return g_singleton
