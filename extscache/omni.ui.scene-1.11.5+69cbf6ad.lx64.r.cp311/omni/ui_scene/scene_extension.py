## Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from . import scene
import omni.ext
import omni.ui as ui
from .compatibility import add_intersection_attributes


class SceneExtension(omni.ext.IExt):
    """The entry point for MDL Material Graph"""

    def on_startup(self):
        self.subscription = ui.add_to_namespace(scene)

        # Compatibility with old intersections
        add_intersection_attributes()

    def on_shutdown(self):
        self.subscription = None
