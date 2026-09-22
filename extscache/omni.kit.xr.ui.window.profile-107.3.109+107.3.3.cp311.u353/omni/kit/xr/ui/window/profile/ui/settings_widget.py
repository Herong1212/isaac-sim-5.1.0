# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

from typing import Tuple, Union

import carb
import carb.settings
import omni.ui
from omni.kit.widget.settings import SettingType

from .settings_model import AssetPathSettingsModel, SettingModel, SettingsComboItemModel, VectorSettingsModel
from .settings_widget_builder import SettingsWidgetBuilder


def create_setting_widget(
    setting_path: str, setting_type: SettingType, range_from=0, range_to=0, step=0.01, **kwargs
) -> omni.ui.Widget:
    """
    Create a UI widget connected with a setting.

    If ``range_from`` >= ``range_to`` there is no limit. Undo/redo operations are also supported, because changing setting
    goes through the :mod:`omni.kit.commands` module, using :class:`.ChangeSettingCommand`.

    Args:
        setting_path: Path to the setting to show and edit.
        setting_type: Type of the setting to expect.
        range_from: Limit setting value lower bound.
        range_to: Limit setting value upper bound.

    Returns:
        :class:`ui.Widget` connected with the setting on the path specified.
    """
    widget = None
    model = None

    # Create widget to be used for particular type
    if setting_type == SettingType.INT:
        model = SettingModel(setting_path, draggable=True)
        widget = SettingsWidgetBuilder.createIntWidget(model, range_from, range_to, step, kwargs)
    elif setting_type == "INTFIELD":
        model = SettingModel(setting_path, draggable=True)
        widget = SettingsWidgetBuilder.createIntFieldWidget(model, kwargs)
    elif setting_type == SettingType.FLOAT:
        model = SettingModel(setting_path, draggable=True)
        widget = SettingsWidgetBuilder.createFloatWidget(model, range_from, range_to, step, kwargs)
    elif setting_type == "FLOATFIELD":
        model = SettingModel(setting_path, draggable=True)
        widget = SettingsWidgetBuilder.createFloatFieldWidget(model, kwargs)
    elif setting_type == SettingType.BOOL:
        model = SettingModel(setting_path)
        widget = SettingsWidgetBuilder.createBoolWidget(model, kwargs)
    elif setting_type == SettingType.STRING:
        model = SettingModel(setting_path)
        widget = omni.ui.StringField(**kwargs)
    elif setting_type == SettingType.COLOR3:
        model = VectorSettingsModel(setting_path, 3)
        widget = SettingsWidgetBuilder.createColorWidget(model, 3, kwargs)
    elif setting_type == SettingType.DOUBLE3:
        model = VectorSettingsModel(setting_path, 3)
        widget = SettingsWidgetBuilder.createVecWidget(model, range_from, range_to, 3, kwargs)
    elif setting_type == SettingType.DOUBLE2:
        model = VectorSettingsModel(setting_path, 2)
        widget = SettingsWidgetBuilder.createVecWidget(model, range_from, range_to, 2, kwargs)
    elif setting_type == SettingType.INT2:
        model = VectorSettingsModel(setting_path, 2)
        widget = SettingsWidgetBuilder.createIVecWidget(model, range_from, range_to, 2, kwargs)
    elif setting_type == "ASSET":
        model = AssetPathSettingsModel(setting_path)
        widget = SettingsWidgetBuilder.createAssetWidget(model, kwargs)
        SettingsWidgetBuilder._restore_defaults(setting_path, widget)
    elif setting_type == "PATH":
        model = AssetPathSettingsModel(setting_path)
        widget = SettingsWidgetBuilder.createPathWidget(model, kwargs)
    elif setting_type == "PATHORASSET":
        model = AssetPathSettingsModel(setting_path)
        widget = SettingsWidgetBuilder.createPathOrAssetWidget(model, kwargs)
    else:
        print("Couldn't find widget for ", setting_type, setting_path)  # Do we have any right now?
        return None

    if widget:
        try:
            widget.model = model
        except Exception:
            print(widget, "doesn't have model")

    return widget, model


def create_setting_widget_combo(
    setting_path: str, items: Union[list, dict], **kwargs
) -> Tuple[SettingsComboItemModel, omni.ui.ComboBox]:
    """
    Creating a Combo Setting widget.


    This function creates a combo box that shows a provided list of names and it is connected with setting by path
    specified. Underlying setting values are used from values of `items` dict.

    Args:
        setting_path: Path to the setting to show and edit.
        items: Can be either :py:obj:`dict` or :py:obj:`list`. For :py:obj:`dict` keys are UI displayed names, values are
            actual values set into settings. If it is a :py:obj:`list` UI displayed names are equal to setting values.
    """
    name_to_value = None

    # if we have a list, we want to synthesize a dict of type label: index
    if isinstance(items, list):
        name_to_value = dict(zip(items, items))
    elif isinstance(items, dict):
        name_to_value = items
    else:
        carb.log_error(f"Unsupported type {type(items)} for items in create_setting_widget_combo")
        return None

    model = SettingsComboItemModel(setting_path, name_to_value)
    widget = omni.ui.ComboBox(model, **kwargs)

    return widget, model
