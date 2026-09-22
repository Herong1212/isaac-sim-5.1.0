# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["FilePickerView"]
import os
import platform
import asyncio
import traceback
import omni.kit.app
import omni.client
import carb.settings
import omni.kit.async_engine as async_engine

from typing import Callable, List, Optional
from carb import eventdispatcher, log_warn
from omni.kit.widget.filebrowser import (
    FileBrowserWidget,
    FileBrowserModel,
    FileBrowserItem,
    NucleusConnectionItem,
    LAYOUT_DEFAULT,
    TREEVIEW_PANE,
    LISTVIEW_PANE,
    CONNECTION_ERROR_GLOBAL_EVENT
)
try:
    from omni.kit.widget.nucleus_connector import disconnect, reconnect, connect_with_dialog, NUCLEUS_CONNECTION_SUCCEEDED_GLOBAL_EVENT
    have_nucleus = True
except ModuleNotFoundError:
    have_nucleus = False
from .model import FilePickerModel
from .collections.bookmark_collection import BookmarkItem
from .collections.collection_data import CollectionData
from .collections.collection_item import CollectionItem, AddNewItem
from .navigation_model import NavigationModel
from .utils import exec_after_redraw
from .style import ICON_PATH

BOOKMARK_ADDED_GLOBAL_EVENT: str = "omni.kit.window.filepicker.BOOKMARK_ADDED"
BOOKMARK_DELETED_GLOBAL_EVENT: str = "omni.kit.window.filepicker.BOOKMARK_DELETED"
BOOKMARK_RENAMED_GLOBAL_EVENT: str = "omni.kit.window.filepicker.BOOKMARK_RENAMED"
NUCLEUS_SERVER_ADDED_GLOBAL_EVENT: str = "omni.kit.window.filepicker.NUCLEUS_SERVER_ADDED"
NUCLEUS_SERVER_DELETED_GLOBAL_EVENT: str = "omni.kit.window.filepicker.NUCLEUS_SERVER_DELETED"
NUCLEUS_SERVER_RENAMED_GLOBAL_EVENT: str = "omni.kit.window.filepicker.NUCLEUS_SERVER_RENAMED"

import carb.events
BOOKMARK_ADDED_EVENT: int = carb.events.type_from_string(BOOKMARK_ADDED_GLOBAL_EVENT)
omni.kit.app.register_event_alias(BOOKMARK_ADDED_EVENT, BOOKMARK_ADDED_GLOBAL_EVENT)
BOOKMARK_DELETED_EVENT: int = carb.events.type_from_string(BOOKMARK_DELETED_GLOBAL_EVENT)
omni.kit.app.register_event_alias(BOOKMARK_DELETED_EVENT, BOOKMARK_DELETED_GLOBAL_EVENT)
BOOKMARK_RENAMED_EVENT: int = carb.events.type_from_string(BOOKMARK_RENAMED_GLOBAL_EVENT)
omni.kit.app.register_event_alias(BOOKMARK_RENAMED_EVENT, BOOKMARK_RENAMED_GLOBAL_EVENT)
NUCLEUS_SERVER_ADDED_EVENT: int = carb.events.type_from_string(NUCLEUS_SERVER_ADDED_GLOBAL_EVENT)
omni.kit.app.register_event_alias(NUCLEUS_SERVER_ADDED_EVENT, NUCLEUS_SERVER_ADDED_GLOBAL_EVENT)
NUCLEUS_SERVER_DELETED_EVENT: int = carb.events.type_from_string(NUCLEUS_SERVER_DELETED_GLOBAL_EVENT)
omni.kit.app.register_event_alias(NUCLEUS_SERVER_DELETED_EVENT, NUCLEUS_SERVER_DELETED_GLOBAL_EVENT)
NUCLEUS_SERVER_RENAMED_EVENT: int = carb.events.type_from_string(NUCLEUS_SERVER_RENAMED_GLOBAL_EVENT)
omni.kit.app.register_event_alias(NUCLEUS_SERVER_RENAMED_EVENT, NUCLEUS_SERVER_RENAMED_GLOBAL_EVENT)

class ViewWidget(FileBrowserWidget):
    def __init__(self, title: str, **kwargs):
        self._available_collections = kwargs.pop("available_collections", "")
        super().__init__(title, **kwargs)

    @property
    def navigation_model(self) -> NavigationModel:
        return self._models

    def create_treeview_model(self, name: str, drop_fn: Callable, filter_fn: Callable) -> NavigationModel:
        return NavigationModel(name=name, drop_fn=drop_fn, filter_fn=filter_fn, available_collections=self._available_collections)


class FilePickerView:
    """
    An embeddable UI component for browsing the filesystem. This widget is more full-functioned
    than :obj:`FileBrowserWidget` but less so than :obj:`FilePickerWidget`. More specifically, this is one of
    the 3 sub-components of its namesake :obj:`FilePickerWidget`. The difference is it doesn't have the Browser Bar
    (at top) or the File Bar (at bottom). This gives users the flexibility to substitute in other surrounding
    components instead.

    Args:
        title (str): Widget title. Default None.

    Keyword Args:
        layout (int): The overall layout of the window, one of: {LAYOUT_SPLIT_PANES, LAYOUT_SINGLE_PANE_SLIM,
            LAYOUT_SINGLE_PANE_WIDE, LAYOUT_DEFAULT}. Default LAYOUT_SPLIT_PANES.
        splitter_offset (int): Position of vertical splitter bar. Default 300.
        show_grid_view (bool): Display grid view in the intial layout. Default True.
        show_recycle_widget (bool): Display recycle widget in the intial layout. Default False.
        grid_view_scale (int): Scales grid view, ranges from 0-5. Default 2.
        on_toggle_grid_view_fn (Callable): Callback after toggle grid view is executed. Default None.
        on_scale_grid_view_fn (Callable): Callback after scale grid view is executed. Default None.
        show_only_collections (list[str]): List of collections to display, any combination of ["bookmarks",
            "omniverse", "my-computer"]. If None, then all are displayed. Default None.
        tooltip (bool): Display tooltips when hovering over items. Default True.
        allow_multi_selection (bool): Allow multiple items to be selected at once. Default False.
        mouse_pressed_fn (Callable): Function called on mouse press. Function signature:
            void mouse_pressed_fn(pane: int, button: int, key_mode: int, item: :obj:`FileBrowserItem`)
        mouse_double_clicked_fn (Callable): Function called on mouse double click.  Function signature:
            void mouse_double_clicked_fn(pane: int, button: int, key_mode: int, item: :obj:`FileBrowserItem`)
        selection_changed_fn (Callable): Function called when selection changed. Function signature:
            void selection_changed_fn(pane: int, selections: list[:obj:`FileBrowserItem`])
        drop_handler (Callable): Function called to handle drag-n-drops.
            Function signature: void drop_fn(dst_item: :obj:`FileBrowserItem`, src_paths: [str])
        item_filter_fn (Callable): This handler should return True if the given tree view item is visible,
            False otherwise. Function signature: bool item_filter_fn(item: :obj:`FileBrowserItem`)
        thumbnail_provider (Callable): This callback returns the path to the item's thumbnail. If not specified,
            then a default thumbnail is used. Signature: str thumbnail_provider(item: :obj:`FileBrowserItem`).
        icon_provider (Callable): This callback provides an icon to replace the default in the tree view.
            Signature str icon_provider(item: :obj:`FileBrowserItem`)
        badges_provider (Callable): This callback provides the list of badges to layer atop the thumbnail
            in the grid view. Callback signature: [str] badges_provider(item: :obj:`FileBrowserItem`)
        treeview_identifier (str): widget identifier for treeview, only used by tests.
        enable_zoombar (bool): Enables/disables zoombar. Default True.
    """

    # Singleton placeholder item in the tree view
    __placeholder_model = None
    # use class attribute to store connected server's url
    # it could shared between different file dialog (OMFP-2569)
    __connected_servers = set()

    def __init__(self, title: str, **kwargs):
        self._title = title
        self._filebrowser = None
        self._auto_select_future = None
        self._layout = kwargs.get("layout", LAYOUT_DEFAULT)
        self._splitter_offset = kwargs.get("splitter_offset", 300)
        self._show_grid_view = kwargs.get("show_grid_view", True)
        self._show_recycle_widget = kwargs.get("show_recycle_widget", False)
        self._grid_view_scale = kwargs.get("grid_view_scale", 2)
        # OM-66270: Add callback to record show grid view settings in between sessions
        self._on_toggle_grid_view_fn = kwargs.get("on_toggle_grid_view_fn", None)
        self._on_scale_grid_view_fn = kwargs.get("on_scale_grid_view_fn", None)
        self._show_only_collections = kwargs.get("show_only_collections", None)
        self._tooltip = kwargs.get("tooltip", True)
        self._allow_multi_selection = kwargs.get("allow_multi_selection", False)
        self._mouse_pressed_fn = kwargs.get("mouse_pressed_fn", None)
        self._mouse_double_clicked_fn = kwargs.get("mouse_double_clicked_fn", None)
        self._selection_changed_fn = kwargs.get("selection_changed_fn", None)
        self._drop_handler = kwargs.get("drop_handler", None)
        self._item_filter_fn = kwargs.get("item_filter_fn", None)
        self._icon_provider = kwargs.get("icon_provider", None)
        self._thumbnail_provider = kwargs.get("thumbnail_provider", None)
        self._treeview_identifier = kwargs.get('treeview_identifier', None)
        self._enable_zoombar = kwargs.get("enable_zoombar", True)

        self._badges_provider = kwargs.get("badges_provider", None)

        self._show_add_new_connection = carb.settings.get_settings().get_as_bool("/exts/omni.kit.window.filepicker/show_add_new_connection")

        if not FilePickerView.__placeholder_model:
            FilePickerView.__placeholder_model = FileBrowserModel(name="Add New Connection ...")
            FilePickerView.__placeholder_model.root.icon = f"{ICON_PATH}/hdd_plus.svg"

        self.__expand_task = None
        self._connection_failed_event_sub = None
        self._connection_succeeded_event_sub = None
        self._connection_status_sub = None

        self._build_ui()

    @property
    def filebrowser(self):
        """ Gets the filebrowser of this view. """
        return self._filebrowser

    @property
    def navigation_model(self) -> Optional[NavigationModel]:
        """ Gets the navigation model of this view. """
        return self._filebrowser.navigation_model if self._filebrowser else None

    @property
    def show_only_collections(self):
        """ Gets the collections list only to show."""
        return self.navigation_model.available_collections if self.navigation_model else self._show_only_collections

    @show_only_collections.setter
    def show_only_collections(self, value: List[str]):
        """ Sets the collections list only to show."""
        self._show_only_collections = value
        if self.navigation_model:
            self.navigation_model.available_collections = value

    def destroy(self):
        """ Destructor """
        # Cancels the expand task.
        if self.__expand_task is not None:
            self.__expand_task.cancel()
            self.__expand_task = None

        # Cancels the auto select task.
        if self._auto_select_future:
            self._auto_select_future.cancel()
            self._auto_select_future = None

        if self._filebrowser:
            self._filebrowser.destroy()
            self._filebrowser = None

        self._mouse_pressed_fn = None
        self._mouse_double_clicked_fn = None
        self._selection_changed_fn = None
        self._drop_handler = None
        self._item_filter_fn = None
        self._icon_provider = None
        self._thumbnail_provider = None

        self._badges_provider = None
        self._connection_failed_event_sub = None
        self._connection_succeeded_event_sub = None
        self._connection_status_sub = None

    @property
    def show_udim_sequence(self):
        """ Whether or not to show UDIM sequence. """
        return self._filebrowser.show_udim_sequence

    @show_udim_sequence.setter
    def show_udim_sequence(self, value: bool):
        """ Show or hides UDIM sequence. """
        self._filebrowser.show_udim_sequence = value

    @property
    def notification_frame(self):
        """The notification frame."""
        return self._filebrowser._notification_frame

    def _build_ui(self):
        """ """
        if self._filebrowser:
            self._filebrowser.destroy()
            self._filebrowser = None
        self._connection_failed_event_sub = None
        self._connection_succeeded_event_sub = None
        self._connection_status_sub = None
        if self.__expand_task is not None:
            self.__expand_task.cancel()
            self.__expand_task = None

        def on_mouse_pressed(pane: int, button: int, key_mod: int, item: FileBrowserItem, x: float = 0, y: float = 0):
            if button == 0 and isinstance(item, AddNewItem):
                # Left mouse button: add new connection
                self.show_connect_dialog(item)
            elif item and item.has_mouse_pressed_fn():
                item.mouse_pressed_fn()
            elif self._mouse_pressed_fn and not self._is_placeholder(item):
                self._mouse_pressed_fn(pane, button, key_mod, item)

        def on_mouse_double_clicked(pane: int, button: int, key_mod: int, item: FileBrowserItem, x: float = 0, y: float = 0):
            if self._is_placeholder(item):
                return
            if item and item.is_folder:
                # In the special case where item errored out previously, try reconnecting the host.
                broken_url = omni.client.break_url(item.path)
                if broken_url.host:
                    def on_host_found(host: FileBrowserItem):
                        if host and host.alert:
                            self.reconnect_server(host)
                    try:
                        self._find_item_with_callback(
                            omni.client.make_url(scheme=broken_url.scheme, host=broken_url.host), on_host_found)
                    except Exception as e:
                        log_warn(str(e))
            if self._mouse_double_clicked_fn:
                self._mouse_double_clicked_fn(pane, button, key_mod, item)

        def on_selection_changed(pane: int, selected: List[FileBrowserItem]):
            # Filter out placeholder item
            selected = list(filter(lambda i: not self._is_placeholder(i), selected))
            if self._selection_changed_fn:
                self._selection_changed_fn(pane, selected)

        self._filebrowser = ViewWidget(
            "All",
            tree_root_visible=False,
            layout=self._layout,
            splitter_offset=self._splitter_offset,
            show_grid_view=self._show_grid_view,
            show_recycle_widget=self._show_recycle_widget,
            grid_view_scale=self._grid_view_scale,
            on_toggle_grid_view_fn=self._on_toggle_grid_view_fn,
            on_scale_grid_view_fn=self._on_scale_grid_view_fn,
            tooltip=self._tooltip,
            allow_multi_selection=self._allow_multi_selection,
            mouse_pressed_fn=on_mouse_pressed,
            mouse_double_clicked_fn=on_mouse_double_clicked,
            selection_changed_fn=on_selection_changed,
            drop_fn=self._drop_handler,
            filter_fn=self._item_filter_fn,
            icon_provider=self._icon_provider,
            thumbnail_provider=self._thumbnail_provider,
            badges_provider=self._badges_provider,
            treeview_identifier=self._treeview_identifier,
            enable_zoombar=self._enable_zoombar,
            available_collections=self._show_only_collections,
        )

        # Listen for connections errors that may occur during navigation
        self._connection_failed_event_sub =\
            eventdispatcher.get_eventdispatcher().observe_event(event_name=CONNECTION_ERROR_GLOBAL_EVENT, on_event=self._on_connection_failed)
        if have_nucleus:
            self._connection_succeeded_event_sub = \
                eventdispatcher.get_eventdispatcher().observe_event(event_name=NUCLEUS_CONNECTION_SUCCEEDED_GLOBAL_EVENT, on_event=self._on_connection_succeeded)
        self._connection_status_sub = omni.client.register_connection_status_callback(self._server_status_changed)

        def expand_collections():
            for collection in self.navigation_model.collection_items:
                self._filebrowser.set_expanded(collection, expanded=True, recursive=False)

        # Finally, expand collection nodes in treeview after UI becomes ready
        # If delay too much here, treeview expand here will override the treeview expand for initialize navigation after UI ready
        self.__expand_task = exec_after_redraw(expand_collections, wait_frames=1)

    def register_collection_item(self, collection_item: CollectionItem) -> bool:
        """
        Register a collection item to the file picker.

        Args:
            collection_item (CollectionItem): The collection item to register.

        Returns:
            bool: True if the collection item was registered, False otherwise.
        """
        registered_collection = self.navigation_model.add_collection(collection_item)
        if registered_collection == collection_item:
            if collection_item.identifier not in self.show_only_collections:
                self.show_only_collections = self.show_only_collections + [collection_item.identifier]
            return True
        return False

    def deregister_collection_item(self, collection_item: CollectionItem) -> bool:
        """
        Deregister a collection item from the file picker.

        Args:
            collection_item (CollectionItem): The collection item to deregister.

        Returns:
            bool: True if the collection item was deregistered, False otherwise.
        """
        removed_collection = self.navigation_model.remove_collection(collection_item.identifier)
        return removed_collection is not None

    def add_collection(self, collection_data: CollectionData) -> FileBrowserItem:
        collection = self.navigation_model.add_collection_by_data(collection_data)
        return collection

    def add_custom_collection(
        self,
        collection_data: CollectionData
    ) -> Optional[CollectionItem]:
        if collection_data.identifier not in self.show_only_collections:
            self.show_only_collections = self.show_only_collections + [collection_data.identifier]
        return self.navigation_model.add_collection_by_data(collection_data)

    def remove_collection(self, collection_id: str):
        if self.navigation_model.remove_collection(collection_id):
            self._build_ui()

    @property
    def collections(self):
        """dict: Dictionary of collections, e.g. 'bookmarks', 'omniverse', 'my-computer'."""
        return self.navigation_model.collections

    def get_root(self, pane: int = None) -> FileBrowserItem:
        """
        Returns the root item of the specified pane.

        Args:
            pane (int): One of {TREEVIEW_PANE, LISTVIEW_PANE}.
        """
        if self._filebrowser:
            return self._filebrowser.get_root(pane)
        return None

    def all_collection_items(self, collection: str = None) -> List[FileBrowserItem]:
        """
        Returns all connections as items for the specified collection. If collection is 'None', then return connections
        from all collections.

        Args:
            collection (str): One of ['bookmarks', 'omniverse', 'my-computer']. Default None.

        Returns:
            List[FileBrowserItem]: All connections found.

        """
        return self.navigation_model.get_connections(collection) if self.navigation_model else []

    def is_collection_root(self, url: str = None) -> bool:
        """
        Returns True if the given url is a collection root url.

        Args:
            url (str): The url to query. Default None.

        Returns:
            bool: The result.
        """
        if not url:
            return False

        for col in self.navigation_model.collection_items:
            if col.path == url:
                return True

        # click the path field root always renturn "omniverse:///"
        # TODO: it's collection name, don't need to change here
        if url.rstrip("/") == "omniverse:":
            return True

        return False

    def has_connection_with_name(self, name: str, collection: str = None) -> bool:
        """
        Returns True if named connection exists within the collection.

        Args:
            name (str): name (could be aliased name) of connection
            collection (str): One of {'bookmarks', 'omniverse', 'my-computer'}. Default None.

        Returns:
            bool

        """
        connections = [i.name for i in self.all_collection_items(collection)]
        return name in connections

    def get_connection_with_url(self, url: str) -> Optional[NucleusConnectionItem]:
        """
        Gets the connection item with the given url.

        Args:
            name (str): name (could be aliased name) of connection

        Returns:
            NucleusConnectionItem
        """
        # TODO: it's collection name, don't need to change here
        for item in self.all_collection_items(collection="omniverse"):
            if item.path == url:
                return item
        return None

    def set_item_filter_fn(self, item_filter_fn: Callable[[str], bool]):
        """
        Sets the item filter function.

        Args:
            item_filter_fn (Callable): Signature is bool fn(item: FileBrowserItem)

        """
        self._item_filter_fn = item_filter_fn
        if self._filebrowser and self._filebrowser._listview_model:
            self._filebrowser._listview_model.set_filter_fn(self._item_filter_fn)

    def set_selections(self, selections: List[FileBrowserItem], pane: int = TREEVIEW_PANE):
        """
        Selected given items in given pane.

        ARGS:
            selections (list[:obj:`FileBrowserItem`]): list of selections.
            pane (int): One of TREEVIEW_PANE, LISTVIEW_PANE, or None for both. Default None.

        """
        if self._filebrowser:
            self._filebrowser.set_selections(selections, pane)

    def get_selections(self, pane: int = LISTVIEW_PANE) -> List[FileBrowserItem]:
        """
        Returns list of currently selected items.

        Args:
            pane (int): One of {TREEVIEW_PANE, LISTVIEW_PANE}.

        Returns:
            list[:obj:`FileBrowserItem`]

        """
        if self._filebrowser:
            return [sel for sel in self._filebrowser.get_selections(pane) if not self._is_placeholder(sel)]
        return []

    def refresh_ui(self, item: FileBrowserItem = None):
        """
        Redraws the subtree rooted at the given item. If item is None, then redraws entire tree.

        Args:
            item (:obj:`FileBrowserItem`): Root of subtree to redraw. Default None, i.e. root.

        """
        # self._build_computer_collection()
        if item:
            item.populated = False
        if self._filebrowser:
            self._filebrowser.refresh_ui(item)

    def is_connection_point(self, item: FileBrowserItem) -> bool:
        """
        Returns true if given item is a direct child of a collection node.

        Args:
            item (:obj:`FileBrowserItem`): Item in question.

        Returns:
            bool

        """
        for collection in self.navigation_model.collection_items:
            if item in collection.connections:
                return True
        return False

    def is_local_point(self, item: FileBrowserItem) -> bool:
        """
        Returns true if given item is a direct child of a my-computer's node.

        Args:
            item (:obj:`FileBrowserItem`): Item in question.

        Returns:
            bool

        """
        return item in self.all_collection_items("my-computer")

    def is_bookmark(self, item: FileBrowserItem, path: Optional[str] = None) -> bool:
        """
        Returns true if given item is a bookmarked item, or if a given path is bookmarked.

        Args:
            item (:obj:`FileBrowserItem`): Item in question.
            path (Optional[str]): Path in question.

        Returns:
            bool

        """
        if path:
            for item in self.all_collection_items("bookmarks"):
                # compare the bookmark path with the formatted file path
                if item.path == item.format_bookmark_path(path):
                    return True
            return False

        # if path is not given, check item type directly
        return isinstance(item, BookmarkItem)

    def is_collection_node(self, item: FileBrowserItem) -> bool:
        """
        Returns true if given item is a collection node.

        Args:
            item (:obj:`FileBrowserItem`): Item in question.

        Returns:
            bool

        """
        return isinstance(item, CollectionItem)

    def select_and_center(self, item: FileBrowserItem):
        """
        Selects and centers the view on the given item, expanding the tree if needed.

        Args:
            item (:obj:`FileBrowserItem`): The selected item.

        """
        if not self._filebrowser:
            return
        if (item and item.is_folder) or not item:
            self._filebrowser.select_and_center(item, pane=TREEVIEW_PANE)
        else:
            self._filebrowser.select_and_center(item.parent, pane=TREEVIEW_PANE)
            exec_after_redraw(lambda item=item: self._filebrowser.select_and_center(item, pane=LISTVIEW_PANE))

    def show_model(self, model: FileBrowserModel):
        """Displays the model on the right side of the split pane"""
        self._filebrowser.show_model(model)

    def show_connect_dialog(self, item: Optional[AddNewItem]) -> None:
        """Displays the add connection dialog."""
        if item and isinstance(item, AddNewItem):
            item.add_new(on_success_fn=self.add_server)
        else:
            carb.log_error("show_connect_dialog: item is not an AddNewItem")

    def add_server(self, name: str, path: str, publish_event: bool = True, auto_select: bool = True) -> FileBrowserModel:
        """
        Creates a :obj:`FileBrowserModel` rooted at the given path, and connects its subtree to the
        tree view.

        Args:
            name (str): Name, label really, of the connection.
            path (str): Fullpath of the connection, e.g. "omniverse://ov-content". Paths to
                Omniverse servers should contain the prefix, "omniverse://".
            publish_event (bool): If True, push a notification to the event stream.

        Returns:
            :obj:`FileBrowserModel`

        Raises:
            :obj:`RuntimeWarning`: If unable to add server.

        """
        (collection, connection) = self.navigation_model.add_path(name, path)
        if collection and connection:
            if connection in collection.connections and publish_event:
                # Push a notification event to the event stream
                omni.kit.app.queue_event(NUCLEUS_SERVER_ADDED_GLOBAL_EVENT, {"name": name, "url": path})

            if auto_select:

                def delay_select():
                    server_item = self.get_connection_with_url(path)
                    if server_item:
                        self.select_and_center(server_item)

                self._auto_select_future = exec_after_redraw(delay_select, wait_frames=4)
            return connection
        else:
            return None

    def _on_connection_failed(self, event: eventdispatcher.Event):
        def set_item_warning(item: FileBrowserItem, msg: str):
            if item and not self._is_placeholder(item):
                self.filebrowser.set_item_warning(item, msg)
        try:
            broken_url = omni.client.break_url(event['url'] or "")
        except Exception:
            return
        # TODO: do we want to support other kind of url for connection?
        if not broken_url.is_raw and broken_url.host:
            url = omni.client.make_url(scheme=broken_url.scheme, host=broken_url.host)
            msg = "Unable to access this server. Please double-click this item or right-click, then 'reconnect server' to refresh the connection."
            self._find_item_with_callback(url, lambda item: set_item_warning(item, msg))

    def _on_connection_succeeded(self, event: eventdispatcher.Event):
        url = event["url"] or ""

        def refresh_connection(item: FileBrowserItem):
            if self._filebrowser:
                # Clear alerts, if any
                self._filebrowser.clear_item_alert(item)
            self.refresh_ui(item)

        self._find_item_with_callback(url, refresh_connection)

    def delete_server(self, item: FileBrowserItem, publish_event: bool = True):
        """
        Disconnects the subtree rooted at the given item.

        Args:
            item (:obj:`FileBrowserItem`): Root of subtree to disconnect.
            publish_event (bool): If True, push a notification to the event stream.

        """
        if not item or not self.is_connection_point(item) or self._is_placeholder(item):
            return

        disconnect(item.path)

        self._filebrowser.delete_child(item, parent=item.parent)

        if publish_event:
            # Push a notification event to the event stream
            omni.kit.app.queue_event(NUCLEUS_SERVER_DELETED_GLOBAL_EVENT, {"name": item.name, "url": item.path})

    def rename_server(self, item: FileBrowserItem, new_name: str, publish_event: bool = True):
        """
        Renames the connection item. Note: doesn't change the connection itself, only how it's labeled
        in the tree view.

        Args:
            item (:obj:`FileBrowserItem`): Root of subtree to disconnect.
            new_name (str): New name.
            publish_event (bool): If True, push a notification to the event stream.

        """
        if not item or not self.is_connection_point(item) or self._is_placeholder(item):
            return
        elif new_name == item.name:
            return

        if self.has_connection_with_name(new_name):
            carb.log_warn(f"Server exist with same name: {new_name}, rename server failed")
            return

        old_name, server_url = item.name, item.path
        self._filebrowser.delete_child(item, parent=item.parent)
        self.add_server(new_name, server_url, publish_event=False)

        if publish_event:
            # Push a notification event to the event stream
            omni.kit.app.queue_event(NUCLEUS_SERVER_RENAMED_GLOBAL_EVENT, {"old_name": old_name, "new_name": new_name, "url": server_url})

    def reconnect_server(self, item: FileBrowserItem):
        """
        Reconnects the server at the given path. Clears out any cached authentication tokens to force the action.

        Args:
            item (:obj:`FileBrowserItem`): Connection item.

        """
        broken_url = omni.client.break_url(item.path)
        if broken_url.scheme != 'omniverse':
            return

        if self.is_connection_point(item):
            reconnect(item.path)

    def log_out_server(self, item: NucleusConnectionItem):
        """
        Log out from the server at the given path.

        Args:
            item (:obj:`NucleusConnectionItem`): Connection item.

        """
        if not isinstance(item, NucleusConnectionItem):
            return

        broken_url = omni.client.break_url(item.path)
        if broken_url.scheme != 'omniverse':
            return

        omni.client.sign_out(item.path)

    def add_bookmark(self, name: str, path: str, is_folder: bool = True, publish_event: bool = True) -> BookmarkItem:
        """
        Creates a :obj:`FileBrowserModel` rooted at the given path, and connects its subtree to the
        tree view.

        Args:
            name (str): Name of the bookmark.
            path (str): Fullpath of the connection, e.g. "omniverse://ov-content". Paths to
                Omniverse servers should contain the prefix, "omniverse://".
            is_folder (bool): If the item to be bookmarked is a folder or not. Default to True.
            publish_event (bool): If True, push a notification to the event stream.

        Returns:
            :obj:`BookmarkItem`

        """
        bookmark = None
        if not (name and path):
            carb.log_warn("Bookmarkname and path are required")
            return None

        collection = self.navigation_model.get_collection("bookmarks")
        if collection is None:
            carb.log_info(f"Cannot add bookmark '{name}' at '{path}' as no bookmarks collection exists")
            return None

        path_collection = self.navigation_model.filter_collection(path)
        if not path_collection:
            carb.log_info(f"Cannot add bookmark '{name}' at '{path}' as no available collection")
            return None

        bookmark = collection.add_path(name, path, is_folder=is_folder)
        if bookmark:
            self._filebrowser.refresh_ui(collection)

            if publish_event:
                # Push a notification event to the event stream
                omni.kit.app.queue_event(BOOKMARK_ADDED_GLOBAL_EVENT, {"name": bookmark.name, "url": bookmark.path})
        else:
            carb.log_error("Failed to add bookmark for {name} at {path}")

        return bookmark

    def delete_bookmark(self, item: BookmarkItem, publish_event: bool = True) -> bool:
        """
        Deletes the given bookmark.

        Args:
            item (:obj:`FileBrowserItem`): Bookmark item.
            publish_event (bool): If True, push a notification to the event stream.

        """
        collection = self.navigation_model.get_collection("bookmarks")
        if collection is None:
            carb.log_warn("No bookmarks collection!")
            return False

        if item is None:
            return False

        if not self.is_bookmark(item):
            carb.log_error(f"Failed to delete '{item.name}' as it is not a bookmark!")
            return False

        bookmark = collection.del_child(item.name)
        if bookmark:
            self._filebrowser.refresh_ui(collection)

            if publish_event:
                # Push a notification event to the event stream
                omni.kit.app.queue_event(BOOKMARK_DELETED_GLOBAL_EVENT,  payload={"name": item.name, "url": item.path})
            return True
        else:
            carb.log_error(f"Failed to delete bookmark '{item.name}' as not found")
            return False

    def rename_bookmark(self, item: BookmarkItem, new_name: str, new_url: str, publish_event: bool = True):
        """
        Renames the bookmark item. Note: doesn't change the connection itself, only how it's labeled
        in the tree view.

        Args:
            item (:obj:`FileBrowserItem`): Bookmark item.
            new_name (str): New name.
            new_url (str): New url address.
            publish_event (bool): If True, push a notification to the event stream.

        """
        if not item or not self.is_bookmark(item):
            return
        elif new_name == item.name and new_url == item.path:
            return

        old_name, is_folder = item.name, item.is_folder
        self.delete_bookmark(item, publish_event=False)
        self.add_bookmark(new_name, new_url, is_folder=is_folder, publish_event=False)
        item.set_bookmark_path(new_url)

        if publish_event:
            # Push a notification event to the event stream
            omni.kit.app.queue_event(BOOKMARK_RENAMED_GLOBAL_EVENT, {"old_name": old_name, "new_name": new_name, "url": new_url})

    def mount_user_folders(self, folders: dict):
        """
        Mounts given set of user folders under the local collection.

        Args:
            folders (dict): Name, path pairs.

        """
        if not folders:
            return

        collection = self.navigation_model.get_collection("my-computer")
        if not collection:
            return

        for name, path in folders.items():
            if name not in collection.children and os.path.exists(path):
                collection.add_path(name, path)

    def _is_placeholder(self, item: FileBrowserItem) -> bool:
        """
        Returns True if given item is the placeholder item.

        Returns:
            bool

        """
        return item and isinstance(item, AddNewItem)

    def toggle_grid_view(self, show_grid_view: bool):
        """
        Toggles file picker between grid and list view.

        Args:
            show_grid_view (bool): True to show grid view, False to show list view.

        """
        self._filebrowser.toggle_grid_view(show_grid_view)

    @property
    def show_grid_view(self):
        """
        Gets file picker stage of grid or list view.

        Returns:
            bool: True if grid view shown or False if list view shown.

        """
        return self._filebrowser.show_grid_view

    def scale_grid_view(self, scale: float):
        """
        Scale file picker's grid view icon size.

        Args:
            scale (float): Scale of the icon.

        """
        self._filebrowser.scale_grid_view(scale)

    def show_notification(self):
        """Utility to show the notification frame."""
        self._filebrowser.show_notification()

    def hide_notification(self):
        """Utility to hide the notification frame."""
        self._filebrowser.hide_notification()

    def _find_item_with_callback(self, path: str, callback: Callable):
        """
        Wrapper around FilePickerModel.find_item_with_callback. This is a workaround for accessing the
        model's class method, which in hindsight should've been made a utility function.

        """
        model = FilePickerModel()
        model.collections = self.collections
        model.find_item_with_callback(path, callback)

    def _server_status_changed(self, url: str, status: omni.client.ConnectionStatus) -> None:
        """Updates NucleuseConnectionItem signed in status based upon server status changed."""
        item = self.get_connection_with_url(url)
        if status == omni.client.ConnectionStatus.CONNECTED:
            if item:
                item.signed_in = True
            FilePickerView.__connected_servers.add(url)
        elif status == omni.client.ConnectionStatus.SIGNED_OUT:
            if item:
                item.signed_in = False
            if url in FilePickerView.__connected_servers:
                FilePickerView.__connected_servers.remove(url)

    @staticmethod
    def is_connected(url: str) -> bool:
        """
         Check if a server is connected.

         Args:
              url: The url of the server

         Returns:
              True if the server is connected, False if not
        """
        return url in FilePickerView.__connected_servers
