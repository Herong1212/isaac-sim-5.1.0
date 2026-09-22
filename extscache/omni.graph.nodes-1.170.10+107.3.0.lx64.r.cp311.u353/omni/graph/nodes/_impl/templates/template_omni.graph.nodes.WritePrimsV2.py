# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import Dict, List, Mapping, Type

from omni.graph.ui import (
    LayerIdentifierWidgetBuilder,
    LayerModel,
    OmniGraphAttributeModel,
    OmniGraphPropertiesWidgetBuilder,
)
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from pxr import Sdf, Usd


class CustomLayout:
    """Custom layout for WritePrims node
    - dynamic output attributes are given 'nice' ui names
    """

    def __init__(self, compute_node_widget):
        self.enable = True
        self._compute_node_widget = compute_node_widget
        self._usd_write_back_model = None

    def apply(self, props):
        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                # put prims at the top
                CustomLayoutProperty("inputs:prims")
                for p in props:
                    if not p.prop_name.startswith("inputs:"):
                        continue

                    if p.prop_name == "inputs:prims":
                        continue

                    if p.prop_name == "inputs:primsBundle":
                        continue

                    if p.prop_name == "inputs:execIn":
                        continue

                    if p.prop_name == "inputs:layerIdentifier":  # will be built later at the end
                        continue

                    if p.prop_name == "inputs:usdWriteBack":
                        self._usd_write_back_build_widget()
                    else:
                        CustomLayoutProperty(p.prop_name)

                self._build_layer_identifier_widget()

        return frame.apply(props)

    def _usd_write_back_build_widget(self):
        def build(
            stage: Usd.Stage,
            attr_name: str,
            metadata: Mapping,
            property_type: Type,
            prim_paths: List[Sdf.Path],
            additional_label_kwargs: Dict = None,
            additional_widget_kwargs: Dict = None,
        ) -> OmniGraphAttributeModel:
            self._usd_write_back_model = OmniGraphPropertiesWidgetBuilder.build(
                stage, attr_name, metadata, property_type, prim_paths, additional_label_kwargs, additional_widget_kwargs
            )
            self._usd_write_back_model.add_value_changed_fn(lambda *_: self._compute_node_widget.request_rebuild())
            return self._usd_write_back_model

        CustomLayoutProperty("inputs:usdWriteBack", build_fn=build)

    def _build_layer_identifier_widget(self):
        def build(
            stage: Usd.Stage,
            attr_name: str,
            metadata: Mapping,
            property_type: Type,
            prim_paths: List[Sdf.Path],
            additional_label_kwargs: Dict,
            additional_widget_kwargs: Dict,
        ) -> LayerModel:
            label_kwargs = {"enabled": self._usd_write_back_model.as_bool}
            if additional_label_kwargs:
                label_kwargs.update(additional_label_kwargs)

            widget_kwargs = {"enabled": self._usd_write_back_model.as_bool}
            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)

            return LayerIdentifierWidgetBuilder.build(
                stage, attr_name, metadata, property_type, prim_paths, label_kwargs, widget_kwargs
            )

        CustomLayoutProperty("inputs:layerIdentifier", build_fn=build)

    def _on_usd_write_back_changed(self, _):
        self._compute_node_widget.request_rebuild()
