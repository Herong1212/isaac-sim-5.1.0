# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["MetadataObjectModel"]

from typing import List

import carb
import omni.kit.commands
import omni.timeline
import omni.ui as ui
import omni.usd
from pxr import Sdf, Usd

from .usd_model_base import UsdBase
from .usd_model_items import OptionItem


class MetadataObjectModel(ui.AbstractItemModel, UsdBase):
    """The value model that is reimplemented in Python to watch a USD paths.
    Paths can be either Attribute or Prim paths"""

    def __init__(
        self,
        stage: Usd.Stage,
        object_paths: List[Sdf.Path],
        self_refresh: bool,
        metadata: dict,
        key: str,
        default,
        options: list,
    ):
        UsdBase.__init__(self, stage, object_paths, self_refresh, metadata)
        ui.AbstractItemModel.__init__(self)

        self._key = key
        self._default_idx = 0
        if default in options:
            self._default_idx = options.index(default)

        self._default_value = default
        self._combobox_options = options
        self._update_option()
        self._current_index = ui.SimpleIntModel(self._default_idx)
        self._current_index.add_value_changed_fn(self._current_index_changed)

        self._has_index = False
        self._update_value()
        self._has_index = True

    def clean(self):
        UsdBase.clean(self)

    def get_item_children(self, item):
        """
        Retrieves the children of an item.

        This method returns the children of the given item.

        Args:
            item: The item to get children for.

        Returns:
            list: A list of children for the given item.
        """
        self._update_value()
        return self._options

    def get_item_value_model(self, item, column_id):
        """
        Retrieves the value model for an item.

        This method returns the value model for the given item.

        Args:
            item: The item to get the value model for.
            column_id: The column ID to get the value model for.

        Returns:
            The value model for the given item.
        """
        if item is None:
            return self._current_index
        return item.model

    def begin_edit(self):  # pragma: no cover
        """
        Begins the edit process.

        This method is not supported in MetadataObjectModel.
        """
        carb.log_warn("begin_edit not supported in MetadataObjectModel")

    def end_edit(self):  # pragma: no cover
        """
        Ends the edit process.

        This method is not supported in MetadataObjectModel.
        """
        carb.log_warn("end_edit not supported in MetadataObjectModel")

    def _get_default_value(self, prop, metadata=None):
        """
        Retrieves the default value for a property.

        This method returns the default value for the given property.

        Args:
            prop: The property to get the default value for.
            metadata: The metadata to get the default value for.

        Returns:
            The default value for the given property.
        """
        self._default_value = self._default_idx
        return (True, self._default_value)

    def _current_index_changed(self, model):
        """
        Handles the change of the current index.

        This method updates the value of the current index and triggers an item change event.

        Args:
            model: The model that triggered the change.
        """
        if not self._has_index:
            return

        index = model.as_int
        if self.set_value(self._options[index].value):
            self._item_changed(None)

    def _update_option(self):
        """
        Updates the options for the combobox.

        This method updates the options for the combobox and triggers an item change event.
        """
        self._options = []
        for index, option in enumerate(self._combobox_options):
            self._options.append(OptionItem(option, int(index)))

    def is_different_from_default(self) -> bool:
        """
        Checks if the value is different from the default.

        This method checks if the value is different from the default.

        Returns:
            bool: True if the value is different from the default, False otherwise.
        """
        if self._value is None:
            return False
        return self._value not in self._combobox_options or (
            self._combobox_options.index(self._value) != self._default_idx
        )

    def _update_value(self, force=False):
        """
        Updates the value of the model.

        This method updates the value of the model and triggers an item change event.
        """
        if self._update_value_objects(force, False):
            index = -1
            for i, item in enumerate(self._options):
                if item.model.get_value_as_string() == self._value:
                    index = i

            if index not in (-1, self._current_index.as_int):
                self._has_index = False
                self._current_index.set_value(index)
                self._item_changed(None)
                self._has_index = True

    def set_default(self, comp=-1):
        """
        Sets the default value for the model.

        This method sets the default value for the model and triggers an item change event.
        """
        self.set_value(self._default_idx, comp)

    def _on_dirty(self):
        """
        Handles the dirty state of the model.

        This method handles the dirty state of the model and triggers an item change event.
        """
        self._update_value()

    def set_value(self, value, comp=-1):
        """
        Sets the value of the model.

        This method sets the value of the model and triggers an item change event.
        """
        if comp != -1:
            carb.log_warn("Arrays not supported in MetadataObjectModel")
            self._update_value(True)  # reset value
            return False

        if not self._ambiguous and not any(self._comp_ambiguous) and value == self._value:
            return False

        self._value = self._combobox_options[int(value)]
        objects = self._get_objects()
        if len(objects) == 0:
            return False

        self._write_value(objects=objects, key=self._key, value=self._value)

        # We just set all the properties to the same value, it's no longer ambiguous
        self._ambiguous = False
        self._comp_ambiguous.clear()
        self.update_control_state()

        return True

    def _read_value(self, obj: Usd.Object, time_code: Usd.TimeCode):
        """
        Reads the value of the model.

        This method reads the value of the model and returns it.
        """
        value = obj.GetMetadata(self._key)
        if not value:
            value = self._default_value

        return value

    def _write_value(self, objects: list, key: str, value):
        """
        Writes the value of the model.

        This method writes the value of the model to the objects.
        """
        path_list = []
        for obj in objects:
            path_list.append(obj.GetPath())

        omni.kit.commands.execute("ChangeMetadata", object_paths=path_list, key=key, value=value)
