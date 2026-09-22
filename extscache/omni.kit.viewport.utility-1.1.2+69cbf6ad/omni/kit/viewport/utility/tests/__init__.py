## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

from .capture import *
from .test_suite import *


async def setup_viewport_test_window(resolution_x: int, resolution_y: int, position_x: int = 0, position_y: int = 0):
    from omni.kit.viewport.utility import get_active_viewport_window
    viewport_window = get_active_viewport_window()
    if viewport_window:
        viewport_window.position_x = position_x
        viewport_window.position_y = position_y
        viewport_window.width = resolution_x
        viewport_window.height = resolution_y
        viewport_window.viewport_api.resolution = (resolution_x, resolution_y)
    return viewport_window
