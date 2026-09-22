# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from __future__ import annotations
"""
Model and Item base classes for the file browser view.
"""
__all__ = ["FileBrowserItem", "FileBrowserItemFactory", "FileBrowserModel"]

import os
import re
import asyncio
import omni.client
import omni.kit.app
import threading
import omni.kit.async_engine as async_engine

from typing import List, Dict, Tuple, Union, Callable, Any, Optional
from datetime import datetime
from collections import OrderedDict
from omni import ui
from carb import log_warn
from omni.kit.helper.file_utils import asset_types
from .thumbnails import list_thumbnails_for_folder_async
from .column_delegate_registry import ColumnDelegateRegistry
from .date_format_menu import get_datetime_format
from . import CONNECTION_ERROR_GLOBAL_EVENT

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from omni.kit.window.filepicker.context_menu import BaseContextMenu

from collections import namedtuple

FileBrowserItemFields = namedtuple("FileBrowserItemFields", "name date size permissions")

compiled_regex = None

# A hacky way to get the number of fields in FileBrowserItemFields. Otherwise we need to set hardcoded "3".
BUILTIN_COLUMNS = len(dir(FileBrowserItemFields)) - len(dir(namedtuple("_", "")))


# OM-80351: Add decorator to wrap the item creation func for different models, so that error in item creation for one
#  single item won't affect the whole directory listing.
def handle_item_creation_exception(func: Callable):
    def wrapped_func(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            log_warn(f"Failed to create item, error encountered: {str(e)}")
            return None
        else:
            return result

    return wrapped_func


class NoLock(object):
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class FileBrowserItem(ui.AbstractItem):
    """
    Base class for the Filebrowser view Item.
    Should be sub-classed to implement specific filesystem behavior. The Constructor should not be
    called directly.  Instead there are factory methods available for creating instances when needed.

    Args:
        path (str): Path of the item.
        fields (:obj:`FileBrowserItemFields`): Fields of the item.
        is_folder (bool): Set to True if the item is a folder.
        is_deleted (bool): Set to True if the item is deleted.
    """

    # flags for item display
    expandable = True       # whether this type of FileBrowserItem is expandable
    hideable = True         # whether this type of FileBrowserItem is hideable

    def __init__(self, path: str, fields: FileBrowserItemFields, is_folder: bool = False, is_deleted: bool = False):
        super().__init__()
        self._path = path.replace("\\", "/")
        self._fields = fields  # Raw field values
        self._models = ()  # Formatted values for display
        self._parent = None
        self._children = OrderedDict()
        self._is_folder = is_folder
        self._is_deleted = is_deleted
        self._populated = False
        self._is_udim_file = False
        self._populate_func = None
        self._populate_future = None
        self._enable_sorting = True  # Enables children to be sorted
        self._icon = None
        self._alert: Tuple[int, str] = None
        self._item_changed  = False
        # Enables thread-safe reads/writes to shared data, e.g. children dict
        self._mutex_lock: threading.Lock = threading.Lock() if is_folder else NoLock()

    @property
    def name(self) -> str:
        """str: Item name."""
        return getattr(self._fields, "name", "")

    @property
    def path(self) -> str:
        """str: Full path name."""
        return self._path

    @property
    def fields(self) -> FileBrowserItemFields:
        """:obj:`FileBrowserItemFields`: A subset of the item's stats stored as a string tuple."""
        return self._fields

    @property
    def models(self) -> Tuple:
        """Tuple[:obj:`ui.AbstractValueModel`]: The columns of this item."""
        return self._models

    @property
    def parent(self) -> object:
        """:obj:`FileBrowserItem`: Parent of this item."""
        return self._parent

    @property
    def children(self) -> Dict[str, FileBrowserItem]:
        """dict[:obj:`FileBrowserItem`]: Children of this item.  Does not populate the item if not already populated."""
        children = {}
        with self._mutex_lock:
            for name, child in self._children.items():
                children[name] = child
        return children

    @property
    def is_folder(self) -> bool:
        """bool: True if this item is a folder."""
        return self._is_folder

    @property
    def item_changed (self) -> bool:
        """bool: True if this item is has been restore/delete aready."""
        return self._item_changed

    @item_changed .setter
    def item_changed (self, value: bool):
        self._item_changed  = value

    @property
    def is_deleted(self) -> bool:
        """bool: True if this item is a deleted folder/file."""
        return self._is_deleted

    @is_deleted.setter
    def is_deleted(self, value: bool):
        self._is_deleted = value

    @property
    def populated(self) -> bool:
        """bool: Get/Set item populated state."""
        return self._populated

    @populated.setter
    def populated(self, value: bool):
        self._populated = value

    @property
    def is_udim_file(self) -> bool:
        """bool: Get/Set item udim_file state."""
        return self._is_udim_file

    @is_udim_file.setter
    def is_udim_file(self, value: bool):
        self._is_udim_file = value

    @property
    def enable_sorting(self) -> bool:
        """bool: True if item's children are sortable."""
        return self._enable_sorting

    @property
    def icon(self) -> str:
        """str: Get/set path to icon file."""
        return self._icon

    @icon.setter
    def icon(self, icon: str):
        self._icon = icon

    @property
    def readable(self) -> bool:
        """ True if the item is readable. """
        return True

    @property
    def writeable(self) -> bool:
        """ True if the item is writeable. """
        return True

    @property
    def alert(self) -> Tuple[int, str]:
        """ Get/set alert level and message. """
        return self._alert

    @alert.setter
    def alert(self, alert: Tuple[int, str]):
        self._alert = alert

    @property
    def expandable(self) -> bool:
        """whether this FileBrowserItem is expandable. Override to change behavior"""
        return True

    @property
    def context_menu(self) -> Optional['BaseContextMenu']:
        """ Optionally provide a context menu to be show when this item is right-clicked. """
        return None

    @property
    def hideable(self) -> bool:
        """whether this FileBrowserItem is hideable. Override to change behavior"""
        return True

    async def on_populated_async(self,
            result=None,
            children: Optional[Dict[str, FileBrowserItem]]=None,
            callback: Optional[Callable[[Dict[str, FileBrowserItem]], None]]=None):
        """
        async callback after finish populating the item.

        Args:
            result(Any): result from populate async.
            children(Dict[str, :obj:`FileBrowserItem`]): dictionary of children items to pass to the callback.
            callback(Callable): function to call.Function signature:
                callback(result: Any, children: Dict[str, FileBrowserItem]) -> None

        """
        if isinstance(result, Exception) and not isinstance(result, asyncio.CancelledError):
            log_warn(f"Error populating '{self.path}': {str(result)}")
        else:
            # add udim placeholders
            FileBrowserUdimItem.populate_udim(self)

            if callback:
                callback(children)

    def get_subitem_model(self, index: int) -> object:
        """
        Return ith column of this item.

        Returns:
            :obj:`AbstractValueModel`

        """
        if self._models and index < len(self._models):
            return self._models[index]
        return None

    def populate_with_callback(self, callback: Callable, timeout: float = 10.0):
        """
        Populate this item if not already populated. When done, executes callback.

        Args:
            callback (Callable): Function signature is void callback(children: [FileBrowserItem]).
            timeout (float): Time out duration on failed server connections. Default 10.0.

        """
        if self._populate_future and not self._populate_future.done():
            # If there is an ongoing task for populating this folder
            # Just add the call back instead of cancel it.
            # populate_with_callback is only called by get_item_children
            # the callback only need one place holder parameter, so could use here.
            # simply cancel the furture cause the expand invalid, see OM-35385
            self._populate_future.add_done_callback(callback)
        else:
            self._populate_future = async_engine.run_coroutine(self.populate_async(lambda result, children: self.on_populated_async(result, children, callback), timeout=timeout))

    async def populate_async(self, callback_async: Callable = None, timeout: float = 10.0) -> Any:
        """
        Populate current item asynchronously if not already. Override this method to customize for specific
        file systems.

        Args:
            callback_async (Callable): Function signature is void callback(result, children: Dict[str, FileBrowserItem]),
                where result is an Exception type upon error.
            timeout (float): Time out duration on failed server connections. Default 10.0.

        Returns:
            Any: Result of executing callback.

        """
        if not self._populated:
            await self.populate_children_async()
            self._populated = True

        result = None
        if callback_async:
            return await callback_async(result, self.children)
        else:
            return result

    async def populate_children_async(self):
        for _, child in self._children.items():
            child._parent = self

    def on_list_change_event(self, event: omni.client.ListEvent, entry: omni.client.ListEntry) -> bool:
        """
        Virtual method to be implemented by sub-class. When called with a ListEvent, should update
        this item's children list with the corresponding ListEntry.

        Args:
            event (:obj:`omni.client.ListEvent`): One of of {UNKNOWN, CREATED, UPDATED, DELETED, METADATA, LOCKED, UNLOCKED}.
            entry (:obj:`omni.client.ListEntry`): Updated entry as defined by omni.client.

        """
        return True

    def add_child(self, item: object) -> Optional[FileBrowserItem]:
        """
        Add item as child.

        Args:
            item (:obj:`FileBrowserItem`): Child item.

        Returns:
            :obj:`FileBrowserItem`: The added item.
        """
        with self._mutex_lock:
            if item:
                self._children[item.name] = item
                item._parent = self

        return item

    def del_child(self, item_name: str) -> Optional[FileBrowserItem]:
        """
        Delete child item by name.

        Args:
            item_name (str): Name of child item.

        Returns:
            :obj:`FileBrowserItem`: The deleted item.

        """
        with self._mutex_lock:
            # Note: Pop (instead of del) item here so as not to destory it. Let garbage collection clean it up when
            # all references are released. Otherwise may result in a race condition (See OM-34661).
            return self._children.pop(item_name) if item_name in self._children.keys() else None

    async def get_custom_thumbnails_for_folder_async(self) -> Dict:
        """
        Return the thumbnail dictionary for this (folder) item.

        Returns:
            Dict: With children url's as keys, and url's to thumbnail files as values.

        """
        # If item is 'None' them interpret as root node
        if self.is_folder:
            return await list_thumbnails_for_folder_async(self.path)
        return {}

    @staticmethod
    def size_as_string(value: int) -> str:
        """ Convert data size in bytes to a human readable string. """
        one_kb = 1024.0
        one_mb = 1024.0 * one_kb
        one_gb = 1024.0 * one_mb
        return (
            f"{value/one_gb:.2f} GB" if value > one_gb else (
                f"{value/one_mb:.2f} MB" if value > one_mb else f"{value/one_kb:.2f} KB"
            )
        )

    @staticmethod
    def datetime_as_string(value: datetime) -> str:
        """ Convert datatime to string. """
        return value.strftime(f"{get_datetime_format()} %I:%M%p")

    def has_mouse_pressed_fn(self):
        """ Check if the item has a mouse pressed callback assigned. """
        return False

    def mouse_pressed_fn(self):
        """ Mouse pressed callback. """
        pass


    def update_permissions(self, new_permissions: 'omni.client.AccessFlags'):
        """
        Update item's permissions.

        Args:
            new_permissions(:obj:'omni.client.AccessFlags'): New permissions to this item.
        """
        self._fields = self._fields._replace(permissions=new_permissions)


class FileBrowserUdimItem(FileBrowserItem):
    """
    A Filebrowser UDIM item class for navigating a the local filesystem in a Filebrowser view.
    Sub-classed from :obj:`FileBrowserItem`.

    Args:
        path (str): path of the item.
        fields (:obj:`FileBrowserItemFields`): Fields of the item.
        is_folder (bool): Specify the item as a folder.
        range_start (int): Starting index of UDIM sequence.
        range_end (int): End index of UDIM sequence.
        repr_frame (int): Index in UDIM sequence.
    """
    def __init__(self, path: str, fields: FileBrowserItemFields, range_start: int, range_end: int, repr_frame: int = None):
        super().__init__(path, fields, is_folder=False)
        self._range_start = range_start
        self._range_end = range_end
        self._repr_frame = repr_frame

    @property
    def repr_path(self) -> str:
        """str: Full thumbnail path name."""
        url_parts = self._path.split(".<UDIM>.")
        if self._repr_frame and len(url_parts) == 2:
            return f"{url_parts[0]}.{self._repr_frame}.{url_parts[1]}"
        else:
            return self._path

    @staticmethod
    def populate_udim(parent: FileBrowserItem):
        """ Generate UDIM items under the given item. """
        udim_added_items = {}
        for _, item in parent._children.items():
            if not item.is_folder and asset_types.is_asset_type(item.path, asset_types.ASSET_TYPE_IMAGE):
                udim_full_path, udim_index = FileBrowserUdimItem.get_udim_sequence(item.path)
                if udim_full_path:
                    if not udim_full_path in udim_added_items:
                        udim_added_items[udim_full_path] = {"placeholder": udim_full_path, "range": [udim_index], "items": [item]}
                    else:
                        udim_added_items[udim_full_path]["range"].append(udim_index)
                        udim_added_items[udim_full_path]["items"].append(item)

        for udim in udim_added_items:
            range = udim_added_items[udim]["range"]
            udim_full_path = udim_added_items[udim]["placeholder"]
            udim_name = os.path.basename(udim_full_path)
            for item in udim_added_items[udim]["items"]:
                item.is_udim_file = True

            # get 1st udim item to use for thumbnail
            item = FileBrowserItemFactory.create_udim_item(udim_name, udim_full_path, range[0], range[-1], range[0])
            parent.add_child(item)

    @staticmethod
    def get_udim_sequence(full_path: str):
        """ Get the UDIM sequence by path. """
        import re

        global compiled_regex
        if compiled_regex == None:
            types = '|'.join([t[1:] for t in asset_types.asset_type_exts(asset_types.ASSET_TYPE_IMAGE)])
            numbers  = "[0-9][0-9][0-9][0-9]"
            compiled_regex = re.compile(r'([\w.-]+)(.)(' + numbers+ r')\.('+types+')$')

        udim_name  = compiled_regex.sub(r"\1\2<UDIM>.\4", full_path)
        if udim_name and udim_name != full_path:
            udim_index  = compiled_regex.sub(r"\3", os.path.basename(full_path))
            return udim_name, udim_index
        return None, None

class FileBrowserItemFactory:
    """
    Factory to create :obj:`FileBrowserItem` instances.
    """
    @staticmethod
    def create_group_item(name: str, path: str) -> FileBrowserItem:
        """
        Create a folder item at the given path.

        Args:
            name (str): name of the item.
            path (str): path of the item.
        """
        if not name:
            return None
        fields = FileBrowserItemFields(name, datetime.now(), 0, 0)
        item = FileBrowserItem(path, fields, is_folder=True)
        item._models = (ui.SimpleStringModel(item.name), datetime.now(), ui.SimpleStringModel(""))
        item._enable_sorting = False
        return item

    @staticmethod
    def create_dummy_item(name: str, path: str) -> FileBrowserItem:
        """
        Create a dummy item at the given path.

        Args:
            name (str): name of the item.
            path (str): path of the item.
        """
        if not name:
            return None
        fields = FileBrowserItemFields(name, datetime.now(), 0, 0)
        item = FileBrowserItem(path, fields, is_folder=False)
        item._models = (ui.SimpleStringModel(item.name), datetime.now(), ui.SimpleStringModel(""))
        return item

    @staticmethod
    def create_udim_item(name: str, path: str, range_start: int, range_end: int, repr_frame: int):
        """
        Create a UDIM item.

        Args:
            name (str): name of the item.
            path (str): path of the item.
            range_start (int): Starting index of UDIM sequence.
            range_end (int): End index of UDIM sequence.
            repr_frame (int): Index in UDIM sequence.
        """
        modified_time = datetime.now()
        fields = FileBrowserItemFields(name, modified_time, 0, omni.client.AccessFlags.READ)
        item = FileBrowserUdimItem(path, fields, range_start, range_end, repr_frame=repr_frame)
        item._models = (ui.SimpleStringModel(f"{name} [{range_start}-{range_end}]"), modified_time, ui.SimpleStringModel("N/A"))
        return item


class FileBrowserModel(ui.AbstractItemModel):
    """
    Base class for the Filebrowser view Model.
    Should be sub-classed to implement specific filesystem behavior.

    Args:
        name (str): Name of root item. If None given, then create an initally empty model.

    Keyword Args:
        drop_fn (Callable): Function called to handle drag-n-drops. Function signature:
            void drop_fn(dst_item: :obj:`FileBrowserItem`, src_item: :obj:`FileBrowserItem`)
        filter_fn (Callable): This handler should return True if the given Filebrowser view item is visible,
            False otherwise. Function signature: bool filter_fn(item: :obj:`FileBrowserItem`)
        sort_by_field (str): Name of column by which to sort items in the same folder. Default "name".
        sort_ascending (bool): Sort in ascending order. Default True.
        timeout (float): Timeout when updating item asynchronously.
    """

    def __init__(self, name: str = None, root_path: str = "", **kwargs):
        super().__init__()

        self._name = name
        self._root_path = root_path
        if name:
            self._root = self.create_root_item(name, root_path)
        else:
            self._root = None

        # By default, display these number of columns
        self._single_column = False
        self._show_udim_sequence = False
        self._drop_fn = kwargs.get("drop_fn", None)
        self._filter_fn = kwargs.get("filter_fn", None)
        self._sort_by_field = kwargs.get("sort_by_field", "name")
        self._sort_ascending = kwargs.get("sort_ascending", True)
        self._timeout = kwargs.get("timeout", 10.0)
        self._list_change_subscription = None
        # Enables thread-safe reads/writes to shared data
        self._pending_item_changed: List = []
        self._mutex_lock: threading.Lock = threading.Lock()
        self._drag_mime_data = None
        self._pending_drop_items: List = []

    @property
    def show_udim_sequence(self):
        """ Show the UDIM sequence. """
        return self._show_udim_sequence

    @show_udim_sequence.setter
    def show_udim_sequence(self, value: bool):
        self._show_udim_sequence = value

    @property
    def name(self) -> str:
        return self._name
 
    @property
    def path(self) -> str:
        return self._root_path

    @property
    def root(self) -> FileBrowserItem:
        """:obj:`FileBrowserItem`: Get/set the root item of this model."""
        return self._root

    @root.setter
    def root(self, item: FileBrowserItem):
        self._root = item
        self._item_changed(None)

    @property
    def sort_by_field(self) -> str:
        """:obj:`FileBrowserItem`: Get/set the sort-by field name."""
        return self._sort_by_field

    @sort_by_field.setter
    def sort_by_field(self, field: str):
        self._sort_by_field = field

    @property
    def sort_ascending(self) -> bool:
        """:obj:`FileBrowserItem`: Get/set the sort ascending state."""
        return self._sort_ascending

    @sort_ascending.setter
    def sort_ascending(self, value: bool):
        self._sort_ascending = value

    def create_root_item(self, name: str, path: str) -> Optional[FileBrowserItem]:
        """
        Create the root item. Override this method to create a custom root item.

        Args:
            name (str): Name of the root item.
            path (str): Path of the root item.

        Returns:
            :obj:`FileBrowserItem`: The root item.
        """
        return FileBrowserItemFactory.create_group_item(name, path)

    def set_filter_fn(self, filter_fn: Callable[[str], bool]):
        """ Set the handler that would return True if the given Filebrowser view item is visible,
            False otherwise. Function signature: bool filter_fn(item: :obj:`FileBrowserItem`)"""
        self._filter_fn = filter_fn

    def copy_presets(self, model: 'FileBrowserModel'):
        """ Reset our fields to default arguments from the given model. """
        # By default, display these number of columns
        if self._drop_fn is None:
            self._drop_fn = model._drop_fn
        if self._filter_fn is None:
            self._filter_fn = model._filter_fn
        self._single_column = model._single_column
        self._sort_by_field = model._sort_by_field
        self._sort_ascending = model._sort_ascending

    def get_item_children(self, item: FileBrowserItem) -> List[FileBrowserItem]:
        """
        Return the list of items that are nested to the given parent item.

        Args:
            item (:obj:`FileBrowserItem`): Parent item.

        Returns:
            list[:obj:`FileBrowserItem`]

        """
        # If item is 'None' them interpret as root node
        item_or_root = item or self._root
        if not item_or_root or not item_or_root.is_folder:
            return []
        if item_or_root.children:
            # Item could also have sort field, used for colletions now
            sort_by_field = item_or_root.sort_by_field if hasattr(item_or_root, "sort_by_field") and item_or_root.sort_by_field else self.sort_by_field

            children = list(item_or_root.children.values())
            if item_or_root.enable_sorting and sort_by_field in item_or_root._fields._fields:
                # Skip root level but otherwise, sort by specified field
                def get_value(item: FileBrowserItem):
                    value = getattr(item.fields, sort_by_field)
                    if isinstance(value,str):
                        value = value.lower()
                        # OM-12985: Sort str by nature value.(For example: put 10.usd after 2.usd)
                        convert = lambda text: int(text) if text.isdigit() else text
                        nature_value = lambda value: [convert(c) for c in re.split('([0-9]+)', value)]
                        return nature_value(value)
                    return value
                children = sorted(children, key=get_value, reverse=not self._sort_ascending)
                # List folders before files
                children = [
                    item
                    for item, is_folder in [(c, f) for f in [True, False] for c in children]
                    if item.is_folder == is_folder
                ]
            if self._filter_fn:
                children = self.filter_items(children)
        else:
            children = []

        if not item_or_root.populated:
            # If item not yet populated, then do it asynchronously. Force redraw when done. Note: When notifying
            # the TreeView with item_changed events, it's important to pass 'None' for the root node.
            item_or_root.populate_with_callback(lambda _: self._delayed_item_changed(item), timeout=self._timeout)

        return children

    def filter_items(self, items: List[FileBrowserItem]) -> List[FileBrowserItem]:
        """
        Return the items fitlered with the filter function set.
        """
        results = []
        for item in items:
            if item.is_folder == False:
                if (self._show_udim_sequence and item.is_udim_file) or \
                   (not self._show_udim_sequence and isinstance(item, FileBrowserUdimItem)):
                    continue

            if self._filter_fn and self._filter_fn(item):
                results.append(item)

        return results

    def get_item_value_model_count(self, item: FileBrowserItem) -> int:
        """
        Return the number of columns this model item contains.

        Args:
            item (:obj:`FileBrowserItem`): The item in question.

        Returns:
            int

        """
        if self._single_column:
            return 1

        if item is None:
            return self.builtin_column_count + len(ColumnDelegateRegistry().get_column_delegate_names())

        return len(item._models)

    def get_item_value_model(self, item: FileBrowserItem, index: int) -> object:
        """
        Get the value model associated with this item.

        Args:
            item (:obj:`FileBrowserItem`): The item in question.

        Returns:
            :obj:`AbstractValueModel`

        """
        if not item:
            item = self._root
        if item:
            return item.get_subitem_model(index)
        else:
            return None

    def auto_refresh_item(self, item: FileBrowserItem, throttle_frames: int = 4):
        """
        Watch the given folder and updates the children list as soon as its contents are changed.

        Args:
            item (:obj:`FileBrowserItem`): The folder item to watch.
            throttle_frames: Number of frames to throttle the UI refresh.

        """
        # If item is 'None' them interpret as root node
        item_or_root = item or self._root
        if not item_or_root or not item_or_root.is_folder:
            return

        self._list_change_subscription = omni.client.list_subscribe_with_callback(
            item_or_root.path, None,
            lambda result, event, entry: self.on_list_change_event(item_or_root, result, event, entry, throttle_frames=throttle_frames))

    def sync_up_item_changes(self, item: FileBrowserItem):
        """
        Scan given folder for missed changes; processes any changes found.

        Args:
            item (:obj:`FileBrowserItem`): The folder item to watch.

        """
        item_or_root = item or self._root
        if not item_or_root or not item_or_root.is_folder:
            return

        async def sync_up_item_changes_async(item: FileBrowserItem):
            if not item.is_folder:
                return

            entries = []
            try:
                include_deleted_option = omni.client.ListIncludeOption.INCLUDE_DELETED_FILES
                result, entries = await asyncio.wait_for(omni.client.list_async(item.path, include_deleted_option=include_deleted_option), timeout=self._timeout)
            except Exception as e:
                log_warn(f"Can't list directory '{item.path}': {str(e)}")
                return
            else:
                if result != omni.client.Result.OK:
                    result = RuntimeWarning(f"Error listing directory '{item.path}': {result}")
                    # Emit notification event
                    omni.kit.app.queue_event(CONNECTION_ERROR_GLOBAL_EVENT, {"url": item.path, "exception": result})
                    return

            children = item.children
            for entry in entries:
                if entry.relative_path not in children:
                    # Entry was added
                    self.on_list_change_event(item, result, omni.client.ListEvent.CREATED, entry)

            entry_names = [entry.relative_path for entry in entries]
            for name in children:
                if name not in entry_names:
                    if asset_types.is_udim_sequence(name):
                        continue

                    # Entry was deleted
                    MockListEntry = namedtuple("MockListEntry", "relative_path")
                    entry = MockListEntry(name)
                    self.on_list_change_event(item, result, omni.client.ListEvent.DELETED, entry)

        async_engine.run_coroutine(sync_up_item_changes_async(item_or_root))

    def on_list_change_event(self, item: FileBrowserItem,
        result: omni.client.Result, event: omni.client.ListEvent, entry: omni.client.ListEntry,
        throttle_frames: int = 4):
        """
        Process change events for the given folder.

        Args:
            item (:obj:`FileBrowserItem`): The folder item.
            result (omni.client.Result): Set by omni.client upon listing the folder.
            event (omni.client.ListEvent): Event type.
            throttle_frames: Number of frames to throttle the UI refresh.

        """
        if item and result == omni.client.Result.OK:
            item_changed = item.on_list_change_event(event, entry)
            # Limit item changed to these events (See OM-29866: Kit crashes during live sync due to auto refresh)
            if item_changed:
                # There may be many change events issued at once. To scale properly, we queue up the changes over a
                # few frames before triggering a single redraw of the UI.
                self._delayed_item_changed(item, throttle_frames=throttle_frames)

    def _delayed_item_changed(self, item: FileBrowserItem, throttle_frames: int = 1):
        """
        Produce item changed event after skipping a beat. This is necessary for guaranteeing that async updates
        are properly recognized and generate their own redraws.

        Args:
            item (:obj:`FileBrowserItem`): The item in question.

        """
        async def item_changed_async(item: FileBrowserItem, throttle_frames: int):
            with self._mutex_lock:
                if item in self._pending_item_changed:
                    return
                else:
                    self._pending_item_changed.append(item)

            # NOTE: Wait a few beats to absorb nearby change events so that we process the changes in one chunk.
            for _ in range(throttle_frames):
                await omni.kit.app.get_app().next_update_async()

            self._item_changed(item)
            with self._mutex_lock:
                try:
                    self._pending_item_changed.remove(item)
                except Exception:
                    pass

        async_engine.run_coroutine(item_changed_async(item, throttle_frames))

    @property
    def single_column(self):
        """The panel on the left side works in one-column mode"""
        return self._single_column

    @single_column.setter
    def single_column(self, value: bool):
        """Set the one-column mode"""
        self._single_column = not not value
        self._item_changed(None)

    @property
    def builtin_column_count(self):
        """Return the number of available columns without tag delegates"""
        return 3

    @property
    def drag_mime_data(self):
        """
        Return the string with the drag and drop payload.
        """
        return self._drag_mime_data

    @drag_mime_data.setter
    def drag_mime_data(self, data: Union[str, List[str]]):
        if isinstance(data, List):
            self._drag_mime_data = "\n".join(data)
        else:
            self._drag_mime_data = data

    def get_drag_mime_data(self, item: FileBrowserItem):
        """Return Multipurpose Internet Mail Extensions (MIME) data for be able to drop this item somewhere"""
        if self._drag_mime_data:
            return self._drag_mime_data
        return (item or self._root).path

    def drop_accepted(self, dst_item: FileBrowserItem, src_item: FileBrowserItem) -> bool:
        """
        Reimplemented from AbstractItemModel. Called to highlight target when drag and drop.
        Returns True if destination item is able to accept a drop. This function can be
        overriden to implement a different behavior.

        Args:
            dst_item (:obj:`FileBrowserItem`): Target item.
            src_item (:obj:`FileBrowserItem`): Source item.

        Returns:
            bool

        """
        if dst_item and dst_item.is_folder:
            # Returns True if item is a folder.
            return True
        return False

    def drop(self, dst_item: FileBrowserItem, source: Union[str, FileBrowserItem]):
        """
        Invoke user-supplied function to handle dropping source onto destination item.

        Args:
            dst_item (:obj:`FileBrowserItem`): Target item.
            src_item (:obj:`FileBrowserItem`): Source item.

        """
        if self._drop_fn and source:
            # OM-87075: Delay a frame and batch process source items, if the source arg passed in is a FileBrowserItem
            # FIXME: The reason for adding this delay is that, when the drop happens between within the same treeview
            #   (eg. selected multiple items and drop to another item in the same tree view the the list view panel)
            #   this ``drop`` is called once per selected item, this causes hang if in `_drop_fn` there's UI related
            #   operation; Thus, here we have to cache pending items and delay a frame;
            #   Ideally, ``omni.ui.TreeView`` might adjust the drop trigger to batch items instead of calling once per
            #   selected item.
            if isinstance(source, FileBrowserItem):
                with self._mutex_lock:
                    self._pending_drop_items.append(source)
            else:
                self._drop_fn(dst_item, source)
                return

            async def delay_drop():
                await omni.kit.app.get_app().next_update_async()
                if self._pending_drop_items:
                    self._drop_fn(dst_item, '\n'.join([item.path for item in self._pending_drop_items]))
                    self._pending_drop_items = []

            async_engine.run_coroutine(delay_drop())


    def destroy(self):
        """ Destructor. """
        self._root = None
        self._drop_fn = None
        self._filter_fn = None
        self._list_change_subscription = None
        self._loop = None
        self._pending_item_changed: List = []
        self._pending_drop_items.clear()
