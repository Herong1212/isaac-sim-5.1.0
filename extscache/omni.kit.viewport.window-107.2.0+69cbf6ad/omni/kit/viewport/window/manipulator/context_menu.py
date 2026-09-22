## Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ["ViewportClickFactory"]

from typing import Sequence
import importlib.util

from pxr import Gf

import carb
from omni.ui import scene as sc

from ..raycast import perform_raycast_query


class WorldSpacePositionCache:
    def __init__(self):
        self.__ndc_z = None

    def __cache_screen_ndc(self, viewport_api, world_space_pos: Gf.Vec3d):
        screen_space_pos = viewport_api.world_to_ndc.Transform(world_space_pos)
        self.__ndc_z = screen_space_pos[2]

    def get_world_position(self, viewport_api, prim_path: str, world_space_pos: Sequence[float], mouse_ndc: Sequence[float]):
        # Simple case, prim hit and world_space_pos is valid, cache NDC-z
        if prim_path:
            world_space_pos = Gf.Vec3d(*world_space_pos)
            self.__cache_screen_ndc(viewport_api, world_space_pos)
            return world_space_pos

        # No prim-path, deliver a best guess at world-position
        # If never over an object, cacluate NDC-z from camera's center-of-interest
        if self.__ndc_z is None:
            # Otherwise use the camera's center-of-interest as the depth
            camera = viewport_api.stage.GetPrimAtPath(viewport_api.camera_path)
            coi_attr = camera.GetAttribute('omni:kit:centerOfInterest')
            if coi_attr:
                world_space_pos = viewport_api.transform.Transform(coi_attr.Get(viewport_api.time))
                self.__cache_screen_ndc(viewport_api, world_space_pos)

        # If we have depth (in NDC), move (x_ndc, y_ndz, z_ndc) to a world-space position
        if mouse_ndc and self.__ndc_z is not None:
            return viewport_api.ndc_to_world.Transform(Gf.Vec3d(mouse_ndc[0], mouse_ndc[1], self.__ndc_z))

        # Nothing, return whatever it was
        return Gf.Vec3d(*world_space_pos)


class ClickGesture(sc.ClickGesture):
    def __init__(self, viewport_api, mouse_button: int = 1):
        super().__init__(mouse_button=mouse_button)
        self.__viewport_api = viewport_api
        self.__ndc_mouse = None

    def __query_completed(self, prim_path: str, world_space_pos, *args):
        viewport_api = self.__viewport_api
        world_space_pos = WorldSpacePositionCache().get_world_position(viewport_api, prim_path, world_space_pos, self.__ndc_mouse)
        if not prim_path:
            selected_prims = viewport_api.usd_context.get_selection().get_selected_prim_paths()
            if len(selected_prims) == 1:
                prim_path = selected_prims[0]
            else:
                prim_path = None

        self.on_clicked(viewport_api.usd_context_name, prim_path, world_space_pos, viewport_api.stage)

    def on_ended(self, *args):
        self.__ndc_mouse = self.sender.gesture_payload.mouse
        mouse, viewport_api = self.__viewport_api.map_ndc_to_texture_pixel(self.__ndc_mouse)
        if mouse and viewport_api:
            perform_raycast_query(
                viewport_api=viewport_api,
                mouse_ndc=self.__ndc_mouse,
                mouse_pixel=mouse,
                on_complete_fn=self.__query_completed
            )

    # User callback when click and Viewport query have completed
    def on_clicked(self, usd_context_name: str, prim_path: str, world_space_pos: Gf.Vec3d, stage):
        # Honor legacy setting /exts/omni.kit.window.viewport/showContextMenu, but ony when it is actually set
        legacy_show_context_menu = carb.settings.get_settings().get("/exts/omni.kit.window.viewport/showContextMenu")
        if (legacy_show_context_menu is not None) and (bool(legacy_show_context_menu) is False):
            return

        try:
            from omni.kit.context_menu import ViewportMenu
            ViewportMenu.show_menu(
                usd_context_name, prim_path, world_space_pos, stage
            )
        except (AttributeError, ImportError):
            if importlib.util.find_spec('omni.kit.context_menu') is None:
                carb.log_error('omni.kit.context_menu must be loaded to use the context menu')
            else:
                carb.log_error('omni.kit.context_menu 1.3.7+ must be loaded to use the context menu')


class ViewportClickManipulator(sc.Manipulator):
    def __init__(self, viewport_api, mouse_button: int = 1, **kwargs):
        super().__init__(**kwargs)
        self.__gesture = ClickGesture(viewport_api, mouse_button)
        self.__transform = None
        self.__screen = None

    def on_build(self):
        # Need to hold a reference to this or the sc.Screen would be destroyed when out of scope
        self.__transform = sc.Transform()
        with self.__transform:
            self.__screen = sc.Screen(gesture=self.__gesture)

    def destroy(self):
        if self.__transform:
            self.__transform.clear()
            self.__transform = None
        self.__screen = None

    @property
    def categories(self) -> Sequence:
        return ('manipulator',)

    @property
    def name(self) -> str:
        return "ContextMenu"


ViewportClickFactory = lambda desc: ViewportClickManipulator(desc.get('viewport_api'))
