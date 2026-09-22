# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["VariantSetModel", "SelectVariantPrimCommand"]

from typing import List

import omni.kit.commands
import omni.ui as ui
from pxr import Sdf, Usd

from .usd_model_base import UsdBase
from .usd_model_items import AllowedTokenItem


class VariantSetModel(ui.AbstractItemModel, UsdBase):
    """
    Model for the variant set.
    """

    def __init__(self, stage: Usd.Stage, object_paths: List[Sdf.Path], variant_set_name: str, self_refresh: bool):
        UsdBase.__init__(self, stage, object_paths, self_refresh, {})
        ui.AbstractItemModel.__init__(self)

        self._variant_set_name = variant_set_name
        self._variant_names = []

        self._current_index = ui.SimpleIntModel()
        self._current_index.add_value_changed_fn(self._current_index_changed)

        self._has_index = False
        self._update_value()
        self._has_index = True

    def clean(self):
        UsdBase.clean(self)

    def get_item_children(self, item):
        """
        Get the children of the item.

        Args:
            item (AbstractItem): The item to get the children of.

        Returns:
            List[AbstractItem]: The children of the item.
        """
        self._update_value()
        return self._variant_names

    def get_item_value_model(self, item, column_id):
        """
        Get the value model of the item.

        Args:
            item (AbstractItem): The item to get the value model of.
            column_id (int): The column id of the item.

        Returns:
            AbstractItem: The value model of the item.
        """
        if item is None:
            return self._current_index

        return item.model

    def begin_edit(self, item=None):
        """
        Begin the edit of the item.

        Args:
            item (AbstractItem): The item to begin the edit of.
        """
        UsdBase.begin_edit(self)

    def end_edit(self, item=None):
        """
        End the edit of the item.

        Args:
            item (AbstractItem): The item to end the edit of.
        """
        UsdBase.end_edit(self)

    def set_value(self, value, comp=-1):
        """
        Set the value of the item.

        Args:
            value (str): The value to set.
            comp (int): The component to set.
        """
        # if one than one item selected then don't early exit as
        # anchor might be same but others may not
        if value == self._value and len(self._variant_names) == 1:
            return

        omni.kit.commands.execute(
            "SelectVariantPrim",
            prim_path=self._object_paths,
            vset_name=self._variant_set_name,
            var_name=value,
        )

    def _current_index_changed(self, model):
        """
        The current index changed.

        Args:
            model (ui.SimpleIntModel): The model of the current index.
        """
        if not self._has_index:
            return

        index = model.as_int
        if self.set_value(self._variant_names[index].model.get_value_as_string()):
            self._item_changed(None)

    def _update_variant_names(self):
        """
        Update the variant names.
        """
        self._variant_names = []

        vset = self._get_variant_set()
        if vset:
            vnames = vset.GetVariantNames()

            self._variant_names.append(AllowedTokenItem(""))  # Empty variant
            for name in vnames:
                self._variant_names.append(AllowedTokenItem(name))

    def _update_value(self, force=False):
        """
        Update the value.

        Args:
            force (bool): Whether to force the update.
        """
        if self._update_value_objects(force, False):
            # TODO don't have to do this every time. Just needed when "VariantNames" actually changed
            self._update_variant_names()

            index = -1
            for i, item in enumerate(self._variant_names):
                if item.model.get_value_as_string() == self._value:
                    index = i

            if index not in (-1, self._current_index.as_int):
                self._current_index.set_value(index)
                self._item_changed(None)

    def _on_dirty(self):
        """
        The dirty event.
        """
        self._item_changed(None)

    def _read_value(self, obj: Usd.Object, time_code: Usd.TimeCode):
        """
        Read the value.

        Args:
            obj (Usd.Object): The object to read the value from.
            time_code (Usd.TimeCode): The time code to read the value from.

        Returns:
            str: The value.
        """
        vsets = obj.GetVariantSets()
        vset = vsets.GetVariantSet(self._variant_set_name)
        return vset.GetVariantSelection()

    def _get_variant_set(self):
        """
        Get the variant set.

        Returns:
            Usd.VariantSet: The variant set.
        """
        prims = self._get_objects()
        prim = prims[0] if len(prims) > 0 else None
        if prim:
            vsets = prim.GetVariantSets()
            return vsets.GetVariantSet(self._variant_set_name)
        return None


# Temporary commands. Expected to be moved when we have better support for variants
class SelectVariantPrimCommand(omni.kit.commands.Command):
    """
    Select the variant prim.
    """

    def __init__(self, prim_path: str, vset_name: str, var_name: str, usd_context_name: str = ""):
        """
        Initialize the command.

        Args:
            prim_path (str): The path of the prim.
            vset_name (str): The name of the variant set.
            var_name (str): The name of the variant.
            usd_context_name (str): The name of the usd context.
        """
        self._usd_context = omni.usd.get_context(usd_context_name)
        self._prim_path = prim_path if isinstance(prim_path, list) else [prim_path]
        self._vset_name = vset_name
        self._var_name = var_name
        self._previous_selection = None

    def do(self):
        """
        Do the command.
        """
        stage = self._usd_context.get_stage()
        self._previous_selection = {}
        for prim_path in self._prim_path:
            prim = stage.GetPrimAtPath(prim_path)
            vset = prim.GetVariantSets().GetVariantSet(self._vset_name)

            self._previous_selection[prim_path] = vset.GetVariantSelection()
            if self._var_name:
                vset.SetVariantSelection(self._var_name)
            else:
                vset.ClearVariantSelection()

    def undo(self):
        """
        Undo the command.
        """
        stage = self._usd_context.get_stage()
        for prim_path in self._prim_path:
            prim = stage.GetPrimAtPath(prim_path)
            vset = prim.GetVariantSets().GetVariantSet(self._vset_name)

            if prim_path in self._previous_selection:
                vset.SetVariantSelection(self._previous_selection[prim_path])
            else:
                vset.ClearVariantSelection()

        self._previous_selection = {}


omni.kit.commands.register_all_commands_in_module(__name__)
