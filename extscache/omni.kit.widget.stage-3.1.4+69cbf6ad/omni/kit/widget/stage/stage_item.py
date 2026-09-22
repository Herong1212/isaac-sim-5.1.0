# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["StageItem"]

import carb
import omni.ui as ui
import omni.kit.usd.layers as layers
import omni.usd

from .models import PrimNameModel, TypeModel, VisibilityModel
from pxr import Sdf, UsdGeom, Usd
from typing import List, Optional


class StageItem(ui.AbstractItem):
    """
    A single AbstractItemModel item that represents a single prim. StageItem is a cached view of the prim.
    """

    def __init__(
        self,
        path: Sdf.Path,
        stage,
        stage_model,
        # Deprecated
        flat=False,
        root_identifier=None,
        load_payloads=False,
        check_missing_references=False,
    ):
        """
        Creates an instance of StageItem.

        Args:
            path (Sdf.Path): The prim path for the item.
            stage (Usd.Stage): Unused.
            stage_model (omni.kit.widget.stage.StageModel): The StageModel of the current item.
        """
        super().__init__()
        self.__stage_model = stage_model

        # Internal access
        self._path = path

        # Prim handle
        self.__prim = None

        # Filtering
        self.__filtered = False
        # True if it has any descendant that is filtered
        self.__child_filtered = False

        # defaultPrim
        self.__is_default = False

        # True if it has missing references
        self.__missing_references = None

        # True if it has references authored
        self.__has_references = False

        # All references/payloads for this prim
        self.__payrefs = set()

        # If this prim includes references/payloads that are out of sync.
        self.__is_outdated = False

        # True if it has payloads authored
        self.__has_payloads = False

        # True if the prim has authored inherits
        self.__has_inherits = False

        # True if the prim has authored specializes
        self.__has_specializes = False

        # True if it's visible
        self.__visible = True

        # True if is in session
        self.__in_session = False

        # True if it's instanceable
        self.__instanceable = False

        # True if this item should be auto-loaded when its
        # references or payloads are outdated.
        self.__auto_reload = False

        # True if it's children of instance.
        self.__instance_proxy = False

        self.__display_name = None

        # Lazy load
        self.__flags_updated = True

        # Models for builtin columns. Those models
        # will only be accessed internally.
        self.__name_model = None
        self.__type_model = None
        self.__visibility_model = None

    def destroy(self):
        """Internal method to release resources."""

        self.__stage = None
        self.__stage_model = None
        self.__payrefs.clear()

    @property
    def filtered(self) -> bool:
        """
        Whether the current stage item is filtered or not by search string.

        Returns:
            bool: Filtered state.
        """
        return self.__filtered

    @filtered.setter
    def filtered(self, value: bool):
        """
        Sets the filtered state to the given value.

        Args:
            value (bool): Filtered state.
        """
        if self.__filtered != value:
            self.__filtered = value
            if self.__name_model:
                self.__name_model.rebuild()

    @property
    def child_filtered(self) -> bool:
        """
        Returns if any child of stage item is filtered.

        Returns:
            bool: True if any child is filtered.
        """
        return self.__child_filtered

    @child_filtered.setter
    def child_filtered(self, value: bool):
        """
        Sets if any child of the stage item is filtered.

        Args:
            value (bool): Value to set.
        """
        if self.__child_filtered != value:
            self.__child_filtered = value
            if self.__name_model:
                self.__name_model.rebuild()

    @property
    def path(self) -> Sdf.Path:
        """
        Prim path.

        Returns:
            Sdf.Path: The prim path.
        """
        return self._path

    @property
    def stage_model(self):
        """
        StageModel this StageItem belongs to.

        Returns:
            omni.kit.widget.stage.StageModel: The StageModel
        """
        return self.__stage_model

    @property
    def usd_context(self) -> Optional[omni.usd.UsdContext]:
        """
        The usd context for the current stage of the stage model.

        Returns:
            Optional[omni.usd.UsdContext]: The associated usd context of the stage model.
        """
        return self.__stage_model.usd_context if self.__stage_model else None

    @property
    def stage(self) -> Optional[Usd.Stage]:
        """
        USD stage the prim belongs to.

        Returns:
            Optional[Usd.Stage]: The associated USD stage of the stage model.
        """
        return self.__stage_model.stage if self.__stage_model else None

    @property
    def payrefs(self) -> List[str]:
        """
        All external references and payloads that influence this prim.

        Returns:
            List[str]: References and payloads associated with this prim.
        """
        self._update_flags_internal()

        return list(self.__payrefs)

    @property
    def is_default(self) -> bool:
        """
        Whether this prim is the default prim or not.

        Returns:
            bool: If this prim is the default prim.
        """
        self._update_flags_internal()

        return self.__is_default

    @property
    def is_outdated(self) -> bool:
        """
        Whether this prim includes references or payloads that has new changes to fetch or not.

        Returns:
            bool: If the prim is outdated.
        """
        self._update_flags_internal()
        return self.__is_outdated

    @property
    def in_session(self) -> bool:
        """
        Whether this prim includes references or payloads that are in a live session.

        Returns:
            bool: If the prim includes references or payloads in live session.
        """
        self._update_flags_internal()

        return self.__in_session

    @property
    def auto_reload(self) -> bool:
        """
        Whether this prim is configured to be auto-reload when its references or payloads are outdated.

        Returns:
            bool: Set to be auto-reloaded or not.
        """
        self._update_flags_internal()

        return self.__auto_reload

    @property
    def root_identifier(self) -> Optional[str]:
        """
        Returns the root layer's identifier of the stage this prim belongs to.

        Returns:
            Optional[str]: The root layer identifier if stage exists else None
        """
        stage = self.stage
        return stage.GetRootLayer().identifier if stage else None

    @property
    def instance_proxy(self) -> bool:
        """
        Whether the prim is an instance proxy or not.

        Returns:
            bool: If the prim is an instance proxy
        """
        self._update_flags_internal()

        return self.__instance_proxy

    @property
    def instanceable(self) -> bool:
        """
        If the prim is instanceable.

        Returns:
            bool: Prim instanceable
        """
        self._update_flags_internal()

        return self.__instanceable

    @property
    def visible(self) -> bool:
        """
        If the prim is visible.

        Returns:
            bool: visibility
        """
        self._update_flags_internal()

        return self.__visible

    @property
    def payloads(self) -> bool:
        """
        Whether the prim has authored payloads.

        Returns:
            bool: If prim has authored payloads
        """
        self._update_flags_internal()

        return self.__has_payloads

    @property
    def references(self) -> bool:
        """
        Whether the prim has authored references.

        Returns:
            bool: If prim has authored references
        """
        self._update_flags_internal()

        return self.__has_references

    @property
    def inherits(self) -> bool:
        """
        Whether the prim has authored inherits.

        Returns:
            bool: If prim has authored inherits
        """
        self._update_flags_internal()

        return self.__has_inherits

    @property
    def specializes(self) -> bool:
        """
        Whether the prim has authored specializes.

        Returns:
            bool: If prim has authored specializes
        """
        self._update_flags_internal()

        return self.__has_specializes

    @property
    def name(self) -> str:
        """
        The Sdf path name.

        Returns:
            str
        """
        return self._path.name

    @property
    def display_name(self) -> str:
        """
        The display name of prim from the metadata. If not set, default to path name.

        Returns:
            str
        """
        self._update_flags_internal()

        return self.__display_name or self.name

    @property
    def prim(self) -> Usd.Prim:
        """
        The prim handle.

        Returns:
            Usd.Prim: The prim handle.
        """
        self._update_flags_internal()

        return self.__prim

    @property
    def active(self) -> bool:
        """
        If the prim is active. If no prim associated, return False.

        Returns:
            bool: prim active
        """
        self._update_flags_internal()

        if not self.__prim:
            return False

        return self.__prim.IsActive()
    
    @property
    def abstract(self) -> bool:
        """
        If the prim is abstract. If no prim associated, return False.

        Returns:
            bool: prim abstract
        """
        self._update_flags_internal()

        if not self.__prim:
            return False

        return self.__prim.IsAbstract()

    @property
    def type_name(self) -> str:
        """
        Type name of the prim. Return empty string if no prim associated.

        Returns:
            str: prim type name
        """
        self._update_flags_internal()

        prim = self.__prim
        if not prim:
            return ""

        return prim.GetTypeName()

    @property
    def is_class(self) -> bool:
        """
        If this prim is a Sdf.SpecifierClass. If no prim associated, return False.

        Returns:
            bool:
        """
        self._update_flags_internal()

        if not self.__prim:
            return False

        return self.__prim.GetSpecifier() == Sdf.SpecifierClass

    @property
    def has_missing_references(self) -> bool:
        """
        Whether the prim includes any missing references or payloads or not, checked recursively.

        Returns:
            bool: If any descendant of the prim has missing reference of payload.
        """
        self._update_flags_internal()

        return self.__missing_references

    @property
    def children(self):
        """
        Returns children items. If children are not populated yet, they will be populated.

        Returns:
            List[StageItem]: Child items.
        """
        return self.__stage_model.get_item_children(self)

    def update_flags(self, prim=None):
        """
        Refreshes item states from USD.

        Keyword Args:
            prim: Unused.
        """
        # Lazy load.
        self.__flags_updated = True

    def _update_prim(self):
        stage = self.stage
        self.__prim = stage.GetPrimAtPath(self._path) if stage else None

    def _update_visibility(self):
        prim = self.prim
        if prim and prim.IsA(UsdGeom.Imageable):
            visibility = UsdGeom.Imageable(prim).ComputeVisibility()
            self.__visible = visibility != UsdGeom.Tokens.invisible
        else:
            self.__visible = False

    def __get_payrefs(self):
        if not self.__has_references and not self.__has_payloads:
            return set()

        result = set()
        references = omni.usd.get_composed_references_from_prim(self.__prim)
        payloads = omni.usd.get_composed_payloads_from_prim(self.__prim)

        for reference, layer in payloads + references:
            if not reference.assetPath:
                continue

            absolute_path = layer.ComputeAbsolutePath(reference.assetPath)
            result.add(absolute_path)

        return result

    def __get_live_status(self):
        if not self.__stage_model.usd_context:
            return

        if self.__payrefs:
            live_syncing = layers.get_live_syncing(self.__stage_model.usd_context)
            for absolute_path in self.__payrefs:
                if live_syncing.is_prim_in_live_session(self.prim.GetPath(), absolute_path):
                    return True

        return False

    def __get_outdated_status(self):
        if not self.__stage_model.usd_context:
            return

        if self.__payrefs:
            layers_state_interface = layers.get_layers_state(self.__stage_model.usd_context)
            for absolute_path in self.__payrefs:
                if layers_state_interface.is_layer_outdated(absolute_path):
                    return True

        return False

    def __get_auto_reload_status(self):
        if not self.__stage_model.usd_context:
            return

        if carb.settings.get_settings().get_as_bool(layers.SETTINGS_AUTO_RELOAD_NON_SUBLAYERS):
            if not self.is_outdated:
                return True

        if self.__payrefs:
            layers_state_interface = layers.get_layers_state(self.__stage_model.usd_context)
            for absolute_path in self.__payrefs:
                if layers_state_interface.is_auto_reload_layer(absolute_path):
                    return True

        return False

    def __has_missing_payrefs(self):
        prim = self.prim
        # If prim is not loaded.
        if prim and not prim.IsLoaded():
            return False

        for identifier in self.payrefs:
            layer = Sdf.Find(identifier)
            if not layer:
                return True

        return False

    def _update_flags_internal(self):
        # Param is for back compitability.
        if not self.__flags_updated:
            return

        self.__flags_updated = False

        self._update_prim()
        prim = self.prim
        if not prim:
            return

        self.__is_default = prim == self.stage.GetDefaultPrim()
        self.__display_name = omni.usd.editor.get_display_name(prim) or ""
        # Refresh model to decide which name to display.
        if self.__name_model:
            self.__name_model.rebuild()
        self._update_visibility()
        self.__has_references = prim.HasAuthoredReferences()
        self.__has_payloads = prim.HasAuthoredPayloads()
        self.__has_inherits = prim.HasAuthoredInherits()
        self.__has_specializes = prim.HasAuthoredSpecializes()
        self.__payrefs = self.__get_payrefs()
        self.__instanceable = prim.IsInstanceable()
        self.__instance_proxy = prim.IsInstanceProxy()
        self.__missing_references = self.__has_missing_payrefs()
        self.__is_outdated = self.__get_outdated_status()
        self.__in_session = self.__get_live_status()
        self.__auto_reload = self.__get_auto_reload_status()

    def __repr__(self):
        return f"<Omni::UI Stage Item '{self._path}'>"

    def __str__(self):
        return f"{self._path}"

    # Internal properties
    @property
    def name_model(self) -> PrimNameModel:
        """
        The prim name model.

        Returns:
            PrimNameModel: The prim name model.
        """
        self._update_flags_internal()

        if not self.__name_model:
            self.__name_model = PrimNameModel(self)

        return self.__name_model

    @property
    def type_model(self) -> TypeModel:
        """
        The prim type model.

        Returns:
            TypeModel: The prim type model.
        """
        self._update_flags_internal()

        if not self.__type_model:
            self.__type_model = TypeModel(self)

        return self.__type_model

    @property
    def visibility_model(self) -> VisibilityModel:
        """
        The prim visibility model.

        Returns:
            TypeModel: The prim visibility model.
        """
        self._update_flags_internal()

        if not self.__visibility_model:
            self.__visibility_model = VisibilityModel(self)

        return self.__visibility_model

    @property
    def is_flat(self) -> bool:
        """
        If the stage model is in flat mode. If no stage model associated, returns False.

        Returns:
            bool: If the stage model is in flat mode
        """
        return self.__stage_model.flat if self.__stage_model else False

    @is_flat.setter
    def is_flat(self, flat: bool):
        """Unused."""
        # Rebuild it only when it's populated
        if self.__name_model:
            self.__name_model.rebuild()

    @property
    def load_payloads(self) -> bool:
        """
        Whether to load payloads. If no stage model associated, returns False.

        Returns:
            bool: Load payloads or not.
        """
        return self.stage_model.load_payloads if self.stage_model else None

    # Deprecated functions
    @property
    def check_missing_references(self):
        """Deprecated: It will always check missing references now."""

        return True

    @check_missing_references.setter
    def check_missing_references(self, value):
        """Deprecated."""
        pass

    def set_default_prim(self, is_default):
        """Deprecated."""
        pass
