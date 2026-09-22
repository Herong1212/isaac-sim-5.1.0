# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import omni
import omni.usd
import omni.ui as ui
from omni.ui import scene as sc
from omni.ui import color as cl
from omni.kit.viewport.utility import get_active_viewport_window

from pxr import Sdf, Gf, Tf, Usd, UsdGeom, UsdSkel
from typing import List, Optional, Tuple

import math

UP_TEXT = "Up"
FORWARD_TEXT = "Forward"
TEXT_SIZE = 30
# nv green: R 118(76) G 185(B9) B 0
UP_COLOR = cl("#00B976")
FORWARD_COLOR = cl("#0076b9")
BG_COLOR = cl("#cdcdcd")
DRAW_ON_VP1 = True
SUPPORT_MULTI_VP1 = True


SETTING_DISPLAY_RETARGET_AXES = "/persistent/exts/omni.anim.retarget.ui/displayRetargetAxes"


class CameraModel(sc.AbstractManipulatorModel):
    """
    The model that tracks the current USD camera and has two items
    'projection' and 'view' that represent the camera matrices.
    """
    def __init__(self):
        super().__init__()

        # Active camera
        self._camera_prim = None
        self._camera_path = None
        self._stage_listener = None

        def on_usd_context_event(event: carb.events.IEvent):
            event_type = event.type
            if event_type == int(omni.usd.StageEventType.OPENED) or event_type == int(omni.usd.StageEventType.CLOSING):
                if self._stage_listener:
                    self._stage_listener.Revoke()
                    self._stage_listener = None
                self._camera_prim = None
                self._camera_path = None
            if event_type == int(omni.usd.StageEventType.OPENED):
                stage = omni.usd.get_context().get_stage()
                self._stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._notice_changed, stage)

        self._stage_event_sub = omni.usd.get_context().get_stage_event_stream().create_subscription_to_pop(
            on_usd_context_event, name="CameraModel stage event"
        )

        # Tracking the camera
        stage = omni.usd.get_context().get_stage()
        if stage:
            self._stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._notice_changed, stage)

    def destroy(self):
        self._stage_event_sub = None
        if self._stage_listener:
            self._stage_listener.Revoke()
            self._stage_listener = None
        self._stage_listener = None
        self._camera_prim = None
        self._camera_path = None
        super().destroy()

    def get_as_floats(self, item):
        """Called by SceneView to get projection and view matrices"""
        if item == self.get_item("projection"):
            return self._get_projection()
        if item == self.get_item("view"):
            return self._get_view()

    def set_floats(self, item, value):
        self._item_changed(item)

    def _notice_changed(self, notice, stage):
        """Called by Tf.Notice"""
        for p in notice.GetChangedInfoOnlyPaths():
            if p.GetPrimPath() == self._camera_path:
                # If it's a camera, dirty the model and view will request new
                # matrices when it needs
                # Technically the view also changes when a parent of the
                # camera_path has changed transform; but for an example
                # it's fine.
                self._item_changed(None)

    @staticmethod
    def _flatten(transform):
        """Convert array[n][m] to array[n*m]"""
        # flatten the matrix by hand
        # USING LIST COMPREHENSION IS VERY SLOW (e.g. return [item for sublist
        # in transform for item in sublist]), which takes around 10ms.
        return [
            transform[0][0],
            transform[0][1],
            transform[0][2],
            transform[0][3],
            transform[1][0],
            transform[1][1],
            transform[1][2],
            transform[1][3],
            transform[2][0],
            transform[2][1],
            transform[2][2],
            transform[2][3],
            transform[3][0],
            transform[3][1],
            transform[3][2],
            transform[3][3],
        ]

    def _get_camera(self):
        """Returns the current camera's frustum"""
        if not self._camera_prim:
            # Get the camera prim
            viewport_window = get_active_viewport_window()
            stage = viewport_window.viewport_api.stage
            if stage:
                self._camera_path = Sdf.Path(viewport_window.viewport_api.camera_path)
                self._camera_prim = stage.GetPrimAtPath(self._camera_path)

        # Extract view and projection
        if self._camera_prim:
            return UsdGeom.Camera(self._camera_prim).GetCamera().frustum

    def _get_view(self) -> List[float]:
        """Returns the view matrix as a list"""
        frustum = self._get_camera()
        if frustum:
            view = frustum.ComputeViewMatrix()
        else:
            view = Gf.Matrix4d(1.0)
        return self._flatten(view)

    def _get_projection(self) -> List[float]:
        """Returns the projection matrix as a list"""
        frustum = self._get_camera()
        if frustum:
            projection = frustum.ComputeProjectionMatrix()
        else:
            projection = Gf.Matrix4d(1.0)
        return self._flatten(projection)


class SkeletonModel(sc.AbstractManipulatorModel):
    """
    User part. The model tracks the position and rotation of the skeleton.
    """
    class VectorItem(sc.AbstractManipulatorItem):
        """
        The Model Item represents the position. It doesn't contain anything
        because because we take the position directly from USD when requesting.
        """
        def __init__(self):
            super().__init__()
            self.value = [0, 0, 0]

    class ValueItem(sc.AbstractManipulatorItem):
        """The Model Item contains a single float value"""
        def __init__(self, value=0):
            super().__init__()
            self.value = [value]

    def __init__(self):
        super().__init__()

        self.draw_up_axis = SkeletonModel.ValueItem()
        self.draw_forward_axis = SkeletonModel.ValueItem()

        self.position = SkeletonModel.VectorItem()
        self.rotation = SkeletonModel.VectorItem()
        self.scale = SkeletonModel.VectorItem()

        self.axis_scales = SkeletonModel.VectorItem()

        self.up_start = SkeletonModel.VectorItem()
        self.up_end = SkeletonModel.VectorItem()
        self.up_text_pos = SkeletonModel.VectorItem()
        self.up_scale = SkeletonModel.ValueItem()

        self.forward_start = SkeletonModel.VectorItem()
        self.forward_end = SkeletonModel.VectorItem()
        self.forward_text_pos = SkeletonModel.VectorItem()
        self.forward_scale = SkeletonModel.ValueItem()

        # current selection
        self._current_path = None
        self._current_prim = None
        self.draw_up_axis.value = 0
        self.draw_forward_axis.value = 0

        def on_usd_context_event(event: carb.events.IEvent):
            event_type = event.type
            if event_type == int(omni.usd.StageEventType.OPENED) or event_type == int(omni.usd.StageEventType.CLOSING):
                if self._stage_listener:
                    self._stage_listener.Revoke()
                    self._stage_listener = None
                self._current_path = None
                self._current_prim = None
            if event_type == int(omni.usd.StageEventType.OPENED):
                stage = omni.usd.get_context().get_stage()
                self._stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._notice_changed, stage)

        self._stage_event_sub = omni.usd.get_context().get_stage_event_stream().create_subscription_to_pop(
            on_usd_context_event, name="CameraModel stage event"
        )
        stage = omni.usd.get_context().get_stage()
        # track selection
        self._stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._notice_changed, stage)

    def destroy(self):
        self._stage_event_sub = None
        if self._stage_listener:
            self._stage_listener.Revoke()
            self._stage_listener = None
        self._stage_listener = None

    def get_item(self, identifier):
        if identifier == "draw_forward_axis":
            return self.draw_forward_axis
        if identifier == "draw_up_axis":
            return self.draw_up_axis
        if identifier == "position":
            return self.position
        if identifier == "rotation":
            return self.rotation
        if identifier == "up_start":
            return self.up_start
        if identifier == "up_end":
            return self.up_end
        if identifier == "up_text_pos":
            return self.up_text_pos
        if identifier == "up_scale":
            return self.up_scale
        if identifier == "forward_start":
            return self.forward_start
        if identifier == "forward_end":
            return self.forward_end
        if identifier == "forward_text_pos":
            return self.forward_text_pos
        if identifier == "forward_scale":
            return self.forward_scale
        if identifier == "scale":
            return self.scale

        raise ValueError(f"Invalid identifier: {identifier}")

    def get_as_value(self, item):
        if item == self.draw_forward_axis:
            return self.draw_forward_axis.value
        if item == self.draw_up_axis:
            return self.draw_up_axis.value
        if item == self.up_scale:
            return self.up_scale.value
        if item == self.forward_scale:
            return self.forward_scale.value
        return 0

    def get_as_vector(self, item):
        if item == self.position:
            return self.position.value
        if item == self.rotation:
            return self.rotation.value
        if item == self.up_start:
            return self.up_start.value
        if item == self.up_end:
            return self.up_end.value
        if item == self.up_text_pos:
            return self.up_text_pos.value
        if item == self.forward_start:
            return self.forward_start.value
        if item == self.forward_end:
            return self.forward_end.value
        if item == self.forward_text_pos:
            return self.forward_text_pos.value
        return []

    def set_skeleton(self, skeleton):
        if not skeleton:
            # this makes the manipulator updated
            self._item_changed(None)
            return
        prim = skeleton.GetPrim()
        if not prim.IsA(UsdSkel.Skeleton):
            return

        prim_path = prim.GetPrimPath()
        if not prim_path:
            return
        self._current_path = prim_path
        self._current_prim = prim
        self._update_transform(prim)

    def get_current_skeleton(self) -> Optional[Usd.Prim]:
        return self._current_prim

    def set_draw_up_axis(self, value):
        if value:
            self.draw_up_axis.value = 1
        else:
            self.draw_up_axis.value = 0
        self._item_changed(None)

    def set_draw_forward_axis(self, value):
        if value:
            self.draw_forward_axis.value = 1
        else:
            self.draw_forward_axis.value = 0
        self._item_changed(None)

    def get_world_matrix(self, prim: Usd.Prim) -> Gf.Matrix4d:
        assert bool(prim), "Prim is invalid"
        xform_cache = UsdGeom.XformCache()
        return xform_cache.GetLocalToWorldTransform(prim)

    def _compute_skeleton_bounding_box(self, skeleton_prim: Usd.Prim) -> (Gf.Vec3d, Gf.Vec3d):
        assert bool(skeleton_prim), "Skeleton prim is invalid"
        assert skeleton_prim.IsA(UsdSkel.Skeleton), f"Prim {skeleton_prim.GetName()} is not a UsdSkel.Skeleton."

        skeleton = UsdSkel.Skeleton(skeleton_prim)
        rest_transforms = skeleton.GetRestTransformsAttr().Get()

        if not rest_transforms:
            raise ValueError("Skeleton has no rest transforms")

        skeleton_world_transform = self.get_world_matrix(skeleton_prim)

        # Initialize min and max corners with the first joint's position
        local_matrix = Gf.Matrix4d(rest_transforms[0])
        world_matrix = skeleton_world_transform * local_matrix
        first_position = world_matrix.ExtractTranslation()
        min_corner = Gf.Vec3d(first_position)
        max_corner = Gf.Vec3d(first_position)

        for local_transform in rest_transforms:
            local_matrix = Gf.Matrix4d(local_transform)
            world_matrix = skeleton_world_transform * local_matrix
            position = world_matrix.ExtractTranslation()

            min_corner = Gf.Vec3d(
                min(min_corner[0], position[0]),
                min(min_corner[1], position[1]),
                min(min_corner[2], position[2])
            )
            max_corner = Gf.Vec3d(
                max(max_corner[0], position[0]),
                max(max_corner[1], position[1]),
                max(max_corner[2], position[2])
            )

        return min_corner, max_corner

    def _compute_skeleton_bounds(self, skeleton_prim: Usd.Prim) -> Gf.Vec3d:
        """
        Calculate the world-space lengths of the bounding box sides of
        the provided Usd.Prim.

        :param skeleton_prim: the Usd.Prim instance of a Skeleton Prim.
        :return: a GfVec3d representing the lengths of the bounding box sides.
        """
        min_corner, max_corner = self._compute_skeleton_bounding_box(skeleton_prim)
        return max_corner - min_corner

    def _update_transform(self, prim):
        def decompose_matrix(matrix: Gf.Matrix4d) -> Tuple[Gf.Vec3d, Gf.Vec3d, Gf.Vec3d]:
            if not isinstance(matrix, Gf.Matrix4d):
                raise ValueError("Input must be a Gf.Matrix4d")

            # Use Factor to decompose the matrix
            isValid, rotation, scale, u, translation, perspectiveMatrix = matrix.Factor()
            # Convert rotation to Euler angles in degrees
            euler_radians = rotation.ExtractRotation().Decompose(Gf.Vec3d(1, 0, 0), Gf.Vec3d(0, 1, 0), Gf.Vec3d(0, 0, 1))
            euler_degrees = Gf.Vec3d(
                math.degrees(euler_radians[0]),
                math.degrees(euler_radians[1]),
                math.degrees(euler_radians[2])
            )

            return translation, euler_degrees, scale

        matrix = self.get_world_matrix(prim)

        translation, rotation_euler, scale = decompose_matrix(matrix)
        self.position.value = translation
        self.rotation.value = rotation_euler
        self.scale.value = scale

        # new: update scale of the axes by checking the bounds of the skeleton prim
        self.axis_scales.value = self._compute_skeleton_bounds(prim)

        # this makes the manipulator update
        self._item_changed(None)

    def _notice_changed(self, notice, stage):
        """Called by Tf.Notice"""
        if self._current_path is not None:
            for p in notice.GetChangedInfoOnlyPaths():
                if self._current_path.HasPrefix(p.GetPrimPath()):
                    cp = stage.GetPrimAtPath(self._current_path)
                    self._update_transform(cp)
                    self._item_changed(None)
                    return

    def get_drawing_transform(self, axis: str):
        start = [0.0, 0.0, 0.0]

        if axis in ["X", "x"]:
            dir = [1.0, 0.0, 0.0]
        if axis in ["Y", "y"]:
            dir = [0.0, 1.0, 0.0]
        if axis in ["Z", "z"]:
            dir = [0.0, 0.0, 1.0]
        if axis in ["-X", "-x", "MINUS X"]:
            dir = [-1.0, 0.0, 0.0]
        if axis in ["-Y", "-y", "MINUS Y"]:
            dir = [0.0, -1.0, 0.0]
        if axis in ["-Z", "-z", "MINUS Z"]:
            dir = [0.0, 0.0, -1.0]

        scale = max(self.axis_scales.value) * 0.4

        end = [dir[0] * scale, dir[1] * scale, dir[2] * scale]
        text_pos = [dir[0] * scale * 1.2, dir[1] * scale * 1.2, dir[2] * scale * 1.2]

        return start, end, text_pos, scale

    def set_up_axis(self, up_axis):
        self.up_start.value, self.up_end.value, self.up_text_pos.value, self.up_scale.value = self.get_drawing_transform(up_axis)
        self._item_changed(None)

    def set_forward_axis(self, forward_axis):
        self.forward_start.value, self.forward_end.value, self.forward_text_pos.value, self.forward_scale.value = self.get_drawing_transform(forward_axis)
        self._item_changed(None)

    def get_current_prim(self) -> Optional[Usd.Prim]:
        return self._current_prim

    def get_current_path(self):
        return self._current_path

    def get_current_prim_world_matrix(self) -> Gf.Matrix4d:
        if self._current_prim:
            return self.get_world_matrix(self._current_prim)
        return Gf.Matrix4d()

class AxisVisualizer(sc.Manipulator):
    def __init__(self, window_visible_fn:callable, **kwargs):
        self._settings = carb.settings.get_settings()
        self._selection = omni.usd.get_context().get_selection()
        self._is_window_visible_fn = window_visible_fn
        super().__init__(**kwargs)

        self._update_sub = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(
            self._on_update_event
        )

        self._should_draw = self._settings.get(SETTING_DISPLAY_RETARGET_AXES)

    def _on_update_event(self, e: carb.events.IEvent):
        self._should_draw = False
        if self._settings.get(SETTING_DISPLAY_RETARGET_AXES):
            # if retarget window is visible
            if self._is_window_visible_fn is not None and self._is_window_visible_fn():
                selected_prims = self._selection.get_selected_prim_paths()
                current_path = self.model.get_current_path()
                if current_path is not None:
                    # if the skeleton or its parent is selected
                    for path in selected_prims:
                        if current_path.HasPrefix(path):
                            self._should_draw = True
                            break
        self.model._item_changed(None)

    def on_build(self):
        """Called when the model is chenged and rebuilds the whole slider"""
        if not self.model:
            return

        draw_forward_axis = self.model.get_as_value(self.model.get_item("draw_forward_axis"))
        draw_up_axis = self.model.get_as_value(self.model.get_item("draw_forward_axis"))

        transform = sc.Matrix44(*CameraModel._flatten(self.model.get_current_prim_world_matrix()))

        if self._should_draw and draw_forward_axis:
            start = self.model.get_as_vector(self.model.get_item("forward_start"))
            end = self.model.get_as_vector(self.model.get_item("forward_end"))
            text_pos = self.model.get_as_vector(self.model.get_item("forward_text_pos"))
            translate = transform * sc.Matrix44.get_translation_matrix(text_pos[0], text_pos[1], text_pos[2])
            with sc.Transform(transform=translate):
                with sc.Transform(look_at=sc.Transform.LookAt.CAMERA, scale_to=sc.Space.SCREEN):
                    sc.Rectangle(250, 70, color=BG_COLOR)
                    sc.Rectangle(250, 70, color=cl.black, thickness=3, wireframe=True)
                sc.Label(
                    FORWARD_TEXT,
                    alignment=ui.Alignment.CENTER,
                    color=FORWARD_COLOR,
                    size=TEXT_SIZE
                )
            with sc.Transform(transform=transform):
                sc.Line([start[0], start[1], start[2]], [end[0], end[1], end[2]], color=FORWARD_COLOR, thickness=5)

        if self._should_draw and draw_up_axis:
            start = self.model.get_as_vector(self.model.get_item("up_start"))
            end = self.model.get_as_vector(self.model.get_item("up_end"))
            text_pos = self.model.get_as_vector(self.model.get_item("up_text_pos"))

            translate = transform * sc.Matrix44.get_translation_matrix(text_pos[0], text_pos[1], text_pos[2])
            with sc.Transform(transform=translate):
                with sc.Transform(look_at=sc.Transform.LookAt.CAMERA, scale_to=sc.Space.SCREEN):
                    sc.Rectangle(100, 70, color=BG_COLOR)
                    sc.Rectangle(100, 70, color=cl.black, thickness=3, wireframe=True)
                sc.Label(
                    UP_TEXT,
                    alignment=ui.Alignment.CENTER,
                    color=UP_COLOR,
                    size=TEXT_SIZE
                )

            with sc.Transform(transform=transform):
                sc.Line([start[0], start[1], start[2]], [end[0], end[1], end[2]], color=UP_COLOR, thickness=5)

    def on_model_updated(self, item):
        # Regenerate the mesh
        self.invalidate()


class DrawSceneViewport():
    def __init__(self, viewport_window, ext_id: str, is_window_visible_fn:callable):
        self.model = SkeletonModel()
        self.model.set_skeleton(None)
        self._scene_view = None
        self._viewport_window = viewport_window
        self._ext_id = ext_id
        self._is_window_visible_fn = is_window_visible_fn
        self.frame = self._viewport_window.get_frame(self._ext_id)
        self.frame.set_build_fn(self.__build_frame)

    def __del__(self):
        self.destroy()

    def __destroy__(self):
        self.model = None
        if self._scene_view:
            # Empty the SceneView of any elements it may have
            self._scene_view.scene.clear()
            # Be a good citizen, and un-register the SceneView from Viewport updates
            if self._viewport_window:
                self._viewport_window.viewport_api.remove_scene_view(self._scene_view)
        # Remove our references to these objects
        self._viewport_window = None
        self._scene_view = None

    def set_skeleton(self, skeleton):
        if self.model:
            self.model.set_skeleton(skeleton)

    def set_draw_up_axis(self, value):
        if self.model:
            self.model.set_draw_up_axis(value)

    def set_draw_forward_axis(self, value):
        if self.model:
            self.model.set_draw_forward_axis(value)

    def get_draw_up_axis(self):
        if self.model:
            return self.model.draw_up_axis.value

    def get_draw_forward_axis(self):
        if self.model:
            return self.model.draw_forward_axis.value

    def set_up_axis(self, up_axis):
        if up_axis and self.model:
            self.model.set_up_axis(up_axis)

    def set_forward_axis(self, forward_axis):
        if forward_axis and self.model:
            self.model.set_forward_axis(forward_axis)

    def __build_frame(self):
        # Create a unique frame for our SceneView
        with self._viewport_window.get_frame(self._ext_id):
            self._scene_view = sc.SceneView(
                model=CameraModel(),
                aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_HORIZONTAL,
                screen_aspect_ratio=1280 / 720,
            )
            # Add the manipulator into the SceneView's scene
            with self._scene_view.scene:
                AxisVisualizer(window_visible_fn=self._is_window_visible_fn, model=self.model)

            # Register the SceneView with the Viewport to get projection and view updates
            self._viewport_window.viewport_api.add_scene_view(self._scene_view)
