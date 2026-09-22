# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

__all__ = ["CameraCalibrationManipulator"]

from typing import Any

import carb
from isaacsim.sensors.rtx.placement.camera_calibration.camera_info import CameraInfoManager
from omni.syntheticdata.scripts.helpers import *
from omni.ui import color as cl
from omni.ui import scene as sc

from ..settings import CameraCalibrationSettings
from .camera_info_model import CameraInfoModel

LEADER_LINE_CIRCLE_RADIUS = 2
LEADER_LINE_THICKNESS = 2
LEADER_LINE_SEGMENT_LENGTH = 20
VERTICAL_MULT = 1.5
HORIZ_TEXT_OFFSET = 5
LINE1_OFFSET = 3
LINE2_OFFSET = 0


class CameraCalibrationManipulator(sc.Manipulator):
    """Manipulator that displays the object path and material assignment
    with a leader line to the top of the object's bounding box.
    """

    def __init__(self, model: CameraInfoModel):
        """
        Create a NavPath Tangent Handle Manipulator.

        Args:
            size: size of the TransformManipulator.
            enabled: If false, Manipulator will be created but disabled (invisible).
            axes: which axes to enable for the Manipulator. You can use this to create 2D or 1D manipulator.
            model: The model for the Manipulator. If None provided, a default SimpleTransformModel will be created.
            style: Use this to override the default style of the Manipulator.
        """
        super().__init__(model=model)
        # dictionary that record camera path to camera scene ui's sc.Transform
        self.camera_ui_dict: dict[str, Any] = {}
        self.camera_info_manager = CameraInfoManager.get_instance()

    def destroy(self):
        """destroy the camera scene ui transform dict"""
        # if current scene ui dict has not been cleaned
        if self.camera_ui_dict is not None:
            # clean each transform item
            for key, ui_transform in self.camera_ui_dict.items():
                ui_transform.clear()

            self.camera_ui_dict.clear()
            self.camera_ui_dict = None

    def on_build(self):
        """Called when the model is changed and rebuilds the whole manipulator"""
        if not self.model:
            return
        # get current selected camera list
        selected_camera_path_list = self.model._selected_camera_path_list
        if not selected_camera_path_list:
            return

        if self.camera_ui_dict is None:
            self.camera_ui_dict = {}

        with sc.Transform():
            self.camera_ui_dict.clear()
            for camera_path in selected_camera_path_list:
                camera_transform = sc.Transform()
                self.camera_ui_dict[str(camera_path)] = camera_transform
                with camera_transform:
                    # check whether user want to show current camera information
                    if CameraCalibrationSettings.show_fov_polygon_enabled:
                        # visualize camera's Fov in the scene
                        self.show_fov_field(camera_path)
                        pass

    # triggered when item model is changed
    def on_model_updated(self, item):
        self.invalidate()

    # draw camera's fov field with scene ui:
    # enable users to check cameras's aidnf
    def show_fov_field(self, camera_path):
        """visualize camera fov with the scene UI"""
        camera_object = self.camera_info_manager.get_camera_info(camera_path)
        self.camera_ui_dict[str(camera_path)].clear()
        if camera_object is None:
            return

        region_dict = camera_object.contours
        if region_dict is None:
            return
        with self.camera_ui_dict[str(camera_path)]:
            for region_key in region_dict.keys():
                # get outline and hole information for every fov polygon
                region = region_dict[region_key]
                outline = region.outline
                holes = region.holes
                if outline is None:
                    continue
                # create a curve to visualize the outline contour
                sc.Curve(
                    [[x, y, z] for x, y, z in outline],
                    thicknesses=[2.0],
                    colors=[cl.red],
                    curve_type=sc.Curve.CurveType.LINEAR,
                )
                # for every hole on the fov polygon, create a curve to visualize its contour
                for hole in holes:
                    sc.Curve(
                        [[x, y, z] for x, y, z in hole],
                        thicknesses=[2.0],
                        colors=[cl.red],
                        curve_type=sc.Curve.CurveType.LINEAR,
                    )
        pass
