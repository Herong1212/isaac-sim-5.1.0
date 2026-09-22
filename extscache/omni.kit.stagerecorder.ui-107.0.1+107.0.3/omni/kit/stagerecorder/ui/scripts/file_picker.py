# Copyright (c) 2022-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
import os
import re
from typing import Callable

import carb
import omni.client
import omni.ui
import psutil
from omni.kit.widget.filebrowser import FileBrowserItem
from omni.kit.window.filepicker import FilePickerDialog


class FileBrowserSelectionType:
    FILE_ONLY = 0
    DIRECTORY_ONLY = 1
    ALL = 2


class FilePicker:
    """
    Args:
        title (str): Title of the window.
        apply_button_name (str): Name of the confirm button.
        selection_type (FileBrowserSelectionType): The file type that confirm event will respond to.
        item_filter_options (list): Array of filter options. Element of array
        is a tuple that first element of this tuple is the regex string for filtering,
        and second element of this tuple is the descriptions, like ("*.*", "All Files").
        By default, it will list all files.
    """

    def __init__(
        self,
        title: str,
        apply_button_name: str,
        selection_type: FileBrowserSelectionType = FileBrowserSelectionType.ALL,
        item_filter_options: list = [("*.*", "All Files (*.*)")],
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
        for item in item_filter_options:
            self._filter_regexes.append(re.compile(item[0], re.IGNORECASE))
            self._filter_descriptions.append(item[1])
        self._build_ui()

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
        if dirname:
            fullpath = f"{dirname}/{filename}"
        else:
            fullpath = filename

        result, entry = omni.client.stat(fullpath)
        if result == omni.client.Result.OK and entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN:
            is_folder = True
        else:
            is_folder = False

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
