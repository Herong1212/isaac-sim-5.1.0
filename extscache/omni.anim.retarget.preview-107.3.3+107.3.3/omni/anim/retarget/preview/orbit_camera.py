# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


import enum
import omni.kit.app
from carb import log_error
from carb.events import IEvent
from omni.kit.manipulator.camera import ViewportCameraManipulator
from pxr import Gf, UsdGeom
from typing import Optional, Union


def _flatten_matrix(matrix: Gf.Matrix4d):
    return [matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],
            matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3],
            matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3],
            matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3]]


class ViewSide(enum.IntEnum):
    FRONT = 0
    RIGHT = 1
    TOP = 2
    DIAGONAL = 3


class OrbitViewportCameraManipulator(ViewportCameraManipulator):
    def __init__(
        self,
        viewport_api,
        bindings: dict = None,
        world_orbit_center: Optional[Union[Gf.Vec3d, list]] = None,
        *args,
        **kwargs
    ):
        super().__init__(viewport_api, bindings, *args, **kwargs)

        self._stage = viewport_api.stage
        self._center_dirty = False
        self._world_orbit_center: Gf.Vec3d
        self.world_orbit_center = world_orbit_center
        self._viewside = ViewSide.DIAGONAL

        # to generate all internal data
        super()._on_began(self.model, [0, 0])

    @property
    def world_orbit_center(self) -> Gf.Vec3d:
        ''' The center point of orbit, in world space
        '''
        return self._world_orbit_center

    @world_orbit_center.setter
    def world_orbit_center(self, value):
        if value is None:
            self._world_orbit_center = Gf.Vec3d(0, 0, 0)
        elif isinstance(value, Gf.Vec3d):
            self._world_orbit_center = value
        elif isinstance(value, list) and len(value) == 3:
            self._world_orbit_center = Gf.Vec3d(value[0], value[1], value[2])
        else:
            log_error(f'OrbitViewportCameraManipulator: world_orbit_center type is not supported, ' + \
                f'expected: Union[Gf.Vec3d, list], got {type(value)}')

        self._center_dirty = True

    def refresh(self, w_eye_pos: Optional[Gf.Vec3d] = None):
        ''' Refreshes the camera transform manually. May be called after changing the orbit center.

        Args:
            w_eye_pos (Optional[Gf.Vec3d]): new eye position in world space. Pass None to use the current position.
        '''
        self._adjust_rotation(w_eye_pos)
        self.model._item_changed(self.model.get_item('transform'))

    @property
    def position(self) -> Gf.Vec3d:
        return Gf.Matrix4d(*self.model.get_as_floats('transform')).ExtractTranslation()

    def switch_view(self, side: ViewSide, distance: float = 500):
        '''
        Sets the current side view.

        Args:
            - side (ViewSide): the view side to be set
            - distance (float): distance from the orbit center, optional. Default value is 500.
        '''
        self._viewside = side
        w_view_dir = self._get_view_dir(side)
        w_eye = self._world_orbit_center - w_view_dir * distance
        eye_translate = Gf.Matrix4d().SetTranslate(w_eye)
        self.model.set_floats('transform', _flatten_matrix(eye_translate))
        self._adjust_rotation()
        self.refresh()

    def _get_view_dir(self, side: ViewSide) -> Gf.Vec3d:
        if self._stage is None:
            right = Gf.Vec3d(-1, 0, 0)
            forward = Gf.Vec3d(0, 0, 1)
            up = Gf.Vec3d(0, 1, 0)
        else:
            up_axis = UsdGeom.GetStageUpAxis(self._stage)
            if up_axis == UsdGeom.Tokens.x:
                right = Gf.Vec3d(0, 0, -1)
                forward = Gf.Vec3d(0, 1, 0)
                up = Gf.Vec3d(1, 0, 0)
            elif up_axis == UsdGeom.Tokens.y:
                right = Gf.Vec3d(-1, 0, 0)
                forward = Gf.Vec3d(0, 0, 1)
                up = Gf.Vec3d(0, 1, 0)
            elif up_axis == UsdGeom.Tokens.z:
                right = Gf.Vec3d(0, -1, 0)
                forward = Gf.Vec3d(1, 0, 0)
                up = Gf.Vec3d(0, 0, 1)

        if side == ViewSide.FRONT:
            return -forward
        elif side == ViewSide.RIGHT:
            return -right
        elif side == ViewSide.TOP:
            return -up
        else:
            return (-forward - right - 0.5 * up).GetNormalized()

    def _adjust_rotation(self, w_eye_pos: Gf.Vec3d = None):
        if w_eye_pos is None:
            w_eye_pos = Gf.Matrix4d(*self.model.get_as_floats('transform')).ExtractTranslation()
        w_up_axis = Gf.Vec3d(*self.model.get_as_floats('up_axis'))

        # LookAt doesn't handle the case when the lookAt dir is parallel to the up axis
        w_lookat_dir = (self._world_orbit_center - w_eye_pos).GetNormalized()
        if abs(Gf.Dot(w_lookat_dir, w_up_axis)) > 0.99999:
            w_up_axis = Gf.Vec3d(0, 0, 1)

        lookat = Gf.Matrix4d().SetLookAt(w_eye_pos, self._world_orbit_center, w_up_axis)
        self.model.set_floats('transform', _flatten_matrix(lookat.GetInverse()))

    def _on_began(self, model, mouse):
        super()._on_began(model, mouse)

        # super._on_began can apply movement and rotation so we adjust the center of orbit here
        # The new orbit center is computed as the intersection of the camera's forward axis
        #    with the horizontal plane that contains the current center
        # _center_dirty is not set, we don't want to re-adjust the rotation
        if not self._center_dirty:
            transform = Gf.Matrix4d(*self.model.get_as_floats('transform'))
            view = transform.GetInverse()
            camera_orbit_center = view.Transform(self._world_orbit_center)
            orbit_screen_plane_coord = Gf.Vec2d(camera_orbit_center[0], camera_orbit_center[1])
            # camera is no longer looking at the current center, so it moved or rotated
            if Gf.Vec2d.GetDot(orbit_screen_plane_coord, orbit_screen_plane_coord) > 0.0001:
                camera_world_pos = transform.ExtractTranslation()
                camera_world_forward = transform.Transform(Gf.Vec3d(0, 0, -1))
                camera_world_forward = camera_world_forward - camera_world_pos
                up_vec = Gf.Vec3d(0, 1, 0)
                stage_up_axis = UsdGeom.GetStageUpAxis(self._stage)
                if stage_up_axis == UsdGeom.Tokens.x:
                    up_vec = Gf.Vec3d(1, 0, 0)
                elif stage_up_axis == UsdGeom.Tokens.z:
                    up_vec = Gf.Vec3d(0, 0, 1)
                plane = Gf.Plane(up_vec, self._world_orbit_center)
                cam_ray = Gf.Ray(camera_world_pos, camera_world_forward)
                intersect = cam_ray.Intersect(plane)
                if intersect[0]:
                    self._world_orbit_center = cam_ray.GetPoint(intersect[1])

        # Adjust the rotation so the camera looks at the orbit
        # Model's transform is set in the first super()._on_began so we call this once after changing the orbit center
        # No need to call later, all allowed camera control leads to proper transforms that look at the orbit center
        if self._center_dirty:
            self._center_dirty = False
            self._adjust_rotation()

        # set center_of_interest, it needs to be in camera-space
        view = Gf.Matrix4d(*self.model.get_as_floats('transform')).GetInverse()
        camera_orbit_center = view.Transform(self._world_orbit_center)
        self.model.set_floats(
            'center_of_interest',
            [camera_orbit_center[0], camera_orbit_center[1], camera_orbit_center[2]]
        )

    def destroy(self):
        self._center_dirty = False
        self._world_orbit_center = Gf.Vec3d(0, 0, 0)
        self._stage = None
        super().destroy()


class AnimatedOrbitViewportCameraManipulator(OrbitViewportCameraManipulator):
    def __init__(
        self,
        viewport_api,
        bindings: dict = None,
        world_orbit_center: Optional[Union[Gf.Vec3d, list]] = None,
        rotate_speed: float = 18.0,   # degrees per sec
        distance = 500,
        *args,
        **kwargs
    ):
        super().__init__(viewport_api, bindings, world_orbit_center, *args, **kwargs)

        self._rotate_speed = rotate_speed
        self._rotating = False
        self._app_stream = omni.kit.app.get_app().get_update_event_stream()
        self._app_sub = None
        self._rot_angle: float = 0.0
        self._distance = distance

    @property
    def rotate_speed(self) -> float:
        ''' Rotation speed in angle (degrees) per second
        '''
        return self._rotate_speed

    @rotate_speed.setter
    def rotate_speed(self, value: float):
        self._rotate_speed = value

    @property
    def rotating(self) -> bool:
        return self._rotating

    @rotating.setter
    def rotating(self, value: bool):
        '''
        Toggles orbiting animation on/off. Orbit starts from the diagonal view.
        '''
        if value != self._rotating:
            self._rotating = value
            if self._rotating:
                self._app_sub = self._app_stream.create_subscription_to_pop(self._rotate)
            else:
                self._app_sub = None

    @property
    def distance(self) -> float:
        '''
        Orbit distance
        '''
        return self._distance

    @distance.setter
    def distance(self, value: float):
        self._distance = value

    def set_rotation(self, angle_in_degrees: Optional[float] = None):
        '''
        Sets the rotation angle. Orbit starts from the diagonal view, angle_in_degrees == 0 is the diagonal view.

        Args:
            angle_in_degrees Optional[float]: the angle to set.
                If not specified, the current rotation angle is applied, which can be used to refresh the camera.
        '''
        if angle_in_degrees is not None:
            self._rot_angle = angle_in_degrees
        self.switch_view(self._viewside, self._distance)
        w_eye_pos = Gf.Matrix4d(*self.model.get_as_floats('transform')).ExtractTranslation()
        l_eye_pos = w_eye_pos - self._world_orbit_center  # to "local" space (with world rotation)
        w_up_axis = Gf.Vec3d(*self.model.get_as_floats('up_axis'))
        rotation = Gf.Rotation().SetAxisAngle(w_up_axis, self._rot_angle)
        rotation_mat = Gf.Matrix4d()
        rotation_mat.SetRotateOnly(rotation)
        l_eye_pos_rotated = rotation_mat.Transform(l_eye_pos)
        w_eye_pos_rotated = l_eye_pos_rotated + self._world_orbit_center  # back to world
        self._adjust_rotation(w_eye_pos_rotated)
        self.refresh()

    def set_distance(self, distance: float, world_orbit_center: Optional[Gf.Vec3d] = None):
        '''
        Sets the orbit distance and optionally the center of orbit by keeping the relative viewing direction.
        Also refreshes the camera.

        Args:
            distance (float): the orbit distance to set.
            world_orbit_center (Optional[Gf.Vec3d]): new orbit center in world space, or None to use the current one
        '''
        # original direction from center to eye, before changing the center
        w_eye_pos = Gf.Matrix4d(*self.model.get_as_floats('transform')).ExtractTranslation()
        w_neg_lookat_dir = (w_eye_pos - self._world_orbit_center).GetNormalized()

        self._distance = distance
        if world_orbit_center is not None:
            self._world_orbit_center = world_orbit_center

        w_eye_pos = self._world_orbit_center + self._distance * w_neg_lookat_dir
        self._adjust_rotation(w_eye_pos)
        self.model._item_changed(self.model.get_item('transform'))

    def _rotate(self, event: IEvent):
        dt = event.payload['dt']
        self._rot_angle += dt * self.rotate_speed
        if self._rot_angle > 360.0:  # avoid numerical errors when running long
            self._rot_angle = self._rot_angle - 360.0
        self.set_rotation()

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._rotating = False
        self._app_stream = None
        self._app_sub = None
