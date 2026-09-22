# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides the SetUsdShadeInfoAttributeCommand class for changing property values of UsdShade info attributes and handling related property and connection updates."""


__all__ = [
    "SetUsdShadeInfoAttributeCommand",
]

from typing import Any, Union

import omni.kit.commands
import omni.usd
from omni.usd.commands import ChangePropertyCommand
from pxr import Sdf, Usd

from ..widgets import remove_properties_and_connections


class SetUsdShadeInfoAttributeCommand(ChangePropertyCommand):  # pragma: no cover
    """Change property value for UsdShade info.* attributes.

    In addition to what is done by ChangePropertyCommand, this command processes the UsdShade network and does the following:
    1. Remove any properties that no longer exist or whose types have changed.
    2. Remove any connections to/from this node that are no longer valid due to property removal or type change.

    Args:
        prop_path (str): The property path.
        value (Any): The new value to set.
        prev (Any): The previous value.
        timecode (Optional[Usd.TimeCode]): The timecode at which the change should happen.
        type_to_create_if_not_exist (Optional[:obj:`Sdf.ValueTypeNames`]): The type to create if it does not exist.
        target_layer (Optional[:obj:`Sdf.Layer`]): The target layer for the change.
        usd_context_name (Union[str, :obj:`omni.usd.UsdContext`, :obj:`Usd.Stage`]): The USD context name or stage.
        is_custom (bool): Specifies if the attribute is custom.
        variability (Optional[:obj:`Sdf.Variability`]): The variability of the attribute."""

    def __init__(
        self,
        prop_path: str,
        value: Any,
        prev: Any,
        timecode=None,
        type_to_create_if_not_exist: Sdf.ValueTypeNames = None,
        target_layer: Sdf.Layer = None,
        usd_context_name: Union[str, omni.usd.UsdContext, Usd.Stage] = "",
        is_custom: bool = False,
        variability: Sdf.Variability = Sdf.VariabilityVarying,
    ):
        """Initialize the command to set USD Shade info attribute values."""
        super().__init__(
            prop_path,
            value,
            prev,
            timecode=timecode or Usd.TimeCode.Default(),
            type_to_create_if_not_exist=type_to_create_if_not_exist,
            target_layer=target_layer,
            usd_context_name=usd_context_name,
            is_custom=is_custom,
            variability=variability,
        )

        self._properties_to_restore = []
        self._connections_to_restore = {}

    def _set_prop_value(self) -> bool:
        super()._set_prop_value()
        (res, self._properties_to_restore, self._connections_to_restore) = remove_properties_and_connections(self._prim)
        return res

    def undo(self):
        """Revert the changes made by the command."""

        def flatten_dict(d, parent_key=""):
            return {
                f"{parent_key}{Sdf.Path.namespaceDelimiter}{k}" if parent_key else k: v
                for kk, vv in d.items()
                for k, v in (
                    flatten_dict(vv, f"{parent_key}{Sdf.Path.namespaceDelimiter}{kk}" if parent_key else kk)
                    if isinstance(vv, dict)
                    else {kk: vv}
                ).items()
            }

        super().undo()

        (res, _properties_to_restore, _connections_to_restore) = remove_properties_and_connections(self._prim)
        if not res:
            return

        # restore properties
        for property_info in self._properties_to_restore:
            attr = self._prim.CreateAttribute(
                property_info["path"].name,
                property_info["type_name"],
                property_info["custom"],
                property_info["variability"],
            )

            if property_info["value"]:
                attr.Set(property_info["value"])

            attr.SetConnections(property_info["connections"])

            property_metadata = property_info.get("metadata", {})
            for k, v in property_metadata.items():
                if k == Sdf.AttributeSpec.CustomDataKey:
                    attr.SetCustomData(v)

                elif isinstance(v, dict):
                    for kk, vv in flatten_dict(v).items():
                        attr.SetMetadataByDictKey(k, kk, vv)

                else:
                    attr.SetMetadata(k, v)

        # restore connections
        for usdshade_port, connected_sources in self._connections_to_restore.items():
            usdshade_port.SetConnectedSources(connected_sources)
