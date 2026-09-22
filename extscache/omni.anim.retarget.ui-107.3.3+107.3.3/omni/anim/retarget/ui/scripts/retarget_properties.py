# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.usd
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutProperty
from omni.kit.property.usd.widgets import ICON_PATH

from pxr import Sdf, Usd, UsdSkel
import RetargetingSchema

from pathlib import Path


CONTROL_RIG_PROPS = [
    "controlRig:forwardAxis",
    "controlRig:upAxis"
]

ANIMATION_SKEL_BINDING_PROPS = [
    "animationSkelBinding:sourceSkeleton"
]


class RetargetProperties:
    def __init__(self):
        self.on_startup()
        self._control_rig_widget = None
        self._anim_skel_binding = None

    def on_startup(self):
        self._add_menus = []
        import omni.kit.window.property as p
        w = p.get_window()
        if w:
            self._control_rig_widget = ControlRigPropertiesWidget("Control Rig")
            w.register_widget(
                "prim",
                "control_rig",
                self._control_rig_widget
            )
            self._animation_skel_binding = AnimationSkelBindingPropertiesWidget("Skeletal Binding")
            w.register_widget(
                "prim",
                "AnimationSkelBinding",
                self._animation_skel_binding
            )

    def on_shutdown(self):
        self._add_menus = []
        import omni.kit.window.property as p
        w = p.get_window()
        if w:
            if self._control_rig_widget is not None:
                w.unregister_widget("prim", "control_rig")
                self._control_rig_widget.destroy()
                self._control_rig_widget = None
            if self._animation_skel_binding is not None:
                w.unregister_widget("prim", "AnimationSkelBinding")
                self._animation_skel_binding.destroy()
                self._animation_skel_binding = None


class ControlRigPropertiesWidget(UsdPropertiesWidget):
    def __init__(self, title: str):
        super().__init__(title, collapsed=False)
        from omni.kit.property.usd import PrimPathWidget
        self._add_button_menus = []
        self._add_button_menus.append(
            PrimPathWidget.add_button_menu_entry(
                "Animation/Control Rig",
                show_fn=self.on_show_menu_control_rig,
                onclick_fn=self.on_click_menu_control_rig,
            )
        )
        self._add_button_menus.append(
            PrimPathWidget.add_button_menu_entry(
                "Animation/Retargeting",
                show_fn=self.on_show_menu_retargeting,
                onclick_fn=self.on_click_menu_retargeting,
            )
        )

    def destroy(self):
        from omni.kit.property.usd import PrimPathWidget
        for menu in self._add_button_menus:
            PrimPathWidget.remove_button_menu_entry(menu)
        self._add_button_menus = []

    def on_show_menu_control_rig(self, objects: dict):
        if "prim_list" not in objects or "stage" not in objects:
            return False
        stage = objects["stage"]
        if not stage:
            return False
        prim_list = objects["prim_list"]
        if len(prim_list) < 1:
            return False
        for item in prim_list:
            if isinstance(item, Sdf.Path):
                prim = stage.GetPrimAtPath(item)
            elif isinstance(item, Usd.Prim):
                prim = item
            if prim.IsA(UsdSkel.Skeleton) and not prim.HasAPI(RetargetingSchema.ControlRigAPI):
                return True
        return False

    def on_click_menu_control_rig(self, payload: PrimSelectionPayload):
        if payload is None:
            return Sdf.Path.emptyPath
        prim_paths = payload.get_paths()
        omni.kit.commands.execute("ApplyControlRigAPICommand", paths=prim_paths)
        return prim_paths

    def on_show_menu_retargeting(self, objects: dict):
        if "prim_list" not in objects or "stage" not in objects:
            return False
        stage = objects["stage"]
        if not stage:
            return False
        prim_list = objects["prim_list"]
        if len(prim_list) < 1:
            return False
        if len(prim_list) > 0:
            item = prim_list[0]
            if isinstance(item, Sdf.Path):
                prim = stage.GetPrimAtPath(item)
            elif isinstance(item, Usd.Prim):
                prim = item
            if prim.IsA(UsdSkel.Skeleton) and not prim.HasAPI(RetargetingSchema.ControlRigAPI):
                return True
        return False

    def on_click_menu_retargeting(self, payload: PrimSelectionPayload):
        if payload is None:
            return Sdf.Path.emptyPath
        prim_paths = payload.get_paths()
        if len(prim_paths) > 0:
            omni.kit.commands.execute("ApplyControlRigAPICommand", paths=[prim_paths[0]])
            omni.kit.commands.execute("RetargetOpenWindowCommand", skel_path=prim_paths[0])
            return [prim_paths[0]]
        return []

    def on_new_payload(self, payload):
        if not super().on_new_payload(payload):
            return False
        if not self._payload or len(self._payload) == 0:
            return False
        for prim_path in payload:
            prim = self._get_prim(prim_path)
            if not prim:
                return False
            if prim.IsA(UsdSkel.Skeleton) and prim.HasAPI(RetargetingSchema.ControlRigAPI):
                return True
        return False

    def _filter_props_to_build(self, props):
        return [prop for prop in props if prop.GetName() in CONTROL_RIG_PROPS]

    def _customize_props_layout(self, props):
        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            CustomLayoutProperty("controlRig:forwardAxis", "Forward Axis")
            CustomLayoutProperty("controlRig:upAxis", "Up Axis")
        return frame.apply(props)


class AnimationSkelBindingPropertiesWidget(UsdPropertiesWidget):
    def __init__(self, title: str):
        super().__init__(title, collapsed=False)
        from omni.kit.property.usd import PrimPathWidget
        self._add_button_menus = []
        self._add_button_menus.append(
            PrimPathWidget.add_button_menu_entry(
                "Animation/Skeletal Binding",
                show_fn=self.on_show_menu,
                onclick_fn=self.on_click_menu,
            )
        )

    def destroy(self):
        from omni.kit.property.usd import PrimPathWidget
        for menu in self._add_button_menus:
            PrimPathWidget.remove_button_menu_entry(menu)
        self._add_button_menus = []

    def on_show_menu(self, objects: dict):
        if "prim_list" not in objects or "stage" not in objects:
            return False
        stage = objects["stage"]
        if not stage:
            return False
        prim_list = objects["prim_list"]
        if len(prim_list) < 1:
            return False
        for item in prim_list:
            if isinstance(item, Sdf.Path):
                prim = stage.GetPrimAtPath(item)
            elif isinstance(item, Usd.Prim):
                prim = item
            if prim.IsA(UsdSkel.Animation) and not prim.HasAPI(RetargetingSchema.AnimationSkelBindingAPI):
                return True
        return False

    def on_click_menu(self, payload: PrimSelectionPayload):
        if payload is None:
            return Sdf.Path.emptyPath
        prim_paths = payload.get_paths()
        omni.kit.commands.execute("ApplyAnimationSkelBindingAPICommand", paths=prim_paths)
        return prim_paths

    def on_new_payload(self, payload):
        if not super().on_new_payload(payload):
            return False
        if not self._payload or len(self._payload) == 0:
            return False
        for prim_path in payload:
            prim = self._get_prim(prim_path)
            if not prim:
                return False
            if prim.IsA(UsdSkel.Animation) and prim.HasAPI(RetargetingSchema.AnimationSkelBindingAPI):
                return True
        return False

    def get_additional_kwargs(self, ui_attr):
        random_prim = Usd.Prim()
        if self._payload:
            prim_paths = self._payload.get_paths()
            for prim_path in prim_paths:
                prim = self._get_prim(prim_path)
                if not prim:
                    continue
                if not random_prim:
                    random_prim = prim
                elif random_prim.GetTypeName() != prim.GetTypeName():
                    break
        if ui_attr.prop_name == "animationSkelBinding:sourceSkeleton":
            return None, {"target_picker_filter_type_list": [UsdSkel.Skeleton], "targets_limit": 1}
        return None, None

    def _filter_props_to_build(self, props):
        return [prop for prop in props if prop.GetName() in ANIMATION_SKEL_BINDING_PROPS]

    def _customize_props_layout(self, props):
        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            CustomLayoutProperty("animationSkelBinding:sourceSkeleton", "Source Skeleton")
        return frame.apply(props)
