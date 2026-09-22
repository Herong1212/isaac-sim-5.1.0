# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["FilePickerAPI"]
import os
import asyncio
import omni.kit.app
import omni.client

from pathlib import Path
from typing import List, Callable, Dict, Optional
from carb import log_warn, log_info
from omni.kit.helper.file_utils import asset_types
from omni.kit.widget.filebrowser import FileBrowserModel, FileBrowserItem, FileBrowserUdimItem, TREEVIEW_PANE, LISTVIEW_PANE
from omni.kit.widget.browser_bar import BrowserBar
try:
    from omni.kit.widget.nucleus_connector import connect
    have_nucleus = True
except ModuleNotFoundError:
    have_nucleus = False
from .model import FilePickerModel
from .collections.bookmark_collection import BookmarkItem
from .collections.collection_item import CollectionItem
from .collections.collection_data import CollectionData
from .view import FilePickerView
from .context_menu import ContextMenu
from .file_bar import FileBar
from .detail_view import DetailView, DetailFrameController
from .utils import LoadingPane


class FilePickerAPI:
    """This class defines the API methods for :obj:`FilePickerWidget`."""

    def __init__(self, model: FilePickerModel = None, view: FilePickerView = None):
        """
        Initialize the FilePickerAPI.

        Args:
            model (:obj:'FilePickerModel'): The model background, default None.
            view (:obj:'FilePickerView'): the content view object. Default None.
        """
        self.model = model
        self.view = view
        self.tool_bar: BrowserBar = None
        self.file_view: FileBar = None
        self.context_menu: ContextMenu = None
        self.listview_menu: ContextMenu = None
        self.detail_view: DetailView = None
        self.error_handler: Callable = None
        self._loading_pane: LoadingPane = None
        self._fallback_search_delegate = None
        self._client_bookmarks_changed_subscription = None
        self._filename = None

    def add_connections(self, connections: dict):
        """
        Adds specified server connections to the tree browser. To facilitate quick startup time, doesn't check
        whether the connection is actually valid.

        Args:
            connections (dict): A dictionary of name, path pairs. For example:
                {"C:": "C:", "ov-content": "omniverse://ov-content"}.  Paths to Omniverse servers
                should be prefixed with "omniverse://".

        """
        if not connections:
            return

        for name, path in connections.items():
            # TODO: it's collection name, don't need to change here
            if not self.view.has_connection_with_name(name, "omniverse"):
                try:
                    self.view.add_server(name, path, auto_select=False)
                except Exception as e:
                    self._warn(str(e))

        # Update the UI
        self.view.refresh_ui()

    def set_current_directory(self, path: str):
        """
        Procedurally sets the current directory. Use this method to set the path in the browser bar.

        Args:
            path (str): The full path name of the folder, e.g. "omniverse://ov-content/Users/me.

        """
        if path and self.tool_bar:
            self.tool_bar.set_path(path.replace("\\", "/"))

    def get_current_directory(self) -> str:
        """
        Returns the current directory from the browser bar.

        Returns:
            str: The system path, which may be different from the displayed path.

        """
        # Return the directory from set_current_directory call first, then fall back to root
        if self.tool_bar:
            path = self.tool_bar.path
            if path:
                return path.replace("\\", "/")
        item = self.view.get_root(LISTVIEW_PANE)
        return item.path if item else None

    def get_current_selections(self, pane: int = LISTVIEW_PANE) -> List[str]:
        """
        Returns current selected as list of system path names.

        Args:
            pane (int): Specifies pane to retrieve selections from, one of {TREEVIEW_PANE = 1, LISTVIEW_PANE = 2,
                BOTH = None}.  Default LISTVIEW_PANE.
        Returns:
            [str]: List of system paths (which may be different from displayed paths, e.g. bookmarks)

        """
        if self.view:
            selections = self.view.get_selections(pane)
            return [sel.path for sel in selections]
        return None

    def set_filename(self, filename: str):
        """
        Sets the filename in the file bar, at bottom of the dialog. The file is not
        required to already exist.

        Args:
            filename (str): The filename only (and not the fullpath), e.g. "myfile.usd".

        """
        if self.file_view:
            dirname = self.get_current_directory()
            if dirname and filename:
                filename = filename.replace('\\', '/')
                if Path(filename).is_relative_to(Path(dirname)):
                    # Strip directory prefix.
                    filename = str(Path(filename).relative_to(Path(dirname)))
                    filename = filename.replace('\\', '/')
                    # Also strip any leading and trailing slashes.
                    filename = filename.strip('/')
            if self.file_view._focus_filename_input:
                self.file_view.focus_filename_input()
            self.file_view.filename = filename
        self._filename = filename

    def get_filename(self) -> str:
        """
        Returns:
            str: Currently selected filename.
        """
        if self.file_view:
            return self.file_view.filename
        return self._filename

    def navigate_to(self, url: str, callback: Callable = None):
        """
        Navigates to the given url, expanding all parent directories in the path.

        Args:
            url (str): The url to navigate to.
            callback (Callable): On successfully finding the item, executes this callback. Function signature:
                void callback(item: FileBrowserItem)

        """
        asyncio.ensure_future(self.navigate_to_async(url, callback))

    async def navigate_to_async(self, url: str, callback: Callable = None):
        """
        Asynchronously navigates to the given url, expanding the all parent directories in the path.

        Args:
            url (str): The url to navigate to.
            callback (Callable): On successfully finding the item, executes this callback. Function signature:
                void callback(item: FileBrowserItem)

        """
        if not url:
            if self.file_view and self.file_view._focus_filename_input:
                self.file_view.focus_filename_input()
            return

        async def navigate_to_url_async(url: str, callback: Callable) -> bool:
            result = False
            if self._loading_pane is None and self.view:
                self._loading_pane = LoadingPane(self.view.notification_frame)

            async def get_item_async(url):
                # Check that file is udim sequnece as those files don't exist on media
                # OM-103188: Check if the url is a collection root, if so the url won't exist
                if asset_types.is_udim_sequence(url) or (self.view and self.view.is_collection_root(url)):
                    stat_result = omni.client.Result.OK
                else:
                    # Check that file exists before navigating to it.
                    stat_result, _ = await omni.client.stat_async(url)
                if stat_result == omni.client.Result.OK:
                    return await self.model.find_item_async(url)
                else:
                    self._warn(f"No item exists with url '{url}'.")
                    return None

            item = None
            if self.view and self._loading_pane:
                self.view.show_notification()
                try:
                    # Set a very long timeout; instead, display an in-progress indicator with a cancel button.
                    item = await self._loading_pane.run_task(get_item_async(url))
                except asyncio.CancelledError:
                    raise asyncio.CancelledError
                finally:
                    if self.view:
                        self.view.hide_notification()

            if item:
                result = True
                # doesn't always get set 1st time when changing directories
                if self.view:
                    self.view.select_and_center(item)

                if item.is_folder:
                    self.set_filename("")
                else:
                    self.set_filename(os.path.basename(item.path))
                if callback:
                    callback(item)
            else:
                self._warn(f"Uh-oh! item at '{url}' not found.")

            # OM-99312: Hide the loading pane when no item exists
            if self._loading_pane and not result:
                self._loading_pane.hide()

            return result


        # if you navigate to URL with valid path but invalid filename, users gets empty window.
        async def try_to_navigate_async(url, callback):
            try:
                result = await navigate_to_url_async(url, callback)
                if not result:
                    # navigate_to_url_async failed, try without filename
                    client_url = omni.client.break_url(url)
                    base_path = omni.client.make_url(
                        scheme=client_url.scheme,
                        user=client_url.user,
                        host=client_url.host,
                        port=client_url.port,
                        path=os.path.dirname(client_url.path),
                        query=None,
                        fragment=client_url.fragment,
                    )
                    if base_path != url:
                        result = await navigate_to_url_async(base_path, callback)
            except asyncio.CancelledError:
                return

        # OM-103188: Don't normalize url if the url is of a collection group; for example if the url is "omniverse://",
        #  the normalized url would become omniverse:/// and will end up not be able to be found
        if self.view and not self.view.is_collection_root(url):
            url = omni.client.normalize_url(url.strip())
        broken_url = omni.client.break_url(url)
        server_url = omni.client.make_url(scheme='omniverse', host=broken_url.host)

        if broken_url.scheme == 'omniverse' and broken_url.host and not self.view.get_connection_with_url(server_url):
            # If server is not connected, then first auto-connect.
            self.connect_server(server_url, callback=lambda *_: asyncio.ensure_future(try_to_navigate_async(url, callback)))
        else:
            await try_to_navigate_async(url, callback)


    def connect_server(self, url: str, callback: Callable = None):
        """
        Connects the server for given url.

        Args:
            url (str): Given url.
            callback (Callable): On successfully connecting the server, executes this callback. Function signature:
                void callback(name: str, server_url: str)

        """
        def on_success(name: str, url: str):
            # OM-94973: Guard against early destruction of view when this is executed async
            if not self.view:
                return
            if not self.view.get_connection_with_url(url):
                self.view.add_server(name, url)
            if callback:
                callback()

        if url:
            broken_url = omni.client.break_url(url)
            if broken_url.scheme == 'omniverse':
                server_url = omni.client.make_url(scheme='omniverse', host=broken_url.host)
                if have_nucleus:
                    connect(broken_url.host, server_url, on_success_fn=on_success)

    def find_subdirs_with_callback(self, url: str, callback: Callable):
        """
        Executes callback on list of subdirectories at given url.

        Args:
            url (str): Url.
            callback (Callable): On success executes this callback with the list of subdir names. Function
                signature: void callback(subdirs: List[str])

        """
        asyncio.ensure_future(self.find_subdirs_async(url, callback))

    async def find_subdirs_async(self, url: str, callback: Callable) -> List[str]:
        """
        Asynchronously executes callback on list of subdirectories at given url.

        Args:
            url (str): Url.
            callback (Callable): On success executes this callback with the list of subdir names. Function
                signature: void callback(subdirs: List[str])

        """
        item, subdirs = None, []
        if not url:
            # For empty url, returns all connections
            for collection in ['omniverse', 'my-computer']:
                subdirs.extend([i.path for i in self.view.all_collection_items(collection)])
        else:
            item = await self.model.find_item_async(url)

        if item:
            result = await item.populate_async(None)
            if isinstance(result, Exception):
                pass
            else:
                subdirs = [c.name for _, c in item.children.items() if c.is_folder and not self.view._is_placeholder(c)]
        # No item found for pathq
        if callback:
            callback(subdirs)

    async def select_items_async(self, url: str, filenames: List[str] = []) -> List[FileBrowserItem]:
        """
        Asynchronously select one or more items in the content view.

        Args:
            url (str): Url.
        Keyword Args:
            filenames (List[str]): A list of file names that to be selected
        """
        if not url:
            return

        item = await self.model.find_item_async(url)
        if not item:
            return
        self.view.select_and_center(item)
        for _ in range(4):
            await omni.kit.app.get_app().next_update_async()

        if item.is_folder and filenames:
            result = await item.populate_async(None)
            if not isinstance(result, Exception):
                if isinstance(filenames, str) and filenames == "*":
                    listview_model = self.view._filebrowser._listview_model
                    selections = listview_model.filter_items([c for _, c in item.children.items()])
                else:
                    selections = [c for _, c in item.children.items() if c.name in filenames]
                self.view.set_selections(selections, pane=LISTVIEW_PANE)
                await omni.kit.app.get_app().next_update_async()

        return self.view.get_selections(pane=LISTVIEW_PANE)

    def add_context_menu(self, name: str, glyph: str, click_fn: Callable, show_fn: Callable, index: int = -1, separator_name="_add_on_end_separator_") -> str:
        """
        Adds menu item, with corresponding callbacks, to the context menu.

        Args:
            name (str): Name of the menu item (e.g. 'Open'), this name must be unique across the context menu.
            glyph (str): Associated glyph to display for this menu item.
            click_fn (Callable): This callback function is executed when the menu item is clicked. Function signature:
                void fn(name: str, path: str), where name is menu name and path is absolute path to clicked item.
            show_fn (Callable): Returns True to display this menu item. Function signature: bool fn(path: str).
                For example, test filename extension to decide whether to display a 'Play Sound' action.
            index (int): The postion that this menu item will be inserted to.
            separator_name (str): The separator name of the separator menu item. Default to '_placeholder_'. When the
                index is not explicitly set, or if the index is out of range, this will be used to locate where to add
                the menu item; if specified, the index passed in will be counted from the saparator with the provided
                name. This is for OM-86768 as part of the effort to match Navigator and Kit UX for Filepicker/Content Browser for context menus.

        Returns:
            str: Name of menu item if successful, None otherwise.

        """
        if self.context_menu:
            return self.context_menu.add_menu_item(name, glyph, click_fn, show_fn, index, separator_name=separator_name)
        return None

    def delete_context_menu(self, name: str):
        """
        Deletes the menu item, with the given name, from the context menu.

        Args:
            name (str): Name of the menu item (e.g. 'Open').

        """
        if self.context_menu:
            self.context_menu.delete_menu_item(name)

    def add_listview_menu(self, name: str, glyph: str, click_fn: Callable, show_fn: Callable, index: int = -1) -> str:
        """
        Adds menu item, with corresponding callbacks, to the list view menu.

        Args:
            name (str): Name of the menu item (e.g. 'Open'), this name must be unique across the list view menu.
            glyph (str): Associated glyph to display for this menu item.
            click_fn (Callable): This callback function is executed when the menu item is clicked. Function signature:
                void fn(name: str, path: str), where name is menu name and path is absolute path to clicked item.
            show_fn (Callable): Returns True to display this menu item. Function signature: bool fn(path: str).
                For example, test filename extension to decide whether to display a 'Play Sound' action.
            index (int): The postion that this menu item will be inserted to.

        Returns:
            str: Name of menu item if successful, None otherwise.

        """
        if self.listview_menu:
            return self.listview_menu.add_menu_item(name, glyph, click_fn, show_fn, index)
        return None

    def delete_listview_menu(self, name: str):
        """
        Deletes the menu item, with the given name, from the list view menu.

        Args:
            name (str): Name of the menu item (e.g. 'Open').

        """
        if self.listview_menu:
            self.listview_menu.delete_menu_item(name)

    def add_detail_frame(self, name: str, glyph: str,
        build_fn: Callable[[], None],
        selection_changed_fn: Callable[[List[str]], None] = None,
        filename_changed_fn: Callable[[str], None] = None,
        destroy_fn: Callable[[], None] = None):
        """
        Adds sub-frame to the detail view, and populates it with a custom built widget.

        Args:
            name (str): Name of the widget sub-section, this name must be unique over all detail sub-sections.
            glyph (str): Associated glyph to display for this subj-section
            build_fn (Callable): This callback function builds the widget.

        Keyword Args:
            selection_changed_fn (Callable): This callback is invoked to handle selection changes.
            filename_changed_fn (Callable): This callback is invoked when filename is changed.
            destroy_fn (Callable): Cleanup function called when destroyed.

        """
        if self.detail_view:
            self.detail_view.add_detail_frame(name, glyph, build_fn,
                selection_changed_fn=selection_changed_fn, filename_changed_fn=filename_changed_fn, destroy_fn=destroy_fn)

    def add_detail_frame_from_controller(self, name: str, controller: DetailFrameController):
        """
        Adds sub-frame to the detail view, and populates it with a custom built widget.

        Args:
            name (str): Name of the widget sub-section, this name must be unique over all detail sub-sections.
            controller (:obj:`DetailFrameController`): Controller object that encapsulates all aspects of creating,
                updating, and deleting a detail frame widget.

        """
        if self.detail_view:
            self.detail_view.add_detail_frame_from_controller(name, controller)

    def delete_detail_frame(self, name: str):
        """
        Deletes the specified detail subsection.

        Args:
            name (str): Name previously assigned to the detail frame.

        """
        if self.detail_view:
            self.detail_view.delete_detail_frame(name)

    def set_search_delegate(self, delegate):
        """
        Sets a custom search delegate for the tool bar.

        Args:
            delegate (:obj:`SearchDelegate`): Object that creates the search widget.

        """
        if self.tool_bar:
            if delegate is None:
                self.tool_bar.set_search_delegate(self._fallback_search_delegate)
            else:
                self.tool_bar.set_search_delegate(delegate)

    def show_model(self, model: FileBrowserModel):
        """
        Displays the given model in the list view, overriding the default model.  For example, this model
        might be the result of a search.

        Args:
            model (:obj:`FileBrowserModel`): Model to display.

        """
        self.view.show_model(model)

    def refresh_current_directory(self):
        """Refreshes the current directory set in the browser bar."""
        item = self.view.get_root(LISTVIEW_PANE)
        if item:
            self.view.refresh_ui(item)

    def toggle_bookmark_from_path(self, name: str, path: str, is_bookmark: bool, is_folder: bool = True):
        """
        Adds/deletes the given bookmark with the specified path. If deleting, then the path argument
        is optional.

        Args:
            name (str): Name to call the bookmark or existing name if delete.
            path (str): Path to the bookmark.
            is_bookmark (bool): True to add, False to delete.
            is_folder (bool): Whether the item to be bookmarked is a folder.

        """
        if is_bookmark:
            self.view.add_bookmark(name, path, is_folder=is_folder)
        else:
            for bookmark in self.view.all_collection_items("bookmarks"):
                if name == bookmark.name:
                    self.view.delete_bookmark(bookmark)
                    break

    def subscribe_client_bookmarks_changed(self):
        """Subscribe to omni.client bookmark changes."""
        def on_client_bookmarks_changed(client_bookmarks: Dict):
            self._update_bookmarks(client_bookmarks)
            self._update_nucleus_servers(client_bookmarks)
        self._client_bookmarks_changed_subscription = omni.client.list_bookmarks_with_callback(on_client_bookmarks_changed)

    def hide_loading_pane(self):
        """
        Hide the loading icon if it exist.
        """
        if self._loading_pane:
            self._loading_pane.hide()

    def register_collection_item(self, collection_item: CollectionItem) -> bool:
        """
        Register a collection item to the file picker.

        Args:
            collection_item (CollectionItem): The collection item to register.

        Returns:
            bool: True if the collection item was registered, False otherwise.
        """
        success = self.view.register_collection_item(collection_item)
        if success:
            self.model.collections = self.view.navigation_model.collections
        return success

    def deregister_collection_item(self, collection_item: CollectionItem) -> bool:
        """
        Deregister a collection item from the file picker.

        Args:
            collection_item (CollectionItem): The collection item to deregister.

        Returns:
            bool: True if the collection item was deregistered, False otherwise.
        """
        success = self.view.deregister_collection_item(collection_item)
        if success:
            self.model.collections = self.view.navigation_model.collections
        return success

    def add_collection(
        self,
        collection_data: CollectionData
    ) -> Optional[CollectionItem]:
        """
        Add custom collection to current content view.
        samples of collection: "My Computer", "Omniverse Bookmark", ...

        Args:
            collection_data (CollectionData): Data to add.

        Returns:
            :obj:`CollectionItem`: The added collection. Could be None if the view is not available or failed to add.
        """
        return self.view.add_custom_collection(collection_data) if self.view else None

    def remove_collection(self, collection_id: str):
        """
        Remove custom collection from current content view.
        samples of collection: "My Computer", "Omniverse Bookmark", ...

        Args:
            collection_id (str): Data id to remove.

        """
        self.view.remove_collection(collection_id)

    def add_show_only_collection(self, collection_id: str):
        """
        Add a filter to show collections. If this collection filter is provided,
        only those that match the filter will be shown, other collections will be hidden.
        Otherwise all collections are shown.

        Args:
            collection_id (str): the filter.

        """
        show_only_collections = self.view.show_only_collections
        if collection_id not in show_only_collections:
            show_only_collections.append(collection_id)
            self.view.show_only_collections = show_only_collections

    def remove_show_only_collection(self, collection_id: str):
        """
        Remove the collection filter

        Args:
            collection_id (str): The filter that previously added.

        """
        self.view.show_only_collections = [x for x in self.view.show_only_collections if x != collection_id]

    def _update_nucleus_servers(self, client_bookmarks: Dict):
        new_servers = {name: url for name, url in client_bookmarks.items() if self._is_valid_server_url(url)}
        # TODO: it's collection name, don't need to change here
        current_servers = self.view.all_collection_items("omniverse")

        # Update server list but don't push a notification event; otherwise, will repeat the update loop.
        renamed_item = None
        for item in current_servers:
            if item.name not in new_servers or item.path != new_servers[item.name]:
                if item.path in new_servers.values():
                    # Means this item is a renamed server, it should not be delete
                    renamed_item = item
                    continue
                self.view.delete_server(item, publish_event=False)
        for name, path in new_servers.items():
            if name not in [item.name for item in current_servers]:
                if self.view:
                    if renamed_item and path == renamed_item.path:
                        self.view.rename_server(renamed_item, name, publish_event=False)
                    else:
                        self.view.add_server(name, path, publish_event=False, auto_select=False)

    def _update_bookmarks(self, client_bookmarks: Dict):
        new_bookmarks = {name: url for name, url in client_bookmarks.items() if not self._is_valid_server_url(url)}
        current_bookmarks = []
        if self.view:
            current_bookmarks = self.view.all_collection_items("bookmarks")

        # Update bookmarks but don't push a notification event; otherwise, will repeat the update loop.
        for item in current_bookmarks:
            if item.name not in new_bookmarks:
                if self.view:
                    self.view.delete_bookmark(item, publish_event=False)
        for name, path in new_bookmarks.items():
            if name not in [item.name for item in current_bookmarks]:
                if self.view:
                    self.view.add_bookmark(
                        name, path, publish_event=False, is_folder=BookmarkItem.is_bookmark_folder(path))

    def _is_valid_server_url(self, url: str):
        if not url:
            return False
        broken_url = omni.client.break_url(url)
        if broken_url.scheme and broken_url.path == "/" and broken_url.host is not None:
            # Url of the form "omniverse://server_name/" should be recognized as server connection
            return True
        return False

    def _info(self, msg: str):
        log_info(msg)

    def _warn(self, msg: str):
        log_warn(msg)
        if self.error_handler:
            self.error_handler(msg)

    def destroy(self):
        """Destructor."""

        self.model = None
        self.view = None
        self.tool_bar = None
        self.file_view = None
        self.context_menu = None
        self.listview_menu = None
        self.detail_view = None
        self.error_handler = None
        if self._loading_pane:
            self._loading_pane.destroy()
            self._loading_pane = None
        self._fallback_search_delegate = None
        self._client_bookmarks_changed_subscription = None
