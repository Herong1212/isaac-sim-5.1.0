# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""A pop up window class to show while waiting operations to be done."""
import urllib
import carb
import carb.settings
import omni.ui as ui

from typing import List, Callable


class Prompt:
    """
    A pop up window in context manager style to perform operations when inside the context.

    Args:
        title (str): window title.
        text (str): decription of the operation to perform when in context.
        button_text (List[str]): text of buttons to create.
        button_fn (List[Callable]): functions to call after clicking buttons.
    Keyword Args:
        modal (bool): True to disable hang detection when in context.
        callback_addons (List[Callable]): callbacks to perform after initializing the window.
        callback_destroy (List[Callable]): callbacks to perform after destroying the window.
        decode_text (bool): unwrap quotes if set.
    """
    def __init__(
        self, title: str, text: str, button_text: List[str], button_fn: List[Callable[[], None]], modal: bool = False,
        callback_addons: List[Callable[[], None]] = [], callback_destroy: List[Callable[[], None]] = [], decode_text: bool = True
    ):
        self._title = title
        self._text = urllib.parse.unquote(text) if decode_text else text
        self._button_list = []
        self._modal = modal
        self._callback_addons = callback_addons
        self._callback_destroy = callback_destroy
        self._buttons = []
        for name, fn in zip(button_text, button_fn):
            self._button_list.append((name, fn))

        self._build_ui()

    def destroy(self):
        """ Destructor. """
        self._cancel_button_fn = None
        self._ok_button_fn = None
        self._button_list = []
        if self._window:
            self._window.destroy()
            del self._window
        self._window = None

        for button in self._buttons:
            button.set_clicked_fn(None)
        self._buttons.clear()

        self._callback_addons = []

        for callback in self._callback_destroy:
            if callback and callable(callback):
                callback()

        self._callback_destroy = []

    def __del__(self):
        self.destroy()

    def __enter__(self):
        self.show()

        if self._modal:
            settings = carb.settings.get_settings()
            # Only use first word as a reason (e.g. "Creating, Opening"). URL won't work as a setting key.
            operation = self._text.split(" ")[0].lower()
            self._hang_detector_disable_key = "/app/hangDetector/disableReasons/{0}".format(operation)
            settings.set(self._hang_detector_disable_key, "1")
            settings.set("/crashreporter/data/appState", operation)

        return self

    def __exit__(self, type, value, trace):
        self.hide()

        if self._modal:
            settings = carb.settings.get_settings()
            settings.destroy_item(self._hang_detector_disable_key)
            settings.set("/crashreporter/data/appState", "started")

    def show(self):
        """ Show the window. """
        self._window.visible = True

    def hide(self):
        """ Hide the window. """
        self._window.visible = False

    def is_visible(self):
        """
        Return:
            Return True if window is visible.
        """
        return self._window.visible

    def set_text(self, text):
        """ Set the operation description. """
        self._text_label.text = text

    def _build_ui(self):
        self._window = ui.Window(
            self._title, visible=False, height=0, dockPreference=ui.DockPreference.DISABLED, raster_policy=ui.RasterPolicy.NEVER
        )
        self._window.flags = (
            ui.WINDOW_FLAGS_NO_COLLAPSE
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_SCROLLBAR
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_MOVE
            | ui.WINDOW_FLAGS_NO_CLOSE
        )

        if self._modal:
            self._window.flags |= ui.WINDOW_FLAGS_MODAL

        with self._window.frame:
            with ui.VStack(height=0):
                ui.Spacer(width=0, height=10)
                with ui.HStack(height=0):
                    ui.Spacer(widht=10, height=0)
                    self._text_label = ui.Label(
                        self._text,
                        width=ui.Percent(100),
                        height=0,
                        word_wrap=True,
                        alignment=ui.Alignment.CENTER,
                    )
                    ui.Spacer(widht=10, height=0)
                ui.Spacer(width=0, height=10)
                with ui.HStack(height=0):
                    ui.Spacer(height=0)
                    for name, fn in self._button_list:
                        if name:
                            button = ui.Button(name)
                            if fn:
                                button.set_clicked_fn(lambda on_fn=fn: (self.hide(), on_fn()))
                            else:
                                button.set_clicked_fn(lambda: self.hide())
                            self._buttons.append(button)
                    ui.Spacer(height=0)
                ui.Spacer(width=0, height=10)

                for callback in self._callback_addons:
                    if callback and callable(callback):
                        callback()
