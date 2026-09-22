# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["SpecsLocking"]

import carb.dictionary
from pxr import Sdf
from typing import Union, List

from .._omni_kit_usd_layers import acquire_specs_locking_interface, release_specs_locking_interface, ILayersInstance


class SpecsLocking:
    def __init__(self, layers_instance: ILayersInstance, usd_context) -> None:
        self._layers_instance = layers_instance
        self._usd_context = usd_context
        self._specs_locking_interface = acquire_specs_locking_interface()
        self._dictionary = carb.dictionary.get_dictionary()

    @property
    def usd_context(self):
        return self._usd_context

    def _destroy(self):
        self._layers_instance = None
        release_specs_locking_interface(self._specs_locking_interface)

    def _populate_all_paths(self, item: carb.dictionary.Item):
        all_locked_spec_paths = []
        count = self._dictionary.get_item_child_count(item)
        for i in range(count):
            spec_path_item = self._dictionary.get_item_child_by_index(item, i)
            spec_path = self._dictionary.get_as_string(spec_path_item)
            all_locked_spec_paths.append(spec_path)

        return all_locked_spec_paths

    def lock_spec(self, spec_path: Union[str, Sdf.Path], hierarchy: bool = False) -> List[str]:
        item = self._specs_locking_interface.lock_spec(self._layers_instance, str(spec_path), hierarchy)
        if not item:
            return []

        all_locked_spec_paths = self._populate_all_paths(item)
        self._dictionary.destroy_item(item)

        return all_locked_spec_paths

    def unlock_spec(self, spec_path: Union[str, Sdf.Path], hierarchy: bool = False) -> List[str]:
        item = self._specs_locking_interface.unlock_spec(self._layers_instance, str(spec_path), hierarchy)
        if not item:
            return []

        all_unlocked_spec_paths = self._populate_all_paths(item)
        self._dictionary.destroy_item(item)

        return all_unlocked_spec_paths

    def unlock_all_specs(self):
        self._specs_locking_interface.unlock_all_specs(self._layers_instance)

    def get_all_locked_specs(self) -> List[str]:
        item = self._specs_locking_interface.get_all_locked_specs(self._layers_instance)
        if not item:
            return []

        all_locked_spec_paths = self._populate_all_paths(item)
        self._dictionary.destroy_item(item)

        return all_locked_spec_paths

    def is_spec_locked(self, spec_path: Union[str, Sdf.Path]) -> bool:
        return self._specs_locking_interface.is_spec_locked(self._layers_instance, str(spec_path))
