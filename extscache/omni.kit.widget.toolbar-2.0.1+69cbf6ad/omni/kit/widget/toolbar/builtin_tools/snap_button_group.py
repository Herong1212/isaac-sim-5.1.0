# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from typing import Optional

__all__ = ["LegacySnapButtonGroup"]

import carb.dictionary
import carb.settings
import omni.kit.context_menu
import omni.ui as ui
from omni.kit.widget.options_menu import OptionCustom, OptionRadios, OptionSeparator, OptionsModel, OptionsMenu

from ..widget_group import WidgetGroup
from .models.setting_model import BoolSettingModel, FloatSettingModel
from .models.snap_mode_model import SnapModeModel


class LegacySnapButtonGroup(WidgetGroup):
    SNAP_ENABLED_SETTING = "/app/viewport/snapEnabled"
    SNAP_MOVE_X_SETTING = "/persistent/app/viewport/stepMove/x"
    SNAP_MOVE_Y_SETTING = "/persistent/app/viewport/stepMove/y"
    SNAP_MOVE_Z_SETTING = "/persistent/app/viewport/stepMove/z"
    SNAP_ROTATE_SETTING = "/persistent/app/viewport/stepRotate"
    SNAP_SCALE_SETTING = "/persistent/app/viewport/stepScale"
    SNAP_TO_SURFACE_SETTING = "/persistent/app/viewport/snapToSurface"

    def __init__(self):
        super().__init__()
        self._settings = carb.settings.get_settings()
        self._settings.set_default_bool(self.SNAP_ENABLED_SETTING, False)
        self._settings.set_default_float(self.SNAP_MOVE_X_SETTING, 50.0)
        self._settings.set_default_float(self.SNAP_MOVE_Y_SETTING, 50.0)
        self._settings.set_default_float(self.SNAP_MOVE_Z_SETTING, 50.0)
        self._settings.set_default_float(self.SNAP_ROTATE_SETTING, 1.0)
        self._settings.set_default_float(self.SNAP_SCALE_SETTING, 1.0)

        self._dict = carb.dictionary.get_dictionary()
        self._snap_setting_model = BoolSettingModel(self.SNAP_ENABLED_SETTING, False)
        self._snap_move_x_settings_model = FloatSettingModel(self.SNAP_MOVE_X_SETTING)
        self._snap_move_y_settings_model = FloatSettingModel(self.SNAP_MOVE_Y_SETTING)
        self._snap_move_z_settings_model = FloatSettingModel(self.SNAP_MOVE_Z_SETTING)
        self._snap_rotate_settings_model = FloatSettingModel(self.SNAP_ROTATE_SETTING)
        self._snap_scale_settings_model = FloatSettingModel(self.SNAP_SCALE_SETTING)

        self._create_snap_increment_setting_window()
        self._snap_mode_model: Optional[SnapModeModel] = None
        self._options_model: Optional[OptionsModel] = None
        self._options_menu: Optional[OptionsMenu] = None
        self._show_menu_task = None

        self._button = None

    def clean(self):
        super().clean()
        self._snap_setting_model.clean()
        self._snap_setting_model = None
        # workaround delayed toolbar rebuild after group is destroyed and access null model
        if self._button:
            self._button.model = ui.SimpleBoolModel()
            self._button = None
        self._snap_move_x_settings_model.clean()
        self._snap_move_x_settings_model = None
        self._snap_move_y_settings_model.clean()
        self._snap_move_y_settings_model = None
        self._snap_move_z_settings_model.clean()
        self._snap_move_z_settings_model = None
        self._snap_rotate_settings_model.clean()
        self._snap_rotate_settings_model = None
        self._snap_scale_settings_model.clean()
        self._snap_scale_settings_model = None
        self._snap_increment_setting_window = None
        self._snap_setting_menu = None
        self._snap_settings = None
        self._snap_to_increment_menu = None
        self._snap_to_face_menu = None
        if self._show_menu_task:
            self._show_menu_task.cancel()
        self._show_menu_task = None

        if self._options_model:
            self._options_model.destroy()
            self._options_model = None
        if self._options_menu:
            self._options_menu.destroy()
            self._options_menu = None
        if self._snap_mode_model:
            self._snap_mode_model.clean()
            self._snap_mode_model = None

    def get_style(self):
        style = {"Button.Image::snap": {"image_url": "${glyphs}/toolbar_snap.svg"}}
        return style

    def create(self, default_size):
        self._button = ui.ToolButton(
            model=self._snap_setting_model,
            name="snap",
            tooltip="Snap",
            width=default_size,
            height=default_size,
            mouse_pressed_fn=lambda x, y, b, _: self._on_mouse_pressed(b, "snap"),
            mouse_released_fn=lambda x, y, b, _: self._on_mouse_released(b),
            checked=self._snap_setting_model.get_value_as_bool(),
        )
        return {"snap": self._button}

    def _on_snap_on_off(self, model):
        self._snap_settings.enabled = self._snap_setting_model.get_value_as_bool()

    def _on_snap_setting_change(self, item, event_type):
        snap_to_face = self._dict.get(item)
        self._snap_to_increment_menu.checked = not snap_to_face
        self._snap_to_face_menu.checked = snap_to_face
        self._snap_settings.enabled = not snap_to_face

    def _on_snap_setting_menu_clicked(self, snap_to_face):
        self._settings.set(self.SNAP_TO_SURFACE_SETTING, snap_to_face)

    def _on_show_snap_increment_setting_window(self):
        self._snap_increment_setting_window.visible = True

    def _create_snap_increment_setting_window(self):
        self._snap_increment_setting_window = ui.Window(
            "Snap Increment Settings Menu",
            width=400,
            height=0,
            flags=ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_SCROLLBAR,
            visible=False,
        )
        with self._snap_increment_setting_window.frame:
            with ui.VStack(spacing=8, height=0, name="frame_v_stack"):
                ui.Label("Snap Settings - Increments", enabled=False)
                ui.Separator()
                with ui.HStack():
                    with ui.HStack(width=120):
                        ui.Label("Position", width=50)
                        ui.Spacer()
                    all_axis = ["X", "Y", "Z"]
                    all_axis_model = {
                        "X": self._snap_move_x_settings_model,
                        "Y": self._snap_move_y_settings_model,
                        "Z": self._snap_move_z_settings_model,
                    }
                    colors = {"X": 0xFF5555AA, "Y": 0xFF76A371, "Z": 0xFFA07D4F}
                    for axis in all_axis:
                        with ui.HStack():
                            with ui.ZStack(width=15):
                                ui.Rectangle(
                                    width=15,
                                    height=20,
                                    style={
                                        "background_color": colors[axis],
                                        "border_radius": 3,
                                        "corner_flag": ui.CornerFlag.LEFT,
                                    },
                                )
                                ui.Label(axis, alignment=ui.Alignment.CENTER)
                            ui.FloatDrag(model=all_axis_model[axis], min=0, max=1000000, step=0.01)
                            ui.Circle(width=20, radius=3.5, size_policy=ui.CircleSizePolicy.FIXED)
                with ui.HStack():
                    with ui.HStack(width=120):
                        ui.Label("Rotation", width=50)
                        ui.Spacer()
                    ui.FloatDrag(model=self._snap_rotate_settings_model, min=0, max=1000000, step=0.01)
                with ui.HStack():
                    with ui.HStack(width=120):
                        ui.Label("Scale", width=50)
                        ui.Spacer()
                    ui.FloatDrag(model=self._snap_scale_settings_model, min=0, max=1000000, step=0.01)

    def _invoke_context_menu(self, button_id: str, min_menu_entries: int = 1):
        """
        Function to invoke context menu.

        Args:
            button_id: button_id of the context menu to be invoked.
            min_menu_entries: minimal number of menu entries required for menu to be visible (default 1).
        """
        self._build_options_menu()
        self._options_menu.show_by_widget(self._button, alignment=ui.Alignment.RIGHT_TOP)
    
    def _build_options_menu(self):
        if self._snap_mode_model is None:
            self._snap_mode_model = SnapModeModel()
        if self._options_model is None:
            radios = [
                "Snap to Increment",
                "Snap to Face",
            ]
            
            def build_setting_menu():
                self._snap_setting_menu = ui.MenuItem(
                    f"Snap Settings {ui.get_custom_glyph_code('${glyphs}/cog.svg')}",
                    triggered_fn=self._on_show_snap_increment_setting_window,
                    enabled=not self._snap_mode_model.as_bool,
                )

            items = [
                OptionCustom(build_fn=build_setting_menu),
                OptionRadios(radios, model=self._snap_mode_model, default=self._snap_mode_model.SNAP_MODE_INCREMENT),
            ]
    
            def on_snap_mode_changed(model):
                self._snap_setting_menu.enabled = not model.as_bool

            self._snap_mode_sub = self._snap_mode_model.subscribe_value_changed_fn(on_snap_mode_changed)
            self._options_model = OptionsModel("Snap", items)
        if self._options_menu is None:
            self._options_menu = OptionsMenu(self._options_model)
