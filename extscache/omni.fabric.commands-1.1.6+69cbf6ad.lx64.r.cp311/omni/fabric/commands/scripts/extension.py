# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""Fabric commands extension"""

import omni.ext
import omni.usd
from .commands import *


class FabricCommandsExtension(omni.ext.IExt):
    """A class that represents an extension for fabric commands.

    This class inherits from omni.ext.IExt and provides the startup and shutdown
    methods which are called when the extension is started up and shut down, respectively."""

    def on_startup(self, ext_id):
        """Called when the extension is started up.

        Parameters:
            ext_id (str): The identifier for the extension."""
        pass

    def on_shutdown(self):
        """Called when the extension is shut down."""
        pass
