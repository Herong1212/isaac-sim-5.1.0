import json
import numpy as np
from enum import Enum, IntFlag
from typing import List, Set, Any, Dict, Optional
import omni.usd
from ..settings import CameraPlacementSettings, GeneralSetting
import omni.kit.mesh.raycast
from omni.metropolis.utils.carb_util import CarbUtil
from omni.metropolis.utils.sensor_util import SensorUtil
from omni.metropolis.utils.math_util import MathNumpyUtil
from .camera_placement_utils import CameraPlacementUtils
from omni.metropolis.utils.usd_util import CameraUSDUtil
from omni.metropolis.utils.usd_util import USDUtil
from isaacsim.sensors.rtx.placement.camera_calibration.calibration_utils import CameraFovUtils
import carb
import math


def load_json_from_file(file_path: str) -> Any:
    """
    Loads JSON data from a file

    :param str file_path: file path
    :return: data in the file
    :rtype: Any
    ::

        data = load_json_from_file(file_path)
    """
    # valid_file_path = validate_file_path(file_path)
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def convert_to_map_pixel(x, y, translation_to_global_coordinates, scale_factor, map_height=1080):

    x_new = int((x + translation_to_global_coordinates["x"]) * scale_factor)
    y_new = int(map_height - 1.0 - ((y + translation_to_global_coordinates["y"]) * scale_factor))

    return (x_new, y_new)


class RoundMode(Enum):
    Nearest = 0
    Up = 1
    Down = 2


class Direction(IntFlag):
    X_Positive = 1 << 0  # 0001
    X_Negative = 1 << 1  # 0010
    Y_Positive = 1 << 2  # 0100
    Y_Negative = 1 << 3  # 1000


class CameraPlacementMode(Enum):
    Connectivity = 0
    CameraDistance = 1


# all four direction that we are intereseted in
# DirectionList = [Direction.X_Negative, Direction.X_Positive, Direction.Y_Negative, Direction.Y_Positive]


class DirectionCacheHelper:
    """helper class to cache the direction matrix"""

    @classmethod
    def create_matrix(cls, x_size: int, y_size: int) -> List[List[Direction]]:
        """
        Initialize a 2D matrix with no directions visited.
        """
        return [[Direction(0) for _ in range(y_size)] for _ in range(x_size)]

    @classmethod
    def mark_visited(cls, matrix: List[List[Direction]], x: int, y: int, direction: Direction) -> None:
        """
        Mark a specific direction as visited for a cell.
        """
        matrix[x][y] |= direction

    @classmethod
    def is_visited(cls, matrix: List[List[Direction]], x: int, y: int, direction: Direction) -> bool:
        """
        Check if a specific direction has been visited for a cell.
        """
        return (matrix[x][y] & direction) == direction


class CameraPlacementHelper:

    # record the order of the camera placement
    DIRECTION_ORDER_LIST = [Direction.X_Negative, Direction.X_Positive, Direction.Y_Negative, Direction.Y_Positive]

    @classmethod
    def get_focus_point_height(cls):
        people_focus_height = CameraPlacementSettings.focus_height
        ground_height = GeneralSetting.customized_floor_height
        # calculate the estimated focus point's height
        point_height = people_focus_height + ground_height
        return point_height

    @classmethod
    def get_camera_placement_yaw_range(cls, direction_category):
        """Output yaw range according to camera direction category"""

        # the yaw range would be the reversed camera direction.
        match direction_category:
            case Direction.X_Positive:
                return [(135, 225)]  # Split into two continuous ranges

            case Direction.Y_Positive:
                return [(225, 315)]

            case Direction.Y_Negative:
                return [(45, 135)]

            case Direction.X_Negative:
                return [(315, 360), (0, 45)]

            case _:
                raise ValueError("Invalid direction category provided.")

    @classmethod
    def get_direction_offset(cls, direction_category):
        """output yaw range according to camera direction category"""
        match direction_category:
            case Direction.X_Positive:
                return (1, 0)

            case Direction.Y_Positive:
                return (0, 1)

            case Direction.Y_Negative:
                return (0, -1)

            case Direction.X_Negative:
                return (-1, 0)

    @classmethod
    def create_sections(cls, focus_height: float, scope: List[tuple[float, float]]):
        """
        Creates an n x m array where each element is an np.array([x, y, z]) based on the coordinates provided.

        Parameters:
        - step: Step size for x and y axes in the grid

        Returns:
        - grid: An n x m numpy array where each element is an np.array([x, y, z])
        """
        step = CameraPlacementSettings.patch_size
        x_min, y_min, x_max, y_max = (
            scope[0][0],
            scope[1][0],
            scope[0][1],
            scope[1][1],
        )
        # Calculate number of rows and columns based on the step size
        rows = int(round((y_max - y_min) / step))
        cols = int(round((x_max - x_min) / step))

        # Initialize an empty grid with reversed shape (cols, rows) for [x][y] indexing
        grid = np.empty((cols, rows), dtype=object)

        # Populate the grid with [x, y, z] points in the [x][y] order
        for i in range(cols):
            for j in range(rows):
                # Calculate x, y values for this cell
                x = x_min + i * step  # x increases left to right
                y = y_min + j * step  # y increases bottom to top

                # Set the grid cell in [x][y] order
                grid[i, j] = np.array([x, y, focus_height])

        return grid

    @classmethod
    def create_hit_matrix(cls, focus_height: float, scope: List[tuple[float, float]], panel_check_height = 2):
        """use raycast to create a height span from the stage"""
        carb.log_warn("create hit matrix is called since navmesh is not available")
        raycast = omni.kit.mesh.raycast.get_mesh_raycast_interface()
        raycast.set_bvh_refresh_rate(omni.kit.mesh.raycast.BvhRefreshRate.FAST, True)
        step = CameraPlacementSettings.patch_size
        x_min, y_min, x_max, y_max = (
            scope[0][0],
            scope[1][0],
            scope[0][1],
            scope[1][1],
        )
         # Calculate number of rows and columns based on the step size
        rows = int(round((y_max - y_min) / step))
        cols = int(round((x_max - x_min) / step))

        # Initialize an empty grid with reversed shape (cols, rows) for [x][y] indexing
        grid = np.empty((cols, rows), dtype=object)

        # Populate the grid with [x, y, z] points in the [x][y] order
        for i in range(cols):
            for j in range(rows):
                # Calculate x, y values for this cell
                x = x_min + i * step  # x increases left to right
                y = y_min + j * step  # y increases bottom to top
                # Set the grid cell in [x][y] order
                start_point = np.array([x, y, focus_height + panel_check_height])
                dir = np.array([0, 0, -1])
                dist = 2*panel_check_height
                hit_result = raycast.closestRaycast(start_point, dir, dist)
                if hit_result and (hit_result.meshIndex != -1):
                    grid[i, j] = np.array([x, y, hit_result.position[2]])
                else:
                    grid[i, j] = start_point
        return grid




    @classmethod
    def get_minimum_camera_distance(cls, focus_height: Optional[float] = 0):
        """calculate the minimum distance projection on the x_y plane"""

        (
            camera_height_range,
            camera_distance_range,
            look_down_angle_range,
        ) = CameraPlacementUtils.get_camera_info_setting()
        # get target object/agent's radius
        target_object_radius = CameraPlacementSettings.estimated_agent_radius
        # get the camera distance
        min_camera_distance = CameraPlacementSettings.min_camera_distance
        # get the clipped camera look down angle range
        clipped_min_look_down_angle, clipped_max_look_down_angle = SensorUtil.get_pitch_range(
            focus_height=focus_height,
            target_object_radius=target_object_radius,
            camera_height_range=camera_height_range,
            camera_distance_range=camera_distance_range,
            look_down_angle_range=look_down_angle_range,
        )
        # get lerp ratio
        lerp_ratio = CameraPlacementSettings.border_checking_index

        min_look_down_angle, max_look_down_angle = look_down_angle_range
        lower_bound_camera_projection_distance = abs(
            (target_object_radius + min_camera_distance) * math.cos(math.radians(max_look_down_angle))
        )

        upper_bound_camera_projection_distance = abs(
            (target_object_radius + min_camera_distance) * math.cos(math.radians(clipped_max_look_down_angle))
        )
        camera_projection_distance = (
            upper_bound_camera_projection_distance * lerp_ratio
            + lower_bound_camera_projection_distance * (1 - lerp_ratio)
        )
        return camera_projection_distance

    @classmethod
    def generate_distance_values(cls, min_distance, max_distance, step):
        """
        Generates a list of distance values starting from min_distance, incremented by step,
        and ensures that max_distance is included in the list.

        Parameters:
        - min_distance (float): The starting distance value.
        - max_distance (float): The maximum distance value to include.
        - step (float): The increment between each distance value.

        Returns:
        - List[float]: A list of distance values from min_distance to max_distance.
        """
        distance_values = []  # Initialize an empty list to store distance values
        current = min_distance  # Start with the minimum distance

        # Loop to generate distance values incremented by 'step' until just below 'max_distance'
        while current < max_distance:
            distance_values.append(current)  # Add the current distance to the list
            current += step  # Increment the current distance by the step value

        # After the loop, check if the list is empty or if the last value is less than max_distance
        if not distance_values or distance_values[-1] < max_distance:
            distance_values.append(max_distance)  # Ensure max_distance is included

        return distance_values  # Return the final list of distance values

    @classmethod
    def check_point_in_scope(cls, target_point, scope: tuple):
        """check the projection of the camera position on the plane"""
        x_min, y_min, x_max, y_max = scope
        x, y = float(target_point[0]), float(target_point[1])
        is_within_x = x_min <= x <= x_max
        is_within_y = y_min <= y <= y_max

        return is_within_x and is_within_y

    @classmethod
    def calculate_camera_direction(cls, camera_path: str):
        """given a camera in the space, return the camera direction category"""

        # get camera prim:
        stage = omni.usd.get_context().get_stage()
        camera = stage.GetPrimAtPath(camera_path)
        # get camera direction vector:
        camera_forward_vector = CameraUSDUtil.get_camera_forward_vector(camera)
        A_x, A_y = camera_forward_vector[0], camera_forward_vector[1]  # We ignore A_z since Z points up

        if abs(A_x) > abs(A_y):
            if A_x >= 0:
                return Direction.X_Positive
            else:
                return Direction.X_Negative
        else:

            if A_y >= 0:
                return Direction.Y_Positive
            else:
                return Direction.Y_Negative

    @classmethod
    def get_space_checking_direction(cls, direction: Direction):
        """in order to place camera in target direction, check whether following direction have enough space to deploy the camera"""
        target_direction_list = []
        match direction:
            case Direction.X_Positive:
                target_direction_list = [Direction.X_Negative, Direction.Y_Negative]

            case Direction.Y_Positive:
                target_direction_list = [Direction.X_Positive, Direction.Y_Negative]

            case Direction.X_Negative:
                target_direction_list = [Direction.X_Positive, Direction.Y_Positive]

            case Direction.Y_Negative:
                target_direction_list = [Direction.Y_Positive, Direction.X_Negative]

        return target_direction_list

    @classmethod
    def get_next_direction(cls, current_direction):
        """return next direction base on defined order"""
        current_direction_index = cls.DIRECTION_ORDER_LIST.index(current_direction)
        next_index = (current_direction_index + 1) % len(cls.DIRECTION_ORDER_LIST)
        return cls.DIRECTION_ORDER_LIST[next_index]


    @classmethod
    def create_signed_section_matrix(cls, floor_height: float, scope: List[tuple[float, float]]):
        """create a signed section matrix"""

        template_section_matrix = None
        if GeneralSetting.need_navmesh_check:
            # template matrix that record each section dot's projection to the ground
            template_section_matrix = CameraPlacementHelper.create_sections(focus_height=floor_height, scope=scope)
        else: # template matrix that build from the raycast
            template_section_matrix = CameraPlacementHelper.create_hit_matrix(focus_height=floor_height, scope=scope)

        signed_section_matrix = CameraFovUtils.sign_2d_matrix(result_hit_matrix=template_section_matrix)
        return signed_section_matrix


    @classmethod
    def validate_scope(cls, scope: Optional[List[tuple[float, float]]] = None):
        """create a stage scope matrix"""
        if scope is None:
            return False
        if len(scope) != 2:
            return False
        if len(scope[0]) != 2 or len(scope[1]) != 2:
            return False
        #if the minimum value is greater than the maximum value return false
        if scope[0][0] >= scope[0][1] or scope[1][0] >= scope[1][1]:
            return False
        return True