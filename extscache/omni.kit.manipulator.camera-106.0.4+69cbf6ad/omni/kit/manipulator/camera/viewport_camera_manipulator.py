# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from .model import CameraManipulatorModel, _flatten_matrix, _optional_bool, _optional_int
from .usd_camera_manipulator import (
        UsdCameraManipulator,
        KIT_COI_ATTRIBUTE,
        KIT_LOOKTHROUGH_ATTRIBUTE,
        KIT_CAMERA_LOCK_ATTRIBUTE,
        _compute_local_transform
)

from omni.ui import scene as sc
from pxr import Usd, UsdGeom, Sdf, Gf
import carb
import math

__all__ = ['ViewportCameraManipulator']


# More advanced implementation for a Viewport that can use picked objects and -look through- arbitrary scene items
#
def _check_for_camera_forwarding(imageable: UsdGeom.Imageable):
    # Look for the relationship setup via LookAtCommand
    prim = imageable.GetPrim()
    look_through = prim.GetRelationship(KIT_LOOKTHROUGH_ATTRIBUTE).GetForwardedTargets()
    if look_through:
        stage = prim.GetStage()
        # Loop over all targets (should really be only one) and see if we can get a valid UsdGeom.Imageable
        for target in look_through:
            target_prim = stage.GetPrimAtPath(target)
            if not target_prim:
                continue
            target_imageable = UsdGeom.Imageable(target_prim)
            if target_imageable:
                return target_imageable
        carb.log_warn(f'{prim.GetPath()} was set up for look-thorugh, but no valid prim was found for targets: {look_through}')

    return imageable


def _setup_center_of_interest(model: sc.AbstractManipulatorModel, prim: Usd.Prim, time: Usd.TimeCode,
                              object_centric: int = 0, viewport_api=None, mouse=None):
    def get_center_of_interest():
        coi_attr = prim.GetAttribute(KIT_COI_ATTRIBUTE)
        if not coi_attr or not coi_attr.IsAuthored():
            # Use UsdGeomCamera.focusDistance is present
            distance = 0
            fcs_dist = prim.GetAttribute('focusDistance')
            if fcs_dist and fcs_dist.IsAuthored():
                distance = fcs_dist.Get(time)
            # distance 0 is invalid, so create the atribute based on length from origin
            if not fcs_dist or distance == 0:
                origin = Gf.Matrix4d(*model.get_as_floats('initial_transform')).Transform((0, 0, 0))
                distance = origin.GetLength()

            coi_attr = prim.CreateAttribute(KIT_COI_ATTRIBUTE, Sdf.ValueTypeNames.Vector3d, True, Sdf.VariabilityUniform)
            coi_attr.Set(Gf.Vec3d(0, 0, -distance))

        # Make sure COI isn't ridiculously low
        coi_val = coi_attr.Get()
        length = coi_val.GetLength()
        if length < 0.000001 or not math.isfinite(length):
            coi_val = Gf.Vec3d(0, 0, -100)
        return coi_val

    def query_completed(path, pos, *args):
        # Reset center-of-interest if there's an obect and world-space position
        if path and pos:
            # Convert carb value to Gf.Vec3d
            pos = Gf.Vec3d(pos.x, pos.y, pos.z)

            # Object centric 1 will use the object-center, so replace pos with the UsdGeom.Imageable's (0, 0, 0) coord
            if object_centric == 1:
                picked_prim = prim.GetStage().GetPrimAtPath(path)
                imageable = UsdGeom.Imageable(picked_prim) if picked_prim else None
                if imageable:
                    pos = imageable.ComputeLocalToWorldTransform(time).Transform(Gf.Vec3d(0, 0, 0))

            if math.isfinite(pos[0]) and math.isfinite(pos[1]) and math.isfinite(pos[2]):
                inv_xform = Gf.Matrix4d(*model.get_as_floats('transform')).GetInverse()
                coi = inv_xform.Transform(pos)
                model.set_floats('center_of_interest_picked', [pos[0], pos[1], pos[2]])
                # Also need to trigger a recomputation of ndc_speed based on our new center of interest
                coi_item = model.get_item('center_of_interest')
                model.set_floats(coi_item, [coi[0], coi[1], coi[2]])
                model._item_changed(coi_item)

        # Re-enable all movement that we previouly disabled
        model.set_ints('disable_pan', [disable_pan])
        model.set_ints('disable_tumble', [disable_tumble])
        model.set_ints('disable_look', [disable_look])
        model.set_ints('disable_zoom', [disable_zoom])

    coi = get_center_of_interest()
    model.set_floats('center_of_interest', [coi[0], coi[1], coi[2]])

    if object_centric != 0:
        # Map the NDC co-ordinates to a viewport's texture-space
        mouse, viewport_api = viewport_api.map_ndc_to_texture_pixel(mouse)
        if (mouse is None) or (viewport_api is None):
            object_centric = 0

    if object_centric == 0:
        model.set_floats('center_of_interest_picked', [])
        return

    # Block all movement until the query completes
    disable_pan = _optional_bool(model, 'disable_pan')
    disable_tumble = _optional_bool(model, 'disable_tumble')
    disable_look = _optional_bool(model, 'disable_look')
    disable_zoom = _optional_bool(model, 'disable_zoom')
    model.set_ints('disable_pan', [1])
    model.set_ints('disable_tumble', [1])
    model.set_ints('disable_look', [1])
    model.set_ints('disable_zoom', [1])
    # Start the query
    viewport_api.request_query(mouse, query_completed)


class ViewportCameraManipulator(UsdCameraManipulator):
    def __init__(self, viewport_api, bindings: dict = None, *args, **kwargs):
        """
        Constructor.

        Args:
            viewport_api (:obj:'ViewportAPI'): The viewport's api interface class.
            bindings (dict): Dictionary that maps a gesture name to a button name..
        """
        super().__init__(bindings, viewport_api.usd_context_name)
        self.__viewport_api = viewport_api

        # def view_changed(*args):
        #     return
        #     from .gesturebase import set_frame_delivered
        #     set_frame_delivered(True)
        # self.__vc_change = viewport_api.subscribe_to_frame_change(view_changed)

    def _on_began(self, model: CameraManipulatorModel, mouse):
        # We need a viewport and a stage to start.  If either are missing disable any further processing.
        viewport_api = self.__viewport_api
        stage = viewport_api.stage if viewport_api else None
        settings = carb.settings.get_settings()

        # Store the viewport_id in the model for use later if necessary
        model.set_ints('viewport_id', [viewport_api.id if viewport_api else 0])
        if not stage:
            # TODO: Could we forward this to adjust the viewport_api->omni.scene.ui ?
            model.set_ints('disable_tumble', [1])
            model.set_ints('disable_look', [1])
            model.set_ints('disable_pan', [1])
            model.set_ints('disable_zoom', [1])
            model.set_ints('disable_fly', [1])
            return

        cam_path = viewport_api.camera_path
        if hasattr(model, '_set_animation_key'):
            model._set_animation_key(cam_path)

        time = viewport_api.time
        cam_prim = stage.GetPrimAtPath(cam_path)
        cam_imageable = UsdGeom.Imageable(cam_prim)
        camera = UsdGeom.Camera(cam_prim) if cam_imageable else None

        if not cam_imageable or not cam_imageable.GetPrim().IsValid():
            raise RuntimeError('ViewportCameraManipulator with an invalid UsdGeom.Imageable or Usd.Prim')

        # Push the viewport's projection into the model
        projection = _flatten_matrix(viewport_api.projection)
        model.set_floats('projection', projection)

        # Check if we should actaully keep camera at identity and forward our movements to another object
        target_imageable = _check_for_camera_forwarding(cam_imageable)
        local_xform, parent_xform = _compute_local_transform(target_imageable, time)

        model.set_floats('initial_transform', _flatten_matrix(local_xform))
        model.set_floats('transform', _flatten_matrix(local_xform))

        # Setup the model if the camera is orthographic (where for Usd we must edit apertures)
        # We do this before center-of-interest query to get disabled-state pushed into the model
        if camera:
            orthographic = int(camera.GetProjectionAttr().Get(time) == 'orthographic')
            if orthographic:
                model.set_floats('initial_aperture', [camera.GetHorizontalApertureAttr().Get(time),
                                                      camera.GetVerticalApertureAttr().Get(time)])
        else:
            orthographic = int(projection[15] == 1 if projection else False)
            model.set_floats('initial_aperture', [])

        # It is unclear whether USD spec requires case sensitive Y, Z only as up.
        # For now do a case-insensitive compare to support [Z|z], [X,x] with fallback to default-Y
        up_axis = UsdGeom.GetStageUpAxis(stage).upper()
        if up_axis == UsdGeom.Tokens.z:
            up_axis = Gf.Vec3d(0, 0, 1)
        elif up_axis == UsdGeom.Tokens.x:
            up_axis = Gf.Vec3d(1, 0, 0)
        else:
            up_axis = Gf.Vec3d(0, 1, 0)

        if not bool(settings.get("exts/omni.kit.manipulator.camera/forceStageUp")):
            up_axis = parent_xform.TransformDir(up_axis).GetNormalized()
        model.set_floats('up_axis', [up_axis[0], up_axis[1], up_axis[2]])

        # Disable undo for implict cameras.  This might be better handled with custom meta-data / attribute long term
        disable_undo = cam_path.pathString in ['/OmniverseKit_Persp', '/OmniverseKit_Front', '/OmniverseKit_Right', '/OmniverseKit_Top']
        model.set_ints('disable_undo', [int(disable_undo)])

        # Test whether this camera is locked
        cam_lock = cam_prim.GetAttribute(KIT_CAMERA_LOCK_ATTRIBUTE)
        if cam_lock and cam_lock.Get():
            model.set_ints('disable_tumble', [1])
            model.set_ints('disable_look', [1])
            model.set_ints('disable_pan', [1])
            model.set_ints('disable_zoom', [1])
            model.set_ints('disable_fly', [1])
        else:
            model.set_ints('orthographic', [orthographic])
            model.set_ints('disable_tumble', [orthographic])
            model.set_ints('disable_look', [orthographic])
            model.set_ints('disable_pan', [0])
            model.set_ints('disable_zoom', [0])
            model.set_ints('disable_fly', [0])

            # Extract the camera's center of interest, from a property or world-space query
            # model.set_ints('object_centric_movement', [1])
            object_centric = settings.get('/exts/omni.kit.manipulator.camera/objectCentric/type') or 0
            object_centric = _optional_int(self.model, 'object_centric_movement', object_centric)
            _setup_center_of_interest(model, target_imageable.GetPrim(), time, object_centric, viewport_api, mouse)

            # Setup the model for command execution on key-framed data
            had_transform_at_key = False
            if not time.IsDefault():
                xformable = UsdGeom.Xformable(target_imageable)
                if xformable:
                    for xformOp in xformable.GetOrderedXformOps():
                        had_transform_at_key = time in xformOp.GetTimeSamples()
                        if had_transform_at_key:
                            break
            model.set_ints('had_transform_at_key', [had_transform_at_key])

            # Set the pan/zoom speed equivalent to the world space travel of the mouse
            model.set_floats('world_speed', [1, 1, 1])
            # Make a full drag across the viewport equal to a 180 tumble
            uv_space = viewport_api.map_ndc_to_texture((1, 1))[0]
            model.set_floats('rotation_speed', [((v * 2.0) - 1.0) for v in uv_space] + [1])

        # Tell the USD manipulator the context and prim to operate on
        self._set_context(viewport_api.usd_context_name, target_imageable.GetPath())

    def destroy(self):
        """ Destroys the manipulator instance. """
        self.__vc_change = None
        self.__viewport_api = None
        super().destroy()


import omni.kit.app
import time

class ZoomEvents:
    __instances = set()

    @staticmethod
    def get_instance(viewport_api):
        instance = None
        for inst in ZoomEvents.__instances:
            if inst.__viewport_api == viewport_api:
                instance = inst
                break

        if instance is None:
            instance = ZoomEvents(viewport_api)
            ZoomEvents.__instances.add(instance)
        else:
            instance.__mark_time()
        return instance

    def __init__(self, viewport_api):
        self.__viewport_api = viewport_api
        self.__mouse = [0, 0]
        self.__manipulator = ViewportCameraManipulator(viewport_api, bindings={'ZoomGesture': 'LeftButton'})
        self.__manipulator.on_build()
        self.__zoom_gesture = self.__manipulator._screen.gestures[0]
        self.__zoom_gesture._disable_flight()
        self.__zoom_gesture.on_began(self.__mouse)

        # 1030
        if hasattr(omni.kit.app, 'UPDATE_ORDER_PYTHON_ASYNC_FUTURE_END_UPDATE'):
            update_order = omni.kit.app.UPDATE_ORDER_PYTHON_ASYNC_FUTURE_END_UPDATE
        else:
            update_order = 50
        from carb.eventdispatcher import get_eventdispatcher
        self.__event_sub = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self.__on_event,
            observer_name="omni.kit.manipulator.camera.ZoomEvents",
            order=update_order
        )

    def update(self, x, y):
        self.__mark_time()
        coi = Gf.Vec3d(*self.__manipulator.model.get_as_floats('center_of_interest'))
        scale = math.log10(max(10, coi.GetLength())) / 40
        self.__mouse = (self.__mouse[0] + x * scale, self.__mouse[1] + y * scale)
        self.__zoom_gesture.on_changed(self.__mouse)
        self.__mark_time()

    def __mark_time(self):
        self.__last_time = time.monotonic()

    def __time_since_last(self):
        return time.monotonic() - self.__last_time

    def __on_event(self, _):
        delta = self.__time_since_last()
        if delta > 0.1:
            self.destroy()

    def destroy(self):
        self.__event_sub = None
        self.__zoom_gesture.on_ended()
        self.__manipulator.destroy()
        try:
            ZoomEvents.__instances.remove(self)
        except KeyError:
            pass


# Helper function to do single a zoom-operation, from a scroll-wheel for example
def _zoom_operation(x, y, viewport_api):
    if not viewport_api:
        return None
    instance = ZoomEvents.get_instance(viewport_api)
    instance.update(x, y)
    return True
