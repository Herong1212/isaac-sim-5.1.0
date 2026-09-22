# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from . import editor
from .layer_watch import LayerWatch
from .usda_edit_utils import is_extension_loaded
from omni.ui import get_custom_glyph_code
from pathlib import Path


class ContentMenu: # pragma: no cover
    """
    When this object is alive, Content Browser has the additional context menu
    with the items that allow to edit the USD files in the external editor.
    """

    def __init__(self):
        import omni.kit.content as content

        self._content_window = content.get_content_window()

        edit_menu_name = f'{get_custom_glyph_code("${glyphs}/menu_rename.svg")}  Edit...'
        self.__edit_menu_subscription = self._content_window.add_icon_menu(
            edit_menu_name, self._on_start_editing, self._is_edit_visible
        )

        stop_menu_name = f'{get_custom_glyph_code("${glyphs}/menu_delete.svg")}  Finish editing'
        self.__stop_menu_subscription = self._content_window.add_icon_menu(
            stop_menu_name, self._on_stop_editing, self._is_stop_visible
        )

    def _is_edit_visible(self, content_url):
        '''True if we can show the menu item "Edit"'''
        for ext in ["usd", "usda", "usdc"]:
            if content_url.endswith(f".{ext}"):
                return not LayerWatch().has_watch(content_url)

    def _on_start_editing(self, menu, value):
        """Start watching for the layer and run the editor"""
        file_path = self._content_window.get_selected_icon_path()

        usda_filename = LayerWatch().start_watch(file_path)
        editor.run_editor(usda_filename)

    def _is_stop_visible(self, content_url):
        """Returns true if the layer is already watched"""
        return LayerWatch().has_watch(content_url)

    def _on_stop_editing(self, menu, value):
        """Stop watching for the layer and remove the temporary files"""
        file_path = self._content_window.get_selected_icon_path()
        LayerWatch().stop_watch(file_path)

    def destroy(self):
        """Stop all watchers and remove the menu from the content browser"""
        del self.__edit_menu_subscription
        self.__edit_menu_subscription = None
        del self.__stop_menu_subscription
        self.__stop_menu_subscription = None
        self._content_window = None
        LayerWatch().stop_all()
