# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pathlib import Path
from typing import List

import omni.graph.core as og
import omni.graph.tools.ogn as ogn
import omni.ui as ui
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.window.property.templates import HORIZONTAL_SPACING


class CustomLayout:
    def __init__(self, compute_node_widget):
        self.enable = True
        self.compute_node_widget = compute_node_widget
        self.controller = og.Controller()
        self.add_button: ui.Button = None
        self.remove_button: ui.Button = None
        self.node = self.controller.node(self.compute_node_widget._payload[-1])

    def _get_input_attrib_names(self) -> List[str]:
        """Return the list of dynamic input attribs"""
        all_attribs = self.node.get_attributes()
        input_attrib_names = []
        for attrib in all_attribs:
            attrib_name = attrib.get_name()
            name_prefix = attrib_name[:13]
            if name_prefix == "inputs:branch":
                input_attrib_names.append(attrib_name)
        return input_attrib_names

    def _get_max_suffix(self) -> int:
        """Return the maximum suffix of dynamic inputs or -1 if there are none"""
        names = self._get_input_attrib_names()
        if not names:
            return -1
        return max(int(name[13:]) for name in names)

    def _on_click_add(self):
        next_suffix = f"{self._get_max_suffix() + 1:02}"
        new_attr = self.controller.create_attribute(
            self.node,
            f"inputs:branch{next_suffix}",
            og.Type(og.BaseDataType.TOKEN, 1, 0, og.AttributeRole.NONE),
            og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
        )
        new_attr.set_metadata(ogn.MetadataKeys.LITERAL_ONLY, "1")
        self.controller.create_attribute(
            self.node,
            f"outputs:output{next_suffix}",
            og.Type(og.BaseDataType.UINT, 1, 0, og.AttributeRole.EXECUTION),
            og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
        )
        self.compute_node_widget.rebuild_window()
        self.remove_button.enabled = True

    def _on_click_remove(self):
        max_suffix = self._get_max_suffix()
        if max_suffix < 0:
            return
        attrib_to_remove = self.node.get_attribute(f"outputs:output{max_suffix:02}")
        self.controller.remove_attribute(attrib_to_remove)
        attrib_to_remove = self.node.get_attribute(f"inputs:branch{max_suffix:02}")
        self.controller.remove_attribute(attrib_to_remove)
        self.compute_node_widget.rebuild_window()
        self.remove_button.enabled = max_suffix > 0

    def _controls_build_fn(self, *args):
        max_suffix = self._get_max_suffix()
        icons_path = Path(__file__).absolute().parent.parent.parent.parent.parent.parent.joinpath("icons")

        with ui.HStack(height=0, spacing=HORIZONTAL_SPACING):
            ui.Spacer()
            self.add_button = ui.Button(
                image_url=f"{icons_path.joinpath('add.svg')}",
                width=22,
                height=22,
                style={"Button": {"background_color": 0x1F2124}},
                clicked_fn=self._on_click_add,
                tooltip_fn=lambda: ui.Label("Add New Branch"),
            )
            self.remove_button = ui.Button(
                image_url=f"{icons_path.joinpath('remove.svg')}",
                width=22,
                height=22,
                style={"Button": {"background_color": 0x1F2124}},
                enabled=(max_suffix > 0),
                clicked_fn=self._on_click_remove,
                tooltip_fn=lambda: ui.Label("Remove Branch"),
            )

    def apply(self, props):
        # Called by compute_node_widget to apply UI when selection changes
        def find_prop(name):
            return next((p for p in props if p.prop_name == name), None)

        frame = CustomLayoutFrame(hide_extra=True)
        names = self._get_input_attrib_names()
        with frame:
            with CustomLayoutGroup("Inputs"):
                for name in names:
                    prop = find_prop(name)
                    CustomLayoutProperty(prop.prop_name)
                CustomLayoutProperty(None, None, build_fn=self._controls_build_fn)

        return frame.apply(props)
