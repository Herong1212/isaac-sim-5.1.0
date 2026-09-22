# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "AbstractLayerCommand", "SetEditTargetCommand", "CreateSublayerCommand", "RemoveSublayerCommand",
    "RemovePrimSpecCommand", "MergeLayersCommand", "FlattenLayersCommand", "CreateLayerReferenceCommand",
    "StitchPrimSpecsToLayer", "MovePrimSpecsToLayerCommand", "MoveSublayerCommand", "ReplaceSublayerCommand",
    "SetLayerMutenessCommand", "LockLayerCommand", "LinkSpecsCommand", "UnlinkSpecsCommand", "LockSpecsCommand",
    "UnlockSpecsCommand"
]
import omni
import carb
import omni.usd
import omni.kit.commands

from pxr import Usd, Sdf, UsdGeom, UsdUtils
from .layer_utils import LayerUtils
from typing import Union, List
from .extension import get_layers
from .specs_linking_and_locking_utils import *


def _get_usd_context(context_name_or_instance: Union[str, omni.usd.UsdContext] = ""):
    if not context_name_or_instance:
        context_name_or_instance = ""

    if isinstance(context_name_or_instance, str):
        usd_context = omni.usd.get_context(context_name_or_instance)
    elif isinstance(context_name_or_instance, omni.usd.UsdContext):
        usd_context = context_name_or_instance
    else:
        usd_context = None

    return usd_context


class AbstractLayerCommand(omni.kit.commands.Command):
    """
    Abstract base class for layer commands.
    It's mainly responsible to create a commmon class
    to save all states before command execution, and restore them
    in the undo function.
    """

    def __init__(self, context_name_or_instance: Union[str, omni.usd.UsdContext] = ""):
        self._usd_context = _get_usd_context(context_name_or_instance)
        self._selection = self._usd_context.get_selection()

    def get_layers(self):
        return get_layers(self._usd_context)

    def get_specs_linking(self):
        layers = self.get_layers()
        if not layers:
            return None

        return layers.get_specs_linking()

    def get_specs_locking(self):
        layers = self.get_layers()
        if not layers:
            return None

        return layers.get_specs_locking()

    def _restore_spec_links_from_dict(self, spec_path_to_layers):
        specs_linking = self.get_specs_linking()
        for spec_path, _ in spec_path_to_layers.items():
            specs_linking.unlink_spec_from_all_layers(spec_path, False)

        for spec_path, layer_identifiers in spec_path_to_layers.items():
            for layer_identifier in layer_identifiers:
                specs_linking.link_spec(spec_path, layer_identifier, False)

    def do(self):
        stage = self._usd_context.get_stage()
        if stage.GetEditTarget().GetLayer():
            self._edit_target_identifier = stage.GetEditTarget().GetLayer().identifier
        else:
            self._edit_target_identifier = stage.GetRootLayer().identifier
        self._prev_selected_paths = list(self._selection.get_selected_prim_paths())

        return self.do_impl()

    def do_impl(self):
        """Abstract do function to be implemented."""

        raise NotImplementedError("Method must be implemented")

    def undo_impl(self):
        """Abstract undo function to be implemented."""

        raise NotImplementedError("Method must be implemented")

    def undo(self):
        self.undo_impl()

        # restore selected prims and layer
        self._selection.set_selected_prim_paths(self._prev_selected_paths, False)
        stage = self._usd_context.get_stage()

        layer = Sdf.Find(self._edit_target_identifier)
        if layer and not stage.IsLayerMuted(layer.identifier):
            edit_target_layer = layer
        else:
            edit_target_layer = stage.GetRootLayer()
        if stage.HasLocalLayer(edit_target_layer):
            edit_target = stage.GetEditTargetForLocalLayer(edit_target_layer)
            stage.SetEditTarget(edit_target)


class SetEditTargetCommand(AbstractLayerCommand):
    """Sets layer as Edit Target."""

    def __init__(self, layer_identifier: str, usd_context: Union[str, omni.usd.UsdContext] = ""):
        """Constructor.

        Keyword Arguments:
            layer_identifier (str): Layer identifier.

            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
        """
        super().__init__(usd_context)
        self._current_edit_target_identifier = layer_identifier

    def do_impl(self):
        stage = self._usd_context.get_stage()
        layer = Sdf.Find(self._current_edit_target_identifier)
        if not layer or not stage.HasLocalLayer(layer):
            carb.log_warn(
                f"Set authoring command failed. Layer is not in the local stack: {self._current_edit_target_identifier}"
            )
        else:
            edit_target = stage.GetEditTargetForLocalLayer(layer)
            stage.SetEditTarget(edit_target)

    def undo_impl(self):
        pass


class CreateSublayerCommand(AbstractLayerCommand):
    """Creates or inserts a sublayer."""

    def __init__(
        self,
        layer_identifier: str,
        sublayer_position: int,
        new_layer_path: str,
        transfer_root_content: bool,
        create_or_insert: bool,
        layer_name: str = "",
        usd_context: Union[str, omni.usd.UsdContext] = "",
    ):
        """Constructor.

        Keyword arguments::
            layer_identifier  (str): The identifier of layer to create sublayer. It should be found by Sdf.Find.

            sublayer_position (int): Sublayer position that the new sublayer is created before.
                                     If position_before == -1, it will create layer at the end of sublayer list.
                                     If position_before >= total_number_of_sublayers, it will create layer at the end of sublayer list.
            new_layer_path (str): Absolute path of new layer. If it's empty, it will create anonymous layer if create_or_insert == True.
                                 If create_or_insert == False and it's empty, it will fail to insert layer.

            transfer_root_content (bool): True if we should move the root contents to the new layer.

            create_or_insert (bool): If it's true, it will create layer from this path. It's insert, otherwise.

            layer_name (str, optional): If it's to create anonymous layer (new_layer_path is empty), this name is used.

            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
        """

        super().__init__(usd_context)

        self._layer_identifier = layer_identifier
        self._sublayer_position = sublayer_position
        self._new_layer_path = new_layer_path
        self._create_or_insert = create_or_insert
        if create_or_insert:
            self._transfer_root_content = transfer_root_content
        else:
            self._transfer_root_content = False
        self._new_layer_identifier = None
        self._layer_name = layer_name
        self._temp_layer = None

    def do_impl(self):
        stage = self._usd_context.get_stage()
        root = stage.GetRootLayer()
        parent_layer = Sdf.Find(self._layer_identifier)
        if self._create_or_insert:
            if self._transfer_root_content:
                self._temp_layer = Sdf.Layer.CreateAnonymous()
                self._temp_layer.TransferContent(root)

            if parent_layer:
                new_layer = LayerUtils.create_sublayer(parent_layer, self._sublayer_position, self._new_layer_path)
                if new_layer:
                    # Copy meta including up axis, units, animation settings, etc, and no sublayers.
                    UsdUtils.CopyLayerMetadata(stage.GetRootLayer(), new_layer, True)
                    LayerUtils.set_custom_layer_name(new_layer, self._layer_name)

                    if self._transfer_root_content:
                        LayerUtils.transfer_layer_content(root, new_layer)
                        root.rootPrims.clear()

                    self._new_layer_identifier = new_layer.identifier
                else:
                    self._new_layer_identifier = None
        else:
            layer = LayerUtils.insert_sublayer(parent_layer, self._sublayer_position, self._new_layer_path)
            if layer:
                self._new_layer_identifier = layer.identifier

        return self._new_layer_identifier

    def undo_impl(self):
        if self._new_layer_identifier:
            stage = self._usd_context.get_stage()
            with Sdf.ChangeBlock():
                if self._transfer_root_content and self._temp_layer:
                    root = stage.GetRootLayer()
                    root.TransferContent(self._temp_layer)

                layer_position_in_parent = LayerUtils.get_sublayer_position_in_parent(
                    self._layer_identifier, self._new_layer_identifier
                )
                if layer_position_in_parent != -1:
                    layer = Sdf.Find(self._layer_identifier)
                    if not layer:
                        return
                    layer_identifier = LayerUtils.remove_sublayer(layer, layer_position_in_parent)
                    LayerUtils.remove_layer_global_muteness(layer, layer_identifier)


class RemoveSublayerCommand(AbstractLayerCommand):
    """Removes a sublayer from parent layer."""

    def __init__(
        self, layer_identifier: str, sublayer_position: int, usd_context: Union[str, omni.usd.UsdContext] = ""
    ):
        """Constructor.

        Keyword Arguments:
            layer_identifier (str): The identifier of layer to remove sublayer.

            sublayer_position (int): The sublayer position to be removed.

            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
        """

        super().__init__(usd_context)

        self._layer_identifier = layer_identifier
        self._sublayer_position = sublayer_position

    def do_impl(self):
        stage = self._usd_context.get_stage()
        root_layer = stage.GetRootLayer()
        self._removed_layer_identifier = None
        layer = Sdf.Find(self._layer_identifier)
        sublayer_identifier = LayerUtils.get_sublayer_identifier(self._layer_identifier, self._sublayer_position)
        if not layer or not sublayer_identifier:
            return

        self._old_layer_global_mute = LayerUtils.get_layer_global_muteness(root_layer, sublayer_identifier)
        self._old_layer_local_mute = stage.IsLayerMuted(sublayer_identifier)
        self._old_layer_lock_status = LayerUtils.get_layer_lock_status(root_layer, sublayer_identifier)
        if Sdf.Layer.IsAnonymousLayerIdentifier(sublayer_identifier):
            # Hold layer reference to avoid it's released for undo
            self._removed_layer = Sdf.Layer.FindOrOpen(sublayer_identifier)
        else:
            self._removed_layer = None
        edit_target_layer = stage.GetEditTarget().GetLayer()
        if edit_target_layer:
            current_edit_target = edit_target_layer.identifier
        else:
            current_edit_target = None
        self._removed_layer_identifier = LayerUtils.remove_sublayer(layer, self._sublayer_position)
        LayerUtils.remove_layer_global_muteness(root_layer, self._removed_layer_identifier)
        LayerUtils.remove_layer_lock_status(root_layer, self._removed_layer_identifier)
        if current_edit_target and current_edit_target == self._removed_layer_identifier:
            edit_target = stage.GetEditTargetForLocalLayer(stage.GetRootLayer())
            stage.SetEditTarget(edit_target)
        elif not current_edit_target:
            root_layer_target = stage.GetEditTargetForLocalLayer(stage.GetRootLayer())
            stage.SetEditTarget(root_layer_target)

    def undo_impl(self):
        if self._removed_layer_identifier:
            stage = self._usd_context.get_stage()
            root_layer = stage.GetRootLayer()
            layer = Sdf.Find(self._layer_identifier)
            if layer:
                position = self._sublayer_position
                sublayer = LayerUtils.insert_sublayer(layer, position, self._removed_layer_identifier)

                if sublayer:
                    if self._old_layer_local_mute:
                        stage.MuteLayer(sublayer.identifier)
                    else:
                        stage.UnmuteLayer(sublayer.identifier)
                    LayerUtils.set_layer_global_muteness(root_layer, sublayer.identifier, self._old_layer_global_mute)
                    LayerUtils.set_layer_lock_status(root_layer, sublayer.identifier, self._old_layer_lock_status)


class RemovePrimSpecCommand(omni.kit.commands.Command):
    """Removes prim spec from a layer."""

    def __init__(
        self,
        layer_identifier: str,
        prim_spec_path: Union[Sdf.Path, List[Sdf.Path]],
        usd_context: Union[str, omni.usd.UsdContext] = "",
    ):
        """Constructor.

        Keyword Arguments:
            layer_identifier (str): The identifier of layer to remove prim.

            prim_spec_path (Union[Sdf.Path, List[Sdf.Path]]): The prim paths to be removed.

            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
        """

        self._usd_context = _get_usd_context(usd_context)
        self._layer_identifier = layer_identifier
        self._anon_layer = None
        if isinstance(prim_spec_path, Sdf.Path) or isinstance(prim_spec_path, str):
            self._prim_spec_paths = [prim_spec_path]
        else:
            self._prim_spec_paths = prim_spec_path

    def do(self):
        layer = Sdf.Find(self._layer_identifier)
        if layer:
            with Sdf.ChangeBlock():
                for prim_spec_path in self._prim_spec_paths:
                    prim_spec = layer.GetPrimAtPath(prim_spec_path)
                    if not prim_spec:
                        return

                    self._anon_layer = Sdf.Layer.CreateAnonymous()
                    Sdf.CreatePrimInLayer(self._anon_layer, prim_spec_path)
                    Sdf.CopySpec(layer, prim_spec_path, self._anon_layer, prim_spec_path)
                    LayerUtils.remove_prim_spec(layer, prim_spec_path)
        else:
            self._anon_layer = None
            self._layer_identifier = None

    def undo(self):
        if self._anon_layer and self._layer_identifier:
            layer = Sdf.Find(self._layer_identifier)
            if layer:
                with Sdf.ChangeBlock():
                    for prim_spec_path in self._prim_spec_paths:
                        Sdf.CreatePrimInLayer(self._anon_layer, prim_spec_path)
                        Sdf.CopySpec(self._anon_layer, prim_spec_path, layer, prim_spec_path)
            self._anon_layer = None


class MergeLayersCommand(AbstractLayerCommand):
    """Merges two layers."""

    def __init__(
        self,
        dst_parent_layer_identifier: str,
        dst_layer_identifier,
        src_parent_layer_identifier: str,
        src_layer_identifier: str,
        dst_stronger_than_src: bool,
        usd_context: Union[str, omni.usd.UsdContext] = "",
        src_layer_offset: Sdf.LayerOffset = Sdf.LayerOffset(0.0, 1.0)
    ):
        """Constructor.

        Keyword Arguments:
            dst_parent_layer_identifier: The parent of target layer.

            dst_layer_identifier: The target layer that source layer is merged to.

            src_parent_layer_identifier: The parent of source layer.

            src_layer_identifier: The source layer.

            dst_stronger_than_src (bool): If target layer is stronger than source, which will decide
                                          how to merge opinions that appear in both layers.

            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.

            src_layer_offset (Sdf.LayerOffset): The source layer offset to target layer. By default, it's identity.
        """
        super().__init__(usd_context)

        self._merged = False
        self._delete_cmds = []
        self._dst_layer_identifier = dst_layer_identifier
        self._src_layer_identifier = src_layer_identifier
        self._dst_parent_layer_identifier = dst_parent_layer_identifier
        self._src_parent_layer_identifier = src_parent_layer_identifier
        self._dst_stronger_than_src = dst_stronger_than_src
        self._src_layer_offset = src_layer_offset

    def do_impl(self):
        temp_layer = None

        stage = self._usd_context.get_stage()
        strong_muted = stage.IsLayerMuted(self._dst_layer_identifier)
        weak_muted = stage.IsLayerMuted(self._src_layer_identifier)
        strong_layer = Sdf.Layer.Find(self._dst_layer_identifier)
        src_sublayer_position = LayerUtils.get_sublayer_position_in_parent(
            self._src_parent_layer_identifier, self._src_layer_identifier
        )
        if strong_muted or not strong_layer:
            # strong layer inactive - delete it
            sublayer_position = LayerUtils.get_sublayer_position_in_parent(
                self._dst_parent_layer_identifier, self._dst_layer_identifier
            )
            delete_cmd = RemoveSublayerCommand(self._dst_parent_layer_identifier, sublayer_position)
            delete_cmd.do_impl()
            self._delete_cmds.append(delete_cmd)
        elif not weak_muted:
            # both are not muted - merge
            temp_layer = Sdf.Layer.CreateAnonymous()
            temp_layer.TransferContent(strong_layer)
            self._removed_layer = temp_layer
            self._merged = omni.usd.merge_layers(
                self._dst_layer_identifier, self._src_layer_identifier,
                self._dst_stronger_than_src, self._src_layer_offset.offset,
                self._src_layer_offset.scale
            )

            # Failed to be merged
            if not self._merged:
                return False

        if self._merged or (not strong_muted and strong_layer):
            # Since omni.usd.merge_layers will clear all sublayers, it needs to
            # insert again to create a remove command if src layer is a sublayer of dst layer.
            if self._merged and self._dst_layer_identifier == self._src_parent_layer_identifier:
                LayerUtils.insert_sublayer(strong_layer, src_sublayer_position, self._src_layer_identifier)

            delete_cmd = RemoveSublayerCommand(self._src_parent_layer_identifier, src_sublayer_position)
            delete_cmd.do_impl()
            self._delete_cmds.append(delete_cmd)

            # FIXME: Remove this weak layer from temp layer also.
            # This is not an issue for offline stage.
            if temp_layer:
                if self._dst_layer_identifier == self._src_parent_layer_identifier:
                    LayerUtils.remove_sublayer(temp_layer, src_sublayer_position)

        return True

    def undo_impl(self):
        if self._merged:
            if self._dst_layer_identifier == self._src_parent_layer_identifier:
                # transfering content here will invalidate prims in the deleted layer
                dst_layer = Sdf.Find(self._dst_layer_identifier)
                if dst_layer:
                    with Sdf.ChangeBlock():
                        Sdf.CopySpec(
                            self._removed_layer, Sdf.Path.absoluteRootPath, dst_layer, Sdf.Path.absoluteRootPath
                        )
                        for delete_cmd in reversed(self._delete_cmds):
                            delete_cmd.undo_impl()
            else:
                with Sdf.ChangeBlock():
                    for delete_cmd in reversed(self._delete_cmds):
                        delete_cmd.undo_impl()
                    layer = Sdf.Find(self._dst_layer_identifier)
                    if layer:
                        # FIXME: It cannot use TransferContent which does not notify anything
                        Sdf.CopySpec(self._removed_layer, Sdf.Path.absoluteRootPath, layer, Sdf.Path.absoluteRootPath)
                        for sublayer in self._removed_layer.subLayerPaths:
                            if sublayer not in layer.subLayerPaths:
                                layer.subLayerPaths.append(sublayer)
            self._removed_layer = None
        else:
            with Sdf.ChangeBlock():
                for delete_cmd in reversed(self._delete_cmds):
                    delete_cmd.undo_impl()
        self._delete_cmds.clear()


class FlattenLayersCommand(AbstractLayerCommand):
    """Flatten Layers."""

    def __init__(self, usd_context: Union[str, omni.usd.UsdContext] = ""):
        """Constructor.

        Keyword Arguments:
            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
        """

        super().__init__(usd_context)
        self._merges = []

    def _traverse(self, results, parent_layer_identifier, layer, layer_identifier, current_subtree_stack):
        # It has circular sublayer tree, like sub1 -> sub2 -> sub1
        if layer_identifier in current_subtree_stack:
            return

        results.append((parent_layer_identifier, layer_identifier))
        current_subtree_stack.append(layer_identifier)
        if not layer:
            return

        for sublayer in layer.subLayerPaths:
            sublayer_identifier = layer.ComputeAbsolutePath(sublayer)
            sublayer = Sdf.Find(sublayer_identifier)
            self._traverse(results, layer.identifier, sublayer, sublayer_identifier, current_subtree_stack)

        current_subtree_stack.pop()

    def _get_sublayers_from_strongest_to_weakest(self):
        stage = self._usd_context.get_stage()
        root_layer = stage.GetRootLayer()
        all_layers = []
        current_subtree_stack = []
        self._traverse(all_layers, None, root_layer, root_layer.identifier, current_subtree_stack)

        return all_layers

    def do_impl(self):
        all_sublayers = self._get_sublayers_from_strongest_to_weakest()
        mergable_parent_identifier = None
        mergable_sublayer_identifier = None
        for i in reversed(range(len(all_sublayers))):
            parent_identifier = all_sublayers[i][0]
            sublayer_identifier = all_sublayers[i][1]
            if mergable_parent_identifier is not None:
                merge = MergeLayersCommand(
                    parent_identifier,
                    sublayer_identifier,
                    mergable_parent_identifier,
                    mergable_sublayer_identifier,
                    True,
                )
                merge.do_impl()
                self._merges.append(merge)
            mergable_parent_identifier = parent_identifier
            mergable_sublayer_identifier = sublayer_identifier

    def undo_impl(self):
        self._merges.reverse()
        for m in self._merges:
            m.undo_impl()
        self._merges.clear()


class CreateLayerReferenceCommand(AbstractLayerCommand):
    """
    Create reference in specific layer.

    It creates a new prim and adds the asset and path as references in specific layer.

    Args:
        layer_identifier: str: Layer identifier to create prim inside.

        path_to (Sdf.Path): Path to create a new prim.

        asset_path (str): The asset it's necessary to add to references.

        prim_path (Sdf.Path): The prim in asset to reference.

        usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
    """

    def __init__(
        self,
        layer_identifier: str,
        path_to: Sdf.Path,
        asset_path: str = None,
        prim_path: Sdf.Path = None,
        usd_context: Union[str, omni.usd.UsdContext] = "",
    ):
        super().__init__(usd_context)

        self._selection = self._usd_context.get_selection()

        stage = self._usd_context.get_stage()
        path_to = Sdf.Path(omni.usd.get_stage_next_free_path(stage, str(path_to), False))

        self._layer_identifier = layer_identifier
        self._asset_path = asset_path
        self._prim_path = prim_path
        self._path_to = path_to

    def do_impl(self):
        layer = Sdf.Find(self._layer_identifier)
        if not layer:
            return False

        # OMPE-37291: Check if crate file version is supported
        if omni.usd.is_usd_crate_file_version_supported(self._asset_path) is False:
            return False

        stage = self._usd_context.get_stage()
        with Usd.EditContext(stage, layer):
            prim_to = stage.DefinePrim(self._path_to)

            with Sdf.ChangeBlock():
                # Set inctanceable
                if self._asset_path:
                    if self._prim_path:
                        prim_to.GetReferences().AddReference(self._asset_path, self._prim_path)
                    else:
                        prim_to.GetReferences().AddReference(self._asset_path)
                elif self._prim_path:
                    prim_to.GetReferences().AddInternalReference(self._prim_path)

    def undo_impl(self):
        layer = Sdf.Find(self._layer_identifier)
        if not layer:
            return False

        # Dereference this. Otherwise it fires error: Cannot remove ancestral prim
        stage = self._usd_context.get_stage()
        with Usd.EditContext(stage, layer):
            prim_to = stage.GetPrimAtPath(self._path_to)
            prim_to.GetReferences().ClearReferences()

            # It would be better to use the following command, but it's in buildins and not available:
            #    delete_cmd = DeletePrimsCommand([self._path_to])
            #    delete_cmd.do()

            for layer in stage.GetLayerStack():
                edit = Sdf.BatchNamespaceEdit()
                temp_layer = Sdf.Layer.CreateAnonymous()

                prim_spec = layer.GetPrimAtPath(self._path_to)
                if prim_spec is None:
                    continue

                parent_spec = prim_spec.realNameParent
                if parent_spec is not None:
                    Sdf.CreatePrimInLayer(temp_layer, self._path_to)
                    Sdf.CopySpec(layer, self._path_to, temp_layer, self._path_to)
                    edit.Add(self._path_to, Sdf.Path.emptyPath)

                layer.Apply(edit)


class StitchPrimSpecsToLayer(AbstractLayerCommand):
    """Flatten specific prims in the stage. It will remove original prim specs after flatten."""

    def __init__(
        self, prim_paths: List[str], target_layer_identifier: str, usd_context: Union[str, omni.usd.UsdContext] = ""
    ):
        """Constructor.

        Keyword Arguments:
            prim_paths (List[str]): A list of prim_paths to flatten with.

            target_layer_identifier (str): The target layer to store the flatten results.

            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
        """

        super().__init__(usd_context)
        self._prim_paths = prim_paths
        self._target_layer_identifier = target_layer_identifier
        self._to_recoverd_layers = {}

    def do_impl(self):
        self._to_recoverd_layers.clear()

        target_layer = Sdf.Find(self._target_layer_identifier)
        stage = self._usd_context.get_stage()
        if stage and target_layer and self._prim_paths:
            # Saves context before real flatten for undo.
            all_sublayer_paths = LayerUtils.get_all_sublayers(stage)
            if self._target_layer_identifier not in all_sublayer_paths:
                all_sublayer_paths.append(self._target_layer_identifier)

            with Sdf.ChangeBlock():
                for sublayer_path in all_sublayer_paths:
                    sublayer = Sdf.Layer.Find(sublayer_path)
                    if not sublayer:
                        continue

                    for prim_spec_path in self._prim_paths:
                        recover_layer = self._to_recoverd_layers.get(sublayer_path, None)
                        if not recover_layer:
                            recover_layer = Sdf.Layer.CreateAnonymous()
                            self._to_recoverd_layers[sublayer_path] = recover_layer

                        prim_spec = sublayer.GetPrimAtPath(prim_spec_path)
                        if not prim_spec:
                            continue

                        Sdf.CreatePrimInLayer(recover_layer, prim_spec_path)
                        Sdf.CopySpec(sublayer, prim_spec_path, recover_layer, prim_spec_path)

                for prim_path in self._prim_paths:
                    omni.usd.stitch_prim_specs(stage, prim_path, target_layer)

                # Delete it from src layer
                all_sublayer_paths.remove(self._target_layer_identifier)
                for sublayer_path in all_sublayer_paths:
                    for prim_spec_path in self._prim_paths:
                        sublayer = Sdf.Layer.Find(sublayer_path)
                        if not sublayer:
                            continue
                        LayerUtils.remove_prim_spec(sublayer, prim_spec_path)

    def undo_impl(self):
        with Sdf.ChangeBlock():
            for layer_identifier, layer_content in self._to_recoverd_layers.items():
                original_layer = Sdf.Layer.Find(layer_identifier)
                if not original_layer:
                    continue

                for prim_spec_path in self._prim_paths:
                    if layer_content.GetPrimAtPath(prim_spec_path):
                        Sdf.CreatePrimInLayer(original_layer, prim_spec_path)
                        Sdf.CopySpec(layer_content, prim_spec_path, original_layer, prim_spec_path)
                    else:
                        LayerUtils.remove_prim_spec(original_layer, prim_spec_path)
        self._to_recoverd_layers.clear()


class MovePrimSpecsToLayerCommand(AbstractLayerCommand):
    """Merge prim spec from src layer to dst layer and remove it from src layer."""

    def __init__(
        self,
        dst_layer_identifier: str,
        src_layer_identifier: str,
        prim_spec_path: str,
        dst_stronger_than_src: bool,
        usd_context: Union[str, omni.usd.UsdContext] = "",
    ):
        """Constructor.

        Keyword Arguments:
            dst_layer_identifier (str): The identifier of target layer.

            src_layer_identifier (str): The identifier of source layer.

            prim_spec_path (str): The prim spec path to be merged.

            dst_stronger_than_src (bool): Target layer is stronger than source layer in stage.

            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
        """

        super().__init__(usd_context)
        self._dst_layer_identifier = dst_layer_identifier
        self._src_layer_identifier = src_layer_identifier
        self._prim_spec_path = prim_spec_path
        self._dst_stronger_than_src = dst_stronger_than_src

    def do_impl(self):
        if self._dst_layer_identifier != self._src_layer_identifier:
            dst_layer = Sdf.Find(self._dst_layer_identifier)
            src_layer = Sdf.Find(self._src_layer_identifier)
            if dst_layer and src_layer:
                self._anon_dst_layer = Sdf.Layer.CreateAnonymous()

                # backup dst node for undo if prim exists
                prim_spec = dst_layer.GetPrimAtPath(self._prim_spec_path)
                self._created_prim = None
                if prim_spec is not None:
                    Sdf.CreatePrimInLayer(self._anon_dst_layer, self._prim_spec_path)
                    Sdf.CopySpec(dst_layer, self._prim_spec_path, self._anon_dst_layer, self._prim_spec_path)
                else:
                    # prim doesnt exist in dst, so merge_prim_spec will create any missing parents in dst,
                    # and we will have to remove them during undo
                    prim_spec = src_layer.GetPrimAtPath(self._prim_spec_path)
                    parent = prim_spec.realNameParent
                    while (
                        parent is not None
                        and parent.realNameParent is not None
                        and dst_layer.GetPrimAtPath(parent.path) is None
                    ):
                        self._created_prim = parent.path
                        parent = parent.realNameParent

                # Create prim spec in dst if it does not exist.
                omni.usd.merge_prim_spec(
                    self._dst_layer_identifier,
                    self._src_layer_identifier,
                    self._prim_spec_path,
                    self._dst_stronger_than_src,
                )

                # Delete it from src layer
                self._delete_cmd = RemovePrimSpecCommand(self._src_layer_identifier, self._prim_spec_path)
                self._delete_cmd.do()
                self._dst_layer_path = self._dst_layer_identifier
        else:
            self._dst_layer_path = None

    def undo_impl(self):
        if self._dst_layer_identifier != self._src_layer_identifier:
            self._delete_cmd.undo()
            self._delete_cmd = None

            if not self._dst_layer_path:
                return

            dst_layer = Sdf.Find(self._dst_layer_identifier)
            if dst_layer:
                prim_spec = self._anon_dst_layer.GetPrimAtPath(self._prim_spec_path)
                if prim_spec is not None:
                    Sdf.CopySpec(self._anon_dst_layer, self._prim_spec_path, dst_layer, self._prim_spec_path)
                else:
                    LayerUtils.remove_prim_spec(dst_layer, self._prim_spec_path)
                if self._created_prim is not None:
                    LayerUtils.remove_prim_spec(dst_layer, self._created_prim.pathString)
                self._anon_dst_layer = None


class MoveSublayerCommand(AbstractLayerCommand):
    """Moves sublayer from one location to the other."""

    def __init__(
        self,
        from_parent_layer_identifier: str,
        from_sublayer_position: int,
        to_parent_layer_identifier: str,
        to_sublayer_position: int,
        remove_source: bool = False,
        usd_context: Union[str, omni.usd.UsdContext] = "",
    ):
        """Constructor.

        Keyword Arguments:
            from_parent_layer_identifier (str): The identifier of source parent layer.

            from_sublayer_position (int): The sublayer position in source parent layer to move.

            to_parent_layer_identifier (str): The identifier of target parent layer.

            to_sublayer_position (int): The sublayer position in target parent layer that layers moves to.
                                        If this position is -1, it means the last position of sublayer array.
                                        If this position is beyond the end of sublayer array. It means to
                                        move this layer to the end of that array.
                                        Otherwise, it's invalid if it's below 0.

            remove_source (bool): Remove source sublayer after moving to target or not.

            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
        """

        super().__init__(usd_context)
        self._from_parent_layer_identifier = from_parent_layer_identifier
        self._from_sublayer_position = from_sublayer_position
        self._sublayer_identifier = LayerUtils.get_sublayer_identifier(
            self._from_parent_layer_identifier, self._from_sublayer_position
        )
        if self._sublayer_identifier:
            self._to_parent_layer_identifier = to_parent_layer_identifier
            self._to_sublayer_position = to_sublayer_position
            self._success = False
            sublayer_position_in_target = LayerUtils.get_sublayer_position_in_parent(
                self._to_parent_layer_identifier, self._sublayer_identifier
            )
            self._remove_source = remove_source
            if self._from_parent_layer_identifier == self._to_parent_layer_identifier:
                # It must remove source to move this layer.
                self._remove_source = True
                self._has_same_layer_in_target = False
            else:
                self._has_same_layer_in_target = sublayer_position_in_target != -1

    def _move_layer(
        self,
        from_parent_layer_identifier,
        sublayer_identifier,
        to_parent_layer_identifier,
        to_sublayer_position,
        remove_source,
    ):
        # Finds moved layer.
        layer_position_in_parent = LayerUtils.get_sublayer_position_in_parent(
            from_parent_layer_identifier, sublayer_identifier
        )

        # Cannot find moved layer
        if layer_position_in_parent == -1:
            carb.log_warn(
                f"Cannot move layer from sublayer {sublayer_identifier} under parent {from_parent_layer_identifier} to "
                f"sublayer at position {to_sublayer_position} under parent {to_parent_layer_identifier} "
                f"since moved layer cannot be found."
            )
            return False

        # Find target layer
        return LayerUtils.move_layer(
            from_parent_layer_identifier,
            layer_position_in_parent,
            to_parent_layer_identifier,
            to_sublayer_position,
            remove_source,
        )

    def do_impl(self):
        if not self._sublayer_identifier:
            return

        self._move_layer(
            self._from_parent_layer_identifier,
            self._sublayer_identifier,
            self._to_parent_layer_identifier,
            self._to_sublayer_position,
            self._remove_source,
        )

    def undo_impl(self):
        if not self._sublayer_identifier:
            return

        self._move_layer(
            self._to_parent_layer_identifier,
            self._sublayer_identifier,
            self._from_parent_layer_identifier,
            self._from_sublayer_position,
            not self._has_same_layer_in_target,
        )


class ReplaceSublayerCommand(AbstractLayerCommand):
    """Replaces sublayer with a new layer."""

    def __init__(
        self,
        layer_identifier: str,
        sublayer_position: int,
        new_layer_path: str,
        usd_context: Union[str, omni.usd.UsdContext] = "",
    ):
        """Constructor.

        Keyword Arguments:
            layer_identifier (str): The identifier of layer to replace sublayer.

            sublayer_position (int): The sublayer position to be replaced.

            new_layer_path (str): The path of new layer.

            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
        """

        super().__init__(usd_context)
        self._layer_identifier = layer_identifier
        self._sublayer_position = sublayer_position
        self._new_layer_path = new_layer_path
        self._old_layer_identifier = None
        self._new_layer_identifier = None

    def do_impl(self):
        self._old_layer_identifier = LayerUtils.get_sublayer_identifier(self._layer_identifier, self._sublayer_position)
        if not self._old_layer_identifier:
            carb.log_warn(f"Cannot replace sublayer with an invalid index {self._sublayer_position}.")
            return

        stage = self._usd_context.get_stage()
        root_layer = stage.GetRootLayer()
        self._old_layer_global_mute = LayerUtils.get_layer_global_muteness(root_layer, self._layer_identifier)
        self._old_layer_local_mute = stage.IsLayerMuted(self._layer_identifier)
        self._old_layer_lock_status = LayerUtils.get_layer_lock_status(root_layer, self._layer_identifier)
        layer = Sdf.Find(self._layer_identifier)
        if layer:
            edit_target_identifier = LayerUtils.get_edit_target(stage)
            new_layer = LayerUtils.replace_sublayer(layer, self._sublayer_position, self._new_layer_path)
            if edit_target_identifier == self._old_layer_identifier:
                LayerUtils.set_edit_target(stage, self._new_layer_path)
            if new_layer:
                LayerUtils.remove_layer_global_muteness(root_layer, self._layer_identifier)
                LayerUtils.remove_layer_lock_status(root_layer, self._layer_identifier)
                self._new_layer_identifier = new_layer.identifier
            else:
                self._new_layer_identifier = None
        else:
            self._new_layer_identifier = None

    def undo_impl(self):
        stage = self._usd_context.get_stage()
        root_layer = stage.GetRootLayer()
        if self._new_layer_identifier:
            with Sdf.ChangeBlock():
                new_layer_position_in_parent = LayerUtils.get_sublayer_position_in_parent(
                    self._layer_identifier, self._new_layer_identifier
                )
                if new_layer_position_in_parent != -1:
                    layer = Sdf.Find(self._layer_identifier)
                    if layer:
                        edit_target_identifier = LayerUtils.get_edit_target(stage)
                        LayerUtils.replace_sublayer(layer, new_layer_position_in_parent, self._old_layer_identifier)
                        if edit_target_identifier == self._old_layer_identifier:
                            LayerUtils.set_edit_target(stage, self._new_layer_path)
                        if self._old_layer_local_mute:
                            stage.MuteLayer(self._old_layer_identifier)
                        else:
                            stage.UnmuteLayer(self._old_layer_identifier)
                        LayerUtils.set_layer_global_muteness(
                            root_layer, self._old_layer_identifier, self._old_layer_global_mute
                        )
                        LayerUtils.set_layer_lock_status(
                            root_layer, self._old_layer_identifier, self._old_layer_lock_status
                        )


class SetLayerMutenessCommand(AbstractLayerCommand):
    """Sets mute state for layer."""

    def __init__(self, layer_identifier: str, muted: bool, usd_context: Union[str, omni.usd.UsdContext] = ""):
        """Constructor.

        Keyword Arguments:
            layer_identifier (str): The identifier of layer to be muted/unmuted.

            muted (bool): Muted or not of this layer.

            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
        """

        super().__init__(usd_context)
        self._layer_identifier = layer_identifier
        self._muted = muted

    def do_impl(self):
        stage = self._usd_context.get_stage()
        if not stage:
            return False

        session_layer_identifier = stage.GetSessionLayer().identifier
        root_layer_identifier = stage.GetRootLayer().identifier
        if self._layer_identifier == session_layer_identifier or self._layer_identifier == root_layer_identifier:
            return False

        edit_target_identifier = LayerUtils.get_edit_target(stage)
        if self._muted:
            stage.MuteLayer(self._layer_identifier)
            if edit_target_identifier == self._layer_identifier:
                stage.SetEditTarget(stage.GetEditTargetForLocalLayer(stage.GetRootLayer()))
        else:
            stage.UnmuteLayer(self._layer_identifier)

    def undo_impl(self):
        stage = self._usd_context.get_stage()
        if not stage:
            return False

        edit_target_identifier = LayerUtils.get_edit_target(stage)
        if not self._muted:
            stage.MuteLayer(self._layer_identifier)
            if edit_target_identifier == self._layer_identifier:
                stage.SetEditTarget(stage.GetEditTargetForLocalLayer(stage.GetRootLayer()))
        else:
            stage.UnmuteLayer(self._layer_identifier)


class LockLayerCommand(AbstractLayerCommand):
    """Sets lock state for layer."""

    def __init__(self, layer_identifier: str, locked: bool, usd_context: Union[str, omni.usd.UsdContext] = ""):
        """Constructor. REMINDER: Locking root layer is not permitted.

        Keyword Arguments:
            layer_identifier (str): The identifier of layer to be muted/unmuted.

            locked (bool): Muted or not of this layer.

            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
        """
        super().__init__(usd_context)

        self._layer_identifier = layer_identifier
        self._locked = locked

    def do_impl(self):
        stage = self._usd_context.get_stage()
        if not stage or self._layer_identifier == stage.GetRootLayer().identifier:
            return False

        root_layer = stage.GetRootLayer()
        LayerUtils.set_layer_lock_status(root_layer, self._layer_identifier, self._locked)
        if self._locked and LayerUtils.get_edit_target(stage) == self._layer_identifier:
            LayerUtils.set_edit_target(stage, stage.GetRootLayer().identifier)

    def undo_impl(self):
        stage = self._usd_context.get_stage()
        if not stage or self._layer_identifier == stage.GetRootLayer().identifier:
            return False

        root_layer = stage.GetRootLayer()
        LayerUtils.set_layer_lock_status(root_layer, self._layer_identifier, not self._locked)


class LinkSpecsCommand(AbstractLayerCommand):
    """Links spec paths to layers."""

    def __init__(
        self,
        spec_paths: Union[str, List[str]],
        layer_identifiers: Union[str, List[str]],
        additive: bool = True,
        hierarchy: bool = False,
        usd_context: Union[str, omni.usd.UsdContext] = "",
    ):
        """Constructor.

        Keyword Arguments:
            spec_paths (Union[str, List[str]]): List of spec paths or single spec path to be linked.

            layer_identifiers (Union[str, List[str]]): List of layer identifiers or single layer identifier.

            additive (bool): Clearing exsiting links or not.

            hierarchy (bool): Linking descendant specs or not.

            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
        """

        super().__init__(usd_context)

        if isinstance(spec_paths, str) or isinstance(spec_paths, Sdf.Path):
            self._paths = [spec_paths]
        else:
            self._paths = spec_paths
        if isinstance(layer_identifiers, str):
            self._layer_identifiers = [layer_identifiers]
        else:
            self._layer_identifiers = layer_identifiers
        self._additive = additive
        self._hierarchy = hierarchy
        self._old_spec_links = {}
        # TODO: Support transferring and discard edits

    def do(self):
        self._old_spec_links = get_spec_layer_links(self._usd_context, self._paths, self._hierarchy)

        if not self._additive:
            unlink_specs_from_all_layers(self._usd_context, self._paths, self._hierarchy)

        link_specs(self._usd_context, self._paths, self._layer_identifiers, self._hierarchy)

    def undo(self):
        new_paths = []
        for path in self._paths:
            if path not in self._old_spec_links:
                new_paths.append(path)

        unlink_specs_from_all_layers(self._usd_context, self._paths, self._hierarchy)
        self._restore_spec_links_from_dict(self._old_spec_links)


class UnlinkSpecsCommand(AbstractLayerCommand):
    """Unlinks spec paths to layers."""

    def __init__(
        self,
        spec_paths: Union[str, List[str]],
        layer_identifiers: Union[str, List[str]],
        hierarchy=False,
        usd_context: Union[str, omni.usd.UsdContext] = "",
    ):
        """Constructor.

        Keyword Arguments:
            spec_paths (Union[str, List[str]]): List of spec paths or single spec path to be unlinked.

            layer_identifiers (Union[str, List[str]]): List of layer identifiers or single layer identifier.

            hierarchy (bool): Unlinking descendant specs or not.

            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
        """

        super().__init__(usd_context)

        if isinstance(spec_paths, str) or isinstance(spec_paths, Sdf.Path):
            self._paths = [spec_paths]
        else:
            self._paths = spec_paths

        if isinstance(layer_identifiers, str):
            self._layer_identifiers = [layer_identifiers]
        else:
            self._layer_identifiers = layer_identifiers
        self._hierarchy = hierarchy
        self._old_spec_links = {}

    def do(self):
        self._old_spec_links = get_spec_layer_links(self._usd_context, self._paths, self._hierarchy)
        unlink_specs(self._usd_context, self._paths, self._layer_identifiers, self._hierarchy)

    def undo(self):
        self._restore_spec_links_from_dict(self._old_spec_links)


class LockSpecsCommand(AbstractLayerCommand):
    """Locks spec paths in the UsdContext."""

    def __init__(
        self, spec_paths: Union[str, List[str]], hierarchy=False, usd_context: Union[str, omni.usd.UsdContext] = ""
    ):
        """Constructor.

        Keyword Arguments:
            spec_paths (Union[str, List[str]]): List of spec paths or single spec path to be locked.

            hierarchy (bool): Locking descendant specs or not.

            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
        """

        super().__init__(usd_context)

        if isinstance(spec_paths, str) or isinstance(spec_paths, Sdf.Path):
            self._paths = [spec_paths]
        else:
            self._paths = spec_paths
        self._hierarchy = hierarchy
        self._old_spec_locks = []
        self._locked_specs = []

    def do(self):
        self._old_spec_locks = get_all_locked_specs(self._usd_context)
        lock_specs(self._usd_context, self._paths, self._hierarchy)
        self._locked_specs = get_all_locked_specs(self._usd_context)

    def undo(self):
        unlock_specs(self._usd_context, self._locked_specs, False)
        self._locked_specs = []

        lock_specs(self._usd_context, self._old_spec_locks, False)
        self._old_spec_locks = []


class UnlockSpecsCommand(AbstractLayerCommand):
    """Unlocks spec paths in the UsdContext"""

    def __init__(
        self, spec_paths: Union[str, List[str]], hierarchy=False, usd_context: Union[str, omni.usd.UsdContext] = ""
    ):
        """Constructor.

        Keyword Arguments:
            spec_paths (Union[str, List[str]]): List of spec paths or single spec path to be unlocked.

            hierarchy (bool): Unlocking descendant specs or not.

            usd_context (Union[str, omni.usd.UsdContext]): Usd context name or instance. It uses default context if it's empty.
        """

        super().__init__(usd_context)

        if isinstance(spec_paths, str) or isinstance(spec_paths, Sdf.Path):
            self._paths = [spec_paths]
        else:
            self._paths = spec_paths
        self._hierarchy = hierarchy
        self._old_spec_locks = []

    def do(self):
        self._old_spec_locks = get_all_locked_specs(self._usd_context)
        unlock_specs(self._usd_context, self._paths, self._hierarchy)

    def undo(self):
        lock_specs(self._usd_context, self._old_spec_locks, False)
