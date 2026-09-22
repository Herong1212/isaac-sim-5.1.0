"""
deprecated
"""
import omni.kit.ui # pragma: no cover
import carb # pragma: no cover
import carb.dictionary # pragma: no cover
import carb.settings # pragma: no cover
import collections # pragma: no cover
from typing import Union, Callable # pragma: no cover

from . import model # pragma: no cover


class SettingType: # pragma: no cover
    """
    Supported setting types
    """

    FLOAT = 0
    INT = 1
    COLOR3 = 2
    BOOL = 3
    STRING = 4
    DOUBLE3 = 5
    INT2 = 6
    DOUBLE2 = 7


def create_setting_widget(
    setting_path: str, setting_type: SettingType, range_from=0, range_to=0, speed=1, **kwargs
) -> omni.kit.ui.Widget: # pragma: no cover
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
        :class:`omni.kit.ui.Widget` connected with the setting on the path specified.
    """
    # Create widget to be used for particular type
    if setting_type == SettingType.INT:
        widget = omni.kit.ui.DragInt("", min=range_from, max=range_to, drag_speed=speed, **kwargs)
    elif setting_type == SettingType.FLOAT:
        widget = omni.kit.ui.DragDouble("", min=range_from, max=range_to, drag_speed=speed, **kwargs)
    elif setting_type == SettingType.BOOL:
        widget = omni.kit.ui.CheckBox(**kwargs)
    elif setting_type == SettingType.STRING:
        widget = omni.kit.ui.TextBox("", **kwargs)
    elif setting_type == SettingType.COLOR3:
        widget = omni.kit.ui.ColorRgb("", **kwargs)
    elif setting_type == SettingType.DOUBLE3:
        widget = omni.kit.ui.DragDouble3("", min=range_from, max=range_to, drag_speed=speed, **kwargs)
    elif setting_type == SettingType.INT2:
        widget = omni.kit.ui.DragInt2("", min=range_from, max=range_to, drag_speed=speed, **kwargs)
    elif setting_type == SettingType.DOUBLE2:
        widget = omni.kit.ui.DragDouble2("", min=range_from, max=range_to, drag_speed=speed, **kwargs)
    else:
        return None

    if isinstance(widget, omni.kit.ui.ModelWidget):
        widget.set_model(model.get_ui_model(), setting_path)

    return widget


def create_setting_widget_combo(setting_path: str, items: Union[list, dict]): # pragma: no cover
    """
    Create a Combo Setting widget.

    This function creates a combo box that shows a provided list of names and it is connected with setting by path 
    specified. Underlying setting values are used from values of `items` dict.

    Args:
        setting_path: Path to the setting to show and edit.
        items: Can be either :py:obj:`dict` or :py:obj:`list`. For :py:obj:`dict` keys are UI displayed names, values are 
            actual values set into settings. If it is a :py:obj:`list` UI displayed names are equal to setting values.
    """
    if isinstance(items, list):
        name_to_value = collections.OrderedDict(zip(items, items))
    elif isinstance(items, dict):
        name_to_value = items
    else:
        carb.log_error(f"Unsupported type {type(items)} for items in create_setting_widget_combo")
        return None

    if isinstance(next(iter(name_to_value.values())), int):
        widget = omni.kit.ui.ComboBoxInt("", list(name_to_value.values()), list(name_to_value.keys()))
    else:
        widget = omni.kit.ui.ComboBox("", list(name_to_value.values()), list(name_to_value.keys()))

    widget.set_model(model.get_ui_model(), setting_path)

    return widget
