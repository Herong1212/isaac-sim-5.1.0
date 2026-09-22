# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import List, Optional

import carb
from pxr import Sdf, Usd, UsdShade, UsdUI

from ..utils import property_name_to_display_name
from .placeholder import UsdShadePropertyPlaceholder
from .shader_info_api import ShaderInfoAPI


class PropertiesBuilderBase:
    """
    This class and it's derived classes provide the means to collect and return UsdShadePropertyPlaceholder's
    for each property on the underlying prim.
    """

    def __init__(self, prim: Usd.Prim, args: dict, schema: Usd.SchemaBase):
        self._prim = prim
        self._args = args
        self._schema = schema
        self._prim_path = prim.GetPath()
        self._placeholder_properties = []
        self._valid = prim.IsA(self._schema)
        self._input_properties = {}
        self._output_properties = {}

        if not self._valid:  # pragma: no cover
            carb.log_error(f"Expected '{self._schema}' prim at: '{self._prim_path}'")

        overlay_property_metadata = self._args.get("overlay_property_metadata", True)
        self._api = ShaderInfoAPI(self._prim, overlay_property_metadata)

    def build(self) -> List[UsdShadePropertyPlaceholder]:
        """
        Build and return the list of UsdShadePropertyPlaceholder's for this prim.
        Populate enable_if_properties with any properties that drive the enable_if evaluation for sibling properties.
        """
        self._placeholder_properties.clear()

        if self._valid:
            self._gather_properties()

            self._sort_by_property_order(self._prim)

            for placeholder in self._placeholder_properties:
                self._set_placeholder_metadata(placeholder)

        return self._placeholder_properties

    def _gather_properties(self) -> None:
        """
        Collect the UsdShadePropertyPlaceholder's for this prim.
        """

        self._placeholder_properties.extend(self._api.get_node_properties())

        inputs = self._api.get_input_properties()
        self._placeholder_properties.extend(inputs)
        self._input_properties = {p.GetName(): p for p in inputs}

        # The UsdShade.Material prim outputs are added in MaterialPropertiesBuilder._append_prim_properties()
        if self._schema != UsdShade.Material:
            outputs = self._api.get_output_properties()
            self._placeholder_properties.extend(outputs)
            self._output_properties = {p.GetName(): p for p in outputs}

        self._append_prim_properties()

    def _sort_by_property_order(
        self, prim: Usd.Prim, placeholder_properties: Optional[List[UsdShadePropertyPlaceholder]] = None
    ) -> None:
        """
        Sort properties according to prim property order metadata.
        """

        property_order = prim.GetPropertyOrder()
        if property_order:
            if placeholder_properties is None:
                placeholder_properties = self._placeholder_properties

            end = len(placeholder_properties)
            placeholder_properties.sort(
                key=lambda prop: (property_order.index(prop.GetName()) if prop.GetName() in property_order else end)
            )

    def _create_placeholder(self, prop: Usd.Property) -> UsdShadePropertyPlaceholder:
        """
        Create a UsdShadePropertyPlaceholder from a Usd.Property
        """

        placeholder = UsdShadePropertyPlaceholder(prop.GetName(), prop.GetAllMetadata())
        self._set_placeholder_metadata(placeholder)
        return placeholder

    def _append_prim_properties(self) -> None:
        """
        Create UsdShadePropertyPlaceholder's for those properties on the prim for which we haven't already done so.
        """

        placeholder_property_names = [p.GetName() for p in self._placeholder_properties]
        prim_properties = [p for p in self._prim.GetProperties() if p.GetName() not in placeholder_property_names]
        self._placeholder_properties.extend([self._create_placeholder(prop) for prop in prim_properties])

    def _add_colorspace_metadata(self, property_name: str, placeholder: UsdShadePropertyPlaceholder) -> None:
        """
        Determine if we need to add colorspace metadata.
        """
        if (
            placeholder.FromSdr()
            or (placeholder.GetTypeName() != Sdf.ValueTypeNames.Asset)
            or placeholder.GetColorSpace()
        ):
            return

        placeholder.SetColorSpace("auto")

    def _set_placeholder_metadata(self, placeholder: UsdShadePropertyPlaceholder) -> None:
        """
        Set display[name|group] metadata for ui:* properties
        """

        property_name = placeholder.GetName()

        # older scenes may contain data that is munged into the ui properties if this is the case then ignore.
        if property_name.startswith("ui:") and property_name in UsdUI.NodeGraphNodeAPI.GetSchemaAttributeNames():
            display_name = property_name_to_display_name(property_name)
            placeholder.SetDisplayName(display_name)
            placeholder.SetDisplayGroup("UI Properties")

        elif property_name.startswith(UsdShade.Tokens.inputs):
            self._add_colorspace_metadata(property_name, placeholder)
