# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""
This module implements a comprehensive capture framework for viewport and application content, supporting various capture modes such as single frame, sequence, and video capture while integrating with the Omniverse Kit SDK and Omni UI for rendering configurations and progress tracking.
"""


from .extension import CaptureExtension
from .capture_options import *
from .capture_progress import *

__all__ = [
    "CaptureExtension",
    "CaptureOptions",
    "CaptureStatus",
    "CaptureRangeType",
    "CaptureRenderPreset",
    "CaptureMovieType",
    "CaptureRenderPreset",
    "CaptureDebugMaterialType",
]
