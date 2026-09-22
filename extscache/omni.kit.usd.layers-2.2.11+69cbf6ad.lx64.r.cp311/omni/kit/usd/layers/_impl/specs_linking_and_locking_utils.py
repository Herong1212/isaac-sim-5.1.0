# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "link_specs", "unlink_specs", "unlink_specs_to_layers", "unlink_specs_from_all_layers",
    "unlink_all_specs", "get_spec_layer_links", "get_spec_links_for_layers",
    "get_all_spec_links", "is_spec_linked", "lock_specs", "unlock_specs",
    "unlock_all_specs", "get_all_locked_specs", "is_spec_locked"
]

import carb

from typing import Union, List, Dict
from pxr import Sdf

from .extension import get_layers


def __to_str_list(pathOrPaths: Union[Union[str, Sdf.Path], List[Union[str, Sdf.Path]]]):
    paths = []
    if pathOrPaths:
        if isinstance(pathOrPaths, str) or isinstance(pathOrPaths, Sdf.Path):
            paths = [str(pathOrPaths)]
        else:
            paths = [str(path) for path in pathOrPaths]

    return paths


def link_specs(
    usd_context,
    spec_paths: Union[Union[str, Sdf.Path], List[Union[str, Sdf.Path]]],
    layer_identifiers: Union[str, List[str]],
    hierarchy=False,
) -> Dict[str, List[str]]:
    paths = __to_str_list(spec_paths)
    identifiers = __to_str_list(layer_identifiers)

    layers = get_layers(usd_context)
    if not layers:
        carb.log_warn(f"Cannot link specs as corresponding layers instance cannot be found.")
        return None

    specs_linking = layers.get_specs_linking()
    if not specs_linking.is_enabled():
        carb.log_warn(f"Cannot link specs as it's not in SPECS_LINKING mode.")
        return None

    spec_path_to_layers: Dict[str, List[str]] = {}
    for path in paths:
        for identifier in identifiers:
            linked_spec_paths = specs_linking.link_spec(path, identifier, hierarchy)
            for spec_path in linked_spec_paths:
                if spec_path not in spec_path_to_layers:
                    spec_path_to_layers[spec_path] = [identifier]
                else:
                    spec_path_to_layers[spec_path].append(identifier)

    return spec_path_to_layers


def unlink_specs(
    usd_context,
    spec_paths: Union[Union[str, Sdf.Path], List[Union[str, Sdf.Path]]],
    layer_identifiers: Union[str, List[str]],
    hierarchy=False,
) -> Dict[str, List[str]]:
    paths = __to_str_list(spec_paths)
    identifiers = __to_str_list(layer_identifiers)

    layers = get_layers(usd_context)
    if not layers:
        carb.log_warn(f"Cannot unlink specs as corresponding layers instance cannot be found.")
        return None

    specs_linking = layers.get_specs_linking()
    if not specs_linking.is_enabled():
        carb.log_warn(f"Cannot unlink specs as it's not in SPECS_LINKING mode.")
        return None

    spec_path_to_layers: Dict[str, List[str]] = {}
    for path in paths:
        for identifier in identifiers:
            unlinked_spec_paths = specs_linking.unlink_spec(path, identifier, hierarchy)
            for spec_path in unlinked_spec_paths:
                if spec_path not in spec_path_to_layers:
                    spec_path_to_layers[spec_path] = [identifier]
                else:
                    spec_path_to_layers[spec_path].append(identifier)

    return spec_path_to_layers


def unlink_specs_to_layers(usd_context, layer_identifiers: Union[str, List[str]]) -> Dict[str, List[str]]:
    identifiers = __to_str_list(layer_identifiers)

    layers = get_layers(usd_context)
    if not layers:
        carb.log_warn(f"Cannot unlink specs as corresponding layers instance cannot be found.")
        return None

    specs_linking = layers.get_specs_linking()
    if not specs_linking.is_enabled():
        carb.log_warn(f"Cannot unlink specs as it's not in SPECS_LINKING mode.")
        return None

    layer_to_spec_paths: Dict[str, List[str]] = {}
    for identifier in identifiers:
        spec_paths = specs_linking.unlink_specs_to_layer(identifier)
        layer_to_spec_paths.update(spec_paths)

    return layer_to_spec_paths


def unlink_specs_from_all_layers(
    usd_context, spec_paths: Union[str, List[str]], hierarchy=False
) -> Dict[str, List[str]]:
    paths = __to_str_list(spec_paths)

    layers = get_layers(usd_context)
    if not layers:
        carb.log_warn(f"Cannot unlink specs as corresponding layers instance cannot be found.")
        return None

    specs_linking = layers.get_specs_linking()
    if not specs_linking.is_enabled():
        carb.log_warn(f"Cannot unlink specs as it's not in SPECS_LINKING mode.")
        return None

    spec_path_to_layers: Dict[str, List[str]] = {}
    for path in paths:
        spec_paths = specs_linking.unlink_spec_from_all_layers(path, hierarchy)
        spec_path_to_layers.update(spec_paths)

    return spec_path_to_layers


def unlink_all_specs(usd_context):
    layers = get_layers(usd_context)
    if not layers:
        carb.log_warn(f"Cannot unlink specs as corresponding layers instance cannot be found.")
        return None

    specs_linking = layers.get_specs_linking()
    if not specs_linking.is_enabled():
        carb.log_warn(f"Cannot unlink specs as it's not in SPECS_LINKING mode.")
        return None

    specs_linking.unlink_all_specs()


def get_spec_layer_links(
    usd_context, spec_paths: Union[Union[str, Sdf.Path], List[Union[str, Sdf.Path]]], hierarchy=False
) -> Dict[str, List[str]]:
    paths = __to_str_list(spec_paths)

    layers = get_layers(usd_context)
    if not layers:
        carb.log_warn(f"Cannot get links as corresponding layers instance cannot be found.")
        return None

    specs_linking = layers.get_specs_linking()
    spec_path_to_layers = {}
    for path in paths:
        spec_path_to_layers.update(specs_linking.get_spec_layer_links(path, hierarchy))

    return spec_path_to_layers


def get_spec_links_for_layers(usd_context, layer_identifiers: Union[str, List[str]]) -> Dict[str, List[str]]:
    identifiers = __to_str_list(layer_identifiers)

    layers = get_layers(usd_context)
    if not layers:
        carb.log_warn(f"Cannot get links as corresponding layers instance cannot be found.")
        return None

    specs_linking = layers.get_specs_linking()
    layer_to_spec_paths: Dict[str, List[str]] = {}
    for layer_identifier in identifiers:
        spec_paths = specs_linking.get_spec_links_for_layer(layer_identifier)
        if layer_identifier not in layer_to_spec_paths:
            layer_to_spec_paths[layer_identifier] = spec_paths
        else:
            layer_to_spec_paths[layer_identifier].extend(spec_paths)

    return layer_to_spec_paths


def get_all_spec_links(usd_context) -> Dict[str, List[str]]:
    layers = get_layers(usd_context)
    if not layers:
        carb.log_warn(f"Cannot get links as corresponding layers instance cannot be found.")
        return None

    specs_linking = layers.get_specs_linking()
    return specs_linking.get_all_spec_links()


def is_spec_linked(usd_context, spec_path: Union[str, Sdf.Path], layer_identifier: str = "") -> bool:
    path = __to_str_list(spec_path)
    if not path:
        return False

    layers = get_layers(usd_context)
    if not layers:
        carb.log_warn(f"Cannot check link state as corresponding layers instance cannot be found.")
        return None

    specs_linking = layers.get_specs_linking()
    return specs_linking.is_spec_linked(path[0], layer_identifier)


def lock_specs(
    usd_context, spec_paths: Union[Union[str, Sdf.Path], List[Union[str, Sdf.Path]]], hierarchy=False
) -> List[str]:
    paths = __to_str_list(spec_paths)

    layers = get_layers(usd_context)
    if not layers:
        carb.log_warn(f"Cannot lock specs as corresponding layers instance cannot be found.")
        return None

    locked_spec_paths = []
    specs_locking = layers.get_specs_locking()
    for path in paths:
        locked_spec_paths.extend(specs_locking.lock_spec(path, hierarchy))

    return locked_spec_paths


def unlock_specs(usd_context, spec_paths: Union[str, List[str]], hierarchy=False) -> List[str]:
    paths = __to_str_list(spec_paths)

    layers = get_layers(usd_context)
    if not layers:
        carb.log_warn(f"Cannot unlock specs as corresponding layers instance cannot be found.")
        return None

    unlocked_spec_paths = []
    specs_locking = layers.get_specs_locking()
    for path in paths:
        unlocked_spec_paths.extend(specs_locking.unlock_spec(path, hierarchy))

    return unlocked_spec_paths


def unlock_all_specs(usd_context):
    layers = get_layers(usd_context)
    if not layers:
        carb.log_warn(f"Cannot unlock specs as corresponding layers instance cannot be found.")
        return None

    specs_locking = layers.get_specs_locking()
    specs_locking.unlock_all_specs()


def get_all_locked_specs(usd_context) -> List[str]:
    layers = get_layers(usd_context)
    if not layers:
        carb.log_warn(f"Cannot get lock states as corresponding layers instance cannot be found.")
        return None

    specs_locking = layers.get_specs_locking()

    return specs_locking.get_all_locked_specs()


def is_spec_locked(usd_context, spec_path: Union[str, Sdf.Path]) -> bool:
    path = __to_str_list(spec_path)
    if not path:
        return False

    layers = get_layers(usd_context)
    if not layers:
        carb.log_warn(f"Cannot check lock state as corresponding layers instance cannot be found.")
        return None

    specs_locking = layers.get_specs_locking()
    return specs_locking.is_spec_locked(path[0])
