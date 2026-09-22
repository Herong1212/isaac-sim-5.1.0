# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from omni.kit.widget.options_menu import OptionItem, OptionsMenu, OptionsModel
from omni.ui import Button, HStack, SimpleBoolModel, Spacer, color

from .model import ApplicationModel

__all__ = ["SettingsModel", "SettingsWidget"]


class SettingsModel:
    def __init__(self):
        self.variants_model = SimpleBoolModel(True)
        self.persist_model = SimpleBoolModel(False)

    @property
    def variants(self) -> bool:
        return self.variants_model.as_bool

    @variants.setter
    def variants(self, value: bool) -> None:
        self.variants_model.as_bool = value

    @property
    def persist(self) -> bool:
        return self.persist_model.as_bool

    @persist.setter
    def persist(self, value: bool) -> None:
        self.persist_model.as_bool = value


class SettingsWidget:
    """Build checkboxes for 'Variants', 'Show Issues on Root Layer only', and 'Save fixes' settings."""

    def __init__(self, model: ApplicationModel | None = None):
        self._model = model or ApplicationModel.get()
        self._options_menu = None
        style = {
            "Button": {"background_color": 0},
            "Button:selected": {"background_color": color.shade("#23211F")},
        }
        with HStack(height=0, style=style):
            Spacer()
            Button(
                width=24,
                height=24,
                image_url="resources/glyphs/settings.svg",
                mouse_pressed_fn=self._on_settings_pressed,
            )

    def _on_settings_pressed(self, x: int, y: int, button: int, flag: int) -> None:
        if button != 0:
            return
        options_model = OptionsModel(
            "Options",
            [
                OptionItem("variants", text="Enable variants", model=self._model.settings_model.variants_model),
                OptionItem("persist", text="Persist fixes", model=self._model.settings_model.persist_model),
            ],
        )
        self._options_menu = OptionsMenu(model=options_model)
        self._options_menu.show_at(x, y)
