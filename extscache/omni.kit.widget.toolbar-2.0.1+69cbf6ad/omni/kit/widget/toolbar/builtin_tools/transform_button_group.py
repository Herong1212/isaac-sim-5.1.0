# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from typing import Optional

__all__ = ["TransformButtonGroup"]

import carb.dictionary
import carb.input
import carb.settings
import omni.ui as ui
from carb.input import KeyboardInput as Key
from omni.kit.widget.options_menu import OptionsMenu, OptionsModel, OptionRadios

from ..hotkey import Hotkey
from ..widget_group import WidgetGroup
from .models.transform_mode_model import LocalGlobalTransformModeModel, TransformModeModel

MOVE_TOOL_NAME = "Move"
ROTATE_TOOL_NAME = "Rotate"
SCALE_TOOL_NAME = "Scale"


class TransformButtonGroup(WidgetGroup):
    TRANSFORM_MOVE_MODE_SETTING = "/app/transform/moveMode"
    TRANSFORM_ROTATE_MODE_SETTING = "/app/transform/rotateMode"

    def __init__(self):
        super().__init__()
        self._input = carb.input.acquire_input_interface()
        self._settings = carb.settings.get_settings()
        self._settings.set_default_string(TransformModeModel.TRANSFORM_OP_SETTING, TransformModeModel.TRANSFORM_OP_MOVE)
        self._settings.set_default_string(
            self.TRANSFORM_MOVE_MODE_SETTING, LocalGlobalTransformModeModel.TRANSFORM_MODE_GLOBAL
        )
        self._settings.set_default_string(
            self.TRANSFORM_ROTATE_MODE_SETTING, LocalGlobalTransformModeModel.TRANSFORM_MODE_GLOBAL
        )

        self._move_op_model = LocalGlobalTransformModeModel(
            op=TransformModeModel.TRANSFORM_OP_MOVE, op_space_setting_path=self.TRANSFORM_MOVE_MODE_SETTING
        )
        self._rotate_op_model = LocalGlobalTransformModeModel(
            op=TransformModeModel.TRANSFORM_OP_ROTATE, op_space_setting_path=self.TRANSFORM_ROTATE_MODE_SETTING
        )
        self._scale_op_model = TransformModeModel(TransformModeModel.TRANSFORM_OP_SCALE)

        def on_hotkey_changed(hotkey: str, button, tool_name: str):
            button.tooltip = f"{tool_name} ({hotkey})"

        self._move_hotkey = Hotkey(
            "toolbar::move",
            Key.W,
            lambda: self._move_op_model.set_value(not self._move_op_model.get_value_as_bool()),
            lambda: self._move_button.enabled
            and self._is_in_context()
            and self._input.get_mouse_value(None, carb.input.MouseInput.RIGHT_BUTTON)
            == 0,  # when RMB is down, it's possible viewport WASD navigation is going on, and don't trigger it if W is pressed
            on_hotkey_changed_fn=lambda hotkey: on_hotkey_changed(hotkey, self._move_button, MOVE_TOOL_NAME),
        )
        self._rotate_hotkey = Hotkey(
            "toolbar::rotate",
            Key.E,
            lambda: self._rotate_op_model.set_value(not self._rotate_op_model.get_value_as_bool()),
            lambda: self._rotate_button.enabled and self._is_in_context()
            and self._input.get_mouse_value(None, carb.input.MouseInput.RIGHT_BUTTON)
            == 0,
            on_hotkey_changed_fn=lambda hotkey: on_hotkey_changed(hotkey, self._rotate_button, ROTATE_TOOL_NAME),
        )
        self._scale_hotkey = Hotkey(
            "toolbar::scale",
            Key.R,
            lambda: self._scale_op_model.set_value(True),
            lambda: self._scale_button.enabled and self._is_in_context(),
            on_hotkey_changed_fn=lambda hotkey: on_hotkey_changed(hotkey, self._scale_button, SCALE_TOOL_NAME),
        )

        self._move_options_model: Optional[OptionsModel] = None
        self._move_options_menu: Optional[OptionsMenu] = None
        self._rotate_options_model: Optional[OptionsModel] = None
        self._rotate_options_menu: Optional[OptionsMenu] = None
        self._custom_move_types = []

    def get_style(self):
        style = {
            "Button.Image::move_op_global": {"image_url": "${glyphs}/toolbar_move_global.svg"},
            "Button.Image::move_op_local": {"image_url": "${glyphs}/toolbar_move_local.svg"},
            "Button.Image::rotate_op_global": {"image_url": "${glyphs}/toolbar_rotate_global.svg"},
            "Button.Image::rotate_op_local": {"image_url": "${glyphs}/toolbar_rotate_local.svg"},
            "Button.Image::scale_op": {"image_url": "${glyphs}/toolbar_scale.svg"},
        }
        return style

    def create(self, default_size):
        self._sub_move, self._move_button = self._create_local_global_button(
            self._move_op_model,
            f"{MOVE_TOOL_NAME} ({self._move_hotkey.get_as_string('W')})",
            "move_op",
            self.TRANSFORM_MOVE_MODE_SETTING,
            "move_op_global",
            "move_op_local",
            default_size,
        )
        self._sub_rotate, self._rotate_button = self._create_local_global_button(
            self._rotate_op_model,
            f"{ROTATE_TOOL_NAME} ({self._rotate_hotkey.get_as_string('E')})",
            "rotate_op",
            self.TRANSFORM_ROTATE_MODE_SETTING,
            "rotate_op_global",
            "rotate_op_local",
            default_size,
        )
        self._scale_button = ui.ToolButton(
            model=self._scale_op_model,
            name="scale_op",
            tooltip=f"{SCALE_TOOL_NAME} ({self._scale_hotkey.get_as_string('R')})",
            width=default_size,
            height=default_size,
            mouse_pressed_fn=lambda *_: self._acquire_toolbar_context(),
        )

        return {"move_op": self._move_button, "rotate_op": self._rotate_button, "scale_op": self._scale_button}

    def clean(self):
        super().clean()
        self._move_button = None
        self._rotate_button = None
        self._scale_button = None
        self._sub_move = None
        self._sub_rotate = None
        self._move_op_model.clean()
        self._move_op_model = None
        self._rotate_op_model.clean()
        self._rotate_op_model = None
        self._scale_op_model.clean()
        self._scale_op_model = None
        self._move_hotkey.clean()
        self._move_hotkey = None
        self._rotate_hotkey.clean()
        self._rotate_hotkey = None
        self._scale_hotkey.clean()
        self._scale_hotkey = None

        if self._move_options_model:
            self._move_options_model.destroy()
            self._move_options_model = None
        if self._move_options_menu:
            self._move_options_menu.destroy()
            self._move_options_menu = None
        if self._rotate_options_model:
            self._rotate_options_model.destroy()
            self._rotate_options_model = None
        if self._rotate_options_menu:
            self._rotate_options_menu.destroy()
            self._rotate_options_menu = None

    def _get_op_button_name(self, model, global_name, local_name):
        if model.as_string == LocalGlobalTransformModeModel.TRANSFORM_MODE_GLOBAL:
            return global_name
        else:
            return local_name

    def _create_local_global_button(
        self, op_model, tooltip, button_name, op_setting_path, global_name, local_name, default_size
    ):

        op_button = ui.ToolButton(
            name=self._get_op_button_name(op_model, global_name, local_name),
            model=op_model,
            tooltip=tooltip,
            width=default_size,
            height=default_size,
            mouse_pressed_fn=lambda x, y, b, _: self._on_mouse_pressed(b, button_name),
            mouse_released_fn=lambda x, y, b, _: self._on_mouse_released(b),
            checked=op_model.get_value_as_bool(),
        )

        def on_op_button_value_change(model):
            op_button.name = self._get_op_button_name(model, global_name, local_name)

        return op_model.subscribe_value_changed_fn(on_op_button_value_change), op_button
    
    def _build_move_options_model(self):
        radios = [
                ("Global (W)", LocalGlobalTransformModeModel.TRANSFORM_MODE_GLOBAL),
                ("Local (W)", LocalGlobalTransformModeModel.TRANSFORM_MODE_LOCAL),
        ]
        if self._custom_move_types:
            for name, type in self._custom_move_types:
                radios.append((name, type))
        items = [
            OptionRadios(radios, setting_path=self.TRANSFORM_MOVE_MODE_SETTING, default=LocalGlobalTransformModeModel.TRANSFORM_MODE_GLOBAL),
        ]

        if self._move_options_model is None:
            self._move_options_model = OptionsModel("Move Mode", items)
        else:
            self._move_options_model.rebuild_items(items)
    
        
    def _build_options_menu(self):
        self._build_move_options_model()
        if self._move_options_menu is None:
            self._move_options_menu = OptionsMenu(self._move_options_model)

        if self._rotate_options_model is None:
            radios = [
                ("Global (E)", LocalGlobalTransformModeModel.TRANSFORM_MODE_GLOBAL),
                ("Local (E)", LocalGlobalTransformModeModel.TRANSFORM_MODE_LOCAL),
            ]
            items = [
                OptionRadios(radios, setting_path=self.TRANSFORM_ROTATE_MODE_SETTING, default=LocalGlobalTransformModeModel.TRANSFORM_MODE_GLOBAL),
            ]
        
            self._rotate_options_model = OptionsModel("Rotate Mode", items)
        if self._rotate_options_menu is None:
            self._rotate_options_menu = OptionsMenu(self._rotate_options_model)

    def _invoke_context_menu(self, button_id: str, min_menu_entries: int = 1):
        """
        Function to invoke context menu.

        Args:
            button_id: button_id of the context menu to be invoked.
            min_menu_entries: minimal number of menu entries required for menu to be visible (default 1).
        """
        self._build_options_menu()
        if button_id == "move_op":
            self._move_options_menu.show_by_widget(self._move_button, alignment=ui.Alignment.RIGHT_TOP)
        elif button_id == "rotate_op":
            self._rotate_options_menu.show_by_widget(self._rotate_button, alignment=ui.Alignment.RIGHT_TOP)

    def add_custom_move_type(self, entry_name: str, move_type: str):
        self._custom_move_types.append((entry_name, move_type))
        if self._move_options_model:
            self._build_move_options_model()

    def remove_custom_move_type(self, entry_name: str):
        for index, entry in enumerate(self._custom_move_types):
            if entry[0] == entry_name:
                del self._custom_move_types[index]
                if self._move_options_model:
                    self._build_move_options_model()
                return
