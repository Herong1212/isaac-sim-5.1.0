# Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
import omni.ext
import carb

from omni.kit.menu.utils import MenuHelperExtensionFull
from .ui_components.caption_window import CaptionWindow
from .settings import ReplicatorCaptionSettings


_extension_instance = None
_ext_id = None
_ext_path = None


def get_instance():
    return _extension_instance


def get_ext_id():
    return _ext_id


def get_ext_path():
    return _ext_path


class IRCInfoCollectorExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        # this step is used to handle the warp issue in the recent version.
        # would be removed later.
        import warp

        warp.init()

        self._menu_helper = MenuHelperExtensionFull()

        # Set instance
        global _extension_instance
        _extension_instance = self
        global _ext_id
        _ext_id = ext_id
        global _ext_path
        _ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id)
        ReplicatorCaptionSettings.EXT_PATH = get_ext_path()

        self._build_ui(ext_id)

    def _build_ui(self, ext_id):
        idx = self._menu_helper.menu_startup(
            lambda eid=ext_id: CaptionWindow(eid),
            "VLM Scene Captioning",
            "VLM Scene Captioning",
            "Tools/Action and Event Data Generation",
            verbose=False,
        )
        self._menu_helper.show_window("", True, idx)
        # Temporary solution to trigger menu refresh
        # since menu helper doest not trigger it at start
        import omni.kit.menu.utils

        omni.kit.menu.utils.rebuild_menus()

    def on_shutdown(self):
        """Cleanup objects on extension shutdown"""

        async def shutdown_menu_helper(menu_helper):
            # First make sure all windows are closed
            for i in range(len(menu_helper._window_list)):
                menu_helper.show_window(None, False, i)
            # Wait for MenuHelperExtensionFull._destroy_window_async to trigger
            await omni.kit.app.get_app().next_update_async()
            # Wait for MenuHelperExtensionFull._destroy_window_async to finish
            await omni.kit.app.get_app().next_update_async()
            # Finally we shutdown the menu
            menu_helper.menu_shutdown()

        asyncio.ensure_future(shutdown_menu_helper(self._menu_helper))

        # Clean variables
        self._core_ext = None
