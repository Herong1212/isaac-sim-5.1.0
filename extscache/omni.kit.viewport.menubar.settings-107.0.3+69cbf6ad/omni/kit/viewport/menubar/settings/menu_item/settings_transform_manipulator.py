# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["SettingsTransformManipulator"]

from functools import partial
from typing import Dict, Optional

import carb.settings
from omni.kit.viewport.menubar.core import (
    CheckboxMenuDelegate,
    ComboBoxMenuDelegate,
    SliderMenuDelegate,
    SettingComboBoxModel,
    ComboBoxItem,
    SettingModelWithDefaultValue,
    ResetHelper,
)
import omni.ui as ui

SETTING_SCALE = "/persistent/exts/omni.kit.manipulator.transform/manipulator/scaleMultiplier"
SETTING_FREE_ROTATION_ENABLED = "/persistent/exts/omni.kit.manipulator.transform/manipulator/freeRotationEnabled"
SETTING_FREE_ROTATION_TYPE = "/persistent/exts/omni.kit.manipulator.transform/manipulator/freeRotationType"
SETTING_INTERSECTION_THICKNESS = "/persistent/exts/omni.kit.manipulator.transform/manipulator/intersectionThickness"

FREE_ROTATION_TYPE_CLAMPED = "Clamped"
FREE_ROTATION_TYPE_CONTINUOUS = "Continuous"

MENU_WIDTH = 350


class _ManipulatorRotationTypeModel(SettingComboBoxModel, ResetHelper):
    def __init__(self):
        types = [FREE_ROTATION_TYPE_CLAMPED, FREE_ROTATION_TYPE_CONTINUOUS]
        super().__init__(SETTING_FREE_ROTATION_TYPE, types)

    def _on_current_item_changed(self, item: ComboBoxItem) -> None:
        super()._on_current_item_changed(item)
        self._update_reset_button()

    def get_default(self):
        return FREE_ROTATION_TYPE_CLAMPED

    def get_value(self):
        settings = carb.settings.get_settings()
        return settings.get(SETTING_FREE_ROTATION_TYPE)

    def restore_default(self) -> None:
        current_index = self.current_index
        if current_index:
            current = current_index.as_int
            items = self.get_item_children(None)
            # Early exit if the model is already correct
            if items[current].value == FREE_ROTATION_TYPE_CLAMPED:
                return
            # Iterate all items, and select the first match to the real value
            for index, item in enumerate(items):
                if item.value == FREE_ROTATION_TYPE_CLAMPED:
                    current_index.set_value(index)
                    return


class SettingsTransformManipulator(ui.Menu):
    """The menu with the transform manipulator settings"""

    def __init__(self, text: str = "", factory: Optional[Dict] = None, **kwargs):
        if factory is None:
            factory = {}
        settings = carb.settings.get_settings()

        settings.set_default_float(SETTING_SCALE, 1.4)
        settings.set_default_bool(SETTING_FREE_ROTATION_ENABLED, True)
        settings.set_default_string(SETTING_FREE_ROTATION_TYPE, FREE_ROTATION_TYPE_CLAMPED)
        settings.set_default_float(SETTING_INTERSECTION_THICKNESS, 10.0)

        super().__init__(text, on_build_fn=partial(self.build_fn, factory), **kwargs)

    def build_fn(self, factory: Dict):
        model = SettingModelWithDefaultValue(SETTING_SCALE, 1.4, draggable=True)
        ui.MenuItem(
            "Transform Manipulator Scale",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=model,
                width=MENU_WIDTH,
                min=0.0,
                max=25.0,
                has_reset=True,
            ),
            identifier='TransoformManipulatorScale'
        )

        model = SettingModelWithDefaultValue(SETTING_FREE_ROTATION_ENABLED, True, draggable=True)
        ui.MenuItem(
            "Enable Free Rotation",
            hide_on_click=False,
            delegate=CheckboxMenuDelegate(
                model=model,
                width=MENU_WIDTH,
                has_reset=True,
            ),
            identifier='EnableFreeRotation'
        )

        model = _ManipulatorRotationTypeModel()
        ui.MenuItem(
            "Free Rotation Type",
            hide_on_click=False,
            delegate=ComboBoxMenuDelegate(
                model=model,
                width=MENU_WIDTH,
                has_reset=True,
            ),
            identifier='FreeRotationType'
        )

        model = SettingModelWithDefaultValue(SETTING_INTERSECTION_THICKNESS, 10.0, True)
        ui.MenuItem(
            "Manipulator Intersection Thickness",
            hide_on_click=False,
            delegate=SliderMenuDelegate(
                model=model,
                width=MENU_WIDTH,
                min=1.0,
                max=50.0,
                has_reset=True,
            ),
            identifier='ManipulatorIntersectionThickness'
        )
