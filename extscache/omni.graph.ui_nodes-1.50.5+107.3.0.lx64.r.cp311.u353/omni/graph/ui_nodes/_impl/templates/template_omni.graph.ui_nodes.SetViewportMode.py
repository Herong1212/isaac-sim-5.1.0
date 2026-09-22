# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from typing import List

import omni.graph.core as og
import omni.ui as ui
from omni.graph.ui import OmniGraphBase
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.window.property.templates import HORIZONTAL_SPACING, LABEL_WIDTH
from pxr import Sdf, Usd

ATTRIB_LABEL_STYLE = {"alignment": ui.Alignment.RIGHT_TOP}
MODE_NAMES = ["Default", "Scripted"]


class ModeAttributeModel(ui.AbstractItemModel, OmniGraphBase):
    class AllowedTokenItem(ui.AbstractItem):
        def __init__(self, item, value):
            super().__init__()
            self.token = item
            self.model = ui.SimpleStringModel(value)

    def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], self_refresh: bool, metadata: dict):
        OmniGraphBase.__init__(self, stage, attribute_paths, self_refresh, metadata)
        ui.AbstractItemModel.__init__(self)

        self._allowed_tokens = [ModeAttributeModel.AllowedTokenItem(i, t) for i, t in enumerate(MODE_NAMES)]

        self._current_index = ui.SimpleIntModel()
        self._current_index.add_value_changed_fn(self._current_index_changed)

        self._updating_value = False

        self._has_index = False
        self._update_value()
        self._has_index = True

    def get_item_children(self, item):
        return self._allowed_tokens

    def get_item_value_model(self, item, column_id):
        if item is None:
            return self._current_index

        return item.model

    def _current_index_changed(self, model):
        if not self._has_index:
            return

        # if we're updating from USD notice change to UI, don't call set_value
        if self._updating_value:
            return

        index = model.as_int
        if self.set_value(index):
            self._item_changed(None)

    def _update_value(self, force=False):
        was_updating_value = self._updating_value
        self._updating_value = True

        if (
            OmniGraphBase._update_value(self, force)
            and (0 <= self._value < len(self._allowed_tokens))
            and (self._value != self._current_index.as_int)
        ):
            self._current_index.set_value(self._value)
            self._item_changed(None)

        self._updating_value = was_updating_value

    def _on_dirty(self):
        self._item_changed(None)


class CustomLayout:
    def __init__(self, compute_node_widget):
        self.enable = True
        self.compute_node_widget = compute_node_widget
        self.controller = og.Controller()
        self.node_prim_path = self.compute_node_widget._payload[-1]
        self.node = self.controller.node(self.node_prim_path)
        self.mode_model = None

    def _mode_build_fn(self, *args) -> ui.AbstractValueModel:
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            ui.Label("Mode", name="label", style=ATTRIB_LABEL_STYLE, width=LABEL_WIDTH)
            ui.Spacer(width=HORIZONTAL_SPACING)
            with ui.ZStack():
                attr_path = self.node_prim_path.AppendProperty("inputs:mode")
                self.mode_model = ModeAttributeModel(self.compute_node_widget.stage, [attr_path], False, {})
                ui.ComboBox(self.mode_model)
        return self.mode_model

    # Called by compute_node_widget to apply UI when selection changes
    def apply(self, props):
        def find_prop(name):
            return next((p for p in props if p.prop_name == name), None)

        # Retrieve the input and output attributes that exist on the node
        all_attributes = self.node.get_attributes()
        input_attribs = [
            attrib.get_name()
            for attrib in all_attributes
            if attrib.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            and attrib.get_name()[:7] == "inputs:"
            and attrib.get_resolved_type().role != og.AttributeRole.EXECUTION
        ]
        output_attribs = [
            attrib.get_name()
            for attrib in all_attributes
            if attrib.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
            and attrib.get_name()[:8] == "outputs:"
            and attrib.get_resolved_type().role != og.AttributeRole.EXECUTION
        ]
        mode_attrib = "inputs:mode"

        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                # Custom enum-style input for inputs:mode
                prop = find_prop(mode_attrib)
                if prop is not None:
                    CustomLayoutProperty(prop.prop_name, mode_attrib[7:], self._mode_build_fn)

                for input_attrib in input_attribs:
                    prop = find_prop(input_attrib)
                    if prop is not None and input_attrib != mode_attrib:
                        CustomLayoutProperty(prop.prop_name, input_attrib[7:])

            with CustomLayoutGroup("Outputs"):
                for output_attrib in output_attribs:
                    prop = find_prop(output_attrib)
                    if prop is not None:
                        CustomLayoutProperty(prop.prop_name, output_attrib[8:])

        return frame.apply(props)
