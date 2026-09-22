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

import omni.ui

from .settings_frame import XRProfile, XRShutdown


class XRSettingsStack:
    """define a stack of Settings Widgets"""

    def __init__(self, components) -> None:
        self._stack: omni.ui.VStack = None
        self._frames: list = []
        self._components = components

        XRShutdown.assert_object_deletion_upon_shutdown(self)

    def build_ui(self, profile: XRProfile) -> None:

        self._stack = omni.ui.VStack(spacing=7)
        with self._stack:
            for component in self._components:
                if isinstance(component, tuple):
                    self._frames.append(component[0](profile=profile, config=component[1]))
                else:
                    self._frames.append(component(profile=profile))
