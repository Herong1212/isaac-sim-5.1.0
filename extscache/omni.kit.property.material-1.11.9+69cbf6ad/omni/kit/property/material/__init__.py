# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides commands for disconnecting and setting info attributes in USD's shading system, and registers custom widgets for material properties in the OmniKit Editor."""

__all__ = ["UsdShadeDisconnectCommand", "SetUsdShadeInfoAttributeCommand"]

from .scripts import *
