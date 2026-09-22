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
import omni.graph.tools.ogn as ogn
import omni.ui as ui
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from template_utils import CreateAttributePopupDialog


class CustomLayout:
    def __init__(self, compute_node_widget):
        self._remove_attribute_menu = None
        self.enable = True
        self.compute_node_widget = compute_node_widget
        self.node_prim_path = self.compute_node_widget._payload[-1]
        self.node = og.Controller.node(self.node_prim_path)
        self.add_attribute_button = None
        self.remove_attribute_button = None

    def _retrieve_existing_inputs(self):
        """Retrieve the input attributes that already exist on the node"""
        all_attributes = self.node.get_attributes()
        inputs = [
            attrib
            for attrib in all_attributes
            if (attrib.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT) and attrib.is_dynamic()
        ]
        return inputs

    def _add_attribute_button_build_fn(self, *args):
        def create_dynamic_attribute(attrib_name, attrib_port_type, attrib_type, attrib_memory_type, cuda_pointers):
            new_attribute = og.Controller.create_attribute(self.node, attrib_name, attrib_type, attrib_port_type)
            if new_attribute is None:
                return

            self.compute_node_widget.rebuild_window()

        def on_click_add():
            CreateAttributePopupDialog(create_dynamic_attribute, og.AttributePortType.INPUT)

        self.add_attribute_button = ui.Button("Add +", width=100, clicked_fn=on_click_add)

    def _remove_attribute_button_build_fn(self, *args):
        def remove_dynamic_attribute(attrib):
            if attrib.get_name() == "inputs:execIn":
                # Hide inputs:execIn instead of removing it
                og.Controller.disconnect_all(("inputs:execIn", self.node))
                attrib.set_metadata(ogn.MetadataKeys.HIDDEN, "1")
                return

            og.Controller.disconnect_all(attrib)
            success = og.Controller.remove_attribute(attrib)
            if not success:
                return
            self.compute_node_widget.rebuild_window()

        def _remove_attribute_menu_build_fn():
            self._remove_attribute_menu = ui.Menu("Remove Attribute")
            outputs = self._retrieve_existing_inputs()
            with self._remove_attribute_menu:
                for attrib in outputs:
                    name = attrib.get_name()
                    ui.MenuItem(name, triggered_fn=partial(remove_dynamic_attribute, attrib))
            self._remove_attribute_menu.show()

        self.remove_attribute_button = ui.Button("Remove -", width=100, clicked_fn=_remove_attribute_menu_build_fn)

    def _special_control_build_fn(self, *args):
        with ui.HStack():
            self._add_attribute_button_build_fn()
            ui.Spacer(width=8)
            self._remove_attribute_button_build_fn()

    def apply(self, props):
        """Called by compute_node_widget to apply UI when selection changes"""

        def find_prop(name):
            try:
                return next((p for p in props if p.prop_name == name))
            except StopIteration:
                return None

        frame = CustomLayoutFrame(hide_extra=True)
        inputs = self._retrieve_existing_inputs()
        with frame:
            with CustomLayoutGroup("Add and Remove Attributes"):
                CustomLayoutProperty(None, None, self._special_control_build_fn)
            with CustomLayoutGroup("Inputs"):
                prop = find_prop("inputs:eventName")
                CustomLayoutProperty(prop.prop_name, "Event Name")
                for input_attrib in inputs:
                    attrib_name = input_attrib.get_name()
                    if input_attrib.is_dynamic():
                        prop = find_prop(attrib_name)
                        if prop is not None:
                            CustomLayoutProperty(prop.prop_name, attrib_name[7:])
        return frame.apply(props)
