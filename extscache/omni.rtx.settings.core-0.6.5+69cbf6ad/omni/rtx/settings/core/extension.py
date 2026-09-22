# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ext
import carb.settings
from omni.rtx.window.settings import RendererSettingsFactory

from .widgets.common_widgets import CommonSettingStack
from .widgets.post_widgets import PostSettingStack
from .widgets.pt_widgets import PTSettingStack
from .widgets.rt_widgets import RTSettingStack
from .widgets.rtpt_widgets import RTPTSettingStack


class RTXSettingsExtension(omni.ext.IExt):

    MENU_PATH = "Rendering"

    rendererNames = ["Real-Time", "Interactive (Path Tracing)", "Real-Time 2.0"]
    stackNames = ["Common", "Ray Tracing", "Path Tracing", "Real-Time 2.0", "Post Processing"]

    def on_startup(self):
        RendererSettingsFactory.register_stack(self.stackNames[0], CommonSettingStack)
        RendererSettingsFactory.register_stack(self.stackNames[1], RTSettingStack)
        RendererSettingsFactory.register_stack(self.stackNames[2], PTSettingStack)
        RendererSettingsFactory.register_stack(self.stackNames[3], RTPTSettingStack)
        RendererSettingsFactory.register_stack(self.stackNames[4], PostSettingStack)
        rtIsEnabled = carb.settings.get_settings().get("/persistent/rtx/modes/rt/enabled")
        ptIsEnabled = carb.settings.get_settings().get("/persistent/rtx/modes/pt/enabled")
        rtptIsEnabled = carb.settings.get_settings().get("/persistent/rtx/modes/rt2/enabled")
        if rtIsEnabled == ptIsEnabled == rtptIsEnabled == False :
            # All renderers are disabled, indicating an invalid configuration. Falling back to the default renderers.
            rtIsEnabled = ptIsEnabled = True

        if rtIsEnabled :
            RendererSettingsFactory.register_renderer(
                self.rendererNames[0], [self.stackNames[0], self.stackNames[1], self.stackNames[4]]
            )
        if ptIsEnabled :
            RendererSettingsFactory.register_renderer(
                self.rendererNames[1], [self.stackNames[0], self.stackNames[2], self.stackNames[4]]
            )
        if rtptIsEnabled :
            RendererSettingsFactory.register_renderer(
                self.rendererNames[2], [self.stackNames[0], self.stackNames[3], self.stackNames[4]]
            )
        RendererSettingsFactory.build_ui()

    def on_shutdown(self):
        for renderer in self.rendererNames:
            RendererSettingsFactory.unregister_renderer(renderer)
        for stack in self.stackNames:
            RendererSettingsFactory.unregister_stack(stack)
        RendererSettingsFactory.build_ui()
