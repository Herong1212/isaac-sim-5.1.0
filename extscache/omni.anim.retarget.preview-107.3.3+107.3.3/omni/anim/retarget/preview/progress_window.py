# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ui as ui


class ProgressWindow:
    def __init__(
        self,
        title=None,
        item_str: str = None
    ):
        self._load_count = 0
        if item_str:
            self._item_str = item_str
        else:
            self._item_str = 'item'
        self._current_item = None

        self._window = ui.Window(
            title if title else "Loading...",
            width=500,
            height=140,
            visible=False,
            flags=ui.WINDOW_FLAGS_NO_RESIZE
        )
        with self._window.frame:
            with ui.VStack():
                with ui.HStack(height=20):
                    self._progress_bar = ui.ProgressBar()
                ui.Spacer(height=3)
                self._loaded_label = ui.Label(self._loaded_text, height=20)
                self._current_label = ui.Label(self._current_text, height=40)
                ui.Spacer(height=3)
                with ui.HStack(height=0):
                    ui.Button("Close", clicked_fn=self.hide)

    def reset(self):
        self._load_count = 0
        self.set_progress(0)
        self.set_current_item(None)

    def set_progress(self, progress):
        self._progress_bar.model.set_value(progress)

    def on_loaded(self, count: int):
        self._load_count = self._load_count + count
        self._loaded_label.text = self._loaded_text

    def set_current_item(self, text: str = None):
        self._current_item = text
        self._current_label.text = self._current_text

    def clean(self):
        if self._progress_bar:
            self._progress_bar.destroy()
            self._progress_bar = None
        if self._window:
            self._window.set_visibility_changed_fn(None)
            self._window.destroy()
            self._window = None
        self._load_count = 0

    def show(self):
        self._window.visible = True

    def hide(self):
        self._window.visible = False

    @property
    def visible(self) -> bool:
        if self._window:
            return self._window.visible
        return False

    @property
    def _loaded_text(self) -> str:
        return f'Total number of {self._item_str}s loaded: {self._load_count}'

    @property
    def _current_text(self) -> str:
        result = f'Loading {self._current_item}' if self._current_item else ""
        MAX_LENGTH = 80
        if len(result) > MAX_LENGTH:
            result = result[:MAX_LENGTH] + '\n       ' + result[MAX_LENGTH:]
        return result
