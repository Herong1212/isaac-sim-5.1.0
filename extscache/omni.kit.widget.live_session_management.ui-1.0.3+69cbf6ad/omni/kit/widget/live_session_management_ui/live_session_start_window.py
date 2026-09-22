# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["LiveSessionStartWindow"]

import asyncio
import re
from typing import Callable

import carb
import omni.ui as ui
import omni.kit.app

from .layer_icons import LayerIcons
from .live_session import LiveSessionInterface
from .live_session_model import LiveSessionComboBoxModel


class LiveSessionStartWindow:
    def __init__(self, session_model: LiveSessionComboBoxModel,
                 prim_path: str,
                 join_session_cb: Callable[[LiveSessionInterface, str, str], bool],
                 create_live_session_cb: Callable[[str, str], LiveSessionInterface]):
        self._window = None
        self._live_prim_path = prim_path
        self._join_session_cb = join_session_cb
        self._create_live_session_cb = create_live_session_cb
        self._buttons = []
        self._existing_sessions_combo = None
        self._session_name_input_field = None
        self._session_name_input_hint = None
        self._error_label = None
        self._error_icon = None
        self._session_name_begin_edit_cb = None
        self._session_name_end_edit_cb = None
        self._session_name_edit_cb = None
        self._existing_sessions_model = session_model
        self._participants_list = None
        self._participants_layout = None
        self._existing_sessions_model.set_user_update_callback(self._on_channel_users_update)
        self._existing_sessions_model.add_value_changed(self._on_session_list_changed)
        self._update_user_list_task: asyncio.Future = None
        self._join_create_radios = None

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
        self._participants_list = None
        if self._window:
            self._window.visible = False
        self._window = None
        if self._existing_sessions_model:
            self._existing_sessions_model.set_user_update_callback(None)
            self._existing_sessions_model.set_model_reset_callback(None)
            self._existing_sessions_model.destroy()
            self._existing_sessions_model = None

        self._participants_layout = None
        self._layers_event_subscription = None
        self._existing_sessions_combo = None
        self._existing_sessions_empty_hint = None
        self._join_create_radios = None
        self._session_name_input_hint = None
        self._session_name_input_field = None
        self._session_name_begin_edit_cb = None
        self._session_name_end_edit_cb = None
        self._session_name_edit_cb = None
        self._error_label = None
        self._error_icon = None
        if self._update_user_list_task:
            try:
                self._update_user_list_task.cancel()
            except Exception:
                pass
        self._update_user_list_task = None

    def _on_sessions_model_reset(self):
        self._update_dialog_states(refresh_model=False)

    @property
    def visible(self):
        return self._window and self._window.visible

    @visible.setter
    def visible(self, value):
        if self._window:
            self._window.visible = value

        if not self._window.visible:
            if self._update_user_list_task:
                try:
                    self._update_user_list_task.cancel()
                except Exception:
                    pass
            self._update_user_list_task = None
            self._existing_sessions_model.stop_channel()

    def select_default_session(self):
        if self._existing_sessions_model:
            self._existing_sessions_model.select_default_session()

    def set_focus(self, join_session):
        if not self._join_create_radios:
            return

        if join_session:
            self._join_create_radios.model.set_value(0)
        else:
            self._join_create_radios.model.set_value(1)

            async def async_focus_keyboard():
                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()
                self._session_name_input_field.focus_keyboard()

            omni.kit.async_engine.run_coroutine(async_focus_keyboard())

    def _on_channel_users_update(self):
        async def _update_users():
            all_users = self._existing_sessions_model.all_users
            current_session = self._existing_sessions_model.current_session
            if not current_session:
                return

            self._participants_list.clear()
            with self._participants_list:
                if len(all_users) > 0:
                    for _, user in all_users.items():
                        is_owner = current_session.owner == user.user_name
                        with ui.VStack(height=0):
                            ui.Spacer(height=5)
                            with ui.HStack(height=0):
                                ui.Spacer(width=10)
                                if is_owner:
                                    ui.Label(f"{user.user_name} - {user.from_app} (owner)", style={"color": 0xFF808080})
                                else:
                                    ui.Label(f"{user.user_name} - {user.from_app}", style={"color": 0xFF808080})
                else:
                    self._build_empty_participants_list()

        if not self._update_user_list_task or self._update_user_list_task.done():
            self._update_user_list_task = asyncio.ensure_future(_update_users())

    def _validate_session_name(self, str):
        if re.match(r'^[a-zA-Z][a-zA-Z0-9-_]*$', str):
            return True

        return False

    def _on_ok_button_fn(self):  # pragma: no cover
        current_option = self._join_create_radios.model.as_int
        join_session = current_option == 0
        if join_session:
            current_session = self._existing_sessions_model.current_session
            if not current_session:
                self._error_label.text = "No Valid Session Selected"
                self._error_label.visible = True
                self._error_icon.visible = True
            elif self._join_session_cb(current_session, self._existing_sessions_model.base_layer_identifier, self._live_prim_path):
                self._error_label.text = ""
                self._error_label.visible = False
                self._error_icon.visible = False
                self.visible = False
            else:
                self._error_label.text = "Failed to join session, please check console for more details."
                self._error_label.visible = True
                self._error_icon.visible = True
        else:
            session_name = self._session_name_input_field.model.get_value_as_string()
            session_name = session_name.strip()
            if not session_name or not self._validate_session_name(session_name):
                self._update_button_status(session_name)
                self._error_label.text = "Session name must be given."
                self._error_label.visible = True
                self._error_icon.visible = True
            else:
                session = self._create_live_session_cb(layer_identifier=self._existing_sessions_model.base_layer_identifier, name=session_name)
                if not session:
                    self._error_label.text = "Failed to create session, please check console for more details."
                    self._error_label.visible = True
                    self._error_icon.visible = True
                elif not self._join_session_cb(session, self._existing_sessions_model.base_layer_identifier, self._live_prim_path):
                    self._error_label.text = "Failed to join session, please check console for more details."
                    self._error_label.visible = True
                    self._error_icon.visible = True
                else:
                    self._error_label.text = ""
                    self._error_label.visible = False
                    self._error_icon.visible = False
                    self.visible = False

    def _on_cancel_button_fn(self):
        self.visible = False

    def _on_key_pressed_fn(self, key, mod, pressed):
        if not pressed:
            return

        func = self._key_functions.get(key)
        if func:
            func()

    def _build_option_checkbox(self, name, text, default_value, tooltip=""): # pragma: no cover
        with ui.HStack(height=0, width=0):
            checkbox = ui.CheckBox(width=20, name=name)
            checkbox.model.set_value(default_value)
            label = ui.Label(text, alignment=ui.Alignment.LEFT)
            if tooltip:
                label.set_tooltip(tooltip)

            return checkbox, label

    def _build_option_radio(self, collection, name, text, tooltip=""):
        style = {
            "": {"background_color": 0x0, "image_url": LayerIcons.get("radio_off")},
            ":checked": {"image_url": LayerIcons.get("radio_on")},
        }

        with ui.HStack(height=0, width=0):
            radio = ui.RadioButton(radio_collection=collection, width=28, height=28, name=name, style=style)
            ui.Spacer(width=4)
            label = ui.Label(text, alignment=ui.Alignment.LEFT_CENTER)
            if tooltip:
                label.set_tooltip(tooltip)

        return radio

    def _update_button_status(self, session_name):
        join_button = self._buttons[0]
        if session_name and not self._validate_session_name(session_name):
            if not str.isalpha(session_name[0]):
                self._error_label.text = "Session name must be prefixed with letters."
            else:
                self._error_label.text = "Only alphanumeric letters, hyphens, or underscores are supported."
            self._error_label.visible = True
            self._error_icon.visible = True
            join_button.enabled = False
        else:
            self._error_label.text = ""
            self._error_label.visible = False
            self._error_icon.visible = False
            join_button.enabled = True

    def _on_session_name_begin_edit(self, model):
        self._session_name_input_hint.visible = False
        session_name = model.get_value_as_string().strip()
        self._update_button_status(session_name)

    def _on_session_name_end_edit(self, model):
        if len(model.get_value_as_string()) == 0:
            self._session_name_input_hint.visible = True

        session_name = model.get_value_as_string().strip()
        self._update_button_status(session_name)

    def _on_session_name_edit(self, model):
        session_name = model.get_value_as_string().strip()
        self._update_button_status(session_name)

    def _update_dialog_states(self, refresh_model=True):
        self._error_label.text = ""
        self._error_label.visible = False
        self._error_icon.visible = False
        current_option = self._join_create_radios.model.as_int
        show_join_session = current_option == 0
        join_button = self._buttons[0]
        if show_join_session:
            self._existing_sessions_combo.visible = True
            self._session_name_input_field.visible = False
            self._session_name_input_hint.visible = False
            self._participants_layout.visible = True
            if refresh_model:
                self._existing_sessions_model.refresh_sessions()
            if self._existing_sessions_model.empty():
                self._existing_sessions_empty_hint.visible = True
            else:
                self._existing_sessions_empty_hint.visible = False
            join_button.text = "JOIN"
        else:
            self._participants_layout.visible = False
            self._existing_sessions_combo.visible = False
            self._session_name_input_field.visible = True
            self._session_name_input_hint.visible = False
            self._existing_sessions_empty_hint.visible = False
            if refresh_model:
                self._existing_sessions_model.clear()
            join_button.text = "CREATE"
            new_session_name = self._existing_sessions_model.create_new_session_name()
            self._session_name_input_field.model.set_value(new_session_name)
            self._session_name_input_field.focus_keyboard()

    def _on_radios_changed_fn(self, model):
        self._update_dialog_states()

        self._on_checkbox_changed_called = False

    def _on_session_list_changed(self, model):
        if self._participants_list:
            self._participants_list.clear()

    def _build_ui(self):
        """Construct the window based on the current parameters"""
        self._window = ui.Window("Live Session", visible=False, height=0, auto_resize=True, dockPreference=ui.DockPreference.DISABLED)
        self._window.flags = (
            ui.WINDOW_FLAGS_NO_COLLAPSE | ui.WINDOW_FLAGS_NO_SCROLLBAR |
            ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_MOVE
        )
        self._window.set_key_pressed_fn(self._on_key_pressed_fn)
        self._window.flags = self._window.flags | ui.WINDOW_FLAGS_MODAL

        self._existing_sessions_model.refresh_sessions()
        empty_sessions = self._existing_sessions_model.empty()

        with self._window.frame:
            with ui.VStack(height=0):
                ui.Spacer(width=0, height=10)
                with ui.HStack(height=0):
                    ui.Spacer()
                    self._join_create_radios = ui.RadioCollection()
                    self._build_option_radio(self._join_create_radios, "join_session_radio_button", "Join Session")
                    ui.Spacer(width=20)
                    self._build_option_radio(self._join_create_radios, "create_session_radio_button", "Create Session")
                    ui.Spacer()
                    self._join_create_radios.model.add_value_changed_fn(lambda _: self._update_dialog_states())
                ui.Spacer(width=0, height=15)
                with ui.HStack(alignment=ui.Alignment.CENTER):
                    ui.Spacer()
                    self._error_icon = ui.Image(LayerIcons.get("warning"), width=14, height=14)
                    self._error_label = ui.Label("", name="error_label", width=0, style={"color": 0xC39D9DCC})
                    ui.Spacer()
                ui.Spacer(width=0, height=5)
                with ui.ZStack(height=0):
                    with ui.HStack(height=0):
                        ui.Spacer(width=20)
                        with ui.ZStack(height=0):
                            self._session_name_input_field = ui.StringField(
                                name="new_session_name_field", width=self._window.width - 40, height=0
                            )
                            self._session_name_input_hint = ui.Label(
                                " New Session Name", alignment=ui.Alignment.LEFT_CENTER, style={"color": 0xFF3F3F3F}
                            )
                            self._session_name_begin_edit_cb = self._session_name_input_field.model.subscribe_begin_edit_fn(
                                self._on_session_name_begin_edit
                            )
                            self._session_name_end_edit_cb = self._session_name_input_field.model.subscribe_end_edit_fn(
                                self._on_session_name_end_edit
                            )
                            self._session_name_edit_cb = self._session_name_input_field.model.subscribe_value_changed_fn(
                                self._on_session_name_edit
                            )
                        ui.Spacer(width=20)
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
                ui.Spacer(width=0, height=10)
                self._participants_layout = ui.VStack(height=0)
                with self._participants_layout:
                    with ui.HStack(height=0):
                        ui.Spacer(width=20)
                        with ui.VStack(height=0, width=0):
                            with ui.HStack(height=0, width=0):
                                ui.Label("Participants:   ", alignment=ui.Alignment.CENTER)
                            with ui.HStack():
                                ui.Spacer()
                                ui.Image(LayerIcons.get("participants"), width=28, height=28)
                                ui.Spacer()
                        ui.Spacer(width=0, height=5)
                        with ui.HStack(height=0):
                            with ui.ScrollingFrame(height=120, style={"background_color": 0xFF24211F}):
                                self._participants_list = ui.VStack(height=0)
                                with self._participants_list:
                                    self._build_empty_participants_list()
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

        if empty_sessions:
            self._join_create_radios.model.set_value(1)
        else:
            self._update_dialog_states()

    def _build_empty_participants_list(self):
        with ui.VStack(height=0):
            ui.Spacer(height=5)
            with ui.HStack(height=0):
                ui.Spacer(width=10)
                ui.Label("No users currently in session.", style={"color": 0xFF808080})
