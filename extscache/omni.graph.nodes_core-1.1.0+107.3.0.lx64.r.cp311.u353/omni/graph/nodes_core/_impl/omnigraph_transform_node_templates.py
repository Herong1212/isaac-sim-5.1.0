# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.graph.core as og
import omni.ui as ui
from omni.graph.ui._impl.omnigraph_attribute_builder import OmniGraphPropertiesWidgetBuilder  # noqa: PLE0402
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry

ATTRIB_LABEL_STYLE = {"alignment": ui.Alignment.RIGHT_TOP}


class RotationNodeCustomLayoutBase:
    """Custom layout for transform nodes with rotation order
    Deactivates rotationOrder based on input tuple count.
    """

    # Set the prim rel name to customize
    _rotation_attr_name = "inputs:rotation"

    def __init__(self, compute_node_widget):
        self.enable = True
        self.compute_node_widget = compute_node_widget
        self.ATTRIB_LABEL_STYLE = ATTRIB_LABEL_STYLE
        self.node_prim_path = compute_node_widget._payload[-1]  # noqa: PLW0212
        self.stage = compute_node_widget.stage
        self.rotation_widget = None
        self.rotation_order_widget = None

    def _get_rotation_tuple_count(self) -> int:
        # Gets the value of the usePath input attribute
        if self.stage.GetPrimAtPath(self.node_prim_path):
            attr = og.Controller.attribute(f"{self.node_prim_path}.{self._rotation_attr_name}")
            attr_type = attr.get_resolved_type()
            if attr_type.base_type != og.BaseDataType.UNKNOWN:
                return attr_type.tuple_count
        return 0

    def _rotation_order_build_fn(self, ui_prop: UsdPropertyUiEntry, *args):
        ui_prop.override_display_name("Rotation Order")
        enable_widget = self._get_rotation_tuple_count() == 3
        self.rotation_order_widget = OmniGraphPropertiesWidgetBuilder.build(
            self.stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [self.node_prim_path],
            {"enabled": enable_widget, "style": ATTRIB_LABEL_STYLE},
            {"enabled": enable_widget},
        )
        return self.rotation_order_widget
