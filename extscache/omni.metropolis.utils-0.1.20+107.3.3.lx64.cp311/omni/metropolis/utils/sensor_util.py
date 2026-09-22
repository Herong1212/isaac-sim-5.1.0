import omni.kit.mesh.raycast
from omni.metropolis.utils.geomtry_util import GeomtryUtil
from omni.metropolis.utils.math_util import MathNumpyUtil
from omni.metropolis.utils.carb_util import CarbUtil
from omni.metropolis.utils.usd_util import USDUtil, CameraUSDUtil
from omni.metropolis.utils.simulation_util import SimulationUtil
import carb
import math
from typing import List, Tuple, Optional, Union, Dict, Any
from omni.syntheticdata.scripts import helpers, sensors
from dataclasses import dataclass, field
import numpy as np
from pxr import UsdGeom, Usd, Gf, Sdf


@dataclass
class CameraPose:
    """
    Represents the pose of a camera, including its position, direction, and focus point.

    All values are stored as NumPy arrays for consistency and vector operations.

    Attributes:
        camera_position (np.ndarray): 3D position of the camera.
        camera_direction (np.ndarray): 3D unit direction vector.
        focus_point (np.ndarray): 3D focus point in world space.
    """

    camera_position: Union[List[float], np.ndarray] = field(default_factory=lambda: np.zeros(3))
    camera_direction: Union[List[float], np.ndarray] = field(default_factory=lambda: np.zeros(3))
    focus_point: Union[List[float], np.ndarray] = field(default_factory=lambda: np.zeros(3))

    def __post_init__(self):
        self.camera_position = np.array(self.camera_position, dtype=np.float32)
        self.camera_direction = np.array(self.camera_direction, dtype=np.float32)
        self.focus_point = np.array(self.focus_point, dtype=np.float32)

    def __eq__(self, other):
        if not isinstance(other, CameraPose):
            return False
        return (
            np.allclose(self.camera_position, other.camera_position)
            and np.allclose(self.camera_direction, other.camera_direction)
            and np.allclose(self.focus_point, other.focus_point)
        )

    def __hash__(self):
        return hash(
            (
                tuple(np.round(self.camera_position, 5)),
                tuple(np.round(self.camera_direction, 5)),
                tuple(np.round(self.focus_point, 5)),
            )
        )


@dataclass
class RaycastContainer:
    """RayCast Container

    Attributes:
        cast_position: position of the focus point
        cast_dir: direction of the raycast
        min_distance: min_distance between camera and object
        max_distance: max_distance between camera and object
    """

    cast_position: tuple
    cast_dir: tuple
    min_distance: float
    max_distance: float


class SensorUtil:
    """sensor related functions a assistan sensor placement and analysis"""

    MINMUM_CAMERA_SPACE = 1

    @classmethod
    def get_pitch_range(
        cls,
        focus_height: float,
        target_object_radius: float,
        camera_height_range: tuple[float],
        camera_distance_range: tuple[float],
        look_down_angle_range: tuple[float],
    ):
        """calculate angle limitation from the max/min camera distance and height"""

        min_camera_height, max_camera_height = camera_height_range
        min_angle, max_angle = look_down_angle_range
        min_camera_distance, max_camera_distance = camera_distance_range
        character_radius = target_object_radius
        max_sin_value = (max_camera_height - focus_height) / (min_camera_distance + character_radius)
        min_sin_value = (min_camera_height - focus_height) / (max_camera_distance + character_radius)

        if max_sin_value > 1:
            max_sin_value = 1

        if max_sin_value < 0 or min_sin_value < 0:
            carb.log_error(
                "Camera should not be lower than character : please reset max/min_camrea_height, people_focus_height or max/min_camera_distance"
            )
            return

        if min_sin_value > 1:
            carb.log_error(
                "Aim Camera to Character received Invalid input : please reset max/min_camrea_height, people_focus_height or max/min_camera_distance"
            )
            return

        # calculate radius angle limitation
        max_angle_in_radians = math.asin(max_sin_value)
        min_angle_in_radians = math.asin(min_sin_value)

        # calculate camera look down angle limitation in degree
        max_angle_in_degrees = min(math.degrees(max_angle_in_radians), max_angle, 90)
        min_angle_in_degrees = max(math.degrees(min_angle_in_radians), min_angle, 0)

        # get the pitch range
        pitch_range = (min_angle_in_degrees, max_angle_in_degrees)
        return pitch_range

    @classmethod
    def get_validated_observation_direction(
        cls,
        target_point: np.ndarray,
        target_object_radius: float,
        camera_height_range: tuple[float],
        camera_distance_range: tuple[float],
        look_down_angle_range: tuple[float],
        yaw_range_list: list[tuple[float]],
        raycast_density,
    ):
        """get best observation point with limited camera position"""
        min_camera_height, max_camera_height = camera_height_range
        focus_height = target_point[2]
        min_camera_distance, max_camera_distance = camera_distance_range
        character_radius = target_object_radius
        raycast = omni.kit.mesh.raycast.get_mesh_raycast_interface()
        # calculate angle limitation from the max/min camera distance and height
        pitch_range = cls.get_pitch_range(
            focus_height=focus_height,
            target_object_radius=target_object_radius,
            camera_height_range=camera_height_range,
            camera_distance_range=camera_distance_range,
            look_down_angle_range=look_down_angle_range,
        )

        # store ray cast direction
        ray_direction_list = []
        result = []
        # use list to store yaw range, handle the edge case when range need to pass x axis
        for yaw_range in yaw_range_list:
            # generate raycast uniformly around the center point
            ray_direction_sub_list = []
            # check whether the range is so narrow that the fibonacci algo cannot be applied
            ray_direction_sub_list = GeomtryUtil.fibonacci_sphere_directions(
                pitch_range=pitch_range, yaw_range=yaw_range, num_points=raycast_density
            )

            ray_direction_list.extend(ray_direction_sub_list)

        for ray_direction in ray_direction_list:
            # clip the distance according to camera height's limitation
            clipped_distance_range = cls.get_validated_observation_distance(
                camera_height_range=camera_height_range,
                camera_distance_range=camera_distance_range,
                unit_vector=ray_direction,
                focus_height=focus_height,
                character_radius=character_radius,
            )

            if clipped_distance_range is None:
                continue

            clipped_min_distance, clipped_max_distance = clipped_distance_range

            min_distance = character_radius + clipped_min_distance
            max_distance = character_radius + clipped_max_distance

            # get the ray cast point around our target point
            raycast.set_bvh_refresh_rate(omni.kit.mesh.raycast.BvhRefreshRate.FAST, True)
            # calculate the ray cast distance
            ray_length = max_camera_distance + 1 + character_radius
            hit_result = raycast.closestRaycast(target_point, ray_direction, ray_length)

            if hit_result:
                meshIndex = hit_result.meshIndex
                position = hit_result.position
            else:
                continue

            # when raycast hit nothing: it means that there are enough space for camera.
            if meshIndex == -1:
                # add raycast to valid raycast list
                result.append(
                    RaycastContainer(
                        cast_position=target_point,
                        cast_dir=ray_direction,
                        min_distance=min_distance,
                        max_distance=max_distance,
                    )
                )
            else:
                hit_pos_np = np.array([position[0], position[1], position[2]])
                ## get the distance between raycast dot and the closest object on that direction
                hit_dist = np.linalg.norm(target_point - hit_pos_np)
                camera_dist = hit_dist - 0.7
                calulated_camera_pos = target_point + ray_direction * hit_dist
                ## check whether there are enough space for cameraa
                if camera_dist >= (min_camera_distance + character_radius) and calulated_camera_pos[2] >= (
                    min_camera_height
                ):
                    max_distance = min(camera_dist, max_distance)
                    if min_distance > max_distance:
                        continue
                    # add raycast to valid raycast list
                    result.append(
                        RaycastContainer(
                            cast_position=target_point,
                            cast_dir=ray_direction,
                            min_distance=min_distance,
                            max_distance=max_distance,
                        )
                    )
        return result

    @classmethod
    def get_validated_observation_distance(
        cls,
        camera_height_range: tuple[float],
        camera_distance_range: tuple[float],
        unit_vector,
        focus_height: float,
        character_radius: float,
    ):
        """check whether current observation direction is valid"""

        min_camera_height, max_camera_height = camera_height_range
        min_camera_distance, max_camera_distance = camera_distance_range

        # check whether the larget distance can stasify the height requirement

        # Calculate distance needed to reach max camera height boundary
        if unit_vector[2] != 0:  # Avoid division by zero
            distance_for_max_height = (max_camera_height - focus_height) / unit_vector[2] - character_radius
            distance_for_min_height = (min_camera_height - focus_height) / unit_vector[2] - character_radius
            # Validate that these distances fall within the allowable camera distance range
            # NOTE:: less restrict value is applied.
            if distance_for_min_height >= max_camera_distance:
                return None

            if distance_for_max_height <= min_camera_distance:
                return None

            min_distance = max(distance_for_min_height, min_camera_distance)
            max_distance = min(distance_for_max_height, max_camera_distance)
            return (min_distance, max_distance)
        else:
            # handle the case when the camera parallel to the ground
            if max_camera_height == min_camera_height == focus_height:
                return (min_camera_distance, max_camera_distance)
            else:
                return None

    @classmethod
    def get_camera_poses_on_direction(
        cls,
        raycast_info_list: list[RaycastContainer],
        camera_distance_step_size: float,
        scope: Optional[List[Tuple[float, float]]] = None,
        camera_on_navmesh: Optional[bool] = False,
    ):
        """check whether the observation position is validate"""
        camera_pos_collection: list[CameraPose] = []

        for raycast_info in raycast_info_list:
            cast_point = raycast_info.cast_position
            cast_direction = raycast_info.cast_dir
            min_distance = raycast_info.min_distance
            max_distance = raycast_info.max_distance

            # help me generate a list of distance value, from min distance to max distance, increase by camera step in each step, include the  max and min distance in the list
            distance_value_list = MathNumpyUtil.split_range_with_step(
                min_value=min_distance, max_value=max_distance, step_size=camera_distance_step_size
            )

            for distance in distance_value_list:
                # calculate the camera translate matched with the distance value
                potential_camera_pos = cast_point + distance * cast_direction
                # check whether camera need to be set on navmesh
                if camera_on_navmesh:
                    if not SimulationUtil.validate_navmesh_point_2d(potential_camera_pos):
                        continue
                # check whether camera need to be generated in certain scope .
                if scope is not None:
                    # we only check whether the projection of the camera is within the scope .
                    if not MathNumpyUtil.is_point_within_scope_nd(
                        target_point=potential_camera_pos, scope=scope, dimension=2
                    ):
                        continue

                # camera aimming at the reverse direction of the cast point
                camera_dir = -1 * MathNumpyUtil.normalize_vector(cast_direction)
                camera_pos_info = CameraPose(
                    camera_position=potential_camera_pos,
                    camera_direction=camera_dir,
                    focus_point=cast_point,
                )
                camera_pos_collection.append(camera_pos_info)

        return camera_pos_collection

    @classmethod
    def estimate_frustum_projection(
        cls,
        camera_position: np.ndarray,
        camera_dir: np.ndarray,
        near_clip: float,
        image_width: int,
        image_height: int,
        fx: Optional[float] = None,
        fy: Optional[float] = None,
        cx: Optional[float] = None,
        cy: Optional[float] = None,
        focal_length: Optional[float] = None,
        horizontal_aperture: Optional[float] = None,
        camera_fov_scope: float = 200,
        platform_height: float = 0,
    ):
        """
        Calculate the intersection of the camera frustum with the ground plane (z=platform_height) using intrinsic parameters.

        Parameters:
        camera_position (numpy.ndarray): 3D position of the camera in world space (x, y, z).
        camera_dir (numpy.ndarray): Normalized direction vector of the camera pointing in its forward direction.
        near_clip (float): Distance to the near clipping plane.
        fx, fy (float): Focal lengths in x and y directions, respectively.
        cx, cy (float): Principal point offsets in pixels in x and y directions, respectively.
        image_width (int): Width of the image sensor or image in pixels.
        image_height (int): Height of the image sensor or image in pixels.

        Returns:
        dict: Dictionary containing the ground plane intersection points (top-left, top-right, bottom-left, bottom-right).
        """

        def calculate_camera_frustrum_intersection(vector, point):
            """Handle Edge Case: The camera's frustrum does not intersect with ground plane"""
            if point is None:
                vector_2d = np.array([vector[0], vector[1], 0])
                unit_dir = MathNumpyUtil.normalize_vector(vector_2d)
                point = (
                    np.array([camera_position[0], camera_position[1], platform_height]) + unit_dir * camera_fov_scope
                )
            return point

        if focal_length is not None and horizontal_aperture is not None:

            # calculate the camera intrinsic information with a different way.
            aspect_ratio = image_width / image_height
            pinhole_ratio = 2 * focal_length * image_width / image_height / horizontal_aperture
            fx = image_width * pinhole_ratio / aspect_ratio / 2
            fy = image_height * pinhole_ratio / 2
            cx = image_width / 2
            cy = image_height / 2

        # Calculate half-width and half-height of the near plane in world units
        half_width = abs((near_clip / fx) * (cx if cx != 0 else image_width / 2))
        half_height = abs((near_clip / fy) * (cy if cy != 0 else image_height / 2))
        forward, right, up = USDUtil.compute_orthonormal_basis(camera_dir)

        top_right_dir = MathNumpyUtil.normalize_vector((half_width * right) + (half_height * up) + near_clip * forward)
        top_left_dir = MathNumpyUtil.normalize_vector((-half_width * right) + (half_height * up) + near_clip * forward)
        bottom_right_dir = MathNumpyUtil.normalize_vector(
            (half_width * right) + (-half_height * up) + near_clip * forward
        )
        bottom_left_dir = MathNumpyUtil.normalize_vector(
            (-half_width * right) + (-half_height * up) + near_clip * forward
        )

        # Project the near plane corners onto the ground plane
        _, top_right = MathNumpyUtil.intersect_with_plane(
            start_point=camera_position, vector=top_right_dir, plane_height=platform_height
        )
        _, top_left = MathNumpyUtil.intersect_with_plane(
            start_point=camera_position, vector=top_left_dir, plane_height=platform_height
        )

        _, bottom_right = MathNumpyUtil.intersect_with_plane(
            start_point=camera_position, vector=bottom_right_dir, plane_height=platform_height
        )
        _, bottom_left = MathNumpyUtil.intersect_with_plane(
            start_point=camera_position, vector=bottom_left_dir, plane_height=platform_height
        )

        top_right = calculate_camera_frustrum_intersection(top_right_dir, top_right)
        top_left = calculate_camera_frustrum_intersection(top_left_dir, top_left)
        bottom_right = calculate_camera_frustrum_intersection(bottom_right_dir, bottom_right)
        bottom_left = calculate_camera_frustrum_intersection(bottom_left_dir, bottom_left)

        # return the intersection of camera's frstum on the ground

        result = {
            "top_left": top_left,
            "top_right": top_right,
            "bottom_left": bottom_left,
            "bottom_right": bottom_right,
        }
        return result

    @classmethod
    def get_validated_camera_poses(
        cls,
        target_point: np.ndarray,
        target_object_radius: float,
        camera_height_range: tuple[float],
        camera_distance_range: tuple[float],
        look_down_angle_range: tuple[float],
        yaw_range_list: list[tuple[float]],
        raycast_density: float,
        camera_distance_step_size: float,
        scope: Optional[List[Tuple[float, float]]] = None,
        camera_on_navmesh: Optional[bool] = False,
    ):
        """encapsulated method, find valid camera position base on preset requirments"""
        # get raycast list around target point
        raycast_info_list = cls.get_validated_observation_direction(
            target_point=target_point,
            target_object_radius=target_object_radius,
            camera_height_range=camera_height_range,
            camera_distance_range=camera_distance_range,
            look_down_angle_range=look_down_angle_range,
            yaw_range_list=yaw_range_list,
            raycast_density=raycast_density,
        )

        # get validated camera pose around the target point
        validated_camera_pos_info = cls.get_camera_poses_on_direction(
            raycast_info_list=raycast_info_list,
            scope=scope,
            camera_on_navmesh=camera_on_navmesh,
            camera_distance_step_size=camera_distance_step_size,
        )

        return validated_camera_pos_info

    @staticmethod
    def reformat_camera_params(camera_params: Dict[str, Any]) -> Dict[str, Any]:
        """helper method to reformat the camera params array"""

        projection_type = camera_params["cameraModel"]
        world_to_view = np.reshape(camera_params["cameraViewTransform"], (4, 4))
        view_to_world = np.linalg.inv(world_to_view)
        width, height = camera_params["renderProductResolution"][0], camera_params["renderProductResolution"][1]
        if projection_type == "fisheyePolynomial":
            ftheta = {
                "width": camera_params["cameraFisheyeNominalWidth"],
                "height": camera_params["cameraFisheyeNominalHeight"],
                "cx": camera_params["cameraFisheyeOpticalCentre"][0],
                "cy": camera_params["cameraFisheyeOpticalCentre"][1],
                "poly_a": camera_params["cameraFisheyePolynomial"][0],
                "poly_b": camera_params["cameraFisheyePolynomial"][1],
                "poly_c": camera_params["cameraFisheyePolynomial"][2],
                "poly_d": camera_params["cameraFisheyePolynomial"][3],
                "poly_e": camera_params["cameraFisheyePolynomial"][4],
                "poly_f": camera_params["cameraFisheyePolynomial"][5],
                "max_fov": camera_params["cameraFisheyeMaxFOV"],
            }
            ftheta["edge_fov"] = helpers.ftheta_distortion(ftheta, ftheta["width"] / 2)
            ftheta["c_ndc"] = np.array(
                [
                    (ftheta["cx"] - ftheta["width"] / 2) / ftheta["width"],
                    (ftheta["height"] / 2 - ftheta["cy"]) / ftheta["width"],
                ]
            )
        else:
            ftheta = None

        view_params = {
            "view_to_world": np.array(view_to_world),
            "world_to_view": np.array(world_to_view),
            "projection_type": projection_type,
            "ftheta": ftheta,
            "width": width,
            "height": height,
            "aspect_ratio": width / height,
            "clipping_range": camera_params["cameraNearFar"],
            "horizontal_aperture": camera_params["cameraAperture"][0],
            "focal_length": camera_params["cameraFocalLength"],
            "cameraProjection": np.reshape(camera_params["cameraProjection"], (4, 4)),
            "renderProductResolution": camera_params["renderProductResolution"],
        }

        return view_params

    @staticmethod
    def get_camera_intrinsic_dict(camera_params: Dict[str, Any]):
        """get camera intrinsic information"""
        intrinsic_matrix = SensorUtil.calculate_3x3_intrinsic_matrix(camera_params=camera_params)
        return {
            "fx": intrinsic_matrix[0][0],
            "fy": intrinsic_matrix[1][1],
            "cx": intrinsic_matrix[0][2],
            "cy": intrinsic_matrix[1][2],
        }

    @staticmethod
    def compute_camera_projection_matrix(three_d_points: List[float], two_d_points: List[float]):
        # Ensure the points are in the correct shape
        three_d_points = np.array(three_d_points, dtype=np.float64)
        two_d_points = np.array(two_d_points, dtype=np.float64)

        num_points = three_d_points.shape[0]
        A = []

        for i in range(num_points):
            X, Y, Z = three_d_points[i, :]
            x, y = two_d_points[i, :]
            A.append([-X, -Y, -Z, -1, 0, 0, 0, 0, x * X, x * Y, x * Z, x])
            A.append([0, 0, 0, 0, -X, -Y, -Z, -1, y * X, y * Y, y * Z, y])

        A = np.array(A)
        U, S, Vh = np.linalg.svd(A)
        L = Vh[-1, :] / Vh[-1, -1]  # Normalize

        camera_projection_matrix = L.reshape(3, 4)
        return camera_projection_matrix

    @staticmethod
    def compute_homography_matrix(proj_matrix: np.ndarray, platform_height: float = 0):
        """
        Computes the homography matrix H from a given 3x4 projection matrix P and plane height h.

        Args:
            P (numpy.ndarray): 3x4 projection matrix.
            h (float): Height of the plane Z = h.

        Returns:
            numpy.ndarray: 3x3 homography matrix H.
        """
        if proj_matrix.shape != (3, 4):
            raise ValueError("Projection matrix P must be of shape (3,4)")

        # Extract columns
        P1, P2, P3, P4 = proj_matrix[:, 0], proj_matrix[:, 1], proj_matrix[:, 2], proj_matrix[:, 3]

        # Compute homography matrix H
        H = np.column_stack([P1, P2, P3 * platform_height + P4])  # Equivalent to [P1 P2 (P3*h + P4)]

        return H

    @staticmethod
    def calculate_3x4_extrinsic_matrix(camera_params: Dict[str, Any]):
        """calculate the extrinsic matrix from camera params"""
        cam_extrinsics = None
        if "world_to_view" in camera_params:
            cam_extrinsics = np.asarray(camera_params["world_to_view"]).reshape(4, 4).T
        elif "cameraViewTransform" in camera_params:
            cam_extrinsics = np.asarray(camera_params["cameraViewTransform"]).reshape(4, 4).T
        else:
            return None
        cam_extrinsics[1, :] = -cam_extrinsics[1, :]
        cam_extrinsics[2, :] = -cam_extrinsics[2, :]
        extrinsics_3x4 = cam_extrinsics[:3, :]
        return extrinsics_3x4

    @staticmethod
    def calculated_3x4_projection_matrix(intrinsic: np.ndarray, extrinsinc: np.ndarray):
        """calculate the projection matrix"""
        projection_matrix = intrinsic @ extrinsinc
        return projection_matrix

    @staticmethod
    def calculate_3x3_intrinsic_matrix(camera_params: Dict[str, Any]):
        """reformat the camera intrinsic metadata generate the intrisic matrix"""
        if "cameraProjection" in camera_params and "renderProductResolution" in camera_params:
            image_width, image_height = tuple(camera_params["renderProductResolution"])
            camera_intrinsics = np.asarray(camera_params["cameraProjection"]).reshape(4, 4).T
            camera_intrinsics[0, 2] = 1
            camera_intrinsics[1, 2] = 1
            camera_intrinsics[0, :] *= image_width / 2
            camera_intrinsics[1, :] *= image_height / 2
            camera_intrinsics = camera_intrinsics[:3, :3]
            camera_intrinsics[2, 2] = 1
            return camera_intrinsics
        else:
            return None

    @staticmethod
    def world_to_image_helper(points: List, view_params: Dict[str, Any]):
        """helper method to project point in 3d space to 2d image coordinate"""
        projected = helpers.world_to_image(viewport=None, points=points, view_params=view_params)
        # get the projected point in space
        proj_i2w = projected
        # calculate the 2d image coordinate.
        projected_xy = projected[..., :2]
        projected_xy[..., 0] *= view_params["width"]
        projected_xy[..., 1] *= view_params["height"]
        return projected_xy.astype(int)

    @staticmethod
    def project_3d_to_2d_persp(points: List, camera_params: Dict[str, Any]):
        """Convert the 3D points to 2D image coordinates using perspective projection."""
        try:
            if points is None or len(points) == 0:
                return None, None

            # Ensure 'points' is a NumPy array
            image_points = SensorUtil.world_to_image_helper(points=points, view_params=camera_params)
            # Create a boolean mask for valid points within image boundaries
            condition = (
                (image_points[:, 0] > 0)
                & (image_points[:, 0] < camera_params["width"])
                & (image_points[:, 1] > 0)
                & (image_points[:, 1] < camera_params["height"])
            )

            # Preserve length by using None for invalid points
            processed_points = [p.tolist() if cond else None for p, cond in zip(points, condition)]
            processed_image_points = [ip.tolist() if cond else None for ip, cond in zip(image_points, condition)]

            return processed_points, processed_image_points

        except Exception as e:
            print(f"Error in project_3d_to_2d_persp: {e}")
            return None, None

    @staticmethod
    def project_3d_to_2d_ortho(
        points: List,
        screen_width: int = 1920,
        screen_height: int = 1080,
        camera_path: Optional[Union[str, Sdf.Path]] = None,
        camera_prim: Optional[Usd.Prim] = None,
        stage=None,
        enable_boundary_check: bool = True,  # New parameter with default True (boundary check ON)
    ):
        """Project a 3D point from world coordinate to image coordinate with an orthographic camera."""

        def world_to_image_space(camera_view_matrix, hA, point, screen_width=1920, screen_height=1080):
            homo_point_translate = np.array([point[0], point[1], point[2], 1])
            # Convert point into camera space
            camera_space_translate = homo_point_translate @ camera_view_matrix
            screen_projection = (
                (1 + camera_space_translate[0] / hA * 20) * screen_width / 2,
                (1 - camera_space_translate[1] / hA * 20 * screen_width / screen_height) * screen_height / 2,
            )
            return screen_projection

        # Get the horizontal aperture from the camera prim
        if camera_prim is None:
            if stage is None:
                stage = omni.usd.get_context().get_stage()
            camera_prim = stage.GetPrimAtPath(camera_path)

        hA = camera_prim.GetAttribute("horizontalAperture").Get()
        # Get camera view matrix
        camera_view_matrix = CameraUSDUtil.get_camera_view_matrix(prim=camera_prim)
        image_points = [
            world_to_image_space(camera_view_matrix, hA, point, screen_width, screen_height) for point in points
        ]
        image_points = np.array(image_points)

        # Floor pixel coordinates for integer pixel locations
        image_points = np.floor(image_points)

        if enable_boundary_check:
            # Apply boundary filtering
            condition = (
                (image_points[:, 0] >= 0)
                & (image_points[:, 0] <= screen_width)
                & (image_points[:, 1] >= 0)
                & (image_points[:, 1] <= screen_height)
            )
        else:
            # Skip boundary filtering (include all projected points)
            condition = np.ones(len(image_points), dtype=bool)

        # Preserve length by using None for invalid points
        processed_points = [p.tolist() if cond else None for p, cond in zip(points, condition)]
        processed_image_points = [ip.tolist() if cond else None for ip, cond in zip(image_points, condition)]

        return processed_points, processed_image_points
