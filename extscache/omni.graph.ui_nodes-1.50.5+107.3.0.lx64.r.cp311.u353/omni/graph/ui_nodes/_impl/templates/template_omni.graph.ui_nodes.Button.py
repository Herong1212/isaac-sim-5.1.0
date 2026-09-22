# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from functools import partial

import omni.graph.core as og
import omni.ui as ui
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidgetBuilder


class CustomLayout:
    def __init__(self, compute_node_widget):
        self.enable = True
        self.compute_node_widget = compute_node_widget
        self.node_prim_path = self.compute_node_widget._payload[-1]
        self.node = og.Controller.node(self.node_prim_path)
        self.icon_textbox_widgets = {}
        self.icon_selector_window = None
        self.icon_selector_window_previous_directory = None

        self.icon_attribs = [
            "inputs:idleIcon",
            "inputs:hoverIcon",
            "inputs:pressedIcon",
            "inputs:disabledIcon",
        ]

    def show_icon_selector_window(self, icon_attrib_name: str):
        # Create and show the file browser window which is used to select icon
        try:
            from omni.kit.window.filepicker import FilePickerDialog
        except ImportError:
            # Do nothing if the module cannot be imported
            return

        def __on_click_okay(filename: str, dirname: str):
            # Hardcode a forward slash rather than using os.path.join,
            # because the dirname will always use forward slash even on Windows machines
            chosen_file = dirname + "/" + filename
            self.icon_textbox_widgets[icon_attrib_name].set_value(chosen_file)
            self.icon_selector_window_previous_directory = self.icon_selector_window.get_current_directory()
            self.icon_selector_window.hide()

        def __on_click_cancel(file_name: str, directory_name: str):
            self.icon_selector_window_previous_directory = self.icon_selector_window.get_current_directory()
            self.icon_selector_window.hide()

        self.icon_selector_window = FilePickerDialog(
            "Select an Icon",
            click_apply_handler=__on_click_okay,
            click_cancel_handler=__on_click_cancel,
            allow_multi_selection=False,
        )
        self.icon_selector_window.show(self.icon_selector_window_previous_directory)

    def icon_attrib_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ui.AbstractValueModel:
        # Build the attribute label, textbox and browse button that's displayed on the property panel
        icon_attrib_name = ui_prop.prop_name

        self.icon_textbox_widgets[icon_attrib_name] = UsdPropertiesWidgetBuilder._string_builder(  # noqa: PLW0212
            self.compute_node_widget.stage,
            icon_attrib_name,
            ui_prop.property_type,
            ui_prop.metadata,
            [self.node_prim_path],
            {"style": {"alignment": ui.Alignment.RIGHT_TOP}},
        )

        ui.Spacer(width=5)
        ui.Button(
            "Browse",
            width=0,
            clicked_fn=partial(self.show_icon_selector_window, icon_attrib_name),
        )
        return self.icon_textbox_widgets[icon_attrib_name]

    def apply(self, props):
        # Called by compute_node_widget to apply UI when selection changes
        def find_prop(name):
            try:
                return next((p for p in props if p.prop_name == name))
            except StopIteration:
                return None

        # Retrieve the input and output attributes that exist on the node
        all_attributes = self.node.get_attributes()
        input_attribs = [
            attrib.get_name()
            for attrib in all_attributes
            if attrib.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            and attrib.get_name()[:7] == "inputs:"
        ]
        output_attribs = [
            attrib.get_name()
            for attrib in all_attributes
            if attrib.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
            and attrib.get_name()[:8] == "outputs:"
        ]

        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                for input_attrib in input_attribs:
                    prop = find_prop(input_attrib)
                    if prop is not None and input_attrib not in self.icon_attribs:
                        CustomLayoutProperty(prop.prop_name, input_attrib[7:])

                for icon_attrib in self.icon_attribs:
                    prop = find_prop(icon_attrib)
                    if prop is not None:
                        build_fn = partial(self.icon_attrib_build_fn, prop)
                        CustomLayoutProperty(prop.prop_name, icon_attrib[7:], build_fn)

            with CustomLayoutGroup("Outputs"):
                for output_attrib in output_attribs:
                    prop = find_prop(output_attrib)
                    if prop is not None:
                        CustomLayoutProperty(prop.prop_name, output_attrib[8:])

        return frame.apply(props)
