# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ViewportScene"]

import omni.ui as ui
from isaacsim.sensors.rtx.placement.scene_ui.camera_calibration_manipulator import (
    CameraCalibrationManipulator,
)
from isaacsim.sensors.rtx.placement.scene_ui.camera_info_model import CameraInfoModel
from omni.ui import scene as sc


class ViewportScene:
    """The Object Info Manipulator, placed into a Viewport"""

    def __init__(self, viewport_window: ui.Window, ext_id: str) -> None:
        self._scene_view = None
        self._viewport_window = viewport_window
        self._camera_manipulator = None
        self._model = None

        # Create a unique frame for our SceneView
        with self._viewport_window.get_frame(ext_id):
            # Create a default SceneView (it has a default camera-model)
            self._scene_view = sc.SceneView()
            # Add the manipulator into the SceneView's scene
            with self._scene_view.scene:
                self._model = CameraInfoModel()
                self._camera_manipulator = CameraCalibrationManipulator(model=self._model)

            # Register the SceneView with the Viewport to get projection and view updates
            self._viewport_window.viewport_api.add_scene_view(self._scene_view)

    def destroy(self):
        if self._scene_view:
            # Empty the SceneView of any elements it may have
            self._scene_view.scene.clear()
            # Be a good citizen, and un-register the SceneView from Viewport updates
            if self._viewport_window:
                self._viewport_window.viewport_api.remove_scene_view(self._scene_view)

        if self._model:
            self._model.destroy()
            self._model = None

        if self._camera_manipulator:
            self._camera_manipulator.destroy()
            self._camera_manipulator = None

        # Remove our references to these objects
        self._viewport_window = None
        self._scene_view = None
