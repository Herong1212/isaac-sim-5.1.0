# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "get_all_sublayers", "is_layer_locked", "is_layer_writable", "get_dirty_layers", "get_edit_target_identifier",
    "set_edit_target_by_identifier", "stitch_prim_specs"
]

import omni.usd
import omni.client
from pxr import Sdf, Usd, Trace
from typing import Dict, List, Union, Set


def _layer_traverse(layer, layer_identifier: str, unique_layer_set: Set[str], include_only_omni_layers: bool, include_anonymous_layers: bool) -> List[str]:
    # It has circular sublayer tree, like sub1 -> sub2 -> sub1
    if layer_identifier in unique_layer_set:
        return []

    # TODO: to support only omni layers, don't need to change here
    if include_only_omni_layers and not omni.client.is_omni_objects_enabled(layer_identifier):
        results = []
    elif not include_anonymous_layers and Sdf.Layer.IsAnonymousLayerIdentifier(layer_identifier):
        results = []
    else:
        results = [layer_identifier]

    unique_layer_set.add(layer_identifier)

    if layer:
        for sublayer in layer.subLayerPaths:
            sublayer_identifier = layer.ComputeAbsolutePath(sublayer)
            sublayer = Sdf.Find(sublayer_identifier)
            results.extend(_layer_traverse(sublayer, sublayer_identifier, unique_layer_set, include_only_omni_layers, include_anonymous_layers))

    unique_layer_set.discard(layer_identifier)

    return results


def get_all_sublayers(stage, include_session_layers=False, include_only_omni_layers=False, include_anonymous_layers=True) -> List[str]:
    """Gets all sublayers from local layer stack of the stage ranking from strongest to weakest."""
    if not stage:
        return []

    unique_layer_set = set([])
    if include_session_layers:
        session_layer = stage.GetSessionLayer()
        all_layers = _layer_traverse(session_layer, session_layer.identifier, unique_layer_set, include_only_omni_layers, include_anonymous_layers)
    else:
        all_layers = []

    root_layer = stage.GetRootLayer()
    all_layers.extend(
        _layer_traverse(root_layer, root_layer.identifier, unique_layer_set, include_only_omni_layers, include_anonymous_layers)
    )

    return all_layers


def is_layer_locked(usd_context, layer_identifier: str) -> bool:
    """Checkes if layer is locked or not in this usd context.

    Layer lock is a customized concept in Kit that's not from USD. It's used to complement the concept
    of file permission. Unlike the writable permission on file system, lock is bound
    to stage. So a layer may be locked in this stage, but not for other stages. Lock status
    is persistent across sessions, and saved as a flag inside the custom data of root layer.
    """

    LAYER_OMNI_CUSTOM_KEY = "omni_layer"
    LAYER_LOCK_STATUS_CUSTOM_KEY = "locked"
    stage = usd_context.get_stage()
    if not stage:
        return False

    root_layer = stage.GetRootLayer()
    custom_data = root_layer.customLayerData
    if LAYER_OMNI_CUSTOM_KEY in custom_data:
        omni_data = custom_data[LAYER_OMNI_CUSTOM_KEY]
        if LAYER_LOCK_STATUS_CUSTOM_KEY in omni_data:
            data = omni_data[LAYER_LOCK_STATUS_CUSTOM_KEY]
            for relative_path, value in data.items():
                absolute_path = root_layer.ComputeAbsolutePath(relative_path)
                if omni.client.equal_urls(layer_identifier, absolute_path):
                    return value

    return False


def is_layer_writable(layer_identifier: str) -> bool:  # pragma: no cover
    """Checks if layer is writable on file system."""

    layer = Sdf.Find(layer_identifier)
    if not layer:
        return False

    if layer.anonymous:
        return True

    # path with explicit branch/checkpoint is read-only
    client_url = omni.client.break_url(layer_identifier)
    if client_url.query:
        return False

    result, entry = omni.client.stat(layer_identifier)
    if result != omni.client.Result.OK:
        # Error doing the stat
        return False

    if not entry.access & omni.client.AccessFlags.WRITE:
        # No access
        return False

    if entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN:
        # This is a folder
        return False

    if entry.flags & omni.client.ItemFlags.IS_INSIDE_MOUNT:
        # Inside a mounted folder
        return False

    if entry.flags & omni.client.ItemFlags.WRITEABLE_FILE:
        # Writeable file
        return True

    if entry.flags & omni.client.ItemFlags.IS_OMNI_OBJECT:
        # Omni Object
        return True

    # Some other type
    return False


def get_dirty_layers(stage: Usd.Stage, include_root_layer=True):
    """Gets all dirty layers that have unsaved changes."""

    dirty_layers = []
    root_layer_identifier = stage.GetRootLayer().identifier
    all_sublayer_identifiers = omni.usd.get_all_sublayers(stage)
    for sublayer_identifier in all_sublayer_identifiers:
        if not include_root_layer and sublayer_identifier == root_layer_identifier:
            continue

        if sublayer_identifier.endswith(".live"):
            continue

        if sublayer_identifier.startswith("metrics:"):
            continue

        layer = Sdf.Find(sublayer_identifier)
        if layer and not layer.anonymous and layer.dirty:
            if sublayer_identifier not in dirty_layers:
                dirty_layers.append(sublayer_identifier)

    return dirty_layers


def get_edit_target_identifier(stage: Usd.Stage) -> str:
    """
    Gets the layer identifier of current edit target.

    Args:
        stage (Usd.Stage): Stage handle

    Returns:
        Layer identifier or empty string if edit target is not set.
    """

    if not stage:
        return ""

    layer = stage.GetEditTarget().GetLayer()
    if not layer:
        return ""

    return layer.identifier


def set_edit_target_by_identifier(stage: Usd.Stage, layer_identifier: str):
    """
    Sets the edit target of stage by layer identifier.

    Args:
        stage (Usd.Stage): Stage handle
        layer_identifier (str): Layer identifier

    Returns:
        True if success, false if layer cannot be found, or layer is not in
        the layer statck of stage.
    """
    layer = Sdf.Find(layer_identifier)
    if not layer:
        return False

    if stage.HasLocalLayer(layer):
        edit_target = stage.GetEditTargetForLocalLayer(layer)
        stage.SetEditTarget(edit_target)

        return True

    return False


@Trace.TraceFunction
def stitch_prim_specs(
    stage: Usd.Stage, prim_path: Union[str, Sdf.Path], target_layer: Sdf.Layer, target_prim_path: str=None,
    include_references_or_payloads=False
):
    """
    Sitches prim specs specified by path scattered in all sublayers and all its children to target layer.

    Args:
        stage (Usd.Stage): Stage handle.
        prim_path (str): Prim path to be stitched.
        target_layer (Sdf.Layer): Target layer to save the stitching results.
        target_prim_path (str): Target prim path. If it's empty or none, it will be the prim_path.
        include_references_or_payloads: If prim is defined inside references or payloads, and this is
            True, it will also stitch the defs from references or payloads, too.
    """
    prim_path = Sdf.Path(prim_path)
    if not target_prim_path:
        target_prim_path = prim_path

    def merge_prim_specs(target_layer, src_layer, dst_strong_than_src, prim_path):
        src_prim_spec = src_layer.GetPrimAtPath(prim_path)
        if not src_prim_spec:
            return

        omni.usd.merge_prim_spec(
            target_layer.identifier, src_layer.identifier,
            prim_path.pathString, dst_strong_than_src
        )

    from_reference_or_payload = False
    introducing_layer = None
    prim_spec_in_def_layer = None
    if include_references_or_payloads:
        usd_prim = stage.GetPrimAtPath(prim_path)
        if usd_prim:
            introducing_layer, introducing_prim_path = omni.usd.get_introducing_layer(usd_prim)
            for prim_spec in usd_prim.GetPrimStack():
                if prim_spec.specifier == Sdf.SpecifierDef:
                    if introducing_layer != prim_spec.layer and introducing_prim_path != prim_path:
                        from_reference_or_payload = True
                        prim_spec_in_def_layer = prim_spec
                        break

    sublayers = get_all_sublayers(stage, True)
    with Sdf.ChangeBlock():
        temp_layer = Sdf.Layer.CreateAnonymous()
        Sdf.CreatePrimInLayer(temp_layer, prim_path)
        for sublayer_identifier in sublayers:
            if (
                from_reference_or_payload and
                introducing_layer and
                introducing_layer.identifier == sublayer_identifier
            ):
                sublayer = Sdf.Layer.CreateAnonymous()
                Sdf.CreatePrimInLayer(sublayer, prim_path)
                Sdf.CopySpec(
                    prim_spec_in_def_layer.layer, prim_spec_in_def_layer.path,
                    sublayer, prim_path
                )
            else:
                sublayer = Sdf.Find(sublayer_identifier)

            if sublayer:
                merge_prim_specs(temp_layer, sublayer, True, prim_path)

        Sdf.CreatePrimInLayer(target_layer, target_prim_path)
        omni.usd.resolve_paths(target_layer.identifier, temp_layer.identifier, True, True)
        Sdf.CopySpec(temp_layer, prim_path, target_layer, target_prim_path)

    return True
