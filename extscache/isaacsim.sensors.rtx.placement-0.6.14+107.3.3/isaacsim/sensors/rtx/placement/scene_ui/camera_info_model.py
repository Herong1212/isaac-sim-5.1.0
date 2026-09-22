# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["CameraInfoModel"]

import carb
import omni.usd
from isaacsim.sensors.rtx.placement.camera_calibration.camera_info import CameraInfoManager
from omni.ui import scene as sc
from pxr import Tf, Usd

from ..settings import CameraCalibrationSettings

# The distance to raise above the top of the object's bounding box
TOP_OFFSET = 5


class CameraInfoModel(sc.AbstractManipulatorModel):
    """
    The model tracks the position and info of the selected object.
    """

    def __init__(self):
        super().__init__()
        self._selected_camera_path_list = []
        # listen to the selection change and camera info update
        self.camera_info_manager = CameraInfoManager.get_instance()
        usd_context = self._get_context()
        self._camera_info_updated_event_name = f"{CameraCalibrationSettings.Camera_Info_Updated_Event}:immediate"

        self._selection_change_event_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            observer_name="isaacsim/sensors/rtx/placement/sensor_selection_change_event",
            event_name= str(usd_context.stage_event_name(omni.usd.StageEventType.SELECTION_CHANGED)),
            on_event = self._on_kit_selection_changed)

        self._sensor_info_update_event_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            observer_name="isaacsim/sensors/rtx/placement/sensor_info_update_event",
            event_name= self._camera_info_updated_event_name,
            on_event = self._on_camera_update)

    def _get_context(self) -> Usd.Stage:
        """Get the UsdContext we are attached to"""
        return omni.usd.get_context()

    def _on_camera_update(self, event):
        # if camera info get changed, update the camera fov directly
        carb.log_info("Sensor info updated")
        self._item_changed(None)

    def clean_event_attributes(self):
        """clean all event related attributes"""
        self._selection_change_event_sub = None
        self._camera_info_updated_event = None

    def clean_camera_data(self):
        """clean current selected camera info"""
        self._selected_camera_path_list = []

    # when selected camera has changed refresh the scene ui
    def _on_kit_selection_changed(self, event):
        """Called when a selection has changed."""
        self._selected_camera_path_list = []
        usd_context = self._get_context()
        stage = usd_context.get_stage()
        if not stage:
            # not a valid stage, return
            return
        prim_paths = usd_context.get_selection().get_selected_prim_paths()
        if not prim_paths:
            self._item_changed(None)
            return

        # record current selected camera list
        for path in prim_paths:
            if str(path) in self.camera_info_manager.get_stored_camera_list():
                self._selected_camera_path_list.append(path)
        carb.log_info("Selected sensor changed")
        self._item_changed(None)

    def destroy(self):
        self.clean_camera_data()
        self.clean_event_attributes()
