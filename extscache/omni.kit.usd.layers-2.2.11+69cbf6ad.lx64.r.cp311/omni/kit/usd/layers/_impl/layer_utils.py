# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["LayerUtils"]

import asyncio
import os
import carb
import omni
import omni.client

from .path_utils import PathUtils
from pxr import Sdf, Usd, UsdUtils
from typing import List, Set, Union


class LayerUtils:
    """LayerUtils provides utilities for operating layers."""

    LAYER_OMNI_CUSTOM_KEY = "omni_layer"
    LAYER_MUTENESS_CUSTOM_KEY = "muteness"
    LAYER_LOCK_STATUS_CUSTOM_KEY = "locked"
    LAYER_NAME_CUSTOM_KEY = "custom_name"
    LAYER_AUTHORING_LAYER_CUSTOM_KEY = "authoring_layer"

    @staticmethod
    def create_sublayer(layer: Sdf.Layer, sublayer_position: int, layer_identifier: str):
        """Creates new sublayer at specific position.

        Args:
            layer (Sdf.Layer): Layer handle.
            sublayer_position: Position to create the new layer.
                               Position should be -1 (the last position) or above 0.
                               If position == -1 or position > len(layer.subLayerPaths), it will create the sublayer at the end.
                               Any other position will be treated as invalid index.
            layer_identifier: New layer path. If it's empty or None, it will create anonymous layer.

        Return:
            New sublayer handle or None if sublayer_position is not valid.
        """

        if sublayer_position != -1 and sublayer_position < 0:
            return None

        if sublayer_position > len(layer.subLayerPaths) or sublayer_position == -1:
            sublayer_position = len(layer.subLayerPaths)

        if layer_identifier:
            new_layer = Sdf.Layer.FindOrOpen(layer_identifier)
            if new_layer:
                new_layer.Clear()
            else:
                new_layer = Sdf.Layer.CreateNew(layer_identifier)
        else:
            new_layer = Sdf.Layer.CreateAnonymous()

        if new_layer:
            relative_path = PathUtils.compute_relative_path(layer.identifier, new_layer.identifier)
            layer.subLayerPaths.insert(sublayer_position, relative_path)

        return new_layer

    @staticmethod
    def insert_sublayer(layer: Sdf.Layer, sublayer_position: int, layer_identifier: str, check_empty_layer=True):
        """Inserts new sublayer at specific position.

        Args:
            layer (Sdf.Layer): Layer handle.
            sublayer_position: Position to insert the new layer.
                               Position should be -1 (the last position) or above 0.
                               If position == -1 or position > len(layer.subLayerPaths), it will insert the sublayer at the end.
                               Any other position will be treated as invalid index.
            layer_identifier: New layer path.

        Return:
            Sublayer handle or None if sublayer_position is not valid or layer_identifier is empty or inserted layer is not existed.
        """

        if sublayer_position != -1 and sublayer_position < 0:
            return None

        if sublayer_position > len(layer.subLayerPaths) or sublayer_position == -1:
            sublayer_position = len(layer.subLayerPaths)

        new_layer = Sdf.Layer.FindOrOpen(layer_identifier)
        if new_layer:
            relative_path = PathUtils.compute_relative_path(layer.identifier, new_layer.identifier)
            layer.subLayerPaths.insert(sublayer_position, relative_path)
        else:
            carb.log_error(f"Failed to insert sublayer {layer_identifier} since it cannot be opened.")

        return new_layer

    @staticmethod
    def replace_sublayer(layer: Sdf.Layer, sublayer_position: int, layer_identifier: str):
        """Replaces new sublayer at specific position.

        Args:
            layer (Sdf.Layer): Layer handle.
            sublayer_position: Position to insert the new layer.
                               Position should be less than len(layer.subLayerPaths).
                               Any other position will be treated as invalid index.
            layer_identifier: New layer path.

        Return:
            Sublayer handle or None if sublayer_position is not valid or layer_identifier is empty or replaced layer is not existed.
        """

        if sublayer_position < 0 or sublayer_position >= len(layer.subLayerPaths):
            return None

        new_layer = Sdf.Layer.FindOrOpen(layer_identifier)
        if new_layer:
            relative_path = PathUtils.compute_relative_path(layer.identifier, new_layer.identifier)
            layer.subLayerPaths[sublayer_position] = relative_path
        else:
            carb.log_error(f"Failed to replace sublayer with {layer_identifier} since it cannot be opened.")

        return new_layer

    @staticmethod
    def get_custom_layer_name(layer: Sdf.Layer):
        """Gets the custom name of layer. This name is saved inside the custom data of layer."""

        custom_data = layer.customLayerData
        name = None
        if LayerUtils.LAYER_OMNI_CUSTOM_KEY in custom_data:
            omni_data = custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY]
            if LayerUtils.LAYER_NAME_CUSTOM_KEY in omni_data:
                name = omni_data[LayerUtils.LAYER_NAME_CUSTOM_KEY]

        if not name:
            name = os.path.basename(layer.identifier)

        return name

    @staticmethod
    def set_custom_layer_name(layer: Sdf.Layer, name: str):
        """
        Sets the custom name of layer, or clear it if name is empty or None.
        The name is saved inside the custom data of layer and can only be
        consumed by Kit application.
        """

        custom_data = layer.customLayerData
        if name:
            if LayerUtils.LAYER_OMNI_CUSTOM_KEY not in custom_data:
                custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY] = {}

            omni_data = custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY]
            omni_data[LayerUtils.LAYER_NAME_CUSTOM_KEY] = name
            custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY] = omni_data
            layer.customLayerData = custom_data
        else:
            if LayerUtils.LAYER_OMNI_CUSTOM_KEY not in custom_data:
                return

            omni_data = custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY]
            if LayerUtils.LAYER_NAME_CUSTOM_KEY in omni_data:
                del omni_data[LayerUtils.LAYER_NAME_CUSTOM_KEY]
                custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY] = omni_data
                layer.customLayerData = custom_data

    @staticmethod
    def transfer_layer_content(
        source_layer: Sdf.Layer, target_layer: Sdf.Layer, copy_custom_data=True, skip_sublayers=True
    ):
        """
        Transfer layer content from source layer to target layer with re-pathing all external
        dependencies.

        Args:
            source_layer (Sdf.Layer): Source layer handle.
            target_layer (Sdf.Layer): Target layer handle.
            copy_custom_data (bool): Whether copying layer metadata or not.
            skip_sublayers (bool): Whether skipping to copy sublayers or not if copy_custom_data is True.
        """

        for root_prim in source_layer.rootPrims:
            Sdf.CopySpec(source_layer, root_prim.path, target_layer, root_prim.path)
        if copy_custom_data:
            UsdUtils.CopyLayerMetadata(source_layer, target_layer, skip_sublayers)
        LayerUtils.resolve_paths(source_layer, target_layer)

    @staticmethod
    def resolve_paths(
        base_layer: Sdf.Layer,
        target_layer: Sdf.Layer,
        store_relative_path=True,
        relative_to_base_layer=False,
        copy_sublayer_offsets=False,
    ):
        """Resolve all paths from References, Sublayers and AssetPaths of target layer based on source layer.
        This function is used normally when you transfer the content from source layer to target layer that
        are not in the same directory. So it needs to resolve all references so that they point to correct
        location.

        Args:
            base_layer (Sdf.Layer): Source layer that references in target layer based on.
            target_layer (Sdf.Layer): Target layer to resolve.
            store_relative_path (bool): True to store relative path, or False to store absolute path.
                                      if relative path cannot be computed (like source layer and
                                      target are not in the same domain), it will save absolute paths.
            relative_to_base_layer (bool): True if the relative path is computed against the target_layer.
                                      False otherwise.
            copy_sublayer_offsets (bool): True to copy sublayer offsets and scales from base to target.
        """
        omni.usd.resolve_paths(
            base_layer.identifier,
            target_layer.identifier,
            store_relative_path,
            relative_to_base_layer,
            copy_sublayer_offsets,
        )

    @staticmethod
    def get_sublayer_position_in_parent(parent_layer_identifier: str, layer_identifier: str):
        """
        Gets the sublayer position in the parent layer.

        Args:
            parent_layer_identifier (str): Parent layer identifier.
            layer_identifier (str): layer identifier to query.

        Returns:
            Position of layer in the subLayerPaths of the parent, or -1 if it cannot be found.
        """

        parent_layer = Sdf.Find(parent_layer_identifier)
        if not parent_layer:
            return -1

        sublayer_paths = parent_layer.subLayerPaths
        layer_identifier = parent_layer.ComputeAbsolutePath(layer_identifier)
        for i in range(len(sublayer_paths)):
            sublayer_path = sublayer_paths[i]
            sublayer_identifier = parent_layer.ComputeAbsolutePath(sublayer_path)
            if sublayer_identifier == layer_identifier:
                return i

        return -1

    @staticmethod
    def has_prim_spec(layer_identifier: str, prim_spec_path):
        layer = Sdf.Find(layer_identifier)
        if not layer:
            return False

        prim_spec = layer.GetPrimAtPath(prim_spec_path)

        return not not prim_spec

    @staticmethod
    def get_sublayer_identifier(layer_identifier: str, sublayer_position: int):
        """
        Gets the sublayer identifier at specific postion with validality.

        Args:
            layer_identifier (str): Parent layer identifier.
            sublayer_position (int): Position of sublayer. It must be -1, which means to
            return the last item. Or it should be equal or above 0.

        Returns:
            None if sublayer_position is invalid or overflow. Or sublayer identifier otherwise.
        """

        parent_layer = Sdf.Find(layer_identifier)
        if not parent_layer:
            return None

        sublayer_paths = parent_layer.subLayerPaths
        if len(sublayer_paths) == 0:
            return None

        if sublayer_position >= len(sublayer_paths) or (sublayer_position != -1 and sublayer_position < 0):
            return None

        sublayer_identifier = parent_layer.ComputeAbsolutePath(sublayer_paths[sublayer_position])

        return sublayer_identifier

    @staticmethod
    def restore_authoring_layer_from_custom_data(stage):
        root_layer = stage.GetRootLayer()
        try:
            # OM-57080: it will through exception if meta includes invalid fields.
            custom_data = root_layer.customLayerData
            if LayerUtils.LAYER_OMNI_CUSTOM_KEY in custom_data:
                omni_data = custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY]
                if LayerUtils.LAYER_AUTHORING_LAYER_CUSTOM_KEY in omni_data:
                    authoring_layer_identifier = omni_data[LayerUtils.LAYER_AUTHORING_LAYER_CUSTOM_KEY]
                    authoring_layer_identifier = root_layer.ComputeAbsolutePath(authoring_layer_identifier)
                    authoring_layer = Sdf.Find(authoring_layer_identifier)
                    if stage.HasLocalLayer(authoring_layer):
                        edit_target = stage.GetEditTargetForLocalLayer(authoring_layer)
                        stage.SetEditTarget(edit_target)
        except Exception as e:
            carb.log_error(f"Failed to restore authoring layer from custom data: {str(e)}.")
            return

    @staticmethod
    def save_authoring_layer_to_custom_data(stage):
        edit_target = stage.GetEditTarget()
        if edit_target.GetLayer() and edit_target.GetLayer().anonymous:
            return

        root_layer = stage.GetRootLayer()
        custom_data = root_layer.customLayerData
        if LayerUtils.LAYER_OMNI_CUSTOM_KEY not in custom_data:
            custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY] = {}

        omni_data = custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY]
        authoring_layer = edit_target.GetLayer().identifier
        authoring_layer = PathUtils.compute_relative_path(root_layer.identifier, authoring_layer)
        omni_data[LayerUtils.LAYER_AUTHORING_LAYER_CUSTOM_KEY] = authoring_layer
        custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY] = omni_data
        root_layer.customLayerData = custom_data

    @staticmethod
    def _get_layer_custom_data_value(root_layer: Sdf.Layer, layer_identifier: str, key: str, default_value=None):
        custom_data = root_layer.customLayerData
        if LayerUtils.LAYER_OMNI_CUSTOM_KEY in custom_data:
            omni_data = custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY]
            if key in omni_data:
                data = omni_data[key]
                layer_identifier = omni.client.normalize_url(layer_identifier)
                for relatvie_path, value in data.items():
                    absolute_path = root_layer.ComputeAbsolutePath(relatvie_path)
                    if layer_identifier == absolute_path:
                        return value

        return default_value

    @staticmethod
    def _set_layer_custom_data_value(root_layer: Sdf.Layer, layer_identifier: str, key: str, value):
        if not layer_identifier:
            return

        custom_data = root_layer.customLayerData
        if LayerUtils.LAYER_OMNI_CUSTOM_KEY not in custom_data:
            custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY] = {}

        omni_data = custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY]
        relative_path = PathUtils.compute_relative_path(root_layer.identifier, layer_identifier)
        if key in omni_data:
            found = False
            layer_identifier = omni.client.normalize_url(layer_identifier)
            for path, _ in omni_data[key].items():
                absolute_path = root_layer.ComputeAbsolutePath(path)
                if layer_identifier == absolute_path:
                    omni_data[key][path] = value
                    found = True
                    break

            if not found:
                omni_data[key][relative_path] = value
        else:
            omni_data[key] = {relative_path: value}
        custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY] = omni_data
        root_layer.customLayerData = custom_data

    @staticmethod
    def _remove_layer_custom_data_by_key(root_layer: Sdf.Layer, layer_identifier: str, key: str):
        if not layer_identifier:
            return

        custom_data = root_layer.customLayerData
        if LayerUtils.LAYER_OMNI_CUSTOM_KEY in custom_data:
            omni_data = custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY]
            if key in omni_data:
                data = omni_data[key]
                layer_identifier = omni.client.normalize_url(layer_identifier)
                for path, _ in data.items():
                    absolute_path = root_layer.ComputeAbsolutePath(path)
                    if layer_identifier == absolute_path:
                        del data[path]
                        omni_data[key] = data
                        custom_data[LayerUtils.LAYER_OMNI_CUSTOM_KEY] = omni_data
                        root_layer.customLayerData = custom_data
                        break

    @staticmethod
    def get_layer_global_muteness(root_layer: Sdf.Layer, layer_identifier: str):
        return LayerUtils._get_layer_custom_data_value(
            root_layer, layer_identifier, LayerUtils.LAYER_MUTENESS_CUSTOM_KEY, False
        )

    @staticmethod
    def set_layer_global_muteness(root_layer: Sdf.Layer, layer_identifier: str, muted: bool):
        return LayerUtils._set_layer_custom_data_value(
            root_layer, layer_identifier, LayerUtils.LAYER_MUTENESS_CUSTOM_KEY, muted
        )

    @staticmethod
    def remove_layer_global_muteness(root_layer: Sdf.Layer, layer_identifier: str):
        return LayerUtils._remove_layer_custom_data_by_key(
            root_layer, layer_identifier, LayerUtils.LAYER_MUTENESS_CUSTOM_KEY
        )

    @staticmethod
    def get_layer_lock_status(root_layer: Sdf.Layer, layer_identifier: str):
        return LayerUtils._get_layer_custom_data_value(
            root_layer, layer_identifier, LayerUtils.LAYER_LOCK_STATUS_CUSTOM_KEY, False
        )

    @staticmethod
    def set_layer_lock_status(root_layer: Sdf.Layer, layer_identifier: str, locked: bool):
        if root_layer.identifier == layer_identifier:
            return

        LayerUtils._set_layer_custom_data_value(
            root_layer, layer_identifier, LayerUtils.LAYER_LOCK_STATUS_CUSTOM_KEY, locked
        )

    @staticmethod
    def remove_layer_lock_status(root_layer: Sdf.Layer, layer_identifier: str):
        return LayerUtils._remove_layer_custom_data_by_key(
            root_layer, layer_identifier, LayerUtils.LAYER_LOCK_STATUS_CUSTOM_KEY
        )

    @staticmethod
    def restore_muteness_from_custom_data(stage):
        muted_layer_identifiers = []
        unmuted_layer_identifiers = []
        sublayers = LayerUtils.get_all_sublayers(stage)

        for sublayer_identifier in sublayers:
            if LayerUtils.get_layer_global_muteness(stage.GetRootLayer(), sublayer_identifier):
                muted_layer_identifiers.append(sublayer_identifier)
            else:
                unmuted_layer_identifiers.append(sublayer_identifier)

        stage.MuteAndUnmuteLayers(muted_layer_identifiers, unmuted_layer_identifiers)

    @staticmethod
    def remove_sublayer(layer: Sdf.Layer, position):
        if len(layer.subLayerPaths) == 0:
            return None

        if position < -1 or position >= len(layer.subLayerPaths):
            return None

        layer_identifier = layer.ComputeAbsolutePath(layer.subLayerPaths[position])
        del layer.subLayerPaths[position]
        return layer_identifier

    @staticmethod
    def remove_prim_spec(layer: Sdf.Layer, prim_spec_path: Union[str, Sdf.Path]):
        """
        Utility to remove prim spec from layer.

        Args:
            layer (Sdf.Layer): Layer handle.
            prim_spec_path (Union[str, Sdf.Path]): Path of prim spec.

        Returns:
            True if success, or False otherwise.
        """

        prim_spec = layer.GetPrimAtPath(prim_spec_path)
        if not prim_spec:
            return False

        if prim_spec.nameParent:
            name_parent = prim_spec.nameParent
        else:
            name_parent = layer.pseudoRoot

        if not name_parent:
            return False

        name = prim_spec.name
        if name in name_parent.nameChildren:
            del name_parent.nameChildren[name]

        return True

    @staticmethod
    def move_layer(
        from_parent_layer_identifier,
        from_sublayer_position,
        to_parent_layer_identifier,
        to_sublayer_position,
        remove_source=False,
    ):
        """Move sublayer from source parent to position of target parent.

        Args:
            from_parent_layer_identifier: The parent of source sublayer.
            from_sublayer_position: The sublayer position to be moved.
            to_parent_layer_identifier: The parent of target sublayer.
            to_sublayer_position: The sublayer position in target parent that source moves to.
            remove_source: Removes the source sublayer or not from source parent after move.
                           If from_parent_layer_identifier == to_parent_layer_layer_identifier,
                           it will always be True.

        Return:
            True if it's successful, False otherwise,
        """

        if (
            from_parent_layer_identifier == to_parent_layer_identifier
            and from_sublayer_position == to_sublayer_position
        ):
            return True

        from_parent_layer = Sdf.Find(from_parent_layer_identifier)
        to_parent_layer = Sdf.Find(to_parent_layer_identifier)
        if not from_parent_layer or not to_parent_layer:
            carb.log_warn(
                f"Move layer failed as layer {from_parent_layer_identifier} or {to_parent_layer_identifier} cannot be found."
            )
            return False

        if len(from_parent_layer.subLayerPaths) == 0:
            carb.log_warn(
                f"Failed to move layer at position {from_sublayer_position} of parent {from_parent_layer_identifier}"
                f" as parent has no sublayers."
            )
            return False

        if (
            from_sublayer_position >= len(from_parent_layer.subLayerPaths)
            or from_sublayer_position < 0
            or (to_sublayer_position != -1 and to_sublayer_position < 0)
        ):
            carb.log_warn(
                f"Failed to move layer at position {from_sublayer_position} of parent {from_parent_layer_identifier} to"
                f" layer at position {to_sublayer_position} of parent {to_parent_layer_identifier}"
            )
            return False

        src_sublayer_paths = from_parent_layer.subLayerPaths
        sublayer_path = src_sublayer_paths[from_sublayer_position]
        sublayer_path = from_parent_layer.ComputeAbsolutePath(sublayer_path)

        # Holds sublayer to avoid it to be released during delete/insert.
        sublayer = Sdf.Find(sublayer_path)
        if remove_source:
            del src_sublayer_paths[from_sublayer_position]

        # Source layer is not in target parent or they are in the same parent
        target_position = LayerUtils.get_sublayer_position_in_parent(to_parent_layer_identifier, sublayer_path)
        if target_position == -1:
            sublayer_path = PathUtils.compute_relative_path(to_parent_layer_identifier, sublayer_path)
            dst_sublayer_paths = to_parent_layer.subLayerPaths
            if to_sublayer_position > len(dst_sublayer_paths) or to_sublayer_position == -1:
                to_sublayer_position = len(dst_sublayer_paths)
            dst_sublayer_paths.insert(to_sublayer_position, sublayer_path)

        return True

    @staticmethod
    def get_edit_target(stage) -> str:
        return omni.usd.get_edit_target_identifier(stage)

    @staticmethod
    def set_edit_target(stage, layer_identifier):
        return omni.usd.set_edit_target_by_identifier(stage, layer_identifier)

    @staticmethod
    def get_all_sublayers(stage, include_session_layers=False, include_only_omni_layers=False, include_anonymous_layers=True) -> List[str]:
        return omni.usd.get_all_sublayers(stage, include_session_layers, include_only_omni_layers, include_anonymous_layers)

    @staticmethod
    def is_layer_writable(layer_identifier) -> bool:
        """Checks if layer is a writable format or writable on the file system."""

        if Sdf.Layer.IsAnonymousLayerIdentifier(layer_identifier):
            return True

        if not omni.usd.is_usd_writable_filetype(layer_identifier):
            return False

        return omni.usd.is_layer_writable(layer_identifier)

    @staticmethod
    def get_dirty_layers(stage, include_root_layer=True, include_only_omni_layers=False) -> List[str]:
        dirty_layers = []
        root_layer_identifier = stage.GetRootLayer().identifier
        all_sublayer_identifiers = LayerUtils.get_all_sublayers(stage, True, include_only_omni_layers, False)
        for sublayer_identifier in all_sublayer_identifiers:
            if not include_root_layer and sublayer_identifier == root_layer_identifier:
                continue

            if sublayer_identifier.endswith('.live'):
                continue

            if sublayer_identifier.startswith("metrics:"):
                continue

            layer = Sdf.Find(sublayer_identifier)
            if layer and layer.dirty:
                dirty_layers.append(sublayer_identifier)

        return dirty_layers

    # TODO Move version related code out
    @staticmethod
    def _is_versioning_enabled():
        try:
            import omni.kit.widget.versioning

            enable_versioning = True
        except Exception:
            enable_versioning = False

        return enable_versioning

    @staticmethod
    async def create_checkpoint_async(layer_identifier: Union[str, List[str]], comment: str, force=False):
        if isinstance(layer_identifier, list):
            identifiers = layer_identifier
        else:
            identifiers = [layer_identifier]

        success_layers = []
        failed_layers = []

        async def check_server_support_and_create_checkpoint(identifier):
            result, server_info = await omni.client.get_server_info_async(identifier)
            if result == omni.client.Result.OK and server_info and server_info.checkpoints_enabled:
                result, _ = await omni.client.create_checkpoint_async(identifier, comment, force)
                if result == omni.client.Result.OK or result == omni.client.Result.ERROR_ALREADY_EXISTS:
                    success_layers.append(identifier)
                else:
                    failed_layers.append(identifier)
                    carb.log_error(f"Failed to create checkpoint for layer {identifier}: {result}.")

        all_futures = []
        for identifier in identifiers:
            all_futures.append(asyncio.ensure_future(check_server_support_and_create_checkpoint(identifier)))

        await asyncio.wait(all_futures)

        return success_layers, failed_layers

    @staticmethod
    def create_checkpoint(layer_identifier: Union[str, List[str]], comment: str, force=False):
        asyncio.ensure_future(LayerUtils.create_checkpoint_async(layer_identifier, comment, force))

    @staticmethod
    async def create_checkpoint_for_stage_async(stage, comment: str, only_dirty_layers=False, force=False):
        if only_dirty_layers:
            all_layers = LayerUtils.get_dirty_layers(stage, True)
        else:
            all_layers = LayerUtils.get_all_sublayers(stage, False, True, False)

        return await LayerUtils.create_checkpoint_async(all_layers, comment, force)

    @staticmethod
    def reload_all_layers(layer_identifiers: Union[str, List[str]]):
        """Reloads all layers in batch."""

        if isinstance(layer_identifiers, str):
            identifiers = [layer_identifiers]
        else:
            identifiers = layer_identifiers

        all_layer_handles = []
        for identifier in identifiers:
            layer = Sdf.Find(identifier)
            if layer:
                all_layer_handles.append(layer)

        if all_layer_handles:
            Sdf.Layer.ReloadLayers(all_layer_handles)
