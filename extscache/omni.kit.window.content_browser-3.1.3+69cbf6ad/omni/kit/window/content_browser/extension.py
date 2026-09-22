# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import os
import asyncio
import carb
import carb.eventdispatcher
import omni.ext
import omni.ui as ui
import omni.kit.window.content_browser_registry as registry
import omni.kit.app

from functools import partial
from typing import Union, Callable, List
from omni.kit.helper.file_utils import FILE_OPENED_GLOBAL_EVENT
from omni.kit.window.filepicker import CollectionData, UI_READY_GLOBAL_EVENT
from omni.kit.widget.filebrowser import FileBrowserModel, FileBrowserItem
from omni.kit.menu.utils import MenuHelperExtension

from .window import ContentBrowserWindow
from .api import ContentBrowserAPI
from .hotkey import ContentHotkeys

g_api_singleton = None


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class ContentBrowserExtension(omni.ext.IExt):
    """The Content Browser extension

    This class serves as the central component of the Content Browser extension. It manages the extension's lifecycle, UI interactions, and integrates various functionalities such as file navigation, search, and custom context menus. Through its methods, it provides an interface to add or remove server connections, navigate directories, manage file selections, and extend the browser's capabilities with custom actions and handlers.
    """

    WINDOW_NAME = "Content"
    """str: The default name for the Content Browser window."""
    MENU_GROUP = "Window"
    """str: The menu group where the window menu item is located."""

    def __init__(self):
        """Initializes the ContentBrowserExtension instance."""
        super().__init__()
        self._extension_api = None

    def on_startup(self, ext_id):
        """Initializes the extension.

        Args:
            ext_id (str): The ID of the extension."""
        # Save away this instance as singleton for the editor window
        self._extension_api = ContentBrowser(ext_id)

    def on_shutdown(self):  # pragma: no cover
        """Cleans up and shuts down the extension."""
        self._window = None
        if self._extension_api:
            self._extension_api._destroy()
            self._extension_api = None



def get_instance():
    global g_api_singleton
    return g_api_singleton


class ContentBrowser(MenuHelperExtension):
    """The Content Browser extension API

    This class serves as the API of the Content Browser extension. It manages the extension's API.
    """
    def __init__(self, ext_id):
        """Initializes the ContentBrowser instance."""
        super().__init__()
        self._api = None
        self._window = None
        self._collections_data = {}
        global g_api_singleton
        g_api_singleton = self

        self.__ext_id = omni.ext.get_extension_name(ext_id)
        self._hotkeys = ContentHotkeys(self.__ext_id, self, ContentBrowserExtension.WINDOW_NAME)
        ui.Workspace.set_show_window_fn(ContentBrowserExtension.WINDOW_NAME, partial(self.show_window, None))

        self.menu_startup(
            ContentBrowserExtension.WINDOW_NAME, ContentBrowserExtension.WINDOW_NAME, ContentBrowserExtension.MENU_GROUP
        )

        ui.Workspace.show_window(ContentBrowserExtension.WINDOW_NAME, True)

        # Listen for relevant event stream events
        self._stage_event_subscription = carb.eventdispatcher.get_eventdispatcher().observe_event(
            observer_name="omni.kit.window.content_browser.extension",
            event_name=FILE_OPENED_GLOBAL_EVENT,
            on_event=self._on_stage_event
        )
        self._content_browser_inited_subscription = carb.eventdispatcher.get_eventdispatcher().observe_event(
            observer_name="omni.kit.window.content_browser.extension",
            event_name=UI_READY_GLOBAL_EVENT,
            on_event=self.decorate_from_registry
        )

    def __del__(self):
        ui.Workspace.set_show_window_fn(ContentBrowserExtension.WINDOW_NAME, None)

    def _destroy(self):
        self._collections_data = None
        self.menu_shutdown()

        global g_api_singleton
        g_api_singleton = None

        self._stage_event_subscription = None
        if self._window:
            self._window.destroy()
            self._window = None
        if self._hotkeys:
            self._hotkeys.destroy()
            self._hotkeys = None
        ui.Workspace.set_show_window_fn(ContentBrowserExtension.WINDOW_NAME, None)

    def _is_visible(self) -> bool:
        return False if self._window is None else self._window.get_visible()

    def _toggle_window(self):
        if self._is_visible():
            self.show_window(None, False)
        else:
            self.show_window(None, True)

    def _on_stage_event(self, stage_event):
        if not stage_event:
            return
        if "url" in stage_event:
            stage_url = stage_event["url"]
            default_folder = os.path.dirname(stage_url)
            self.navigate_to(default_folder)

    async def _destroy_window_async(self):
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._window:
            self._window.destroy()
            self._window = None

    def _visibility_changed_fn(self, visible):
        self.menu_refresh()
        if not visible:
            # Destroy the window, since we are creating new window
            # in show_window
            asyncio.ensure_future(self._destroy_window_async())

    @property
    def window(self) -> ui.Window:
        """Gets the main dialog window for this extension.

        Returns:
            ui.Window: The associated window instance if present; otherwise, None."""
        return self._window

    @window.setter
    def window(self, window: ui.Window):
        """Set the main dialog window for this content browser api class.

        Args:
            ui.Window: The associated window instance."""
        self._window = window
        for collection_data in self._collections_data.values():
            window.widget.api.add_collection(collection_data)
        self._window.set_visibility_changed_listener(self._visibility_changed_fn)

    def show_window(self, menu, value):
        """Shows the Content Browser window, creating it if it does not exist.

        Args:
            menu: The menu from which the show window action was triggered.
            value (bool): The desired visibility state of the Content Browser window."""
        if value:
            self._window = ContentBrowserWindow()
            api = self._window.widget.api
            assert api is not None
            for collection_data in self._collections_data.values():
                self._window.widget.api.add_collection(collection_data)
            self._window.set_visibility_changed_listener(self._visibility_changed_fn)
        elif self._window:
            self._window.set_visible(value)

    @property
    def api(self) -> ContentBrowserAPI:
        """Gets the Content Browser API instance.

        Returns:
            ContentBrowserAPI: The API instance if the extensions is present; otherwise, None."""
        if self._window and self._window.widget:
                return self._window.widget.api
        return None

    def add_connections(self, connections: dict):
        """
        Adds specified server connections to the tree browser.

        Args:
            connections (dict): A dictionary of name, path pairs. For example:
                {"C:": "C:", "ov-content": "omniverse://ov-content"}.  Paths to Omniverse servers
                should be prefixed with "omniverse://".

        """
        if self.api:
            self.api.add_connections(connections)

    def set_current_directory(self, path: str):
        """
        Procedurally sets the current directory path.

        Args:
            path (str): The full path name of the folder, e.g. "omniverse://ov-content/Users/me.

        Raises:
            RuntimeWarning: If path doesn't exist or is unreachable.

        """
        if self.api:
            try:
                self.api.set_current_directory(path)
            except Exception:
                raise

    def get_current_directory(self) -> str:
        """
        Returns the current directory fom the browser bar.

        Returns:
            str: The system path, which may be different from the displayed path.

        """
        if self.api:
            return self.api.get_current_directory()
        return None

    def get_current_selections(self, pane: int = 2) -> List[str]:
        """
        Returns current selected as list of system path names.

        Args:
            pane (int): Specifies pane to retrieve selections from, one of {TREEVIEW_PANE = 1, LISTVIEW_PANE = 2,
                BOTH = None}.  Default LISTVIEW_PANE.
        Returns:
            List[str]: List of system paths (which may be different from displayed paths, e.g. bookmarks)

        """
        if self.api:
            return self.api.get_current_selections(pane)
        return []

    def subscribe_selection_changed(self, fn: Callable):
        """
        Subscribes to file selection changes.

        Args:
            fn (Callable): callback function when file selection changed.

        """
        registry.register_selection_handler(fn)
        if self.api:
            self.api.subscribe_selection_changed(fn)

    def unsubscribe_selection_changed(self, fn: Callable):
        """
        Unsubscribes this callback from selection changes.

        Args:
            fn (Callable): callback function when file selection changed.

        """
        registry.deregister_selection_handler(fn)
        if self.api:
            self.api.unsubscribe_selection_changed(fn)

    def navigate_to(self, url: str):
        """
        Navigates to the given url, expanding all parent directories along the path.

        Args:
            url (str): The path to navigate to.

        """
        if self.api:
            self.api.navigate_to(url)

    async def navigate_to_async(self, url: str):
        """
        Asynchronously navigates to the given url, expanding all parent directories along the path.

        Args:
            url (str): The url to navigate to.

        """
        if self.api:
            await self.api.navigate_to_async(url)

    async def select_items_async(self, url: str, filenames: List[str] = []) -> List[FileBrowserItem]:
        """
        Asynchronously selects display items by their names.

        Args:
            url (str): Url of the parent folder.
            filenames (List[str]): Names of items to select.

        Returns:
            List[FileBrowserItem]: List of selected items.

        """
        if self.api:
            return await self.api.select_items_async(url, filenames=filenames)
        return []

    def add_context_menu(
        self,
        name: str,
        glyph: str,
        click_fn: Callable,
        show_fn: Callable,
        index: int = 0,
        separator_name="_add_on_end_separator_",
    ) -> str:
        """
		Add menu item, with corresponding callbacks, to the context menu.

        Args:
            name (str): Name of the menu item (e.g. 'Open'), this name must be unique across the context menu.
            glyph (str): Associated glyph to display for this menu item.
            click_fn (Callable): This callback function is executed when the menu item is clicked. Function signature is
                void fn(name: str, path: str), where name is menu name and path is absolute path to clicked item.
            show_fn (Callable): Returns True to display this menu item. Function signature - bool fn(path: str).
                For example, test filename extension to decide whether to display a 'Play Sound' action.
            index (int): The position that this menu item will be inserted to.
            separator_name (str): The separator name of the separator menu item. Default to '_placeholder_'. When the
                index is not explicitly set, or if the index is out of range, this will be used to locate where to add
                the menu item; if specified, the index passed in will be counted from the saparator with the provided
                name. This is for OM-86768 as part of the effort to match Navigator and Kit UX for Filepicker/Content Browser for context menus.

        Returns:
            str: Name of menu item if successful, None otherwise.

        """
        registry.register_context_menu(name, glyph, click_fn, show_fn, index)
        if self.api:
            return self.api.add_context_menu(name, glyph, click_fn, show_fn, index, separator_name=separator_name)
        return name

    def delete_context_menu(self, name: str):
        """
        Delete the menu item, with the given name, from the context menu.

        Args:
            name (str): Name of the menu item (e.g. 'Open').

        """
        try:
            registry.deregister_context_menu(name)
            self.api.delete_context_menu(name)
        except AttributeError:
            # it can happen when content_browser is unloaded early. This way we don't need to unsubscribe
            pass

    def add_listview_menu(self, name: str, glyph: str, click_fn: Callable, show_fn: Callable, index: int = -1) -> str:
        """
        Add menu item, with corresponding callbacks, to the list view menu.

        Args:
            name (str): Name of the menu item (e.g. 'Open'), this name must be unique across the list view menu.
            glyph (str): Associated glyph to display for this menu item.
            click_fn (Callable): This callback function is executed when the menu item is clicked. Function signature:
                void fn(name: str, path: str), where name is menu name and path is absolute path to clicked item.
            show_fn (Callable): Returns True to display this menu item. Function signature: bool fn(path: str).
                For example, test filename extension to decide whether to display a 'Play Sound' action.
            index (int): The position that this menu item will be inserted to.

        Returns:
            str: Name of menu item if successful, None otherwise.

        """
        registry.register_listview_menu(name, glyph, click_fn, show_fn, index)
        if self.api:
            return self.api.add_listview_menu(name, glyph, click_fn, show_fn, index)
        return name

    def delete_listview_menu(self, name: str):
        """
        Delete the menu item, with the given name, from the list view menu.

        Args:
            name (str) - Name of the menu item (e.g. 'Open').

        """
        registry.deregister_listview_menu(name)
        if self.api:
            self.api.delete_listview_menu(name)

    def add_import_menu(self, name: str, glyph: str, click_fn: Callable, show_fn: Callable) -> str:
        """
        Add menu item, with corresponding callbacks, to the Import combo box.

        Args:
            name (str): Name of the menu item, this name must be unique across the menu.
            glyph (str): Associated glyph to display for this menu item.
            click_fn (Callable): This callback function is executed when the menu item is clicked. Function signature:
                void fn(name: str, path: str), where name is menu name and path is absolute path to clicked item.
            show_fn (Callable): Returns True to display this menu item. Function signature: bool fn(path: str).
                For example, test filename extension to decide whether to display a 'Play Sound' action.

        Returns:
            str: Name of menu item if successful, None otherwise.

        """
        registry.register_import_menu(name, glyph, click_fn, show_fn)
        if self.api:
            self.api.add_import_menu(name, glyph, click_fn, show_fn)

    def delete_import_menu(self, name: str):
        """
        Delete the menu item, with the given name, from the Import combo box.

        Args:
            name (str): Name of the menu item.

        """
        registry.deregister_import_menu(name)
        if self.api:
            self.api.delete_import_menu(name)

    def add_file_open_handler(self, name: str, open_fn: Callable, file_type: Union[int, Callable]) -> str:
        """
        Registers callback/handler to open a file of matching type.

        Args:
            name (str): Unique name of handler.
            open_fn (Callable): This function is executed when a matching file is selected for open, i.e. double clicked,
                right mouse menu open, or path submitted to browser bar.  Function signature:
                void open_fn(full_path: str), full_path is the file's system path.
            file_type (Union[int, func]): Can either be an enumerated int that is one of: [FILE_TYPE_USD,
                FILE_TYPE_IMAGE, FILE_TYPE_SOUND, FILE_TYPE_TEXT, FILE_TYPE_VOLUME] or a more general boolean function
                that returns True if this function should be activated on the given file.  Function
                signature: bool file_type(full_path: str).

        Returns:
            str - Name if successful, None otherwise.

        """
        registry.register_file_open_handler(name, open_fn, file_type)
        if self.api:
            return self.api.add_file_open_handler(name, open_fn, file_type)
        return name

    def delete_file_open_handler(self, name: str):
        """
        Unregisters the named file open handler.

        Args:
            name (str): Name of the handler.

        """
        registry.deregister_file_open_handler(name)
        if self.api:
            self.api.delete_file_open_handler(name)

    def get_file_open_handler(self, url: str) -> Callable:
        """Returns the matching file open handler for the given file path.

        Args:
            url (str): The url of the file to open.

        Returns:
            Callable: The function to handle the file open event for the given url if one exists; otherwise, None."""
        if self.api:
            return self.api.get_file_open_handler(url)

    def set_search_delegate(self, delegate: "SearchDelegate"):
        """
        Sets a custom search delegate for the tool bar.

        Args:
            delegate (SearchDelegate): Object that creates the search widget.

        """
        registry.register_search_delegate(delegate)
        if self.api:
            self.api.set_search_delegate(delegate)

    def unset_search_delegate(self, delegate: "SearchDelegate"):
        """
        Clears the custom search delegate for the tool bar.

        Args:
            delegate (:obj:`SearchDelegate`): Object that creates the search widget.

        """
        registry.deregister_search_delegate(delegate)
        if self.api:
            self.api.set_search_delegate(None)

    def decorate_from_registry(self, event: carb.events.IEvent | carb.eventdispatcher.Event):
        """Decorates from registry based on the event.

        Args:
            event (carb.events.IEvent): Event that triggers decoration."""
        if not self.api:
            return
        try:
            # Ensure event is for the content window
            if event.payload["title"] != "Content":
                return
        except Exception as e:
            return
        # Add custom menu functions
        for id, args in registry.custom_menus().items():
            context, name = id.split("::")
            if not context or not name:
                continue
            if context == "context":
                self.api.add_context_menu(args["name"], args["glyph"], args["click_fn"], args["show_fn"], args["index"])
            elif context == "listview":
                self.api.add_listview_menu(
                    args["name"], args["glyph"], args["click_fn"], args["show_fn"], args["index"]
                )
            elif context == "import":
                self.api.add_import_menu(args["name"], args["glyph"], args["click_fn"], args["show_fn"])
            elif context == "file_open":
                self.api.add_file_open_handler(args["name"], args["click_fn"], args["show_fn"])
            elif context == "checkpoint":
                self.api.add_checkpoint_menu(
                    args["name"], args["glyph"], args["click_fn"], args["show_fn"], args["index"]
                )
            else:
                pass
        # Add custom selection handlers
        for handler in registry.selection_handlers():
            self.api.subscribe_selection_changed(handler)
        # Set search delegate if any
        if registry.search_delegate():
            self.api.set_search_delegate(registry.search_delegate())

    def show_model(self, model: FileBrowserModel):
        """
        Displays the given model in the list view, overriding the default model.  For example, this model
        might be the result of a search.

        Args:
            model (FileBrowserModel): Model to display.

        """
        if self.api:
            self.api.show_model(model)

    def toggle_grid_view(self, show_grid_view: bool):
        """
        Toggles file picker between grid and list view.

        Args:
            show_grid_view (bool): True to show grid view, False to show list view.

        """
        if self._window:
            self._window.widget._view.toggle_grid_view(show_grid_view)

    def toggle_bookmark_from_path(self, name: str, path: str, is_bookmark: bool, is_folder: bool = True) -> bool:
        """
        Adds/deletes the given bookmark with the specified path. If deleting, then the path argument
        is optional.

        Args:
            name (str): Name to call the bookmark or existing name if delete.
            path (str): Path to the bookmark.
            is_bookmark (bool): True to add, False to delete.
            is_folder (bool): Whether the item to be bookmarked is a folder.

        Returns:
            bool: True if successful.

        """
        if self.api:
            self.api.toggle_bookmark_from_path(name, path, is_bookmark, is_folder=is_folder)

    def refresh_current_directory(self):
        """Refreshes the current directory set in the browser bar."""
        if self.api:
            self.api.refresh_current_directory()

    def get_checkpoint_widget(self) -> "CheckpointWidget":
        """Gets the checkpoint widget.

        Returns:
            CheckpointWidget: The checkpoint widget if present; otherwise, None."""
        if self._window:
            return self._window.widget._checkpoint_widget
        return None

    def get_timestamp_widget(self) -> "TimestampWidget":
        """Gets the timestamp widget.

        Returns:
            TimestampWidget: The timestamp widget if present; otherwise, None."""
        if self._window:
            return self._window.widget._timestamp_widget
        return None

    def add_checkpoint_menu(self, name: str, glyph: str, click_fn: Callable, show_fn: Callable, index=-1) -> str:
        """
        Add menu item, with corresponding callbacks, to checkpoint items.

        Args:
            name (str): Name of the menu item, this name must be unique across the menu.
            glyph (str): Associated glyph to display for this menu item.
            click_fn (Callable): This callback function is executed when the menu item is clicked. Function signature:
                void fn(name: str, path: str), where name is menu name and path is absolute path to clicked item.
            show_fn (Callable): Returns True to display this menu item. Function signature: bool fn(path: str).
                For example, test filename extension to decide whether to display a 'Play Sound' action.
            index (int): The position that this menu item will be inserted to. By default, the item will be appened.

        Returns:
            str: Name of menu item if successful, None otherwise.
        """
        if self.api:
            registry.register_checkpoint_menu(name, glyph, click_fn, show_fn, index)
            self.api.add_checkpoint_menu(name, glyph, click_fn, show_fn, index)

    def delete_checkpoint_menu(self, name: str):
        """
        Delete the menu item, with the given name, from context menu of checkpoint item.

        Args:
            name (str): Name of the menu item.
        """

        if self.api:
            registry.deregister_checkpoint_menu(name)
            self.api.delete_checkpoint_menu(name)

    def add_collection_data(self, collection_data: CollectionData):
        """Adds collection data to the browser.

        Args:
            collection_data (CollectionData): The collection data to add."""
        self._collections_data[collection_data.identifier] = collection_data
        if self.api:
            self.api.add_show_only_collection(collection_data.identifier)
            self.api.add_collection(collection_data)

    def remove_collection_data(self, collection_id: str):
        """Removes collection data from the browser.

        Args:
            collection_id (str): Identifier of the collection to remove."""
        del self._collections_data[collection_id]
        if self.api:
            self.api.remove_show_only_collection(collection_id)
            self.api.remove_collection(collection_id)


def get_content_instance():
    global g_api_singleton
    return g_api_singleton
