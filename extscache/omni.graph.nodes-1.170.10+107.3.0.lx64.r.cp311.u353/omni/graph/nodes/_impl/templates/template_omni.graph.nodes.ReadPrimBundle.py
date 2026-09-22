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
from pxr import Sdf, Usd


class CustomLayout(ogui.ReadPrimsCustomLayoutBase):
    """Custom layout for ReadPrimBundle node
    - inputs:usePath disables inputs:prim and enables inputs:primPath when true.
    """

    _value_is_output = True

    def __init__(self, compute_node_widget):
        super().__init__(compute_node_widget)
        self.prim_rel_model = None
        self.use_path_model = None
        self.prim_path_model = None

    def apply(self, props):
        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop = self._find_prop(props, "inputs:prim")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._prim_rel_build_fn, prop))

                prop = self._find_prop(props, "inputs:usePath")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._use_path_build_fn, prop))

                prop = self._find_prop(props, "inputs:primPath")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._prim_path_build_fn, prop))

                prop = self._find_prop(props, "inputs:attrNamesToImport")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._attr_names_to_import_build_fn, prop))

                prop = self._find_prop(props, "inputs:usdTimecode")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._usd_timecode_build_fn, prop))

                prop = self._find_prop(props, "inputs:computeBoundingBox")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Compute Bounding Box")

        return frame.apply(props)

    def _on_target_prim_rel_changed(self, *args):
        # When the inputs:prims relationship changes
        # Dirty the attribute name list model because the prim may have changed
        self.prim_rel_model._set_dirty()  # noqa: PLW0212

    def _prim_rel_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build the relationship input prim widget
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget.payload[-1]
        use_path = self._get_use_path(stage, node_prim_path)
        ui_prop.override_display_name("Prim")
        self.prim_rel_model = OmniGraphPropertiesWidgetBuilder.build(
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"enabled": not use_path, "style": self.ATTRIB_LABEL_STYLE},
            {
                "enabled": not use_path,
                "on_remove_target": self._on_target_prim_rel_changed,
                "target_picker_on_add_targets": self._on_target_prim_rel_changed,
            },
        )
        return self.prim_rel_model

    def _use_path_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build the boolean toggle for inputs:usePath
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget.payload[-1]
        ui_prop.override_display_name("Use Path")
        self.use_path_model = OmniGraphPropertiesWidgetBuilder.build(
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"style": self.ATTRIB_LABEL_STYLE},
        )
        self.use_path_model.add_value_changed_fn(self._on_usepath_changed)
        return self.use_path_model

    def _prim_path_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build widget for attribute inputs:primPath with extended types
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget.payload[-1]
        use_path = self._get_use_path(stage, node_prim_path)
        ui_prop.override_display_name("Prim Path")
        self.prim_path_model = OmniGraphPropertiesWidgetBuilder.build(
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"enabled": use_path, "style": self.ATTRIB_LABEL_STYLE},
            {"enabled": use_path},
        )
        return self.prim_path_model

    def _on_usepath_changed(self, _):
        # When the inputs:usePath toggle changes
        self.prim_rel_model._set_dirty()  # noqa: PLW0212
        self.prim_path_model._set_dirty()  # noqa: PLW0212
        # FIXME: Not sure why _set_dirty doesn't trigger UI change, have to rebuild
        self.compute_node_widget.request_rebuild()

    def _get_use_path(self, stage: Usd.Stage, node_prim_path: Sdf.Path) -> bool:
        # Gets the value of the usePath input attribute
        prim = stage.GetPrimAtPath(node_prim_path)
        if prim:
            return prim.GetAttribute("inputs:usePath").Get()
        return False
