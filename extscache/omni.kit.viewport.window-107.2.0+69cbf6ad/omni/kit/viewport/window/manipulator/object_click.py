## Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ["ObjectClickFactory"]

from typing import Sequence

from omni.ui import scene as sc
from pxr import Gf, Sdf
import carb
import omni.kit.commands
from ..raycast import perform_raycast_query


KIT_COI_ATTRIBUTE = 'omni:kit:centerOfInterest'


class ObjectClickGesture(sc.DoubleClickGesture):
    def __init__(self, viewport_api, mouse_button: int):
        super().__init__(mouse_button=mouse_button)
        self.__viewport_api = viewport_api
        self.__ndc_mouse = None

    def __query_completed(self, prim_path: str, world_space_pos, *args):
        if not prim_path:
            return

        viewport_api = self.__viewport_api
        stage = viewport_api.stage
        cam_path = viewport_api.camera_path
        cam_prim = stage.GetPrimAtPath(cam_path)
        if not cam_prim:
            carb.log_error(f'Could not find prim for camera path "{cam_path}"')
            return
        if True:  # noqa PLW0125
            # Get position directly from USD
            from pxr import Usd, UsdGeom
            hit_prim = stage.GetPrimAtPath(prim_path)
            if not hit_prim:
                carb.log_error(f'Could not find prim for hit path "{prim_path}"')
                return
            box_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
            prim_center = box_cache.ComputeWorldBound(hit_prim).ComputeCentroid()
        else:
            # Get the word-transform of the hit prim
            prim_matrix = Gf.Matrix4d(*viewport_api.usd_context.compute_path_world_transform(prim_path))
            # Get the position of the center of the object (based on transform)
            prim_center = prim_matrix.Transform(Gf.Vec3d(0, 0, 0))

        # Move the prim center into local space of the camera
        prim_center = viewport_api.view.Transform(prim_center)
        # Set the camera's center-of-interest attribute (in an undo-able way)
        coi_attr = cam_prim.GetAttribute(KIT_COI_ATTRIBUTE)
        omni.kit.commands.execute("ChangePropertyCommand",
                                  prop_path=coi_attr.GetPath(),
                                  value=prim_center,
                                  prev=coi_attr.Get() if coi_attr else None,
                                  type_to_create_if_not_exist=Sdf.ValueTypeNames.Vector3d)

    def on_ended(self, *args):
        if self.state == sc.GestureState.CANCELED:
            return
        self.__ndc_mouse = self.sender.gesture_payload.mouse
        mouse, viewport_api = self.__viewport_api.map_ndc_to_texture_pixel(self.__ndc_mouse)
        if mouse and viewport_api:
            perform_raycast_query(viewport_api=viewport_api,
                                  mouse_ndc=self.__ndc_mouse,
                                  mouse_pixel=mouse,
                                  on_complete_fn=self.__query_completed)


class ObjectClickManipulator(sc.Manipulator):
    VP_COI_SETTING = "/exts/omni.kit.viewport.window/coiDoubleClick"

    def __init__(self, viewport_api, mouse_button: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.__gesture = ObjectClickGesture(viewport_api, mouse_button)
        self.__transform = None
        self.__screen = None
        settings = carb.settings.get_settings()
        self.__setting_sub = settings.subscribe_to_node_change_events(self.VP_COI_SETTING, self.__coi_enabled_changed)

    def __coi_enabled_changed(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if self.__screen and event_type == carb.settings.ChangeEventType.CHANGED:
            self.__screen.visible = carb.settings.get_settings().get(self.VP_COI_SETTING)

    def on_build(self):
        # Need to hold a reference to this or the sc.Screen would be destroyed when out of scope
        self.__transform = sc.Transform()
        with self.__transform:
            self.__screen = sc.Screen(gesture=self.__gesture)
        # Enable / Disable functionality based on current setting value
        self.__coi_enabled_changed(None, carb.settings.ChangeEventType.CHANGED)

    def destroy(self):
        setting_sub, self.__setting_sub = self.__setting_sub, None
        if setting_sub is not None:
            carb.settings.get_settings().unsubscribe_to_change_events(setting_sub)
        if self.__transform:
            self.__transform.clear()
            self.__transform = None
        self.__screen = None

    @property
    def categories(self) -> Sequence:
        return ('manipulator',)

    @property
    def name(self) -> str:
        return "ObjectClick"


ObjectClickFactory = lambda desc: ObjectClickManipulator(desc.get('viewport_api'))
