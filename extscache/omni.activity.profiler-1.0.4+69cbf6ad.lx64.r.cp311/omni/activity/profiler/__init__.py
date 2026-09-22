## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

"""Converts carb profiler events to omni activity events."""

# Necessary so we can link to the Python source instead of copying it.
__all__ = ['IActivityProfiler', 'acquire_activity_profiler', 'release_activity_profiler', 'CAPTURE_MASK_SCENE_LOADING', 'CAPTURE_MASK_LATENCY', 'CAPTURE_MASK_STARTUP']
from .impl import *
