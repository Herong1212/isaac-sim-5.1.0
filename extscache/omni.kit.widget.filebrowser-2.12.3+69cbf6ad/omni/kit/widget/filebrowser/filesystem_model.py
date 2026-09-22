# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
Model and Item classes for navigating the local file system on the machine.
"""
__all__ = ["FileSystemItem", "FileSystemItemFactory", "FileSystemModel"]
import os
import stat
import asyncio
import omni.client

from datetime import datetime
from typing import Callable, Any
from omni import ui
from .model import FileBrowserItem, FileBrowserItemFields, FileBrowserModel, handle_item_creation_exception
from .style import ICON_PATH
from carb import log_warn


class FileSystemItem(FileBrowserItem):
    """
    A Filebrowser item class for navigating a the local filesystem in a Filebrowser view.
    Sub-classed from :obj:`FileBrowserItem`.

    Args:
        path (str): Path of the item.
        fields (:obj:`FileBrowserItemFields`): Fields of the item.
        is_folder (bool): Specify the item as a folder.
    """
    def __init__(self, path: str, fields: FileBrowserItemFields, is_folder: bool = False):
        super().__init__(path, fields, is_folder=is_folder)

    async def populate_async(self, callback_async: Callable, timeout: float = 10.0) -> Any:
        """
        Populate current item asynchronously if not already. Overrides base method.

        Args:
            callback_async (Callable): Function signature is void callback(result, children: [FileBrowserItem]),
                where result is an Exception type upon error.
            timeout (float): Time out duration on failed server connections. Default 10.0.

        Returns:
            Any: Result of executing callback.

        """
        result = None
        if not self.populated:
            if self.is_folder:
                try:
                    with os.scandir(self.path) as it:
                        prev_children = self.children
                        self.children.clear()
                        entries = {entry.name: entry for entry in it}
                        for name in sorted(entries):
                            entry = entries[name]
                            try:
                                if not FileSystemItem.keep_entry(entry):
                                    continue
                                create_item = FileSystemItemFactory.create_entry_item(entry)
                            except PermissionError:
                                # If we do not have permission to the child entry, skip and continue.
                                log_warn(f"Can't list files. Permission denied for {entry.path}")
                                continue

                            prev_item = prev_children.get(name, None)
                            if prev_item and prev_item.writeable != create_item.writeable:
                                create_item.item_changed = True
                            self.add_child(create_item)
                except asyncio.CancelledError:
                    # NOTE: Return early if operation cancelled, without marking as 'populated'.
                    return None
                except PermissionError as e:
                    log_warn(f"Can't list files. Permission denied for {self.path}")
                    result = e
                except Exception as e:
                    result = e

            # NOTE: Mark this item populated even when there's an error so we don't repeatedly try.
            self.populated = True

        if callback_async:
            try:
                return await callback_async(result, self.children)
            except asyncio.CancelledError:
                return None
        else:
            return result

    def on_list_change_event(self, event: omni.client.ListEvent, entry: omni.client.ListEntry) -> bool:
        """
        Handle ListEvent changes, should update this item's children list with the corresponding ListEntry.

        Args:
            event (:obj:`omni.client.ListEvent`): One of of {UNKNOWN, CREATED, UPDATED, DELETED, METADATA, LOCKED, UNLOCKED}.
            entry (:obj:`omni.client.ListEntry`): Updated entry as defined by omni.client.

        """
        if not entry:
            return False
        item_changed = False
        child_name = entry.relative_path
        child_name = child_name[:-1] if child_name.endswith("/") else child_name
        full_path = f"{self.path}/{entry.relative_path}"
        if event == omni.client.ListEvent.CREATED:
            if not child_name in self.children:
                item_changed = True
            self.add_child(FileSystemItemFactory.create_omni_entry_item(entry, full_path))
        elif event == omni.client.ListEvent.DELETED:
            self.del_child(child_name)
            item_changed = True
        elif event == omni.client.ListEvent.UPDATED:
            child = self.children.get(child_name)
            if child:
                # Update file size
                size_model = child.get_subitem_model(2)
                size_model.set_value(FileBrowserItem.size_as_string(entry.size))

        return item_changed

    @staticmethod
    def keep_entry(entry: os.DirEntry) -> bool:
        """
        Return True if we want to keep the given entry.

        Args:
            entry (:obj:`os.DirEntry`): directory entry.
        """
        if os.name == "nt":
            # On Windows, test for hidden directories & files
            try:
                file_attrs = entry.stat().st_file_attributes
            except:
                return False
            if file_attrs & stat.FILE_ATTRIBUTE_SYSTEM:
                return False
        elif os.name == "posix":
            if entry.is_symlink():
                try:
                    entry.stat()
                except:
                    # NOTE: What accounts for the return value here?
                    return False
        return True

    @property
    def readable(self) -> bool:
        """
        Return True if the item is readable.
        """
        return (self._fields.permissions & omni.client.AccessFlags.READ) > 0

    @property
    def writeable(self) -> bool:
        """
        Return True if the item is writable.
        """
        return (self._fields.permissions & omni.client.AccessFlags.WRITE) > 0


class FileSystemItemFactory:
    """
    Factory to create :obj:`FileSystemItem` instances.
    """
    @staticmethod
    @handle_item_creation_exception
    def create_group_item(name: str, path: str) -> FileSystemItem:
        """
        Create a folder item at the given path.

        Args:
            name (str): name of the item.
            path (str): path of the item.
        """
        if not name:
            return None
        access = omni.client.AccessFlags.READ | omni.client.AccessFlags.WRITE
        fields = FileBrowserItemFields(name, datetime.now(), 0, access)
        item = FileSystemItem(path, fields, is_folder=True)
        item._models = (ui.SimpleStringModel(item.name), datetime.now(), ui.SimpleStringModel(""))
        return item

    @staticmethod
    @handle_item_creation_exception
    def create_entry_item(entry: os.DirEntry) -> FileSystemItem:
        """
        Create a local file item from the entry.
        """
        if not entry:
            return None
        modified_time = datetime.fromtimestamp(entry.stat().st_mtime)
        stats = entry.stat()
        # OM-73238 Translate system access flags to omni.client flags
        access = 0
        if entry.stat().st_mode & stat.S_IRUSR:
            access |= omni.client.AccessFlags.READ
        if entry.stat().st_mode & stat.S_IWUSR:
            access |= omni.client.AccessFlags.WRITE
        fields = FileBrowserItemFields(entry.name, modified_time, stats.st_size, access)
        item = FileSystemItem(entry.path, fields, is_folder=entry.is_dir())

        size_model = ui.SimpleStringModel(FileBrowserItem.size_as_string(entry.stat().st_size))
        item._models = (ui.SimpleStringModel(item.name), modified_time, size_model)
        return item

    @staticmethod
    @handle_item_creation_exception
    def create_omni_entry_item(entry: omni.client.ListEntry, path: str) -> FileSystemItem:
        """
        Create a file item at the given path.

        Args:
            entry (:obj:`omni.client.ListEntry`): entry as defined by omni.client.
            path (str): path of the item.
        """
        if not entry:
            return None
        name = entry.relative_path
        name = name[:-1] if name.endswith("/") else name
        modified_time = entry.modified_time
        fields = FileBrowserItemFields(name, modified_time, entry.size, entry.access)
        is_folder = (entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN) > 0
        item = FileSystemItem(path, fields, is_folder=is_folder)

        size_model = ui.SimpleStringModel(FileBrowserItem.size_as_string(entry.size))
        item._models = (ui.SimpleStringModel(item.name), modified_time, size_model)
        return item


class FileSystemModel(FileBrowserModel):
    """
    A Filebrowser model class for navigating a the local filesystem in a Filebrowser view.
    Sub-classed from :obj:`FileBrowserModel`.

    Args:
        name (str): Name of root item..
        root_path (str): Root path. If None, then create empty model. Default "C:".

    Keyword Args:
        drop_fn (Callable): Function called to handle drag-n-drops. Function signature:
            void drop_fn(dst_item: :obj:`FileBrowserItem`, src_item: :obj:`FileBrowserItem`)
        filter_fn (Callable): This handler should return True if the given Filebrowser view item is visible,
            False otherwise. Function signature: bool filter_fn(item: :obj:`FileBrowserItem`)
        sort_by_field (str): Name of column by which to sort items in the same folder. Default "name".
        sort_ascending (bool): Sort in ascending order. Default True.
    """

    def __init__(self, name: str, root_path: str = "C:", **kwargs):
        import carb.settings

        super().__init__(**kwargs)
        if not root_path:
            return
        if not root_path.endswith("/"):
            root_path += "/"
        self._root = FileSystemItemFactory.create_group_item(name, root_path)

        theme = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"
        self._root.icon = f"{ICON_PATH}/{theme}/hdd.svg"
