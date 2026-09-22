import carb
from pxr import Gf, UsdGeom, Usd
import numpy as np
from isaacsim.sensors.rtx.placement.camera_placement.camera_placement_manager import (
    CameraPlacementManager,
)
from isaacsim.sensors.rtx.placement.camera_placement.camera_placement_helper import CameraPlacementHelper
from ..settings import CameraPlacementSettings
from .camera_cluster import CameraClusterHelper, CameraClusterManager
from ..utils import CameraGeneralUtil
from isaacsim.util.debug_draw import _debug_draw
import omni.usd
from typing import Tuple, List, Optional
import colorsys
from omni.ui import color as cl


draw = _debug_draw.acquire_debug_draw_interface()


class BaseColors:
    """A class to store predefined colors and generate distinguishable colors dynamically."""

    # Predefined base colors (RGBA format, 0-1 range)
    RED = (1, 0, 0, 1)
    GREEN = (0, 1, 0, 1)
    BLUE = (0, 0, 1, 1)
    YELLOW = (1, 1, 0, 1)
    CYAN = (0, 1, 1, 1)
    MAGENTA = (1, 0, 1, 1)

    # Ordered base color list for easy access
    BASE_COLOR_MAP = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA]

    @classmethod
    def generate_colors(cls, n: int):
        """
        Generate `n` distinguishable colors.
        - First, return predefined base colors.
        - If more colors are needed, generate them using HSV space.

        Args:
            n (int): Number of colors to generate.

        Returns:
            List[Tuple[float, float, float, float]]: List of colors in RGBA format (0-1 range).
        """
        colors = cls.BASE_COLOR_MAP[: min(n, len(cls.BASE_COLOR_MAP))]

        # Generate additional colors dynamically if needed
        for i in range(len(colors), n):
            hue = i / n  # Evenly distribute hues
            saturation = 0.7
            value = 0.9
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            colors.append((*rgb, 1))  # Convert to RGBA

        return colors

    @classmethod
    def get_base_colors(cls):
        """Returns all predefined base colors."""
        return cls.BASE_COLOR_MAP


def show_all_selected_camera_coverage(draw_camera_focus_point: Optional[bool] = True, target_scope: Optional[List[Tuple[float, float]]] = None):
    """
    Visualize the frequency of camera coverage in the stage.
    Points are displayed with colors representing coverage frequency.
    Points above the maximum coverage threshold are ignored.
    """
    # Acquire the debug draw interface
    draw = _debug_draw.acquire_debug_draw_interface()

    # Clear the stage
    draw.clear_points()
    draw.clear_lines()
    # Get camera coverage per patch requirement
    required_camera_per_patch = CameraPlacementSettings.required_camera_per_patch
    # Initialize variables
    covered_dots = [[] for _ in range(required_camera_per_patch + 1)]
    camera_placement_manager = CameraPlacementManager.get_instance()
    if not CameraPlacementHelper.validate_scope(target_scope):
        target_scope = None
    camera_placement_manager.initialize_section_status(section_scope=target_scope)
    x_size, y_size = camera_placement_manager.get_section_size()
    stage_section_matrix = camera_placement_manager.get_stage_section_matrix()

    # Template matrix to record point coverage
    camera_matrix = np.zeros((x_size, y_size), dtype=int)
    camera_prim_list = CameraGeneralUtil.get_target_camera_prims_under_root()
    camera_prim_path_list = [camera_prim.GetPrimPath() for camera_prim in camera_prim_list]
    # Get all selected prim list
    context = omni.usd.get_context()
    selected_prim_paths = context.get_selection().get_selected_prim_paths()
    selected_camera_list = list(filter(lambda x: x in selected_prim_paths, camera_prim_path_list))
    focus_point_list = []

    # Calculate coverage for each selected camera
    for camera_path in selected_camera_list:
        covered_point_list, focus_point_pos, _ = camera_placement_manager.calculate_existing_camera_coverage(
            camera_path=camera_path
        )

        focus_point_list.append(Gf.Vec3d(focus_point_pos.tolist()))

        for element in covered_point_list:
            x, y = element
            camera_matrix[x][y] = min(camera_matrix[x][y] + 1, required_camera_per_patch)

    # Generate distinguishable colors for coverage levels
    color_list = BaseColors.generate_colors(required_camera_per_patch)

    # Assign points to corresponding coverage bins
    min_coverage_count = 0
    fully_coverage_count = 0
    accessible_section_count = 0
    for x in range(x_size):
        for y in range(y_size):
            if not camera_placement_manager.is_point_accessible(x=x, y=y):
                continue

            accessible_section_count += 1
            dot_pos = stage_section_matrix[x][y]
            coverage_count = camera_matrix[x][y]

            if coverage_count > 0:
                min_coverage_count += 1
                covered_dots[coverage_count].append(Gf.Vec3d(dot_pos.tolist()))
                if coverage_count >= required_camera_per_patch:
                    fully_coverage_count += 1

    coverage_ratio = min_coverage_count / accessible_section_count
    fully_coverage_ratio = fully_coverage_count / accessible_section_count
    carb.log_warn(f"Current coverage ratio {str(coverage_ratio)}")
    carb.log_warn(f"Current full coverage ratio {str(fully_coverage_ratio)}")

    # Draw covered points for each coverage level
    for coverage_level in range(1, required_camera_per_patch + 1):
        if covered_dots[coverage_level]:
            draw.draw_points(
                covered_dots[coverage_level],
                [color_list[coverage_level - 1]] * len(covered_dots[coverage_level]),
                [10] * len(covered_dots[coverage_level]),
            )

    if draw_camera_focus_point:
        draw.draw_points(focus_point_list, [BaseColors.GREEN] * len(focus_point_list), [20] * len(focus_point_list))


def clean_the_stage():
    """clean the visualization"""
    draw = _debug_draw.acquire_debug_draw_interface()
    draw.clear_points()
    draw.clear_lines()


def get_camera_cluster(n=3, start_index=0, max_iteration=1000, target_scope: Optional[List[Tuple[float, float]]] = None):
    """test camera fov estimate and visualize the result"""
    cluster_manager = CameraClusterManager.get_instance()
    clustered_camera_list = cluster_manager.cluster_camera_in_stage(n, start_index, max_iteration, target_scope)
    carb.log_warn("Current cluster_camera_list" + str(list(clustered_camera_list)))
    return clustered_camera_list


def visualize_camera_cluster(clustered_camera_list, target_cluster_index, color, target_scope: Optional[List[Tuple[float, float]]] = None):
    """visualize camera cluster with target cluster index as input."""

    draw = _debug_draw.acquire_debug_draw_interface()
    # remove other visualization
    draw.clear_points()
    draw.clear_lines()
    target_camera_path_list = []
    camera_prim_list = CameraGeneralUtil.get_target_camera_prims_under_root()
    camera_prim_path_list = [camera_prim.GetPrimPath() for camera_prim in camera_prim_list]
    camera_placement_manager = CameraPlacementManager.get_instance()
    if not CameraPlacementHelper.validate_scope(target_scope):
        target_scope = None
    camera_placement_manager.initialize_section_status(section_scope=target_scope)
    stage_section_matrix = camera_placement_manager.get_stage_section_matrix()

    for i in range(len(camera_prim_path_list)):
        if clustered_camera_list[i] == target_cluster_index:
            target_camera_path_list.append(camera_prim_path_list[i])

    x_size, y_size = camera_placement_manager.get_section_size()
    camera_matrix = np.zeros((x_size, y_size), dtype=int)
    center_point_list = []

    for camera_path in target_camera_path_list:
        covered_point_list, _, _ = camera_placement_manager.calculate_existing_camera_coverage(camera_path=camera_path)
        for element in covered_point_list:
            x, y = element
            camera_matrix[x][y] = 1

        # calculate the center point of the camera FOV cluster
        center_x, center_y = tuple(map(int, np.mean(covered_point_list, axis=0)))
        center_point = stage_section_matrix[center_x][center_y]
        center = Gf.Vec3d(center_point.tolist())
        center_point_list.append(center)

    covered_dot = []

    for x in range(x_size):
        for y in range(y_size):
            visited = camera_matrix[x][y] == 1
            dot_pos = stage_section_matrix[x][y]
            if visited:
                covered_dot.append(Gf.Vec3d(dot_pos.tolist()))

    # draw the point covered by camera fov
    draw.draw_points(covered_dot, [color] * len(covered_dot), [10] * len(covered_dot))
    # draw the center point
    draw.draw_points(center_point_list, [BaseColors.YELLOW] * len(center_point_list), [30] * len(center_point_list))


def visualize_camera_placement_on_targetscope(target_scope: Optional[List[Tuple[float, float]]] = None, prim_path=None):
    """visualize camera cluster with target cluster index as input."""
    draw = _debug_draw.acquire_debug_draw_interface()
    # remove other visualization
    draw.clear_points()
    draw.clear_lines()

    camera_placement_manager = CameraPlacementManager.get_instance()
    if target_scope is None:
        stage = omni.usd.get_context().get_stage()
        target_prim = stage.GetPrimAtPath(prim_path)
        box_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        bound = box_cache.ComputeWorldBound(target_prim)
        box_range = bound.ComputeAlignedBox()
        bboxMin = box_range.GetMin()
        bboxMax = box_range.GetMax()
        x_max, y_max, z_max = bboxMax[0], bboxMax[1], bboxMax[2]
        x_min, y_min, z_min = bboxMin[0], bboxMin[1], bboxMin[2]

    target_scope = [(x_min, x_max), (y_min, y_max)]
    camera_placement_manager.initialize_section_status(section_scope=target_scope, focus_height=0.3)
    camera_placement_manager.place_camera_in_scope()
    x_size, y_size = camera_placement_manager.get_section_size()
    camera_matrix = np.zeros((x_size, y_size), dtype=int)
    camera_prim_list = CameraGeneralUtil.get_target_camera_prims_under_root()
    camera_prim_path_list = [camera_prim.GetPrimPath() for camera_prim in camera_prim_list]
    stage_section_matrix = camera_placement_manager.get_stage_section_matrix()
    for camera_path in camera_prim_path_list:
        covered_point_list, _, _ = camera_placement_manager.calculate_existing_camera_coverage(camera_path=camera_path)
        for element in covered_point_list:
            x, y = element
            camera_matrix[x][y] = 1

    covered_dot = []
    uncovered_dot = []
    for x in range(x_size):
        for y in range(y_size):
            visited = camera_matrix[x][y] == 1
            dot_pos = stage_section_matrix[x][y]
            if visited:
                covered_dot.append(Gf.Vec3d(dot_pos.tolist()))
            else:
                uncovered_dot.append(Gf.Vec3d(dot_pos.tolist()))

    draw.draw_points(covered_dot, [BaseColors.RED] * len(covered_dot), [10] * len(covered_dot))
    draw.draw_points(uncovered_dot, [BaseColors.GREEN] * len(uncovered_dot), [10] * len(uncovered_dot))
