# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['CameraManipulatorBase', 'adjust_center_of_interest']

from omni.ui import scene as sc
from .gestures import build_gestures
from .model import CameraManipulatorModel, _optional_bool, _flatten_matrix
from pxr import Gf


# Common math to adjust the center-of-interest
def adjust_center_of_interest(model: CameraManipulatorModel, initial_transform: Gf.Matrix4d, final_transform: Gf.Matrix4d):
    """
    Adjust the center-of-interest if requested.

    Args
        model (CameraManipulatorModel): Camera manipulator model.
        initial_transform (Gf.Matrix4d): The initial position of the camera.
        final_transform (Gf.Matrix4d): The final transform of the camera.

    Returns:
        Tuple[[Gf.Vec3d], [Gf.Vec3d]]: Start and end of center of interest.
    """
    # For object-centric movement we always adjust it if an object was hit
    object_centric = _optional_bool(model, 'object_centric_movement')
    coi_picked = model.get_as_floats('center_of_interest_picked') if object_centric else False
    adjust_center_of_interest = (object_centric and coi_picked) or _optional_bool(model, 'adjust_center_of_interest')
    if not adjust_center_of_interest:
        return None, None

    # When adjusting the center of interest we'll operate on a direction and length (in camera-space)
    # Which helps to not introduce -drift- as we jump through the different spaces to update it.
    # Final camera position
    world_cam_pos = final_transform.Transform(Gf.Vec3d(0, 0, 0))
    # center_of_interest_start is in camera-space
    center_of_interest_start = Gf.Vec3d(*model.get_as_floats('center_of_interest_start'))
    # Save the direction
    center_of_interest_dir = center_of_interest_start.GetNormalized()
    if coi_picked:
        # Keep original center-of-interest direction, but adjust its length to the picked position
        world_coi = Gf.Vec3d(coi_picked[0], coi_picked[1], coi_picked[2])
        # TODO: Setting to keep subsequent movement focused on screen-center or move it to the object.
        if False:
            # Save the center-of-interest to the hit-point by adjusting direction
            center_of_interest_dir = final_transform.GetInverse().Transform(world_coi).GetNormalized()
    else:
        # Move center-of-interest to world space at initial transform
        world_coi = initial_transform.Transform(center_of_interest_start)

    # Now get the length between final camera-position and the world-space-coi,
    # and apply that to the direction.
    center_of_interest_end = center_of_interest_dir * (world_cam_pos - world_coi).GetLength()
    return center_of_interest_start, center_of_interest_end


class CameraManipulatorBase(sc.Manipulator):
    """ Base class, resposible for building up the gestures. """
    def __init__(self, bindings: dict = None, model: sc.AbstractManipulatorModel = None, *args, **kwargs):
        """
        Constructor

        Args:
            bindings (dict): Set up the bindings for the manipulator.
            model (omni.ui.scene.AbstractManipulatorModel): Set the model of the manipulator.
        """
        super().__init__(*args, **kwargs)
        self._screen = None
        # Provide some defaults
        self.model = model or CameraManipulatorModel()
        self.bindings = bindings
        # Provide a slot for a user to fill in with a GestureManager but don't use anything by default
        self.manager = None
        self.gestures = []
        self.__transform = None
        self.__gamepad = None

    def _on_began(self, model: CameraManipulatorModel, *args, **kwargs):
        pass

    def on_build(self):
        # Need to hold a reference to this or the sc.Screen would be destroyed when out of scope
        """ Called when the manipulator is build. """
        self.__transform = sc.Transform()
        with self.__transform:
            self._screen = sc.Screen(gestures=self.gestures or build_gestures(self.model, self.bindings, self.manager, self._on_began))

    def destroy(self):
        """Destroys the manipulator instance."""
        if self.__gamepad:
            self.__gamepad.destroy()
            self.__gamepad = None
        if self.__transform:
            self.__transform.clear()
            self.__transform = None
        self._screen = None
        if hasattr(self.model, 'destroy'):
            self.model.destroy()

    @property
    def gamepad_enabled(self) -> bool:
        """
        Get whether or not the gamepad is enabled.

        Returns:
            bool
        """
        return self.__gamepad is not None

    @gamepad_enabled.setter
    def gamepad_enabled(self, value: bool):
        """
        Enable or disable the gamepad controller.

        Args:
            value (bool): Set whether or not the gamepad is enabled.
        """
        if value:
            if not self.__gamepad:
                from .gamepad import GamePadController
                self.__gamepad = GamePadController(self)
        elif self.__gamepad:
            self.__gamepad.destroy()
            self.__gamepad = None


# We have all the imoorts already, so provide a simple omni.ui.scene camera manipulator that one can use.
# Takes an omni.ui.scene view and center-of-interest and applies model changes to that view
class SceneViewCameraManipulator(CameraManipulatorBase):
    """A simple camera manipulator for controlling the camera's center of interest to omni.ui.scene view."""
    def __init__(self, center_of_interest, *args, **kwargs):
        """
        Constructor.

        Args:
            center_of_interest (Gf.Vec3d): Set the center of interest for the camera
        """
        super().__init__(*args, **kwargs)
        self.__center_of_interest = center_of_interest

    def _on_began(self, model: CameraManipulatorModel, mouse):
        model.set_floats('center_of_interest', [self.__center_of_interest[0], self.__center_of_interest[1], self.__center_of_interest[2]])
        if _optional_bool(model, 'orthographic'):
            model.set_ints('disable_tumble', [1])
            model.set_ints('disable_look', [1])

    def on_model_updated(self, item):
        """
        Called whenever the model changes.

        Args:
            item (omni.ui.scene.AbstractManipulatorItem): Identify which item in the model has changed.
        """
        model = self.model
        if item == model.get_item('transform'):
            final_transform = Gf.Matrix4d(*model.get_as_floats(item))
            initial_transform = Gf.Matrix4d(*model.get_as_floats('initial_transform'))
            # Adjust our center-of-interest
            coi_start, coi_end = adjust_center_of_interest(model, initial_transform, final_transform)
            if coi_end:
                self.__center_of_interest = coi_end

            # omni.ui.scene.SceneView.CameraModel expects 'view', but we operate on 'transform'
            # The following will push our transform changes into the SceneView.model.view
            sv_model = self.scene_view.model
            view = sv_model.get_item('view')
            sv_model.set_floats(view, _flatten_matrix(final_transform.GetInverse()))
            sv_model._item_changed(view)
