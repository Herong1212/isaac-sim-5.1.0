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
# Using these is at your own risk, and forward-compatability is not supported

import omni.ext
from omni.kit.xr.core import XRShutdown


class XRCommonProfileExtension(omni.ext.IExt):
    def on_startup(self, ext_id) -> None:
        pass

    def on_shutdown(self) -> None:

        # Run all shutdown tasks to ensure we're ready for a relaunch
        XRShutdown.run_shutdown_functions("omni.kit.xr.profile.common")
