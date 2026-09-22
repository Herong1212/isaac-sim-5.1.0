# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["ButtonExample"]

import copy
from typing import List

import carb
import carb.settings
import omni.ui as ui

from omni.kit.viewport.menubar.core import (
    ViewportMenuDelegate,
    ViewportButtonItem,
)

from .style import UI_STYLE
from ..style import VIEWPORT_MENUBAR_STYLE


class ButtonExample(ViewportButtonItem):
    """The button for screenshot"""

    def __init__(self, btn_id: int = 0, **kwargs):
        self._settings = carb.settings.get_settings()
        setting_root = f"/exts/omni.kit.viewport.menubar.example/button/{btn_id}"
        setting_visible = f"{setting_root}/visible"
        setting_order = f"{setting_root}/order"
        self._settings.set(setting_visible, True)
        self._settings.set(setting_order, -90)
        self.clicked = False

        test_ui_style = copy.copy(VIEWPORT_MENUBAR_STYLE)
        test_ui_style.update(UI_STYLE)
        super().__init__(
            text=kwargs.pop("text", None) or "Button With Flyout Menu",
            name=kwargs.pop("name", None) or "Sample",
            visible_setting_path=setting_visible,
            order_setting_path=setting_order,
            onclick_fn=self._on_click,
            build_menu_fn=self._build_menu_items if not kwargs.get("build_window_fn", None) else None,
            style=test_ui_style,
            **kwargs,
        )

    def _build_menu_items(self) -> List[ui.MenuItem]:
        return [
            ui.MenuItem(
                "Button 0",
                delegate=ViewportMenuDelegate(),
                hotkey_text="1",
            ),

            ui.MenuItem(
                "Button 1",
                delegate=ViewportMenuDelegate(),
                hotkey_text="CTRL + 2",
            ),
        ]

    def _on_click(self):
        self.clicked = True
