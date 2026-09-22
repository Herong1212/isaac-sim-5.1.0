# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from __future__ import annotations

import omni.anim.navigation.core as nav
import omni.kit.commands
import omni.usd
from omni.kit.usd_undo import UsdLayerUndo
from pxr import Gf, Sdf, Usd, UsdGeom
import NavSchema

NAVMESH_VOLUME_NAME = "NavMeshVolume"
NAVMESH_VOLUME_INCLUDE = 0
NAVMESH_VOLUME_EXCLUDE = 1

HALF_EXTENT = 0.5
INCLUDE_SCALE = 10.0
EXCLUDE_SCALE = 2.0


def get_stage_default_prim_path(stage):
    if stage.HasDefaultPrim():
        return stage.GetDefaultPrim().GetPath()
    else:
        return Sdf.Path.absoluteRootPath


def refresh_property_window():
    try:
        import omni.kit.window.property as p
        p.get_window().request_rebuild()
    except ImportError:
        pass


class CreateNavMeshVolumeCommand(omni.kit.commands.Command):
    """Creates a navigation mesh volume.
    Args:
        parent_prim_path: The parent prim path in the stage where to add the navigation mesh volume.
        volume_type: The type of volume to create. NAVMESH_VOLUME_INCLUDE or NAVMESH_VOLUME_EXCLUDE
        position: The position to create the navigation mesh volume.
        usd_context_name: The name of the usd context for this command
        layer: The layer to create the navigation mesh volume.
    """

    def __init__(
        self, parent_prim_path: Sdf.Path = Sdf.Path.emptyPath,
        volume_type: int = NAVMESH_VOLUME_INCLUDE,
        position: Gf.Vec3d = None,
        usd_context_name: str = "",
        layer: Sdf.Layer = None
    ):
        self._usd_undo = None
        self._parent_prim_path = parent_prim_path
        self._usd_context = omni.usd.get_context(usd_context_name)
        self._layer = layer
        self._selection = self._usd_context.get_selection()
        self._volume_type = volume_type
        self._position = position

    def do(self):
        stage = self._usd_context.get_stage()
        meters_per_unit = UsdGeom.GetStageMetersPerUnit(stage)
        if self._layer is None:
            self._layer = stage.GetEditTarget().GetLayer()
        self._usd_undo = UsdLayerUndo(self._layer)
        self._prim_path = Sdf.Path(omni.usd.get_stage_next_free_path(stage, f"/{NAVMESH_VOLUME_NAME}", True))
        self._usd_undo.reserve(self._prim_path)

        volume = NavSchema.NavMeshVolume.Define(stage, self._prim_path)
        volumeTypeAttr = volume.GetNavVolumeTypeAttr()
        if volumeTypeAttr:
            volumeTypeAttr.Set("Include" if self._volume_type == NAVMESH_VOLUME_INCLUDE else "Exclude")

        omni.kit.commands.execute(
            "ApplyNavMeshAPICommand", prim_path=self._prim_path, api=NavSchema.NavMeshAreaAPI
        )

        # set the default boundable extent
        prim = stage.GetPrimAtPath(self._prim_path)
        boundable = UsdGeom.Boundable(prim)
        extentAttr = boundable.GetExtentAttr()
        if extentAttr:
            # the unit of the defined extent is meter, should convert to the target unit
            halfExtent = HALF_EXTENT / meters_per_unit
            extentAttr.Set([(-halfExtent, -halfExtent, -halfExtent), (halfExtent, halfExtent, halfExtent)])

        self._selection.set_prim_path_selected(self._prim_path.pathString, True, True, True, True)

        scale = Gf.Matrix4d(1.0)
        scale.SetScale(INCLUDE_SCALE if self._volume_type == NAVMESH_VOLUME_INCLUDE else EXCLUDE_SCALE)
        xform = scale
        if self._position:
            xform = xform * Gf.Matrix4d(1.0).SetTranslate(self._position)

        # transform the navmesh volume
        omni.kit.commands.execute("TransformPrim", path=self._prim_path, new_transform_matrix=xform)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class ApplyNavMeshAPICommand(omni.kit.commands.Command):
    """Applies an API schema to a prim
    Args:
        prim_path: The prim path in the stage on which to add the API schema
        api: The api schema to add
        usd_context_name: The name of the usd context for this command
    """

    def __init__(self, prim_path: Sdf.Path, api: Usd.APISchemaBase, usd_context_name: str = ""):
        self._api = api
        self._prim_path = prim_path
        self._usd_context_name = usd_context_name
        self._usd_context = omni.usd.get_context(self._usd_context_name)
        self._stage = self._usd_context.get_stage()

    def do(self):
        prim = self._stage.GetPrimAtPath(self._prim_path)
        prim.ApplyAPI(self._api)
        refresh_property_window()

    def undo(self):
        prim = self._stage.GetPrimAtPath(self._prim_path)
        prim.RemoveAPI(self._api)
        refresh_property_window()


class RemoveNavMeshAPICommand(omni.kit.commands.Command):
    """Removes an API schema from a prim
    Args:
        prim_path: The prim path in the stage on which to remove the API schema
        api: The api schema to remove
        usd_context_name: The name of the usd context for this command
    """
    def __init__(self, prim_path: Sdf.Path, api: Usd.APISchemaBase, usd_context_name: str = ""):
        self._api = api
        self._prim_path = prim_path
        self._usd_context_name = usd_context_name
        self._usd_context = omni.usd.get_context(self._usd_context_name)
        self._stage = self._usd_context.get_stage()

    def do(self):
        prim = self._stage.GetPrimAtPath(self._prim_path)
        prim.RemoveAPI(self._api)
        refresh_property_window()

    def undo(self):
        prim = self._stage.GetPrimAtPath(self._prim_path)
        prim.ApplyAPI(self._api)
        refresh_property_window()


omni.kit.commands.register_all_commands_in_module(__name__)
