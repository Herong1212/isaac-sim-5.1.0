# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from functools import partial
import os

import omni
import omni.client
from omni.kit.widget.prompt import PromptButtonInfo, PromptManager

from .filebrowser import FileBrowserMode, FileBrowserSelectionType, FileBrowserUI


class FilePicker:
    def __init__(self, title, mode, file_type, filter_options, save_extensions=None):
        self._mode = mode
        self._ui_handler = None
        self._app = omni.kit.app.get_app()
        self._open_handler = None
        self._cancel_handler = None
        self._save_extensions = save_extensions
        self._ui_handler = FileBrowserUI(
            title, mode, file_type, filter_options, enable_versioning_pane=(mode == FileBrowserMode.OPEN)
        )

    def _show_prompt(self, file_path, file_save_handler):
        def _on_file_save(file_browser):
            if file_save_handler:
                file_save_handler(file_path, True)
                file_browser.hide()

        PromptManager.post_simple_prompt(
            f'{omni.ui.get_custom_glyph_code("${glyphs}/exclamation.svg")} Overwrite',
            f"File {os.path.basename(file_path)} already exists, do you want to overwrite it?",
            ok_button_info=PromptButtonInfo("YES", partial(_on_file_save, self._ui_handler)),
            cancel_button_info=PromptButtonInfo("NO")
        )

    def _save_and_prompt_if_exists(self, file_path, file_save_handler=None):
        result, _ = omni.client.stat(file_path)
        if result == omni.client.Result.OK:
            self._show_prompt(file_path, file_save_handler)
        elif file_save_handler:
            file_save_handler(file_path, False)
            self._ui_handler.hide()

    def _on_file_open(self, path, filter_index=-1):
        if self._mode == FileBrowserMode.SAVE:
            _, ext = os.path.splitext(path)
            if (
                filter_index >= 0
                and self._save_extensions
                and filter_index < len(self._save_extensions)
                and ext not in self._save_extensions
            ):
                path += self._save_extensions[filter_index]

            self._save_and_prompt_if_exists(path, self._open_handler)
        elif self._open_handler:
            self._open_handler(path, False)
            self._ui_handler.hide()

    def _on_cancel_open(self):
        if self._cancel_handler:
            self._cancel_handler()

    def set_file_selected_fn(self, file_open_handler):
        self._open_handler = file_open_handler

    def set_cancel_fn(self, cancel_handler):
        self._cancel_handler = cancel_handler

    def show(self, dir=None, filename=None):
        if self._ui_handler:
            if dir:
                self._ui_handler.set_current_directory(dir)

            if filename:
                self._ui_handler.set_current_filename(filename)
            self._ui_handler.open(self._on_file_open, self._on_cancel_open)

    def hide(self):
        if self._ui_handler:
            self._ui_handler.hide()

    def set_current_directory(self, dir):
        if self._ui_handler:
            self._ui_handler.set_current_directory(dir)

    def set_current_filename(self, filename):
        if self._ui_handler:
            self._ui_handler.set_current_filename(filename)

    def get_current_filename(self):
        if self._ui_handler:
            return self._ui_handler.get_current_filename()

        return None

    def destroy(self):
        if self._ui_handler:
            self._ui_handler.destroy()
        self._ui_handler = None
