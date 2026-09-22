import json
import math
import os
import pathlib
from copy import deepcopy

import carb
import numpy as np
import omni.usd
from omni.metropolis.utils.usd_util import USDUtil, CameraUSDUtil
from omni.metropolis.utils.sensor_util import SensorUtil
from ..utils import CameraGeneralUtil
from omni.syntheticdata.scripts.helpers import *
from pxr import Gf, Sdf, Usd, UsdGeom, UsdSkel
from typing import List, Tuple, Optional, Any, Dict, Union
from omni.metropolis.utils.data_capture_util import CameraDataCaptureHelper
from functools import partial
from dataclasses import dataclass

from ..settings import CameraCalibrationSettings, GeneralSetting
from .calibration_utils import CalibrationDataProcessUtils, CalibrationCacheFolderUtils

# FIXME:: set the default resolution as a place holder
_DEFAULT_RESOLUTION = (1920, 1080)


# helper method to convert float/int list
def format_coordinate(
    target_coord: Union[List[Union[float, int]], Tuple[Union[float, int], ...]], target_dimension: Optional[int] = None
) -> Dict[str, Union[float, int]]:
    """Converts a list or tuple of floats/ints into a coordinate dictionary with x, y, z keys."""

    if target_dimension is None:
        target_dimension = len(target_coord)
    else:
        target_dimension = min(target_dimension, len(target_coord))

    if target_dimension == 3:
        return {"x": target_coord[0], "y": target_coord[1], "z": target_coord[2]}
    elif target_dimension == 2:
        return {"x": target_coord[0], "y": target_coord[1]}

    return {}  # Return an empty dictionary if target_dimension doesn't match


@dataclass
class CalibrationDotInfo:
    """structure to store formalized calibration dot information"""

    world_coord: List[float]
    target_camera_image_coord: List[float]
    top_camera_image_coord: List[float]

    def get_formatted_world_coord(self) -> Dict[str, float]:
        return format_coordinate(self.world_coord)

    def get_formatted_target_camera_coord(self) -> Dict[str, int]:
        return format_coordinate(self.target_camera_image_coord)


class CameraCalibrationHelper:
    """Helper functions to output the camera calibration info in standard format"""

    VIEWPORT_RESOLUTION: Tuple[int, int] | None = _DEFAULT_RESOLUTION
    PIXEL_PER_METER: float | None = None
    REFERENCE_ORIGIN_OFFSET: Tuple[float, float] | None = None

    @classmethod
    def is_pixel_per_meter_valid(cls):
        """whether the pixel 2 meter factor is set correctly"""
        if cls.PIXEL_PER_METER == 0 or cls.PIXEL_PER_METER is None:
            carb.log_error("pixel per meter value has not been set correctly.")
            return False
        else:
            return True

    @classmethod
    def update_reference_origin_offset(cls, reference_origin_offset: Optional[Tuple[float, float]] = None):
        """"""
        cls.REFERENCE_ORIGIN_OFFSET = reference_origin_offset

    @classmethod
    def update_pixel_per_meter(cls, target_scale_factor: Optional[float] = None):
        """set the scale factor"""
        if target_scale_factor is not None:
            if target_scale_factor == 0:
                carb.log_error("scale factor can not be set to zero")
        cls.PIXEL_PER_METER = target_scale_factor

    @classmethod
    def get_pixel_per_meter(cls) -> float:
        """validate and return the pixel per meter unit"""
        if not cls.is_pixel_per_meter_valid():
            return cls.PIXEL_PER_METER
        else:
            return None

    @classmethod
    def convert_to_floor_map(cls, point: List[float], image_height: int) -> List[float] | None:
        """convert the coordinate of a point within ov space to the coordinate of the point in global coordinate"""
        if not cls.is_pixel_per_meter_valid():
            return None

        pixel_per_meter = cls.get_pixel_per_meter()
        floor_x = point[0] / pixel_per_meter
        floor_y = (image_height - point[1]) / pixel_per_meter
        return [floor_x, floor_y]

    # NOTE:: the structure of this function has been adjusted to fetch the data from the
    @classmethod
    async def get_camera_params(cls, camera_path: str, camera_resolution: Optional[Tuple[int, int]] = None):
        """get camera params dependence on camera types"""
        # apply default resolution during the camera calibration.
        if camera_resolution is None:
            camera_resolution = cls.VIEWPORT_RESOLUTION

        target_camera_path_list = [camera_path]
        camera_param_annos = ["camera_params"]
        camera_info_dict = {}
        post_processing_fn = partial(
            CalibrationDataProcessUtils.fetch_and_reformat_camera_params, camera_info_dict=camera_info_dict
        )

        await CameraDataCaptureHelper.capture_static_data_async(
            camera_path_list=target_camera_path_list,
            annotator_name_list=camera_param_annos,
            post_processing_fn=post_processing_fn,
            camera_resolution=camera_resolution,
            loading_frame=6,
        )

        return camera_info_dict

    @classmethod
    async def store_camera_view_images(
        cls, camera_path_list: List[str], camera_resolution: Optional[Tuple[int, int]] = None
    ):
        """get camera params dependence on camera types"""
        # apply default resolution during the camera calibration.
        if camera_resolution is None:
            camera_resolution = cls.VIEWPORT_RESOLUTION
        # set target annotator
        camera_param_annos = ["rgb"]
        # helper method to fetch camera view information
        post_processing_fn = partial(CalibrationDataProcessUtils.fetch_camera_view_image)
        await CameraDataCaptureHelper.capture_static_data_async(
            camera_path_list=camera_path_list,
            annotator_name_list=camera_param_annos,
            post_processing_fn=post_processing_fn,
            camera_resolution=camera_resolution,
            loading_frame=5,
        )

    @classmethod
    def format_polygon_contour_vertices(
        cls,
        contour_vertices: List,
        top_camera_path: Optional[Union[Sdf.Path, str]] = None,
        camera_resolution: Optional[Tuple[int, int]] = None,
    ) -> List | None:
        """formatted contour information"""

        if top_camera_path is None:
            top_camera_path = CameraCalibrationSettings.top_view_camera_path

        formatted_contour = []
        if camera_resolution is None:
            camera_resolution = cls.VIEWPORT_RESOLUTION
        width, height = camera_resolution
        # project the contour to the top view. if the point is out of the scope, the dot would be replace with None
        contour_vertices_in_view, _ = SensorUtil.project_3d_to_2d_ortho(
            camera_path=top_camera_path, points=np.array(contour_vertices), screen_width=width, screen_height=height
        )
        if contour_vertices_in_view is None:
            carb.log_error("fail to formate the polygo vertex")
            return None
        # filter out valid orthographic camera pos:
        filtered_vertex_list = [x for x in contour_vertices_in_view if x is not None]
        # if region is out of the scope, else if contour is an empty list, ignore this region.
        if len(filtered_vertex_list) == 0:
            return None
        # for each dot in the outline, record the world space x, y value, store value into a list
        for dot in filtered_vertex_list:
            formatted_contour.append(str(str(float(dot[0])) + " " + str(float(dot[1]))))

        return formatted_contour

    @classmethod
    def generate_fov_contour_vertex_top(
        cls,
        region_dict,
        top_camera_path: Optional[Union[Sdf.Path, str]] = None,
        camera_resolution: Optional[Tuple[int, int]] = None,
    ):
        """generate fov contour vertex following certain format"""

        if top_camera_path is None:
            top_camera_path = CameraCalibrationSettings.top_view_camera_path
        ov_multiple_polygon_list = []
        ploygon_type = CameraCalibrationSettings.PloygonType.Empty
        ov_result = None
        for region_key in region_dict:
            fov_polygon_list = []
            # structure to store FOV polygon outline information
            fov_outline_list = []
            # get FOV polygon information according to their region key
            contour_dict = region_dict[region_key]
            # FOV polygon's outline list
            outline = contour_dict.outline
            # a list that store contour nodes of every hole in current FOV
            holes = contour_dict.holes
            if outline is not None:
                # convert the outline point from world coordinate to image coordinate. Check whether region is covered by topview camera
                fov_outline_list = cls.format_polygon_contour_vertices(
                    top_camera_path=top_camera_path, contour_vertices=outline, camera_resolution=camera_resolution
                )
                fov_polygon_list.append(fov_outline_list)

                # handle FOV region's holes contour in the same way
                for hole in holes:
                    fov_hole_list = []
                    if hole is not None:
                        fov_hole_list = cls.format_polygon_contour_vertices(
                            top_camera_path=top_camera_path, contour_vertices=hole, camera_resolution=camera_resolution
                        )
                        fov_polygon_list.append(fov_hole_list)

                ov_multiple_polygon_list.append(fov_polygon_list)

        # check whether the FOV is a single_ploygon
        if len(region_dict.keys()) == 0:
            ploygon_type = CameraCalibrationSettings.PloygonType.Empty
        elif len(region_dict.keys()) == 1:
            ov_result = ov_multiple_polygon_list[0]
            ploygon_type = CameraCalibrationSettings.PloygonType.SinglePolygon
        else:
            ov_result = ov_multiple_polygon_list
            ploygon_type = CameraCalibrationSettings.PloygonType.MultiPolygon

        return ploygon_type, str(ov_result).replace("[", "(").replace("]", ")").replace("'", "")

    @classmethod
    def camera_focus_point_pos(
        cls, camera_path: Union[Sdf.Path, str], top_camera_path: Optional[Union[Sdf.Path, str]] = None
    ):
        """calculate camera's forward vector from frustum"""
        if top_camera_path is None:
            top_camera_path = CameraCalibrationSettings.top_view_camera_path
        stage = omni.usd.get_context().get_stage()
        camera_prim = stage.GetPrimAtPath(camera_path)
        # get camera's frustum information
        focus_point_pos = CameraUSDUtil.get_camera_focus_point(camera_prim=camera_prim, near_plane=True)
        # check whether the forward vector spot is within top camer scope
        _, image_pos = SensorUtil.project_3d_to_2d_ortho(
            camera_path=top_camera_path, points=np.array([focus_point_pos])
        )
        return focus_point_pos

    @classmethod
    # extract 3d position list from the prims
    def get_3d_point_list_from_prims(cls, prim_path_list: List[Union[str, Sdf.Path]]):
        points_list_3d = []
        for prim_path in prim_path_list:
            translate = USDUtil.get_prim_pos(prim_path=prim_path)
            if translate:
                x, y, z = translate[0], translate[1], translate[2]
                points_list_3d.append([x, y, z])
        return points_list_3d

    @classmethod
    def calculate_camera_3d_rotation(
        cls, prim: Optional[Usd.Prim] = None, prim_path: Optional[Union[Sdf.Path, str]] = None, stage=None
    ):
        """get camera's rotation in degree"""
        camera_transform = USDUtil.get_prim_transform(prim=prim, prim_path=prim_path, stage=stage)
        rotation_matrix = np.transpose(camera_transform[:3, :3])
        rotation_in_degree_from_matrix = CameraGeneralUtil.matrix_to_euler_angles(
            mat=rotation_matrix, degrees=True, extrinsic=False
        )
        return rotation_in_degree_from_matrix

    @classmethod
    def get_camera_top_view_poses(
        cls, camera_path: Union[Sdf.Path, str], top_camera_path: Optional[Union[Sdf.Path, str]] = None
    ):
        """get cameras world coordinate, calculate camera's 2d rotation information, 3d rotation information and 3d positio"""
        if top_camera_path is None:
            top_camera_path = CameraCalibrationSettings.top_view_camera_path
        stage = omni.usd.get_context().get_stage()
        camera_prim = stage.GetPrimAtPath(camera_path)
        if camera_prim.GetTypeName() == "Camera":
            # get camera's ov coordinate translation and rotation
            ov_camera_translation = camera_prim.GetAttribute("xformOp:translate").Get()
            # get camera's forward vector
            ov_focus_point_translation = cls.camera_focus_point_pos(
                camera_path=camera_path, top_camera_path=top_camera_path
            )
            # get camera rotation:

            ov_direction_vector = [
                ov_focus_point_translation[0] - ov_camera_translation[0],
                ov_focus_point_translation[1] - ov_camera_translation[1],
            ]
            # calculate rotation from the forward vector in degree
            ov_rotation_projection = math.degrees(math.atan2(ov_direction_vector[0], ov_direction_vector[1]))
            top_view_rotation_deg = (ov_rotation_projection + 360) % 360
            top_view_translation = [ov_camera_translation[0], ov_camera_translation[1]]
            return top_view_translation, top_view_rotation_deg

        return None, None


class CameraCalibrationCache:
    """contain necessary data to be recorded in the camera calibration file"""

    def __init__(
        self,
        top_view_rotation: List[float] = None,
        top_view_translation: List[float] = None,
        calibration_dot_infos: List[CalibrationDotInfo] = None,
        region_dict: Dict = None,
        camera_params: Dict = None,
        camera_path: str = None,
    ):
        self.top_view_rotation = top_view_rotation
        self.top_view_translation = top_view_translation
        self.calibration_dot_infos = calibration_dot_infos
        self.region_dict = region_dict
        self.camera_params = camera_params
        self.camera_path = camera_path

    def cache_calibration_dots_and_proj_matrix(self, formatted_calibration_cache: Dict):
        """write current camera information to the calibration info dict"""
        # record camera's extrinsic matrix
        extrinsic_matrix = SensorUtil.calculate_3x4_extrinsic_matrix(camera_params=self.camera_params)
        # record camera's intrinsic matrix
        intrinsic_matrix = SensorUtil.calculate_3x3_intrinsic_matrix(camera_params=self.camera_params)
        image_cooridnate_list = []
        world_coordinate_list = []
        projection_matrix = None
        # if target camera has calibration dots
        if self.calibration_dot_infos is None:
            carb.log_error(
                "Warning::{target_camera}'s calibration dot info is invalid".format(target_camera=self.camera_path)
            )
            return

        calibration_dot_image_coords: List = formatted_calibration_cache["imageCoordinates"]
        calibration_dot_world_coords: List = formatted_calibration_cache["globalCoordinates"]
        calibration_dot_image_coords.pop(0)
        calibration_dot_world_coords.pop(0)

        for calibration_dot_info in self.calibration_dot_infos:
            # list to calculate the project matrix
            image_cooridnate_list.append(calibration_dot_info.target_camera_image_coord)
            world_coordinate_list.append(calibration_dot_info.world_coord)
            # store the matched calibration dot pairs
            formatted_dot_image_coord = calibration_dot_info.get_formatted_target_camera_coord()
            formatted_dot_word_coord = calibration_dot_info.get_formatted_world_coord()
            calibration_dot_image_coords.append(formatted_dot_image_coord)
            calibration_dot_world_coords.append(formatted_dot_word_coord)

        # calculate the projection matrix
        projection_matrix = SensorUtil.compute_camera_projection_matrix(
            three_d_points=world_coordinate_list, two_d_points=image_cooridnate_list
        )
        # calculate camera's homography matrix
        # fetch user specified floor height:
        floor_height = GeneralSetting.customized_floor_height
        homography_matrix = SensorUtil.compute_homography_matrix(
            proj_matrix=projection_matrix, platform_height=floor_height
        )

        formatted_calibration_cache["intrinsicMatrix"] = intrinsic_matrix.tolist()
        formatted_calibration_cache["extrinsicMatrix"] = extrinsic_matrix.tolist()
        formatted_calibration_cache["cameraMatrix"] = projection_matrix.tolist()
        formatted_calibration_cache["homography"] = homography_matrix.tolist()

    def get_formatted_fov_polygon(self) -> str:
        """format the vertex information stored in the fov poly"""

        if self.region_dict is None:
            return ""
        ov_formatted_polygon = ""
        polygon_status, ov_polygon_info = CameraCalibrationHelper.generate_fov_contour_vertex_top(
            region_dict=self.region_dict
        )
        if polygon_status == CameraCalibrationSettings.PloygonType.SinglePolygon:
            ov_formatted_polygon = "POLYGON" + str(ov_polygon_info)
        elif polygon_status == CameraCalibrationSettings.PloygonType.MultiPolygon:
            ov_formatted_polygon = "MULTIPOLYGON" + str(ov_polygon_info)
        return ov_formatted_polygon

    def cache_camera_attributes(self, formatted_calibration_cache: Dict):
        """cache the camera attribute to calibration file"""

        formatted_calibration_cache["id"] = USDUtil.get_prim_name(prim_path=self.camera_path)
        formatted_calibration_cache["coordinates"] = format_coordinate(self.top_view_translation)
        # get camera rotation in ov world coordinate
        camera_rotation = CameraCalibrationHelper.calculate_camera_3d_rotation(prim_path=self.camera_path)

        # fetch camera resolution from camera params
        camera_width, camera_height = None, None
        camera_width = int(self.camera_params.get("width", None))
        camera_height = int(self.camera_params.get("height", None))

        if camera_width is None or camera_height is None:
            camera_width, camera_height = CameraCalibrationHelper.VIEWPORT_RESOLUTION

        for item in formatted_calibration_cache["attributes"]:

            if item["name"] == "direction":
                item["value"] = str(self.top_view_rotation)

            if item["name"] == "direction3d":
                item["value"] = str(
                    str(camera_rotation[0]) + "," + str(camera_rotation[1]) + "," + str(camera_rotation[2])
                )

            if item["name"] == "fps":
                item["value"] = str(30)

            if item["name"] == "frameWidth":
                item["value"] = str(camera_width)

            if item["name"] == "frameHeight":
                item["value"] = str(camera_height)

            if item["name"] == "fieldOfViewPolygon":
                item["value"] = self.get_formatted_fov_polygon()

    def cache_camera_fetha(self, formatted_calibration_cache: Dict):
        """cache formatted fisheye camera data"""

        ftheta = self.camera_params.get("ftheta", None)

        if ftheta is None:
            return

        fisheye_theta = dict(ftheta)
        fisheye_theta = CalibrationDataProcessUtils.round_floats_in_nested_dict(data=fisheye_theta)
        formatted_fisheye_data = [
            {"name": "nominalWidth", "value": str(ftheta["width"])},
            {"name": "nominalHeight", "value": str(ftheta["height"])},
            {"name": "opticalCenter", "value": "{c_x},{c_y}".format(c_x=ftheta["cx"], c_y=ftheta["cy"])},
            {
                "name": "radialDistortionCoefficients",
                "value": "{k0},{k1},{k2},{k3},{k4},{k5}".format(
                    k0=ftheta["poly_a"],
                    k1=ftheta["poly_b"],
                    k2=ftheta["poly_c"],
                    k3=ftheta["poly_d"],
                    k4=ftheta["poly_e"],
                    k5=ftheta["poly_f"],
                ),
            },
            {
                "name": "tangentialDistortionCoefficients",
                "value": "{p0},{p1}".format(p0=ftheta["p_0"], p1=ftheta["p_1"]),
            },
            {
                "name": "higherOrderDistortionCoefficients",
                "value": "{s0},{s1},{s2},{s3}".format(
                    s0=ftheta["s_0"],
                    s1=ftheta["s_1"],
                    s2=ftheta["s_2"],
                    s3=ftheta["s_3"],
                ),
            },
        ]

        # extend the attribute dictionary.
        formatted_calibration_cache["attributes"].extend(formatted_fisheye_data)

        return formatted_calibration_cache

    def cache_conversion_factors(self, formatted_calibration_cache: Dict, conversion_factors: Optional[Dict] = None):
        """cache conversion factors: pixe_per_meter, offset"""
        pixel_per_meter = None
        offset = None

        if conversion_factors is not None:
            pixel_per_meter = conversion_factors.get("pixel_per_meter", None)
            offset = conversion_factors.get("offset", None)

        if pixel_per_meter is None:
            pixel_per_meter = CameraCalibrationHelper.PIXEL_PER_METER

        if offset is None:
            offset = CameraCalibrationHelper.REFERENCE_ORIGIN_OFFSET

        formatted_calibration_cache["scaleFactor"] = pixel_per_meter
        formatted_calibration_cache["translationToGlobalCoordinates"] = format_coordinate(offset)


class CalibrationFileGenerator:
    """generate formatted camera calibration file base on the template"""

    @classmethod
    def generate_calibration_file(cls, camera_calibration_cache_dict: Dict[str, CameraCalibrationCache]):
        """generate calibration file according to camera information"""
        # reset the offset value to None:
        # TODO::obtain the sample calibration file path
        sample_calibration_file_path = CalibrationCacheFolderUtils.get_calibration_sample_file_path()
        calibration_file_path = CalibrationCacheFolderUtils.get_calibration_file_path()

        f = open(sample_calibration_file_path, "r")
        sample_data = json.load(f)
        calibration_dict = dict(sample_data)
        sample_sensor_metadata_dict = sample_data["sensors"][0]
        # pop the default value in calibration_dict
        calibration_dict["sensors"].pop()

        # Write camera calibration data
        for camera_path, camera_calibration_cache in camera_calibration_cache_dict.items():
            # cache camera data to the file
            sensor_metadata_dict = deepcopy(sample_sensor_metadata_dict)
            # store basic camera attributes
            camera_calibration_cache.cache_camera_attributes(formatted_calibration_cache=sensor_metadata_dict)
            # store calibration dot information and calculate the projection matrix
            camera_calibration_cache.cache_calibration_dots_and_proj_matrix(
                formatted_calibration_cache=sensor_metadata_dict
            )
            # store camera parameter related to fish eye camera
            camera_calibration_cache.cache_camera_fetha(formatted_calibration_cache=sensor_metadata_dict)
            # store offset and scale factor
            camera_calibration_cache.cache_conversion_factors(formatted_calibration_cache=sensor_metadata_dict)
            calibration_dict["sensors"].append(sensor_metadata_dict)

        out_file = open(calibration_file_path, "w+", encoding="utf-8")
        json.dump(calibration_dict, out_file, ensure_ascii=False, indent=4)
