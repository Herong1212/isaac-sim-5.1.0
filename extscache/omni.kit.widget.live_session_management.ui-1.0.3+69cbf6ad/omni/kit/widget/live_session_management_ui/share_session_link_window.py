# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["ShareSessionLinkWindow"]

import carb
import omni.ui as ui
import omni.kit.clipboard

from .layer_icons import LayerIcons


class ShareSessionLinkWindow:
    """
    ShareSessionLinkWindow serves for providing UX to select and copy Live Session link so that it
    can be easily shared to other users.
    """

    def __init__(self, session_model):
        self._window = None
        self._buttons = []
        self._existing_sessions_combo = None
        self._existing_sessions_model = session_model

        self._key_functions = {
            int(carb.input.KeyboardInput.ENTER): self._on_ok_button_fn,
            int(carb.input.KeyboardInput.ESCAPE): self._on_cancel_button_fn
        }

        self._build_ui()
        self._existing_sessions_model.set_model_reset_callback(self._on_sessions_model_reset)

    def destroy(self):
        for button in self._buttons:
            button.set_clicked_fn(None)
        self._buttons.clear()
        if self._window:
            self._window.visible = False
        self._window = None
        if self._existing_sessions_model:
            self._existing_sessions_model.set_model_reset_callback(None)
            self._existing_sessions_model.destroy()
            self._existing_sessions_model = None

        self._existing_sessions_combo = None
        self._existing_sessions_empty_hint = None
        self._error_label = None

    def _on_sessions_model_reset(self):
        self._update_dialog_states()

    @property
    def visible(self):
        return self._window and self._window.visible

    @visible.setter
    def visible(self, value):
        if self._window:
            self._window.visible = value

        if not self._window.visible:
            self._existing_sessions_model.stop_channel()

    def _on_ok_button_fn(self):
        current_session = self._existing_sessions_model.current_session
        if not current_session or self._existing_sessions_model.empty():
            self._error_label.text = "No Valid Session Selected."
            return

        omni.kit.clipboard.copy(current_session.shared_link)
        self._error_label.text = ""
        self.visible = False

    def _on_cancel_button_fn(self):
        self.visible = False

    def _on_key_pressed_fn(self, key, mod, pressed):
        if not pressed:
            return

        func = self._key_functions.get(key)
        if func:
            func()

    def _update_dialog_states(self):
        if self._existing_sessions_model.empty():
            self._existing_sessions_empty_hint.visible = True
        else:
            self._existing_sessions_empty_hint.visible = False
            self._error_label.text = ""

    def _build_ui(self):
        """Construct the window based on the current parameters"""
        self._window = ui.Window(
            "SHARE LIVE SESSION LINK", visible=False, height=0,
            auto_resize=True, dockPreference=ui.DockPreference.DISABLED
        )
        self._window.flags = (
            ui.WINDOW_FLAGS_NO_COLLAPSE | ui.WINDOW_FLAGS_NO_SCROLLBAR |
            ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_MOVE
        )
        self._window.set_key_pressed_fn(self._on_key_pressed_fn)
        self._window.flags = self._window.flags | ui.WINDOW_FLAGS_MODAL

        self._existing_sessions_model.refresh_sessions(True)

        STYLES = {
            "Button.Image::confirm_button": {
                "image_url": LayerIcons.get("link"), "alignment" : ui.Alignment.RIGHT_CENTER
            },
            "Label::copy_link": {"font_size": 14},
            "Rectangle::hovering": {"border_radius": 2, "margin": 0, "padding": 0},
            "Rectangle::hovering:hovered": {"background_color": 0xCC9E9E9E},
        }

        with self._window.frame:
            with ui.VStack(height=0, style=STYLES):
                ui.Spacer(width=0, height=10)
                with ui.HStack(height=0):
                    ui.Spacer(width=20)
                    self._error_label = ui.Label(
                        "", name="error_label", style={"color": 0xFF0000CC},
                        alignment=ui.Alignment.LEFT, word_wrap=True
                    )
                    ui.Spacer(width=20)
                ui.Spacer(width=0, height=5)
                with ui.HStack(height=0):
                    ui.Spacer(width=20)
                    with ui.ZStack(height=0):
                        self._existing_sessions_combo = ui.ComboBox(
                            self._existing_sessions_model, width=self._window.width - 40, height=0
                        )
                        self._existing_sessions_empty_hint = ui.Label(
                            " No Existing Sessions", alignment=ui.Alignment.LEFT_CENTER, style={"color": 0xFF3F3F3F}
                        )
                    ui.Spacer(width=20)
                ui.Spacer(width=0, height=30)
                with ui.HStack(height=0):
                    ui.Spacer()
                    with ui.ZStack(width=120, height=30):
                        ui.Rectangle(name="hovering")
                        with ui.HStack():
                            ui.Spacer()
                            ui.Label("Copy Link", width=0, name="copy_link")
                            ui.Spacer(width=8)
                            ui.Image(LayerIcons.get("link"), width=20)
                            ui.Spacer()
                        ok_button = ui.InvisibleButton(name="confirm_button")
                        ok_button.set_clicked_fn(self._on_ok_button_fn)
                        self._buttons.append(ok_button)
                    ui.Spacer()
                ui.Spacer(width=0, height=20)

        self._update_dialog_states()
