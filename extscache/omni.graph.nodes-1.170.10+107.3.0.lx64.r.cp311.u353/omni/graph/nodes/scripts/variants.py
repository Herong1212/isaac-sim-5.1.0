# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from functools import partial
from typing import List, Optional

import omni.graph.core as og
import omni.ui as ui
from omni.graph.ui import (
    LayerIdentifierWidgetBuilder,
    OmniGraphAttributeModel,
    OmniGraphPropertiesWidgetBuilder,
    OmniGraphTfTokenAttributeModel,
)
from omni.kit.property.usd import AllowedTokenItem as BaseAllowedTokenItem
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry
from omni.kit.window.property.templates import HORIZONTAL_SPACING, LABEL_WIDTH
from usdrt import Sdf, Usd

from .variant_utils import (  # noqa PLE0402
    get_attr_has_connections,
    get_attr_value,
    get_descendants,
    get_target_prim,
    override_display_name,
    pretty_name,
)

ATTRIB_LABEL_STYLE = {"alignment": ui.Alignment.RIGHT_TOP}


class VariantTokenModel(OmniGraphTfTokenAttributeModel):
    """Model for selecting the variant set name. We modify the list to show variant sets which are available
    on the target prim."""

    class AllowedTokenItem(BaseAllowedTokenItem):
        def __init__(self, item, label):
            """
            Args:
                item: the variant set name token to be shown
                label: the label to show in the drop-down
            """
            super().__init__(item)
            self.token = item
            self.model = ui.SimpleStringModel(label)

    def __init__(
        self,
        stage: Usd.Stage,
        attribute_paths: List[Sdf.Path],
        self_refresh: bool,
        metadata: dict,
        node_prim_path: Sdf.Path,
    ):
        """
        Args:
            stage: The current stage
            attribute_paths: The list of full attribute paths
            self_refresh: ignored
            metadata: pass-through metadata for model
            node_prim_path: The path of the compute node
        """
        self._stage = stage
        self._node_prim_path = node_prim_path
        self._target_prim = None
        super().__init__(stage, attribute_paths, self_refresh, metadata)

    def _get_allowed_tokens(self, _):
        # Override of TfTokenAttributeModel to specialize what tokens are to be shown
        # Returns the attributes we want to let the user select from
        prim = self._stage.GetPrimAtPath(self._node_prim_path)
        if not prim:
            return []

        self._target_prim = get_target_prim(self._stage, self._node_prim_path)

        tokens = self._get_tokens(self._target_prim)

        current_value = og.Controller().get(attribute=self._get_attributes()[0])
        if current_value and current_value not in tokens:
            tokens.append(current_value)
        tokens.insert(0, "")
        return tokens

    @staticmethod
    def _item_factory(item):
        # Construct the item for the model
        label = item
        return VariantTokenModel.AllowedTokenItem(item, label)

    def _update_allowed_token(self, **kwargs):
        # Override of TfTokenAttributeModel to specialize the model items
        super()._update_allowed_token(token_item=self._item_factory)

    def _get_tokens(self, prim: Usd.Prim) -> List[str]:
        return []


class VariantSetNamesTokenModel(VariantTokenModel):
    def _get_variant_set_names(self, prim: Usd.Prim) -> List[str]:
        if prim:
            variant_sets = prim.GetVariantSets()
            variant_sets_names = list(variant_sets.GetNames())
            return variant_sets_names
        return []

    def _get_tokens(self, prim: Usd.Prim) -> List[str]:
        return self._get_variant_set_names(prim)


class VariantNamesTokenModel(VariantTokenModel):
    def _get_variant_names(self, prim: Usd.Prim) -> List[str]:
        node_prim = self._stage.GetPrimAtPath(self._node_prim_path)
        if node_prim and prim:
            variant_sets = prim.GetVariantSets()
            variant_set_name = get_attr_value(node_prim, "inputs:variantSetName")
            variant_set = variant_sets.GetVariantSet(variant_set_name)
            variant_sets_names = list(variant_set.GetVariantNames())
            return variant_sets_names
        return []

    def _get_tokens(self, prim: Usd.Prim) -> List[str]:
        return self._get_variant_names(prim)


# noinspection PyProtectedMember
class CustomVariantLayout:
    """Custom layout for the variant set and variant name attributes"""

    def __init__(self, compute_node_widget):
        self.enable = True
        self.compute_node_widget = compute_node_widget

        self.prim_rel_layout = None
        self.prim_rel_model = None

        self.layer_identifier_layout = None
        self.layer_identifier_model = None

        self.variant_set_name_token_model = None
        self.variant_set_name_string_model = None
        self.variant_name_token_model = None
        self.variant_name_string_model = None
        self.variant_name_a_token_model = None
        self.variant_name_a_string_model = None
        self.variant_name_b_token_model = None
        self.variant_name_b_string_model = None

        self.variant_set_name_string_layout = None
        self.variant_set_name_token_layout = None
        self.variant_name_string_layout = None
        self.variant_name_token_layout = None
        self.variant_name_a_string_layout = None
        self.variant_name_a_token_layout = None
        self.variant_name_b_string_layout = None
        self.variant_name_b_token_layout = None

    def get_node_prim_path(self):
        node_prim_path = self.compute_node_widget.payload[-1]
        return node_prim_path

    @staticmethod
    def _set_child_string_field_enabled(widget: ui.Widget, enabled: bool):
        for child in get_descendants(widget):
            if isinstance(child, ui.StringField):
                child.enabled = enabled

    def _get_target_prim(self) -> Usd.Prim:
        return get_target_prim(self.compute_node_widget.stage, self.get_node_prim_path())

    def _get_attr_has_connections(self, attr_name: str) -> bool:
        stage = self.compute_node_widget.stage
        node_prim_path = self.get_node_prim_path()
        prim = stage.GetPrimAtPath(node_prim_path)
        return get_attr_has_connections(prim, attr_name)

    def _token_builder(self, ui_prop: UsdPropertyUiEntry) -> ui.AbstractValueModel:
        return OmniGraphPropertiesWidgetBuilder._tftoken_builder(  # noqa: PLW0212
            stage=self.compute_node_widget.stage,
            attr_name=ui_prop.prop_name,
            type_name=ui_prop.property_type,
            metadata=ui_prop.metadata,
            prim_paths=[self.get_node_prim_path()],
            additional_label_kwargs={"style": ATTRIB_LABEL_STYLE},
            additional_widget_kwargs={"no_allowed_tokens_model_cls": OmniGraphAttributeModel},
        )

    def _relationship_builder(self, ui_prop: UsdPropertyUiEntry, changed_fn) -> ui.AbstractValueModel:
        return OmniGraphPropertiesWidgetBuilder._relationship_builder(  # noqa: PLW0212
            stage=self.compute_node_widget.stage,
            attr_name=ui_prop.prop_name,
            metadata=ui_prop.metadata,
            prim_paths=[self.get_node_prim_path()],
            additional_label_kwargs={"style": ATTRIB_LABEL_STYLE},
            additional_widget_kwargs={
                "on_remove_target": changed_fn,
                "target_picker_on_add_targets": changed_fn,
                "targets_limit": 1,
            },
        )

    def _bool_builder(self, ui_prop: UsdPropertyUiEntry) -> ui.AbstractValueModel:
        return OmniGraphPropertiesWidgetBuilder._bool_builder(  # noqa: PLW0212
            stage=self.compute_node_widget.stage,
            attr_name=ui_prop.prop_name,
            type_name=ui_prop.property_type,
            metadata=ui_prop.metadata,
            prim_paths=[self.get_node_prim_path()],
            additional_label_kwargs={"style": ATTRIB_LABEL_STYLE},
        )

    def _layer_identifier_builder(self, ui_prop: UsdPropertyUiEntry):
        return LayerIdentifierWidgetBuilder.build(
            stage=self.compute_node_widget.stage,
            attr_name=ui_prop.prop_name,
            property_type=ui_prop.property_type,
            metadata=ui_prop.metadata,
            prim_paths=[self.get_node_prim_path()],
            additional_label_kwargs={"style": ATTRIB_LABEL_STYLE},
        )

    def _combo_box_builder(self, ui_prop: UsdPropertyUiEntry, model_cls, changed_fn=None) -> ui.AbstractValueModel:
        stage = self.compute_node_widget.stage
        node_prim_path = self.get_node_prim_path()

        with ui.HStack(spacing=HORIZONTAL_SPACING):
            prop_name = pretty_name(ui_prop.prop_name)
            ui.Label(prop_name, name="label", style=ATTRIB_LABEL_STYLE, width=LABEL_WIDTH)
            ui.Spacer(width=HORIZONTAL_SPACING)
            with ui.ZStack():
                attr_path = node_prim_path.AppendProperty(ui_prop.prop_name)
                # Build the token-selection widget when prim is known
                model = model_cls(stage, [attr_path], False, {}, node_prim_path)
                ui.ComboBox(model)
            if changed_fn:
                model._current_index.add_value_changed_fn(changed_fn)  # noqa PLW0212

        return model

    def _prim_rel_build_fn(self, ui_prop: UsdPropertyUiEntry, *_) -> ui.AbstractValueModel:
        # Build the relationship input prim widget
        self.prim_rel_layout = ui.HStack(spacing=0)
        with self.prim_rel_layout:
            self.prim_rel_model = self._relationship_builder(ui_prop, self._on_target_prim_rel_changed)
        return self.prim_rel_model

    def _layer_identifier_build_fn(self, ui_prop: UsdPropertyUiEntry, *args):
        # Build the token layer identifier widget
        self.layer_identifier_layout = ui.HStack(spacing=0)
        with self.layer_identifier_layout:
            self.layer_identifier_model = self._layer_identifier_builder(ui_prop)
        return self.layer_identifier_model

    def _variant_set_name_build_fn(self, ui_prop: UsdPropertyUiEntry, *_) -> list[ui.AbstractValueModel]:
        # Build the VariantSetName widget
        # Build the simple string input for data-driven variant set name and a ComboBox for when there are
        # variants and no data-driven variant set name
        self.variant_set_name_string_layout = ui.HStack(spacing=0)
        with self.variant_set_name_string_layout:
            self.variant_set_name_string_model = self._token_builder(ui_prop)

        self.variant_set_name_token_layout = ui.HStack(spacing=0)
        with self.variant_set_name_token_layout:
            self.variant_set_name_token_model = self._combo_box_builder(
                ui_prop, VariantSetNamesTokenModel, self._on_variant_set_changed
            )

        self._update_variant_set_visibility()
        return [self.variant_set_name_string_model, self.variant_set_name_token_model]

    def _update_variant_set_visibility(self):
        # Show the string input if the prim is unknown or if the attribute has connections
        # otherwise show the token input
        if self.variant_set_name_string_layout and self.variant_set_name_token_layout:
            attr_has_connections = self._get_attr_has_connections("inputs:variantSetName")
            target_prim = self._get_target_prim()

            use_string = not target_prim or attr_has_connections
            self.variant_set_name_string_layout.visible = use_string
            self.variant_set_name_token_layout.visible = not use_string

    def _update_variant_set_name(self):
        # Update the variant set name widget visibility when the target prim changes
        self._update_variant_set_visibility()
        if self.variant_set_name_token_model:
            self.variant_set_name_token_model._set_dirty()  # noqa: PLW0212
        if self.variant_set_name_string_model:
            self.variant_set_name_string_model._set_dirty()  # noqa: PLW0212

    # ------------------------------------------------------------------------------------------
    def _variant_name_build_fn(self, ui_prop: UsdPropertyUiEntry, *_) -> list[ui.AbstractValueModel]:
        # Build the VariantName widget
        # Build the simple string input for data-driven variant name and a ComboBox for when there are
        # variants and no data-driven variant name
        self.variant_name_string_layout = ui.HStack(spacing=0)
        with self.variant_name_string_layout:
            self.variant_name_string_model = self._token_builder(ui_prop)

        self.variant_name_token_layout = ui.HStack(spacing=0)
        with self.variant_name_token_layout:
            self.variant_name_token_model = self._combo_box_builder(ui_prop, VariantNamesTokenModel)

        self._update_variant_name_visibility()
        return [self.variant_name_string_model, self.variant_name_token_model]

    def _update_variant_name_visibility(self):
        # Show the string input if the prim is unknown or if the attribute has connections
        # otherwise show the token input
        attr_has_connections = self._get_attr_has_connections("inputs:variantName")
        target_prim = self._get_target_prim()
        if self.variant_name_string_layout and self.variant_name_token_layout:
            use_string = not target_prim or attr_has_connections
            self.variant_name_string_layout.visible = use_string
            self.variant_name_token_layout.visible = not use_string

    def _update_variant_name(self):
        # Update the variant name widget visibility when the target prim changes
        self._update_variant_name_visibility()
        if self.variant_name_token_model:
            self.variant_name_token_model._set_dirty()  # noqa: PLW0212
        if self.variant_name_string_model:
            self.variant_name_string_model._set_dirty()  # noqa: PLW0212

    # ------------------------------------------------------------------------------------------
    def _variant_name_a_build_fn(self, ui_prop: UsdPropertyUiEntry, *_) -> list[ui.AbstractValueModel]:
        # Build the VariantName widget
        # Build the simple string input for data-driven variant name and a ComboBox for when there are
        # variants and no data-driven variant name
        self.variant_name_a_string_layout = ui.HStack(spacing=0)
        with self.variant_name_a_string_layout:
            self.variant_name_a_string_model = self._token_builder(ui_prop)

        self.variant_name_a_token_layout = ui.HStack(spacing=0)
        with self.variant_name_a_token_layout:
            self.variant_name_a_token_model = self._combo_box_builder(ui_prop, VariantNamesTokenModel)

        self._update_variant_name_a_visibility()
        return [self.variant_name_a_string_model, self.variant_name_a_token_model]

    def _update_variant_name_a_visibility(self):
        # Show the string input if the prim is unknown or if the attribute has connections
        # otherwise show the token input
        attr_has_connections = self._get_attr_has_connections("inputs:variantNameA")
        target_prim = self._get_target_prim()
        if self.variant_name_a_string_layout and self.variant_name_a_token_layout:
            use_string = not target_prim or attr_has_connections
            self.variant_name_a_string_layout.visible = use_string
            self.variant_name_a_token_layout.visible = not use_string

    def _update_variant_name_a(self):
        # Update the variant name widget visibility when the target prim changes
        self._update_variant_name_a_visibility()
        if self.variant_name_a_token_model:
            self.variant_name_a_token_model._set_dirty()  # noqa: PLW0212
        if self.variant_name_a_string_model:
            self.variant_name_a_string_model._set_dirty()  # noqa: PLW0212

    # ------------------------------------------------------------------------------------------
    def _variant_name_b_build_fn(self, ui_prop: UsdPropertyUiEntry, *_) -> list[ui.AbstractValueModel]:
        # Build the VariantName widget
        # Build the simple string input for data-driven variant name and a ComboBox for when there are
        # variants and no data-driven variant name
        self.variant_name_b_string_layout = ui.HStack(spacing=0)
        with self.variant_name_b_string_layout:
            self.variant_name_b_string_model = self._token_builder(ui_prop)

        self.variant_name_b_token_layout = ui.HStack(spacing=0)
        with self.variant_name_b_token_layout:
            self.variant_name_b_token_model = self._combo_box_builder(ui_prop, VariantNamesTokenModel)

        self._update_variant_name_b_visibility()
        return [self.variant_name_b_string_model, self.variant_name_b_token_model]

    def _update_variant_name_b_visibility(self):
        # Show the string input if the prim is unknown or if the attribute has connections
        # otherwise show the token input
        attr_has_connections = self._get_attr_has_connections("inputs:variantNameB")
        target_prim = self._get_target_prim()
        if self.variant_name_b_string_layout and self.variant_name_b_token_layout:
            use_string = not target_prim or attr_has_connections
            self.variant_name_b_string_layout.visible = use_string
            self.variant_name_b_token_layout.visible = not use_string

    def _update_variant_name_b(self):
        # Update the variant name widget visibility when the target prim changes
        self._update_variant_name_b_visibility()
        if self.variant_name_b_token_model:
            self.variant_name_b_token_model._set_dirty()  # noqa: PLW0212
        if self.variant_name_b_string_model:
            self.variant_name_b_string_model._set_dirty()  # noqa: PLW0212

    # ------------------------------------------------------------------------------------------
    def _on_target_prim_rel_changed(self, *_):
        # When the inputs:primRel token changes update the relevant widgets
        self.prim_rel_model._set_dirty()  # noqa: PLW0212
        self._update_variant_set_name()
        self._update_variant_name()
        self._update_variant_name_a()
        self._update_variant_name_b()

    def _on_variant_set_changed(self, _):
        # When the variantSet changes update the relevant widgets
        self._update_variant_name()
        self._update_variant_name_a()
        self._update_variant_name_b()

    def apply(self, props):
        # Apply the property values to the compute node
        def find_prop(name) -> Optional[UsdPropertyUiEntry]:
            try:
                return next((p for p in props if p.prop_name == name))
            except StopIteration:
                return None

        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop_functions = [
                    ("prim", self._prim_rel_build_fn),
                    ("variantSetName", self._variant_set_name_build_fn),
                    ("variantName", self._variant_name_build_fn),
                    ("variantNameA", self._variant_name_a_build_fn),
                    ("variantNameB", self._variant_name_b_build_fn),
                    ("blendedVariantName", None),
                    ("blend", None),
                    ("setVariant", None),
                    ("layerIdentifier", self._layer_identifier_build_fn),
                ]

                for prop_name, build_fn in prop_functions:
                    prop = find_prop(f"inputs:{prop_name}")
                    if prop:
                        override_display_name(prop)
                        CustomLayoutProperty(
                            prop.prop_name,
                            None,
                            build_fn=partial(build_fn, prop) if build_fn else None,
                        )

            with CustomLayoutGroup("Outputs"):
                for attr in ["exists", "success", "variantSetNames", "variantName"]:
                    prop = find_prop(f"outputs:{attr}")
                    if prop:
                        CustomLayoutProperty(prop.prop_name, pretty_name(prop.prop_name))

        return frame.apply(props)
