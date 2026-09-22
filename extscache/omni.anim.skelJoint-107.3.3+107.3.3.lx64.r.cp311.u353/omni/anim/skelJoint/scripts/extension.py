# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import carb.settings
import omni.ext
from omni.kit.window.preferences import register_page, unregister_page

from ..bindings._omni_anim_skelJoint import *
from .properties_widget import OmniSkelProperties
from .save_pose import SavePose

kSkelAnimationDragDropSetting = "/app/viewport/animationDragDrop"
kEnabledSavePose = "/exts/omni.anim.skelJoint/enableSavePose"
kViewportDisplayExcludes = "/exts/omni.kit.viewport.menubar.display/showByType/exclude_list"


class PublicExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        self._plugin = acquire_interface()
        self._properties = OmniSkelProperties()
        # check save pose menu support
        settings = carb.settings.get_settings()
        enable_save_pose = settings.get(kEnabledSavePose)
        if enable_save_pose is not None and enable_save_pose:
            self._save_pose = SavePose(ext_id)
        else:
            self._save_pose = None
        # set up for kit to allow drag/drop settings
        self._has_drag_drop_setting = settings.get(kSkelAnimationDragDropSetting)
        settings.set(kSkelAnimationDragDropSetting, True)
        try:
            from .assignAnim import AnimationDropHelper

            self._anim_drop_helper = AnimationDropHelper()
        except ImportError:
            pass

        # Add "Skeletons" in viewport menubar "Display" - "Show By Type" if it is removed
        self.__enable_skeletons_display = False
        try:
            import omni.kit.viewport.menubar.display
            excludes = settings.get(kViewportDisplayExcludes)
            if excludes and "Skeletons" in excludes:
                excludes = [item for item in excludes if item != "Skeletons"]
                settings.set(kViewportDisplayExcludes, excludes)
                self.__enable_skeletons_display = True
        except ImportError:
            pass

    def on_shutdown(self):
        self._properties.on_shutdown()
        self._properties = None
        self._plugin = None
        if self._save_pose:
            self._save_pose.destroy()
            self._save_pose = None
        # restore anim drop helper
        setting = carb.settings.get_settings()
        setting.set(kSkelAnimationDragDropSetting, self._has_drag_drop_setting)
        self._anim_drop_helper = None
        release_interface(self._plugin)

        # Remove "Skeletons" from viewport menubar "Display" - "Show By Type" if it is appended by this extension
        if self.__enable_skeletons_display:
            try:
                import omni.kit.viewport.menubar.display
                excludes = setting.get(kViewportDisplayExcludes)
                if excludes is None:
                    excludes = ["Skeletons"]
                    setting.set(kViewportDisplayExcludes, excludes)
                elif "Skeletons" not in excludes:
                    excludes.append("Skeletons")
                    setting.set(kViewportDisplayExcludes, excludes)
            except ImportError:
                pass
