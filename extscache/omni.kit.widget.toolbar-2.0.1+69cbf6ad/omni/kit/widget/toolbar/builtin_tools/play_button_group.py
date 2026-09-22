# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from typing import Optional

__all__ = ["PlayButtonGroup"]

import carb.dictionary
import carb.settings
import omni.timeline
import omni.ui as ui
from carb.input import KeyboardInput as Key
from omni.kit.commands import execute
from omni.kit.widget.options_menu import OptionCustom, OptionItem, OptionSeparator, OptionsModel, OptionsMenu

from ..hotkey import Hotkey
from ..widget_group import WidgetGroup

from .models.setting_model import BoolSettingModel
from .models.timeline_model import TimelinePlayPauseModel

PLAY_TOOL_NAME = "Play"
PAUSE_TOOL_NAME = "Pause"


class PlayButtonGroup(WidgetGroup):
    PLAY_ANIMATIONS_SETTING = "/app/player/playAnimations"
    PLAY_AUDIO_SETTING = "/app/player/audio/enabled"
    PLAY_SIMULATIONS_SETTING = "/app/player/playSimulations"
    PLAY_COMPUTEGRAPH_SETTING = "/app/player/playComputegraph"

    all_settings_paths = [
        PLAY_ANIMATIONS_SETTING,
        PLAY_AUDIO_SETTING,
        PLAY_SIMULATIONS_SETTING,
        PLAY_COMPUTEGRAPH_SETTING,
    ]

    def __init__(self):
        super().__init__()
        self._play_button = None
        self._play_hotkey = None
        self._stop_button = None
        self._settings = carb.settings.get_settings()
        self._dict = carb.dictionary.get_dictionary()
        self._timeline_play_pause_model = TimelinePlayPauseModel()
        self._timeline = omni.timeline.get_timeline_interface()

        self._settings.set_default_bool(self.PLAY_ANIMATIONS_SETTING, True)
        self._settings.set_default_bool(self.PLAY_AUDIO_SETTING, True)
        self._settings.set_default_bool(self.PLAY_SIMULATIONS_SETTING, True)
        self._settings.set_default_bool(self.PLAY_COMPUTEGRAPH_SETTING, True)

        stream = self._timeline.get_timeline_event_stream()
        self._sub = stream.create_subscription_to_pop(self._on_timeline_event)

        self._play_animation_model: Optional[BoolSettingModel] = None
        self._play_audio_model: Optional[BoolSettingModel] = None
        self._play_simulation_model: Optional[BoolSettingModel] = None
        self._play_compute_graph_model: Optional[BoolSettingModel] = None
        self._options_model: Optional[OptionsModel] = None
        self._options_menu: Optional[OptionsMenu] = None

        self._show_menu_task = None
        self._visible = True

    def clean(self):
        super().clean()
        self._sub = None
        if self._timeline_play_pause_model:
            self._timeline_play_pause_model.clean()
            self._timeline_play_pause_model = None
        self._play_button = None
        self._stop_button = None
        if self._show_menu_task:
            self._show_menu_task.cancel()
        self._show_menu_task = None
        if self._play_hotkey:
            self._play_hotkey.clean()
            self._play_hotkey = None
        self._visible = True

        if self._options_model:
            self._options_model.destroy()
            self._options_model = None
        if self._options_menu:
            self._options_menu.destroy()
            self._options_menu = None
        if self._play_animation_model:
            self._play_animation_model.clean()
            self._play_animation_model = None
        if self._play_audio_model:
            self._play_audio_model.clean()
            self._play_audio_model = None
        if self._play_simulation_model:
            self._play_simulation_model.clean()
            self._play_simulation_model = None
        if self._play_compute_graph_model:
            self._play_compute_graph_model.clean()
            self._play_compute_graph_model = None

    def get_style(self):
        style = {
            "Button.Image::play": {"image_url": "${glyphs}/toolbar_play.svg"},
            "Button.Image::play:checked": {"image_url": "${glyphs}/toolbar_pause.svg"},
            "Button.Image::stop": {"image_url": "${glyphs}/toolbar_stop.svg"},
        }
        return style

    def create(self, default_size):
        # Build Play button
        self._play_button = ui.ToolButton(
            model=self._timeline_play_pause_model,
            name="play",
            tooltip=f"{PLAY_TOOL_NAME} ('Space')",
            width=default_size,
            height=default_size,
            mouse_pressed_fn=lambda x, y, b, _: self._on_mouse_pressed(b, "play"),
            mouse_released_fn=lambda x, y, b, _: self._on_mouse_released(b),
            checked=self._timeline_play_pause_model.get_value_as_bool(),
        )

        def on_play_hotkey_changed(hotkey: str):
            if self._play_button:
                self._play_button.tooltip = f"{PLAY_TOOL_NAME} ({hotkey})"

        # Assign Play button Hotkey
        if self._play_hotkey:
            self._play_hotkey.clean()
        self._play_hotkey = Hotkey(
            "toolbar::play",
            Key.SPACE,
            lambda: self._timeline_play_pause_model.set_value(not self._timeline_play_pause_model.get_value_as_bool()),
            lambda: self._play_button is not None and self._play_button.enabled and self._is_in_context(),
            on_hotkey_changed_fn=lambda hotkey: on_play_hotkey_changed(hotkey),
        )

        self._visible = True

        def on_stop_clicked(*_):
            self._acquire_toolbar_context()
            execute("ToolbarStopButtonClicked")

        self._stop_button = ui.Button(
            name="stop",
            tooltip="Stop",
            width=default_size,
            height=default_size,
            visible=False,
            clicked_fn=on_stop_clicked,
        )

        return {"play": self._play_button, "stop": self._stop_button}

    def _on_setting_changed(self, item, event_type, menu_item):
        menu_item.checked = self._dict.get(item)

    def _on_timeline_event(self, e):
        if e.type == int(omni.timeline.TimelineEventType.PLAY):
            if self._play_button:
                self._play_button.set_tooltip(f"{PAUSE_TOOL_NAME} ({self._play_hotkey.get_as_string('Space')})")
            if self._stop_button:
                self._stop_button.visible = self._visible
        if e.type == int(omni.timeline.TimelineEventType.PAUSE):
            if self._play_button:
                self._play_button.set_tooltip(f"{PLAY_TOOL_NAME} ({self._play_hotkey.get_as_string('Space')})")
        if e.type == int(omni.timeline.TimelineEventType.STOP):
            if self._stop_button:
                self._stop_button.visible = False
            if self._play_button:
                self._play_button.set_tooltip(f"{PLAY_TOOL_NAME} ({self._play_hotkey.get_as_string('Space')})")
        if hasattr(omni.timeline.TimelineEventType, 'DIRECTOR_CHANGED') and\
                e.type == int(omni.timeline.TimelineEventType.DIRECTOR_CHANGED):
            self._visible = not e.payload['hasDirector']
            if self._stop_button:
                self._stop_button.visible = self._visible
            if self._play_button:
                self._play_button.visible = self._visible

    def _select_all(self):
        execute("ToolbarPlayFilterSelectAll", settings=self.all_settings_paths)

    def _invoke_context_menu(self, button_id: str, min_menu_entries: int = 1):
        """
        Function to invoke context menu.

        Args:
            button_id: button_id of the context menu to be invoked.
            min_menu_entries: minimal number of menu entries required for menu to be visible (default 1).
        """
        self._build_options_menu()
        self._options_menu.show_by_widget(self._play_button, alignment=ui.Alignment.RIGHT_TOP)
    
    def _build_options_menu(self):
        if self._options_model is None:
            self._play_animation_model = BoolSettingModel(self.PLAY_ANIMATIONS_SETTING)
            self._play_audio_model = BoolSettingModel(self.PLAY_AUDIO_SETTING)
            self._play_simulation_model = BoolSettingModel(self.PLAY_SIMULATIONS_SETTING)
            self._play_compute_graph_model = BoolSettingModel(self.PLAY_COMPUTEGRAPH_SETTING)

            items = [
                OptionItem("Animation", default=True, model=self._play_animation_model),
                OptionItem("Audio", default=True, model=self._play_audio_model),
                OptionItem("Simulations", default=True, model=self._play_simulation_model),
                OptionItem("OmniGraph", default=True, model=self._play_compute_graph_model),

                OptionSeparator(),
                OptionCustom(build_fn=lambda: ui.MenuItem("Select All", triggered_fn=self._select_all, hide_on_click=False)),
            ]
            self._options_model = OptionsModel("Filter", items)
        if self._options_menu is None:
            self._options_menu = OptionsMenu(self._options_model)
