# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from .extension import open_window, select_skeleton
from .utils import refresh_property_window

import omni
from omni.kit.usd_undo import UsdLayerUndo
from pxr import Sdf
import RetargetingSchema
from typing import List


class RetargetSelectSkeletonCommand(omni.kit.commands.Command):
    def __init__(self, skel_path: str):
        self._skel_path = skel_path

    def do(self):
        select_skeleton(self._skel_path)


class RetargetOpenWindowCommand(omni.kit.commands.Command):
    def __init__(self, skel_path: str):
        self._skel_path = skel_path

    def do(self):
        open_window()
        select_skeleton(self._skel_path)


class ApplyControlRigAPICommand(omni.kit.commands.Command):
    def __init__(
            self,
            layer: Sdf.Layer = None,
            paths: List[Sdf.Path] = []
    ):
        self._usd_undo = None
        self._layer = layer
        self._paths = paths

    def do(self):
        stage = omni.usd.get_context().get_stage()
        if self._layer is None:
            self._layer = stage.GetEditTarget().GetLayer()
        self._usd_undo = UsdLayerUndo(self._layer)
        for path in self._paths:
            prim = stage.GetPrimAtPath(path)
            if not prim.HasAPI(RetargetingSchema.ControlRigAPI):
                self._usd_undo.reserve(path)
                RetargetingSchema.ControlRigAPI.Apply(prim)
        refresh_property_window()

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()
        refresh_property_window()


class ApplyAnimationSkelBindingAPICommand(omni.kit.commands.Command):
    def __init__(
            self,
            layer: Sdf.Layer = None,
            paths: List[Sdf.Path] = []
    ):
        self._usd_undo = None
        self._layer = layer
        self._paths = paths

    def do(self):
        stage = omni.usd.get_context().get_stage()
        if self._layer is None:
            self._layer = stage.GetEditTarget().GetLayer()
        self._usd_undo = UsdLayerUndo(self._layer)
        for path in self._paths:
            prim = stage.GetPrimAtPath(path)
            if not prim.HasAPI(RetargetingSchema.AnimationSkelBindingAPI):
                self._usd_undo.reserve(path)
                RetargetingSchema.AnimationSkelBindingAPI.Apply(prim)
        refresh_property_window()

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()
        refresh_property_window()


omni.kit.commands.register_all_commands_in_module(__name__)
