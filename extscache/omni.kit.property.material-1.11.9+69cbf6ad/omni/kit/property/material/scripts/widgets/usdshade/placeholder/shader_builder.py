# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from pxr import Sdf, Usd, UsdShade

from ..utils import (
    get_info_ids_for_prim,
    get_mdl_subidentifiers_for_prim,
    get_shader_info,
    property_name_to_display_name,
)
from .builder_base import PropertiesBuilderBase
from .placeholder import UsdShadePropertyPlaceholder


class ShaderPropertiesBuilder(PropertiesBuilderBase):
    def __init__(self, prim: Usd.Prim, args: dict):
        super().__init__(prim, args, UsdShade.Shader)

    def _gather_properties(self) -> None:
        """
        Query the Sdr.ShaderNode that is associated with this prim to obtain:
            1. node level properties, e.g. description.
            2. input and output properties.
        """
        info = get_shader_info(UsdShade.Shader(self._prim))
        if (info[0] == UsdShade.Tokens.sourceAsset) and not (info[1] and info[2]):
            super()._append_prim_properties()
            return

        super()._gather_properties()

        if UsdShade.NodeDefAPI(self._prim).GetShaderId() == "UsdPreviewSurface":
            self._fix_usdpreview_surface_outputs()

    def _fix_usdpreview_surface_outputs(self):
        """
        Special case for UsdPreviewSurface.
        The Sdr returns a single output "out", however the spec defines 2 outputs: surface and displacement.
        """

        # ToDo: see if we could solve this by using annotation metadata is UsdPreviewSurface.mdl.
        preview_surface_outputs = [f"{UsdShade.Tokens.outputs}surface", f"{UsdShade.Tokens.outputs}displacement"]

        for p in self._placeholder_properties:
            name = p.GetName()
            if name in preview_surface_outputs:
                p.SetDisplayGroup("Outputs")
                self._output_properties[name] = p

        out = f"{UsdShade.Tokens.outputs}out"
        self._placeholder_properties = [p for p in self._placeholder_properties if p.GetName() != out]

    def _set_placeholder_metadata(self, placeholder: UsdShadePropertyPlaceholder) -> None:
        """
        If the property name starts with "info:", set the displayName and displayGroup metadata.
        Otherwise pass this up to parent class for handling.
        """

        def set_display_group(
            property_name: str, placeholder: UsdShadePropertyPlaceholder, placeholders: dict, prefix: str
        ) -> None:
            if property_name not in placeholders:
                placeholder.SetDisplayGroup("")

            else:
                display_group = placeholder.GetDisplayGroup()

                if not display_group:
                    placeholder.SetDisplayGroup(prefix)

                elif not display_group.startswith(f"{prefix}"):
                    placeholder.SetDisplayGroup(f"{prefix}{Sdf.Path.namespaceDelimiter}{display_group}")

        property_name = placeholder.GetName()

        if property_name.startswith("info:"):
            hidden = True
            allowed_tokens = []

            if property_name == UsdShade.Tokens.infoImplementationSource:
                hidden = False

            else:
                implementation_source = UsdShade.Shader(self._prim).GetImplementationSource()

                if implementation_source == UsdShade.Tokens.id:
                    hidden = property_name != UsdShade.Tokens.infoId

                elif implementation_source == UsdShade.Tokens.sourceAsset:
                    hidden = UsdShade.Tokens.sourceAsset not in property_name

            if property_name.endswith(UsdShade.Tokens.infoId):
                display_name = "ID"
                allowed_tokens = get_info_ids_for_prim(self._prim)

            elif property_name.endswith(UsdShade.Tokens.sourceAsset):
                display_name = "MDL Source Asset"

            elif property_name.endswith(UsdShade.Tokens.subIdentifier):
                display_name = "MDL Subidentifier"
                allowed_tokens = get_mdl_subidentifiers_for_prim(self._prim)

            else:
                display_name = property_name_to_display_name(property_name)

            placeholder.SetDisplayGroup("Info")
            placeholder.SetDisplayName(display_name)
            placeholder.SetHidden(hidden)

            if allowed_tokens:
                placeholder.SetMetadata("allowedTokens", allowed_tokens)

        elif property_name.startswith(UsdShade.Tokens.inputs):
            set_display_group(property_name, placeholder, self._input_properties, "Inputs")

        elif property_name.startswith(UsdShade.Tokens.outputs):
            set_display_group(property_name, placeholder, self._output_properties, "Outputs")

        else:
            super()._set_placeholder_metadata(placeholder)
