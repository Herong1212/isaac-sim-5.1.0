# Copyright (c) 2022-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.graph.core as og
from omni.graph.nodes.scripts.ui_utils import (
    _build_add_remove_buttons,
    _get_string_permutation,
    _retrieve_existing_alphabetic_dynamic_inputs,
)
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty

DYN_ATTRIBUTE_FORMAT = "inputs:"
MIN_INPUT_COUNT = 2


class CustomLayout:
    def __init__(self, compute_node_widget):
        self.enable = True
        self.compute_node_widget = compute_node_widget
        self.controller = og.Controller()
        self.add_button = None
        self.remove_button = None
        self.node_prim_path = self.compute_node_widget._payload[-1]
        self.node = self.controller.node(self.node_prim_path)
        self._retrieve_existing_inputs = _retrieve_existing_alphabetic_dynamic_inputs

    def _on_click_add(self):
        (input_attribs, _) = self._retrieve_existing_inputs(self.node)
        new_attrib_count = len(input_attribs) + 1
        self._resize_input_array(new_attrib_count)

    def _on_click_remove(self):
        (input_attribs, _) = self._retrieve_existing_inputs(self.node)
        if not input_attribs:
            return

        # Decrement the array size to trigger the removal of the last attribute
        new_attrib_count = len(input_attribs) - 1
        if new_attrib_count >= MIN_INPUT_COUNT:
            self._resize_input_array(new_attrib_count)

    def _resize_input_array(self, new_count: int):
        """Resize the input array

        Args:
            new_count: The new array size"""
        (input_attribs, largest_suffix) = self._retrieve_existing_inputs(self.node)
        current_attrib_count = len(input_attribs)
        if new_count > current_attrib_count:
            numerics_list = og.AttributeType.get_unions()["numerics"]
            create_count = new_count - current_attrib_count
            while create_count > 0:
                create_count = create_count - 1
                largest_suffix = largest_suffix + 1
                self.controller.create_attribute(
                    self.node,
                    DYN_ATTRIBUTE_FORMAT + _get_string_permutation(largest_suffix),
                    "[" + ",".join(numerics_list) + "]",
                    og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
                    None,
                    (og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION, numerics_list),
                )
        else:
            remove_count = current_attrib_count - new_count
            while remove_count > 0:
                attrib_to_remove = self.node.get_attribute(
                    f"{DYN_ATTRIBUTE_FORMAT}{_get_string_permutation(largest_suffix)}"
                )
                try:
                    self.controller.remove_attribute(attrib_to_remove)
                except og.OmniGraphError:
                    return
                largest_suffix = largest_suffix - 1
                remove_count = remove_count - 1

    def _controls_build_fn(self, *args):
        def _remove_button_enabled() -> bool:
            (input_attribs, _) = self._retrieve_existing_inputs(self.node)
            return len(input_attribs) > MIN_INPUT_COUNT

        _build_add_remove_buttons(self, self._on_click_add, self._on_click_remove, _remove_button_enabled)

    def apply(self, props):
        # Called by compute_node_widget to apply UI when selection changes
        def find_prop(name):
            return next((p for p in props if p.prop_name == name), None)

        frame = CustomLayoutFrame(hide_extra=True)
        (input_attribs, _) = self._retrieve_existing_inputs(self.node)
        with frame:
            with CustomLayoutGroup("Inputs"):
                for attrib in input_attribs:
                    prop = find_prop(attrib.get_name())
                    if prop is not None:
                        CustomLayoutProperty(prop.prop_name)

                CustomLayoutProperty(None, None, build_fn=self._controls_build_fn)

            prop = find_prop("outputs:minimum")
            if prop is not None:
                with CustomLayoutGroup("Outputs"):
                    CustomLayoutProperty(prop.prop_name)

        return frame.apply(props)
