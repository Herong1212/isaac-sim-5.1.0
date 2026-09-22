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

from .xr_gui_layers import XRControllerGuiLayer, XRHandGuiLayer, XRTooltipsGuiLayer
from .xr_tools import XRGrabTool, XRMenuTool, XRMoveTool, XRNavigationTool, XRSelectTool, XRTeleportTool


class XRUIStageCommonExtension(omni.ext.IExt):
    def on_startup(self, ext_id) -> None:
        # Register tools and gui layers
        self.register_tools()

    def on_shutdown(self) -> None:
        # Remove all registered tools and gui_layers
        # This will remove them from the xr framework
        self.__tools = []
        self.__gui_layers = []

        # Run all shutdown tasks to ensure we're ready for a relaunch
        XRShutdown.run_shutdown_functions("omni.kit.xr.ui.stage")

    def register_tools(self) -> None:
        """
        This function instantiates tools and gui_layers.
        The classes register themselves as components into the xr framework.
        """

        self.__gui_layers = [
            XRControllerGuiLayer(),
            XRTooltipsGuiLayer(),
            XRHandGuiLayer(),
        ]
        self.__tools = [
            XRGrabTool(),
            XRSelectTool(),
            XRTeleportTool(),
            XRNavigationTool(),
            XRMenuTool(),
            XRMoveTool(),
        ]
