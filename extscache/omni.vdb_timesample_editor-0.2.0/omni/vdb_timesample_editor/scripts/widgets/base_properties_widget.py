# Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.kit.window.property as p
import omni.usd as ou
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget


class BasePropertiesWidget(UsdPropertiesWidget):
    def __init__(self, title, element_type):
        super().__init__(title, collapsed=False, multi_edit=False)

        self.element_type = element_type
        self.id = "omni.vdb_timesample_editor." + element_type

        w = p.get_window()
        w.register_widget("prim", self.id, self)

    def clean(self):
        self.reset()
        super().clean()

    def reset(self):
        super().reset()

    def on_shutdown(self):
        w = p.get_window()
        w.unregister_widget("prim", self.id)

    def on_new_payload(self, payload):
        if not super().on_new_payload(payload):
            return False

        if len(self._payload) == 0:
            return False

        for path in self._payload:
            prim = self._get_prim(path)
            if prim is None:
                return False
            if prim.GetTypeName() == self.element_type:
                return True

        return False

    def get_prim(self):
        return ou.get_context().get_stage().GetPrimAtPath(self._payload[-1])

    def build_items(self):
        self.reset()

        if len(self._payload) == 0:
            return

        # call build in children class
        self.build_properties()
