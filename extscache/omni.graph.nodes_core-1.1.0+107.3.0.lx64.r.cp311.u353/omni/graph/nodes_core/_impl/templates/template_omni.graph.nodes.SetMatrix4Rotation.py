# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from functools import partial

import omni.graph.core as og
import omni.graph.ui as ogui
from omni.graph.nodes_core._impl.omnigraph_transform_node_templates import RotationNodeCustomLayoutBase
from omni.graph.ui import OmniGraphPropertiesWidgetBuilder
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry


class CustomLayout(RotationNodeCustomLayoutBase):
    """Custom layout for SetMatrix4Rotation node
    Reorganizes inputs for readability and deactivates rotationAxis / rotationOrder / fixedRotationAxis
    based on rotationAngle.
    """

    _rotation_attr_name = "inputs:rotationAngle"

    def __init__(self, compute_node_widget):
        super().__init__(compute_node_widget)
        self.rotation_axis_model = None
        self.custom_axis_model = None

    def _get_rotation_axis(self) -> str:
        # Gets the value of the usePath input attribute
        if self.stage.GetPrimAtPath(self.node_prim_path):
            attr = og.Controller.attribute(f"{self.node_prim_path}.inputs:fixedRotationAxis")
            return attr.get()
        return ""

    def apply(self, props):
        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop = ogui.find_prop(props, "inputs:matrix")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Matrix")

                prop = ogui.find_prop(props, "inputs:rotationAngle")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Rotation")

                prop = ogui.find_prop(props, "inputs:rotationOrder")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._rotation_order_build_fn, prop))

                prop = ogui.find_prop(props, "inputs:fixedRotationAxis")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._rotation_axis_build_fn, prop))

                prop = ogui.find_prop(props, "inputs:rotationAxis")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._custom_rotation_axis_build_fn, prop))

            with CustomLayoutGroup("Outputs"):
                prop = ogui.find_prop(props, "outputs:matrix")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Prims")
        return frame.apply(props)

    def _rotation_axis_changed(self, *args):
        # When the fixedRotationAxis attribute changes
        # Only update if we don't have upstream connections to avoid continuously refreshing
        if not self.rotation_axis_model.has_connections():
            self.compute_node_widget.request_rebuild()

    def _rotation_axis_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        ui_prop.override_display_name("Rotation Axis")
        enable_widget = self._get_rotation_tuple_count() == 1
        self.rotation_axis_model = OmniGraphPropertiesWidgetBuilder.build(
            self.stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [self.node_prim_path],
            {"enabled": enable_widget, "style": self.ATTRIB_LABEL_STYLE},
            {"enabled": enable_widget},
        )
        self.rotation_axis_model.add_item_changed_fn(self._rotation_axis_changed)
        return self.rotation_axis_model

    def _custom_rotation_axis_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        ui_prop.override_display_name("Custom Rotation Axis")
        enable_widget = (self._get_rotation_tuple_count() == 1) and (self._get_rotation_axis() == "Custom")
        self.custom_axis_model = OmniGraphPropertiesWidgetBuilder.build(
            self.stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [self.node_prim_path],
            {"enabled": enable_widget, "style": self.ATTRIB_LABEL_STYLE},
            {"enabled": enable_widget},
        )
        return self.custom_axis_model
