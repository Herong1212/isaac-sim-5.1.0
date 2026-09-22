# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui

from typing import Callable, List
from functools import partial
from carb import log_warn
import omni.kit.widget.context_menu
from .checkpoints_model import CheckpointItem
from .style import get_style


class ContextMenu:
    """
    Creates popup menu for the hovered CheckpointItem.  In addition to the set of default actions below,
    users can add more via the add_menu_item API.

    """

    def __init__(self):
        self._menu_dict: list = []
        self._context: dict = None
        self._build_ui()

    @property
    def menu(self) -> ui.Menu:
        """:obj:`omni.ui.Menu` The menu widget"""
        return omni.kit.widget.context_menu.get_instance().get_context_menu()

    @property
    def context(self) -> dict:
        """dict: Provides data to the callback.  Available keys are {'item', 'is_bookmark', 'is_connection', 'selected'}"""
        return self._context

    def show(self, item: CheckpointItem, selected: List[CheckpointItem] = []):
        """
        Creates the popup menu from definition for immediate display. Receives as input, information about the
        item.  These values are made available to the callback via the 'context' dictionary.

        Args:
            item (CheckpointItem): Item for which to create menu.,
            selected (List[CheckpointItem]): List of currently selected items. Default [].

        """
        self._context = {}
        self._context["item"] = item
        self._context["selected"] = selected

        omni.kit.widget.context_menu.get_instance().show_context_menu(
            "",
            self._context,
            self._menu_dict,
        )

    def add_menu_item(self, name: str, glyph: str, onclick_fn: Callable, enable_fn: Callable, index: int = -1) -> str:
        """
        Adds menu item, with corresponding callbacks, to this context menu.

        Args:
            name (str): Name of the menu item (e.g. 'Open'), this name must be unique across the context menu.
            glyph (str): Associated glyph to display for this menu item.
            onclick_fn (Callable): This callback function is executed when the menu item is clicked. Function signature:
                void fn(name: str, item: CheckpointItem), where name is menu name.
            enable_fn (Callable): Returns 1 to enable this menu item, 0 to disable, -1 to hide.
                Function signature: bool fn(name: str, item: CheckpointItem).
            index (int): The position that this menu item will be inserted to.

        Returns:
            str: Name of menu item if successful, None otherwise.

        """
        if name and name in [item.get("name", None) for item in self._menu_dict]:
            # Reject duplicates
            return None

        menu_item = {"name": name, "glyph": glyph or ""}
        if onclick_fn:
            menu_item["onclick_fn"] = lambda context, name=name: onclick_fn(name, context["item"])
        if enable_fn:
            menu_item["enabled_fn"] = lambda context, name=name: enable_fn(name, context["item"])

        if index < 0 or index >= len(self._menu_dict):
            index = len(self._menu_dict)

        self._menu_dict.insert(index, menu_item)
        return name

    def delete_menu_item(self, name: str):
        """
        Deletes the menu item, with the given name, from this context menu.

        Args:
            name (str): Name of the menu item (e.g. 'Open').

        """
        if not name:
            return
        found = (i for i, item in enumerate(self._menu_dict) if name == item.get("name", None))
        for j in sorted([i for i in found], reverse=True):
            del self._menu_dict[j]

    def _build_ui(self):
        '''
        Example:

        self._menu_dict = [
            {
                "name": "Test",
                "glyph": "pencil.svg",
                "onclick_fn": lambda context: print(">>> TESTING"),
            },
        ]
        '''
        pass

    def _on_copy_to_clipboard(self, item: CheckpointItem):
        try:
            import omni.kit.clipboard

            omni.kit.clipboard.copy(item.path)
        except ImportError:
            log_warn("Warning: Could not import omni.kit.clipboard.")

    def destroy(self):
        self._menu_dict = None
        self._context = None

        omni.kit.widget.context_menu.get_instance().close_menu()
