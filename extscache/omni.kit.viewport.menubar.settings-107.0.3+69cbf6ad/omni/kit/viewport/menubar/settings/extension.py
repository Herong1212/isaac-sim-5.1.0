# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ViewportSettingsMenuBarExtension"]

import omni.ext
from .setting_menu_container import SettingMenuContainer


class ViewportSettingsMenuBarExtension(omni.ext.IExt):
    """The Entry Point for the Viewport Settings in Viewport Menu Bar"""

    def on_startup(self, ext_id):
        self._settings_menu = SettingMenuContainer()  # noqa: PLW0201

    def on_shutdown(self):
        self._settings_menu.destroy()
        self._settings_menu = None  # noqa: PLW0201
