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
import omni.ui as ui
from omni.graph.nodes.scripts.ui_utils import _get_attribute_ui_name, _retrieve_existing_alphabetic_dynamic_inputs
from omni.graph.ui import LayerIdentifierWidgetBuilder, OmniGraphPropertiesWidgetBuilder
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry

ATTRIB_LABEL_STYLE = {"alignment": ui.Alignment.RIGHT_TOP}


class CustomLayout:
    """Custom layout for WritePrim node
    - dynamic output attributes are given 'nice' ui names
    """

    def __init__(self, compute_node_widget):
        self.enable = True
        self.compute_node_widget = compute_node_widget
        self.node_prim_path = self.compute_node_widget._payload[-1]
        self.controller = og.Controller()
        self.node = self.controller.node(self.node_prim_path)
        self._retrieve_existing_inputs = _retrieve_existing_alphabetic_dynamic_inputs
        self.usd_write_back_model = None
        self.layer_identifier_model = None
        self.stage = compute_node_widget.stage

    def _usd_write_back_build_fn(self, ui_prop: UsdPropertyUiEntry, *args):
        # Build the boolean toggle for inputs:usePath
        self.usd_write_back_model = OmniGraphPropertiesWidgetBuilder.build(
            self.stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [self.node_prim_path],
            {"style": ATTRIB_LABEL_STYLE},
        )
        self.usd_write_back_model.add_value_changed_fn(self._on_usd_write_back_changed)
        return self.usd_write_back_model

    def _layer_identifier_build_fn(self, ui_prop: UsdPropertyUiEntry, *args):
        # Build the token input prim path widget
        self.layer_identifier_model = LayerIdentifierWidgetBuilder.build(
            self.stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [self.node_prim_path],
            {"enabled": self.usd_write_back_model.as_bool, "style": ATTRIB_LABEL_STYLE},
            {"enabled": self.usd_write_back_model.as_bool},
        )
        return self.layer_identifier_model

    def _on_usd_write_back_changed(self, _):
        # When the usd write back toggle changes
        self.layer_identifier_model._set_dirty()  # noqa: PLW0212
        # FIXME: Not sure why _set_dirty doesn't trigger UI change, have to rebuild
        self.compute_node_widget.request_rebuild()

    def apply(self, props):
        # Called by compute_node_widget to apply UI when selection changes
        def find_prop(name):
            try:
                return next((p for p in props if p.prop_name == name))
            except StopIteration:
                return None

        frame = CustomLayoutFrame(hide_extra=True)
        (input_attribs, _) = self._retrieve_existing_inputs(self.node)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop = find_prop("inputs:prim")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Prim")

                prop = ogui.find_prop(props, "inputs:usdWriteBack")
                if prop:
                    CustomLayoutProperty(prop.prop_name, build_fn=partial(self._usd_write_back_build_fn, prop))

                prop = ogui.find_prop(props, "inputs:layerIdentifier")
                if prop:
                    CustomLayoutProperty(prop.prop_name, build_fn=partial(self._layer_identifier_build_fn, prop))

                for attrib in input_attribs:
                    attr_name = attrib.get_name()
                    if attr_name not in ["inputs:prim", "inputs:usdWriteBack", "inputs:execIn"]:
                        prop = find_prop(attr_name)
                        if prop is not None:
                            ui_name = prop.metadata.get("displayName")
                            if ui_name is None:
                                ui_name = _get_attribute_ui_name(prop.prop_name)
                            CustomLayoutProperty(prop.prop_name, ui_name)

        return frame.apply(props)
