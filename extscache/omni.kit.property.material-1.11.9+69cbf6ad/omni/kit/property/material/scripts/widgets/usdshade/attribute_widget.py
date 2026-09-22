# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides a custom widget for displaying UsdShade attributes in the Raw Properties widget, specifically modifying the display metadata to present a flat list of properties."""

__all__ = ["UsdShadeAttributeWidget"]

from typing import List

from omni.kit.property.usd.usd_property_widget import RawUsdPropertiesWidget, UsdPropertyUiEntry
from pxr import Sdf, UsdShade


class UsdShadeAttributeWidget(RawUsdPropertiesWidget):
    """A widget that overrides the display of UsdShade attributes in the Raw Properties widget.

    This widget modifies the UsdPropertyUiEntry instances to remove the display[Name|Group] metadata, resulting in a flat list presentation of the properties without pagination.
    """

    def _customize_props_layout(self, props: List[UsdPropertyUiEntry]) -> List[UsdPropertyUiEntry]:
        """
        If prims are UsdShade then remove:
            1. display name - so the true property name is shown.
            2. display group - so properties are shown unpaginated.
        """

        prims_are_usdshade = self._payload and all(
            (prim.IsA(UsdShade.NodeGraph) or prim.IsA(UsdShade.Shader))
            for prim in [self._get_prim(prim_path) for prim_path in self._payload]
        )

        if not prims_are_usdshade:
            return super()._customize_props_layout(props)

        customized = props.copy()

        for prop in customized:
            metadata = prop.metadata

            if Sdf.PropertySpec.DisplayNameKey in metadata:
                del metadata[Sdf.PropertySpec.DisplayNameKey]

            prop.override_display_group("")

        customized.sort(key=lambda x: x.prop_name)
        return super()._customize_props_layout(customized)
