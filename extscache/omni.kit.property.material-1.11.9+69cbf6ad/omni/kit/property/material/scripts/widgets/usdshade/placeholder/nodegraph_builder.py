# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from pxr import Sdf, Usd, UsdShade

from .builder_base import PropertiesBuilderBase
from .placeholder import UsdShadePropertyPlaceholder


class NodeGraphPropertiesBuilder(PropertiesBuilderBase):
    def __init__(self, prim: Usd.Prim, args: dict, schema: Usd.SchemaBase = UsdShade.NodeGraph):
        super().__init__(prim, args, schema)

    def _set_placeholder_metadata(self, placeholder: UsdShadePropertyPlaceholder) -> None:
        property_name = placeholder.GetName()
        if property_name.startswith(UsdShade.Tokens.inputs):  # pragma: no cover
            if not placeholder.GetDisplayGroup():
                placeholder.SetDisplayGroup("Inputs")

            if not placeholder.GetDisplayName():
                # display name is not set
                display_name = property_name.replace(UsdShade.Tokens.inputs, "", 1)
                placeholder.SetDisplayName(display_name)

            super()._set_placeholder_metadata(placeholder)

        elif property_name.startswith(UsdShade.Tokens.outputs):  # pragma: no cover
            placeholder.SetDisplayGroup("Outputs")

            display_name = property_name.split(Sdf.Path.namespaceDelimiter)[-1]
            placeholder.SetDisplayName(display_name)

        # Nodegraphs in older scene files might have a ui:description property, so move it into Description
        # Note, ui:description is not a valid UsdUI.NodeGraphNodeAPI schema attribute.
        elif property_name == "ui:description":
            placeholder.SetDisplayName("Description")
            placeholder.SetDisplayGroup("Description")

        else:
            super()._set_placeholder_metadata(placeholder)
