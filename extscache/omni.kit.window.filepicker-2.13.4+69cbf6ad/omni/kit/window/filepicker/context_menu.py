# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["BaseContextMenu", "ContextMenu", "UdimContextMenu", "CollectionContextMenu", "ConnectionContextMenu", "BookmarkContextMenu", "LocalContextMenu"]
import asyncio
import os
import omni.ui as ui

from functools import partial
from typing import Callable
from omni.kit.widget.filebrowser import FileBrowserItem
from .view import FilePickerView
from .file_ops import *
import carb
import omni.kit.widget.context_menu
from .style import ICON_COMMON_PATH

class BaseContextMenu:
    """
    Base class popup menu for the hovered FileBrowserItem.  Provides API for users to add menu items.

    """
    def __init__(self, title: str = None, **kwargs):
        """
        Initialize the BaseContextMenu.

        Keyword Args:
            title (Optional[str]): The title of the context menu default `None`.
        """

        self._title: str = title
        self._view: FilePickerView = kwargs.get("view", None)
        self._checkpoint = kwargs.get("checkpoint", None)
        self._menu_dict: list = []
        self._context: dict = None

    @property
    def menu(self) -> ui.Menu:
        """Returns: obj:`omni.ui.Menu` The menu widget"""
        return omni.kit.widget.context_menu.get_instance().get_context_menu()

    @property
    def context(self) -> dict:
        """dict: Provides data to the callback.  Available keys are {'item', 'selected'}"""
        return self._context

    def show(
        self,
        item: FileBrowserItem,
        selected: List[FileBrowserItem] = [],
    ):
        """
        Creates the popup menu from definition for immediate display. Receives as input, information about the
        item.  These values are made available to the callback via the 'context' dictionary.

        Args:
            item (FileBrowseritem): Item for which to create menu.,
            selected ([FileBrowserItem]): List of currently selected items. Default [].

        """
        self._context = {}
        self._context["item"] = item
        self._context["selected"] = selected

        omni.kit.widget.context_menu.get_instance().show_context_menu(
            self._title,
            self._context,
            self._menu_dict,
        )

    def hide(self):
        """
        Hides the popup menu if it is shown.

        """
        context_menu = omni.kit.widget.context_menu.get_instance().get_context_menu()
        if context_menu:
            context_menu.hide()

    def add_menu_item(self, name: str, glyph: str, onclick_fn: Callable, show_fn: Callable, index: int = -1, separator_name: Optional[str] = None) -> str:
        """
        Adds menu item, with corresponding callbacks, to this context menu.

        Args:
            name (str): Name of the menu item (e.g. 'Open'), this name must be unique across the context menu.
            glyph (str): Associated glyph to display for this menu item.
            onclick_fn (Callable): This callback function is executed when the menu item is clicked. Function signature:
                void fn(context: Dict)
            show_fn (Callable): Returns True to display this menu item. Function signature: bool fn(context: Dict).
                For example, test filename extension to decide whether to display a 'Play Sound' action.
            index (int): The position that this menu item will be inserted to.
            separator_name (str): The separator name of the separator menu item. Default to '_placeholder_'. When the
                index is not explicitly set, or if the index is out of range, this will be used to locate where to add
                the menu item; if specified, the index passed in will be counted from the saparator with the provided
                name. This is for OM-86768 as part of the effort to match Navigator and Kit UX for Filepicker/Content Browser for context menus.

        Returns:
            str: Name of menu item if successful, None otherwise.

        """
        if not name:
            return None
        elif name in [item.get("name", None) for item in self._menu_dict]:
            # Reject duplicates
            return None

        menu_item = {"name": name, "glyph": glyph or ""}
        if onclick_fn:
            menu_item["onclick_fn"] = lambda context, name=name: onclick_fn(name, context["item"].path)
        if show_fn:
            menu_item["show_fn"] = lambda context: show_fn(context["item"].path)

        if index >= 0 and index <= len(self._menu_dict) and separator_name is None:
            pass
        else:
            if separator_name is None:
                separator_name = "_placeholder_"
            placeholder_index = (i for i, item in enumerate(self._menu_dict) if separator_name in item)
            matched = next(placeholder_index, len(self._menu_dict))
            index = max(min(matched + index, len(self._menu_dict)), 0)

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

    def destroy(self):
        """Destructor."""
        omni.kit.widget.context_menu.get_instance().close_menu()

class ContextMenu(BaseContextMenu):
    """
    Creates popup menu for the hovered FileBrowserItem.  In addition to the set of default actions below,
    users can add more via the add_menu_item API.

    """
    def __init__(self, **kwargs):
        """ Creates the ContextMenu for the file picker, including all common menu items """

        super().__init__(title="Context menu", **kwargs)

        self._menu_dict = [
            {
                "name": "Open in File Browser",
                "glyph": f"{ICON_COMMON_PATH}/icoOpen.svg",
                "onclick_fn": lambda context: open_in_file_browser(context["item"]),
                "show_fn": [lambda context: os.path.exists(context["item"].path)],
            },
            {
                "name": "New USD File",
                "glyph": f"{ICON_COMMON_PATH}/icoNewUsdFile.svg",
                "onclick_fn": lambda context: create_usd_file(context["item"]),
                "show_fn": [
                    lambda context: context["item"].is_folder,
                    lambda _: is_usd_supported(),
                    # OM-72882: should not allow creating folder/file in read-only directory
                    lambda context: context["item"].writeable,
                    lambda context: len(context["selected"]) <= 1,
                    lambda context: not context["item"] in self._view.all_collection_items(collection="omniverse"),
                ]
            },
            {
                "name": "Restore",
                "glyph": f"{ICON_COMMON_PATH}/icoRestore.svg",
                "onclick_fn": lambda context: restore_items(context["selected"], self._view),
                "show_fn": [
                    # OM-72882: should not allow deleting folder/file in read-only directory
                    lambda context: context["item"].writeable,
                    lambda context: context["item"].is_deleted,
                ],
            },
            {
                "name": "Refresh",
                "glyph": f"{ICON_COMMON_PATH}/icoRefresh.svg",
                "onclick_fn": lambda context: refresh_item(context["item"], self._view),
                "show_fn": [lambda context: len(context["selected"]) <= 1,]
            },
            {
                "name": "",
                "_add_on_begin_separator_": "",
            },
            {
                "name": "",
                "_add_on_end_separator_": "",
            },
            {
                "name": "New Folder",
                "glyph": f"{ICON_COMMON_PATH}/icoNewFolder.svg",
                "onclick_fn": lambda context: create_folder(context["item"]),
                "show_fn": [
                    lambda context: context["item"].is_folder,
                    # OM-72882: should not allow creating folder/file in read-only directory
                    lambda context: context["item"].writeable,
                    lambda context: len(context["selected"]) <= 1,
                    # TODO: Can we create any folder in the omniverer server's root folder?
                    #lambda context: not(context["item"].parent and \
                    #         context["item"].parent.path == "omniverse://"),
                ],
            },
            {
                "name": "",
            },
            {
                "name": "Create Checkpoint",
                "glyph":  f"{ICON_COMMON_PATH}/icoCreate.svg",
                "onclick_fn": lambda context: checkpoint_items(context["selected"], self._checkpoint),
                "show_fn": [
                    lambda context: not context["item"].is_folder,
                    lambda context: len(context["selected"]) == 1,
                ],
                "show_fn_async": is_item_checkpointable,
            },
            {
                "name": "",
            },
            {
                "name": "Rename",
                "glyph": f"{ICON_COMMON_PATH}/icoRename.svg",
                "onclick_fn": lambda context: rename_item(context["item"], self._view),
                "show_fn": [
                    lambda context: len(context["selected"]) == 1,
                    lambda context: context["item"].writeable,
                ]
            },
            {
                "name": "Delete",
                "glyph": f"{ICON_COMMON_PATH}/icoDeleteTrashcan.svg",
                "onclick_fn": lambda context: delete_items(context["selected"], self._view),
                "show_fn": [
                    # OM-72882: should not allow deleting folder/file in read-only directory
                    lambda context: context["item"].writeable,
                    lambda context: not context["item"].is_deleted,
                    # OM-94626: we couldn't delete when select nothing
                    lambda context: len(context["selected"]) >= 1,
                ],
            },
            {
                "name": "",
                "_placeholder_": ""
            },
            {
                "name": "Add Bookmark",
                "glyph": f"{ICON_COMMON_PATH}/icoAddBookmark.svg",
                "onclick_fn": lambda context: add_bookmark(context["item"], self._view),
                "show_fn": [lambda context: len(context["selected"]) <= 1,]
            },
            {
                "name": "Copy URL Link",
                "glyph": f"{ICON_COMMON_PATH}/icoLink.svg",
                "onclick_fn": lambda context: copy_to_clipboard(context["item"]),
                "show_fn": [lambda context: len(context["selected"]) <= 1,]
            },
            {
                "name": "Obliterate",
                "glyph": f"{ICON_COMMON_PATH}/icoDeleteTrashcan.svg",
                "onclick_fn": lambda context: obliterate_items(context["selected"], self._view),
                "show_fn": [
                    # OM-72882: should not allow deleting folder/file in read-only directory
                    lambda context: context["item"].writeable,
                    lambda context: context["item"].is_deleted,
                ],
            },
        ]


class UdimContextMenu(BaseContextMenu):
    """Creates popup menu for the hovered FileBrowserItem that are Udim nodes."""
    def __init__(self, **kwargs):
        super().__init__(title="Udim menu", **kwargs)

        self._menu_dict = [
            {
                "name": "Add Bookmark",
                "glyph": f"{ICON_COMMON_PATH}/icoAddBookmark.svg",
                "onclick_fn": lambda context: add_bookmark(context["item"], self._view),
            },
        ]


class CollectionContextMenu(BaseContextMenu):
    """Creates popup menu for the hovered FileBrowserItem that are collection nodes."""
    def __init__(self, **kwargs):
        super().__init__(title="Collection menu", **kwargs)

        # OM-75883: override menu dict for "Omniverse" collection node, there should be only
        # one menu entry, matching Navigator UX
        self._menu_dict = [
            {
                "name": "Add Server",
                "glyph": f"{ICON_COMMON_PATH}/icoAddCloudServer_18.svg",
                "onclick_fn": lambda context: add_connection(context["item"], self._view),
                "show_fn": [
                    lambda context: isinstance(context['item'], CollectionItem) and context['item'].add_new_item,
                ],
            },
        ]


class ConnectionContextMenu(BaseContextMenu):
    """Creates popup menu for the server connection FileBrowserItem grouped under Omniverse collection node."""
    def __init__(self, **kwargs):
        super().__init__(title="Connection menu", **kwargs)

        # OM-86768: matching context menu with Navigator UX for server connection
        # TODO: Add API Tokens and Clear Cached Folders once API is exposed in omni.client
        self._menu_dict = [
            {
                "name": "Reconnect Server",
                "glyph": f"{ICON_COMMON_PATH}/icoReconnectServer.svg",
                "onclick_fn": lambda context: refresh_connection(context["item"], self._view),
                "show_fn": [
                    lambda context: context["item"].parent.path.startswith("omniverse://"),
                ]
            },
            {
                "name": "",
            },
            {
                "name": "Rename",
                "glyph": f"{ICON_COMMON_PATH}/icoRename.svg",
                "onclick_fn": lambda context: rename_item(context["item"], self._view),
                "show_fn": [
                    lambda context: len(context["selected"]) == 1,
                ]
            },
            {
                "name": "",
            },
            {
                "name": "Log In",
                "glyph": f"{ICON_COMMON_PATH}/icoLogIn.svg",
                "onclick_fn": lambda context: refresh_connection(context["item"], self._view),
                "show_fn": [
                    lambda context: context["item"].parent.path.startswith("omniverse://"),
                    lambda context: not FilePickerView.is_connected(context["item"].path),
                ],
            },
            {
                "name": "Log Out",
                "glyph": f"{ICON_COMMON_PATH}/icoLogIn.svg",
                "onclick_fn": lambda context: log_out_from_connection(context["item"], self._view),
                "show_fn": [
                    lambda context: context["item"].parent.path.startswith("omniverse://"),
                    lambda context: FilePickerView.is_connected(context["item"].path),
                ],
            },
            {
                "name": "",
            },
            {
                "name": "About",
                "glyph": f"{ICON_COMMON_PATH}/icoQuestion.svg",
                "onclick_fn": lambda context: about_connection(context["item"]),
                "show_fn": [
                    lambda context: context["item"].parent.path.startswith("omniverse://"),
                ]
            },
            {
                "name": "Remove Server",
                "glyph": f"{ICON_COMMON_PATH}/icoDeleteTrashcan.svg",
                "onclick_fn": lambda context: remove_connection(context["item"], self._view),
            },
        ]


class BookmarkContextMenu(BaseContextMenu):
    """Creates popup menu for BookmarkItems."""
    def __init__(self, **kwargs):
        super().__init__(title="Bookmark menu", **kwargs)

        # OM-66726: Edit bookmark similar to Navigator
        self._menu_dict = [
            {
                "name": "Edit",
                "glyph": f"{ICON_COMMON_PATH}/icoRename.svg",
                "onclick_fn": lambda context: edit_bookmark(context['item'], self._view),
            },
            {
                "name": "Delete",
                "glyph": f"{ICON_COMMON_PATH}/icoDeleteTrashcan.svg",
                "onclick_fn": lambda context: delete_bookmark(context['item'], self._view),
            },
        ]

class LocalContextMenu(BaseContextMenu):
    """
    Creates popup menu for the hovered FileBrowserItem.  In addition to the set of default actions below,
    users can add more via the add_menu_item API.

    """
    def __init__(self, **kwargs):
        super().__init__(title="Context menu", **kwargs)

        self._menu_dict = [
            {
                "name": "Open in File Browser",
                "glyph": f"{ICON_COMMON_PATH}/icoOpen.svg",
                "onclick_fn": lambda context: open_in_file_browser(context["item"]),
                "show_fn": [lambda context: os.path.exists(context["item"].path)],
            },
            {
                "name": "New USD File",
                "glyph": f"{ICON_COMMON_PATH}/icoNewUsdFile.svg",
                "onclick_fn": lambda context: create_usd_file(context["item"]),
                "show_fn": [
                    lambda context: context["item"].is_folder,
                    lambda _: is_usd_supported(),
                    # OM-72882: should not allow creating folder/file in read-only directory
                    lambda context: context["item"].writeable,
                    lambda context: len(context["selected"]) <= 1,
                    lambda context: not context["item"] in self._view.all_collection_items(collection="omniverse"),
                ]
            },
            {
                "name": "Refresh",
                "glyph": f"{ICON_COMMON_PATH}/icoRefresh.svg",
                "onclick_fn": lambda context: refresh_item(context["item"], self._view),
                "show_fn": [lambda context: len(context["selected"]) <= 1,]
            },
            {
                "name": "",
                "_placeholder_": "",
            },
            {
                "name": "New Folder",
                "glyph": f"{ICON_COMMON_PATH}/icoAdd.svg",
                "onclick_fn": lambda context: create_folder(context["item"]),
                "show_fn": [
                    lambda context: context["item"].is_folder,
                    # OM-72882: should not allow creating folder/file in read-only directory
                    lambda context: context["item"].writeable,
                    lambda context: len(context["selected"]) <= 1,
                    # TODO: Can we create any folder in the omniverer server's root folder?
                    #lambda context: not(context["item"].parent and \
                    #         context["item"].parent.path == "omniverse://"),
                ],
            },
            {
                "name": "",
                "_placeholder_": ""
            },
            {
                "name": "Copy URL Link",
                "glyph": f"{ICON_COMMON_PATH}/icoLink.svg",
                "onclick_fn": lambda context: copy_to_clipboard(context["item"]),
                "show_fn": [lambda context: len(context["selected"]) <= 1,]
            },
        ]
