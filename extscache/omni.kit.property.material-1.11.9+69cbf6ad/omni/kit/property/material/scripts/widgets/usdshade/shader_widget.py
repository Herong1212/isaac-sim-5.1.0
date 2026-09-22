# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides a UsdShadeShaderWidget class for representing and interacting with USD Shade shaders in a user interface."""

__all__ = ["UsdShadeShaderWidget"]

import omni.kit.commands
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
from pxr import Sdf, UsdShade

from .base_widget import UsdShadeBaseWidget


class UsdShadeShaderWidget(UsdShadeBaseWidget):
    """A widget class for representing and interacting with USD Shade shaders.

    This widget is specifically designed for working with shading elements within a USD scene. It extends the capabilities of the UsdShadeBaseWidget to provide a user interface component that allows for the selection and manipulation of Shader prims. The widget can be titled for context within the UI.

    Args:
        title (str): The title of the shader widget. Defaults to 'Shader'."""

    def __init__(self, title: str = "Shader"):
        """Initializes the UsdShadeShaderWidget."""
        super().__init__(UsdShade.Shader, title)

    def _on_info_property_changed(self, changed_property_name: str) -> None:
        """
        If 'info:mdl:sourceAsset' property has changed, clear 'info:mdl:sourceAsset:subIdentifier'
        """

        if changed_property_name == "info:mdl:sourceAsset":
            stage = self._payload.get_stage()

            for prim_path in self._shader_prim_paths:
                prop_path = prim_path.AppendProperty("info:mdl:sourceAsset:subIdentifier")
                attribute = stage.GetAttributeAtPath(prop_path)

                omni.kit.commands.execute(
                    "ChangePropertyCommand",
                    prop_path=prop_path,
                    type_to_create_if_not_exist=Sdf.ValueTypeNames.Token,
                    value="",
                    prev=(attribute.Get() if attribute else ""),
                )

    def _path_requires_rebuild(self, path: Sdf.Path) -> bool:
        """
        If one of the info: attributes has changed, we will force a rebuild of the widget.
        """
        if path.name.startswith("info:"):
            self._on_info_property_changed(path.name)
            return True

        return super()._path_requires_rebuild(path)

    def on_new_payload(self, payload: PrimSelectionPayload) -> bool:
        """Processes the given payload and updates the shader widget if necessary.

        Args:
            payload (:obj:`PrimSelectionPayload`): The payload containing prims to represent.

        Returns:
            bool: True if the prims can be represented, False otherwise."""

        if not super().on_new_payload(payload):
            return False

        for prim_path in payload:
            self._shader_prim_paths.append(prim_path)

        # Load any modules needed to draw this widget
        self._load_mdl_modules()

        return True
