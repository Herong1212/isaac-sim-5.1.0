# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ImportLayerCommand"]

import re
from typing import Callable
from typing import List
from typing import Optional

import carb
from omni.usd.commands import DeletePrimsCommand
from pxr import Sdf
from pxr import Usd

import omni.kit.commands
import omni.usd
from omni.usd.commands import UsdStageHelper

from .prim_serializer import update_property_paths


class ImportLayerCommand(omni.kit.commands.Command, UsdStageHelper):
    """Imports the given layer to the given stage under the specific root.

    Args:
        layer (Sdf.Layer): All the prims from this layer will be imported to the stage.
        root (Sdf.Path): The new prims will be placed under this path.
        stage (Optional[Usd.Stage]): The stage where the new prims will be added. If None, the stage from the USD Context is used.
        filter_fn (Optional[Callable]): An optional filter function used to determine whether a prim is valid for import.
    """

    def __init__(
        self,
        layer: Sdf.Layer,
        root: Sdf.Path = Sdf.Path.absoluteRootPath,
        stage: Optional[Usd.Stage] = None,
        filter_fn: Optional[Callable] = None,
    ):
        """Initializes an ImportLayerCommand instance that imports a layer into a stage under a specific root. This constructor sets up the internal tracking for created paths and the current selection."""
        UsdStageHelper.__init__(self, stage)
        self._layer = layer
        self._root = root
        self._created_paths: List[str] = []
        self._selection: List[str] = []
        self._filter_fn: Optional[Callable] = filter_fn

    def do(self):
        """Executes the command by importing prims from a layer to the stage. It saves the current selection, copies prim specs to the target layer using a filter function if provided, updates property paths, and updates the selection with the newly created prims."""
        # Save selection
        self._selection = omni.usd.get_context().get_selection().get_selected_prim_paths()

        stage = self._get_stage()
        target_layer = stage.GetEditTarget().GetLayer()
        paths_map = {}

        with Sdf.ChangeBlock():
            for prim_spec in self._layer.rootPrims:
                root_spec = prim_spec.nameChildren[0]
                if self._filter_fn and not self._filter_fn(root_spec):
                    carb.log_warn(f"{root_spec.name} is not a valid prim type to paste here, ignoring.")
                    continue

                prim_path = root_spec.path
                prim_name = root_spec.name
                target_path = get_layer_next_free_path(stage, self._root.AppendChild(prim_name).pathString, False)

                # Copy to stage
                Sdf.CopySpec(self._layer, prim_path, target_layer, target_path)

                paths_map[prim_path] = target_path
                self._created_paths.append(target_path)

            for path in self._created_paths:
                for source_path, target_path in paths_map.items():
                    update_property_paths(target_layer.GetPrimAtPath(path), source_path, target_path)

        omni.usd.get_context().get_selection().set_selected_prim_paths(self._created_paths, True)

        self._layer = None

    def undo(self):
        """Reverts the import operation by deleting the prims created during the import and restoring the original selection."""
        # Delete created
        DeletePrimsCommand(self._created_paths).do()
        # Restore selection
        omni.usd.get_context().get_selection().set_selected_prim_paths(self._selection, False)


def get_layer_next_free_path(stage, path, prepend_default_prim, is_batch_editing=True):
    """This checks both in the stage and in the current edit target layer, since during
    batch editing, the changes won't have made it to the usd stage yet."""
    if prepend_default_prim and stage.HasDefaultPrim():
        default_prim = stage.GetDefaultPrim()
        if default_prim:
            path = default_prim.GetPath().pathString + path

    def increment_path(path):
        match = re.search(r"_(\d+)$", path)
        if match:
            new_num = int(match.group(1)) + 1
            ret = re.sub(r"_(\d+)$", str.format("_{:02d}", new_num), path)
        else:
            ret = path + "_01"
        return ret

    while stage.GetPrimAtPath(path):
        path = increment_path(path)

    if is_batch_editing:
        layer = stage.GetEditTarget().GetLayer()
        while layer.GetPrimAtPath(path):
            path = increment_path(path)

    return path
