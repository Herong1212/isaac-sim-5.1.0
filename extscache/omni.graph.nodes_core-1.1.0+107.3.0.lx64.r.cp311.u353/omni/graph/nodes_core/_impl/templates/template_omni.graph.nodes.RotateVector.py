# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from functools import partial

import omni.graph.ui as ogui
from omni.graph.nodes_core._impl.omnigraph_transform_node_templates import RotationNodeCustomLayoutBase
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty


class CustomLayout(RotationNodeCustomLayoutBase):
    """Custom layout for RotateVector node
    - inputs:rotationOrder is disabled when inputs:rotation is not a vector3.
    """

    _rotation_attr_name = "inputs:rotation"

    def apply(self, props):
        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop = ogui.find_prop(props, "inputs:rotation")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Rotation")

                prop = ogui.find_prop(props, "inputs:rotationOrder")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._rotation_order_build_fn, prop))

                prop = ogui.find_prop(props, "inputs:vector")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Vector")

            with CustomLayoutGroup("Outputs"):
                prop = ogui.find_prop(props, "outputs:result")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Result")
        return frame.apply(props)
