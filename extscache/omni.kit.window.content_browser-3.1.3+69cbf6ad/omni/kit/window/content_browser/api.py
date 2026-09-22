# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import asyncio
import carb

from typing import List, Callable, Union
from omni.kit.window.filepicker import FilePickerAPI, delete_items, rename_item
from omni.kit.widget.filebrowser import FileBrowserItem, LISTVIEW_PANE, FileBrowserUdimItem, save_items_to_clipboard, get_clipboard_items, clear_clipboard, is_clipboard_cut
from .file_ops import add_file_open_handler, delete_file_open_handler, get_file_open_handler, cut_items, paste_items


class ContentBrowserAPI(FilePickerAPI):
    """This class defines the API methods for :obj:`ContentBrowserWidget`."""
    def __init__(self):
        super().__init__()
        self._on_selection_changed_subs = set()
        self._checkpoint_widget = None

    def _set_checkpoint_widget(self, widget: "CheckpointWidget"):
        """Internal private API."""

        self._checkpoint_widget = widget

    def add_import_menu(self, name: str, glyph: str, click_fn: Callable, show_fn: Callable) -> str:
        """
        Adds menu item, with corresponding callbacks, to the Import combo box.

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
        if self.tool_bar:
            import_menu = self.tool_bar.import_menu
            if import_menu:
                return import_menu.add_menu_item(name, glyph, click_fn, show_fn)
        return None

    def delete_import_menu(self, name: str):
        """
        Deletes the menu item, with the given name, from the Import combo box.

        Args:
            name (str): Name of the menu item.

        """
        if self.tool_bar:
            import_menu = self.tool_bar.import_menu
            if import_menu:
                import_menu.delete_menu_item(name)

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
            str: Name if successful, None otherwise.

        """
        return add_file_open_handler(name, open_fn, file_type)

    def delete_file_open_handler(self, name: str):
        """
        Unregisters the named file open handler.

        Args:
            name (str): Name of the handler.

        """
        delete_file_open_handler(name)

    def get_file_open_handler(self, url: str) -> Callable:
        """
        Returns the matching file open handler for the given file path.

        Args:
            url str: The url of the file to open.

        """
        return get_file_open_handler(url)

    def subscribe_selection_changed(self, fn: Callable):
        """
        Subscribes to file selection changes.

        Args:
            fn (Callable): callback function when file selection changed.

        """
        self._on_selection_changed_subs.add(fn)

    def unsubscribe_selection_changed(self, fn: Callable):
        """
        Unsubscribe this callback from selection changes.

        Args:
            fn (Callable): callback function when file selection changed.

        """
        if fn in self._on_selection_changed_subs:
            self._on_selection_changed_subs.remove(fn)

    def _notify_selection_subs(self, pane: int, selected: List[FileBrowserItem]):
        for fn in self._on_selection_changed_subs or []:

            async def async_cb(pane: int, selected: List[FileBrowserItem]):
                # Making sure callback was not removed between async schedule/execute
                if fn in self._on_selection_changed_subs:
                    fn(pane, selected)

            asyncio.ensure_future(async_cb(pane, selected))

    def add_checkpoint_menu(self, name: str, glyph: str, click_fn: Callable, show_fn: Callable, index=-1) -> str:
        """
        Adds menu item, with corresponding callbacks, to context menu of checkpoint items.

        Args:
            name (str): Name of the menu item, this name must be unique across the menu.
            glyph (str): Associated glyph to display for this menu item.
            click_fn (Callable): This callback function is executed when the menu item is clicked. Function signature:
                void fn(name: str, path: str), where name is menu name and path is absolute path to clicked item.
            show_fn (Callable): Returns True to display this menu item. Function signature: bool fn(path: str).
                For example, test filename extension to decide whether to display a 'Play Sound' action.
            index (int): The position that this menu item will be inserted to. By default, the item will be appended.

        Returns:
            str: Name of menu item if successful, None otherwise.

        """
        if self._checkpoint_widget:
            self._checkpoint_widget.add_context_menu(name, glyph, click_fn, show_fn, index)

    def delete_checkpoint_menu(self, name: str):
        """
        Deletes the menu item, with the given name, from the context menu of checkpoint items.

        Args:
            name (str): Name of the menu item.

        """
        if self._checkpoint_widget:
            self._checkpoint_widget.delete_context_menu(name)

    def copy_selected_items(self):
        selections = self.__get_valid_copy_cut_items()
        if selections:
            save_items_to_clipboard(selections)
        else:
            self._post_warning("Cannot rename as nothing selected!")

    def cut_selected_items(self):
        selections = self.__get_valid_copy_cut_items()
        if selections:
            for item in selections:
                if not item.writeable:
                    self._post_warning(f"Cannot cut '{item.name}' as locked!")
                    return
            cut_items(selections, self.view)

    def paste_items(self):
        selections = self.view.get_selections()
        if len(get_clipboard_items()) == 0:
            self._post_warning("Cannot paste as nothing in clipboard!")
        elif len(selections) > 1:
            self._post_warning("Cannot paste as multiple destination selected!")
        else:
            item = selections[0] if selections else self.view.get_root(LISTVIEW_PANE)
            print(f"paste to {item}")
            if not item:
                self._post_warning("Cannot paste as no available destination!")
            elif not item.is_folder:
                self._post_warning(f"Cannot paste as destination '{item.name}' is not a folder!")
            elif not item.writeable:
                self._post_warning(f"Cannot paste as destination '{item.name}' is locked!")
            else:
                paste_items(item, get_clipboard_items(), view=self.view, force_drop=True)

    def delete_selected_items(self):
        selections = self.view.get_selections()
        for item in selections:
            if not item.writeable:
                self._post_warning(f"Cannot delete '{item.name}' as locked!")
                return
            elif item.is_deleted:
                self._post_warning(f"Cannot delete '{item.name}' as already deleted!")
                return
        if len(selections) >= 1:
            item = self.view.get_root(LISTVIEW_PANE)
            # OM-72882: should not allow deleting folder/file in read-only directory
            if not item.writeable:
                self._post_warning(f"Cannot delete as '{item.name}' locked!")
            elif item.is_deleted:
                self._post_warning(f"Cannot delete as '{item.name}' already locked!")
            else:
                delete_items(selections, self.view)

    def clear_clipboard(self):
        refresh_listview = is_clipboard_cut()
        clear_clipboard()

        if refresh_listview:
            # Update listview to refresh cut item status
            self.view._filebrowser.refresh_ui(listview_only=True)

    def __get_valid_copy_cut_items(self):
        selections = self.view.get_selections(pane=LISTVIEW_PANE)
        if selections:
            for item in selections:
                if self.view.is_collection_node(item) or self.view.is_bookmark(item) or isinstance(item, FileBrowserUdimItem) or self.view.is_connection_point(item):
                    return []
        return selections

    def rename_selected_item(self):
        selections = self.view.get_selections()
        if len(selections) == 0:
            self._post_warning("Cannot rename as nothing selected!")
        elif len(selections) > 1:
            self._post_warning("Cannot rename as multiple selected!")
        elif not selections[0].writeable:
            self._post_warning(f"Cannot rename '{selections[0].name}' as locked!")
        else:
            rename_item(selections[0], self.view)

    def _post_warning(self, message: str) -> None:
        try:
            import omni.kit.notification_manager as nm
            nm.post_notification(message, status=nm.NotificationStatus.WARNING)
        except ImportError:
            pass
        finally:
            carb.log_warn(message)

    def destroy(self):
        super().destroy()

        self._checkpoint_widget = None
        if self._on_selection_changed_subs:
            self._on_selection_changed_subs.clear()
