# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
Model and Item classes for navigating a Nucleus Server.
"""
__all__ = ["NucleusItem", "NucleusItemFactory", "NucleusModel", "NucleusConnectionItem"]
import asyncio
from datetime import datetime
from typing import Callable, Any

import omni.client
import omni.kit.app
from omni import ui
from .model import FileBrowserItem, FileBrowserItemFields, FileBrowserModel, handle_item_creation_exception
from .style import ICON_PATH
from . import CONNECTION_ERROR_GLOBAL_EVENT

class NucleusItem(FileBrowserItem):
    """
    A Filebrowser item class for navigating a Nucleus server in a Filebrowser view.
    Sub-classed from :obj:`FileBrowserItem`.

    Args:
        path (str): Path of the item.
        fields (:obj:`FileBrowserItemFields`): Fields of the item.
        is_folder (bool): Specify the item as a folder.
        is_deleted (bool): Specify the item as deleted.
    """
    def __init__(self, path: str, fields: FileBrowserItemFields, is_folder: bool = True, is_deleted: bool = False):
        super().__init__(path, fields, is_folder=is_folder, is_deleted=is_deleted)

    async def populate_async(self, callback_async: Callable = None, timeout: float = 10.0) -> Any:
        """
        Populate current item asynchronously if not already. Overrides base method.

        Args:
            callback_async (Callable): Function signature is void callback(result, children: [FileBrowserItem]),
                where result is an Exception type upon error.
            timeout (float): Time out duration on failed server connections. Default 10.0.

        Returns:
            Any: Result of executing callback.

        """
        result = omni.client.Result.OK
        if not self.populated:
            entries = []
            prev_children = {}
            try:
                result, entries = await asyncio.wait_for(omni.client.list_async(self.path), timeout=timeout)
            except asyncio.CancelledError:
                # NOTE: Return early if operation cancelled, without marking as 'populated'.
                return omni.client.Result.OK
            except (asyncio.TimeoutError, Exception) as e:
                result = omni.client.Result.ERROR
            finally:
                if result == omni.client.Result.OK:
                    prev_children = self.children
                    self.children.clear()
                else:
                    result = RuntimeWarning(f"Error listing directory '{self.path}': {result}")
                    # Emit connection error event
                    omni.kit.app.queue_event(CONNECTION_ERROR_GLOBAL_EVENT, {"url": self.path, "exception": result})

            for entry in entries:
                full_path = f"{self.path}/{entry.relative_path}"
                name = entry.relative_path.rstrip("/")
                create_item = NucleusItemFactory.create_entry_item(entry, full_path)
                prev_item = prev_children.get(name, None)
                if prev_item and prev_item.writeable != create_item.writeable:
                    create_item.item_changed = True
                self.add_child(create_item)

            # NOTE: Mark this item populated even when there's an error so we don't repeatedly try.
            self.populated = True

        if callback_async:
            try:
                return await callback_async(result, self.children)
            except asyncio.CancelledError:
                return omni.client.Result.OK
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
                self.add_child(NucleusItemFactory.create_entry_item(entry, full_path))
            else:
                item = self.children[child_name]
                if item.is_deleted:
                    item.is_deleted = False
                    item.item_changed  = True
            item_changed = True
        elif event == omni.client.ListEvent.DELETED:
            if child_name in self.children:
                item = self.children[child_name]
                item.is_deleted = True
                item.item_changed = True
            item_changed = True
        elif event == omni.client.ListEvent.OBLITERATED:
            self.del_child(child_name)
            item_changed = True
        elif event == omni.client.ListEvent.UPDATED:
            child = self.children.get(child_name)
            if child:
                # Update file size
                size_model = child.get_subitem_model(2)
                size_model.set_value(FileBrowserItem.size_as_string(entry.size))
        elif event == omni.client.ListEvent.METADATA:
            if child_name in self.children:
                item = self.children[child_name]
                if item._fields.permissions != entry.access:
                    item.item_changed = True
                    # Update file permissions
                    item.update_permissions(entry.access)
                    item_changed = True

        return item_changed

    @property
    def readable(self) -> bool:
        """ Return True if the item is readable. """
        return (self._fields.permissions & omni.client.AccessFlags.READ) > 0

    @property
    def writeable(self) -> bool:
        """ Return True if the item is writable. """
        return (self._fields.permissions & omni.client.AccessFlags.WRITE) > 0


class NucleusConnectionItem(NucleusItem):
    """
    NucleusItem that represents a nucleus connection.
    Sub-classed from :obj:`NucleusItem`.

    Args:
        path (str): Path of the item.
        fields (:obj:`FileBrowserItemFields`): Fields of the item.
        is_folder (bool): Specify the item as a folder.
        is_deleted (bool): Specify the item as deleted.
    """
    def __init__(self, path: str, fields: FileBrowserItemFields, is_folder: bool = True):
        super().__init__(path, fields, is_folder=is_folder)
        self._signed_in = False

    @property
    def signed_in(self):
        """ Return True when signed in to the Nucleus server. """
        return self._signed_in

    @signed_in.setter
    def signed_in(self, value):
        self._signed_in = value


class NucleusItemFactory:
    """
    Factory to create :obj:`NucleusItem` instances.
    """
    @staticmethod
    @handle_item_creation_exception
    def create_group_item(name: str, path: str) -> NucleusItem:
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
        item = NucleusConnectionItem(path, fields)
        item._models = (ui.SimpleStringModel(item.name), datetime.now(), ui.SimpleStringModel(""))
        return item

    @staticmethod
    @handle_item_creation_exception
    def create_entry_item(entry: omni.client.ListEntry, path: str) -> NucleusItem:
        """
        Create a file item at the given path.

        Args:
            entry (:obj:`omni.client.ListEntry`): entry as defined by omni.client.
            path (str): path of the item.
        """
        if not entry:
            return None
        name = entry.relative_path.rstrip("/")

        modified_time = entry.modified_time
        fields = FileBrowserItemFields(name, modified_time, entry.size, entry.access)
        is_folder = (entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN) > 0
        is_deleted = (entry.flags & omni.client.ItemFlags.IS_DELETED) > 0
        item = NucleusItem(path, fields, is_folder=is_folder, is_deleted=is_deleted)

        size_model = ui.SimpleStringModel(FileBrowserItem.size_as_string(entry.size))
        item._models = (ui.SimpleStringModel(item.name), modified_time, size_model)
        return item


class NucleusModel(FileBrowserModel):
    """
    A Filebrowser model class for navigating a Nucleus server in a Filebrowser view.
    Sub-classed from :obj:`FileBrowserModel`.

    Args:
        name (str): Name of root item..
        root_path (str): Root path. If None, then create empty model. Example: "omniverse://ov-content".

    Keyword Args:
        drop_fn (Callable): Function called to handle drag-n-drops. Function signature:
            void drop_fn(dst_item: :obj:`FileBrowserItem`, src_item: :obj:`FileBrowserItem`)
        filter_fn (Callable): This handler should return True if the given Filebrowser view item is visible,
            False otherwise. Function signature: bool filter_fn(item: :obj:`FileBrowserItem`)
        sort_by_field (str): Name of column by which to sort items in the same folder. Default "name".
        sort_ascending (bool): Sort in ascending order. Default True.
    """

    def __init__(self, name: str, root_path: str, **kwargs):
        super().__init__(name=name, root_path=root_path, **kwargs)
        
    def create_root_item(self, name: str, path: str) -> FileBrowserItem:
        import carb.settings
        
        item = NucleusItemFactory.create_group_item(name, path)
        theme = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"
        item.icon = f"{ICON_PATH}/{theme}/hdd.svg"
        return item
