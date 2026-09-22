import numpy as np
from itertools import combinations
from pxr import Sdf, Usd
import random
from ..settings import CameraCalibrationSettings, GeneralSetting
from .calibration_utils import CameraRayCastUtils
from .calibration_helper import CameraCalibrationHelper, CalibrationDotInfo
from omni.metropolis.utils.simulation_util import SimulationUtil
from omni.metropolis.utils.sensor_util import SensorUtil
from omni.metropolis.utils.math_util import MathUtil
from omni.metropolis.utils.usd_util import CameraUSDUtil
from typing import Dict, Optional, Any, Union, List
import carb


class CalibrationDotHelper:
    """helper method to generate calibration dots"""

    def compute_scatter_metric(points):
        """
        Compute the average pairwise distance among the points.
        """
        total_distance = 0
        count = 0
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                distance = np.linalg.norm(points[i] - points[j])
                total_distance += distance
                count += 1
        average_distance = total_distance / count if count > 0 else 0
        return average_distance

    async def select_points(camera_path, top_camera_path, lines, num_attempts=2000):
        """
        Select six points from the given lines such that:
        - No three points are colinear.
        - No four points are coplanar.
        - The points are as scattered as possible.
        """
        best_points = None
        best_scatter = -np.inf
        tol = 1e-6
        # Preprocess lines to ensure diversity (optional but recommended)
        # For simplicity, assume lines are already suitable

        calibration_num = CameraCalibrationSettings.calibration_prim_num
        formatted_camera_params = await CameraCalibrationHelper.get_camera_params(camera_path=camera_path)

        for attempt in range(num_attempts):
            # Randomly select lines that equal to users' setting value
            selected_lines = random.sample(lines, calibration_num)
            points = []
            # Select points on each line
            for S, E in selected_lines:
                # To maximize scatter, consider using endpoints
                # Or select points towards the extremes
                t = random.choice([0.0, 1.0])  # Choose endpoints
                # Alternatively, use random t
                # t = random.uniform(0, 1)
                P = S + t * (E - S)
                points.append(P)
            # Check for colinearity
            colinear = any(MathUtil.is_colinear(*combo, tol=tol) for combo in combinations(points, 3))
            if colinear:
                continue  # Try next attempt
            # Check for coplanarity
            coplanar = any(MathUtil.is_coplanar(*combo, tol=tol) for combo in combinations(points, 4))
            if coplanar:
                continue  # Try next attempt

            valid_calibration_dot_infos = await CalibrationDotHelper.get_validate_pos_in_scope(
                pos_list=points,
                target_camera_path=camera_path,
                top_camera_path=top_camera_path,
                target_camera_params=formatted_camera_params,
            )

            if not valid_calibration_dot_infos:
                continue

            # Compute scatter metric
            scatter = CalibrationDotHelper.compute_scatter_metric(points)
            # Update best points if scatter is improved
            if scatter > best_scatter:
                best_scatter = scatter
                best_points = points

        if best_points is not None:
            return best_points, best_scatter
        else:
            raise ValueError("Could not find suitable points after multiple attempts.")

    def generate_lines_in_stage(camera_path):
        """get generate lines in the stage via raycast"""
        point_list = []
        # set a boundary, ignore all the point within the scope.
        clipping_distance_min = 3.0
        clipping_distance_max = 20
        # get calibration seed
        seed = CameraCalibrationSettings.raycast_seed
        point_list = CameraUSDUtil.get_camera_frustum_corners(camera_path=camera_path)
        if not point_list or len(point_list) < 8:
            return None

        line_set = []
        upper_patform = point_list[:4]
        lower_patform = point_list[-4:]
        dot_upper_matrix, dot_lower_matrix = CameraRayCastUtils.generate_dot_point_pair_matrix(
            upper_patform, lower_patform, seed
        )
        row = len(dot_upper_matrix)
        col = len(dot_upper_matrix[0])
        for i in range(row):
            for j in range(col):
                hit_dot = CameraRayCastUtils.get_calibration_dot(dot_upper_matrix[i][j], dot_lower_matrix[i][j])
                start_point = dot_upper_matrix[i][j]
                start_point_np = np.array([start_point[0], start_point[1], start_point[2]])
                hit_dot_np = np.array([hit_dot[0], hit_dot[1], hit_dot[2]])
                # ensure there is enough  distance between start point and end point
                vector_scale = np.linalg.norm(start_point - hit_dot_np)
                # ensure the camera and calibration dot distance is within a reasonable range
                if vector_scale > clipping_distance_min:

                    vector_direction = (hit_dot_np - start_point_np) / vector_scale
                    start_point_np = start_point_np + vector_direction * clipping_distance_min
                    end_point_np = start_point_np + vector_direction * min(clipping_distance_max, vector_scale)
                    line_set.append((start_point_np, end_point_np))

        return line_set

    async def pick_calibration_dot(camera_path: str, top_view_camera_path: str):
        """pick calibration dot"""
        lines = CalibrationDotHelper.generate_lines_in_stage(camera_path=camera_path)
        best_points, best_scatter = await CalibrationDotHelper.select_points(
            camera_path=camera_path, top_camera_path=top_view_camera_path, lines=lines
        )
        return best_points

    async def get_validate_pos_in_scope(
        pos_list: List,
        target_camera_path: Union[Sdf.Path, str],
        top_camera_path: Union[Sdf.Path, str],
        target_camera_params: Optional[Dict] = None,
    ) -> None | List[CalibrationDotInfo]:
        """check whether dot is within target camera's view scope and top camera's view scope"""
        # if target camera params is not fetched
        points = np.array(pos_list)
        if target_camera_params is None:
            carb.log_error("Input is none, regenerate the camera params")
            target_camera_params = await CameraCalibrationHelper.get_camera_params(camera_path=target_camera_path)

        calibration_dots_in_camera_scope, target_camera_image_coordinate = SensorUtil.project_3d_to_2d_persp(
            points=points, camera_params=target_camera_params
        )
        # check whether the selected point cluster could be covered by the top view camera's scope.
        calibration_dots_in_top_camera_scope, top_camera_image_coordinate = SensorUtil.project_3d_to_2d_ortho(
            camera_path=top_camera_path, points=points
        )
        # calibration dot in camera scope
        if (
            calibration_dots_in_camera_scope is None
            or calibration_dots_in_top_camera_scope is None
            or (None in calibration_dots_in_camera_scope)
            or (None in calibration_dots_in_top_camera_scope)
        ):
            return None

        calibration_dot_infos: List[CalibrationDotInfo] = []
        for i in range(len(calibration_dots_in_camera_scope)):
            world_coord = calibration_dots_in_top_camera_scope[i]
            target_camera_image_coord = target_camera_image_coordinate[i]
            top_camera_image_coord = top_camera_image_coordinate[i]
            calibration_dot_info = CalibrationDotInfo(
                world_coord=world_coord,
                target_camera_image_coord=target_camera_image_coord,
                top_camera_image_coord=top_camera_image_coord,
            )
            calibration_dot_infos.append(calibration_dot_info)

        return calibration_dot_infos
