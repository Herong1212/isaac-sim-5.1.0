# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides the UsdUIBackdropWidget class, which is a specialized USD properties widget for interacting with USD UI Backdrop elements within a properties panel."""


from typing import List

import carb
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget, UsdPropertyUiEntry
from pxr import UsdUI

from .usdshade import property_name_to_display_name


class UsdUIBackdropWidget(UsdPropertiesWidget):
    """A widget representing a USD UI Backdrop within a properties panel.

    This widget extends the UsdPropertiesWidget to specifically handle the display and
    interaction with USD UI Backdrop elements. It provides a custom property layout
    and integrates with the material adapter settings. The widget is initialized
    with a title and configures itself based on the application settings.

    Args:
        title (str): The title of the backdrop widget. Defaults to 'Backdrop'."""

    MATERIAL_ADAPTER_SETTING_PATH = "/ext/omni.kit.property.material/enableAdapter"
    """str: Path to material adapter settings."""

    def __init__(self, title: str = "Backdrop"):
        """Initializes the backdrop widget with optional title."""
        settings = carb.settings.get_settings()
        enable_adapter = settings.get_as_bool(self.MATERIAL_ADAPTER_SETTING_PATH) or False

        super().__init__(title, False, enable_adapter=enable_adapter)

    def on_new_payload(self, payload: PrimSelectionPayload) -> bool:
        """Handles a new payload for the widget.

        Args:
            payload (:obj:`PrimSelectionPayload`): The new payload to be handled by the widget.

        Returns:
            bool: True if the payload is processed successfully, otherwise False."""
        if not (payload and super().on_new_payload(payload)):
            return False

        for prim_path in self._payload:
            prim = self._get_prim(prim_path)

            if not (prim and prim.IsA(UsdUI.Backdrop)):
                return False

        return True  # pragma: no cover

    def _customize_props_layout(self, props: List[UsdPropertyUiEntry]) -> List[UsdPropertyUiEntry]:
        properties = super()._customize_props_layout(props)

        for ui_prop in properties:
            if ui_prop.prop_name.startswith("ui"):
                ui_prop.override_display_group("UI Properties")
                display_name = property_name_to_display_name(ui_prop.prop_name)
                ui_prop.override_display_name(display_name)
                ui_prop.display_group_collapsed = False

        return properties
