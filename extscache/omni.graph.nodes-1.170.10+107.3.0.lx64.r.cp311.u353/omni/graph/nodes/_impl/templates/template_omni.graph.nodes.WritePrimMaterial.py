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
from omni.graph.ui import LayerIdentifierWidgetBuilder, OmniGraphPropertiesWidgetBuilder
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry


class CustomLayout(ogui.PrimPathCustomLayoutBase):
    """Custom layout for WritePrimMaterial
    - inputs:primPath/materialPath are disabled when inputs:prim/material target a prim.
    """

    _prim_rel_name = "inputs:prim"

    def __init__(self, compute_node_widget):
        super().__init__(compute_node_widget)
        self.material_model = None
        self.material_path_model = None
        self.layer_identifier_widget = None

    def apply(self, props):
        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop = self._find_prop(props, "inputs:prim")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._prim_build_fn, prop))
                    prop.override_display_name("Prim")

                prop = self._find_prop(props, "inputs:primPath")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._prim_path_build_fn, prop))
                    prop.override_display_name("Prim Path")

                prop = self._find_prop(props, "inputs:material")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._material_build_fn, prop))
                    prop.override_display_name("Material")

                prop = self._find_prop(props, "inputs:materialPath")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._material_path_build_fn, prop))
                    prop.override_display_name("Material Path")

                prop = self._find_prop(props, "inputs:layerIdentifier")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._layer_identifier_build_fn, prop))
                    prop.override_display_name("Layer Identifier")

        return frame.apply(props)

    def _on_material_changed(self, *args):
        # When the material relationship changes
        self.material_path_model._set_dirty()  # noqa: PLW0212
        # FIXME: Not sure why _set_dirty doesn't trigger UI change, have to rebuild
        self.compute_node_widget.request_rebuild()

    def _material_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build the material relationship widget
        self.material_model = OmniGraphPropertiesWidgetBuilder.build(
            self.stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [self.node_prim_path],
            {"style": self.ATTRIB_LABEL_STYLE},
            {
                "on_remove_target": self._on_material_changed,
                "target_picker_on_add_targets": self._on_material_changed,
            },
        )
        return self.material_model

    def _material_path_build_fn(self, ui_prop: UsdPropertyUiEntry, *args) -> ogui.OmniGraphAttributeModel:
        # Build the materialPath attribute widget
        use_path = not self._rel_has_target("inputs:material")
        self.material_path_model = OmniGraphPropertiesWidgetBuilder.build(
            self.stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [self.node_prim_path],
            {"enabled": use_path, "style": self.ATTRIB_LABEL_STYLE},
            {"enabled": use_path},
        )
        return self.material_path_model

    def _layer_identifier_build_fn(self, ui_prop: UsdPropertyUiEntry, *args):
        # Build the layer identifier path
        self.layer_identifier_widget = LayerIdentifierWidgetBuilder.build(
            self.stage,
            ui_prop.prop_name,
            ui_prop.metadata,
            ui_prop.property_type,
            [self.node_prim_path],
            {"style": self.ATTRIB_LABEL_STYLE},
        )
        return self.layer_identifier_widget
