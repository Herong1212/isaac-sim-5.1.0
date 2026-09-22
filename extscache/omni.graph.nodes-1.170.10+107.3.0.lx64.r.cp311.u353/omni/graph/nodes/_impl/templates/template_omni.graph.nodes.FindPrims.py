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
from omni.graph.ui import OmniGraphAttributeModel, OmniGraphPropertiesWidgetBuilder
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry


class CustomLayout(ogui.PrimPathCustomLayoutBase):
    """Custom layout for FindPrims node
    - inputs:rootPrimPath/requiredRelationshipTarget is disabled when inputs:rootPrim/requiredTarget targets a prim.
    - attributes are presented in a more logical order
    """

    _prim_rel_name = "inputs:rootPrim"

    def __init__(self, compute_node_widget):
        super().__init__(compute_node_widget)
        self.req_rel_tgt_model = None
        self.req_rel_tgt_path_widget = None

    def apply(self, props):
        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop = self._find_prop(props, "inputs:rootPrim")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._prim_build_fn, prop))
                    prop.override_display_name("Root Prim")

                prop = self._find_prop(props, "inputs:rootPrimPath")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._prim_path_build_fn, prop))
                    prop.override_display_name("Root Prim Path")

                prop = self._find_prop(props, "inputs:recursive")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Recursive")

                prop = self._find_prop(props, "inputs:namePrefix")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Prim Name Prefix")

                prop = self._find_prop(props, "inputs:pathPattern")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Prim Path Pattern")

                prop = self._find_prop(props, "inputs:type")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Prim Type Pattern")

                prop = self._find_prop(props, "inputs:requiredAttributes")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Attribute Names")

                prop = self._find_prop(props, "inputs:requiredRelationship")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Relationship Name")

                prop = self._find_prop(props, "inputs:requiredTarget")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._req_rel_tgt_build_fn, prop))
                    prop.override_display_name("Relationship Prim")

                prop = self._find_prop(props, "inputs:requiredRelationshipTarget")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._req_rel_tgt_path_build_fn, prop))
                    prop.override_display_name("Relationship Prim Path")

                prop = self._find_prop(props, "inputs:ignoreSystemPrims")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Ignore System Prims")

            with CustomLayoutGroup("Outputs"):
                prop = self._find_prop(props, "outputs:prims")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Prims")

                prop = self._find_prop(props, "outputs:primPaths")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Prim Paths")
        return frame.apply(props)

    def _on_req_rel_tgt_changed(self, *args):
        # When the requiredTarget relationship changes
        self.req_rel_tgt_path_widget._set_dirty()  # noqa: PLW0212
        # FIXME: Not sure why _set_dirty doesn't trigger UI change, have to rebuild
        self.compute_node_widget.request_rebuild()

    def _req_rel_tgt_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> OmniGraphAttributeModel:
        # Build the requiredTarget relationship widget
        self.req_rel_tgt_model = OmniGraphPropertiesWidgetBuilder.build(
            self.stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [self.node_prim_path],
            {"style": self.ATTRIB_LABEL_STYLE},
            {
                "on_remove_target": self._on_req_rel_tgt_changed,
                "target_picker_on_add_targets": self._on_req_rel_tgt_changed,
            },
        )
        return self.req_rel_tgt_model

    def _req_rel_tgt_path_build_fn(self, ui_prop: UsdPropertyUiEntry, *args):
        # Build the requiredRelationshipTarget attribute widget
        use_path = not self._rel_has_target("inputs:requiredTarget")
        self.req_rel_tgt_path_widget = OmniGraphPropertiesWidgetBuilder.build(
            self.stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [self.node_prim_path],
            {"enabled": use_path, "style": self.ATTRIB_LABEL_STYLE},
            {"enabled": use_path},
        )
