# Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from functools import partial

import omni.ui as ui
import omni.usd
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidgetBuilder
from omni.kit.window.property.templates import HORIZONTAL_SPACING
from pxr import Sdf

from .base_properties_widget import BasePropertiesWidget
from .timesample_editor import TimeSampleEditor


class TimeSamplePropertiesWidget(BasePropertiesWidget):
    """
    Adds Edit button to the property attribute which can contain timeSamples metadata.

    Args:
        element_type: prim typename.
        attribute_names: list of attribute names.

    Usage (registration from different extension):
        from omni.vdb_timesample_editor import TimeSamplePropertiesWidget
        self.emitter_timesample_widget = TimeSamplePropertiesWidget(
            "FlowEmitterNanoVdb",
            ["nanoVdbSmokes:assetPath", "nanoVdbTemperatures:assetPath"]
        )
    """

    def __init__(self, element_type, attribute_names):
        super().__init__("Time Samples", element_type)

        self._attribute_names = attribute_names

    def _open_window(self, attr):
        editor = TimeSampleEditor()
        editor.show(attr.GetPath())

    def _build_attribute(self, attr_name):
        stage = omni.usd.get_context().get_stage()
        prim = self.get_prim()
        attr = prim.GetAttribute(attr_name)
        if attr:
            with ui.HStack(spacing=HORIZONTAL_SPACING):
                with ui.VStack():
                    self.value_widget = UsdPropertiesWidgetBuilder._sdf_asset_path_builder(
                        stage,
                        attr_name,
                        Sdf.ValueTypeNames.Asset,
                        {},
                        [prim.GetPath()],
                    )
                ui.Button(
                    "Edit", tooltip="Edit Time Samples Metadata", width=30, clicked_fn=partial(self._open_window, attr)
                )

    def build_properties(self):
        for attr_name in self._attribute_names:
            self._build_attribute(attr_name)
