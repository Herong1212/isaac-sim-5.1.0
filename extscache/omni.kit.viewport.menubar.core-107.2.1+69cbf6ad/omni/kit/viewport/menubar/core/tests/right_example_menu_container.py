# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["RightExampleMenuContainer"]

from typing import Dict
from functools import partial

import carb
import carb.settings
from omni.kit.viewport.menubar.core import (
    IconMenuDelegate,
    ViewportMenuContainer,
    ViewportMenuDelegate,
)
import omni.ui as ui

from .style import UI_STYLE


class RightExampleMenuContainer(ViewportMenuContainer):
    """The menu aligned to right"""

    def __init__(self):
        self._settings = carb.settings.get_settings()
        self._settings.set("/exts/omni.kit.viewport.menubar.example/right/visible", True)
        self._settings.set("/exts/omni.kit.viewport.menubar.example/right/order", 100)
        super().__init__(
            name="Right Samples Menu",
            delegate=IconMenuDelegate("Sample", text=True),
            visible_setting_path="/exts/omni.kit.viewport.menubar.example/right/visible",
            order_setting_path="/exts/omni.kit.viewport.menubar.example/right/order",
            style=UI_STYLE
        )

        self._settings = carb.settings.get_settings()

    def build_fn(self, factory: Dict):
        """Entry point for the menu bar"""
        ui.Menu(
            self.name, delegate=self._delegate, on_build_fn=partial(self._build_menu_items, factory), style=UI_STYLE
        )

    def _build_menu_items(self, factory):
        ui.MenuItem(
            "Normal",
            checkable=False,
            delegate=ViewportMenuDelegate(),
        )

        ui.MenuItem(
            "Checked",
            checkable=True,
            checked=True,
            delegate=ViewportMenuDelegate(),
        )

        ui.MenuItem(
            "Disabled",
            enabled=False,
            delegate=ViewportMenuDelegate(),
        )

        ui.MenuItem(
            "Icon on the right",
            delegate=ViewportMenuDelegate(icon_name="Sample")
        )

        ui.Separator()

        with ui.Menu(
            "Sub menuitems without icon",
            delegate=ViewportMenuDelegate()
        ):
            for i in range(5):
                ui.MenuItem(f"Sub item {i}", delegate=ViewportMenuDelegate(),)

        with ui.Menu(
            "Sub menuitems with icon",
            delegate=ViewportMenuDelegate(icon_name="Sample"),
        ):
            for i in range(5):
                ui.MenuItem(f"Sub item {i}", delegate=ViewportMenuDelegate(),)
