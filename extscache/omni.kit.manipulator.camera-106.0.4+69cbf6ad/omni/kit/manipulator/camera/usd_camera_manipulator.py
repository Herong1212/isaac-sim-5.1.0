# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from .manipulator import CameraManipulatorBase, adjust_center_of_interest
from .model import _optional_bool, _flatten_matrix
from omni.kit import commands, undo
import omni.usd
from pxr import Usd, UsdGeom, Sdf, Tf, Gf
import carb.profiler
import carb.settings
import math
from typing import List


__all__ = ['UsdCameraManipulator']

KIT_COI_ATTRIBUTE = 'omni:kit:centerOfInterest'
KIT_LOOKTHROUGH_ATTRIBUTE = 'omni:kit:viewport:lookThrough:target'
KIT_CAMERA_LOCK_ATTRIBUTE = 'omni:kit:cameraLock'


def _get_context_stage(usd_context_name: str):
    return omni.usd.get_context(usd_context_name).get_stage()

def _compute_local_transform(imageable: UsdGeom.Imageable, time: Usd.TimeCode):
    # xformable = UsdGeom.Xformable(imageable)
    # if xformable:
    #     return xformable.GetLocalTransformation(time)

    world_xform = imageable.ComputeLocalToWorldTransform(time)
    parent_xform = imageable.ComputeParentToWorldTransform(time)
    parent_ixform = parent_xform.GetInverse()
    return (world_xform * parent_ixform), parent_ixform

class SRTDecomposer:
    def __init__(self, prim: Usd.Prim, time: Usd.TimeCode = None):
        if time is None:
            time = Usd.TimeCode.Default()

        xform_srt = omni.usd.get_local_transform_SRT(prim, time)
        xform_srt = (Gf.Vec3d(xform_srt[0]), Gf.Vec3d(xform_srt[1]), Gf.Vec3i(xform_srt[2]), Gf.Vec3d(xform_srt[3]))
        self.__start_scale, self.__start_rotation_euler, self.__start_rotation_order, self.__start_translation = xform_srt
        self.__current_scale, self.__current_rotation_euler, self.__current_rotation_order, self.__current_translation = xform_srt

    @staticmethod
    def __repeat(t: float, length: float) -> float:
        return t - (math.floor(t / length) * length)

    @staticmethod
    def __generate_compatible_euler_angles(euler: Gf.Vec3d, rotation_order: Gf.Vec3i) -> List[Gf.Vec3d]:
        equal_eulers = [euler]

        mid_order = rotation_order[1]

        equal = Gf.Vec3d()
        for i in range(3):
            if i == mid_order:
                equal[i] = 180 - euler[i]
            else:
                equal[i] = euler[i] + 180

        equal_eulers.append(equal)

        for i in range(3):
            equal[i] -= 360

        equal_eulers.append(equal)

        return equal_eulers

    @staticmethod
    def __find_best_euler_angles(old_rot_vec: Gf.Vec3d, new_rot_vec: Gf.Vec3d, rotation_order: Gf.Vec3i) -> Gf.Vec3d:
        equal_eulers = SRTDecomposer.__generate_compatible_euler_angles(new_rot_vec, rotation_order)
        nearest_euler = None

        for euler in equal_eulers:
            for i in range(3):
                euler[i] = SRTDecomposer.__repeat(euler[i] - old_rot_vec[i] + 180.0, 360.0) + old_rot_vec[i] - 180.0

            if nearest_euler is None:
                nearest_euler = euler
            else:
                distance_1 = (nearest_euler - old_rot_vec).GetLength()
                distance_2 = (euler - old_rot_vec).GetLength()

                if distance_2 < distance_1:
                    nearest_euler = euler

        return nearest_euler

    def update(self, xform: Gf.Matrix4d):
        # Extract new translation
        self.__current_translation = xform.ExtractTranslation()

        # Extract new euler rotation
        ro = self.__start_rotation_order
        old_s_mtx = Gf.Matrix4d().SetScale(self.__start_scale)
        old_t_mtx = Gf.Matrix4d().SetTranslate(self.__start_translation)
        rot_new = (old_s_mtx.GetInverse() * xform * old_t_mtx.GetInverse()).ExtractRotation()

        axes = [Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis()]
        decomp_rot = rot_new.Decompose(axes[ro[2]], axes[ro[1]], axes[ro[0]])
        index_order = Gf.Vec3i()
        for i in range(3):
            index_order[ro[i]] = 2 - i

        new_rot_vec = Gf.Vec3d(decomp_rot[index_order[0]], decomp_rot[index_order[1]], decomp_rot[index_order[2]])
        new_rot_vec = self.__find_best_euler_angles(self.__start_rotation_euler, new_rot_vec, self.__start_rotation_order)
        self.__current_rotation_euler = new_rot_vec

        # Because this is a camera manipulation, we purposefully ignore scale and rotation order changes
        # They remain constant across the interaction.

        return self

    @property
    def translation(self):
        return self.__current_translation

    @property
    def rotation(self):
        return self.__current_rotation_euler

    @property
    def start_translation(self):
        return self.__start_translation

    @property
    def start_rotation(self):
        self.__start_rotation_euler


class ExternalUsdCameraChange():
    def __init__(self, time: Usd.TimeCode):
        self.__tf_listener = None
        self.__usd_context_name, self.__prim_path = None, None
        self.__updates_paused = False
        self.__kill_external_animation = None
        self.__time = time

    def __del__(self):
        self.destroy()

    def update(self, model, usd_context_name: str, prim_path: Sdf.Path):
        self.__kill_external_animation = getattr(model, '_kill_external_animation', None)
        if self.__kill_external_animation is None:
            return

        self.__prim_path = prim_path
        if usd_context_name != self.__usd_context_name:
            self.__usd_context_name = usd_context_name
            if self.__tf_listener:
                self.__tf_listener.Revoke()
                self.__tf_listener = None

        if not self.__tf_listener:
            try:
                stage = _get_context_stage(self.__usd_context_name)
                if stage:
                    self.__tf_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self.__object_changed, stage)
            except ImportError:
                pass

    def destroy(self):
        if self.__tf_listener:
            self.__tf_listener.Revoke()
            self.__tf_listener = None
        self.__usd_context_name, self.__prim_path = None, None
        self.__kill_external_animation = None

    @carb.profiler.profile
    def __object_changed(self, notice, sender):
        if self.__updates_paused:
            return
        if not sender or sender != _get_context_stage(self.__usd_context_name):
            return

        for p in notice.GetChangedInfoOnlyPaths():
            if (p.IsPropertyPath()
                and p.GetPrimPath() == self.__prim_path
                and UsdGeom.Xformable.IsTransformationAffectedByAttrNamed(p.name)):
                xformable = UsdGeom.Xformable(sender.GetPrimAtPath(self.__prim_path))
                xform = _flatten_matrix(xformable.GetLocalTransformation(self.__time)) if xformable else None
                self.__kill_external_animation(True, xform)
                break

    def pause_tracking(self):
        self.__updates_paused = True

    def start_tracking(self):
        self.__updates_paused = False


class UsdCameraManipulator(CameraManipulatorBase):
    """Base Usd camera manipulator implementation that will set model's value back to Usd data via kit-commands."""
    def __init__(self, bindings: dict = None, usd_context_name: str = '', prim_path: Sdf.Path = None, *args, **kwargs):
        """
        Constructor.

        Args:
            bindings (dict): Set the bindings for the class.
            usd_context_name (str): Set the name of the usd context.
            prim_path (Sdf.Path): Set the camera prim path.
        """
        self.__usd_context_name, self.__prim_path = None, None
        self.__external_change_tracker = None
        super().__init__(bindings, *args, **kwargs)
        self._set_context(usd_context_name, prim_path)

    def _set_context(self, usd_context_name: str, prim_path: Sdf.Path):
        self.__usd_context_name = usd_context_name
        self.__prim_path = prim_path
        self.__srt_decompose = None
        if prim_path and carb.settings.get_settings().get('/persistent/app/camera/controllerUseSRT'):
            stage = _get_context_stage(self.__usd_context_name)
            if stage:
                prim = stage.GetPrimAtPath(prim_path)
                if prim:
                    model = self.model
                    time = model.get_as_floats('time') if model else None
                    time = Usd.TimeCode(time[0]) if time else Usd.TimeCode.Default()
                    self.__srt_decompose = SRTDecomposer(prim)

    def _on_began(self, model, *args, **kwargs):
        super()._on_began(model, *args, **kwargs)
        stage = _get_context_stage(self.__usd_context_name)
        if not stage:
            # TODO: Could we forward this to adjust the viewport_api->omni.scene.ui ?
            model.set_ints('disable_tumble', [1])
            model.set_ints('disable_look', [1])
            model.set_ints('disable_pan', [1])
            model.set_ints('disable_zoom', [1])
            model.set_ints('disable_fly', [1])
            return

        cam_prim = stage.GetPrimAtPath(self.__prim_path)
        cam_imageable = UsdGeom.Imageable(cam_prim) if bool(cam_prim) else None

        if not cam_imageable or not cam_imageable.GetPrim().IsValid():
            raise RuntimeError('ViewportCameraManipulator with an invalid UsdGeom.Imageable or Usd.Prim')

        # Check if we should actaully keep camera at identity and forward our movements to another object
        local_xform, parent_xform = _compute_local_transform(cam_imageable, Usd.TimeCode.Default())

        model.set_floats('initial_transform', _flatten_matrix(local_xform))
        model.set_floats('transform', _flatten_matrix(local_xform))

        up_axis = UsdGeom.GetStageUpAxis(stage)
        if up_axis == UsdGeom.Tokens.x:
            up_axis = Gf.Vec3d(1, 0, 0)
        elif up_axis == UsdGeom.Tokens.y:
            up_axis = Gf.Vec3d(0, 1, 0)
        elif up_axis == UsdGeom.Tokens.z:
            up_axis = Gf.Vec3d(0, 0, 1)

        if not bool(carb.settings.get_settings().get("exts/omni.kit.manipulator.camera/forceStageUp")):
            up_axis = parent_xform.TransformDir(up_axis).GetNormalized()
        model.set_floats('up_axis', [up_axis[0], up_axis[1], up_axis[2]])

    @carb.profiler.profile
    def __vp1_cooperation(self, prim_path, time, usd_context_name: str, center_of_interest_end):
        try:
            from omni.kit import viewport_legacy
            vp1_iface = viewport_legacy.get_viewport_interface()
            final_transform, coi_world, pos_world, cam_path = None, None, None, None
            for vp1_handle in vp1_iface.get_instance_list():
                vp1_window = vp1_iface.get_viewport_window(vp1_handle)
                if not vp1_window or (vp1_window.get_usd_context_name() != usd_context_name):
                    continue
                if not final_transform:
                    # Save the path's string represnetation
                    cam_path = prim_path.pathString
                    # We need to calculate world-space transform for VP-1, important for nested camera's
                    # TODO: UsdBBoxCache.ComputeWorldBound in compute_path_world_transform doesn't seem to work for non-geometry:
                    # final_transform = omni.usd.get_context(usd_context_name).compute_path_world_transform(cam_path)
                    # final_transform = Gf.Matrix4d(*final_transform)
                    final_transform = UsdGeom.Imageable(prim_path).ComputeLocalToWorldTransform(time)
                    # center_of_interest_end is adjusted and returned for VP-2
                    center_of_interest_end = Gf.Vec3d(0, 0, -center_of_interest_end.GetLength())
                    # Pass world center-of-interest to VP-1 set_camera_target
                    coi_world = final_transform.Transform(center_of_interest_end)
                    # Pass world position to VP-1 set_camera_position
                    pos_world = final_transform.Transform(Gf.Vec3d(0, 0, 0))
                    # False for first call to set target only, True for second to trigger radius re-calculation
                    # This isn't particuarly efficient; but 'has to be' for now due to some Viewport-1 internals
                vp1_window.set_camera_target(cam_path, coi_world[0], coi_world[1], coi_world[2], False)
                vp1_window.set_camera_position(cam_path, pos_world[0], pos_world[1], pos_world[2], True)
        except Exception:
            pass

        return center_of_interest_end

    @carb.profiler.profile
    def on_model_updated(self, item):
        """
        Called whenever the model changes.

        Args:
            item (omni.ui.scene.AbstractManipulatorItem): Identify which item in the model has changed.
        """
        # Handle case of inertia being applied though a new stage-open
        usd_context_name = self.__usd_context_name
        if usd_context_name is None or _get_context_stage(usd_context_name) is None:
            return

        model = self.model
        prim_path = self.__prim_path
        time = model.get_as_floats('time')
        time = Usd.TimeCode(time[0]) if time else Usd.TimeCode.Default()
        undoable = False


        def run_command(cmd_name, **kwargs):
            carb.profiler.begin(1, cmd_name)
            if undoable:
                commands.execute(cmd_name, **kwargs)
            else:
                commands.create(cmd_name, **kwargs).do()
            carb.profiler.end(1)

        try:
            if item == model.get_item('transform'):
                if self.__external_change_tracker:
                    self.__external_change_tracker.update(model, usd_context_name, prim_path)
                    self.__external_change_tracker.pause_tracking()

                # We are undoable on the final event if undo hasn't been disabled on the model
                undoable = _optional_bool(self.model, 'interaction_ended') and not _optional_bool(self.model, 'disable_undo')
                if undoable:
                    undo.begin_group()

                final_transform = Gf.Matrix4d(*model.get_as_floats('transform'))
                initial_transform = model.get_as_floats('initial_transform')
                initial_transform = Gf.Matrix4d(*initial_transform) if initial_transform else initial_transform
                had_transform_at_key = _optional_bool(self.model, 'had_transform_at_key')

                if self.__srt_decompose:
                    srt_deompose = self.__srt_decompose.update(final_transform)
                    run_command(
                        'TransformPrimSRTCommand',
                        path=prim_path,
                        new_translation=srt_deompose.translation,
                        new_rotation_euler=srt_deompose.rotation,
                        # new_scale=srt_deompose.scale,
                        # new_rotation_order=srt_deompose.rotation_order,
                        old_translation=srt_deompose.start_translation,
                        old_rotation_euler=srt_deompose.start_rotation,
                        # old_rotation_order=srt_deompose.start_rotation_order,
                        # old_scale=srt_deompose.start_scale,
                        time_code=time,
                        had_transform_at_key=had_transform_at_key,
                        usd_context_name=usd_context_name
                    )
                else:
                    run_command(
                        'TransformPrimCommand',
                        path=prim_path,
                        new_transform_matrix=final_transform,
                        old_transform_matrix=initial_transform,
                        time_code=time,
                        had_transform_at_key=had_transform_at_key,
                        usd_context_name=usd_context_name
                    )

                center_of_interest_start, center_of_interest_end = adjust_center_of_interest(model, initial_transform, final_transform)
                if center_of_interest_start and center_of_interest_end:
                    # See if we need to adjust center-of-interest to cooperate with Viewport-1, which can only do a 1 dimensional version
                    center_of_interest_end = self.__vp1_cooperation(prim_path, time, usd_context_name, center_of_interest_end)
                    run_command(
                        'ChangePropertyCommand',
                        prop_path=prim_path.AppendProperty(KIT_COI_ATTRIBUTE),
                        value=center_of_interest_end,
                        prev=center_of_interest_start,
                        usd_context_name=usd_context_name
                    )

            elif item == model.get_item('current_aperture'):
                # We are undoable on the final event if undo hasn't been disabled on the model
                undoable = _optional_bool(self.model, 'interaction_ended') and not _optional_bool(self.model, 'disable_undo')
                if undoable:
                    undo.begin_group()

                initial_aperture = model.get_as_floats('initial_aperture')
                current_aperture = model.get_as_floats('current_aperture')
                prop_names = ('horizontalAperture', 'verticalAperture')
                for initial_value, current_value, prop_name in zip(initial_aperture, current_aperture, prop_names):
                    run_command(
                        'ChangePropertyCommand',
                        prop_path=prim_path.AppendProperty(prop_name),
                        value=current_value,
                        prev=initial_value,
                        timecode=time,
                        usd_context_name=usd_context_name
                    )

            elif item == model.get_item('interaction_animating'):
                interaction_animating = model.get_as_ints(item)
                if interaction_animating and interaction_animating[0]:
                    if not self.__external_change_tracker:
                        self.__external_change_tracker = ExternalUsdCameraChange(time)
                    self.__external_change_tracker.update(model, usd_context_name, prim_path)
                    self.__external_change_tracker.pause_tracking()
                elif self.__external_change_tracker:
                    self.__external_change_tracker.destroy()
                    self.__external_change_tracker = None

        finally:
            if undoable:
                undo.end_group()
            if self.__external_change_tracker:
                self.__external_change_tracker.start_tracking()
