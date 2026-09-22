# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ViewportDisplayMenuBarExtension", "get_instance"]

from typing import Optional
import omni.ext
from omni.kit.viewport.menubar.core import BaseCategoryItem
from .display_menu_container import DEFAULT_SECTION, DisplayMenuContainer


_extension_instance = None


class ViewportDisplayMenuBarExtension(omni.ext.IExt):
    """The Entry Point for the Display Settings in Viewport Menu Bar"""

    def on_startup(self, ext_id):
        self._display_menu = DisplayMenuContainer()  # noqa: PLW0201

        global _extension_instance
        _extension_instance = self

    def on_shutdown(self):
        self._display_menu.destroy()
        self._display_menu = None  # noqa: PLW0201

        global _extension_instance
        _extension_instance = None

    def register_custom_setting(self, text: str, setting_path: str):
        """
        Register custom display setting.

        Args:
            text (str): Text shown in menu item.
            setting_path (str): Setting path for custom display setting (bool value).
        """
        if self._display_menu:
            self._display_menu.register_custom_setting(text, setting_path)

    def deregister_custom_setting(self, text: str):
        """
        Deregister custom display setting.

        Args:
            text (str): Text shown in menu item.
        """
        if self._display_menu:
            self._display_menu.deregister_custom_setting(text)

    def register_custom_category_item(self, category: str, item: BaseCategoryItem, section: str = DEFAULT_SECTION):
        """
        Register custom display setting in category.

        Args:
            category (str): Category to add menu item. Can be an existing category e.g. "Heads Up Display" or a new one.
            item (item: BaseCategoryItem): Item to append.
            section (str): Optional section to organize category, default no section.
        """
        if self._display_menu:
            self._display_menu.register_custom_category_item(category, item, section)

    def deregister_custom_category_item(self, category: str, item: BaseCategoryItem):
        """
        Deregister custom display setting in category.

        Args:
            category (str): Category to remove menu item. Can be an existing category e.g. "Heads Up Display" or a new one.
            item (item: BaseCategoryItem): Item to remove.
        """
        if self._display_menu:
            self._display_menu.deregister_custom_category_item(category, item)


def get_instance() -> Optional[ViewportDisplayMenuBarExtension]:
    """
    Get extension instance.
    """
    return _extension_instance
