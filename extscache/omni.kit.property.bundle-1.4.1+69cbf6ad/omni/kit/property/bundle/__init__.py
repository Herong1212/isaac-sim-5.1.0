# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides classes for registering and managing custom property widgets for USD prims within the Omniverse Kit application."""


from .widgets import *

__all__ = [
    "BundlePropertyWidgets",
    "GeomPrimSchemeDelegate",
    "MaterialPrimSchemeDelegate",
    "PathPrimSchemeDelegate",
    "ShaderPrimSchemeDelegate",
]
