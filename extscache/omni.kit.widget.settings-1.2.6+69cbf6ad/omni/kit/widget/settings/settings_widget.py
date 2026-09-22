"""
Source for SettingType, SettingWidgetType, SettingsSearchableCombo, create_setting_widget, create_setting_widget_combo.
"""
__all__ = ['SettingType', 'SettingWidgetType', 'create_setting_widget', 'create_setting_widget_combo', 'SettingsSearchableCombo']

from enum import Enum
from typing import Optional, Tuple, Union
import carb
import carb.settings
import omni.ui as ui
from .settings_model import (
    SettingModel,
    SettingsComboItemModel,
    VectorFloatSettingsModel,
    VectorIntSettingsModel,
    AssetPathSettingsModel,
    RadioButtonSettingModel,
)
from .settings_widget_builder import SettingsWidgetBuilder
import omni.kit.app


class SettingType(Enum):
    """
    Supported setting types for create_setting_widget.
    """
    FLOAT = 0
    """Setting is a floating-point number."""
    INT = 1
    """Setting is a integer number."""
    COLOR3 = 2
    """Setting is a three color floating-point numbers (0.0-1.0)."""
    BOOL = 3
    """Setting is a boolean."""
    STRING = 4
    """Setting is a string."""
    DOUBLE3 = 5
    """Setting is a three double-precision floating-point numbers."""
    INT2 = 6
    """Setting is a two integer numbers."""
    DOUBLE2 = 7
    """Setting is a two double-precision floating-point numbers."""
    ASSET = 8
    """Setting is a asset path."""


class SettingWidgetType(Enum):
    """
    Supported setting UI widget types
    """
    FLOAT = 0
    """Setting is a floating-point number."""
    INT = 1
    """Setting is a integer number."""
    COLOR3 = 2
    """Setting is a three color floating-point numbers (0.0-1.0)."""
    BOOL = 3
    """Setting is a boolean."""
    STRING = 4
    """Setting is a string."""
    DOUBLE3 = 5
    """Setting is a three double-precision floating-point numbers."""
    INT2 = 6
    """Setting is a two integer numbers."""
    DOUBLE2 = 7
    """Setting is a two double-precision floating-point numbers."""
    ASSET = 8
    """Setting is a asset path."""
    COMBOBOX = 9
    """Setting is Combo box."""
    RADIOBUTTON = 10
    """Setting is Radio buttons."""
    VECTOR3 = 11
    """Setting is Vector3."""


#  TODO: Section will be moved to some location like omni.ui.settings
#  #############################################################################################
def create_setting_widget(
    setting_path: str, setting_type: SettingType, range_from=0, range_to=0, speed=1, **kwargs
) -> Tuple[ui.Widget, ui.AbstractValueModel]:
    """
    Create a UI widget connected with a setting.

    If ``range_from`` >= ``range_to`` there is no limit. Undo/redo operations are also supported, because changing setting
    goes through the :mod:`omni.kit.commands` module, using :class:`.ChangeSettingCommand`.

    Args:
        setting_path: Path to the setting to show and edit.
        setting_type: Type of the setting to expect.
        range_from: Limit setting value lower bound.
        range_to: Limit setting value upper bound.
        speed: Range speed

    Returns:
        :class:`ui.Widget` and :class:`ui.AbstractValueModel` connected with the setting on the path specified.
    """
    widget = None
    model = None

    # In case setting_type is not an Enum (e.g. from deprecated module - omni.kit.widget.settings.deprecated.SettingType)
    # We do not support it anymore.
    # The string "ASSET" is for backward compatibility
    if not isinstance(setting_type, Enum) and setting_type != "ASSET":
        carb.log_warn(f"Unsupported setting widget type {setting_type} for {setting_path}")
        return None, None

    # Create widget to be used for particular type.
    if setting_type == SettingWidgetType.COMBOBOX:
        setting_is_index = kwargs.pop("setting_is_index", None)
        widget, model = SettingsWidgetBuilder.createComboboxWidget(setting_path, setting_is_index=setting_is_index, additional_widget_kwargs=kwargs)
    elif setting_type == SettingWidgetType.RADIOBUTTON:
        model = RadioButtonSettingModel(setting_path)
        widget = SettingsWidgetBuilder.createRadiobuttonWidget(model, setting_path, additional_widget_kwargs=kwargs)

    elif setting_type in [SettingType.INT, SettingWidgetType.INT]:
        model = SettingModel(setting_path, draggable=True)
        if model.get_value_as_int() is not None:
            widget = SettingsWidgetBuilder.createIntWidget(model, range_from, range_to, additional_widget_kwargs=kwargs)
    elif setting_type in [SettingType.FLOAT, SettingWidgetType.FLOAT]:
        model = SettingModel(setting_path, draggable=True)
        if model.get_value_as_float() is not None:
            widget = SettingsWidgetBuilder.createFloatWidget(model, range_from, range_to, additional_widget_kwargs=kwargs)
    elif setting_type in [SettingType.BOOL, SettingWidgetType.BOOL]:
        model = SettingModel(setting_path)
        if model.get_value_as_bool() is not None:
            widget = SettingsWidgetBuilder.createBoolWidget(model, additional_widget_kwargs=kwargs)
    elif setting_type in [SettingType.STRING, SettingWidgetType.STRING]:
        model = SettingModel(setting_path)
        if model.get_value_as_string() is not None:
            widget = ui.StringField(**kwargs)
    elif setting_type in [SettingType.COLOR3, SettingWidgetType.COLOR3]:
        model = VectorFloatSettingsModel(setting_path, 3)
        widget = SettingsWidgetBuilder.createColorWidget(model, comp_count=3, additional_widget_kwargs=kwargs)
    elif setting_type in [SettingWidgetType.VECTOR3]:
        model = VectorFloatSettingsModel(setting_path, 3)
        widget = SettingsWidgetBuilder.createVecWidget(model, range_from, range_to, comp_count=3, additional_widget_kwargs=kwargs)
    elif setting_type in [SettingType.DOUBLE2, SettingWidgetType.DOUBLE2]:
        model = VectorFloatSettingsModel(setting_path, 2)
        widget = SettingsWidgetBuilder.createDoubleArrayWidget(model, range_from, range_to, comp_count=2, additional_widget_kwargs=kwargs)
    elif setting_type in [SettingType.DOUBLE3, SettingWidgetType.DOUBLE3]:
        model = VectorFloatSettingsModel(setting_path, 3)
        widget = SettingsWidgetBuilder.createDoubleArrayWidget(model, range_from, range_to, comp_count=3, additional_widget_kwargs=kwargs)
    elif setting_type in [SettingType.INT2, SettingWidgetType.INT2]:
        model = VectorIntSettingsModel(setting_path, 2)
        widget = SettingsWidgetBuilder.createIntArrayWidget(model, range_from, range_to, comp_count=2, additional_widget_kwargs=kwargs)
    elif setting_type in [SettingType.ASSET, SettingWidgetType.ASSET, "ASSET"]:  # The string "ASSET" is for backward compatibility
        model = AssetPathSettingsModel(setting_path)
        widget = SettingsWidgetBuilder.createAssetWidget(model, additional_widget_kwargs=kwargs)
    else:  # pragma: no cover
        # Convenient way to extend new types of widget creation.
        build_widget_func = getattr(SettingsWidgetBuilder, f"create{setting_type.name.capitalize()}Widget", None)
        if build_widget_func:
            widget, model = build_widget_func(setting_path, additional_widget_kwargs=kwargs)
        else:
            carb.log_warn(f"Couldn't find widget for {setting_type} - {setting_path}")  # Do we have any right now?
            return None, None

    if widget and not isinstance(widget, ui.HStack):
        try:
            widget.model = model
        except Exception:
            # Don't panic. Some returned "widget" is a stack - e.g. createColorWidget(), so the line above raises an exception.
            # All widgets created have models already.
            # We keep this try except block just for backward compatibility.
            carb.log_info(f"{widget} ({setting_type}) doesn't have model")

    if isinstance(widget, ui.Widget) and not "identifier" in kwargs:
        widget.identifier = setting_path

    return widget, model


def create_setting_widget_combo(setting_path: str, items: Union[list, dict], setting_is_index: Optional[bool] = None,
                                allow_non_items: bool = False,
                                **kwargs) -> Tuple[SettingsComboItemModel, ui.ComboBox]:
    """
    Create a Combo Setting widget.


    This function creates a combo box that shows a provided list of names and it is connected with setting by path
    specified. Underlying setting values are used from values of `items` dict.

    Args:
        setting_path: Path to the setting to show and edit.
        items: Can be either :py:obj:`dict` or :py:obj:`list`. For :py:obj:`dict` keys are UI displayed names, values are
            actual values set into settings. If it is a :py:obj:`list` UI displayed names are equal to setting values.
        setting_is_index:
            None - Detect type from setting_path value. If the type is int, set to True.
            True - setting_path value is index into items list (default)
            False - setting_path value is string in items list
        allow_non_items:
            False - Will log errors if the setting is changed to a value that is not in the items parameter.
            True  - Will allow values that are not in the items parameter.
        **kwargs: Additional keyword arguments to omni.ui Widget constructor.
    """
    return SettingsWidgetBuilder.createComboboxWidget(setting_path, items=items, setting_is_index=setting_is_index,
                                                      allow_non_items = allow_non_items,
                                                      additional_widget_kwargs=kwargs)


class SettingsSearchableCombo:
    """
    Searchable combo box, needs omni.kit.widget.searchable_combobox extensions
    """
    def __init__(self, setting_path: str, key_value_pairs: dict, default_key: str):
        self._path = setting_path
        self._items = key_value_pairs
        self._default_key = default_key
        self._set_by_ui = False
        self._component_combo = None

        manager = omni.kit.app.get_app().get_extension_manager()
        self._hooks = []
        self._hooks.append(
            manager.subscribe_to_extension_enable(
                on_enable_fn=lambda _: self._register_searchwidget(),
                on_disable_fn=lambda _: self._unregister_searchwidget(),
                ext_name="omni.kit.widget.searchable_combobox",
                hook_name="omni.kit.widget.settings omni.kit.widget.searchable_combobox listener",
            )
        )

        self._update_setting = omni.kit.app.SettingChangeSubscription(self._path, self._on_setting_change)

    def destroy(self):
        """
        Destroy class and cleanup.
        """
        if self._component_combo:
            self._component_combo.destroy()
        self._component_combo = None
        self._update_setting = None
        self._hooks = []

    def _register_searchwidget(self):
        from omni.kit.widget.searchable_combobox import build_searchable_combo_widget

        def on_combo_click(model):
            item_key = model.get_value_as_string()
            if not item_key or item_key not in self._items:
                # There is no corresponding item name in the items list, so we don't set the setting
                return
            item_value = self._items[item_key]
            self._set_by_ui = True
            carb.settings.get_settings().set_string(self._path, item_value)

        key_index = -1
        key_list = sorted(list(self._items.keys()))
        self._component_combo = build_searchable_combo_widget(key_list, key_index, on_combo_click, widget_height=18, default_value=self._default_key)

    def _unregister_searchwidget(self):
        self._component_combo = None

    def get_key_from_value(self, value):
        """
        Gets key from value.
        """
        try:
            idx = list(self._items.values()).index(value)
            key = list(self._items.keys())[idx]
        except ValueError:
            # Display the value itself as the key when it's not found in the items list
            key = value
        return key

    def get_current_key(self):
        """
        Gets current key selected in combo box.
        """
        current_value = carb.settings.get_settings().get_as_string(self._path)
        return self.get_key_from_value(current_value)

    def _on_setting_change(owner, item: carb.dictionary.Item, event_type):
        if owner._set_by_ui:
            owner._set_by_ui = False
        else:
            if owner._component_combo:
                owner._component_combo.set_text(new_text=owner.get_current_key())
            else:
                carb.log_warn("omni.kit.widget.searchable_combobox isn't loaded")
