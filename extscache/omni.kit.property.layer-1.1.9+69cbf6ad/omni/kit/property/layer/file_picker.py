"""This module provides a file selection dialog interface for selecting files or directories with customizable filters and actions."""

__all__ = ["FilePicker"]

import asyncio
import re
from typing import Iterable, Tuple, Union

import omni.client
import omni.ui
from omni.kit.widget.filebrowser import FileBrowserItem
from omni.kit.window.filepicker import FilePickerDialog


class FileBrowserSelectionType:
    """Enumeration of file browser selection types.

    This class defines constants to specify the type of items that can be selected in a file browser. It is used to configure file pickers and dialogs to restrict the selection to files, directories, or allow both.

    Attributes:
        FILE_ONLY (int): Constant to specify that only files can be selected.
        DIRECTORY_ONLY (int): Constant to specify that only directories can be selected.
        ALL (int): Constant to allow selection of both files and directories."""

    FILE_ONLY = 0
    """int: Represents selection of files only."""
    DIRECTORY_ONLY = 1
    """int: Represents selection of directories only."""
    ALL = 2
    """int: Allows selection of both files and directories."""


class FilePicker:
    """A class for creating a file selection dialog.

    This class provides a user interface to select files or directories from the filesystem.

    Args:
        title (str): The title of the file picker window.
        apply_button_name (str): The label of the apply button in the dialog.
        selection_type (:obj:`FileBrowserSelectionType`): The type of selection to allow (file, directory, or both).
        item_filter_options (Iterable[Tuple[Union[re.Pattern, str], str]]): A list of filter options for limiting the files that can be selected. Each filter option is a tuple where the first element is a regex pattern (as a string or compiled regex object) that files must match, and the second element is a human-readable description of the filter.
    """

    def __init__(
        self,
        title: str,
        apply_button_name: str,
        selection_type: FileBrowserSelectionType = FileBrowserSelectionType.ALL,
        item_filter_options: Iterable[Tuple[Union[re.Pattern, str], str]] = ((re.compile(".*"), "All Files (*.*)")),
    ):
        """Initializes the FilePicker with custom configurations."""
        self._title = title
        self._filepicker = None
        self._selection_type = selection_type
        self._custom_select_fn = None
        self._custom_cancel_fn = None
        self._apply_button_name = apply_button_name
        self._filter_regexes = []
        self._filter_descriptions = []
        self._current_directory = None
        for regex, desc in item_filter_options:
            if not isinstance(regex, re.Pattern):
                regex = re.compile(regex, re.IGNORECASE)
            self._filter_regexes.append(regex)
            self._filter_descriptions.append(desc)
        self._build_ui()

    def destroy(self):
        """Cleans up the file picker and destroys the file picker dialog."""
        self.set_custom_fn(None, None)
        if self._filepicker:
            self._filepicker.destroy()

    def set_custom_fn(self, select_fn, cancel_fn):
        """Sets custom functions for select and cancel actions.

        Args:
            select_fn (Callable): Function to call when a file is selected.
            cancel_fn (Callable): Function to call when the dialog is canceled."""
        self._custom_select_fn = select_fn
        self._custom_cancel_fn = cancel_fn

    def show_dialog(self):
        """Displays the file picker dialog using the current directory."""
        self._filepicker.show(self._current_directory)
        self._current_directory = None

    def hide_dialog(self):
        """Hides the file picker dialog."""
        self._filepicker.hide()

    def set_current_directory(self, dir_path: str):
        """Sets the current directory for the file picker.

        Args:
            dir (str): The directory to be set as current."""
        self._current_directory = dir_path

    def set_current_filename(self, filename: str):
        """Sets the filename in the file picker's dialog.

        Args:
            filename (str): The filename to be set."""
        self._filepicker.set_filename(filename)

    def _build_ui(self):
        on_click_open = lambda f, d: asyncio.ensure_future(self._on_click_open(f, d))
        on_click_cancel = lambda f, d: asyncio.ensure_future(self._on_click_cancel(f, d))

        # Create the dialog
        self._filepicker = FilePickerDialog(
            self._title,
            allow_multi_selection=False,
            apply_button_label=self._apply_button_name,
            click_apply_handler=on_click_open,
            click_cancel_handler=on_click_cancel,
            item_filter_options=self._filter_descriptions,
            item_filter_fn=lambda item: self._on_filter_item(item),
            error_handler=lambda m: self._on_error(m),
        )

        # Start off hidden
        self.hide_dialog()

    def _on_filter_item(self, item: FileBrowserItem) -> bool:
        if not item or item.is_folder:
            return True

        if self._filepicker.current_filter_option >= len(self._filter_regexes):
            return False

        regex = self._filter_regexes[self._filepicker.current_filter_option]
        return regex.match(item.path)

    def _on_error(self, msg: str):
        """
        Demonstrates error handling. Instead of just printing to the shell, the App can
        display the error message to a console window.
        """
        print(msg)

    async def _on_click_open(self, filename: str, dirname: str):
        """
        The meat of the App is done in this callback when the user clicks 'Accept'. This is
        a potentially costly operation so we implement it as an async operation.  The inputs
        are the filename and directory name. Together they form the fullpath to the selected
        file.
        """
        dirname = dirname.strip()
        if dirname and not dirname.endswith("/"):
            dirname += "/"
        fullpath = f"{dirname}{filename}"

        result, entry = omni.client.stat(fullpath)
        is_folder = bool(result == omni.client.Result.OK and entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN)
        if (is_folder and self._selection_type == FileBrowserSelectionType.FILE_ONLY) or (
            not is_folder and self._selection_type == FileBrowserSelectionType.DIRECTORY_ONLY
        ):
            return

        self.hide_dialog()
        await omni.kit.app.get_app().next_update_async()

        if self._custom_select_fn:
            self._custom_select_fn(fullpath)

    async def _on_click_cancel(self, filename: str, dirname: str):
        """
        This function is called when the user clicks 'Cancel'.
        """
        self.hide_dialog()
        await omni.kit.app.get_app().next_update_async()

        if self._custom_cancel_fn:
            self._custom_cancel_fn()
