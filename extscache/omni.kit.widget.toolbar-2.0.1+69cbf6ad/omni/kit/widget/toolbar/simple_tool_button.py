# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["SimpleToolButton"]

import omni.ui
import weakref
from .hotkey import Hotkey
from .widget_group import WidgetGroup


class SimpleToolButton(WidgetGroup):
    """
    A helper class to create simple WidgetGroup that contains only one ToolButton.

    Args:
        name: Name of the ToolButton.
        tooltip: Tooltip of the ToolButton.
        icon_path: The icon to be used when button is not checked.
        icon_checked_path: The icon to be used when button is checked.
        hotkey: HotKey to toggle the button (optional).
        toggled_fn: Callback function when button is toggled. Signature: on_toggled(checked) (optional).
        model: Model for the ToolButton (optional).
        additional_style: Additional styling to apply to the ToolButton (optional).
    """

    def __init__(
        self,
        name,
        tooltip,
        icon_path,
        icon_checked_path,
        hotkey=None,
        toggled_fn=None,
        model=None,
        additional_style=None,
    ):
        super().__init__()
        self._name = name
        self._tooltip = tooltip
        self._icon_path = icon_path
        self._icon_checked_path = icon_checked_path
        self._hotkey = hotkey
        self._toggled_fn = toggled_fn
        self._model = model
        self._additional_style = additional_style
        self._hotkey = None
        if hotkey:
            def on_hotkey_changed(hotkey: str):
                self._tool_button.tooltip = f"{self._tooltip} ({hotkey})"

            self._select_hotkey = Hotkey(
                f"{name}::hotkey",
                hotkey,
                lambda: self._on_hotkey(),
                lambda: self._tool_button.enabled and self._is_in_context(),
                on_hotkey_changed_fn=lambda hotkey: on_hotkey_changed(hotkey),
            )

    def clean(self):
        super().clean()
        self._value_sub = None
        self._tool_button = None
        if self._select_hotkey:
            self._select_hotkey.clean()
            self._select_hotkey = None

    def get_style(self):
        style = {
            f"Button.Image::{self._name}": {"image_url": self._icon_path},
            f"Button.Image::{self._name}:checked": {"image_url": self._icon_checked_path},
        }
        if self._additional_style:
            style.update(self._additional_style)

        return style

    def create(self, default_size):
        def on_value_changed(model, widget):
            widget = widget()
            if widget is not None:
                if model.get_value_as_bool():
                    self._acquire_toolbar_context()
                else:
                    self._release_toolbar_context()

                widget._toggled_fn(model.get_value_as_bool())

        self._tool_button = omni.ui.ToolButton(
            name=self._name, model=self._model, tooltip=self._tooltip, width=default_size, height=default_size
        )

        if self._toggled_fn is not None:
            self._value_sub = self._tool_button.model.subscribe_value_changed_fn(
                lambda model, widget=weakref.ref(self): on_value_changed(model, widget)
            )

        # return a dictionary of name -> widget if you want to expose it to other widget_group
        return {self._name: self._tool_button}

    def get_tool_button(self):
        return self._tool_button

    def _on_hotkey(self):
        self._tool_button.model.set_value(not self._tool_button.model.get_value_as_bool())
