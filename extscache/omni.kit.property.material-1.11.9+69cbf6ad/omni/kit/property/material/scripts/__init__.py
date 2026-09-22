# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module imports and consolidates functionalities from commands and extension submodules within the omni.kit.property.material.scripts package."""

__all__ = [
    "UsdShadeDisconnectCommand",
    "SetUsdShadeInfoAttributeCommand",
    "MaterialPropertyExtension",
    "get_binding_from_prims",
]

from .commands import *
from .extension import MaterialPropertyExtension
from .widgets import get_binding_from_prims
