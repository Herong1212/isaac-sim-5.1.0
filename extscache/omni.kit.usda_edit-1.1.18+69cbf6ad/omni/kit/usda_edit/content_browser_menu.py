# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.usd

from . import editor
from .layer_watch import LayerWatch
from .usda_edit_utils import is_extension_loaded, post_notification
import os


def content_browser_available() -> bool:
    """Returns True if the extension "omni.kit.widget.content_browser" is loaded"""
    return is_extension_loaded("omni.kit.window.content_browser")


class ContentBrowserMenu:
    """
    When this object is alive, Layers 2.0 has the additional context menu
    with the items that allow to edit the layer in the external editor.
    """

    def __init__(self):
        import omni.kit.window.content_browser as content

        self._content_window = content.get_content_window()
        self.__start_name = self._content_window.add_context_menu(
            "Edit...", "menu_rename.svg", ContentBrowserMenu.start_editing, ContentBrowserMenu.is_not_editing
        )
        self.__end_name = self._content_window.add_context_menu(
            "Finish editing", "menu_delete.svg", ContentBrowserMenu.stop_editing, ContentBrowserMenu.is_editing
        )

    def destroy(self): # pragma: no cover
        """Stop all watchers and remove the menu from Layers 2.0"""
        if content_browser_available():
            self._content_window.delete_context_menu(self.__start_name)
            self._content_window.delete_context_menu(self.__end_name)
        self.__start_name = None
        self.__end_name = None
        self._content_window = None
        LayerWatch().stop_all()

    @staticmethod
    def start_editing(menu: str, content_url: str):
        """Start watching for the layer and run the editor"""
        usda_filename = LayerWatch().start_watch(content_url)
        if not editor.run_editor(usda_filename):
            post_notification("No text editor can be found!")

    @staticmethod
    def stop_editing(menu: str, content_url: str):
        """Stop watching for the layer and remove the temporary files"""
        LayerWatch().stop_watch(content_url)

    @staticmethod
    def is_editing(content_url: str) -> bool:
        """Returns true if the layer is already watched"""
        return LayerWatch().has_watch(content_url)

    @staticmethod
    def is_not_editing(content_url: str) -> bool:
        """Returns true if the layer is not watched"""
        return omni.usd.is_usd_writable_filetype(content_url) and not ContentBrowserMenu.is_editing(content_url)
