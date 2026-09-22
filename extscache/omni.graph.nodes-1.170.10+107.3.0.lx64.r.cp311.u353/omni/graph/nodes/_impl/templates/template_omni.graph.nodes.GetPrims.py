# Copyright (c) 2022-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from functools import partial

import omni.ui as ui
from omni.graph.ui import OmniGraphAttributeModel, OmniGraphPropertiesWidgetBuilder
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry


class CustomLayout:
    """Custom layout for GetPrims node"""

    def __init__(self, compute_node_widget):
        self.enable = True
        self.compute_node_widget = compute_node_widget
        self.node_prim_path = compute_node_widget._payload[-1]  # noqa: PLW0212
        self.stage = compute_node_widget.stage
        self.ATTRIB_LABEL_STYLE = {"alignment": ui.Alignment.RIGHT_TOP}

        self.target_prims_name = "inputs:prims"
        self.target_prims_model = None
        self.path_pattern_model = None
        self.type_pattern_model = None
        self.inverse_model = None

    def apply(self, props):
        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop = self._find_prop(props, "inputs:prims")
                builder = partial(self._build_target_prims_fn, "target_prims_model", "Prims", prop)
                CustomLayoutProperty(None, None, build_fn=builder)

                prop = self._find_prop(props, "inputs:pathPattern")
                builder = partial(self._build_widget_fn, "path_pattern_model", "Path Pattern", prop)
                CustomLayoutProperty(None, None, build_fn=builder)

                prop = self._find_prop(props, "inputs:typePattern")
                builder = partial(self._build_widget_fn, "type_pattern_model", "Type Pattern", prop)
                CustomLayoutProperty(None, None, build_fn=builder)

                prop = self._find_prop(props, "inputs:inverse")
                builder = partial(self._build_widget_fn, "inverse_model", "Inverse", prop)
                CustomLayoutProperty(None, None, build_fn=builder)

        return frame.apply(props)

    def _find_prop(self, props, name):
        try:
            return next((p for p in props if p.prop_name == name))
        except StopIteration:
            return None

    def _has_target_prims(self, target_prims_name: str) -> bool:
        # Returns True if prim relationship has targets
        prim = self.stage.GetPrimAtPath(self.node_prim_path)
        if prim:
            rel = prim.GetRelationship(target_prims_name)
            if rel:
                return len(rel.GetTargets()) != 0
        return False

    def _on_target_prims_changed(self, *args):
        self.target_prims_model._set_dirty()  # noqa: PLW0212
        # FIXME: Not sure why _set_dirty doesn't trigger UI change, have to rebuild
        self.compute_node_widget.request_rebuild()

    def _build_target_prims_fn(
        self, property_name, new_name: str, ui_prop: UsdPropertyUiEntry, *args
    ) -> OmniGraphAttributeModel:
        ui_prop.override_display_name(new_name)
        model = OmniGraphPropertiesWidgetBuilder.build(
            self.stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [self.node_prim_path],
            {
                "style": self.ATTRIB_LABEL_STYLE,
            },
            {
                "on_remove_target": self._on_target_prims_changed,
                "target_picker_on_add_targets": self._on_target_prims_changed,
            },
        )
        setattr(self, property_name, model)
        return model

    def _build_widget_fn(
        self, property_name, new_name: str, ui_prop: UsdPropertyUiEntry, *args
    ) -> OmniGraphAttributeModel:
        has_targets = self._has_target_prims(self.target_prims_name)
        ui_prop.override_display_name(new_name)
        model = OmniGraphPropertiesWidgetBuilder.build(
            self.stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [self.node_prim_path],
            {"enabled": not has_targets, "style": self.ATTRIB_LABEL_STYLE},
            {"enabled": not has_targets},
        )
        setattr(self, property_name, model)
        return model
