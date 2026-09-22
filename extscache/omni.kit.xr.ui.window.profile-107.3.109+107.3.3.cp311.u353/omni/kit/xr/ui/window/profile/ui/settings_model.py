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

import math
from typing import Any, Dict, Sequence, Union

import carb
import carb.dictionary
import carb.settings
import omni.kit.commands
import omni.kit.ui
import omni.ui as ui
import omni.usd


def update_reset_button(settingModel):
    """
    work out whether to show the reset button highlighted or not depending on whether the setting
    is set to it's default value
    """
    if not settingModel._reset_button:
        return

    default_path = "/defaults" + settingModel._path
    if settingModel._path.startswith("/persistent"):
        default_path = "/defaults" + settingModel._path[11:]

    setting = settingModel._settings.get(settingModel._path)
    defSetting = settingModel._settings.get(default_path)

    # Deal with problem inside carb where empty strings equal no item present
    if defSetting is None:
        defSetting = ""

    if isinstance(setting, Sequence):
        if len(setting) == len(defSetting):
            different = False
            for idx in range(len(setting)):
                if not (
                    setting[idx] == defSetting[idx]
                    or (isinstance(setting[idx], float) and math.isclose(setting[idx], defSetting[idx]))
                ):
                    different = True

            if different is False:
                settingModel._reset_button.visible = False
            else:
                settingModel._reset_button.visible = True
        else:
            settingModel._reset_button.visible = True
    else:
        if setting == defSetting or (
            isinstance(setting, float) and isinstance(defSetting, float) and math.isclose(setting, defSetting)
        ):
            settingModel._reset_button.visible = False
        else:
            settingModel._reset_button.visible = True


class SettingModel(ui.AbstractValueModel):
    """
    Model for simple scalar/POD carb.settings
    """

    def __init__(self, setting_path: str, draggable: bool = False):
        """
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

        self._update_setting = omni.kit.app.SettingChangeSubscription(self._path, self._on_change)

    def _on_change(owner, value, event_type) -> None:
        if event_type == carb.settings.ChangeEventType.CHANGED:
            owner._on_dirty()
            if not owner._editing:
                owner._update_reset_button()

    def begin_edit(self) -> None:
        self._editing = True
        ui.AbstractValueModel.begin_edit(self)
        self.initialValue = self._settings.get(self._path)

    def end_edit(self) -> None:
        ui.AbstractValueModel.end_edit(self)
        omni.kit.commands.execute(
            "ChangeSettingCommand", path=self._path, value=self._settings.get(self._path), prev=self.initialValue
        )
        # Marks stage dirty manually since settings change are not synced to USD until user saves.
        if self._path.startswith("/xrstage"):
            omni.usd.get_context().set_pending_edit(True)
        self._update_reset_button()
        self._editing = False

    def get_value_as_string(self) -> str:
        val = self._settings.get(self._path)
        if val is None:
            val = ""
        return val

    def get_value_as_float(self) -> float:
        val = self._settings.get(self._path)
        if not isinstance(val, float):
            val = 0.0
        return val

    def get_value_as_bool(self) -> bool:
        val = self._settings.get(self._path)
        if not isinstance(val, bool):
            val = False
        return val

    def get_value_as_int(self) -> int:
        val = self._settings.get(self._path)
        if not isinstance(val, int):
            val = 0
        return val

    def set_value(self, value: Any):
        if not self.draggable:
            omni.kit.commands.execute("ChangeSettingCommand", path=self._path, value=value)
            # Marks stage dirty manually since settings change are not synced to USD until user saves.
            if self._path.startswith("/xrstage"):
                omni.usd.get_context().set_pending_edit(True)
            self._update_reset_button()
            self._on_dirty()
        else:
            self._settings.set(self._path, value)

    def _update_reset_button(self):
        update_reset_button(self)

    def set_reset_button(self, button: ui.Rectangle):
        self._reset_button = button
        self._update_reset_button()

    def _on_dirty(self):
        # Tell the widgets that the model value has changed
        self._value_changed()

    def destroy(self):
        self._reset_button = None
        self._update_setting = None


class AssetPathSettingsModel(SettingModel):
    def get_resolved_path(self):
        # @TODO: do I need to add in some kind of URI Resolution here?
        return self.get_value_as_string()


class VectorSettingsModel(ui.AbstractItemModel):
    """
    Model For Color, Vec3 and other multi-component settings
    Assumption is the items are draggable, so we only store a command when the dragging has completed.
    """

    def __init__(self, setting_path: str, component_count: int):
        """
        Args:
            setting_path: setting_path carb setting to create a model for
            component_count: how many elements does the setting have?
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

        # Create root model
        self._root_model = ui.SimpleIntModel()
        self._root_model.add_value_changed_fn(lambda a: self._item_changed(None))

        # Create three models per component
        self._items = [VectorItem(ui.SimpleFloatModel(0.0)) for i in range(self._comp_count)]
        for item in self._items:
            item.model.add_value_changed_fn(lambda a, item=item: self._on_value_changed(item))
            item.model.add_begin_edit_fn(lambda a, item=item: self.begin_edit(item))
            item.model.add_end_edit_fn(lambda a, item=item: self.end_edit(item))

        value = self._settings.get(self._path)

        if value is None:
            value = [0.0 for i in range(self._comp_count)]

        dict1 = carb.dictionary.acquire_dictionary_interface()
        arint_item = dict1.create_item(None, "", carb.dictionary.ItemType.DICTIONARY)
        dict1.set_float_array(arint_item, value)

        self._on_change(arint_item, carb.settings.ChangeEventType.CHANGED)
        self._update_setting = omni.kit.app.SettingChangeSubscription(self._path, self._on_change)

    def _on_change(owner, item: carb.dictionary._dictionary.Item, event_type):
        """
        when an undo, reset_to_default or other change to the setting happens outside this model
        update the component child models
        """
        if event_type == carb.settings.ChangeEventType.CHANGED and not owner._dirty:
            if len(item) == owner._comp_count:
                for cnt, vecItem in enumerate(owner._items):
                    model = vecItem.model
                    model.set_value(item["%i" % cnt])

            owner._update_reset_button()

    def _construct_vector_from_item(self):
        data = [item.model.get_value_as_float() for item in self._items]
        return data

    def _on_value_changed(self, item):
        self._item_changed(item)

    def get_item_children(self, item):
        return self._items

    def get_item_value_model(self, item, column_id):
        if item is None:
            return self._root_model
        return item.model

    def begin_edit(self, item):
        """
        TODO: if we don't add this override (even without a real implementation) we get crashes
        """
        pass

    def set_reset_button(self, button):
        self._reset_button = button
        self._update_reset_button()

    def _update_reset_button(self):
        update_reset_button(self)

    def end_edit(self, item):
        self._dirty = True  # Use to stop _on_change running
        vector = self._construct_vector_from_item()
        if vector:
            omni.kit.commands.execute("ChangeSettingCommand", path=self._path, value=vector)
            # Marks stage dirty manually since settings change are not synced to USD until user saves.
            if self._path.startswith("/xrstage"):
                omni.usd.get_context().set_pending_edit(True)
            self._update_reset_button()
        self._dirty = False

    def destroy(self):
        self._update_setting = None
        self._root_model = None
        self._on_change = None
        self._reset_button = None


class SettingsComboValueModel(ui.AbstractValueModel):
    """
    Model to store a pair (label, value of arbitrary type) for use in a ComboBox
    """

    def __init__(self, label: str, value: Any):
        """
        Args:
            label: what appears in the UI widget
            value: the value corresponding to that label
        """
        ui.AbstractValueModel.__init__(self)
        self.label = label
        self.value = value

    def __repr__(self):
        return f'"SettingsComboValueModel label:{self.label} value:{self.value}"'

    def get_value_as_string(self) -> str:
        """
        this is called to get the label of the combo box item
        """
        return self.label

    def get_setting_value(self) -> Union[str, int]:
        """
        we call this to get the value of the combo box item
        """
        return self.value


class SettingsComboNameValueItem(ui.AbstractItem):
    def __init__(self, label: str, value: str):
        super().__init__()
        self.model = SettingsComboValueModel(label, value)

    def __repr__(self):
        return f'"SettingsComboNameValueItem {self.model}"'


class SettingsComboItemModel(ui.AbstractItemModel):
    """
    Model for a combo box - for each setting we have a dictionary of key, values
    """

    def __init__(self, setting_path, key_value_pairs: Dict[str, Any]):
        super().__init__()
        self._settings = carb.settings.get_settings()
        self._dictionary = carb.dictionary.get_dictionary()
        self._path = setting_path
        self._reset_button = None
        self._items = []
        for x, y in key_value_pairs.items():
            self._items.append(SettingsComboNameValueItem(x, y))

        self._current_index = ui.SimpleIntModel()
        self._prev_index_val = self._current_index.as_int

        # This sets the index to the current value of the setting, we can't always assume 0th/first
        self._on_setting_change(self, carb.settings.ChangeEventType.CHANGED)

        self._current_index.add_value_changed_fn(self._current_index_changed)

        self._update_setting = omni.kit.app.SettingChangeSubscription(self._path, self._on_setting_change)
        self._dirty = True

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
        # TODO: should be able to extract the value from the item, but not sure how
        value = owner._settings.get(owner._path)
        if event_type == carb.settings.ChangeEventType.CHANGED:
            # We need to back track from the value to the index of the item that contains it
            index = -1
            for i in range(0, len(owner._items)):
                if owner._items[i].model.value == value:
                    index = i

            if index != -1 and owner._current_index.as_int != index:
                owner._dirty = False
                owner._current_index.set_value(index)
                owner._item_changed(None)
                owner._dirty = True

            owner._update_reset_button()

    def _current_index_changed(self, model):
        if self._dirty:
            self._item_changed(None)
            newValue = self._items[model.as_int].model.get_setting_value()
            oldValue = self._items[self._prev_index_val].model.get_setting_value()
            self._prev_index_val = model.as_int
            omni.kit.commands.execute("ChangeSettingCommand", path=self._path, value=newValue, prev=oldValue)

            # Marks stage dirty manually since settings change are not synced to USD until user saves.
            if self._path.startswith("/xrstage"):
                omni.usd.get_context().set_pending_edit(True)
            self._update_reset_button()

    def set_reset_button(self, button):
        self._reset_button = button
        self._update_reset_button()

    def get_item_children(self, item):
        return self._items

    def get_item_value_model(self, item, column_id: int):
        if item is None:
            return self._current_index
        return item.model

    def destroy(self):
        self._update_setting = None
        self._reset_button = None
