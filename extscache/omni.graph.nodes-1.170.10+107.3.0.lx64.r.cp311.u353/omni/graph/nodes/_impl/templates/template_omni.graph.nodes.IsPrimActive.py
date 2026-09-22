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
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty


class CustomLayout(ogui.PrimPathCustomLayoutBase):
    """Custom layout for IsPrimActive node
    - inputs:prim is disabled when inputs:primTarget targets a prim.
    """

    _prim_rel_name = "inputs:primTarget"

    def apply(self, props):
        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop = self._find_prop(props, "inputs:primTarget")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._prim_build_fn, prop))
                    prop.override_display_name("Prim")

                prop = self._find_prop(props, "inputs:prim")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._prim_path_build_fn, prop))
                    prop.override_display_name("Prim Path")

            with CustomLayoutGroup("Outputs"):
                prop = self._find_prop(props, "outputs:active")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Active")

        return frame.apply(props)
