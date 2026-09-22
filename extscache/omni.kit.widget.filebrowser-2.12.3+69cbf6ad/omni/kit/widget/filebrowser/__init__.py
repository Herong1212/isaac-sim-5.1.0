# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
The basic UI widget and set of supporting classes for navigating the filesystem through a tree or grid view.
The filesystem can either be from your local machine or the Omniverse server.

Example:

.. code-block:: python

    With just a few lines of code, you can create a powerful, flexible tree view widget that you
    can embed into your view.

        filebrowser = FileBrowserWidget(
            "Omniverse",
            layout=SPLIT_PANES,
            mouse_pressed_fn=on_mouse_pressed,
            selection_changed_fn=on_selection_changed,
            drop_fn=drop_handler,
            filter_fn=item_filter_fn,
        )

Module Constants:

    layout: {LAYOUT_SINGLE_PANE_SLIM, LAYOUT_SINGLE_PANE_WIDE, LAYOUT_SPLIT_PANES, LAYOUT_DEFAULT}

"""
__all__ = [
    "FileBrowserWidget",
    "FileBrowserItemCard",
    "FileBrowserModel",
    "FileBrowserItem",
    "FileBrowserUdimItem",
    "FileBrowserItemFactory",
    "FileBrowserItemFields",
    "FileSystemModel",
    "FileSystemItem",
    "NucleusModel",
    "NucleusItem",
    "NucleusConnectionItem",
    "ColumnDelegateRegistry",
    "ColumnItem",
    "AbstractColumnDelegate",
    "find_thumbnails_for_files_async",
    "list_thumbnails_for_folder_async",
    "save_items_to_clipboard",
    "get_clipboard_items",
    "is_clipboard_cut",
    "is_path_cut",
    "clear_clipboard",
    "CONNECTION_ERROR_EVENT",
    "CONNECTION_ERROR_GLOBAL_EVENT",
    "MISSING_IMAGE_THUMBNAILS_EVENT",
    "MISSING_IMAGE_THUMBNAILS_GLOBAL_EVENT",
    "THUMBNAILS_GENERATED_EVENT",
    "THUMBNAILS_GENERATED_GLOBAL_EVENT",
    "ALERT_INFO",
    "ALERT_WARNING",
    "ALERT_ERROR",
    "LAYOUT_SINGLE_PANE_SLIM",
    "LAYOUT_SINGLE_PANE_WIDE",
    "LAYOUT_SPLIT_PANES",
    "LAYOUT_SINGLE_PANE_LIST",
    "LAYOUT_DEFAULT",
    "TREEVIEW_PANE",
    "LISTVIEW_PANE",
]
LAYOUT_SINGLE_PANE_SLIM = 1
LAYOUT_SINGLE_PANE_WIDE = 2
LAYOUT_SPLIT_PANES = 3
LAYOUT_SINGLE_PANE_LIST = 4
LAYOUT_DEFAULT = 3

TREEVIEW_PANE = 1
LISTVIEW_PANE = 2

from omni.kit.app import register_event_alias
import carb.events
CONNECTION_ERROR_GLOBAL_EVENT: str = "omni.kit.widget.filebrowser.CONNECTION_ERROR"
CONNECTION_ERROR_EVENT: int = carb.events.type_from_string(CONNECTION_ERROR_GLOBAL_EVENT)
register_event_alias(CONNECTION_ERROR_EVENT, CONNECTION_ERROR_GLOBAL_EVENT)

MISSING_IMAGE_THUMBNAILS_GLOBAL_EVENT: str = "omni.services.thumbnails.MISSING_IMAGE_THUMBNAILS"
MISSING_IMAGE_THUMBNAILS_EVENT: int = carb.events.type_from_string(MISSING_IMAGE_THUMBNAILS_GLOBAL_EVENT)
register_event_alias(MISSING_IMAGE_THUMBNAILS_EVENT, MISSING_IMAGE_THUMBNAILS_GLOBAL_EVENT)

THUMBNAILS_GENERATED_GLOBAL_EVENT: str = "omni.services.thumbnails.THUMBNAILS_GENERATED"
THUMBNAILS_GENERATED_EVENT: int = carb.events.type_from_string(THUMBNAILS_GENERATED_GLOBAL_EVENT)
register_event_alias(THUMBNAILS_GENERATED_EVENT, THUMBNAILS_GENERATED_GLOBAL_EVENT)

ALERT_INFO = 1
ALERT_WARNING = 2
ALERT_ERROR = 3

from .widget import FileBrowserWidget
from .card import FileBrowserItemCard
from .model import FileBrowserModel, FileBrowserItem, FileBrowserUdimItem, FileBrowserItemFactory, FileBrowserItemFields
from .filesystem_model import FileSystemModel, FileSystemItem
from .nucleus_model import NucleusModel, NucleusItem, NucleusConnectionItem
from .column_delegate_registry import ColumnDelegateRegistry
from .abstract_column_delegate import ColumnItem
from .abstract_column_delegate import AbstractColumnDelegate
from .thumbnails import find_thumbnails_for_files_async, list_thumbnails_for_folder_async
from .clipboard import save_items_to_clipboard, get_clipboard_items, is_clipboard_cut, is_path_cut, clear_clipboard
