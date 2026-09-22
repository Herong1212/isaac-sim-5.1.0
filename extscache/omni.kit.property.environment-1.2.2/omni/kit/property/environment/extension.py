# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ext
import omni.kit.window.property

from .environment_property_widget import EnvironmentPropertyWidget


class EnvironmentPropertyExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        self._registered = False
        self._register_widget()

        global _instance
        _instance = self

    def on_shutdown(self):
        global _instance
        if _instance:
            _instance = None

        self._unregister_widget()

    def _register_widget(self):
        w = omni.kit.window.property.get_window()
        if w:
            self._environment_widget = EnvironmentPropertyWidget()
            w.register_widget("prim", "Environment", self._environment_widget)
            self._registered = True

    def _unregister_widget(self):
        if self._registered:
            w = omni.kit.window.property.get_window()
            if w:
                w.unregister_widget("prim", "Environment")
                self._environment_widget.destroy()
                self._registered = False
