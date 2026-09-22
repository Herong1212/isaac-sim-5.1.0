# Copyright (c) 2018-2025, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ScriptEditorExtension"]

import asyncio

import omni.ext
from omni.kit.menu.utils import MenuHelperExtensionFull

from .script_editor_window import ScriptEditorWindow


class ScriptEditorExtension(omni.ext.IExt, MenuHelperExtensionFull):
    """The entry point for Script Editor Window"""

    def _create_window(self):
        return ScriptEditorWindow(self._ext_name)

    def on_startup(self, ext_id):
        self._ext_name = omni.ext.get_extension_name(ext_id)
        self.menu_startup(self._create_window, ScriptEditorWindow.TITLE, ScriptEditorWindow.TITLE, "Window")

    def on_shutdown(self):
        self.menu_shutdown()

    async def _destroy_window_async(self, index):
        # Here do not destroy window when invisible to keep script in text editor
        return
