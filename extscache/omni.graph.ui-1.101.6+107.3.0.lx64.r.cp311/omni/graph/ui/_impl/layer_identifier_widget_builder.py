# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from enum import Enum, auto
from typing import Dict, List, Mapping, Type, Union

import carb.events
import omni.client.utils as clientutils
import omni.kit.usd.layers as layers
import omni.ui as ui
import omni.usd
from omni.kit.window.property.templates import HORIZONTAL_SPACING
from pxr import Pcp, Sdf, Usd

from .omnigraph_attribute_builder import OmniGraphPropertiesWidgetBuilder  # noqa: PLE0402
from .omnigraph_attribute_models import OmniGraphTfTokenAttributeModel  # noqa: PLE0402

CURRENT_AUTHORING_LAYER_TAG = "<Current Authoring Layer>"
SESSION_LAYER_TAG = "<Session Layer>"
ROOT_LAYER_TAG = "<Root Layer>"
INVALID_LAYER_TAG = "<Invalid Layer>"


def get_strongest_opinion_layer_from_node(node: Pcp.NodeRef, attr_name: str):
    layer_stack = node.layerStack
    spec_path = node.path.AppendProperty(attr_name)
    for layer in layer_stack.layers:
        attr_spec = layer.GetAttributeAtPath(spec_path)
        if attr_spec and attr_spec.HasInfo("default"):
            return layer

    for child_node in node.children:
        layer = get_strongest_opinion_layer_from_node(child_node, attr_name)
        if layer:
            return layer

    return None


def get_strongest_opinion_layer(stage: Usd.Stage, prim_path: Union[Sdf.Path, str], attr_name: str):
    prim = stage.GetPrimAtPath(prim_path)
    prim_index = prim.GetPrimIndex()
    return get_strongest_opinion_layer_from_node(prim_index.rootNode, attr_name)


class LayerType(Enum):
    CURRENT_AUTHORING_LAYER = auto()
    SESSION_LAYER = auto()
    ROOT_LAYER = auto()
    OTHER = auto()
    INVALID = auto()


class LayerItem(ui.AbstractItem):
    def __init__(self, layer: Union[Sdf.Layer, str], stage: Usd.Stage):
        super().__init__()
        self.layer = layer
        if layer is None:
            self.token = ""
            self.model = ui.SimpleStringModel(CURRENT_AUTHORING_LAYER_TAG)
            self.layer_type = LayerType.CURRENT_AUTHORING_LAYER
        else:
            prefix = ""
            suffix = ""
            if isinstance(layer, Sdf.Layer):
                if layer == stage.GetRootLayer():
                    self.layer_type = LayerType.ROOT_LAYER
                    self.token = ROOT_LAYER_TAG
                    suffix = f" {layer.identifier}"
                elif layer == stage.GetSessionLayer():
                    self.layer_type = LayerType.SESSION_LAYER
                    self.token = SESSION_LAYER_TAG
                    suffix = f" {layer.identifier}"
                else:
                    self.layer_type = LayerType.OTHER
                    # make the layer identifier relative to CURRENT EDIT TARGET layer
                    self.token = clientutils.make_relative_url_if_possible(
                        stage.GetEditTarget().GetLayer().realPath, layer.identifier
                    )

            elif isinstance(layer, str):
                self.token = layer
                self.layer_type = LayerType.INVALID
                prefix = f"{INVALID_LAYER_TAG} "

            self.model = ui.SimpleStringModel(prefix + self.token + suffix)


class LayerModel(OmniGraphTfTokenAttributeModel):
    def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], self_refresh: bool, metadata: dict):
        super().__init__(stage, attribute_paths, self_refresh, metadata)
        usd_context = omni.usd.get_context_from_stage(stage)
        self._layers = layers.get_layers(usd_context)
        self._layers_event_subscription = self._layers.get_event_stream().create_subscription_to_pop(
            self._on_layer_events, name="Layer Identifier Model"
        )

    def clean(self):
        self._layers_event_subscription = None
        super().clean()

    def _update_allowed_token(self, token_item=LayerItem):
        self._allowed_tokens = [  # noqa PLW0201
            LayerItem(None, self._stage)
        ]  # empty entry, meaning do not change target layer

        current_value_in_list = self._allowed_tokens[-1].token == self._value
        layer_stack = self._stage.GetLayerStack()
        for layer in layer_stack:
            self._allowed_tokens.append(LayerItem(layer, self._stage))
            if not current_value_in_list and self._is_value_equal_url(self._allowed_tokens[-1]):
                current_value_in_list = True

        if not current_value_in_list:
            layer = self._get_value_strongest_layer()

            self._allowed_tokens.append(
                LayerItem(clientutils.make_absolute_url_if_possible(layer.realPath, self._value), self._stage)
            )

    def _on_layer_events(self, event: carb.events.IEvent):
        payload = layers.get_layer_event_payload(event)
        if not payload:
            return

        if payload.event_type == layers.LayerEventType.SUBLAYERS_CHANGED:
            self._update_value(force=True)
            self._item_changed(None)

    def _update_index(self):
        index = -1
        for i, token in enumerate(self._allowed_tokens):
            if self._is_value_equal_url(token):
                index = i
                break
        return index

    def _is_value_equal_url(self, layer_item: LayerItem) -> bool:
        if layer_item.layer_type == LayerType.CURRENT_AUTHORING_LAYER:
            return self._value == ""
        if layer_item.layer_type == LayerType.SESSION_LAYER:
            return self._value == SESSION_LAYER_TAG
        if layer_item.layer_type == LayerType.ROOT_LAYER:
            return self._value == ROOT_LAYER_TAG

        identifier = layer_item.layer if layer_item.layer_type == LayerType.INVALID else layer_item.layer.identifier
        layer = self._get_value_strongest_layer()
        return clientutils.make_absolute_url_if_possible(
            self._stage.GetEditTarget().GetLayer().realPath, identifier
        ) == clientutils.make_absolute_url_if_possible(layer.realPath, self._value)

    def _get_value_strongest_layer(self):
        attributes = self._get_attributes()
        # only process the last entry for now
        attr_path = attributes[-1].GetPath()
        prim_path = attr_path.GetPrimPath()
        attr_name = attr_path.name
        return get_strongest_opinion_layer(attributes[-1].GetStage(), prim_path, attr_name)


class LayerIdentifierWidgetBuilder:
    @classmethod
    def build(
        cls,
        stage: Usd.Stage,
        attr_name: str,
        metadata: Mapping,
        property_type: Type,
        prim_paths: List[Sdf.Path],
        additional_label_kwargs: Dict = None,
        additional_widget_kwargs: Dict = None,
    ) -> LayerModel:
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            label_kwargs = {}
            if additional_label_kwargs:
                label_kwargs.update(additional_label_kwargs)
            label = OmniGraphPropertiesWidgetBuilder.create_label(attr_name, metadata, label_kwargs)
            model = LayerModel(stage, [path.AppendProperty(attr_name) for path in prim_paths], False, metadata)
            widget_kwargs = {"name": "choices"}
            if additional_widget_kwargs:
                widget_kwargs.update(additional_widget_kwargs)
            with ui.ZStack():
                value_widget = ui.ComboBox(model, **widget_kwargs)
                mixed_overlay = OmniGraphPropertiesWidgetBuilder.create_mixed_text_overlay()

            OmniGraphPropertiesWidgetBuilder.create_control_state(
                model=model, value_widget=value_widget, mixed_overlay=mixed_overlay, **widget_kwargs, label=label
            )
            return model
