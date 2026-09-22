# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ext
import omni.kit.xr.core.recorder as xcr_player
import omni.ui
from omni.kit.xr.profile.common import XRProfileCommon
from omni.kit.xr.ui.window.profile import (
    XRMenuAdvancedFrame,
    XRMenuClippingPlanesFrame,
    XRMenuDesktopDisplayFrame,
    XRMenuFoveationSettingsFrame,
    XRMenuGeneralARFrame,
    XRMenuMatteObjectFrame,
    XRMenuNavigationFrame,
    XRMenuOutputFrame,
    XRMenuScalingFrame,
    XRMenuSystemInfo,
    XRMenuViewportSettingsFrame,
    XRMenuXRDepthFrame,
)


class XRProfileARExtension(XRProfileCommon, omni.ext.IExt):
    def on_profile_startup(self):

        self.set_ar_mode(True)
        self.disable_saving()

        advancedComponents = [
            XRMenuViewportSettingsFrame,
            XRMenuNavigationFrame,
            XRMenuFoveationSettingsFrame,
            XRMenuScalingFrame,
            XRMenuDesktopDisplayFrame,
            XRMenuXRDepthFrame,
            XRMenuMatteObjectFrame,
            XRMenuClippingPlanesFrame,
            XRMenuOutputFrame,
        ]

        general_menu_config = {
            "render_quality_items": self.get_default_render_quality_items(),
            "show_selected_output_plugin": True,
            "show_resolution_multiplier": True,
            "show_tooltips": True,
        }

        componentList = [
            (XRMenuGeneralARFrame, general_menu_config),
            (XRMenuSystemInfo, {"collapsed": True}),
            (
                XRMenuAdvancedFrame,
                {"components": advancedComponents, "collapsed": True},
            ),
        ]

        window = self.setup_settings_window(componentList, icons=["data/icon/ar.svg", "data/icon/ar_active.svg"])

        config = {"profile_settings_window": {"component_list": window.component_list, "icons": window.icons}}
        self.get_profile().set_config(config)

    def on_deactivate_profile(self) -> None:
        xcr_player.stop_replay_service(self)
