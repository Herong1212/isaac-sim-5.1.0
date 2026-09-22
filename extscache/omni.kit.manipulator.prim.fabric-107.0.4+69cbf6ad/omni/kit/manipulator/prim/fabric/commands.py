# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["TransformMultiPrimsFabricSRT"]

from typing import List, Optional, Tuple, Union

import carb
import omni.kit.commands
import usdrt.Gf
import usdrt.hierarchy
import usdrt.Rt
import usdrt.Sdf
import usdrt.Usd
import usdrt.UsdGeom


class TransformMultiPrimsFabricSRT(omni.kit.commands.Command):
    """
    Transform Fabric primitives in Fabric stage.
    Args:
        paths (List[usdrt.Sdf._Sdf.Path]): List of path strings for selected prims.
        new_translations (List[usdrt.Gf.Vec3d]): List of new translation values for prims.
        new_rotation_eulers (List[usdrt.Gf.Vec3d]): List of new rotation euler angles for prims.
        new_rotation_orders (List[usdrt.Gf.Vec3i]): List of new rotation orders for prims.
        new_scales (List[usdrt.Gf.Vec3d]): List of new scale values for prims.
        old_translations (List[usdrt.Gf.Vec3d]): Previous translations for undo functionality.
        old_rotation_eulers (List[usdrt.Gf.Vec3d]): Previous rotations in Euler form for undo.
        old_rotation_orders (List[usdrt.Gf.Vec3i]): Previous rotation orders for undo functionality.
        old_scales (List[usdrt.Gf.Vec3d]): Previous scale values for undo functionality.
        stage (usdrt.Usd.Stage): The stage to operate.
        time_code (usdrt.Usd.TimeCode): The timecode to change. Default is usdrt.Usd.TimeCode.Default().
        write_to_stage (bool):Whether to write the prim after it's transformed.
    """

    def __init__(
        self,
        paths: list[usdrt.Sdf._Sdf.Path],
        new_translations: List[usdrt.Gf.Vec3d] = None,
        new_rotation_eulers: List[usdrt.Gf.Vec3d] = None,
        new_rotation_orders: List[usdrt.Gf.Vec3i] = None,
        new_scales: List[usdrt.Gf.Vec3d] = None,
        old_translations: List[usdrt.Gf.Vec3d] = None,
        old_rotation_eulers: List[usdrt.Gf.Vec3d] = None,
        old_rotation_orders: List[usdrt.Gf.Vec3i] = None,
        old_scales: List[usdrt.Gf.Vec3d] = None,
        stage=None,
        time_code: usdrt.Usd.TimeCode = usdrt.Usd.TimeCode.Default(),
        write_to_stage: bool = False,
    ):
        """Initializes the command for transforming multiple primitives in a Fabric stage."""
        if stage is None:
            stage_id = omni.usd.get_context().get_stage_id()
            stage = usdrt.Usd.Stage.Attach(stage_id)
        self._stage = stage
        self._paths = paths
        self._write_to_stage = write_to_stage
        self._time_code = time_code

        self._new_translations = [
            usdrt.Gf.Vec3d(new_translations[i * 3], new_translations[i * 3 + 1], new_translations[i * 3 + 2])
            for i in range(0, int(len(new_translations) / 3))
        ]
        self._new_rotation_eulers = [
            usdrt.Gf.Vec3d(new_rotation_eulers[i * 3], new_rotation_eulers[i * 3 + 1], new_rotation_eulers[i * 3 + 2])
            for i in range(0, int(len(new_rotation_eulers) / 3))
        ]
        self._new_rotation_orders = [
            usdrt.Gf.Vec3i(new_rotation_orders[i * 3], new_rotation_orders[i * 3 + 1], new_rotation_orders[i * 3 + 2])
            for i in range(0, int(len(new_rotation_orders) / 3))
        ]
        self._new_scales = [
            usdrt.Gf.Vec3d(new_scales[i * 3], new_scales[i * 3 + 1], new_scales[i * 3 + 2])
            for i in range(0, int(len(new_scales) / 3))
        ]

        if (
            old_translations != None
            and old_rotation_eulers != None
            and old_rotation_orders != None
            and old_scales != None
        ):
            self._old_translations = [
                usdrt.Gf.Vec3d(old_translations[i * 3], old_translations[i * 3 + 1], old_translations[i * 3 + 2])
                for i in range(0, int(len(old_translations) / 3))
            ]
            self._old_rotation_eulers = [
                usdrt.Gf.Vec3d(
                    old_rotation_eulers[i * 3], old_rotation_eulers[i * 3 + 1], old_rotation_eulers[i * 3 + 2]
                )
                for i in range(0, int(len(old_rotation_eulers) / 3))
            ]
            self._old_rotation_orders = [
                usdrt.Gf.Vec3i(
                    old_rotation_orders[i * 3], old_rotation_orders[i * 3 + 1], old_rotation_orders[i * 3 + 2]
                )
                for i in range(0, int(len(old_rotation_orders) / 3))
            ]
            self._old_scales = [
                usdrt.Gf.Vec3d(old_scales[i * 3], old_scales[i * 3 + 1], old_scales[i * 3 + 2])
                for i in range(0, int(len(old_scales) / 3))
            ]

        stage_id = self._stage.GetStageIdAsStageId()
        fabric_id = self._stage.GetFabricId()
        self._hier = usdrt.hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)

    def _matrix_from_euler(self, eulers: Tuple[float, ...], ro: usdrt.Gf.Vec3i):
        axes = [usdrt.Gf.Vec3d(1, 0, 0), usdrt.Gf.Vec3d(0, 1, 0), usdrt.Gf.Vec3d(0, 0, 1)]
        nrs = [usdrt.Gf.Rotation(axes[i], eulers[i]) for i in [ro[0], ro[1], ro[2]]]
        nr = nrs[0] * nrs[1] * nrs[2]
        rot_mtx = usdrt.Gf.Matrix4d().SetRotate(nr)
        return rot_mtx

    def _set_transform(self, prim, translation, rotation_order, rotation_eulers, scale, time_code):
        rot_order = usdrt.Gf.Vec3i(rotation_order[0], rotation_order[1], rotation_order[2])
        rotation_mtx = self._matrix_from_euler((rotation_eulers[0], rotation_eulers[1], rotation_eulers[2]), rot_order)

        translate_mtx = usdrt.Gf.Matrix4d().SetTranslate(translation)
        scale_mtx = usdrt.Gf.Matrix4d().SetScale(scale)

        final_mtx = scale_mtx * rotation_mtx * translate_mtx
        if self._hier.set_world_xform(prim.GetPath(), final_mtx):
            self._hier.update_world_xforms()
        else:
            carb.log_warn(
                f"TransformMultiPrimsFabricSRT.do(): no transform matrix attribute for {prim.GetPath().pathString}"
            )

    def do(self):
        """Performs the transformation on multiple primitives."""
        for i, path in enumerate(self._paths):
            prim = self._stage.GetPrimAtPath(path)

            self._set_transform(
                prim,
                self._new_translations[i],
                self._new_rotation_orders[i],
                self._new_rotation_eulers[i],
                self._new_scales[i],
                self._time_code,
            )

    def undo(self):
        """Reverts the transformation applied to the primitives."""
        if (
            self._old_translations != None
            and self._old_rotation_eulers != None
            and self._old_rotation_orders != None
            and self._old_scales != None
        ):
            for i, path in enumerate(self._paths):
                prim = self._stage.GetPrimAtPath(path)
                self._set_transform(
                    prim,
                    self._old_translations[i],
                    self._old_rotation_orders[i],
                    self._old_rotation_eulers[i],
                    self._old_scales[i],
                    self._time_code,
                )
