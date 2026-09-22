# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Use these at your own risk, and forward-compatability is not supported

__all__ = ["XRTargetInfo"]

from typing import Optional

from pxr import Gf

from ..._xrcore import XRTargetInfo_Internal

# =================================================
# This file constructs a shim for the C++
# functionality exposed into python and adds
# types, type conversions, documentation, and
# improved python integration for these functions.
# =================================================

# ================================================
# XRTargetInfo class wrapper
# ================================================

# pylint: disable=protected-access
# noinspection PyProtectedMember


class XRTargetInfo:
    def __init__(self, internal: XRTargetInfo_Internal):
        self.__internal: XRTargetInfo_Internal = internal

    def __eq__(self, other) -> bool:
        if isinstance(other, XRTargetInfo):
            return self.__internal == other.__internal
        return False

    def __hash__(self):
        return self.__internal.__hash__()

    def _get_internal(self) -> XRTargetInfo_Internal:
        return self.__internal

    @property
    def valid(self) -> bool:
        """
        Property indicating that the target info is valid.
        If the ray does not hit anything the target info is invalid.
        """
        return self.__internal.valid

    @property
    def position(self) -> Gf.Vec3f:
        """
        The position in stage space that was hit by the ray.
        """
        return Gf.Vec3f(self.__internal.position)

    @property
    def normal(self) -> Gf.Vec3f:
        """
        The normal direction in stage space at the hit point of the surface that was hit.
        """
        return Gf.Vec3f(self.__internal.normal)

    @property
    def instance_id(self) -> int:
        """
        The instance id of the object that was hit.
        """
        return self.__internal.instance_id

    def get_target_usd_path(self) -> Optional[str]:
        """
        The prim path of the object that the ray hit.
        """
        return self.__internal.get_target_usd_path()

    def get_target_enclosing_model_usd_path(self) -> Optional[str]:
        """
        Most model are composed of several prims. This function returns the prim path
        to the model whose geometry was hit by the ray.
        """
        return self.__internal.get_target_enclosing_model_usd_path()
