# Copyright (c) 2022-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import omni.ext
import omni.kit.ui
import omni.ui as ui
from omni.kit.stagerecorder.core import *

from .window import RecordWindow


class PublicExtension(omni.ext.IExt):
    WINDOW_NAME = "Stage Recorder"
    MENU_PATH = f"Window/Animation/{WINDOW_NAME}"

    def on_startup(self, ext_id):
        self._ext_id = ext_id
        self._plugin = acquire_interface()
        self._window = None

        # Allows someone to call ui.Workspace.show_window("Stage Recorder") for example
        ui.Workspace.set_show_window_fn(PublicExtension.WINDOW_NAME, lambda visible: self.show_window(None, visible))

        # Insertion into main menu with working toggle
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu = editor_menu.add_item(
                PublicExtension.MENU_PATH,
                self.show_window,
                toggle=True,
                value=False,
            )

    def on_shutdown(self):
        ui.Workspace.set_show_window_fn(PublicExtension.WINDOW_NAME, None)

        if self._window:
            self._window.set_visibility_changed_fn(None)
            self._window.destroy()
            self._window = None

        if self._menu:
            self._menu = None

        release_interface(self._plugin)

    def show_window(self, menu_path: str, visible: bool):
        if visible:
            if self._is_initialized():
                if not self._window:
                    self._window = RecordWindow(self._ext_id, self._plugin)
                    self._window.set_visibility_changed_fn(self._visiblity_changed_fn)
                self._window.show()
        elif self._window:
            self._window.hide()

    def _visiblity_changed_fn(self, visible):
        self._set_menu_value(visible)

    def _set_menu_value(self, checked: bool):
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            editor_menu.set_value(PublicExtension.MENU_PATH, checked)

    def _is_initialized(self):
        has_ext_id = hasattr(self, "_ext_id") and bool(self._ext_id)
        if not has_ext_id:
            carb.log_error(f"{PublicExtension.WINDOW_NAME}: Unexpected missing extension ID")

        has_plugin = hasattr(self, "_plugin") and bool(self._plugin)
        if not has_plugin:
            carb.log_error(f"{PublicExtension.WINDOW_NAME}: Unexpected missing plug-in")

        return has_ext_id and has_plugin
