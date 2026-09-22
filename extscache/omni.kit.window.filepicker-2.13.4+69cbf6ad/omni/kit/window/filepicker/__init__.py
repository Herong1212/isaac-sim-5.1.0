# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
This Kit extension provides both a popup dialog as well as an embeddable widget that
you can add to your code for browsing the filesystem. Incorporates
:obj:`BrowserBarWidget` and :obj:`FileBrowserWidget` into a general-purpose utility.
The filesystem can either be from your local machine or the Omniverse server.

Example:

    With just a few lines of code, you can create a ready-made dialog window. Then,
    customize it by setting any number of attributes.

        filepicker = FilePickerDialog(
            "my-filepicker",
            apply_button_label="Open",
            click_apply_handler=on_click_open,
            click_cancel_handler=on_click_cancel )

        filepicker.show()

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
__all__ = [
    "UI_READY_EVENT",
    "UI_READY_GLOBAL_EVENT",
    "SETTING_PERSISTENT_SHOW_GRID_VIEW",
    "SETTING_PERSISTENT_GRID_VIEW_SCALE",
    "CollectionData",
    "FilePickerDialog",
    "FilePickerWidget",
    "FilePickerView",
    "FilePickerModel",
    "FilePickerAPI",
    "BaseContextMenu",
    "ContextMenu",
    "CollectionContextMenu",
    "ConnectionContextMenu",
    "BookmarkContextMenu",
    "UdimContextMenu",
    "LocalContextMenu",
    "DetailView",
    "DetailFrameController",
    "ToolBar",
    "TimestampWidget",
    "SearchDelegate",
    "SearchResultsModel",
    "SearchResultsItem",
    "delete_items",
    "move_items",
    "rename_item",
    "ConfirmItemDeletionDialog",
    "get_user_folders_dict",

    "CollectionItem",
    "AddNewItem",
]

import carb.events
UI_READY_GLOBAL_EVENT: str = "omni.kit.window.filepicker.UI_READY"
UI_READY_EVENT: int = carb.events.type_from_string(UI_READY_GLOBAL_EVENT)

from omni.kit.app import register_event_alias
register_event_alias(UI_READY_EVENT, UI_READY_GLOBAL_EVENT)

SETTING_ROOT = "/exts/omni.kit.window.filepicker/"
SETTING_PERSISTENT_ROOT = "/persistent" + SETTING_ROOT
SETTING_PERSISTENT_SHOW_GRID_VIEW = SETTING_PERSISTENT_ROOT + "show_grid_view"
SETTING_PERSISTENT_GRID_VIEW_SCALE = SETTING_PERSISTENT_ROOT + "grid_view_scale"

from .collections.collection_data import CollectionData
from .collections.collection_item import CollectionItem, AddNewItem
from .extension import FilePickerExtension
from .dialog import FilePickerDialog
from .widget import FilePickerWidget
from .view import FilePickerView
from .model import FilePickerModel
from .api import FilePickerAPI
from .context_menu import (
    BaseContextMenu,
    ContextMenu,
    CollectionContextMenu,
    ConnectionContextMenu,
    BookmarkContextMenu,
    UdimContextMenu,
    LocalContextMenu,
)
from .detail_view import DetailView, DetailFrameController
from .tool_bar import ToolBar
from .timestamp import TimestampWidget
try:
    from omni.kit.widget.search_delegate import SearchDelegate, SearchResultsModel, SearchResultsItem
except ModuleNotFoundError:  # pragma: no cover
    pass
from .file_ops import delete_items, rename_item, move_items
from .item_deletion_dialog import ConfirmItemDeletionDialog
from .utils import get_user_folders_dict
