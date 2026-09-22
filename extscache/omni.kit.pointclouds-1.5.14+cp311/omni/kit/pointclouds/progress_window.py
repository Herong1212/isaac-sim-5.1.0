# Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from functools import partial
from pathlib import Path

import omni.ui as ui

CURRENT_PATH = Path(__file__).parent
ICONS_PATH = CURRENT_PATH.parent.parent.parent.joinpath("icons")
MAX_SCAN_TASKS_SHOW = 5


def modal_import_error(title, error_message):
    window_flags = ui.WINDOW_FLAGS_NO_RESIZE
    window_flags |= ui.WINDOW_FLAGS_NO_SCROLLBAR
    window_flags |= ui.WINDOW_FLAGS_MODAL
    window = ui.Window(title, width=0, height=0, flags=window_flags)

    def close_modal_window(window):
        window.visible = False

    with window.frame:
        with ui.VStack(height=0):
            ui.Spacer(width=0, height=10)
            with ui.HStack(height=0):
                ui.Spacer(width=40)
                ui.Label(error_message, word_wrap=True, alignment=ui.Alignment.CENTER)
                ui.Spacer(width=40)
            ui.Spacer(width=0, height=10)
            with ui.HStack(height=0):
                ui.Spacer(height=0)
                ui.Button("Close", clicked_fn=partial(close_modal_window, window))
                ui.Spacer(height=0)
            ui.Spacer(width=0, height=10)

    window.visible = True


class ProgressWindow:
    """Creates a modal window with a status label and a progress bar inside.

    Args:
        title (str): Title of this window.
        cancel_button_fn (function): The callback after cancel button is clicked.
        status_text (str): The status text.
        progress_text (str): The text appearing before the progress bar.
        warning_text (str): Tooltip text on the warning icon.
        has_progress (bool): Shows progress bar.
        has_warning (bool): Shows warning icon next to the progress bar.
        modal (bool): Set the window to be modal (cannot interact with background)
    """

    def __init__(
        self,
        title,
        cancel_button_fn=None,
        status_text="",
        progress_text="",
        warning_text="",
        button_text="",
        has_progress=False,
        has_warning=False,
        modal=False,
    ):
        self._status_texts = [status_text]
        self._progress_texts = [progress_text]
        self._progress_values = [0]
        self._warning_texts = [warning_text]
        self._error_texts = [""]
        self._title = title
        self._cancel_button_text = button_text
        self._cancel_button_fn = cancel_button_fn
        self._has_progress = has_progress
        self._has_warning = has_warning
        self._modal = modal

        self._task_idx = 0
        self._visible = False

        # widgets rebuild in each build_ui
        self._status_labels = []
        self._progress_labels = []
        self._progress_bars = []
        self._warning_icons = []
        self._error_icons = []

        self._build_ui()

    def __del__(self):
        self._cancel_button_fn = None

    def __enter__(self):
        self._popup.visible = True
        return self

    def __exit__(self, type, value, trace):
        self._popup.visible = False

    def set_cancel_fn(self, on_cancel_button_clicked):
        self._cancel_button_fn = on_cancel_button_clicked

    def set_status_text(self, status_text, has_error=False):
        self._status_labels[0].text = status_text
        self._has_error = has_error

    def get_status_text(self):
        return self._status_labels[0].text

    status_text = property(get_status_text, set_status_text)

    def set_progress_text(self, progress_text):
        if progress_text != "":
            if self._progress_labels[0]:
                self._progress_labels[0].text = progress_text
            else:
                self._has_progress = True
                self._progress_texts[0] = progress_text

    def get_progress_text(self):
        return self._progress_texts[0]

    progress_text = property(get_progress_text, set_progress_text)

    def set_button_text(self, text):
        self._cancel_button_text = text

    def set_warning_text(self, warning_text):
        if self._warning_icons[0]:
            self._warning_icons[0].visible = warning_text != ""

        if warning_text != "":
            if self._warning_icons[0]:
                self._warning_icons[0].tooltip = warning_text
            else:
                self._has_warning = True
                self._warning_texts[0] = warning_text

    def get_warning_text(self):
        return self._warning_icons[0].tooltip if self._has_warning else ""

    warning_text = property(get_warning_text, set_warning_text)

    def show(self):
        self._visible = True
        self._popup.visible = True

    def hide(self):
        self._visible = False
        self._popup.visible = False

    def is_visible(self):
        return self._popup.visible

    def set_progress(self, value):
        if self._has_progress:
            if self._progress_bars[0]:
                self._progress_bars[0].model.set_value(value)
            else:
                self._progress_values[0] = value

    def create_task(self):
        self._task_idx = self._task_idx + 1
        self._status_texts.append("")
        self._progress_texts.append("")
        self._progress_values.append(0)
        self._warning_texts.append("")
        self._error_texts.append("")
        self._build_ui()
        if self._popup:
            self._popup.visible = True
        return self._task_idx

    def set_task_status_text(self, task_idx, status_text, error_text=""):
        self._status_texts[task_idx] = status_text
        self._error_texts[task_idx] = error_text
        if task_idx >= len(self._status_labels):
            self._build_ui()
        elif self._status_labels[task_idx]:
            if status_text != "":
                self._status_labels[task_idx].text = status_text
            self._error_icons[task_idx].visible = self._error_texts[task_idx] != ""
            self._error_icons[task_idx].tooltip = self._error_texts[task_idx]

    def set_task_progress_text(self, task_idx, progress_text):
        self._progress_texts[task_idx] = progress_text
        if task_idx >= len(self._progress_labels):
            self._build_ui()
        elif self._progress_labels[task_idx]:
            self._progress_labels[task_idx].text = progress_text

    def set_task_progress(self, task_idx, value):
        self._progress_values[task_idx] = value
        if task_idx >= len(self._progress_bars):
            self._build_ui()
        if self._progress_bars[task_idx]:
            self._progress_bars[task_idx].visible = True
            self._progress_bars[task_idx].model.set_value(value)

    def set_task_warning_text(self, task_idx, warning_text):
        self._warning_texts[task_idx] = warning_text
        if task_idx >= len(self._warning_icons):
            self._build_ui()
        elif self._warning_icons[task_idx]:
            self._warning_icons[task_idx].visible = warning_text != ""
            self._warning_icons[task_idx].tooltip = warning_text

    def _on_cancel_button_fn(self):
        self.hide()
        if self._cancel_button_fn:
            self._cancel_button_fn()

    def _build_ui(self):
        self._popup = ui.Window(self._title, visible=False, height=0, dockPreference=ui.DockPreference.DISABLED)
        self._popup.flags = ui.WINDOW_FLAGS_NO_COLLAPSE | ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_RESIZE

        if self._modal:
            self._popup.flags = self._popup.flags | ui.WINDOW_FLAGS_MODAL | ui.WINDOW_FLAGS_NO_MOVE

        self._status_labels = []
        self._progress_labels = []
        self._progress_bars = []
        self._warning_icons = []

        tasks_cnt = len(self._status_texts)

        with self._popup.frame:
            with ui.VStack(height=0):
                if tasks_cnt > MAX_SCAN_TASKS_SHOW:
                    frame = ui.ScrollingFrame(
                        height=73 * MAX_SCAN_TASKS_SHOW,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    )
                else:
                    frame = ui.Frame(height=0)
                with frame:
                    with ui.VStack(height=0):
                        for i in range(tasks_cnt):
                            if i == 0 and tasks_cnt > 1:
                                # Skip initial status if there are already tasks loading
                                self._status_labels = [None]
                                self._progress_labels = [None]
                                self._progress_bars = [None]
                                self._warning_icons = [None]
                                self._error_icons = [None]
                                continue
                            ui.Spacer(height=10)
                            with ui.VStack(height=0):
                                with ui.HStack(height=0):
                                    ui.Spacer(width=10)
                                    with ui.HStack(height=0):
                                        self._error_icons.append(ui.ImageWithProvider(width=15))
                                        self._error_icons[i].style = {
                                            "image_url": str(ICONS_PATH.joinpath("error.svg"))
                                        }
                                        self._error_icons[i].tooltip = self._error_texts[i]
                                        self._error_icons[i].visible = self._error_texts[i] != ""
                                        ui.Spacer(width=7)
                                        self._status_labels.append(ui.Label(self._status_texts[i], width=0, height=0))
                                if self._has_progress:
                                    ui.Spacer(height=10)
                                    with ui.HStack(height=0):
                                        ui.Spacer(width=20)
                                        self._progress_labels.append(
                                            ui.Label(self._progress_texts[i], width=0, height=0)
                                        )
                                        ui.Spacer(width=7)
                                        self._progress_bars.append(ui.ProgressBar())
                                        self._progress_bars[i].visible = self._progress_texts[i] != ""
                                        self._progress_bars[i].model.set_value(self._progress_values[i])
                                        if self._has_warning:
                                            ui.Spacer(width=7)
                                            self._warning_icons.append(ui.ImageWithProvider(width=15))
                                            self._warning_icons[i].style = {
                                                "image_url": str(ICONS_PATH.joinpath("warn.svg"))
                                            }
                                            self._warning_icons[i].tooltip = self._warning_texts[i]
                                            self._warning_icons[i].visible = self._warning_texts[i] != ""
                                        ui.Spacer(width=10)
                                    ui.Spacer(height=5)
                            ui.Spacer(height=10)
                ui.Spacer(height=5)
                with ui.HStack(height=0):
                    ui.Spacer(height=0)
                    cancel_button = ui.Button(self._cancel_button_text, width=0, height=0)
                    cancel_button.set_clicked_fn(self._on_cancel_button_fn)
                    ui.Spacer(height=0)
                ui.Spacer(width=0, height=10)

        self._popup.visible = self._visible
