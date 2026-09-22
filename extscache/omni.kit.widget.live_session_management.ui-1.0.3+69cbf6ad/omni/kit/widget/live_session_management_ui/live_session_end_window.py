# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["LiveSessionEndWindow"]

import asyncio
from typing import Callable

import carb
import omni.ui as ui

from .file_picker import FilePicker, FileBrowserMode, FileBrowserSelectionType


class LiveSessionEndWindow:

    def __init__(self, current_session, on_ok_button_cb: Callable[[], None], warn_root_prims=False):
        self.current_session = current_session
        self._window = None
        self._buttons = []
        self.options_combo = None
        self._file_picker = None
        self._on_ok_button_cb = on_ok_button_cb

        self._key_functions = {
            int(carb.input.KeyboardInput.ENTER): self._on_ok_button_fn,
            int(carb.input.KeyboardInput.ESCAPE): self._on_cancel_button_fn
        }

        self._build_ui()
        if warn_root_prims:
            self.set_error_msg("There are PrimSpecs defined in the root layer.  Changes from the live session could be hidden if they are merged to a new layer.")

    def destroy(self):
        for button in self._buttons:
            button.set_clicked_fn(None)
        self._buttons.clear()
        if self._window:
            self._window.visible = False
        self._window = None
        self.options_combo = None
        if self._file_picker:
            self._file_picker.destroy()
        self._file_picker = None

    async def __aenter__(self):
        self.visible = True
        # Wait until dialog disappears
        while self.visible:
            await asyncio.sleep(0.1)

    async def __aexit__(self, exc_type, exc, tb):
        self.visible = False

    @property
    def visible(self):
        return self._window and self._window.visible

    @visible.setter
    def visible(self, value):
        if self._window:
            self._window.visible = value

    def _on_ok_button_fn(self):
        # Clear error message
        self.set_error_msg("")

        # Call callback
        if self._on_ok_button_cb:
            self._on_ok_button_cb()

    def _on_cancel_button_fn(self):
        self.visible = False

    def _on_key_pressed_fn(self, key, mod, pressed):
        if not pressed:
            return

        func = self._key_functions.get(key)
        if func:
            func()

    def _create_file_picker(self):
        filter_options = [
            (r"^(?=.*.usd$)((?!.*\.(sublayer)\.usd).)*$", "USD File (*.usd)"),
            (r"^(?=.*.usda$)((?!.*\.(sublayer)\.usda).)*$", "USDA File (*.usda)"),
            (r"^(?=.*.usdc$)((?!.*\.(sublayer)\.usdc).)*$", "USDC File (*.usdc)"),
            ("(.*?)", "All Files (*.*)"),
        ]
        layer_file_picker = FilePicker(
            "Save Live Changes",
            FileBrowserMode.SAVE,
            FileBrowserSelectionType.FILE_ONLY,
            filter_options,
            [".usd", ".usda", ".usdc", ".usd"],
        )

        return layer_file_picker

    def show_file_picker(self, file_handler, default_location=None, default_filename=None, new_os_window=False):
        if not self._file_picker:
            self._file_picker = self._create_file_picker()

        self._file_picker.set_file_selected_fn(file_handler)
        self._file_picker.show(default_location, default_filename)

        if new_os_window:
            self._file_picker._ui_handler._file_picker._filepicker._window.move_to_new_os_window()

    def _on_description_begin_edit(self, model):
        self.description_field_hint_label.visible = False

    def _on_description_end_edit(self, model):
        if len(model.get_value_as_string()) == 0:
            self.description_field_hint_label.visible = True

    def set_error_msg(self, msg):
        """Show error message in dialog"""
        self._error_label.text = msg

    def _build_ui(self):
        """Construct the window based on the current parameters"""
        self._window = ui.Window("Merge Options", visible=False, height=0, dockPreference=ui.DockPreference.DISABLED)
        self._window.flags = (
            ui.WINDOW_FLAGS_NO_COLLAPSE | ui.WINDOW_FLAGS_NO_SCROLLBAR |
            ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_MOVE
        )
        self._window.set_key_pressed_fn(self._on_key_pressed_fn)
        self._window.flags = self._window.flags | ui.WINDOW_FLAGS_MODAL

        with self._window.frame:
            with ui.VStack(height=0):
                ui.Spacer(width=0, height=10)
                with ui.HStack(height=0):
                    ui.Spacer()
                    ui.Label(
                        "Live Session is ending.", word_wrap=True, alignment=ui.Alignment.CENTER, width=self._window.width - 80, height=0
                    )
                    ui.Spacer()
                with ui.HStack(height=0):
                    ui.Spacer()
                    ui.Label(
                        f"How do you want to merge changes from '{self.current_session.name}' session?",
                        alignment=ui.Alignment.CENTER, word_wrap=True, width=self._window.width - 80, height=0
                    )
                    ui.Spacer()
                ui.Spacer(width=0, height=10)
                with ui.HStack(height=0):
                    ui.Spacer()
                    self.options_combo = ui.ComboBox(
                        0, "Merge to corresponding layers", "Merge to a new layer",
                        word_wrap=True, width=self._window.width - 80, height=0
                    )
                    ui.Spacer()

                ui.Spacer(width=0, height=10)

                with ui.HStack(height=0):
                    ui.Spacer(width=40)
                    self._checkpoint_comment_frame = ui.Frame()
                    with self._checkpoint_comment_frame:
                        with ui.VStack(height=0, spacing=5):
                            ui.Label("Checkpoint Description")
                            with ui.ZStack():
                                self.description_field = ui.StringField(multiline=True, height=80)
                                self.description_field_hint_label = ui.Label(
                                    " Description", alignment=ui.Alignment.LEFT_TOP, style={"color": 0xFF3F3F3F}
                                )
                                self._description_begin_edit_sub = self.description_field.model.subscribe_begin_edit_fn(
                                    self._on_description_begin_edit
                                )
                                self._description_end_edit_sub = self.description_field.model.subscribe_end_edit_fn(
                                    self._on_description_end_edit
                                )
                    ui.Spacer(width=40)

                ui.Spacer(width=0, height=10)
                with ui.HStack(height=0):
                    ui.Spacer()
                    self._error_label = ui.Label(
                        "", alignment=ui.Alignment.CENTER, word_wrap=True, width=self._window.width - 80, style={"color": 0xFF0000CC}
                    )
                    ui.Spacer()

                ui.Spacer(width=0, height=10)
                with ui.HStack(height=0):
                    ui.Spacer(height=0)
                    ok_button = ui.Button("CONTINUE", name="confirm_button", width=120, height=0)
                    ok_button.set_clicked_fn(self._on_ok_button_fn)
                    cancel_button = ui.Button("CANCEL", name="cancel_button", width=120, height=0)
                    cancel_button.set_clicked_fn(self._on_cancel_button_fn)
                    self._buttons.append(ok_button)
                    self._buttons.append(cancel_button)
                    ui.Spacer(height=0)
                ui.Spacer(width=0, height=10)
