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


import omni.kit.app
from omni.kit.xr.core import XRWeakMethod

from ..ui.settings_frame import XRSettingsFrame

# =======================================================
# Menu component describing anchor mode
# The anchor describes where the virtual world is anchored to the physical world
#
# Contains:
# - Set anchor of the world
# - Select prim as anchor
#
# =======================================================


class XRMenuAnchorFrame(XRSettingsFrame):
    def get_frame_name(self):
        return "Anchor Settings"

    def build_ui(self):
        rebuildUI = XRWeakMethod(self._rebuild)

        self._subs.append(
            omni.kit.app.SettingChangeSubscription(self.get_persistent_path() + "anchorMode", lambda *_: rebuildUI())
        )

        anchormode_items = {
            "Active Camera": "active camera",
            "Custom USD Anchor": "custom anchor",
            "Scene Origin": "scene origin",
        }
        self.add_setting_combo("Physical World USD Anchor", self.get_persistent_path() + "anchorMode", anchormode_items)

        customAnchorPath = self.get_scene_persistent_path() + "customAnchor"
        self.add_setting("PATH", "Path For Custom USD Anchor", customAnchorPath)
