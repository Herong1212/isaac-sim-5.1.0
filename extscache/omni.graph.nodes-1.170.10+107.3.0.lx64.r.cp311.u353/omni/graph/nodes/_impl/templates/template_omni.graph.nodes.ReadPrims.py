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
from omni.graph.ui._impl.omnigraph_attribute_builder import OmniGraphPropertiesWidgetBuilder
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry


class CustomLayout(ogui.ReadPrimsCustomLayoutBase):
    """Custom layout for ReadPrims node
    - inputs:useFindPrims disables inputs:prims and enables inputs:typePattern/pathPattern when true.
    """

    _value_is_output = True

    def __init__(self, compute_node_widget):
        super().__init__(compute_node_widget)
        self.use_find_prims_model = None
        self.path_pattern_model = None
        self.type_pattern_model = None
        self.compute_bounding_box_model = None
        self.apply_skel_binding_model = None

    def apply(self, props):
        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop = self._find_prop(props, "inputs:prims")
                if prop:
                    CustomLayoutProperty(prop.prop_name, build_fn=partial(self._prims_rel_build_fn, prop))

                prop = self._find_prop(props, "inputs:useFindPrims")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._use_find_prims_build_fn, prop))

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

        return frame.apply(props)

    def _use_find_prims_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build the boolean toggle for inputs:useFindPrims
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget._payload[-1]  # noqa: PLW0212
        ui_prop.override_display_name("Use Find Prims")
        self.use_find_prims_model = OmniGraphPropertiesWidgetBuilder.build(  # noqa: PLW0212
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"style": self.ATTRIB_LABEL_STYLE},
        )
        self.use_find_prims_model.add_value_changed_fn(self._on_use_find_prims_changed)
        return self.use_find_prims_model

    def _path_pattern_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build the token inputs:pathPattern widget
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget._payload[-1]  # noqa: PLW0212
        use_prims_rel = self._use_prims_rel(stage, node_prim_path)
        ui_prop.override_display_name("Path Pattern")
        self.path_pattern_model = OmniGraphPropertiesWidgetBuilder.build(  # noqa: PLW0212
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"enabled": not use_prims_rel, "style": self.ATTRIB_LABEL_STYLE},
            {"enabled": not use_prims_rel},
        )
        return self.path_pattern_model

    def _type_pattern_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build the token inputs:typePattern widget
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget._payload[-1]  # noqa: PLW0212
        use_prims_rel = self._use_prims_rel(stage, node_prim_path)
        ui_prop.override_display_name("Type Pattern")
        self.type_pattern_model = OmniGraphPropertiesWidgetBuilder.build(  # noqa: PLW0212
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"enabled": not use_prims_rel, "style": self.ATTRIB_LABEL_STYLE},
            {"enabled": not use_prims_rel},
        )
        return self.type_pattern_model

    def _apply_skel_binding_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build the boolean toggle for inputs:applySkelBinding
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget._payload[-1]  # noqa: PLW0212
        ui_prop.override_display_name("Apply Skel Binding")
        self.apply_skel_binding_model = OmniGraphPropertiesWidgetBuilder.build(  # noqa: PLW0212
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"style": self.ATTRIB_LABEL_STYLE},
        )
        return self.apply_skel_binding_model

    def _compute_bounding_box_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build the relationship inputs:computeBoundingBox widget
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget._payload[-1]  # noqa: PLW0212
        ui_prop.override_display_name("Compute Bounding Box")
        self.compute_bounding_box_model = OmniGraphPropertiesWidgetBuilder.build(  # noqa: PLW0212
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"style": self.ATTRIB_LABEL_STYLE},
        )
        return self.compute_bounding_box_model

    def _use_prims_rel(self, stage, node_prim_path):
        # Controls on/off behavior of inputs:prims and inputs:pathPattern and inputs:typePattern
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget._payload[-1]  # noqa: PLW0212
        prim = stage.GetPrimAtPath(node_prim_path)
        if prim:
            return not prim.GetAttribute("inputs:useFindPrims").Get()
        return True

    def _on_target_prims_rel_changed(self, *args):
        # When the inputs:prim relationship changes
        # Dirty the attribute name list model because the prim may have changed
        self.path_pattern_model._set_dirty()  # noqa: PLW0212
        self.prims_rel_widget._set_dirty()  # noqa: PLW0212

    def _on_use_find_prims_changed(self, _):
        # When the inputs:useFindPrims toggle changes
        self.prims_rel_widget._set_dirty()  # noqa: PLW0212
        self.path_pattern_model._set_dirty()  # noqa: PLW0212
        # FIXME: Not sure why _set_dirty doesn't trigger UI change, have to rebuild
        self.compute_node_widget.request_rebuild()
