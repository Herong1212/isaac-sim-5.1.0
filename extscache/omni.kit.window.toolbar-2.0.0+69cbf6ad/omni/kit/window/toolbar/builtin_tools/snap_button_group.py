# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.kit.app
omni.kit.app.log_deprecation(
    '"import omni.kit.window.toolbar.builtin_tools.snap_button_group" is deprecated. '
    'Please use "import omni.kit.widget.toolbar.builtin_tools.snap_button_group"'
)
from omni.kit.widget.toolbar.builtin_tools.snap_button_group import *  # backward compatible
