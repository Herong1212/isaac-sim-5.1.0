# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
import re
from typing import Iterable, Tuple, Union

import omni.client

from omni.kit.window.filepicker import FilePickerDialog
from omni.kit.widget.filebrowser import FileBrowserItem


class FileBrowserSelectionType:
    FILE_ONLY = 0
    DIRECTORY_ONLY = 1
    ALL = 2


class FileBrowserMode:
    OPEN = 0
    SAVE = 1


class FileBrowserUI:
    def __init__(self, title, mode, selection_type, filter_options, **kwargs):
        if mode == FileBrowserMode.OPEN:
            confirm_text = "Open"
        else:
            confirm_text = "Save"
        self._file_picker = FilePickerApp(title, confirm_text, selection_type, filter_options, **kwargs)

    def set_current_directory(self, dir):
        self._file_picker.set_current_directory(dir)

    def set_current_filename(self, filename):
        self._file_picker.set_current_filename(filename)

    def get_current_filename(self):
        return self._file_picker.get_current_filename()

    def open(self, select_fn, cancel_fn):
        self._file_picker.set_custom_fn(select_fn, cancel_fn)
        self._file_picker.show_dialog()

    def destroy(self):
        self._file_picker.set_custom_fn(None, None)
        self._file_picker = None

    def hide(self):
        self._file_picker.hide_dialog()


class FilePickerApp:
    """
    Standalone app to demonstrate the use of the FilePicker dialog.

    Args:
        title (str): Title of the window.
        apply_button_name (str): Name of the confirm button.
        selection_type (FileBrowserSelectionType): The file type that confirm event will respond to.
        item_filter_options (list): Array of filter options. Element of array
        is a tuple that first element of this tuple is the regex string for filtering,
        and second element of this tuple is the descriptions, like ("*.*", "All Files").
        By default, it will list all files.
        kwargs: additional keyword arguments to be passed to FilePickerDialog.
    """

    def __init__(
        self,
        title: str,
        apply_button_name: str,
        selection_type: FileBrowserSelectionType = FileBrowserSelectionType.ALL,
        item_filter_options: Iterable[Tuple[Union[re.Pattern, str], str]] = ((
            re.compile(".*"), "All Files (*.*)")),
        **kwargs,
    ):
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
        self._build_ui(**kwargs)

    def set_custom_fn(self, select_fn, cancel_fn):
        self._custom_select_fn = select_fn
        self._custom_cancel_fn = cancel_fn

    def show_dialog(self):
        self._filepicker.show(self._current_directory)
        self._current_directory = None

    def hide_dialog(self):
        self._filepicker.hide()

    def set_current_directory(self, dir: str):
        self._current_directory = dir
        if not self._current_directory.endswith("/"):
            self._current_directory += "/"

    def set_current_filename(self, filename: str):
        self._filepicker.set_filename(filename)

    def get_current_filename(self):
        return self._filepicker.get_filename()

    def _build_ui(self, **kwargs):
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
            **kwargs,
        )

    def _on_filter_item(self, item: FileBrowserItem) -> bool:
        if not item or item.is_folder:
            return True

        if self._filepicker.current_filter_option >= len(self._filter_regexes):
            return False

        regex = self._filter_regexes[self._filepicker.current_filter_option]
        if regex.match(item.path):
            return True
        else:
            return False

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
        fullpath = omni.client.make_absolute_url_if_possible(dirname, filename)

        result, entry = omni.client.stat(fullpath)
        if result == omni.client.Result.OK and entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN:
            is_folder = True
        else:
            is_folder = False

        if not is_folder and self._selection_type == FileBrowserSelectionType.DIRECTORY_ONLY:
            return

        if self._custom_select_fn:
            self._custom_select_fn(fullpath, self._filepicker.current_filter_option)
        else:
            self.hide_dialog()

    async def _on_click_cancel(self, filename: str, dirname: str):
        """
        This function is called when the user clicks 'Cancel'.
        """
        if self._custom_cancel_fn:
            self._custom_cancel_fn()

        self.hide_dialog()
