# Copyright (c) 2021-2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from functools import partial

import omni.graph.ui as ogui
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry


class CustomLayout(ogui.PrimAttributeCustomLayoutBase):
    def apply(self, props):
        # Called by compute_node_widget to apply UI when selection changes
        def find_prop(name):
            try:
                return next((p for p in props if p.prop_name == name))
            except StopIteration:
                return None

        def build_fn_for_value(prop: UsdPropertyUiEntry):
            def build_fn(*args):
                # The resolved attribute is procedural and does not inherit the meta-data of the extended attribute
                # so we need to manually set the display name
                prop.override_display_name("Value")
                self.compute_node_widget.build_property_item(
                    self.compute_node_widget.stage, prop, self.compute_node_widget._payload  # noqa: PLW0212
                )

            return build_fn

        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop = find_prop("inputs:prim")
                CustomLayoutProperty(None, None, build_fn=partial(self._prim_rel_build_fn, prop))
                prop = find_prop("inputs:name")
                CustomLayoutProperty(None, None, build_fn=partial(self._name_attrib_build_fn, prop))

                prop = find_prop("inputs:usePath")
                CustomLayoutProperty(None, None, build_fn=partial(self._use_path_build_fn, prop))

                prop = find_prop("inputs:primPath")
                CustomLayoutProperty(None, None, build_fn=partial(self._prim_path_build_fn, prop))

                prop = find_prop("inputs:firstElement")
                CustomLayoutProperty(prop.prop_name, "First Element")

                prop = find_prop("inputs:rangeSize")
                CustomLayoutProperty(prop.prop_name, "Range Size")

            with CustomLayoutGroup("Outputs"):
                prop = find_prop("outputs:value")
                CustomLayoutProperty(None, None, build_fn=build_fn_for_value(prop))

                prop = find_prop("outputs:inputArraySize")
                CustomLayoutProperty(prop.prop_name, "Input Array Size")

        return frame.apply(props)
