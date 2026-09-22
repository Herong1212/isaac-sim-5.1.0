# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["SimpleGrid", "SimpleOrigin", "CameraAxisLayer"]

# Simple scene items that don't yet warrant a devoted extension

from typing import Optional, Sequence

import carb
import omni.ui
from omni.ui import (
    scene as sc,
    color as cl
)
from pxr import UsdGeom, Gf


def _flatten_matrix(matrix: Gf.Matrix4d):
    m0, m1, m2, m3 = matrix[0], matrix[1], matrix[2], matrix[3]
    return [m0[0], m0[1], m0[2], m0[3],
            m1[0], m1[1], m1[2], m1[3],
            m2[0], m2[1], m2[2], m2[3],
            m3[0], m3[1], m3[2], m3[3]]


def _flatten_rot_matrix(matrix: Gf.Matrix3d):
    m0, m1, m2 = matrix[0], matrix[1], matrix[2]
    return [m0[0], m0[1], m0[2], 0,
            m1[0], m1[1], m1[2], 0,
            m2[0], m2[1], m2[2], 0,
            0, 0, 0, 1]


class SimpleGrid:
    def __init__(self, vp_args, line_count: float = 100, line_step: float = 10, thicknes: float = 1,
                 color: Optional[cl] = None):
        self.__viewport_grid_vis_sub: Optional[carb.SubscriptionId] = None
        self.__transform: sc.Transform = sc.Transform()
        if color is None:
            color = cl(0.25)
        with self.__transform:
            for i in range(line_count * 2 + 1):
                sc.Line(
                    ((i - line_count) * line_step, 0, -line_count * line_step),
                    ((i - line_count) * line_step, 0, line_count * line_step),
                    color=color, thickness=thicknes,
                )
                sc.Line(
                    (-line_count * line_step, 0, (i - line_count) * line_step),
                    (line_count * line_step, 0, (i - line_count) * line_step),
                    color=color, thickness=thicknes,
                )

        self.__vc_change = None
        viewport_api = vp_args.get('viewport_api')
        if viewport_api:
            self.__vc_change = viewport_api.subscribe_to_view_change(self.__view_changed)

            self.__viewport_api_id: str = str(viewport_api.id)
            self.__viewport_grid_vis_sub = carb.settings.get_settings().subscribe_to_node_change_events(
                f"/persistent/app/viewport/{self.__viewport_api_id}/guide/grid/visible",
                self.__viewport_grid_display_changed
            )
            self.__viewport_grid_display_changed(None, carb.settings.ChangeEventType.CHANGED)

    def __del__(self):
        self.destroy()

    def __view_changed(self, viewport_api):
        stage = viewport_api.stage
        up = UsdGeom.GetStageUpAxis(stage) if stage else None
        if up == UsdGeom.Tokens.z:
            self.__transform.transform = [0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1]
        elif up == UsdGeom.Tokens.x:
            self.__transform.transform = [0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]
        else:
            self.__transform.transform = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]

    def __viewport_grid_display_changed(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            key = f"/persistent/app/viewport/{self.__viewport_api_id}/guide/grid/visible"
            self.visible = bool(carb.settings.get_settings().get(key))

    @property
    def name(self):
        return 'Grid'

    @property
    def categories(self):
        return ['guide']

    @property
    def visible(self):
        return self.__transform.visible

    @visible.setter
    def visible(self, value):
        self.__transform.visible = bool(value)

    def destroy(self):
        if self.__viewport_grid_vis_sub is not None:
            carb.settings.get_settings().unsubscribe_to_change_events(self.__viewport_grid_vis_sub)
            self.__viewport_grid_vis_sub = None
        if self.__vc_change:
            self.__vc_change.destroy()
            self.__vc_change = None


class SimpleOrigin:
    def __init__(self, desc: dict, visible: bool = False, length: float = 5, thickness: float = 4):
        self.__viewport_origin_vis_sub: Optional[carb.SubscriptionId] = None
        self._transform: sc.Transform = sc.Transform(visible=visible)
        with self._transform:
            origin = (0, 0, 0)
            sc.Line(origin, (length, 0, 0), color=cl.red, thickness=thickness)
            sc.Line(origin, (0, length, 0), color=cl.green, thickness=thickness)
            sc.Line(origin, (0, 0, length), color=cl.blue, thickness=thickness)

        viewport_api = desc.get('viewport_api')
        if not viewport_api:
            raise RuntimeError('Cannot create CameraAxisLayer without a viewport')

        self.__viewport_api_id: str = str(viewport_api.id)
        self.__viewport_origin_vis_sub = carb.settings.get_settings().subscribe_to_node_change_events(
            f"/persistent/app/viewport/{self.__viewport_api_id}/guide/origin/visible",
            self.__viewport_origin_display_changed
        )
        self.__viewport_origin_display_changed(None, carb.settings.ChangeEventType.CHANGED)

    def __viewport_origin_display_changed(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            key = f"/persistent/app/viewport/{self.__viewport_api_id}/guide/origin/visible"
            self.visible = bool(carb.settings.get_settings().get(key))

    @property
    def name(self):
        return 'Origin'

    @property
    def categories(self):
        return ['guide']

    @property
    def visible(self):
        return self._transform.visible

    @visible.setter
    def visible(self, value):
        self._transform.visible = bool(value)

    def destroy(self):
        if self.__viewport_origin_vis_sub:
            carb.settings.get_settings().unsubscribe_to_change_events(self.__viewport_origin_vis_sub)
            self.__viewport_origin_vis_sub = None


class CameraAxisLayer:
    CAMERA_AXIS_DEFAULT_SIZE = (60, 60)
    CAMERA_AXIS_SIZE_SETTING = "/app/viewport/defaults/guide/axis/size"

    def __init__(self, desc: dict):
        self.__transform = None
        self.__scene_view = None
        self.__vc_change = None
        self.__root = None
        self.__change_event_subs: Optional[Sequence[carb.SubscriptionId]] = None

        viewport_api = desc.get('viewport_api')
        if not viewport_api:
            raise RuntimeError('Cannot create CameraAxisLayer without a viewport')

        settings = carb.settings.get_settings()
        size = settings.get(CameraAxisLayer.CAMERA_AXIS_SIZE_SETTING) or CameraAxisLayer.CAMERA_AXIS_DEFAULT_SIZE

        alignment = omni.ui.Alignment.LEFT_BOTTOM
        direction = omni.ui.Direction.BOTTOM_TO_TOP
        self.__root = omni.ui.Stack(direction)
        with self.__root:
            self.__scene_view = sc.SceneView(
                alignment=alignment,
                width=omni.ui.Length(size[0]),
                height=omni.ui.Length(size[1])
            )
            omni.ui.Spacer()

        thickness = 2
        length = 0.5
        text_offset = length + 0.25
        text_size = 14
        colors = (
            (0.6666, 0.3765, 0.3765, 1.0),
            (0.4431, 0.6392, 0.4627, 1.0),
            (0.3098, 0.4901, 0.6274, 1.0),
        )
        labels = ('X', 'Y', 'Z')
        with self.__scene_view.scene:
            origin = (0, 0, 0)
            self.__transform = sc.Transform()
            with self.__transform:
                for i in range(3):
                    color = colors[i]
                    vector = [0, 0, 0]
                    vector[i] = length
                    sc.Line(origin, vector, color=color, thickness=thickness)
                    vector[i] = text_offset
                    with sc.Transform(transform=sc.Matrix44.get_translation_matrix(vector[0], vector[1], vector[2])):
                        sc.Label(labels[i], color=color, alignment=omni.ui.Alignment.CENTER, size=text_size)

        self.__vc_change = viewport_api.subscribe_to_view_change(self.__view_changed)

        self.__viewport_api_id: str = str(viewport_api.id)
        self.__change_event_subs = (
            settings.subscribe_to_node_change_events(
                f"/persistent/app/viewport/{self.__viewport_api_id}/guide/axis/visible",
                self.__viewport_axis_display_changed
            ),
            settings.subscribe_to_node_change_events(
                f"{CameraAxisLayer.CAMERA_AXIS_SIZE_SETTING}/0", self.__viewport_axis_size_changed
            ),
            settings.subscribe_to_node_change_events(
                f"{CameraAxisLayer.CAMERA_AXIS_SIZE_SETTING}/1", self.__viewport_axis_size_changed
            )
        )

        self.__viewport_axis_display_changed(None, carb.settings.ChangeEventType.CHANGED)

    def __view_changed(self, viewport_api):
        self.__transform.transform = _flatten_rot_matrix(viewport_api.view.GetOrthonormalized().ExtractRotationMatrix())

    def __viewport_axis_display_changed(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            key = f"/persistent/app/viewport/{self.__viewport_api_id}/guide/axis/visible"
            self.visible = bool(carb.settings.get_settings().get(key))

    def __viewport_axis_size_changed(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            size = carb.settings.get_settings().get(CameraAxisLayer.CAMERA_AXIS_SIZE_SETTING)
            if len(size) == 2:
                self.__scene_view.width, self.__scene_view.height = omni.ui.Length(size[0]), omni.ui.Length(size[1])

    def destroy(self):
        if self.__change_event_subs:
            settings = carb.settings.get_settings()
            for sub in self.__change_event_subs:
                settings.unsubscribe_to_change_events(sub)
            self.__change_event_subs = None
        if self.__vc_change:
            self.__vc_change.destroy()
            self.__vc_change = None
        if self.__transform:
            self.__transform.clear()
            self.__transform = None
        if self.__scene_view:
            self.__scene_view.destroy()
            self.__scene_view = None
        if self.__root:
            self.__root.clear()
            self.__root.destroy()
            self.__root = None

    @property
    def visible(self):
        return self.__root.visible

    @visible.setter
    def visible(self, value):
        self.__root.visible = value

    @property
    def categories(self):
        return ['guide']

    @property
    def name(self):
        return 'Axis'
