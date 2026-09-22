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
# Use these at your own risk, and forward-compatability is not supported

import omni.ext
import omni.kit.commands
import omni.kit.xr.core.recorder as xcr_player
import omni.usd
from omni.kit.xr.profile.common import XRProfileCommon
from omni.kit.xr.ui.window.profile import (  # XRMenuEyeTrackingFrame,
    XRMenuAdvancedFrame,
    XRMenuClippingPlanesFrame,
    XRMenuDesktopDisplayFrame,
    XRMenuFoveationSettingsFrame,
    XRMenuGeneralVRFrame,
    XRMenuNavigationFrame,
    XRMenuOutputFrame,
    XRMenuScalingFrame,
    XRMenuSystemInfo,
    XRMenuViewportSettingsFrame,
)


class XRProfileVRExtension(XRProfileCommon, omni.ext.IExt):
    def on_profile_startup(self):
        self.disable_saving()

        advancedComponents = [
            XRMenuViewportSettingsFrame,
            XRMenuNavigationFrame,
            XRMenuFoveationSettingsFrame,
            XRMenuScalingFrame,
            XRMenuDesktopDisplayFrame,
            XRMenuClippingPlanesFrame,
            XRMenuOutputFrame,
        ]

        general_menu_config = {
            "render_quality_items": self.get_default_render_quality_items(),
            "show_selected_output_plugin": True,
            "show_resolution_multiplier": True,
            "show_tooltips": True,
        }

        window = self.setup_settings_window(
            [
                (XRMenuGeneralVRFrame, general_menu_config),
                (XRMenuSystemInfo, {"collapsed": True}),
                (
                    XRMenuAdvancedFrame,
                    {"components": advancedComponents, "collapsed": True},
                ),
            ],
            ["data/icon/vr.svg", "data/icon/vr_active.svg"],
        )

        config = {"profile_settings_window": {"component_list": window.component_list, "icons": window.icons}}
        self.get_profile().set_config(config)

    def on_deactivate_profile(self) -> None:
        xcr_player.stop_replay_service(self)
