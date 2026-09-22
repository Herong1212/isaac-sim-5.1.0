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

import omni.ext
import omni.ui
import omni.usd
from omni.kit.xr.profile.common import XRProfileCommon
from omni.kit.xr.ui.window.profile import (
    XRMenuAdvancedFrame,
    XRMenuClippingPlanesFrame,
    XRMenuDesktopDisplayFrame,
    XRMenuGeneralTabletARFrame,
    XRMenuMatteObjectFrame,
    XRMenuNavigationFrame,
    XRMenuOutputFrame,
    XRMenuScalingFrame,
    XRMenuSystemInfo,
    XRMenuViewportSettingsFrame,
)


class XRProfileTabletARExtension(XRProfileCommon, omni.ext.IExt):
    def on_profile_startup(self):

        self.set_ar_mode(True)

        self.disable_saving()

        advancedComponents = [
            XRMenuViewportSettingsFrame,
            XRMenuNavigationFrame,
            XRMenuScalingFrame,
            XRMenuDesktopDisplayFrame,
            XRMenuMatteObjectFrame,
            XRMenuClippingPlanesFrame,
            XRMenuOutputFrame,
        ]

        general_menu_config = {
            "render_quality_items": self.get_default_render_quality_items(),
            "show_selected_output_plugin": True,
            "show_resolution_multiplier": True,
        }

        self.setup_zero_conf()

        self.setup_settings_window(
            [
                (XRMenuGeneralTabletARFrame, general_menu_config),
                (XRMenuSystemInfo, {"collapsed": True}),
                (
                    XRMenuAdvancedFrame,
                    {"components": advancedComponents, "collapsed": True},
                ),
            ],
            icons=["data/icon/tabletar.svg", "data/icon/tabletar_active.svg"],
        )
