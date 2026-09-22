"""
Source for SettingModel, RadioButtonSettingModel, AssetPathSettingsModel, VectorFloatComponentModel, VectorIntComponentModel, VectorSettingsModel, VectorFloatSettingsModel, VectorIntSettingsModel, SettingsComboValueModel, SettingsComboNameValueItem, SettingsComboItemModel.
"""
__all__ = ['update_reset_button', 'SettingModel', 'RadioButtonSettingModel', 'AssetPathSettingsModel', 'VectorFloatComponentModel', 'VectorIntComponentModel', 'VectorSettingsModel', 'VectorFloatSettingsModel', 'VectorIntSettingsModel', 'SettingsComboValueModel', 'SettingsComboNameValueItem', 'SettingsComboItemModel']

from typing import Any, Dict, Union

import carb
import carb.dictionary
import carb.settings
import omni.kit.commands
import omni.ui as ui


def update_reset_button(settingModel):
    """
    work out whether to show the reset button highlighted or not depending on whether the setting
    is set to it's default value
    """
    if not settingModel._reset_button:
        return

    # This lookup of rtx-defaults involves some other extension having copied
    # the data from /rtx to /rtx-defaults..
    default_path = settingModel._path.replace("/rtx/", "/rtx-defaults/")
    item = settingModel._settings.get_settings_dictionary(default_path)

    if item is not None:
        if settingModel._settings.get(settingModel._path) == settingModel._settings.get(default_path):
            settingModel._reset_button.visible = False
        else:
            settingModel._reset_button.visible = True
    else: # pragma: no cover
        carb.log_info(f"update_reset_button: \"{default_path}\" not found")


class SettingModel(ui.AbstractValueModel):
    """
    Model for simple scalar/POD carb.settings
    """

    def __init__(self, setting_path: str, draggable: bool = False):
        """
        SettingModel init function.

        Args:
            setting_path: setting_path carb setting to create a model for
            draggable: is it a numeric value you will drag in the UI?
        """
        ui.AbstractValueModel.__init__(self)
        self._settings = carb.settings.get_settings()
        self._dictionary = carb.dictionary.get_dictionary()
        self._path = setting_path
        self.draggable = draggable
        self.initialValue = None
        self._reset_button = None
        self._editing = False
        self._range_set = False
        self._min = None
        self._max = None

        self._update_setting = omni.kit.app.SettingChangeSubscription(self._path, self._on_change)

    def set_range(self, min_val, max_val):
        '''
        set the allowable range for the setting. This is more restrictive than the UI min/max setting
        which still lets you set out of range values using the keyboard (e.g click and type in slider)
        '''
        self._range_set = True
        self._min = min_val
        self._max = max_val

    def _on_change(owner, value, event_type) -> None:
        if event_type == carb.settings.ChangeEventType.CHANGED:
            owner._on_dirty()
            if owner._editing is False:
                owner._update_reset_button()

    def begin_edit(self) -> None:
        self._editing = True
        ui.AbstractValueModel.begin_edit(self)
        self.initialValue = self._settings.get(self._path)
        if self.initialValue is None: # pragma: no cover
            carb.log_warn(f"a value for setting {self._path} has been requested but is not available")

    def end_edit(self) -> None:
        ui.AbstractValueModel.end_edit(self)
        value = self._settings.get(self._path)
        if value is None: # pragma: no cover
            carb.log_warn(f"a value for setting {self._path} has been requested but is not available")
        omni.kit.commands.execute(
            "ChangeSetting", path=self._path, value=value, prev=self.initialValue
        )
        self._update_reset_button()
        self._editing = False

    def _get_value(self):
        value = self._settings.get(self._path)
        if value is None: # pragma: no cover
            carb.log_warn(f"a value for setting {self._path} has been requested but is not available")
        return value

    def get_value(self):
        """
        Get current value
        """
        return self._get_value()

    def get_value_as_string(self) -> str:
        """
        Get current value as string
        """
        return self._get_value()

    def get_value_as_float(self) -> float:
        """
        Get current value as float
        """
        v = self._get_value()
        return 0.0 if v is None else float(v)

    def get_value_as_bool(self) -> bool:
        """
        Get current value as bool
        """
        return bool(self._get_value())

    def get_value_as_int(self) -> int:
        """
        Get current value as integer
        """
        v = self._get_value()
        return 0 if v is None else int(v)

    def set_value(self, value: Any):
        if self._range_set and (value < self._min or value > self._max):
            #print(f"not changing value to {value} as it's outside the range {self._min}-{self._max}")
            return

        if not self.draggable:
            omni.kit.commands.execute("ChangeSetting", path=self._path, value=value)
            update_reset_button(self)
            self._on_dirty()
        else:
            omni.kit.commands.execute("ChangeDraggableSetting", path=self._path, value=value)

    def _update_reset_button(self):
        update_reset_button(self)

    def set_reset_button(self, button: ui.Rectangle):
        """
        Set reset button from ui.Rectangle.
        """
        self._reset_button = button
        update_reset_button(self)

    def _on_dirty(self):
        # Tell the widgets that the model value has changed
        self._value_changed()

    def destroy(self): # pragma: no cover
        """
        Destroy class and cleanup.
        """
        self._reset_button = None
        self._update_setting = None


class RadioButtonSettingModel(ui.SimpleStringModel):
    """Model for simple RadioButton widget. The setting value and options are strings."""

    def __init__(self, setting_path: str):
        """
        RadioButtonSettingModel init function.

        Args:
            setting_path: Carb setting path to create a model for.
                          RadioButton items are specified in carb.settings "{setting_path}/items"
        """
        super().__init__()
        self._settings = carb.settings.get_settings()
        self._dictionary = carb.dictionary.get_dictionary()
        self._setting_path = setting_path
        self._items = None
        self._reset_button = None
        self._editing = False
        # This sets the index to the current value of the setting, we can't always assume 0th/first
        self._on_setting_change(self, carb.settings.ChangeEventType.CHANGED)

        self.add_value_changed_fn(self._value_changed)

        self._update_setting = omni.kit.app.SettingChangeSubscription(self.setting_path, self._on_setting_change)

    @property
    def setting_path(self):
        return self._setting_path

    @property
    def items(self) -> tuple:
        return self._items if self._items is not None else self._get_items()

    def set_reset_button(self, button: ui.Rectangle):
        """
        Set reset button from ui.Rectangle.
        """
        self._reset_button = button
        update_reset_button(self)

    def _update_reset_button(self):
        update_reset_button(self)

    def _execute_kit_change_setting_command(self, value, previous_value=None):
        kwargs = {"value": value, "path": self.setting_path}
        if isinstance(previous_value, int):
            kwargs["prev"] = previous_value
        omni.kit.commands.execute("ChangeSetting", **kwargs)

    def _on_setting_change(self, _: carb.dictionary.Item, event_type):
        """
        This gets called this if:
        + Something else changes the setting (e.g an undo command)
        + We also use as a debugging tool to make sure things were changed..

        Args:
            _ (carb.dictionary.Item): Not used here.
            event_type: use to filter
        """
        if event_type != carb.settings.ChangeEventType.CHANGED:
            return

        value = self._settings.get(self.setting_path)
        self.set_value(value, update_setting=False)
        self._update_reset_button()

    def _value_changed(self, model):
        self.set_value(self.get_value_as_string())

    def get_value(self) -> str:
        """Return current selected item string/label."""
        return self.get_value_as_string()

    def set_value(self, value: Union[int, str], update_setting: bool = True):
        """Set given value as current selected

        Args:
            value (int|str): Value to set. It can be either an int (index) or a string (label)

        Kwargs:
            update_setting (bool): Update corresponding carb.setting. Default True.
        """
        if isinstance(value, int):
            value = self.items[value]

        super().set_value(value)
        if update_setting:
            self._execute_kit_change_setting_command(value)

        update_reset_button(self)

    def get_value_as_int(self) -> int:
        """Return current selected item idx."""
        value = self.get_value()
        try:
            idx = self.items.index(value)
        except ValueError:
            idx = -1

        return idx

    def _get_items(self) -> tuple:
        """Return radiobutton items from carb.settings."""
        setting_path = self.setting_path.split("/")[:-1]
        setting_path.append("items")
        setting_path = "/".join(setting_path)
        self._itmes = tuple(self._settings.get(setting_path) or [])
        return self._itmes


class AssetPathSettingsModel(SettingModel):
    def get_resolved_path(self):
        """
        Get full path.
        """
        # @TODO: do I need to add in some kind of URI Resolution here?
        return self.get_value_as_string()


class VectorFloatComponentModel(ui.SimpleFloatModel):
    """
    VectorFloatComponentModel
    """
    def __init__(self, parent, vec_index, immediate_mode):
        """
        VectorFloatComponentModel init function.
        """
        super().__init__()
        self.parent = parent
        self.vec_index = vec_index
        self.immediate_mode = immediate_mode
        self._range_set = False
        self._min = None
        self._max = None

    def set_range(self, min_val=None, max_val=None):
        '''
        set the allowable range for the setting. This is more restrictive than the UI min/max setting
        which still lets you set out of range values using the keyboard (e.g click and type in slider)
        '''
        if min_val is None and max_val is None:
            self._range_set = False
        else:
            self._range_set = True
        self._min = min_val
        self._max = max_val

    def get_value_as_float(self):
        # The SimpleFloatModel class is storing a simple float value which works with get/set, so lets use that
        if not self.immediate_mode:
            return super().get_value_as_float()

        val = self.parent._settings.get(self.parent._path)
        # NOTE: Not sure why, but sometimes val can be a 2 float rather than a 3
        if len(val) > self.vec_index:
            return val[self.vec_index]
        return 0.0

    def set_value(self, val):
        if self._range_set and (val < self._min or val > self._max):
            carb.log_verbose(f"not changing value to {val} as it's outside the range {self._min}-{self._max}")
            return
        super().set_value(val)  # If this isn't here, any callbacks won't get called
        # As the change occurs, set the setting immediately so any client (e.g the viewport) see it instantly
        if self.immediate_mode:
            vec = self.parent._settings.get(self.parent._path)
            vec[self.vec_index] = val
            self.parent._settings.set(self.parent._path, vec)


class VectorIntComponentModel(ui.SimpleIntModel):
    def __init__(self, parent, vec_index, immediate_mode):
        """
        VectorIntComponentModel init function.
        """
        super().__init__()
        self.parent = parent
        self.vec_index = vec_index
        self.immediate_mode = immediate_mode

    def get_value_as_int(self):
        # The SimpleIntModel class is storing a simple int value which works with get/set, so lets use that
        if not self.immediate_mode:
            return super().get_value_as_int()

        val = self.parent._settings.get(self.parent._path)
        # NOTE: Not sure why, but sometimes val can be a 2 int rather than a 3
        if len(val) > self.vec_index:
            return val[self.vec_index]
        return 0

    def set_value(self, val):
        super().set_value(val)  # If this isn't here, any callbacks won't get called
        # As the change occurs, set the setting immediately so any client (e.g the viewport) see it instantly
        if self.immediate_mode:
            vec = self.parent._settings.get(self.parent._path)
            vec[self.vec_index] = val
            self.parent._settings.set(self.parent._path, vec)


class VectorSettingsModel(ui.AbstractItemModel):
    """
    Model For Color, Vec3 and other multi-component settings
    Assumption is the items are draggable, so we only store a command when the dragging has completed.

    TODO: Needs testing with component_count = 2,4
    """

    def __init__(self, setting_path: str, component_count: int, item_class: ui.AbstractItemModel, immediate_mode: bool):
        """
        VectorSettingsModel init function.

        Args:
            setting_path: setting_path carb setting to create a model for
            component_count: how many elements does the setting have?
            immediate_mode: do we update the underlying setting immediately, or wait for endEdit
        """
        ui.AbstractItemModel.__init__(self)
        self._comp_count = component_count
        self._path = setting_path
        self._settings = carb.settings.get_settings()
        self._dictionary = carb.dictionary.get_dictionary()
        self._dirty = False
        self._reset_button = None

        class VectorItem(ui.AbstractItem):
            def __init__(self, model):
                super().__init__()
                self.model = model

        # Create one model per component
        self._items = [VectorItem(item_class(self, i, immediate_mode)) for i in range(self._comp_count)]
        for item in self._items:
            # Tell the parent model when the submodel changes the value
            item.model.add_value_changed_fn(lambda a, item=item: self._item_changed(item))
            # These cause the component-wise R,G,B sliders to log a change command
            item.model.add_begin_edit_fn(lambda a, item=item: self.begin_edit(item))
            item.model.add_end_edit_fn(lambda a, item=item: self.end_edit(item))

    def _on_change(owner, item: carb.dictionary._dictionary.Item, event_type: carb.settings.ChangeEventType):
        """
        when an undo, reset_to_default or other change to the setting happens outside this model
        update the component child models
        """
        if event_type == carb.settings.ChangeEventType.CHANGED and not owner._dirty:
            owner._item_changed(None)
            owner._update_reset_button()

    def get_item_children(self, item: ui.AbstractItem = None):
        """
        this is called by the widget when it needs the submodel items
        """
        if item is None:
            return self._items
        return super().get_item_children(item)

    def get_item_value_model(self, sub_model_item: ui.AbstractItem = None, column_id: int = 0):
        """
        This is called by the widget when it needs the submodel item models.
        (to then get or set them)
        """
        if sub_model_item is None:
            return self._items[column_id].model
        return sub_model_item.model

    def begin_edit(self, item: ui.AbstractItem):
        """
        Stub: need implementation to prevent crashes.
        """
        lambda: None

    def set_reset_button(self, button: ui.Rectangle):
        """
        Set reset button from ui.Rectangle.
        """
        self._reset_button = button
        update_reset_button(self)

    def _update_reset_button(self):
        update_reset_button(self)

    def end_edit(self, item):
        pass

    def destroy(self): # pragma: no cover
        """
        Destroy class and cleanup.
        """
        self._update_setting = None
        self._root_model = None
        self._on_change = None
        self._reset_button = None

    def set_value(self, values: Union[tuple, list]):
        """Set list of values to the model."""
        for idx, child_item in enumerate(self.get_item_children()):
            child_item.model.set_value(values[idx])


class VectorFloatSettingsModel(VectorSettingsModel):
    def __init__(self, setting_path: str, component_count: int, immediate_mode: bool = True):
        super().__init__(setting_path, component_count, VectorFloatComponentModel, immediate_mode)

        # Register change event when the underlying setting changes.. but make sure start off with the correct
        # Setting also..
        dict1 = carb.dictionary.acquire_dictionary_interface()
        arint_item = dict1.create_item(None, "", carb.dictionary.ItemType.DICTIONARY)
        value = self._settings.get(self._path)
        if value is None:
            carb.log_warn(f"a value for setting {self._path} has been requested but is not available")
        dict1.set_float_array(arint_item, value)
        self._on_change(arint_item, carb.settings.ChangeEventType.CHANGED)
        self._update_setting = omni.kit.app.SettingChangeSubscription(self._path, self._on_change)

    def end_edit(self, item):
        old_dirty = self._dirty
        self._dirty = True  # Use to stop _on_change running
        vector = [item.model.get_value_as_float() for item in self._items]
        if vector:
            omni.kit.commands.execute("ChangeSetting", path=self._path, value=vector)
            self._update_reset_button()
        self._dirty = old_dirty

    def get_value(self) -> tuple:
        """Return current float values tuple."""
        values = []
        for child_item in self.get_item_children():
            values.append(child_item.model.get_value_as_float())
        return tuple(values)


class VectorIntSettingsModel(VectorSettingsModel):
    def __init__(self, setting_path: str, component_count: int, immediate_mode: bool = True):
        super().__init__(setting_path, component_count, VectorIntComponentModel, immediate_mode)

        # Register change event when the underlying setting changes.. but make sure start off with the correct
        # Setting also..
        dict1 = carb.dictionary.acquire_dictionary_interface()
        arint_item = dict1.create_item(None, "", carb.dictionary.ItemType.DICTIONARY)
        value = self._settings.get(self._path)
        if value is None:
            carb.log_warn(f"a value for setting {self._path} has been requested but is not available")
        dict1.set_int_array(arint_item, value)
        self._on_change(arint_item, carb.settings.ChangeEventType.CHANGED)
        self._update_setting = omni.kit.app.SettingChangeSubscription(self._path, self._on_change)

    def end_edit(self, item):
        old_dirty = self._dirty
        self._dirty = True  # Use to stop _on_change running
        vector = [item.model.get_value_as_float() for item in self._items]
        if vector:
            omni.kit.commands.execute("ChangeSetting", path=self._path, value=vector)
            self._update_reset_button()
        self._dirty = old_dirty

    def get_value(self) -> tuple:
        """Return current int values tuple."""
        values = []
        for child_item in self.get_item_children():
            values.append(child_item.model.get_value_as_int())
        return tuple(values)


class SettingsComboValueModel(ui.AbstractValueModel):
    """
    Model to store a pair (label, value of arbitrary type) for use in a ComboBox
    """

    def __init__(self, label: str, value: Any):
        """
        SettingsComboValueModel init function.

        Args:
            label: what appears in the UI widget
            value: the value corresponding to that label
        """
        ui.AbstractValueModel.__init__(self)
        self.label = str(label)
        self.value = value

    def __repr__(self):
        return f'"SettingsComboValueModel label:{self.label} value:{self.value}"'

    def get_value_as_string(self) -> str:
        """
        this is called to get the label of the combo box item
        """
        return self.label

    def get_setting_value(self) -> Union[str, int, float]:
        """
        we call this to get the value of the combo box item
        """
        return self.value


class SettingsComboNameValueItem(ui.AbstractItem):
    """
    SettingsComboNameValueItem for combo boxes
    """
    def __init__(self, label: str, value: str):
        """
        SettingsComboNameValueItem init function.
        """
        super().__init__()
        self.model = SettingsComboValueModel(label, value)

    def __repr__(self):
        return f'"SettingsComboNameValueItem {self.model}"'


class SettingsComboItemModel(ui.AbstractItemModel):
    """
    Model for a combo box - for each setting we have a dictionary of key, values
    """
    class ComboboxIndexModel(ui.SimpleIntModel):
        """
        A custom ui.SimpleIntModel that can handle value <-> index conversion when setting values.
        """
        def __init__(self, combobox_model, *args, **kwargs):
            self._combobox_model = combobox_model
            super().__init__(*args, **kwargs)

        def set_value(self, value, as_index=True):
            """Set the given index value to the model.
            If the given value is not int type, it will try to find the index from the given value.
            If the given value is int but as_index is False, it will still try to find the index
            from the given value.
            """
            # The given value is a setting value, try to find its index
            if not isinstance(value, int) or not as_index:
                value = self._combobox_model.get_item_index(value)

            return super().set_value(value)

    def __init__(self, setting_path, key_value_pairs: Dict[str, Any], setting_is_index: bool = True, allow_non_items: bool = False):
        super().__init__()
        self._settings = carb.settings.get_settings()
        self._dictionary = carb.dictionary.get_dictionary()
        self._setting_is_index = setting_is_index
        self._path = setting_path
        self._reset_button = None
        self._items = []
        for label, value in key_value_pairs.items():
            self._items.append(SettingsComboNameValueItem(label, value))

        self._allow_non_items = allow_non_items

        self._current_index = SettingsComboItemModel.ComboboxIndexModel(self)
        self._prev_index_val = self._current_index.as_int

        # This sets the index to the current value of the setting, we can't always assume 0th/first
        self._on_setting_change(self, carb.settings.ChangeEventType.CHANGED)

        self._current_index.add_value_changed_fn(self._current_index_changed)

        self._update_setting = omni.kit.app.SettingChangeSubscription(self._path, self._on_setting_change)
        self._dirty = True

    @property
    def setting_is_index(self):
        return self._setting_is_index

    def _update_reset_button(self):
        update_reset_button(self)

    def _on_setting_change(owner, item: carb.dictionary.Item, event_type):
        """
        This gets called this if:
        + Something else changes the setting (e.g an undo command)
        + We also use as a debugging tool to make sure things were changed..

        Args:
            owner: will be an instance of SettingsComboItemModel
            item: ?
            event_type: use to filter
        """
        value = owner._settings.get(owner._path)
        if event_type == carb.settings.ChangeEventType.CHANGED:
            owner.set_value(value)
            owner._update_reset_button()
            owner._dirty = True

    def _current_index_changed(self, model):
        if self._dirty:
            self._item_changed(None)
            index = model.as_int

            if self._setting_is_index:
                new_value = index
                old_value = self._prev_index_val
            else:
                new_value = self._items[index].model.get_setting_value()
                old_value = self._items[self._prev_index_val].model.get_setting_value()
            # update settings only when we need to
            if new_value != self._settings.get(self._path):
                omni.kit.commands.execute("ChangeSetting", path=self._path, value=new_value, prev=old_value)
                self._prev_index_val = index
                self._update_reset_button()

    def set_items(self, key_value_pairs: Dict[str, Any]):
        """
        Set items and refresh UI.
        """
        self._items.clear()
        for x, y in key_value_pairs.items():
            self._items.append(SettingsComboNameValueItem(x, y))
        self._item_changed(None)
        self._dirty = True

    def set_reset_button(self, button: ui.Rectangle):
        """
        Set reset button from ui.Rectangle.
        """
        self._reset_button = button
        update_reset_button(self)

    def get_item_children(self, item: ui.AbstractItem = None):
        """
        this is called by the widget when it needs the submodel items
        """
        if item is None:
            return self._items
        return super().get_item_children(item)

    def get_item_value_model(self, item: ui.AbstractItem = None, column_id: int = 0):
        if item is None:
            return self._current_index
        return item.model

    def get_value_as_int(self) -> int:
        """Get current selected item index
        Return:
            (int) Current selected item index
        """
        return self._current_index.get_value_as_int()

    def get_value_as_string(self) -> str:
        """Get current selected item label string.

        Return:
            (str) Current selected item label string.
        """
        return self._items[self.get_value_as_int()].model.get_value_as_string()

    def get_value(self) -> Any:
        """Get current selected item value or index value if setting_is_index is True.

        Return:
            (int|str|float) Current selected item value or index value depends
                      on the self._setting_is_index attribute.
        """
        index = self.get_value_as_int()
        return index if self._setting_is_index else self._items[index].model.get_setting_value()

    def get_item_index(self, value: Any) -> Union[int, None]:
        """Get the item index to the given value.

        Arg:
            value (int|str|float): The value to set.

        Return:
            (int|None) Item index. None if no item found.
        """
        if self._setting_is_index and isinstance(value, int) and value > -1:
            return value

        # Setting value matches combobox item's value
        for idx, item in enumerate(self._items):
            if item.model.value == value:
                return idx

        # Backward compatible
        for idx, item in enumerate(self._items):
            if item.model.label == value:
                return idx

    def set_value(self, value: Any) -> Union[int, None]:
        """Set current selected to the given value

        Arg:
            value (int|str|float): The value to set.

        Return:
            (int|None) Item index set. None if no item found.
        """
        idx = self.get_item_index(value)
        if isinstance(idx, int) and idx >= 0:
            if self.get_value_as_int() != idx:
                self._dirty = True
                self._current_index.set_value(idx)
                self._item_changed(None)
                self._dirty = False
            return idx
        elif self._allow_non_items:
            # Some combo-boxes might enter limbo state but recover after an update or two
            pass
        else:
            carb.log_warn(f"Unable to set \"{value}\" to combobox model. Setting path: {self._path}")

    def destroy(self): # pragma: no cover
        """
        Destroy class and cleanup.
        """
        self._update_setting = None
        self._reset_button = None
