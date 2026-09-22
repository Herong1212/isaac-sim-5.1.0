# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["FilePickerDialog"]
import carb
import omni.ui as ui

from typing import List, Callable, Tuple
from omni.kit.widget.filebrowser import FileBrowserModel
from .widget import FilePickerWidget
from .detail_view import DetailFrameController
from .utils import exec_after_redraw


class FilePickerDialog:
    """
    A popup window for browsing the filesystem and taking action on a selected file.
    Includes a browser bar for keyboard input with auto-completion for navigation of the tree
    view.  For similar but different options, see also :obj:`FilePickerWidget` and :obj:`FilePickerView`.

    Args:
        title (str): Window title. Default None.

    Keyword Args:
        width (int): Window width. Default 1000.
        height (int): Window height. Default 600.
        click_apply_handler (Callable): Function that will be called when the user accepts
            the selection. Function signature:
            apply_handler(file_name: str, dir_name: str) -> None.
        click_cancel_handler (Callable): Function that will be called when the user clicks
            the cancel button. Function signature:
            cancel_handler(file_name: str, dir_name: str) -> None.
        other: Additional args listed for :obj:`FilePickerWidget`

    """

    def __init__(self, title: str, **kwargs):
        self._window = None
        self._widget = None
        self._width = kwargs.get("width", 1000)
        self._height = kwargs.get("height", 600)
        self._click_cancel_handler = kwargs.get("click_cancel_handler", None)
        self._click_apply_handler = kwargs.get("click_apply_handler")
        self.__show_task = None

        self._key_functions = {
            int(carb.input.KeyboardInput.ESCAPE): self._click_cancel_handler,
            # OM-79404: Add enter key press handler
            # OM-117841 Temporarily revert the changes when enter key press.
            # int(carb.input.KeyboardInput.ENTER): self._click_apply_handler,
        }

        self._build_ui(title, **kwargs)

    def _build_ui(self, title: str, **kwargs):
        window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_DOCKING
        self._window = ui.Window(title, width=self._width, height=self._height, flags=window_flags)
        self._window.set_key_pressed_fn(self._on_key_pressed)

        def on_cancel(*args):
            if self._click_cancel_handler:
                self._click_cancel_handler(*args)
            else:
                self._window.visible = False

        with self._window.frame:
            kwargs["click_cancel_handler"] = on_cancel
            self._key_functions[int(carb.input.KeyboardInput.ESCAPE)] = on_cancel
            self._widget = FilePickerWidget(title, window=self._window, **kwargs)
            self._window.set_width_changed_fn(self._widget._on_window_width_changed)

    def _on_key_pressed(self, key, mod, pressed):
        if not pressed:
            return

        func = self._key_functions.get(key)
        if func and mod in (0, ui.Widget.FLAG_WANT_CAPTURE_KEYBOARD):
            filename, dirname = self._widget.get_selected_filename_and_directory()
            func(filename, dirname)

    def set_visibility_changed_listener(self, listener: Callable[[bool], None]):
        """
        Call the given handler when window visibility is changed.

        Args:
            listener (Callable): Handler with signature listener[visible: bool).

        """
        if self._window:
            self._window.set_visibility_changed_fn(listener)

    def add_connections(self, connections: dict):
        """
        Adds specified server connections to the browser.

        Args:
            connections (dict): A dictionary of name, path pairs. For example:
                {"C:": "C:", "ov-content": "omniverse://ov-content"}.  Paths to Omniverse servers
                should be prefixed with "omniverse://".

        """
        self._widget.api.add_connections(connections)

    def set_current_directory(self, path: str):
        """
        Procedurally sets the current directory path.

        Args:
            path (str): The full path name of the folder, e.g. "omniverse://ov-content/Users/me.

        Raises:
            :obj:`RuntimeWarning`: If path doesn't exist or is unreachable.

        """
        self._widget.api.set_current_directory(path)

    def get_current_directory(self) -> str:
        """
        Returns the current directory from the browser bar.

        Returns:
            str: The system path, which may be different from the displayed path.

        """
        return self._widget.api.get_current_directory()

    def get_current_selections(self, pane: int = 2) -> List[str]:
        """
        Returns current selected as list of system path names.

        Args:
            pane (int): Specifies pane to retrieve selections from, one of {TREEVIEW_PANE = 1, LISTVIEW_PANE = 2,
                BOTH = None}.  Default LISTVIEW_PANE.
        Returns:
            [str]: List of system paths (which may be different from displayed paths, e.g. bookmarks)

        """
        return self._widget.api.get_current_selections(pane)

    def set_filename(self, filename: str):
        """
        Sets the filename in the file bar, at bottom of the dialog.

        Args:
            filename (str): The filename only (and not the fullpath), e.g. "myfile.usd".

        """
        self._widget.api.set_filename(filename)

    def get_filename(self) -> str:
        """
        Returns:
            str: Currently selected filename.
        """
        return self._widget.api.get_filename()

    def get_file_postfix(self) -> str:
        """
        Returns:
            str: Currently selected postfix.
        """
        return self._widget.file_bar.selected_postfix

    def set_file_postfix(self, postfix: str):
        """Sets the file postfix in the file bar."""
        self._widget.file_bar.set_postfix(postfix)

    def get_file_postfix_options(self) -> List[str]:
        """
        Returns:
            List[str]: List of all postfix strings.
        """
        return self._widget.file_bar.postfix_options

    def get_file_extension(self) -> str:
        """
        Returns:
            str: Currently selected filename extension.
        """
        return self._widget.file_bar.selected_extension

    def set_file_extension(self, extension: str):
        """Sets the file extension in the file bar."""
        self._widget.file_bar.set_extension(extension)

    def get_file_extension_options(self) -> List[Tuple[str, str]]:
        """
        Returns:
            List[str]: List of all extension options strings.
        """
        return self._widget.file_bar.extension_options

    def set_filebar_label_name(self, name: str):
        """
        Sets the text of the name label for filebar, at the bottom of dialog.

        Args:
            name (str): By default, it's "File name" if it's not set. For some senarios that,
            it only allows to choose folder, it can be configured with this API for better UX.
        """
        self._widget.file_bar.label_name = name

    def get_filebar_label_name(self) -> str:
        """
        Returns:
            str: Currently text of name label for file bar.
        """
        return self._widget.file_bar.label_name

    def set_item_filter_fn(self, item_filter_fn: Callable[[str], bool]):
        """
        Sets the item filter function.

        Args:
            item_filter_fn (Callable): Signature is bool fn(item: FileBrowserItem)

        """
        self._widget.set_item_filter_fn(item_filter_fn)

    def set_click_apply_handler(self, click_apply_handler: Callable[[str, str], None]):
        """
        Sets the function to execute upon clicking apply.

        Args:
            click_apply_handler (Callable): Callback with filename being the name of the file, and dirname being the containing directory path with an ending slash.
                Function Signature is fn(filename: str, dirname: str) -> None

        """
        self._widget.set_click_apply_handler(click_apply_handler)
        # OM-79404: update key func for ENTER key when reseting click apply handler
        # OM-117841 Temporarily revert the changes when enter key press.
        # self._key_functions[int(carb.input.KeyboardInput.ENTER)] = click_apply_handler

    def navigate_to(self, path: str):
        """
        Navigates to a path, i.e. the path's parent directory will be expanded and leaf selected.

        Args:
            path (str): The path to navigate to.

        """
        self._widget.api.navigate_to(path)

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
        self._widget.api.toggle_bookmark_from_path(name, path, is_bookmark, is_folder=is_folder)

    def refresh_current_directory(self):
        """Refreshes the current directory set in the browser bar."""
        self._widget.api.refresh_current_directory()

    @property
    def current_filter_option(self):
        """int: Index of current filter option, range 0 .. num_filter_options."""
        return self._widget.current_filter_option

    def add_detail_frame_from_controller(self, name: str, controller: DetailFrameController):
        """
        Adds subsection to the detail view, and populate it with a custom built widget.

        Args:
            name (str): Name of the widget sub-section, this name must be unique over all detail sub-sections.
            controller (:obj:`DetailFrameController`): Controller object that encapsulates all aspects of creating,
                updating, and deleting a detail frame widget.

        Returns:
            ui.Widget: Handle to created widget.

        """
        self._widget.api.add_detail_frame_from_controller(name, controller)

    def delete_detail_frame(self, name: str):
        """
        Deletes the named detail frame.

        Args:
            name (str): Name of the frame.

        """
        self._widget.api.delete_detail_frame(name)

    def set_search_delegate(self, delegate):
        """
        Sets a custom search delegate for the tool bar.

        Args:
            delegate (:obj:`SearchDelegate`): Object that creates the search widget.

        """
        self._widget.api.set_search_delegate(delegate)

    def show_model(self, model: FileBrowserModel):
        """
        Displays the given model in the list view, overriding the default model.  For example, this model
        might be the result of a search.

        Args:
            model (:obj:`FileBrowserModel`): Model to display.

        """
        self._widget.api.show_model(model)

    def show(self, path: str = None):
        """
        Shows this dialog.  Currently pops up atop all other windows but is not completely
        modal, i.e. does not take over input focus.

        Args:
            path (str): If optional path is specified, then navigates to it upon startup.

        """
        self._window.visible = True
        if path:
            if self.__show_task:
                self.__show_task.cancel()
            self.__show_task = exec_after_redraw(lambda path=path: self.navigate_to(path), 6)

    def hide(self):
        """
        Hides this dialog. Automatically called when "Cancel" buttons is clicked.

        """
        self._window.visible = False

    def destroy(self):
        """Destructor."""
        if self.__show_task:
            self.__show_task.cancel()
        self.__show_task = None
        if self._widget is not None:
            self._widget.destroy()
        self._widget = None
        if self._window:
            self.set_visibility_changed_listener(None)
            self._window.destroy()
        self._window = None
