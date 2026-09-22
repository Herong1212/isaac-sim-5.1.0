# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module extends several metadata for instructing UX implementation, and it provides APIs for accessing those metadata."""

__all__ = [
    "HIDE_IN_STAGE_WINDOW", "NO_DELETE", "ALWAYS_PICK_MODEL", "DISPLAY_NAME",
    "set_hide_in_stage_window", "is_hide_in_stage_window", "set_no_delete",
    "is_no_delete", "set_always_pick_model", "is_always_pick_model",  "set_hide_in_ui",
    "is_hide_in_ui", "set_display_name", "get_display_name"
]
from .editor import *