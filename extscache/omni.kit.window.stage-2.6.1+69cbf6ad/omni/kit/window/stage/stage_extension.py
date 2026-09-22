# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["StageExtension"]

import asyncio
import omni.ext
import omni.ui as ui
from omni.kit.menu.utils import MenuHelperExtension

from .stage_window import StageWindow


class StageExtension(omni.ext.IExt, MenuHelperExtension):
    """The entry point for Stage Window"""

    WINDOW_NAME = "Stage"
    MENU_GROUP = "Window"

    def on_startup(self):
        ui.Workspace.set_show_window_fn(StageExtension.WINDOW_NAME, self.show_window)
        ui.Workspace.show_window(StageExtension.WINDOW_NAME)

        self.menu_startup(StageExtension.WINDOW_NAME, StageExtension.WINDOW_NAME, StageExtension.MENU_GROUP)

    def on_shutdown(self):
        self.menu_shutdown()
        if self._window:
            self._window.destroy()
            self._window = None

        ui.Workspace.set_show_window_fn(StageExtension.WINDOW_NAME, None)

    async def _destroy_window_async(self):
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._window:
            self._window.destroy()
            self._window = None

    def _visiblity_changed_fn(self, visible):
        self.menu_refresh()
        if not visible:
            # Destroy the window, since we are creating new window
            # in show_window
            asyncio.ensure_future(self._destroy_window_async())

    def show_window(self, value):
        if value:
            self._window = StageWindow()
            self._window.set_visibility_changed_listener(self._visiblity_changed_fn)
        elif self._window:
            self._window.visible = False
