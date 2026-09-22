# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["LeftExampleMenuContainer"]

from typing import Dict

import carb
import carb.settings
from omni.kit.viewport.menubar.core import (
    IconMenuDelegate,
    SliderMenuDelegate,
    CheckboxMenuDelegate,
    ViewportMenuContainer,
    FloatArraySettingColorMenuItem,
    ComboBoxMenuDelegate,
    SpinnerMenuDelegate,
    ComboBoxModel,
    CategoryMenuDelegate,
    CategoryStatus,
)
import omni.ui as ui

from .style import UI_STYLE


class LeftExampleMenuContainer(ViewportMenuContainer):
    """The menu aligned to left"""

    def __init__(self):
        self._settings = carb.settings.get_settings()
        self._settings.set("/exts/omni.kit.viewport.menubar.example/left/visible", True)
        self._settings.set("/exts/omni.kit.viewport.menubar.example/left/order", -100)
        super().__init__(
            name="Left Samples Menu",
            delegate=IconMenuDelegate("Sample"),
            visible_setting_path="/exts/omni.kit.viewport.menubar.example/left/visible",
            order_setting_path="/exts/omni.kit.viewport.menubar.example/left/order",
            style=UI_STYLE
        )

        self._settings = carb.settings.get_settings()

        self.float_slider_delegate = None

    def build_fn(self, factory: Dict):
        ui.Menu(
            self.name, delegate=self._delegate, on_build_fn=self._build_menu_items, style=self._style
        )

    def _build_menu_items(self):
        ui.MenuItem("Text only with clickable", hide_on_click=False, onclick_fn=lambda: print("Text Menu clicked"))
        ui.MenuItem(
            "Icon",
            delegate=IconMenuDelegate("Sample", text=True, has_triangle=False),
            hide_on_click=False, onclick_fn=lambda: print("Icon Menu clicked")
        )

        ui.Separator()

        self.float_slider_delegate = SliderMenuDelegate(
            model=ui.SimpleFloatModel(0.5),
            min=0.0,
            max=1.0,
            tooltip="Float slider Sample",
        )
        ui.MenuItem(
            "Float Slider",
            hide_on_click=False,
            delegate=self.float_slider_delegate
        )

        ui.MenuItem(
            "Int Slider",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=ui.SimpleIntModel(5),
                min=1,
                max=15,
                slider_class=ui.IntSlider,
                tooltip="Int slider Sample",
            ),
        )

        ui.Separator()

        ui.MenuItem(
            "CheckBox",
            hide_on_click=False,
            delegate=CheckboxMenuDelegate(
                model=ui.SimpleBoolModel(True),
                tooltip="CheckBox Sample",
            ),
        )

        ui.Separator()

        ui.MenuItem(
            "ComboBox",
            delegate=ComboBoxMenuDelegate(
                model=ComboBoxModel(["This", "is", "a", "test", "combobox"], values=[0, 1, 2, 3, 4])
            ),
            hide_on_click=False,
        )

        ui.Separator()
        ui.MenuItem(
            "Spinner with range",
            delegate=SpinnerMenuDelegate(
                model=ui.SimpleIntModel(80), min=50, max=100,
            ),
            hide_on_click=False,
        )
        ui.MenuItem(
            "Spinner without range",
            delegate=SpinnerMenuDelegate(
                model=ui.SimpleIntModel(80),
            ),
            hide_on_click=False,
        )

        ui.Separator()

        FloatArraySettingColorMenuItem(
            "/exts/omni.kit.viewport.menubar.example/left/color",
            [0.1, 0.2, 0.3],
            name="Selection Color",
            start_index=0
        )

        ui.Separator()
        ui.MenuItem(
            "Category All",
            delegate=CategoryMenuDelegate(CategoryStatus.ALL)
        )
        ui.MenuItem(
            "Category Mixed",
            delegate=CategoryMenuDelegate(CategoryStatus.MIXED)
        )
        ui.MenuItem(
            "Category Empty",
            delegate=CategoryMenuDelegate(CategoryStatus.EMPTY)
        )
