# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["JoinWithSessionLinkWindow"]

import asyncio
from typing import Callable

import carb
import omni.kit.app
import omni.kit.clipboard
import omni.ui as ui

from .layer_icons import LayerIcons


class JoinWithSessionLinkWindow:

    def __init__(self, on_ok_button_cb: Callable[[str], None]) -> None:
        """
        Args:
            on_ok_button_cb (Callable): callback function called when user presses Ok or Enter
                callback passed in a `str` to the session link
        """
        self._window = None
        self._on_ok_button_cb = on_ok_button_cb
        self._buttons = []
        self._session_link_input_field = None
        self._session_link_input_hint = None
        self._error_label = None
        self._session_link_begin_edit_cb = None
        self._session_link_end_edit_cb = None
        self._session_link_edit_cb = None

        self._key_functions = {
            int(carb.input.KeyboardInput.ENTER): self._on_ok_button_fn,
            int(carb.input.KeyboardInput.ESCAPE): self._on_cancel_button_fn
        }

        self._build_ui()

    def destroy(self):
        self._layers_interface = None
        for button in self._buttons:
            button.set_clicked_fn(None)
        self._buttons.clear()
        if self._window:
            self._window.visible = False
        self._window = None

        self._session_link_input_hint = None
        self._session_link_input_field = None
        self._session_link_begin_edit_cb = None
        self._session_link_end_edit_cb = None
        self._session_link_edit_cb = None
        self._error_label = None

    @property
    def visible(self):
        return self._window and self._window.visible

    @visible.setter
    def visible(self, value):
        if self._window:
            self._window.visible = value
            if value:
                asyncio.ensure_future(self.focus_field())

    async def focus_field(self):
        await omni.kit.app.get_app().next_update_async()
        if self._session_link_input_field:
            self._session_link_input_field.focus_keyboard()

    @property
    def current_session_link(self):
        if self._session_link_input_field:
            return self._session_link_input_field.model.get_value_as_string()

        return ""

    @current_session_link.setter
    def current_session_link(self, value):
        if self._session_link_input_field:
            self._session_link_input_field.model.set_value(value)

    def _validate_session_link(self, str):
        # omni.usd.libs are optional to this extension, import Usd here
        from pxr import Usd
        return str and Usd.Stage.IsSupportedFile(str)

    def _on_cancel_button_fn(self):
        self.visible = False

    def _on_key_pressed_fn(self, key, mod, pressed):
        if not pressed:
            return

        func = self._key_functions.get(key)
        if func:
            func()

    def _update_button_status(self):
        if not self._session_link_input_field:
            return False

        session_link = self._session_link_input_field.model.get_value_as_string()
        session_link = session_link.strip()
        join_button = self._buttons[0]
        if not self._validate_session_link(session_link):
            if session_link:
                self._error_label.text = "The link is not supported for USD."
            else:
                self._error_label.text = ""
            join_button.enabled = False
        else:
            self._error_label.text = ""
            join_button.enabled = True

        if not session_link:
            self._session_link_input_hint.visible = True
        else:
            self._session_link_input_hint.visible = False

        return join_button.enabled

    def _on_session_link_begin_edit(self, model):
        self._update_button_status()

    def _on_session_link_end_edit(self, model):
        self._update_button_status()

    def _on_session_link_edit(self, model):
        self._update_button_status()

    def _on_paste_link_fn(self):
        link = omni.kit.clipboard.paste()
        if link:
            self._session_link_input_field.model.set_value(link)

    def _on_ok_button_fn(self):
        if not self._update_button_status():
            return

        self._error_label.text = ""
        self.visible = False

        session_link = self._session_link_input_field.model.get_value_as_string()
        session_link = session_link.strip()

        if self._on_ok_button_cb:
            self._on_ok_button_cb(session_link)

    def _build_ui(self):
        """Construct the window based on the current parameters"""
        self._window = ui.Window(
            "JOIN LIVE SESSION WITH LINK", visible=False, width=500, height=0,
            auto_resize=True, dockPreference=ui.DockPreference.DISABLED
        )
        self._window.flags = (
            ui.WINDOW_FLAGS_NO_COLLAPSE | ui.WINDOW_FLAGS_NO_SCROLLBAR |
            ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_MOVE
        )
        self._window.set_key_pressed_fn(self._on_key_pressed_fn)
        self._window.flags = self._window.flags | ui.WINDOW_FLAGS_MODAL

        STYLES = {
            "Rectangle::hovering": {"background_color": 0x0, "border_radius": 2, "margin": 0, "padding": 0},
            "Rectangle::hovering:hovered": {"background_color": 0xFF9E9E9E},
            "Button.Image::paste_button": {"image_url": LayerIcons().get("paste"), "color": 0xFFD0D0D0},
            "Button::paste_button": {"background_color": 0x0, "margin": 0},
            "Button::paste_button:checked": {"background_color": 0x0},
            "Button::paste_button:hovered": {"background_color": 0x0},
            "Button::paste_button:pressed": {"background_color": 0x0},
        }

        with self._window.frame:
            with ui.VStack(height=0, style=STYLES):
                ui.Spacer(width=0, height=10)
                with ui.HStack(height=0):
                    ui.Spacer(width=20)
                    self._error_label = ui.Label("", name="error_label", style={"color": 0xFF0000CC}, alignment=ui.Alignment.LEFT, word_wrap=True)
                    ui.Spacer(width=20)
                ui.Spacer(width=0, height=5)
                with ui.ZStack(height=0):
                    with ui.HStack(height=0):
                        ui.Spacer(width=20)
                        with ui.ZStack(width=20, height=20):
                            ui.Rectangle(name="hovering")
                            paste_link_button = ui.ToolButton(name="paste_button", image_width=20, image_height=20)
                            paste_link_button.set_clicked_fn(self._on_paste_link_fn)
                        ui.Spacer(width=4)
                        with ui.VStack():
                            ui.Spacer()
                            with ui.ZStack(height=0):
                                self._session_link_input_field = ui.StringField(
                                    name="new_session_link_field", width=self._window.width - 40, height=0
                                )
                                self._session_link_input_hint = ui.Label(
                                    "   Paste Live Session Link Here", alignment=ui.Alignment.LEFT_CENTER,
                                    style={"color": 0xFF3F3F3F}
                                )
                                self._session_link_begin_edit_cb = self._session_link_input_field.model.subscribe_begin_edit_fn(
                                    self._on_session_link_begin_edit
                                )
                                self._session_link_end_edit_cb = self._session_link_input_field.model.subscribe_end_edit_fn(
                                    self._on_session_link_end_edit
                                )
                                self._session_link_edit_cb = self._session_link_input_field.model.subscribe_value_changed_fn(
                                    self._on_session_link_edit
                                )
                            ui.Spacer()
                        ui.Spacer(width=20)
                ui.Spacer(width=0, height=30)
                with ui.HStack(height=0):
                    ui.Spacer(height=0)
                    ok_button = ui.Button("JOIN", name="confirm_button", width=120, height=0)
                    ok_button.set_clicked_fn(self._on_ok_button_fn)
                    cancel_button = ui.Button("CANCEL", name="cancel_button", width=120, height=0)
                    cancel_button.set_clicked_fn(self._on_cancel_button_fn)
                    self._buttons.append(ok_button)
                    self._buttons.append(cancel_button)
                    ui.Spacer(height=0, width=20)
                ui.Spacer(width=0, height=20)

                # 0 for ok button, 0 for cancel button and appends paste link button at last
                self._buttons.append(paste_link_button)

        self._update_button_status()
