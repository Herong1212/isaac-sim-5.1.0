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
from omni.graph.ui import OmniGraphPropertiesWidgetBuilder
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry


class CustomLayout(ogui.ReadPrimsCustomLayoutBase):
    """Custom layout for ReadPrims node"""

    _value_is_output = True

    def __init__(self, compute_node_widget):
        super().__init__(compute_node_widget)
        self.path_pattern_model = None
        self.type_pattern_model = None
        self.apply_skel_binding_model = None
        self.change_tracking_model = None
        self.bundle_change_tracking_model = None
        self.compute_bounding_box_model = None

    def apply(self, props):
        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop = self._find_prop(props, "inputs:prims")
                if prop:
                    CustomLayoutProperty(
                        prop.prop_name, build_fn=partial(self._prims_rel_build_fn, prop, enabled_by_use_rel=False)
                    )
                prop = self._find_prop(props, "inputs:pathPattern")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._path_pattern_build_fn, prop))

                prop = self._find_prop(props, "inputs:typePattern")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._type_pattern_build_fn, prop))

                prop = self._find_prop(props, "inputs:attrNamesToImport")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._attr_names_to_import_build_fn, prop))

                prop = self._find_prop(props, "inputs:usdTimecode")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._usd_timecode_build_fn, prop))

                prop = self._find_prop(props, "inputs:computeBoundingBox")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._compute_bounding_box_build_fn, prop))

                prop = self._find_prop(props, "inputs:applySkelBinding")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._apply_skel_binding_build_fn, prop))

                prop = self._find_prop(props, "inputs:enableChangeTracking")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._enable_change_tracking_build_fn, prop))

                prop = self._find_prop(props, "inputs:enableBundleChangeTracking")
                if prop:
                    CustomLayoutProperty(
                        None, None, build_fn=partial(self._enable_bundle_change_tracking_build_fn, prop)
                    )

        return frame.apply(props)

    def _path_pattern_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build the token inputs:pathPattern widget
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget.payload[-1]
        ui_prop.override_display_name("Path Pattern")
        self.path_pattern_model = OmniGraphPropertiesWidgetBuilder.build(
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"style": self.ATTRIB_LABEL_STYLE},
        )
        return self.path_pattern_model

    def _type_pattern_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build the token inputs:typePattern widget
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget.payload[-1]
        ui_prop.override_display_name("Type Pattern")
        self.type_pattern_model = OmniGraphPropertiesWidgetBuilder.build(
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"style": self.ATTRIB_LABEL_STYLE},
        )
        return self.type_pattern_model

    def _apply_skel_binding_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build the boolean toggle for inputs:applySkelBinding
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget.payload[-1]
        ui_prop.override_display_name("Apply Skel Binding")
        self.apply_skel_binding_model = OmniGraphPropertiesWidgetBuilder.build(
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"style": self.ATTRIB_LABEL_STYLE},
        )
        return self.apply_skel_binding_model

    def _enable_change_tracking_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build the boolean toggle for inputs:enableChangeTracking
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget.payload[-1]
        ui_prop.override_display_name("USD Change Tracking")
        self.change_tracking_model = OmniGraphPropertiesWidgetBuilder.build(
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"style": self.ATTRIB_LABEL_STYLE},
        )
        return self.change_tracking_model

    def _enable_bundle_change_tracking_build_fn(
        self, ui_prop: UsdPropertyUiEntry, *args
    ) -> ogui.OmniGraphAttributeModel:
        # Build the boolean toggle for inputs:enableBundleChangeTracking
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget.payload[-1]
        ui_prop.override_display_name("Bundle Change Tracking")
        self.bundle_change_tracking_model = OmniGraphPropertiesWidgetBuilder.build(
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"style": self.ATTRIB_LABEL_STYLE},
        )
        return self.bundle_change_tracking_model

    def _compute_bounding_box_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build the relationship inputs:computeBoundingBox widget
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget.payload[-1]
        ui_prop.override_display_name("Compute Bounding Box")
        self.compute_bounding_box_model = OmniGraphPropertiesWidgetBuilder.build(
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"style": self.ATTRIB_LABEL_STYLE},
        )
        return self.compute_bounding_box_model

    def _on_target_prims_rel_changed(self, *args):
        # When the inputs:prim relationship changes
        # Dirty the attribute name list model because the prim may have changed
        self.path_pattern_model._set_dirty()  # noqa: PLW0212
