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

from typing import Optional

import omni.ext
from omni.kit.viewport.registry import RegisterViewportLayer
from omni.kit.xr.core import XRShutdown

from .viewport_controller import XRViewportController
from .viewport_layer import XRViewportLayer


class XRUIViewportWindowExtension(omni.ext.IExt):
    def on_startup(self, ext_id) -> None:
        self.__viewport_controller: Optional[XRViewportController] = XRViewportController()
        self.__viewport_layer = RegisterViewportLayer(XRViewportLayer, "omni.kit.xr.ui.window.viewport")

    def on_shutdown(self) -> None:
        self.__viewport_layer.destroy()
        self.__viewport_controller = None

        # Run all shutdown tasks to ensure we're ready for a relaunch
        XRShutdown.run_shutdown_functions("omni.kit.xr.ui.window.viewport")
