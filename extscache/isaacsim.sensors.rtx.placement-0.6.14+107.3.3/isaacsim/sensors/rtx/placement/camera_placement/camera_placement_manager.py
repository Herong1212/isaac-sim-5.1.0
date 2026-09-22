from __future__ import annotations
import os
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import carb
import math
from .camera_placement_utils import CameraPlacementUtils
from omni.metropolis.utils.math_util import MathNumpyUtil
from ..settings import CameraPlacementSettings, GeneralSetting
from omni.metropolis.utils.usd_util import USDUtil, CameraUSDUtil
from omni.metropolis.utils.sensor_util import SensorUtil, CameraPose
from omni.metropolis.utils.geomtry_util import GeomtryUtil
from omni.metropolis.utils.file_util import JSONFileUtil
from omni.metropolis.utils.simulation_util import SimulationUtil
from ..camera_calibration.contour_polygon import FOVStatus
from .camera_placement_helper import (
    CameraPlacementHelper,
    Direction,
    DirectionCacheHelper,
    CameraPlacementMode,
    RoundMode,
)
from ..utils import CameraGeneralUtil
import omni.usd
from pxr import UsdGeom, Usd


class CameraPlacementManager:
    """Global class which stores current and predicted positions of all characters and moving objects."""

    __instance: CameraPlacementManager = None

    def __init__(self):
        if self.__instance is not None:
            raise RuntimeError("Only one instance of CameraPlacementManager is allowed")

        self.stage_section_matrix = None
        self.signed_section_matrix = None
        self.cached_focused_matrix = None
        self.connectivity_matrices = None  # connectivity would be update as the placement of each camera in the stage.
        self.cached_border_matrix = None
        self.coverage_counter_matrix = None
        self.direction_to_camera_info_list: dict[Direction, List[Dict[str, Any]]] = {}
        self.camera_distance_matrices = None

        self.stage_scope: List[tuple[float, float]] = (
            []
        )  # record the stage's scope, each element is a min, max range of the dimension
        self.focus_height: float | None = None

        CameraPlacementManager.__instance = self

    def destroy(self):
        CameraPlacementManager.__instance = None

    def __del__(self):
        self.destroy()

    @classmethod
    def get_instance(cls) -> CameraPlacementManager:
        if cls.__instance is None:
            CameraPlacementManager()
        return cls.__instance

    def get_signed_matrix(self):
        return self.signed_section_matrix

    def get_stage_section_matrix(self):
        return self.stage_section_matrix

    def get_cached_focused_matrix(self):
        return self.cached_focused_matrix

    def is_point_focused(self, x: int, y: int, direction: Direction):
        """check whether user has attempt to place camera on certain point"""
        return DirectionCacheHelper.is_visited(self.cached_focused_matrix, x, y, direction)

    def is_point_accessible(self, x: int, y: int):
        """check whether the point is on the navmesh"""
        return self.signed_section_matrix[x][y] == FOVStatus.ACCESSIBLE.value

    def is_point_on_border(self, x: int, y: int, direction: Direction):
        return DirectionCacheHelper.is_visited(self.cached_border_matrix, x, y, direction)

    def mark_point_as_border(self, x: int, y: int, direction: Direction):
        DirectionCacheHelper.mark_visited(self.cached_border_matrix, x=x, y=y, direction=direction)

    def mark_point_focused(self, x: int, y: int, direction: Direction):
        DirectionCacheHelper.mark_visited(self.cached_focused_matrix, x=x, y=y, direction=direction)

    # NOTE::update the way to store coverage
    def get_point_cover_count(self, x: int, y: int):
        """get how many time the point need to be covered"""
        return self.coverage_counter_matrix[x][y]

    def mark_point_covered(self, x: int, y: int):
        """mark the point as covered, update the coverage counter"""
        self.coverage_counter_matrix[x][y] = max(self.coverage_counter_matrix[x][y] - 1, 0)

    def is_point_fully_covered(self, x: int, y: int) -> bool:
        return self.get_point_cover_count(x=x, y=y) == 0

    def get_focus_point(self, x: int, y: int, point_height=None):
        if point_height is None:
            return self.stage_section_matrix[x][y]

        point_pos = self.stage_section_matrix[x][y]
        point_pos_np = np.array([point_pos[0], point_pos[1], point_height])
        return point_pos_np

    def set_point_camera_distance(self, x: int, y: int, target_direction: Direction, target_value):
        """set point's camera distance from certain point"""
        camera_distance_matrix = self.camera_distance_matrices[target_direction]
        camera_distance_matrix[x][y] = target_value

    def get_point_camera_distance(self, x: int, y: int, target_direction: Direction):
        """get target point's camera distance in target direction"""
        camera_distance_matrix = self.camera_distance_matrices[target_direction]
        camera_distance = camera_distance_matrix[x][y]
        return camera_distance

    def get_coveraged_sum_count(self):
        """calculate the coverage ratio of target direction"""
        x_size, y_size = self.get_section_size()
        # get the min camera coverage requirement on each patch
        required_camera_per_patch = CameraPlacementSettings.required_camera_per_patch
        covered_counter = 0
        for x in range(x_size):
            for y in range(y_size):
                # only check patchs on navmesh
                if self.is_point_accessible(x=x, y=y):
                    # for each patch, calculate how many camera coverage is still required.
                    covered_counter = covered_counter + (
                        required_camera_per_patch - self.get_point_cover_count(x=x, y=y)
                    )

        return covered_counter

    def get_all_distance(self, direction: Direction):
        """calculate the sum of camera distance in target direction"""
        x_size, y_size = self.get_section_size()
        total_camera_distance = 0
        for x in range(x_size):
            for y in range(y_size):
                camera_distance = self.get_point_camera_distance(x=x, y=y, target_direction=direction)
                total_camera_distance = total_camera_distance + camera_distance
        return total_camera_distance

    def get_section_size(self):
        """get the size of current space"""
        if self.stage_section_matrix is None:
            return None
        x_size, y_size = len(self.stage_section_matrix), len(self.stage_section_matrix[0])

        return (x_size, y_size)

    def get_coverage_area_scope(self) -> list[tuple[float, float]]:
        """get the 3d scope of the coverage area scope"""
        x_size, y_size = self.get_section_size()
        min_point = self.stage_section_matrix[0][0]
        max_point = self.stage_section_matrix[x_size - 1][y_size - 1]
        x_min, y_min = min_point[0], min_point[1]
        x_max, y_max = max_point[0], max_point[1]

        return [(x_min, x_max), (y_min, y_max)]

    def calculate_point_coordinate(self, position, round_mode: Optional[RoundMode] = RoundMode.Nearest):
        """calculate the coodinate of a 3d point in current stage section matrix"""
        if self.stage_section_matrix is None:
            carb.log_warn("stage section matrix has not been initialized")

        # according to the properties of the stage section matrix
        step = CameraPlacementSettings.patch_size
        x_size, y_size = self.get_section_size()
        scope = self.get_coverage_area_scope()
        x_min, y_min = scope[0][0], scope[1][0]
        x_pos, y_pos = position[0], position[1]

        if round_mode == RoundMode.Nearest:
            x_coordinate = round((x_pos - x_min) / step)
            y_coordinate = round((y_pos - y_min) / step)

        elif round_mode == RoundMode.Up:
            x_coordinate = np.ceil((x_pos - x_min) / step)
            y_coordinate = np.ceil((y_pos - y_min) / step)
        else:
            x_coordinate = np.floor((x_pos - x_min) / step)
            y_coordinate = np.floor((y_pos - y_min) / step)

        x_limitation = x_size - 1

        y_limitation = y_size - 1

        x_coordinate = np.clip(x_coordinate, 0, x_limitation)
        y_coordinate = np.clip(y_coordinate, 0, y_limitation)
        return (int(x_coordinate), int(y_coordinate))

    def initialize_direction_camera_count(self):
        """record camera information in each direction"""
        self.direction_to_camera_info_list = {}
        for direction in Direction:
            self.direction_to_camera_info_list[direction] = []

    def get_all_camera_info(self) -> Dict:
        """return all recorded camera information"""
        return self.direction_to_camera_info_list

    def initialize_section_status(
        self, section_scope: Optional[List[tuple[float, float]]] = None, focus_height: Optional[float] = None
    ):
        """split stage into multiple section, initialize data structures to abstract stage information"""
        # if there is no predined scope, use the stage's scope as the default value

        if not CameraPlacementHelper.validate_scope(section_scope):
            carb.log_warn("Invalid stage scope, please check the scope value, attempt to fetch scope from the navmesh")
            section_scope = None

        if section_scope is None:
            if GeneralSetting.need_navmesh_check:
                section_scope = SimulationUtil.get_navmesh_scope()
            else:
                carb.log_warn("No target scope provided, navmesh is not available neither stage scope, plese check the input")
                return None
        self.stage_scope = section_scope

        # if there is no customized floor height value, navmesh's z value would be take as a default value
        if focus_height is None:
            focus_height = CameraPlacementHelper.get_focus_point_height()

        self.focus_height = focus_height

        floor_height = GeneralSetting.customized_floor_height


        self.signed_section_matrix = CameraPlacementHelper.create_signed_section_matrix(floor_height=floor_height, scope=section_scope)

        self.stage_section_matrix = CameraPlacementHelper.create_sections(
            focus_height=focus_height, scope=section_scope
        )

        x_size, y_size = self.get_section_size()

        self.cached_focused_matrix = DirectionCacheHelper.create_matrix(
            x_size, y_size
        )  # sections to record focused point of each camera in different directions
        self.cached_border_matrix = DirectionCacheHelper.create_matrix(
            x_size, y_size
        )  # sections to record border information/ the area that cannot be choosed as focus point

        self.connectivity_matrices: Dict[Direction, List[List[int]]] = {
            direction: np.zeros((x_size, y_size), dtype=int) for direction in Direction
        }

        self.initialize_coverage_counter()
        # connect the space 's connectivity in four direction, record the result in matrix
        self.recalculate_connectivity()
        # compute the limitation of the camera, clipping the space where camera cannot be set.
        self.calculate_border()
        self.initialize_direction_camera_count()
        self.create_camera_distance_matrix()

    def get_connectivity_matrix(self, direction: Direction):
        return self.connectivity_matrices[direction]

    def create_camera_distance_matrix(self):
        """Calculate the camera distance for each point in each direction"""
        self.camera_distance_matrices = {}
        # get the size of the space matrix:
        x_size, y_size = self.get_section_size()
        patch_size = CameraPlacementSettings.patch_size
        # use the width and height of the matrix to calculated a potential largest point distance
        largest_distance = math.sqrt(x_size * x_size + y_size * y_size) * patch_size
        for direction in Direction:
            # remove the effect of the inaccessible point:
            camera_matrix = np.full((x_size, y_size), 0, dtype=int)
            self.camera_distance_matrices[direction] = camera_matrix
            for x in range(x_size):
                for y in range(y_size):
                    if self.is_point_accessible(x=x, y=y):
                        self.set_point_camera_distance(
                            x=x, y=y, target_direction=direction, target_value=largest_distance
                        )

    def recalculate_connectivity(self):
        """
        Recalculate the connectivity for each point in each direction, using a sliding window approach.
        If `sliding_window_length` is None, calculates connectivity for the entire matrix.

        Args:
            sliding_window_length (Optional[int]): The length of the sliding window. Default is None for global calculation.
        """
        x_size, y_size = self.get_section_size()
        sliding_window_length = self.get_section_scope_in_view()
        # Reset all connectivity matrices to zero
        for direction in Direction:
            self.connectivity_matrices[direction].fill(0)

        # Recalculate connectivity for each direction
        for direction in Direction:
            x_offset, y_offset = CameraPlacementHelper.get_direction_offset(direction)
            result_matrix = self.connectivity_matrices[direction]

            # Process rows or columns depending on direction
            if x_offset != 0:  # Horizontal direction
                for y in range(y_size):
                    row = [
                        self.get_point_cover_count(x, y) if self.is_point_accessible(x, y) else -1
                        for x in range(x_size)
                    ]
                    if x_offset < 0:
                        row = row[::-1]
                    row_connectivity = self._calculate_array_connectivity(row, sliding_window_length)
                    if x_offset < 0:
                        row_connectivity = row_connectivity[::-1]
                    for x in range(x_size):
                        result_matrix[x][y] = row_connectivity[x]
            elif y_offset != 0:  # Vertical direction
                for x in range(x_size):
                    col = [
                        self.get_point_cover_count(x, y) if self.is_point_accessible(x, y) else -1
                        for y in range(y_size)
                    ]
                    if y_offset < 0:
                        col = col[::-1]
                    col_connectivity = self._calculate_array_connectivity(col, sliding_window_length)
                    if y_offset < 0:
                        col_connectivity = col_connectivity[::-1]
                    for y in range(y_size):
                        result_matrix[x][y] = col_connectivity[y]

        return self.connectivity_matrices

    def _calculate_array_connectivity(self, arr: List[int], sliding_window_length: Optional[int]) -> List[int]:
        """
        Calculate connectivity for a 1D array (row or column) using a sliding window approach.
        Computes the sum of the sliding window's z-values for each point.

        Args:
            arr (List[int]): The 1D array of cover counts or -1 for inaccessible points.
            sliding_window_length (Optional[int]): The length of the sliding window. Default is None for global calculation.

        Returns:
            List[int]: The connectivity values for each point in the 1D array.
        """
        M = len(arr)
        connectivity = [0] * M  # Initialize the result array
        current_z = 0  # Current sliding window sum

        # If the sliding window length is None, set it to the entire array length
        if sliding_window_length is None:
            sliding_window_length = M

        # Reverse the array for efficient sliding window computation
        reversed_arr = arr[::-1]
        reversed_connectivity = [0] * M  # To store the results in reverse order

        for i in range(M):
            # Reset connectivity if the current point is inaccessible
            if reversed_arr[i] == -1:
                current_z = 0
            else:
                current_z += reversed_arr[i]

            # Remove the leftmost value if the sliding window exceeds its length
            if i >= sliding_window_length:
                if reversed_arr[i - sliding_window_length] != -1:
                    current_z -= reversed_arr[i - sliding_window_length]
                else:
                    current_z = 0  # Reset if the leftmost value was inaccessible

            # Update the reversed connectivity for the current point
            reversed_connectivity[i] = current_z if reversed_arr[i] != -1 else -1

        # Reverse the result back to match the original array order
        connectivity = reversed_connectivity[::-1]
        return connectivity

    def get_section_scope_in_view(self) -> int | None:
        """calculate the section scope of the camera"""
        apply_camera_distance_check = CameraPlacementSettings.limit_fov_by_distance
        camera_distance_span = CameraPlacementSettings.max_camera_distance - CameraPlacementSettings.min_camera_distance
        patch_size = CameraPlacementSettings.patch_size
        if apply_camera_distance_check:
            sliding_window_length = int(camera_distance_span / patch_size)
        else:
            sliding_window_length = None
        return sliding_window_length

    def update_connectivity(self, target_points: Optional[List[Tuple[int, int]]] = None):
        """
        Update the connectivity after the placement of the camera in the stage, using a sliding window approach.

        Args:
            target_points (Optional[List[Tuple[int, int]]]): Points to update. If None, recalculates the entire connectivity matrix.
            sliding_window_length (Optional[int]): The length of the sliding window. Default is None for global calculation.
        """
        x_size, y_size = self.get_section_size()

        sliding_window_length = self.get_section_scope_in_view()

        if target_points is None:
            # Recalculate the entire connectivity matrix
            self.recalculate_connectivity()
            return

        if not target_points:
            return  # No target points to process

        for direction in Direction:
            x_offset, y_offset = CameraPlacementHelper.get_direction_offset(direction)
            result_matrix = self.connectivity_matrices[direction]

            # Extract affected rows or columns
            affected_x = set()
            affected_y = set()

            for x, y in target_points:
                if x_offset != 0:  # Horizontal direction
                    affected_y.add(y)
                if y_offset != 0:  # Vertical direction
                    affected_x.add(x)

            # Recalculate affected rows or columns
            for y in affected_y:  # Recalculate all rows affected
                row = [
                    self.get_point_cover_count(x, y) if self.is_point_accessible(x, y) else -1 for x in range(x_size)
                ]
                if x_offset < 0:
                    row = row[::-1]
                row_connectivity = self._calculate_array_connectivity(row, sliding_window_length)
                if x_offset < 0:
                    row_connectivity = row_connectivity[::-1]
                for x in range(x_size):
                    result_matrix[x][y] = row_connectivity[x]

            for x in affected_x:  # Recalculate all columns affected
                col = [
                    self.get_point_cover_count(x, y) if self.is_point_accessible(x, y) else -1 for y in range(y_size)
                ]
                if y_offset < 0:
                    col = col[::-1]
                col_connectivity = self._calculate_array_connectivity(col, sliding_window_length)
                if y_offset < 0:
                    col_connectivity = col_connectivity[::-1]
                for y in range(y_size):
                    result_matrix[x][y] = col_connectivity[y]

    def initialize_coverage_counter(self):
        """initialize the counter matrix to record coverage"""
        x_size, y_size = self.get_section_size()
        required_camera_per_patch = CameraPlacementSettings.required_camera_per_patch
        coverage_counter_matrix = np.full((x_size, y_size), 0, dtype=int)
        for x in range(x_size):
            for y in range(y_size):
                # check whether point is accessible point
                if self.is_point_accessible(x=x, y=y):
                    coverage_counter_matrix[x][y] = required_camera_per_patch

        self.coverage_counter_matrix = coverage_counter_matrix

    def calculate_border(self):
        """
        Mark points within a certain distance from an inaccessible area (-1) or boundary as edges in specific directions.
        """

        # calculate what is the border in current setting:
        minimum_camera_space = CameraPlacementHelper.get_minimum_camera_distance(focus_height=self.focus_height)
        step = CameraPlacementSettings.patch_size
        x_size, y_size = self.get_section_size()
        distance = math.ceil(minimum_camera_space / step)

        for x in range(x_size):
            for y in range(y_size):
                if not self.is_point_accessible(x=x, y=y):  # Inaccessible area
                    # Check neighbors within the specified distance for each direction
                    for d in range(1, distance + 1):
                        # if there are accessible sections on the X_Positive side of the edge, mark the sections as border for X_Negative direction
                        # since inaccesible point is on the reverse direction.
                        if x + d < x_size:
                            self.mark_point_as_border(x + d, y, Direction.X_Negative)

                        # if there are accessible sections on the X_Negative side of the edge, mark the sections as border for X_Positive direction
                        # since inaccesible point is on the reverse direction.
                        if x - d >= 0:
                            self.mark_point_as_border(x - d, y, Direction.X_Positive)

                        if y + d < y_size:
                            self.mark_point_as_border(x, y + d, Direction.Y_Negative)

                        if y - d >= 0:
                            self.mark_point_as_border(x, y - d, Direction.Y_Positive)

    def get_point_connectivity(self, x: int, y: int, direction: Direction) -> int:
        """Retrieve the connectivity index for a given point and direction."""
        x_size, y_size = self.get_section_size()
        if direction in self.connectivity_matrices:
            if 0 <= x < x_size and 0 <= y < y_size:
                return self.connectivity_matrices[direction][x][y]
        return -1  # Return -1 if the point is out of bounds or direction not valid

    def calculate_coverage(
        self,
        camera_position: np.ndarray,
        camera_polygon: dict[str, float],
        signed_coverage: Optional[bool] = False,
        record_covered_coordate: Optional[bool] = False,
    ):
        """check how many unvisited point would be coverted by this camera"""
        covered_coordinate = []

        max_camera_distance = CameraPlacementSettings.max_camera_distance
        min_camera_distance = CameraPlacementSettings.min_camera_distance

        apply_camera_distance_check = CameraPlacementSettings.limit_fov_by_distance

        top_left = camera_polygon["top_left"]
        top_right = camera_polygon["top_right"]
        bottom_right = camera_polygon["bottom_right"]
        bottom_left = camera_polygon["bottom_left"]

        fov_contour = [top_left, top_right, bottom_right, bottom_left]
        # predict the shape and the boudnary of camera view FOV projection on the ground
        boundary_info = GeomtryUtil.compute_bounding_box(polygon_vertices=fov_contour, dimension=2)
        #  only count points that has not yet been included in the estimate FOV scope
        x_min = boundary_info[0][0]
        y_min = boundary_info[1][0]
        x_max = boundary_info[0][1]
        y_max = boundary_info[1][1]

        # get the intesection of polygon on the focused area.
        max_vertex = np.array([x_max, y_max, self.focus_height])
        min_vertex = np.array([x_min, y_min, self.focus_height])
        # make the range loose, since there would be a geometry check after this
        max_x_coordinate, max_y_coordinate = self.calculate_point_coordinate(
            position=max_vertex, round_mode=RoundMode.Up
        )
        min_x_coordinate, min_y_coordinate = self.calculate_point_coordinate(
            position=min_vertex, round_mode=RoundMode.Down
        )

        # the clip the scope of predicted FOV polygon
        x_range = range(min_x_coordinate, max_x_coordinate)
        y_range = range(min_y_coordinate, max_y_coordinate)
        # count the number of covered point in the FOV polygon
        counter = 0

        raycast = omni.kit.mesh.raycast.get_mesh_raycast_interface()
        raycast.set_bvh_refresh_rate(omni.kit.mesh.raycast.BvhRefreshRate.FAST, True)

        for x in x_range:
            for y in y_range:

                focus_pos_np = self.get_focus_point(x=x, y=y)

                if self.is_point_fully_covered(x=x, y=y):
                    continue
                if not GeomtryUtil.is_point_in_convex_polygon(focus_pos_np, fov_contour):
                    continue
                if not self.is_point_accessible(x=x, y=y):
                    continue

                # get the potential character position on this point
                camera_pos_np = np.array(camera_position)
                if apply_camera_distance_check:
                    camera_distance = np.linalg.norm(camera_pos_np - focus_pos_np)
                    if camera_distance > max_camera_distance or camera_distance < min_camera_distance:
                        continue

                raycast_test_vector = camera_pos_np - focus_pos_np
                ray_cast_direction = MathNumpyUtil.normalize_vector(raycast_test_vector)
                ray_length = math.sqrt(
                    sum([raycast_test_vector[0] ** 2 + raycast_test_vector[1] ** 2 + raycast_test_vector[2] ** 2])
                )
                hit_result = raycast.closestRaycast(focus_pos_np, ray_cast_direction, ray_length)

                meshIndex = hit_result.meshIndex
                hit_position = hit_result.position

                if (
                    meshIndex == -1
                    or np.linalg.norm(camera_pos_np - np.array([hit_position[0], hit_position[1], hit_position[2]]))
                    < 0.2
                ):
                    counter = counter + self.get_point_cover_count(x=x, y=y)
                    if signed_coverage:
                        # udpate the coverage matrix
                        self.mark_point_covered(x=x, y=y)

                    if record_covered_coordate:
                        covered_fov_point = (x, y)
                        covered_coordinate.append(covered_fov_point)

        return counter, covered_coordinate

    def get_best_camera_pose_connectivity(
        self,
        direction: Direction,
        focus_point: Optional[np.ndarray] = None,
        coordinate: Optional[tuple[float, float]] = None,
    ) -> CameraPose | None:
        """Given a focus point in the stage, calculate the best position that can cover most of the section on the ground. Then simulation the camera placement"""

        if focus_point is None:
            x, y = coordinate
            focus_point = self.get_focus_point(x=x, y=y)

        if coordinate is None:
            coordinate = self.calculate_point_coordinate(position=focus_point)

        validated_camera_pos_info: list[CameraPose] = []
        best_camera_pos_info: CameraPose | None = None

        # pick validate camera position around the focus point
        validated_camera_pos_info = self.get_validated_camera_poses(
            target_point=focus_point, target_direction=direction
        )

        max_coverage = 0

        # find the best position to set up the camera given choosed focus point
        for camera_info in validated_camera_pos_info:
            camera_position = camera_info.camera_position
            camera_dir = camera_info.camera_direction
            # predict the camera FOV and calculate the coverage of camera FOV
            camera_fov_polygon = self.estimate_camera_fov(camera_position=camera_position, camera_dir=camera_dir)
            coverage, _ = self.calculate_coverage(camera_position=camera_position, camera_polygon=camera_fov_polygon)
            if coverage > max_coverage:
                max_coverage = coverage
                best_camera_pos_info = camera_info

        if best_camera_pos_info is not None:
            camera_position = best_camera_pos_info.camera_position
            camera_dir = best_camera_pos_info.camera_direction
            camera_fov_polygon = self.estimate_camera_fov(camera_position=camera_position, camera_dir=camera_dir)

            # mark the point covered by camera FOV
            # simulation the camera placement
            _, covered_coordinates = self.calculate_coverage(
                camera_position=camera_position,
                camera_polygon=camera_fov_polygon,
                record_covered_coordate=True,
                signed_coverage=True,
            )
            # update camera connectivity directly
            if len(covered_coordinates) > 0:
                self.update_connectivity(target_points=covered_coordinates)

        else:
            carb.log_info("No Valid Camera for Current Position" + str(focus_point) + str(coordinate))

        x_coordinate, y_coordinate = coordinate
        # mark the point as focus
        self.mark_point_focused(x=x_coordinate, y=y_coordinate, direction=direction)

        return best_camera_pos_info

    def get_best_camera_pose_distance(
        self, direction: Direction, focus_point=None, coordinate: tuple | None = None
    ) -> CameraPose | None:
        """Given a focus point in the stage, calculate the best position that can cover most of the section on the ground. Then simulation the camera placement"""
        if focus_point is None:
            x, y = coordinate
            focus_point = self.get_focus_point(x=x, y=y)

        if coordinate is None:
            coordinate = self.calculate_point_coordinate(position=focus_point)

        validated_camera_pos_info: list[CameraPose] = []
        best_camera_pos_info: CameraPose | None = None

        # pick validate camera position around the focus point
        validated_camera_pos_info = self.get_validated_camera_poses(
            target_point=focus_point, target_direction=direction
        )
        max_distance_reduce = 0

        # find the best position to set up the camera given choosed focus point
        for camera_info in validated_camera_pos_info:
            camera_position = camera_info.camera_position
            # predict the camera FOV and calculate the coverage of camera FOV
            distance_update = self.estimate_camera_distance_update(
                camera_position=camera_position, focus_point_coordinate=coordinate, direction=direction
            )
            if distance_update > max_distance_reduce:
                max_distance_reduce = distance_update
                best_camera_pos_info = camera_info

        if best_camera_pos_info is not None:
            camera_position = best_camera_pos_info.camera_position
            # mark the point covered by camera FOV
            # simulation the camera placement
            self.update_point_to_camera_distance(
                camera_position=camera_position, focus_point_coordinate=coordinate, direction=direction
            )
        else:
            carb.log_info("No Valid Camera for Current Position" + str(focus_point) + str(coordinate))

        x_coordinate, y_coordinate = coordinate
        # mark the point as focus
        self.mark_point_focused(x=x_coordinate, y=y_coordinate, direction=direction)
        self.set_point_camera_distance(x=x_coordinate, y=y_coordinate, target_direction=direction, target_value=0)
        return best_camera_pos_info

    def has_enough_space(self, x, y, direction_list: list[Direction]):
        for direct in direction_list:
            if self.is_point_on_border(x, y, direct):
                return False

        return True

    def get_all_accessible_section_count(self):
        """get all accessible section in the stage"""
        x_size, y_size = self.get_section_size()
        total_node = x_size * y_size
        for x in range(x_size):
            for y in range(y_size):
                if not self.is_point_accessible(x=x, y=y):
                    total_node = total_node - 1

        return total_node

    def get_iteration_order(self, direction: Direction):
        """base on the direction, determine the order to iterate the grid"""
        x_size, y_size = self.get_section_size()
        # Get the offsets and determine iteration ranges based on direction
        x_offset, y_offset = CameraPlacementHelper.get_direction_offset(direction)

        if x_offset == 1:
            x_range = range(x_size - 1, -1, -1)
            y_range = range(y_size)
        if x_offset == -1:
            x_range = range(x_size)
            y_range = range(y_size - 1, -1, -1)

        if y_offset == 1:
            x_range = range(x_size - 1, -1, -1)
            y_range = range(y_size - 1, -1, -1)

        if y_offset == -1:
            x_range = range(x_size)
            y_range = range(y_size)

        # Determine the primary and secondary loop axes based on the direction
        primary_range = x_range if x_offset != 0 else y_range
        secondary_range = y_range if x_offset != 0 else x_range

        return primary_range, secondary_range, x_offset

    def choose_best_observation_point_connectivity(self, direction: Direction, check_camera_space: bool = False):
        """Update the connectivity matrix to choose the best observation point."""

        recast_checking_direct = CameraPlacementHelper.get_space_checking_direction(direction=direction)
        best_observation_index = -1
        best_observation_coordinate = None
        threshold_meter = CameraPlacementSettings.min_view_distance
        section_distance = CameraPlacementSettings.patch_size
        index_threshold = threshold_meter / section_distance

        primary_range, secondary_range, x_offset = self.get_iteration_order(direction=direction)
        for secondary in secondary_range:
            for primary in primary_range:

                enough_space = True
                x, y = (primary, secondary) if x_offset != 0 else (secondary, primary)

                if check_camera_space:
                    enough_space = self.has_enough_space(x, y, recast_checking_direct)

                # Skip inaccessible points
                if not self.is_point_accessible(x=x, y=y):
                    continue

                # Update observation index if the point is not focused
                if not self.is_point_focused(x=x, y=y, direction=direction) and enough_space:
                    curr_connectivity = self.get_point_connectivity(x=x, y=y, direction=direction)
                    current_observation_index = curr_connectivity
                    # use > to ensure that the first point gonna be recorded, instead of the last one
                    if current_observation_index > best_observation_index:
                        best_observation_index = current_observation_index
                        best_observation_coordinate = (x, y)

        # Check if the best observation meets the threshold; return None if it doesn't
        if best_observation_index == -1:
            return None

        if best_observation_index < index_threshold:
            return None

        return best_observation_coordinate

    def choose_best_observation_point_distance(self, direction: Direction, check_camera_space: bool = False):
        """choose the best observation points base on point to camera distance"""
        recast_checking_direct = CameraPlacementHelper.get_space_checking_direction(direction=direction)
        # Initialize the best observation index and coordinate
        best_observation_coordinate = None
        largest_distance_point = 0
        primary_range, secondary_range, x_offset = self.get_iteration_order(direction=direction)
        for secondary in secondary_range:
            for primary in primary_range:

                enough_space = True
                x, y = (primary, secondary) if x_offset != 0 else (secondary, primary)

                if check_camera_space:
                    enough_space = self.has_enough_space(x, y, recast_checking_direct)

                # Skip inaccessible points
                if not self.is_point_accessible(x=x, y=y):
                    continue

                # Update observation index if the point is not focused
                if not self.is_point_focused(x=x, y=y, direction=direction) and enough_space:
                    curr_connectivity = self.get_point_camera_distance(x=x, y=y, target_direction=direction)
                    if curr_connectivity > largest_distance_point:
                        largest_distance_point = curr_connectivity
                        best_observation_coordinate = (x, y)

        # Check if the best observation meets the threshold; return None if it doesn't
        return best_observation_coordinate

    def get_best_camera_in_the_direction(
        self, direction: Direction, camera_placement_mode: CameraPlacementMode, create_camera_directly=True
    ) -> None | dict:
        """Place one camera in the stage in required direction on the most ideal position"""
        # Initialize variables
        camera_info = {}

        # loop until we find out a valid camera position or run out of all the choice
        while True:
            # Find the best observation coordinate base on different requirments
            best_observation_coordinate = None
            if camera_placement_mode == CameraPlacementMode.Connectivity:
                best_observation_coordinate = self.choose_best_observation_point_connectivity(
                    direction=direction, check_camera_space=True
                )
            else:
                # if user choose to place camera base on point to camera distance
                best_observation_coordinate = self.choose_best_observation_point_distance(
                    direction=direction, check_camera_space=True
                )

            if best_observation_coordinate is None:
                carb.log_warn("Failed to pick a valid focus point for the camera. Please change the direction.")
                return None

            best_camera_info = None
            # Calculate the best camera position and rotation
            if camera_placement_mode == CameraPlacementMode.Connectivity:
                best_camera_info = self.get_best_camera_pose_connectivity(
                    direction=direction, focus_point=None, coordinate=best_observation_coordinate
                )
            else:
                # if user choose to place camera base on point to camera distance
                best_camera_info = self.get_best_camera_pose_distance(
                    direction=direction, focus_point=None, coordinate=best_observation_coordinate
                )

            # if camera could be placed with given focus point.
            if best_camera_info is not None:
                # Increment camera count and cache camera info
                camera_position = best_camera_info.camera_position
                focus_point = best_camera_info.focus_point
                if create_camera_directly:
                    camera_primpath = CameraGeneralUtil.spawn_camera(
                        spawn_location=camera_position, focus_point=focus_point
                    )
                    # get camera path from the generated camera prim
                    camera_info["camera_path"] = str(camera_primpath.GetPrimPath())

                camera_info["camera_position"] = camera_position
                camera_info["focus_point"] = focus_point
                return camera_info

    def get_total_camera_number(self):
        """get total camera number"""
        counter = 0
        for direction in Direction:
            camera_num = len(self.direction_to_camera_info_list[direction])
            counter = camera_num + counter
        return counter

    def calculate_simple_camera_coverage(
        self,
        camera_position,
        focus_point_position: Any | None = None,
        focus_point_coordinate: Optional[tuple[int, int]] = None,
    ):
        """calculate the point covered by camera, without considering about the coverage/direction"""
        if focus_point_position is None:
            # calculate the estimated focus point's height
            x, y = focus_point_coordinate
            focus_point_position = self.get_focus_point(x=x, y=y)

        # estimate the camera fov via the camera information
        camera_pos_np = np.array(camera_position)
        focus_point_np = np.array(focus_point_position)

        cast_vector = focus_point_np - camera_pos_np
        camera_dir = MathNumpyUtil.normalize_vector(cast_vector)
        # predict camera's fov information
        camera_fov_polygon = self.estimate_camera_fov(camera_position=camera_position, camera_dir=camera_dir)
        # calculate camera's coverage, ignore whether the point has already been coverged
        counter, covered_point_list = self.calculate_coverage(
            camera_position=camera_position,
            camera_polygon=camera_fov_polygon,
            signed_coverage=False,
            record_covered_coordate=True,
        )

        return covered_point_list

    def has_enough_number(self):
        """enough camera number in the stage"""
        # check whether total camera number is equal to the target number
        total_camera_limitation = CameraPlacementSettings.total_camera_number
        total_camera_number = self.get_total_camera_number()
        total_camera_number_reach = total_camera_limitation > 0 and (total_camera_number >= total_camera_limitation)
        return total_camera_number_reach

    def get_current_camera_coverage(self):
        """calculate and sign the coverage of existing cameras in the stage"""
        camera_prim_list = CameraGeneralUtil.get_target_camera_prims_under_root()
        camera_prim_path_list = [camera_prim.GetPrimPath() for camera_prim in camera_prim_list]
        for camera_path in camera_prim_path_list:
            # calculate the camera direction category
            camera_direction = CameraPlacementHelper.calculate_camera_direction(camera_path=camera_path)
            # calculate covered points and focus point coorindate in the stage
            covered_point_list, focus_point_position, camera_info = self.calculate_existing_camera_coverage(
                camera_path=camera_path
            )
            # mark covered points
            for point_cooridnate in covered_point_list:
                covered_x, covered_y = point_cooridnate
                self.mark_point_covered(x=covered_x, y=covered_y)

            # check whether existing camera's focus point is on our target scope:
            if focus_point_position[2] == self.focus_height:

                point_2d_projection = [focus_point_position[0], focus_point_position[0]]

                # check whether the focus point in the covered point
                if MathNumpyUtil.is_point_within_scope_nd(target_point=point_2d_projection, scope=self.stage_scope):
                    # mark focus points
                    focus_x, focus_y = self.calculate_point_coordinate(focus_point_position)
                    # mark focused points in the stage
                    self.mark_point_focused(x=focus_x, y=focus_y, direction=camera_direction)

            # record the camera information if the category
            self.direction_to_camera_info_list[camera_direction].append(camera_info)

        carb.log_warn("pre existed camera's coverage has been recorded")

    def calculate_existing_camera_coverage(self, camera_path: str):
        """estimate the camera fov in the stage"""
        stage = omni.usd.get_context().get_stage()
        camera_prim = stage.GetPrimAtPath(camera_path)
        image_width, image_height = 1920, 1080
        clipping_range = camera_prim.GetAttribute("clippingRange").Get()
        near_clip = clipping_range[0]
        horizontal_aperture = camera_prim.GetAttribute("horizontalAperture").Get()
        focal_length = camera_prim.GetAttribute("focalLength").Get()
        # get camera position information
        camera_info = {}
        camera_position = USDUtil.get_prim_pos(camera_prim)
        camera_dir = CameraUSDUtil.get_camera_forward_vector(camera_prim=camera_prim)
        # do not use the default camera parameter so that it can be compatible with any preset camera in the stage.
        camera_pos_np = np.array([camera_position[0], camera_position[1], camera_position[2]])
        camera_fov_polygon = SensorUtil.estimate_frustum_projection(
            camera_position=camera_pos_np,
            camera_dir=camera_dir,
            focal_length=focal_length,
            horizontal_aperture=horizontal_aperture,
            near_clip=near_clip,
            image_width=image_width,
            image_height=image_height,
            platform_height=self.focus_height,
            camera_fov_scope=200,
        )
        # calculate camera focus point on the target platform

        t, camera_focus_point = MathNumpyUtil.intersect_with_plane(
            start_point=camera_pos_np, vector=camera_dir, plane_height=self.focus_height
        )
        # if cannot find intersection on the platform
        if camera_focus_point is None:
            camera_focus_point = CameraUSDUtil.get_camera_focus_point(camera_prim=camera_prim)

        counter, covered_point_list = self.calculate_coverage(
            camera_position=camera_position,
            camera_polygon=camera_fov_polygon,
            signed_coverage=False,
            record_covered_coordate=True,
        )

        camera_info["camera_path"] = camera_path
        camera_info["camera_position"] = camera_pos_np
        camera_info["focus_point"] = camera_focus_point

        return covered_point_list, camera_focus_point, camera_info

    def record_point_to_camera_distance(self):
        """For each direction, calculate camera distance of each points in the stage"""
        for direction in Direction:
            camera_info_list = self.direction_to_camera_info_list[direction]
            for camera_info in camera_info_list:
                camera_position = camera_info["camera_position"]
                focus_point = camera_info["focus_point"]
                self.update_point_to_camera_distance(
                    camera_position=camera_position, direction=direction, focus_point_position=focus_point
                )

    def update_point_to_camera_distance(
        self, camera_position, direction, focus_point_position=None, focus_point_coordinate=None
    ):
        """update point to camera distance in the stage"""
        # get the character height and ground height:
        covered_point_list = self.calculate_simple_camera_coverage(
            camera_position=camera_position,
            focus_point_position=focus_point_position,
            focus_point_coordinate=focus_point_coordinate,
        )
        camera_pos_np = np.array([camera_position[0], camera_position[1], camera_position[2]])
        # for each point in camera fov, update the recorded point to camera value
        for point in covered_point_list:
            x, y = point
            point_pos_np = self.get_focus_point(x=x, y=y)
            distance = np.linalg.norm(camera_pos_np - point_pos_np)
            # calculate the point to camera distance
            current_camera_distance = self.get_point_camera_distance(x=x, y=y, target_direction=direction)
            if distance < current_camera_distance:
                self.set_point_camera_distance(x=x, y=y, target_value=distance, target_direction=direction)

    def estimate_camera_distance_update(
        self,
        camera_position,
        focus_point_position: Any = None,
        focus_point_coordinate: tuple | None = None,
        direction: Direction = Direction(0),
    ):
        """with new camera placed in the stage, calculate the reduce of point to camera distance sum"""
        camera_pos_np = np.array(camera_position)
        reduced_camera_distance_sum = 0
        # estimate the camera fov via the camera information
        covered_point_list = self.calculate_simple_camera_coverage(
            camera_position=camera_position,
            focus_point_position=focus_point_position,
            focus_point_coordinate=focus_point_coordinate,
        )
        # iterate through all point within the camera fov
        for point in covered_point_list:
            x, y = point
            point_pos_np = self.get_focus_point(x=x, y=y)
            distance = np.linalg.norm(camera_pos_np - point_pos_np)
            current_camera_distance = self.get_point_camera_distance(x=x, y=y, target_direction=direction)
            if distance < current_camera_distance:
                update = current_camera_distance - distance
                reduced_camera_distance_sum = reduced_camera_distance_sum + update

        return reduced_camera_distance_sum

    def place_camera_in_scope(
        self, consider_pre_exist_camera: Optional[bool] = True, create_camera_directly: Optional[bool] = True
    ):
        """start placing camera in the stage"""
        # place basic camera in the stage::
        # record the coverage of existing caemra in the stage
        if consider_pre_exist_camera:
            self.get_current_camera_coverage()
        carb.log_warn("Start generate cameras, ensure all the point have been covered!")
        self.coverage_based_camera_placement()
        # check whether refined camera is required:
        camera_number_limitation = CameraPlacementSettings.total_camera_number
        if camera_number_limitation > 0 and camera_number_limitation > self.get_total_camera_number():
            carb.log_warn("Start generate refine cameras, that is far more than need!")
            # record each point's point to camera distance
            self.record_point_to_camera_distance()
            self.proximity_based_camera_placement(create_camera_directly=create_camera_directly)
        self.cache_camera_data_as_json()
        pass

    def check_fully_coverage_ratio(self):
        """check whether coverage ratio reached"""
        target_coverage_ratio = CameraPlacementSettings.target_coverage_ratio
        x_size, y_size = self.get_section_size()

        fully_covered_counter = 0
        total_accessible_area = 0
        for x in range(x_size):
            for y in range(y_size):
                if self.is_point_accessible(x=x, y=y):
                    if self.is_point_fully_covered(x=x, y=y):
                        fully_covered_counter = fully_covered_counter + 1
                    total_accessible_area = total_accessible_area + 1

        if target_coverage_ratio <= fully_covered_counter / total_accessible_area:
            carb.log_warn("fully covered")
            return True

        return False

    def coverage_based_camera_placement(self, create_camera_directly=True):
        """place camera in the stage from all four direction, only consider the connectivity"""
        # iterate through all the direction
        coverage_delta_threshold = CameraPlacementSettings.min_coverage_increase
        # Minimum average improvement in coverage ratio to continue placement
        continue_camera_placement_in_direction: dict[Direction, bool] = (
            {}
        )  # whether certain direction has enough camera
        direction_to_coverage_deltas_dict: dict[Direction, list] = {}

        rolling_window_size = (
            5  # currently the rolling window is set to 3, this value should be customizable in the future
        )

        for direction in Direction:
            # set up coverage delta list for each direction
            continue_camera_placement_in_direction[direction] = True
            direction_to_coverage_deltas_dict[direction] = []

        current_direction = Direction.X_Positive

        finish_placement = False

        pre_exist_camera_num = self.get_total_camera_number()

        while not finish_placement:
            # check whether enough camera in the stage
            if self.has_enough_number():
                break

            # check whether there are enough camera in this direction.
            if continue_camera_placement_in_direction[current_direction]:
                previous_coverage = self.get_coveraged_sum_count()
                recent_coverage_deltas = direction_to_coverage_deltas_dict[current_direction]
                # place a camera in the stage: base one the dot's connectivity
                camera_info = self.get_best_camera_in_the_direction(
                    direction=current_direction,
                    camera_placement_mode=CameraPlacementMode.Connectivity,
                    create_camera_directly=create_camera_directly,
                )

                if camera_info is None:
                    continue_camera_placement_in_direction[current_direction] = False
                    carb.log_warn(f"Fail to place camera in direction {current_direction.name}. No valid focus point")
                    # continue # fail to put another camera in the space
                else:
                    index_of_camera = self.get_total_camera_number()

                    carb.log_warn(
                        f"place camera base on connectivity in stage. Direction : {current_direction.name} Index of camera  {str(index_of_camera)}"
                    )

                    camera_info_list = self.direction_to_camera_info_list[current_direction]
                    camera_info_list.append(camera_info)

                    new_coverage = self.get_coveraged_sum_count()
                    # update the coverage delta list,  ensure the sliding widow size
                    increased_coverage = new_coverage - previous_coverage
                    recent_coverage_deltas.append(increased_coverage)
                    if len(recent_coverage_deltas) > rolling_window_size:
                        recent_coverage_deltas.pop(0)

                    # Calculate average increase rate
                    average_increase_coverage = sum(recent_coverage_deltas) / len(recent_coverage_deltas)
                    # Check stopping conditions :: coverage increase ratio is too slow
                    if average_increase_coverage < coverage_delta_threshold:
                        carb.log_warn(
                            f"Direction: {str(current_direction)} Average coverage improvement {average_increase_coverage} below threshold. Stopping camera placement."
                        )
                        continue_camera_placement_in_direction[current_direction] = False

            # switch to the next direction
            current_direction = CameraPlacementHelper.get_next_direction(current_direction=current_direction)
            # check whether we can end the generation
            all_direction_enough = not (True in continue_camera_placement_in_direction.values())

            fully_covered = self.check_fully_coverage_ratio()

            finish_placement = all_direction_enough or fully_covered

        current_camera_num = self.get_total_camera_number()
        increased_camera = current_camera_num - pre_exist_camera_num

        carb.log_warn(f"Notice:: basic cameras have been placed: extra camera number { str(increased_camera) }")

    def proximity_based_camera_placement(self, create_camera_directly=True):
        """place camera in the stage from all four direction, consider the  camera distance"""
        # iterate through all the direction
        continue_camera_placement_in_direction: dict[Direction, bool] = (
            {}
        )  # whether certain direction has enough camera
        direction_to_distance_deltas_dict: dict[Direction, list] = {}
        rolling_window_size = (
            3  # currently the rolling window is set to 3, this value should be customizable in the future
        )
        distance_delta_threshold = (
            4  # stop the camera placement in certain direction if the decreased camera distance is less than this value
        )

        for direction in Direction:
            # set up coverage delta list for each direction
            continue_camera_placement_in_direction[direction] = True
            direction_to_distance_deltas_dict[direction] = []

        current_direction = Direction.X_Positive

        finish_placement = False

        pre_exist_camera_num = self.get_total_camera_number()

        while not finish_placement:
            # check whether there are enough camera in the stage
            if self.has_enough_number():
                break
            # check whether we still need to place camera in current direction:
            if continue_camera_placement_in_direction[current_direction]:
                # caclulate the previous camera distance sum
                previous_distance_sum = self.get_all_distance(direction=current_direction)
                recent_distance_deltas = direction_to_distance_deltas_dict[current_direction]
                # place a camera in the stage: base on each dot's camera distance
                camera_info = self.get_best_camera_in_the_direction(
                    direction=current_direction,
                    camera_placement_mode=CameraPlacementMode.CameraDistance,
                    create_camera_directly=create_camera_directly,
                )

                if camera_info is None:
                    continue_camera_placement_in_direction[current_direction] = False
                    # continue # fail to put another camera in the space
                else:
                    index_of_camera = self.get_total_camera_number()
                    carb.log_warn(
                        f"place camera base on connectivity in stage. Direction : {str(current_direction)} Index of camera  {str(index_of_camera)}"
                    )
                    camera_info_list = self.direction_to_camera_info_list[current_direction]
                    camera_info_list.append(camera_info)

                    # Calculate updated camera distance and improvement
                    new_distance_sum = self.get_all_distance(direction=current_direction)

                    # update the distance delta list,  ensure the sliding widow size
                    decreased_distance_sum = previous_distance_sum - new_distance_sum
                    recent_distance_deltas.append(decreased_distance_sum)
                    if len(recent_distance_deltas) > rolling_window_size:
                        recent_distance_deltas.pop(0)

                    # Calculate average increase rate
                    average_decrease_distance = sum(recent_distance_deltas) / len(recent_distance_deltas)
                    # Check stopping conditions :: distance increase ratio is too slow
                    if average_decrease_distance < distance_delta_threshold:
                        carb.log_info("Average camera distance improvement below threshold. Stopping camera placement.")
                        continue_camera_placement_in_direction[current_direction] = False

            # switch current direction to the next one
            current_direction = CameraPlacementHelper.get_next_direction(current_direction=current_direction)
            # check whether each direction have enough cameras
            all_direction_enough = not (True in continue_camera_placement_in_direction.values())
            finish_placement = all_direction_enough

        current_camera_num = self.get_total_camera_number()
        increased_camera = current_camera_num - pre_exist_camera_num

        carb.log_warn(f"Notice:: pruning cameras have been placed. increased camera number { str(increased_camera) }")

    def cache_camera_data_as_json(self):
        """cache camera position, camera category and camera's focus point as a json file"""
        camera_placement_output_folder_path = CameraPlacementSettings.camera_placement_output_folder_path
        carb.log_warn("----------Store Camera Information:-------- ")
        if not os.path.isdir(camera_placement_output_folder_path):
            carb.log_error(
                f"WARNING:: No valid root folder for camera placement output. Folder {camera_placement_output_folder_path} does not exist !"
            )
            return False

        camera_info_dict = self.direction_to_camera_info_list

        default_camera_info_file_name = "camera_info_payload.json"
        file_path = os.path.join(camera_placement_output_folder_path, default_camera_info_file_name)
        json_serializable_dict = JSONFileUtil.convert_to_json_serializable(camera_info_dict)
        JSONFileUtil.write_to_file(file_path=file_path, data=json_serializable_dict)

        carb.log_warn(
            f"WARNING:: Camera info payload has been cached. File {file_path} has been generated to store the info !"
        )
        for key in camera_info_dict.keys():
            carb.log_warn(f"WARNING:: Camera nums on each direction : {len(camera_info_dict[key])} .")

    def estimate_camera_fov(self, camera_position, camera_dir):
        """estimate the coverage of a camera's fov in the space"""
        default_camera_parameters = CameraPlacementUtils.default_camera_information()
        focal_length = default_camera_parameters["focal_length"]

        horizontal_aperture = default_camera_parameters["horizontal_aperture"]
        near_clip = default_camera_parameters["clip_distance"]

        image_width, image_height = default_camera_parameters["image_width"], default_camera_parameters["image_height"]

        platform_height = self.focus_height

        fov_polygon = SensorUtil.estimate_frustum_projection(
            camera_position=camera_position,
            camera_dir=camera_dir,
            focal_length=focal_length,
            horizontal_aperture=horizontal_aperture,
            near_clip=near_clip,
            image_width=image_width,
            image_height=image_height,
            platform_height=platform_height,
            camera_fov_scope=200,
        )

        return fov_polygon

    def get_validated_camera_poses(self, target_point: np.ndarray, target_direction: Direction):
        """get validated camera poses aroudn the target point"""
        (
            camera_height_range,
            camera_distance_range,
            look_down_angle_range,
        ) = CameraPlacementUtils.get_camera_info_setting()
        camera_distance_step_size = CameraPlacementSettings.camera_distance_step_size
        raycast_density = CameraPlacementSettings.raycast_density
        target_object_radius = CameraPlacementSettings.estimated_agent_radius
        yaw_range_list = CameraPlacementHelper.get_camera_placement_yaw_range(direction_category=target_direction)
        camera_on_navmesh = CameraPlacementSettings.camera_on_navmesh
        # get validated camera poses
        validated_camera_poses = SensorUtil.get_validated_camera_poses(
            target_point=target_point,
            target_object_radius=target_object_radius,
            camera_height_range=camera_height_range,
            camera_distance_range=camera_distance_range,
            look_down_angle_range=look_down_angle_range,
            yaw_range_list=yaw_range_list,
            raycast_density=raycast_density,
            camera_distance_step_size=camera_distance_step_size,
            scope=self.stage_scope,
            camera_on_navmesh=camera_on_navmesh,
        )
        return validated_camera_poses


    def place_camera_in_target_scope(self, target_scope: Optional[List[Tuple[int, int]]] = None):
        """place camera in the target scope"""
        if not CameraPlacementHelper.validate_scope(target_scope):
            carb.log_warn("Invalid stage scope, please check the scope value, attempt to fetch scope from the navmesh")
            target_scope = None

        if target_scope is None:
            if not GeneralSetting.need_navmesh_check:
                carb.log_warn("No target scope provided, navmesh is not available neither stage scope, plese check the input")
                return None
        # initialize the section status
        self.initialize_section_status(section_scope=target_scope)
        self.place_camera_in_scope()


    def place_camera_in_target_scope_v2(
        self,
        target_scope: List[Tuple[int, int]] = None,
        camera_look_down_angle_range: Optional[Tuple[float, float]] = None,
        camera_height_range: Optional[Tuple[float, float]] = None,
        camera_distance_range: Optional[Tuple[float, float]] = None,
        camera_num: Optional[int] = 10,
        required_camera_per_patch: Optional[int] = None,
        focus_platform_height: Optional[float] = None,
        target_section_distance: Optional[float] = None,
        consider_pre_exist_camera: Optional[bool] = True,
        spawn_camera: Optional[bool] = True,
        output_camera_data: Optional[bool] = True,
        restrict_camera_scope: Optional[bool] = True,
    ) -> List[Dict[str, Any]] | None:
        """
        Place camera to cover the target scope:
            target scope: target scope to place the camera
            format: [(x_min, x_max),(y_min, y_max)]
            camera_look_down_angle/camera_height_range/camera_distance_range:
            format: (min_look_down_angle, max_look_down_angle)
        """
        x_span_scale = abs(target_scope[0][1] - target_scope[0][0])
        y_span_scale = abs(target_scope[1][1] - target_scope[1][0])
        shorter_span = min(x_span_scale, y_span_scale)
        recommended_section_dist = shorter_span / 10
        # tuning the section distance base on the inputed scope.
        # ensure there are at least 10 section for each side.
        if target_section_distance is None or target_section_distance > recommended_section_dist:
            carb.log_warn(
                f"input section distance {target_section_distance} is too large, replace the patch size with {recommended_section_dist}"
            )
            target_section_distance = recommended_section_dist

        carb.log_warn(f"Camera placement target scope : {str(target_scope)} ")
        CameraPlacementSettings.patch_size = target_section_distance

        if required_camera_per_patch is not None:
            CameraPlacementSettings.required_camera_per_patch = required_camera_per_patch
        else:
            # if there is no specific camrea requirement, then we set the converage requirement to the same value as current camera num
            # ensure that each camera can obtain a relative large camera view scope within the stage.
            CameraPlacementSettings.required_camera_per_patch = camera_num

        if camera_look_down_angle_range is not None:
            min_camera_look_down_angle, max_camera_look_down_angle = camera_look_down_angle_range
            CameraPlacementSettings.min_camera_look_down_angle = min_camera_look_down_angle
            CameraPlacementSettings.max_camera_look_down_angle = max_camera_look_down_angle

        if camera_height_range is not None:
            min_camera_height, max_camera_height = camera_height_range
            CameraPlacementSettings.min_camera_height = min_camera_height
            CameraPlacementSettings.max_camera_height = max_camera_height
            carb.log_warn(
                "camera_height_range"
                + str([CameraPlacementSettings.min_camera_height, CameraPlacementSettings.max_camera_height])
            )

        if camera_distance_range is not None:
            min_camera_distance, max_camera_distance = camera_distance_range
            CameraPlacementSettings.min_camera_distance = min_camera_distance
            CameraPlacementSettings.max_camera_distance = max_camera_distance
            carb.log_warn(
                "camera_distance_range"
                + str([CameraPlacementSettings.min_camera_distance, CameraPlacementSettings.max_camera_distance])
            )
        # consider camera distance when estimate camera fov during placement.
        CameraPlacementSettings.limit_fov_by_distance = restrict_camera_scope
        # set the total camera num:
        CameraPlacementSettings.total_camera_number = camera_num
        # get the camera placement manager
        self.initialize_section_status(section_scope=target_scope, focus_height=focus_platform_height)
        self.place_camera_in_scope(
            consider_pre_exist_camera=consider_pre_exist_camera, create_camera_directly=spawn_camera
        )

        # if there is no need to extract the camera information
        if not output_camera_data:
            return None

        camera_info_cache = []
        for direction, camera_info_list in self.direction_to_camera_info_list.items():
            if camera_info_list:
                for camera_info in camera_info_list:
                    camera_position = camera_info.get("camera_position", None)
                    focus_point = camera_info.get("focus_point", None)
                    if camera_position is None or focus_point is None:
                        continue

                    # get camera rotation in quatf
                    camera_rotation = CameraPlacementUtils.get_camera_rotation_in_quatf(
                        camera_pos=camera_position, focus_point=focus_point
                    )
                    camera_info_dict = {}
                    camera_info_dict["translate"] = camera_position
                    camera_info_dict["rotation"] = camera_rotation
                    camera_info_cache.append(camera_info_dict)
        carb.log_info("Current target camera within the scope " + str(camera_info_cache))
        return camera_info_cache

    # NOTE:template function used to test the scope based camera placement
    def place_camera_in_scope_covered_by_prim(
        self,
        prim_path=None,
        camera_look_down_angle_range: Optional[Tuple[float, float]] = None,
        camera_height_range: Optional[Tuple[float, float]] = None,
        camera_distance_range: Optional[Tuple[float, float]] = None,
        camera_num: Optional[int] = 10,
        required_camera_per_patch: Optional[int] = None,
        focus_platform_height: Optional[float] = None,
        target_section_distance: Optional[float] = None,
        consider_pre_exist_camera: Optional[bool] = True,
        spawn_camera: Optional[bool] = True,
        output_camera_data: Optional[bool] = True,
        restrict_camera_scope: Optional[bool] = True,
    ):
        """visualize camera placement on target scope"""
        stage = omni.usd.get_context().get_stage()
        target_prim = stage.GetPrimAtPath(prim_path)
        box_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        bound = box_cache.ComputeWorldBound(target_prim)
        box_range = bound.ComputeAlignedBox()
        bboxMin = box_range.GetMin()
        bboxMax = box_range.GetMax()
        x_max, y_max = bboxMax[0], bboxMax[1]
        x_min, y_min = bboxMin[0], bboxMin[1]
        target_scope = [(x_min, x_max), (y_min, y_max)]
        self.place_camera_in_target_scope_v2(
            target_scope=target_scope,
            camera_distance_range=camera_distance_range,
            camera_look_down_angle_range=camera_look_down_angle_range,
            camera_height_range=camera_height_range,
            camera_num=camera_num,
            required_camera_per_patch=required_camera_per_patch,
            focus_platform_height=focus_platform_height,
            target_section_distance=target_section_distance,
            consider_pre_exist_camera=consider_pre_exist_camera,
            spawn_camera=spawn_camera,
            output_camera_data=output_camera_data,
            restrict_camera_scope=restrict_camera_scope,
        )
