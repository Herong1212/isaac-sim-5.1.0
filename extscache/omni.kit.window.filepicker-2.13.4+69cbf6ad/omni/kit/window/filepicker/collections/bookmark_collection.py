# Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["BookmarkItem", "BookmarkCollectionItem"]

from datetime import datetime
import re
from typing import Dict, Optional

import omni.client
from omni import ui
from omni.kit.widget.filebrowser import FileBrowserItem, FileBrowserItemFields, find_thumbnails_for_files_async
from .collection_item import CollectionItem
from ..style import ICON_PATH


class BookmarkItem(FileBrowserItem):

    _thumbnail_dict: Dict = {}

    def __init__(self, path: str, fields: Optional[FileBrowserItemFields] = None, is_folder: bool = True, name: Optional[str] = None):
        if name and not fields:
            access = omni.client.AccessFlags.READ | omni.client.AccessFlags.WRITE
            fields = FileBrowserItemFields(name, datetime.now(), 0, access)
        super().__init__(path, fields, is_folder=is_folder)
        self._models = (ui.SimpleStringModel(self.name), datetime.now(), ui.SimpleStringModel(""))
        self._path = self.format_bookmark_path(path)
        self._expandable = False

    def on_list_change_event(self, event: omni.client.ListEvent, entry: omni.client.ListEntry) -> bool:
        """
        Handles ListEvent changes, should update this item's children list with the corresponding ListEntry.

        Args:
            event (:obj:`omni.client.ListEvent`): One of of {UNKNOWN, CREATED, UPDATED, DELETED, METADATA, LOCKED, UNLOCKED}.
            entry (:obj:`omni.client.ListEntry`): Updated entry as defined by omni.client.

        """
        # bookmark item doesn't need to populate children, so always return False indicating item is
        # not changed
        return False

    def set_bookmark_path(self, path : str) -> None:
        """Sets the bookmark item path"""
        self._path = path

    @property
    def readable(self) -> bool:
        return (self._fields.permissions & omni.client.AccessFlags.READ) > 0

    @property
    def writeable(self) -> bool:
        return (self._fields.permissions & omni.client.AccessFlags.WRITE) > 0

    @property
    def expandable(self) -> bool:
        return self._expandable

    @expandable.setter
    def expandable(self, value: bool):
        self._expandable = value

    @property
    def hideable(self) -> bool:
        return False

    def format_bookmark_path(self, path: str):
        """Helper method to generate a bookmark path from the given path."""
        # OM-66726: Content Browser should edit bookmarks similar to Navigator
        if self.is_local_path(path) and not path.startswith("file://"):
            # Need to prefix "file://" for local path, so that local bookmark works in Navigator
            path = "file://" + path

        # make sure folder path ends with "/" so Navigator would recognize it as a directory
        if self._is_folder:
            path = path.rstrip("/") + "/"
        return path

    @staticmethod
    def is_bookmark_folder(path: str):
        """Helper method to check if a given path is a bookmark of a folder."""
        return path.endswith("/")

    @staticmethod
    def is_local_path(path: str) -> bool:
        """Returns True if given path is a local path"""
        return omni.client.is_local_url(path)

    async def get_custom_thumbnails_for_folder_async(self) -> Dict:
        """
        Returns the thumbnail dictionary for this (folder) item.

        Returns:
            Dict: With children url's as keys, and url's to thumbnail files as values.

        """
        if not self.is_folder:
            return {}

        # Files in the root folder only
        file_urls = []
        for _, item in self.children.items():
            if item.is_folder or item.path in self._thumbnail_dict:
                # Skip if folder or thumbnail previously found
                pass
            else:
                file_urls.append(item.path)

        thumbnail_dict = await find_thumbnails_for_files_async(file_urls)

        for url, thumbnail_url in thumbnail_dict.items():
            if url and thumbnail_url:
                self._thumbnail_dict[url] = thumbnail_url

        return self._thumbnail_dict


class BookmarkCollectionItem(CollectionItem):
    def __init__(self):
        super().__init__("bookmarks", "Bookmarks", f"{ICON_PATH}/bookmark.svg", order=0)

    def create_child_item(self, name: str, path: str, is_folder: bool = True) -> Optional[BookmarkItem]:
        if name and path:
            return BookmarkItem(path, is_folder=is_folder, name=name)
        else:
            return None
