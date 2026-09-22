# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides a helper class for collecting files from a folder with filtering and custom collection logic, and a UI class for file selection."""


from typing import Callable
from omni.kit.async_engine import run_coroutine
import asyncio
import carb
import functools
import os
import omni.client
import omni.kit.app
import traceback
import weakref
import urllib
import carb.settings
import omni.ui


class CheckBoxStatus:
    """A class to manage the status of a checkbox.

    This class holds the state of a checkbox and its associated file path, providing a structured way to manage checkbox states within UI components.

    Args:
        checkbox: The checkbox UI element this status is associated with.
        file_path: The file path related to the checkbox, used to identify it uniquely."""

    def __init__(self, checkbox, file_path):
        """Initializes a new instance of CheckBoxStatus."""
        self.checkbox = checkbox
        self.file_path = file_path
        self.is_checking = False


class SelectFileDialog:
    """A user interface class for selecting files from a dialog window.

    This class creates a modal dialog window that allows users to select multiple files and perform actions such as collecting the selected files or cancelling the selection.

    Args:
      on_collect_fn (Callable, optional): Function to call with selected files when 'Collect Selected' is clicked.
      on_cancel_fn (Callable, optional): Function to call when 'Cancel' is clicked."""

    WINDOW_WIDTH = 580
    MAX_VISIBLE_FILE_COUNT = 10

    def __init__(self, on_collect_fn=None, on_cancel_fn=None):
        self._collect_fn = on_collect_fn
        self._cancel_fn = on_cancel_fn
        self._checkboxes_status = []
        self._select_all_checkbox_is_checking = False
        self._selected_files = []

        flags = omni.ui.WINDOW_FLAGS_NO_COLLAPSE | omni.ui.WINDOW_FLAGS_NO_SCROLLBAR | omni.ui.WINDOW_FLAGS_MODAL
        self._window = omni.ui.Window(
            "Select Files to Collect",
            visible=False,
            width=0,
            height=0,
            flags=flags,
            auto_resize=True,
            padding_x=10,
            dockPreference=omni.ui.DockPreference.DISABLED,
        )

        with self._window.frame:
            with omni.ui.VStack(height=0, width=SelectFileDialog.WINDOW_WIDTH):
                self._files_scroll_frame = omni.ui.ScrollingFrame(
                    height=160, horizontal_scrollbar_policy=omni.ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON
                )
                omni.ui.Spacer(width=0, height=10)
                with omni.ui.HStack(height=0):
                    omni.ui.Spacer(height=0)
                    self._collect_selected_button = omni.ui.Button("Collect Selected", width=0, height=0)
                    self._collect_selected_button.set_clicked_fn(self._on_collect_fn)
                    omni.ui.Spacer(width=5, height=0)
                    self._cancel_button = omni.ui.Button("Cancel", width=0, height=0)
                    self._cancel_button.set_clicked_fn(self._on_cancel_fn)
                    omni.ui.Spacer(height=0)
                omni.ui.Spacer(height=5)

    def destroy(self):
        self._collect_fn = None
        self._cancel_fn = None
        self._checkboxes_status = None
        self._selected_files = None
        if self._window:
            del self._window
        self._window = None

    def __del__(self):
        self.destroy()

    def _on_collect_fn(self):
        self._window.visible = False

        async def _delay_collect(frames=2):
            for _ in range(frames):
                await omni.kit.app.get_app().next_update_async()
            if self._collect_fn:
                self._collect_fn(self._selected_files)
            self._selected_files = []

        run_coroutine(_delay_collect())

    def _on_cancel_fn(self):
        self._window.visible = False
        self._selected_files = []
        if self._cancel_fn:
            self._cancel_fn()

    def _on_select_all_fn(self, model):
        if self._select_all_checkbox_is_checking:
            return

        self._select_all_checkbox_is_checking = True
        if model.get_value_as_bool():
            for checkbox_status in self._checkboxes_status:
                checkbox_status.checkbox.model.set_value(True)
        else:
            for checkbox_status in self._checkboxes_status:
                checkbox_status.checkbox.model.set_value(False)
        self._select_all_checkbox_is_checking = False

    def _check_and_select_all(self, select_all_check_box):
        self._select_all_checkbox_is_checking = True
        select_all_check_box.model.set_value(True)
        self._select_all_checkbox_is_checking = False

    def _on_checkbox_fn(self, model, check_box_index, select_all_check_box):
        check_box_status = self._checkboxes_status[check_box_index]
        if check_box_status.is_checking:
            return

        check_box_status.is_checking = True
        if model.get_value_as_bool():
            self._selected_files.append(check_box_status.file_path)
            self._check_and_select_all(select_all_check_box)
        else:
            self._selected_files.remove(check_box_status.file_path)
            self._select_all_checkbox_is_checking = True
            select_all_check_box.model.set_value(False)
            self._select_all_checkbox_is_checking = False
        check_box_status.is_checking = False

    def show(self, file_paths=None):
        self._files_scroll_frame.clear()

        # make a copy
        self._selected_files.extend(file_paths)
        self._checkboxes_status = []

        # build layers_scroll_frame
        self._first_item_stack = None
        with self._files_scroll_frame:
            with omni.ui.VStack(height=0):
                omni.ui.Spacer(width=0, height=10)
                with omni.ui.HStack(height=0):
                    omni.ui.Spacer(width=20, height=0)
                    self._select_all_checkbox = omni.ui.CheckBox(
                        width=20, identifier="select_all", style={"font_size": 16}
                    )
                    self._select_all_checkbox.model.set_value(True)
                    omni.ui.Label("File Name", alignment=omni.ui.Alignment.LEFT)
                    omni.ui.Spacer(width=20, height=0)
                omni.ui.Spacer(width=0, height=10)
                with omni.ui.HStack(height=0):
                    omni.ui.Spacer(width=20, height=0)
                    omni.ui.Separator(height=0, style={"color": 0xFF808080})
                    omni.ui.Spacer(width=20, height=0)
                omni.ui.Spacer(width=0, height=5)

                for i in range(len(file_paths)):
                    file_path = file_paths[i]
                    style = {}
                    label_text = urllib.parse.unquote(file_path).replace("\\", "/")
                    omni.ui.Spacer(width=0, height=5)
                    stack = omni.ui.HStack(height=0, style=style)
                    if self._first_item_stack is None:
                        self._first_item_stack = stack
                    with stack:
                        omni.ui.Spacer(width=20, height=0)
                        checkbox = omni.ui.CheckBox(width=20, style={"font_size": 16})
                        checkbox.model.set_value(True)
                        omni.ui.Label(label_text, word_wrap=False, alignment=omni.ui.Alignment.LEFT)
                        omni.ui.Spacer(width=20, height=0)
                        checkbox.model.add_value_changed_fn(
                            lambda a, b=i, c=self._select_all_checkbox: self._on_checkbox_fn(a, b, c)
                        )
                        self._checkboxes_status.append(CheckBoxStatus(checkbox, file_path))

            self._select_all_checkbox.model.add_value_changed_fn(lambda a: self._on_select_all_fn(a))
        self._window.visible = True

        async def __delay_adjust_window_size(weak_self):
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            __self = weak_self()
            if not __self:
                return

            y0 = __self._files_scroll_frame.screen_position_y
            y1 = __self._first_item_stack.screen_position_y
            fixed_height = y1 - y0 + 5
            item_height = __self._first_item_stack.computed_content_height + 5
            count = min(SelectFileDialog.MAX_VISIBLE_FILE_COUNT, len(__self._selected_files))

            scroll_frame_new_height = fixed_height + count * item_height
            __self._files_scroll_frame.height = omni.ui.Pixel(scroll_frame_new_height)

        if len(file_paths) > 0:
            asyncio.ensure_future(__delay_adjust_window_size(weakref.ref(self)))

    def is_visible(self):
        return self._window.visible


def handle_exception(func):
    """Decorator that catches and logs exceptions in asynchronous functions.

    Args:
        func (Callable): The asynchronous function to be wrapped by the decorator.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            carb.log_error(f"Exception when async '{func}'")
            carb.log_error(f"{e}")
            carb.log_error(f"{traceback.format_exc()}")

    return wrapper


class FolderCollectHelper:
    """A helper class for collecting files from a specified folder with filtering and custom collection logic.

    The class is designed to process a folder, apply a filter to the files within, perform a collection operation, and execute a callback once file collection is finished. It also manages a progress popup to inform the user about the ongoing operation.

    Args:
        folder (str): The path of the folder from which to collect files.
        filter_fn (Callable): A function to filter files. It should return True for files to be collected.
        collect_fn (Callable): A function to execute on the collected files.
        finish_get_files_callback (Callable): A callback function to execute after file collection is completed.
        progress_popup: An object to show progress and status during the file collection operation."""

    def __init__(
        self,
        folder: str,
        filter_fn: Callable,
        collect_fn: Callable,
        finish_get_files_callback: Callable,
        progress_popup,
    ):
        self._collect_dir = folder
        self._filter = filter_fn
        self._collect_fn = collect_fn
        self._finish_get_files_callback = finish_get_files_callback
        self._progress_popup = progress_popup
        # set a recursive max depth for nucleus search. NGSearch service not works as expect in some nucleus server.
        self._recursive = 10
        self.__files = []
        self._select_window = None

        # omni.client doesn't understand my-computer
        if self._collect_dir.startswith("my-computer://"):
            self._collect_dir = self._collect_dir[len("my-computer://") :]

        # make the search recursively for local files
        if omni.client.is_local_url(self._collect_dir):
            self._recursive = 100

        self.__list_task = run_coroutine(self.__get_files())

    def destroy(self):
        if not self.__list_task.done():
            self.__list_task.cancel()

        self._progress_popup.hide()
        self._progress_popup = None
        if self._select_window:
            self._select_window.destroy()
            self._select_window = None

    def _get_selected_window(self):
        if not self._select_window:
            self._select_window = SelectFileDialog(self._collect_fn, self.destroy())
        return self._select_window

    async def _get_files_by_client(self, directory: str, recursive: int):
        result, entries = await omni.client.list_async(directory)
        if result != omni.client.Result.OK:
            return
        else:
            if len(entries) > 100:
                carb.log_warn(f"Skip collect folder for too many subfiles in folder: {directory}")
                return
            if recursive == self._recursive:
                self._progress_popup.status_text = f"Get folder's files 1/{len(entries)}..."
                self._progress_popup.progress = 1
                self._progress_popup.total_steps = len(entries)
            if recursive == self._recursive - 1:
                self._progress_popup.progress = self._progress_popup.progress + 1
                self._progress_popup.status_text = (
                    f"Get folder's files {self._progress_popup.progress}/{self._progress_popup.total_steps}..."
                )
            for entry in entries:
                file_path = f"{directory}/{entry.relative_path}"
                if self._filter(file_path):
                    self.__files.append(file_path)
                elif entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN and recursive > 0:
                    await self._get_files_by_client(file_path, recursive - 1)
                elif recursive == 0:
                    carb.log_warn(f"Skip collect for hierarchy is too deep in folder: {directory}")

    @handle_exception
    async def __get_files(self):
        self.__files = []
        self._progress_popup.show()
        self._progress_popup.progress = 0
        self._progress_popup.total_steps = 0
        await self._get_files_by_client(self._collect_dir, self._recursive)
        self._progress_popup.hide()
        if self._finish_get_files_callback:
            self._finish_get_files_callback()
        select_window = self._get_selected_window()
        select_window.show(self.__files)
