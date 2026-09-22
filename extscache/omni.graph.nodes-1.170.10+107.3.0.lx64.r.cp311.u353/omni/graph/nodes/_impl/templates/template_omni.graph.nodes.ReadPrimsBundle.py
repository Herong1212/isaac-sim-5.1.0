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
    """Custom layout for ReadPrimsBundle node
    - inputs:usePaths disables inputs:prims and enables inputs:primPaths when true.
    """

    _value_is_output = True

    def __init__(self, compute_node_widget):
        super().__init__(compute_node_widget)
        self.use_paths_model = None
        self.prim_paths_model = None

    def apply(self, props):
        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop = self._find_prop(props, "inputs:prims")
                if prop:
                    CustomLayoutProperty(prop.prop_name, build_fn=partial(self._prims_rel_build_fn, prop))

                prop = self._find_prop(props, "inputs:usePaths")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._use_paths_build_fn, prop))

                prop = self._find_prop(props, "inputs:primPaths")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._prim_paths_build_fn, prop))

                prop = self._find_prop(props, "inputs:attrNamesToImport")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._attr_names_to_import_build_fn, prop))

                prop = self._find_prop(props, "inputs:usdTimecode")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._usd_timecode_build_fn, prop))

        return frame.apply(props)

    def _use_prims_rel(self, stage, node_prim_path):
        # Controls on/off behavior of inputs:prims and inputs:primPaths
        prim = stage.GetPrimAtPath(node_prim_path)
        if prim:
            return not prim.GetAttribute("inputs:usePaths").Get()
        return True

    def _use_paths_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build the boolean toggle for inputs:usePaths
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget.payload[-1]
        ui_prop.override_display_name("Use Paths")
        self.use_paths_model = OmniGraphPropertiesWidgetBuilder.build(
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"style": self.ATTRIB_LABEL_STYLE},
        )
        self.use_paths_model.add_value_changed_fn(self._on_use_paths_changed)
        return self.use_paths_model

    def _prim_paths_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build widget for attribute inputs:primPaths with extended types
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget.payload[-1]
        use_prims_rel = self._use_prims_rel(stage, node_prim_path)
        ui_prop.override_display_name("Prim Paths")
        self.prim_paths_model = OmniGraphPropertiesWidgetBuilder.build(
            stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [node_prim_path],
            {"enabled": not use_prims_rel, "style": self.ATTRIB_LABEL_STYLE},
            {"enabled": not use_prims_rel},
        )
        return self.prim_paths_model

    def _on_use_paths_changed(self, _):
        # When the inputs:usePath toggle changes
        self.prims_rel_widget._set_dirty()  # noqa: PLW0212
        self.prim_paths_model._set_dirty()  # noqa: PLW0212
        # FIXME: Not sure why _set_dirty doesn't trigger UI change, have to rebuild
        self.compute_node_widget.request_rebuild()
