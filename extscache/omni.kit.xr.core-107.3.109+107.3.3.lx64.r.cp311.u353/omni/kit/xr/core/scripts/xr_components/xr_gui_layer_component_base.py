# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

import carb

from .xr_usd_component_base import XRUsdComponentBase


class XRGuiLayerComponentBase(XRUsdComponentBase):

    def __init__(self, name: str):

        super().__init__("xr_gui." + name)

        self.__gui_layer_enabled = True

        self.get_settings().set_default("/xr/ui/enabled", True)

        if not self.get_settings().get_as_bool("/xr/ui/enabled"):
            self.__gui_layer_enabled = False

        super().start("xr_gui." + name, self.__gui_layer_enabled)

    def run_enable_if_enabled(self) -> None:
        # A component or python extension can be loaded
        # after the tool has been enabled, in which
        # case we need to manually trigger the enable

        if not self.__gui_layer_enabled:
            return

        if self.get_xr_core().is_gui_layer_enabled(self.get_name()):
            self.on_enable()
