from pxr import Gf
import numpy as np
from typing import Dict, List, Optional
import carb
import math
from ..utils import CameraGeneralUtil
from omni.metropolis.utils.simulation_util import SimulationUtil
from omni.metropolis.utils.math_util import MathUtil, MathNumpyUtil
from omni.metropolis.utils.usd_util import USDUtil
from ..settings import CameraPlacementSettings
from pxr import Gf


class CameraPlacementUtils:
    """util function for camera placement"""

    @staticmethod
    def default_camera_information() -> Dict[str, float]:
        """
        Retrieve default camera parameters.
        Returns:
            Dict[str, float]: A dictionary containing default camera settings.
                - 'focal_length': The default focal length of the camera lens.
                - 'horizontal_aperture': The default horizontal aperture size.
                - 'clip_distance': The default clipping distance.
                - 'image_width': The default width of the image in pixels.
                - 'image_height': The default height of the image in pixels.
        """
        return {
            "focal_length": 18.14756,
            "horizontal_aperture": 20.955,
            "clip_distance": 1.0,
            "image_width": 1920,
            "image_height": 1080,
        }

    @staticmethod
    def get_camera_rotation_in_quatf(camera_pos, focus_point):
        """get camera rotation in quatf"""
        camera_rotation = Gf.Quatd(
            CameraGeneralUtil.lookat_to_quatf(
                Gf.Vec3d(focus_point[0], focus_point[1], focus_point[2]),
                Gf.Vec3d(camera_pos[0], camera_pos[1], camera_pos[2]),
                Gf.Vec3d(0, 0, 1),
            )
        )
        return camera_rotation

    @staticmethod
    def get_camera_info_setting() -> tuple:
        """get camera related settings information"""
        max_camera_height = CameraPlacementSettings.max_camera_height
        min_camera_height = CameraPlacementSettings.min_camera_height
        max_look_down_angle = CameraPlacementSettings.max_camera_look_down_angle
        min_look_down_angle = CameraPlacementSettings.min_camera_look_down_angle
        min_camera_distance = CameraPlacementSettings.min_camera_distance
        max_camera_distance = CameraPlacementSettings.max_camera_distance
        camera_height_range = (min_camera_height, max_camera_height)
        camera_distance_range = (min_camera_distance, max_camera_distance)
        look_down_angle_range = (min_look_down_angle, max_look_down_angle)
        return camera_height_range, camera_distance_range, look_down_angle_range
