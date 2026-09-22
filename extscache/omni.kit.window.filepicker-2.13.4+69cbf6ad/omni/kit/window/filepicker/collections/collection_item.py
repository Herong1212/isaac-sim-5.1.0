from abc import abstractmethod
from collections import namedtuple
from datetime import datetime
from typing import Dict, List, Optional, Callable

import carb
import omni.client
from omni.kit.widget.filebrowser import FileBrowserItem, FileBrowserItemFields
import omni.ui as ui
from ..style import ICON_PATH


CollectionItemFields = namedtuple('CollectionItemFields', FileBrowserItemFields._fields + ('order',))

class AddNewItem(FileBrowserItem):
    def __init__(self, name: str, icon: str = f"{ICON_PATH}/hdd_plus.svg"):
        """
        Item to add a new child.

        Args:
            name (str): Name of the item.
            icon (str): Icon of the item.
        """
        fields = FileBrowserItemFields(name, datetime.now(), 0, 0)
        super().__init__("", fields, is_folder=True)
        self._models = (ui.SimpleStringModel(name), datetime.now(), ui.SimpleStringModel(""))
        self._enable_sorting = False
        self.icon = icon

    @abstractmethod
    def add_new(self, on_success_fn: Callable[[str, str, bool, bool], None]) -> None:
        """
        Add a new child. Override this method to show UI to add a new child.

        Args:
            on_success_fn (Callable[[str, str, bool, bool], None]): Callback function that is called when the child is added.
                The function signature is: def on_success_fn(name: str, path: str, publish_event: bool, auto_select: bool) -> None:
        """
        return None


class CollectionItem(FileBrowserItem):
    def __init__(self, identifier: str, title: str, icon: str, access: int = omni.client.AccessFlags.READ | omni.client.AccessFlags.WRITE, populated: bool = True, order=10000):
        """
        Item for a collection which is a singleton that manages the a set of connections/bookmarks/drivers for the browser.

        Args:
            identifier (str): Identifier of the collection. Could be "omniverse" or "https".
            title (str): Title of the collection.
            icon (str): Icon of the collection.
            access (int): Access flags of the collection. Default is omni.client.AccessFlags.READ | omni.client.AccessFlags.WRITE.
            populated (bool): Whether the collection is populated. Default is True. If False, will populate the collection when list children.
            order (int): Order of the collection. Default is 10000.
        """
        self.identifier = identifier
        self.title = title
        self.order = order

        fields = CollectionItemFields(title, datetime.now(), 0, access, order)
        super().__init__(f"{identifier}://", fields, is_folder=True)
        self._models = (ui.SimpleStringModel(title), datetime.now(), ui.SimpleStringModel(""), ui.SimpleIntModel(order))

        self._enable_sorting = False  # Sort for all children in FileBrowserModel
        self._sort_connections = False  # Sort for children of this item only
        self.icon = icon
        self.populated = populated
        self.visible = True

        self._show_add_new_connection = carb.settings.get_settings().get_as_bool("/exts/omni.kit.window.filepicker/show_add_new_connection")
        if self._show_add_new_connection:
            self._add_new_item = self.create_add_new_item()
            if self._add_new_item:
                self._add_new_item._parent = self
        else:
            self._add_new_item = None

    @property
    def children(self) -> Dict[str, FileBrowserItem]:
        """dict[:obj:`FileBrowserItem`]: Children of this item.  Does not populate the item if not already populated."""
        children = {}
        with self._mutex_lock:
            if self._sort_connections:
                sorted_children = sorted(self._children.items())
            else:
                sorted_children = self._children.items()
            for name, child in sorted_children:
                children[name] = child

        # Always put the add new connection item at the end
        if self._add_new_item:
            children[self._add_new_item.name] = self._add_new_item
        return children

    @property
    def children_list(self) -> List[FileBrowserItem]:
        """List[:obj:`FileBrowserItem`]: List of avalible children of this item. Does not include the add new connection item."""
        return [item for item in self.children.values() if not isinstance(item, AddNewItem)] if self._add_new_item else self.children.values()

    @property
    def connections(self) -> List[FileBrowserItem]:
        """List[:obj:`FileBrowserItem`]: List of connections of this item."""
        return []

    @property
    def add_new_item(self) -> Optional[AddNewItem]:
        """Optional[:obj:`AddNewItem`]: Add new connection item."""
        return self._add_new_item

    def accept_url(self, url: str) -> bool:
        """
        Check if the url is accepted by the collection.

        Args:
            url (str): Url to check.

        Returns:
            bool: True if the url is accepted, False otherwise.
        """
        try:
            broken_url = omni.client.break_url(url)
            identifier = broken_url.scheme
            return identifier == self.identifier
        except Exception:
            carb.log_warn(f"Cannot parse url: {url}")
            return False

    def create_add_new_item(self) -> Optional[AddNewItem]:
        """
        Create a item to add a new connection. Override this method to create a custom item.

        Returns:
            Optional[:obj:`AddNewItem`]: Item to add a new connection. None if the collection does not support adding new connections.
        """
        return None

    def create_child_item(self, name: str, path: str, is_folder: bool = True) -> Optional[FileBrowserItem]:
        """
        Create a connection item. Override this method to create a custom connection item.

        Args:
            name (str): Name of the item.
            path (str): Path of the item.
            is_folder (bool): Whether the item is a folder.

        Returns:
            Optional[:obj:`FileBrowserItem`]: The created child item.
        """
        item = FileBrowserItem(name, path, is_folder)
        fields = FileBrowserItemFields(name, datetime.now(), 0, 0)
        item = FileBrowserItem(path, fields, is_folder=True)
        item._models = (ui.SimpleStringModel(item.name), datetime.now(), ui.SimpleStringModel(""))
        item._enable_sorting = False

        return item

    def add_path(self, name: str, path: str, is_folder: bool = True) -> Optional[FileBrowserItem]:
        """
        Add a path to the collection.

        Args:
            name (str): Name the path.
            path (str): Path.
            is_folder (bool): Whether the path represents a folder.

        Returns:
            Optional[:obj:`FileBrowserItem`]: The added child item.
        """
        item = self.create_child_item(name, path, is_folder)
        if item is None:
            return None
        return self.add_child(item)

    def add_child(self, item: FileBrowserItem) -> Optional[FileBrowserItem]:
        for child in self._children.values():
            if child.name == item.name and child.path == item.path:
                # Duplicate item.
                # It is possible that items may be added twice:
                # First from the add new connection dialog,
                # and second from the omni.client subscribe event.
                return None
            if child.name == item.name:
                carb.log_warn(f"Failed to add '{item.name}': '{item.path}' as name already exists.")
                return None
            elif child.path == item.path:
                carb.log_warn(f"Failed to add '{item.name}': '{item.path}' as dupliated path in '{child.name}'")
                return None

        return super().add_child(item)
