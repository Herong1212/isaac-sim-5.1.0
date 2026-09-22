# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

from .xr_menu_general_frame import XRMenuGeneralFrame

# =======================================================
# General AR Settings
# =======================================================


class XRMenuGeneralARFrame(XRMenuGeneralFrame):
    def get_frame_name(self):
        return "General"

    def is_collapsable(self):
        return False
