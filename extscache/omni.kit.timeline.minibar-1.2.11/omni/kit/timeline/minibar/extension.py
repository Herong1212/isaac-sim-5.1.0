# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["TimelineMinibarExtension"]

import omni.ext
from omni.kit.viewport.registry import RegisterViewportLayer

from .minibar_scene import TimelineMinibarScene


class TimelineMinibarExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        self._minibar_layer = RegisterViewportLayer(TimelineMinibarScene, ext_id)

    def on_shutdown(self):  # pragma: no cover
        self._minibar_layer = None
