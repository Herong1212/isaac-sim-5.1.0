# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["SpecsLinking"]

import carb.dictionary
from pxr import Sdf
from typing import Union, List, Dict

from .._omni_kit_usd_layers import acquire_specs_linking_interface, release_specs_linking_interface, ILayersInstance


class SpecsLinking:
    def __init__(self, layers_instance: ILayersInstance, usd_context) -> None:
        self._layers_instance = layers_instance
        self._usd_context = usd_context
        self._specs_linking_interface = acquire_specs_linking_interface()
        self._dictionary = carb.dictionary.get_dictionary()

    @property
    def usd_context(self):
        return self._usd_context

    def _destroy(self):
        self._layers_instance = None
        release_specs_linking_interface(self._specs_linking_interface)

    def _populate_all_paths(self, item: carb.dictionary.Item):
        layer_spec_paths = {}
        count = self._dictionary.get_item_child_count(item)
        for i in range(count):
            sub_item = self._dictionary.get_item_child_by_index(item, i)
            identifier_item = self._dictionary.get_item(sub_item, "key")
            spec_paths_item = self._dictionary.get_item(sub_item, "value")
            identifier_or_spec_path = self._dictionary.get_as_string(identifier_item)
            value_count = self._dictionary.get_item_child_count(spec_paths_item)
            all_paths = []
            for j in range(value_count):
                spec_path_item = self._dictionary.get_item_child_by_index(spec_paths_item, j)
                spec_path = self._dictionary.get_as_string(spec_path_item)
                all_paths.append(spec_path)

            layer_spec_paths[identifier_or_spec_path] = all_paths

        return layer_spec_paths

    def is_enabled(self) -> bool:
        return self._specs_linking_interface.is_enabled(self._layers_instance)

    def link_spec(self, spec_path: Union[str, Sdf.Path], layer_identifier: str, hierarchy: bool = False) -> List[str]:
        item = self._specs_linking_interface.link_spec(
            self._layers_instance, str(spec_path), layer_identifier, hierarchy
        )
        if not item:
            return []

        all_spec_paths = self._populate_all_paths(item)
        self._dictionary.destroy_item(item)

        return all_spec_paths.get(layer_identifier, [])

    def unlink_spec(self, spec_path: Union[str, Sdf.Path], layer_identifier: str, hierarchy: bool = False) -> List[str]:
        item = self._specs_linking_interface.unlink_spec(
            self._layers_instance, str(spec_path), layer_identifier, hierarchy
        )
        if not item:
            return []

        all_spec_paths = self._populate_all_paths(item)
        self._dictionary.destroy_item(item)

        return all_spec_paths.get(layer_identifier, [])

    def unlink_spec_from_all_layers(
        self, spec_path: Union[str, Sdf.Path], hierarchy: bool = False
    ) -> Dict[str, List[str]]:
        item = self._specs_linking_interface.unlink_spec_from_all_layers(
            self._layers_instance, str(spec_path), hierarchy
        )
        if not item:
            return {}

        spec_to_layers = self._populate_all_paths(item)
        self._dictionary.destroy_item(item)

        return spec_to_layers

    def unlink_specs_to_layer(self, layer_identifier: str) -> List[str]:
        item = self._specs_linking_interface.unlink_specs_to_layer(self._layers_instance, layer_identifier)
        if not item:
            return []

        all_spec_paths = self._populate_all_paths(item)
        self._dictionary.destroy_item(item)

        return all_spec_paths.get(layer_identifier, [])

    def unlink_all_specs(self):
        self._specs_linking_interface.unlink_all_specs(self._layers_instance)

    def get_spec_layer_links(self, spec_path: Union[str, Sdf.Path], hierarchy: bool = False):
        item = self._specs_linking_interface.get_spec_layer_links(self._layers_instance, str(spec_path), hierarchy)
        if not item:
            return {}

        spec_to_layers = self._populate_all_paths(item)
        self._dictionary.destroy_item(item)

        return spec_to_layers

    def get_spec_links_for_layer(self, layer_identifier: str) -> List[str]:
        item = self._specs_linking_interface.get_spec_links_for_layer(self._layers_instance, layer_identifier)
        if not item:
            return []

        result = self._populate_all_paths(item)
        self._dictionary.destroy_item(item)

        return result.get(layer_identifier, [])

    def get_all_spec_links(self):
        item = self._specs_linking_interface.get_all_spec_links(self._layers_instance)
        if not item:
            return {}

        spec_to_layers = self._populate_all_paths(item)
        self._dictionary.destroy_item(item)

        return spec_to_layers

    def is_spec_linked(self, spec_path: str, layer_identifier: str = ""):
        return self._specs_linking_interface.is_spec_linked(self._layers_instance, spec_path, layer_identifier)
