# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from .retarget_window import RetargetWindow
from .retarget_properties import RetargetProperties
from .skel_selection_combo import StageInfo
from .viewport_menu import RetargetViewportMenu

import carb
import omni.ext
import omni.kit.browser.sample

ext = None


class PublicExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        global ext
        ext = self
        self._stage_info = StageInfo()
        self._window = RetargetWindow(ext_id, self._stage_info)
        self._properties = RetargetProperties()

        self._sample_folder = carb.settings.get_settings().get_as_string("/exts/omni.anim.retarget/sample_folder")
        if self._sample_folder:
            omni.kit.browser.sample.register_sample_folder(self._sample_folder, "Animation/Retargeting")

        self._usd_context = omni.usd.get_context()
        events = self._usd_context.get_stage_event_stream()
        self._stage_event_sub = events.create_subscription_to_pop(
            self._on_stage_event, name="retarget window stage event"
        )

        self._viewport_menu = RetargetViewportMenu()

    def _on_stage_event(self, event: carb.events.IEvent):
        if self._window:
            if event.type == int(omni.usd.StageEventType.CLOSED):
                self._window.rebuild()
            elif event.type == int(omni.usd.StageEventType.OPENED):
                self._window.rebuild()
            elif event.type == int(omni.usd.StageEventType.HIERARCHY_CHANGED):
                self._window.rebuild()

    def on_shutdown(self):
        global ext

        if self._viewport_menu:
            self._viewport_menu.destroy()
            self._viewport_menu = None

        if self._window:
            self._window.destroy()
            self._window = None

        self._properties.on_shutdown()
        self._properties = None

        self._stage_info.on_shutdown()
        self._stage_info = None

        if self._sample_folder:
            omni.kit.browser.sample.unregister_sample_folder(self._sample_folder)

        ext = None

    def open_window(self):
        self._window.open_window()

    def set_skeleton(self, skel_path):
        if self._window:
            self._window.set_skeleton(skel_path)

    def get_skeleton(self):
        return self._window.get_skeleton()


def open_window():
    global ext
    ext.open_window()


def select_skeleton(skel_path):
    global ext
    ext.set_skeleton(skel_path)


def get_skeleton():
    global ext
    return ext.get_skeleton()
