# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["PrimNameModel"]

import omni.ui as ui

import unicodedata
import carb
import carb.settings
import omni.usd
from pxr import Sdf
from typing import Callable
from omni.usd import make_valid_identifier
from ..utils import UnicodeNormalizationMethod, get_unicode_normalization_method


try:
    import omni.kit.notification_manager as nm
except ImportError:
    nm = None

class PrimNameModel(ui.AbstractValueModel):
    """The model that changes the prim name"""

    def __init__(self, stage_item):
        super().__init__()
        self.__stage_item = stage_item
        self.__label_on_begin = None
        self.__old_label = None
        self.__name_prefix = None
        self.__suffix_order = None
        self.rebuild()

    @staticmethod
    def _get_path_converter() -> Callable:
        """
        The Path conversion function to use for prim paths.

        Returns:
            Callable: The path conversion function.
        """
        return Sdf.Path

    def _refresh_name_prefix_and_suffix(self):
        parts = self.__stage_item.name.rpartition("_")
        if self.__stage_item.stage_model.show_prim_displayname:
            parts = self.__stage_item.display_name.rpartition("_")
        else:
            parts = self.__stage_item.name.rpartition("_")

        self.__name_prefix = None
        self.__suffix_order = None
        if parts and len(parts) > 1:
            suffix_order = parts[-1]
            are_all_digits = True
            for c in suffix_order:
                if not c.isdigit():
                    are_all_digits = False
                    break

            if are_all_digits and suffix_order:
                self.__name_prefix = parts[0].lower()
                self.__suffix_order = int(suffix_order)

        if self.__suffix_order is None:
            self.__name_prefix = self.__stage_item.name.lower()
            self.__suffix_order = 0

    @staticmethod
    def _make_valid_identifier(name: str):
        return make_valid_identifier(name)

    @property
    def stage_item(self):
        return self.__stage_item

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, value: str):
        self.__label = value

    @property
    def _old_label(self):
        return self.__old_label

    @property
    def _label_on_begin(self):
        return self.__label_on_begin

    @property
    def _prim_path(self):
        """DEPRECATED: to ensure back-compatibility."""
        return self.path

    @property
    def _name_prefix(self):
        """Name prefix without suffix number, e.g, `abc_01` will return abc. It's used for column sort."""

        return self.__name_prefix

    @property
    def _suffix_order(self):
        """Number suffix, e.g, `abc_01` will return 01. It's used for column sort."""

        return self.__suffix_order

    @property
    def path(self):
        return self.__stage_item.path

    def destroy(self):
        self.__stage_item = None

    def get_value_as_string(self):
        """Reimplemented get string"""
        return self.__label

    def rebuild(self):
        if self.__stage_item.is_flat:
            self.__label = str(self.__stage_item.path)
        else:
            if self.__stage_item.path == self._get_path_converter().absoluteRootPath:
                self.__label = "Root:"
            elif self.__stage_item.stage_model.show_prim_displayname:
                self.__label = self.__stage_item.display_name
            else:
                self.__label = self.__stage_item.name

        self._refresh_name_prefix_and_suffix()

    def begin_edit(self):
        self.__old_label = self.__label
        stage_model = self.__stage_item.stage_model
        if stage_model.show_prim_displayname:
            self.__label_on_begin = self.__stage_item.display_name
        else:
            self.__label_on_begin = self.__stage_item.name
            # OMPE-31959: Check and convert current label if NFC is enabled
            unicode_normalization_method = get_unicode_normalization_method()
            original_label = self.__label_on_begin
            if unicode_normalization_method != UnicodeNormalizationMethod.DISABLED:
                self.__label_on_begin = unicodedata.normalize(unicode_normalization_method, self.__label_on_begin)

            # Warn user if normalization changes the label
            if original_label != self.__label_on_begin:
                msg = f"Unicode {unicode_normalization_method} normalization has altered the prim name from '{original_label}' to '{self.__label_on_begin}'."
                carb.log_warn(msg)
                if nm:
                    nm.post_notification(msg, status=nm.NotificationStatus.WARNING)

        self.__label = self.__label_on_begin
        if self.__old_label != self.__label:
            self._value_changed()

    def set_value(self, value):
        """Reimplemented set"""

        try:
            value = str(value)
        except ValueError:
            value = ""
        if value != self.__label:
            self.__label = value
            self._value_changed()

    def end_edit(self):
        stage_model = self.__stage_item.stage_model
        unicode_normalization_method = get_unicode_normalization_method()
        if self.__label_on_begin == self.__label and unicode_normalization_method == UnicodeNormalizationMethod.DISABLED:
            if self.__label != self.__old_label:
                self.__label = self.__old_label
                self._value_changed()
            return

        if stage_model.show_prim_displayname:
            # OM-85989: If display name is going to be shown, use the text in the new label directly
            if stage_model.rename_prim(self.__stage_item.path, self.__label):
                self._refresh_name_prefix_and_suffix()
        else:
            # Get the unique name, replacing invalid characters with '_'
            parent_path = self.__stage_item.path.GetParentPath()
            valid_label_identifier = self._make_valid_identifier(self.__label)

            # Start candidate with the normalized valid identifier.
            new_prim_name = valid_label_identifier

            # OMPE-31959: Perform NFC normalization if enabled and we have a parent,
            # precompute the set of normalized names of the parent's children.
            if unicode_normalization_method != UnicodeNormalizationMethod.DISABLED:
                # Notify user if normalization changes the prim name
                original_prim_name = new_prim_name
                new_prim_name = unicodedata.normalize(unicode_normalization_method, new_prim_name)
                if original_prim_name != new_prim_name:
                    msg = f"Unicode {unicode_normalization_method} normalization has altered the prim name from '{original_prim_name}' to '{new_prim_name}'."
                    carb.log_warn(msg)
                    if nm:
                        nm.post_notification(msg, status=nm.NotificationStatus.WARNING)

                parent_prim = self.__stage_item.stage.GetPrimAtPath(parent_path)
                normalized_child_names = {
                    unicodedata.normalize(unicode_normalization_method, child.GetName())
                    for child in parent_prim.GetChildren()
                    if child != self.__stage_item.prim
                }
                # If the candidate name already exists among the normalized names,
                # create a new candidate name with a numerical suffix.
                if new_prim_name in normalized_child_names:
                    new_prim_path = parent_prim.GetPath().AppendChild(new_prim_name)
                    new_prim_path = omni.usd.get_stage_next_free_path(
                        self.__stage_item.stage, new_prim_path, False, self.__stage_item.prim)
                    new_prim_name = Sdf.Path(new_prim_path).name
                    if new_prim_name == self.__label_on_begin:
                        return
            else:
                # Fallback: check with GetPrimAtPath if NFC normalization is not enabled.
                created_path = parent_path.AppendElementString(new_prim_name)
                new_prim_path = omni.usd.get_stage_next_free_path(
                    self.__stage_item.stage, created_path, False, source_prim=self.__stage_item.prim)
                new_prim_name = Sdf.Path(new_prim_path).name

            # We check to be sure the stage accepts the rename of the item. If the item fails the rename, we
            # need to be sure to reset the label back to its original label name to prevent the interface being
            # out of sync with what is presented in the usd stage data. Both cases need `_value changed()` called.
            if stage_model.rename_prim(self.__stage_item.path, new_prim_name):
                self._refresh_name_prefix_and_suffix()
                self.__label = new_prim_name
            else:
                self.__label = self.__label_on_begin

        self._value_changed()
