from __future__ import annotations

import asyncio
import os
import carb
import numpy as np
import omni.usd
from isaacsim.sensors.rtx.placement.camera_calibration.camera_info import CameraInfoManager, CameraInfo
from omni.metropolis.utils.usd_util import USDUtil
from omni.metropolis.utils.sensor_util import SensorUtil
from PIL import Image, ImageDraw

from .calibration_helper import CameraCalibrationHelper, CameraCalibrationCache, CalibrationFileGenerator
from ..settings import CameraCalibrationSettings, GeneralSetting
from .calibration_utils import CalibrationSetUpUtils, CalibrationCacheFolderUtils, CalibrationDataProcessUtils
from .calibration_dot_helper import CalibrationDotHelper, CalibrationDotInfo
from typing import Optional, List, Dict, Tuple, Any, Union
from pxr import Gf, UsdGeom, Usd, Sdf
from ..utils import CameraGeneralUtil


class CameraCalibrationManager:
    """Global class which stores current and predicted positions of all characters and moving objects."""

    __instance: CameraCalibrationManager = None

    def __init__(self):
        if self.__instance is not None:
            raise RuntimeError("Only one instance of CameraCalibrationManager is allowed")

        # build a camera info dict to store all camera related information.
        self.camera_info_manager: CameraInfoManager = CameraInfoManager.get_instance()
        # character dict that match character object with prim path
        CameraCalibrationManager.__instance = self

    def destroy(self):
        CameraCalibrationManager.__instance = None

    def __del__(self):
        self.destroy()

    @classmethod
    def get_instance(cls) -> CameraCalibrationManager:
        if cls.__instance is None:
            CameraCalibrationManager()
        return cls.__instance

    async def generate_calibration_dot_prim_async(self):
        """generate calibration dot prims"""

        # get the number of calibration dots
        if not CalibrationSetUpUtils.is_valid_top_view_camera_type():
            carb.log_error(
                "Top camera is either not generated or in wrong projection type. Top camera should be orthographic projection camera."
            )
            return

        top_view_camera_path = CameraCalibrationSettings.top_view_camera_path
        calibration_dots_parent_path = CameraCalibrationSettings.calibration_prim_path
        CalibrationSetUpUtils.remove_calibration_dot_prim(calibration_dots_parent_path)
        if not self.camera_info_manager.refresh_camera_info(reset_camera_info=True):
            carb.log_error("no valid camera in the scene, fail to generate calibration dot")
            return

        camera_info_dict = self.camera_info_manager.get_camera_info_dict()

        for camera_prim_path, camera_info in camera_info_dict.items():
            # get camera name
            camera_name = camera_info.camera_name

            choosed_point = await CalibrationDotHelper.pick_calibration_dot(
                camera_path=camera_prim_path, top_view_camera_path=top_view_camera_path
            )
            formatted_point = [carb.Float3(dot[0], dot[1], dot[2]) for dot in choosed_point]
            CalibrationSetUpUtils.spawn_calibration_dot_prim(calibration_dots_parent_path, formatted_point, camera_name)

    def generate_calibration_dot_prim(self):
        """generate xform to present 3d"""
        asyncio.ensure_future(self.generate_calibration_dot_prim_async())

    def create_top_view_camera(
        self,
        root_prim_path: Optional[Union[Sdf.Path, str]] = None,
        clipping_height: Optional[float] = None,
        top_view_resolution: Optional[Tuple[int, int]] = None,
    ):
        """create top view camera, adjust camera's position to include whole stage
        and update "top view camera path" to the prim path of new top view camera"""

        if root_prim_path is None:
            root_prim_path = CameraCalibrationSettings.scene_bounding_box_path

        if clipping_height is None:
            clipping_height = GeneralSetting.customized_ceiling_height
        # check whether the target root prim path is valid

        if top_view_resolution is None:
            top_view_resolution = CameraCalibrationHelper.VIEWPORT_RESOLUTION

        stage = omni.usd.get_context().get_stage()
        # check whether the root prim selected by customers is correct or not.
        if not USDUtil.is_valid_prim(stage=stage, prim_path=root_prim_path):
            carb.log_error(
                "{root_prim_path} is not a valid Scene Bounding Box Path Value".format(root_prim_path=root_prim_path)
            )
            return
        # spawn the top view camera
        top_camera_prim = CalibrationSetUpUtils.spawn_top_view_camera()

        if top_camera_prim is None or not top_camera_prim.IsValid():
            carb.log_error("Failed to spawn top view camera")
            return

        # calculate the top camera's position and horizontal aperture to ensure all target area are covered.
        spawn_location, horizontal_aperture = CalibrationSetUpUtils.calculate_top_camera_parameter(
            top_view_resolution=top_view_resolution, root_prim_path=root_prim_path
        )
        camera_pos = Gf.Vec3d(spawn_location[0], spawn_location[1], 200)
        spawn_rotation = Gf.Quatd(1, 0, 0, 0)
        top_camera_prim.GetAttribute("xformOp:orient").Set(spawn_rotation)
        top_camera_prim.GetAttribute("xformOp:translate").Set(camera_pos)

        # check whether cliping height is set:
        if clipping_height != -1:
            # calculate the clipping plane distance:
            camera_position = USDUtil.get_prim_pos(top_camera_prim)
            camera_height = camera_position[2]
            clipping_distance = camera_height - clipping_height

            original_clippingrange = top_camera_prim.GetAttribute("clippingRange").Get()
            new_clippingrange = Gf.Vec2d(clipping_distance, original_clippingrange[1])
            top_camera_prim.GetAttribute("clippingRange").Set(new_clippingrange)

        # adjust top camera type to orthographic camera
        top_camera_prim.GetAttribute("horizontalAperture").Set(horizontal_aperture)
        top_camera_prim.GetAttribute("projection").Set("orthographic")

    def is_ready_to_calibrate(self):
        """check whether the calibration file is ready to be generated"""
        stage = omni.usd.get_context().get_stage()
        # check whether the camera root prim is valid
        camera_prim_list = CameraGeneralUtil.get_target_camera_prims_under_root()
        if not camera_prim_list:
            # remind user to generate cameras
            camera_parent_path = GeneralSetting.camera_parent_prim_path
            carb.log_warn(
                "Warning:: There is no valid camera prim under {camera_path}".format(
                    camera_path=str(camera_parent_path)
                )
            )
            return False

        # check whether calibration prims have been generated
        calibration_root_prim_path = CameraCalibrationSettings.calibration_prim_path
        if not USDUtil.is_valid_prim(stage=stage, prim_path=calibration_root_prim_path):
            # remind user to generate calibration dots
            carb.log_error("The calibration dot has not yet been generated. Fail to generate calibration info.")
            return False

        # check whether top view camera's projection type is correct:
        if not CalibrationSetUpUtils.is_valid_top_view_camera_type():
            carb.log_error(
                "Top camera is either not generated or in wrong projection type. Top camera should be orthographic projection camera."
            )
            return False

    async def get_validate_calibration_dot_infos(
        self, camera_prim_path: str, camera_params: Optional[Dict] = None
    ) -> List[CalibrationDotInfo] | None:
        """double check whether the camera calibration dot is still available"""

        stage = omni.usd.get_context().get_stage()
        calibration_root_prim_path = CameraCalibrationSettings.calibration_prim_path
        # get current top camera information:
        top_view_camera_path = CameraCalibrationSettings.top_view_camera_path
        # get current valid camera pos:
        camera_info: CameraInfo = self.camera_info_manager.get_camera_info(camera_prim_path=camera_prim_path)
        camera_name = camera_info.camera_name
        calibration_prim_path = "{calibration_root_prim_path}/{camera_name}".format(
            calibration_root_prim_path=calibration_root_prim_path, camera_name=camera_name
        )
        calibration_prim = stage.GetPrimAtPath(calibration_prim_path)
        if not USDUtil.is_valid_prim(prim=calibration_prim):
            return False

        # get current exist calibration dots
        calibration_dots = calibration_prim.GetChildren()
        calibration_dots_pos = [USDUtil.get_prim_pos(prim=prim) for prim in calibration_dots]
        # get camera params
        calibration_dot_infos = await CalibrationDotHelper.get_validate_pos_in_scope(
            pos_list=calibration_dots_pos,
            target_camera_path=camera_prim_path,
            top_camera_path=top_view_camera_path,
            target_camera_params=camera_params,
        )
        return calibration_dot_infos

    def calculate_conversion_factors_from_root(
        self, top_camera_resolution: Tuple[int, int] = (1920, 1080)
    ) -> Dict | None:
        """calculate the factors to convert a point from ov coordiante to top view image coordinate"""

        # get the bounding box of the root prim selected by user
        stage = omni.usd.get_context().get_stage()
        stage_root_prim_path = CameraCalibrationSettings.scene_bounding_box_path
        stage_root_prim = stage.GetPrimAtPath(stage_root_prim_path)
        purposes = [UsdGeom.Tokens.default_]
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), purposes)
        bound = bbox_cache.ComputeWorldBound(stage_root_prim)
        range = bound.ComputeAlignedBox()
        bbox_center = bound.ComputeCentroid()
        bbox_max = range.GetMax()
        bbox_min = range.GetMin()
        point_min = [bbox_min[0], bbox_min[1], bbox_min[2]]
        point_max = [bbox_max[0], bbox_max[1], bbox_min[2]]
        # get top view camera's camera path
        top_view_camera_path = CameraCalibrationSettings.top_view_camera_path
        points = np.array([point_min, point_max])
        # project the world cooridnate to the top view camera's image plane
        points, image_coordinates = SensorUtil.project_3d_to_2d_ortho(
            camera_path=top_view_camera_path,
            points=points,
            screen_width=1920,
            screen_height=1080,
            enable_boundary_check=False,
        )
        # if points fail to be converted to the 2d space
        if None in points:
            return None

        # Correct distance calculation
        points_distance = ((points[0][0] - points[1][0]) ** 2 + (points[0][1] - points[1][1]) ** 2) ** 0.5
        image_space_distance = (
            (image_coordinates[0][0] - image_coordinates[1][0]) ** 2
            + (image_coordinates[0][1] - image_coordinates[1][1]) ** 2
        ) ** 0.5
        # Avoid division by zero
        if points_distance == 0:
            carb.log_warn("Error: Zero points_distance, check bounding box data")
        else:
            pixel_per_meter = image_space_distance / points_distance
            # Correct offset calculation
            offset_x = image_coordinates[0][0] / pixel_per_meter - point_min[0]
            offset_y = (top_camera_resolution[1] - image_coordinates[0][1]) / pixel_per_meter - point_min[1]

        result_dict = {"pixel_per_meter": pixel_per_meter, "offset": (offset_x, offset_y)}
        return result_dict

    def calculate_conversion_factors_from_dots(
        self, all_calibration_dot_infos: List[CalibrationDotInfo], top_camera_resolution: Tuple[int, int] = (1920, 1080)
    ) -> Dict | None:
        """Calculate the factors to convert a point from OV coordinate to top-view image coordinate using multiple calibration dots."""
        if not all_calibration_dot_infos:
            carb.log_warn("No calibration dots found. Cannot compute conversion factors.")
            return None

        # Store world coordinates (XY only) and image coordinates (XY only)
        world_coords = np.array([[dot.world_coord[0], dot.world_coord[1]] for dot in all_calibration_dot_infos])
        image_coords = np.array(
            [[dot.top_camera_image_coord[0], dot.top_camera_image_coord[1]] for dot in all_calibration_dot_infos]
        )

        # Compute pairwise distances in world space and image space
        ov_distances = []
        pixel_distances = []

        num_dots = len(world_coords)
        for i in range(num_dots):
            for j in range(i + 1, num_dots):
                ov_distance = np.linalg.norm(world_coords[i] - world_coords[j])
                pixel_distance = np.linalg.norm(image_coords[i] - image_coords[j])

                if ov_distance > 0:  # Avoid division by zero
                    ov_distances.append(ov_distance)
                    pixel_distances.append(pixel_distance)

        # Compute average pixel per meter ratio
        if len(ov_distances) == 0:
            carb.log_warn("No valid distances found between calibration dots.")
            return None

        pixel_per_meter = np.sum(np.array(pixel_distances)) / np.sum(np.array(ov_distances))

        # Compute the average offset between the image and world coordinates
        world_to_pixel_x = image_coords[:, 0] / pixel_per_meter - world_coords[:, 0]
        world_to_pixel_y = (top_camera_resolution[1] - image_coords[:, 1]) / pixel_per_meter - world_coords[:, 1]

        offset_x = np.mean(world_to_pixel_x)
        offset_y = np.mean(world_to_pixel_y)

        carb.log_warn(f"Calculated pixel per meter: {pixel_per_meter}, Offset: ({offset_x}, {offset_y})")

        result_dict = {"pixel_per_meter": pixel_per_meter, "offset": (offset_x, offset_y)}
        return result_dict

    def calculate_conversion_factors(
        self,
        calibration_info_dict: Dict[str, CameraCalibrationCache],
        camera_resolution: Tuple[int, int] = (1920, 1080),
    ) -> Dict | None:
        """calculate conversion factors"""
        result = None
        result = self.calculate_conversion_factors_from_root(camera_resolution)
        if result is None:
            all_calibration_dot_infos: List[CalibrationDotInfo] = []
            # Collect all calibration dots
            for camera_prim_path, calibration_info in calibration_info_dict.items():
                calibration_dot_infos = calibration_info.calibration_dot_infos
                if calibration_dot_infos:
                    all_calibration_dot_infos.extend(calibration_dot_infos)

            result = self.calculate_conversion_factors_from_dots(
                all_calibration_dot_infos=all_calibration_dot_infos, camera_resolution=camera_resolution
            )
        return result

    def generate_calibration(self):
        """generate calibraiton file"""
        asyncio.ensure_future(self.generate_calibration_async())

    async def generate_calibration_async(self):
        """generate calibration file"""
        # get value from setting
        top_camera_path = CameraCalibrationSettings.top_view_camera_path
        camera_calibration_cache_dict: Dict[str, CameraCalibrationCache] = {}
        # renew the contour vertex list for each camera
        self.refresh_fov_info()
        camera_info_dict = self.camera_info_manager.get_camera_info_dict()

        for camera_prim_path, camera_info in camera_info_dict.items():
            region_dict = camera_info.contours
            top_view_translate, top_view_rotation_deg = CameraCalibrationHelper.get_camera_top_view_poses(
                camera_path=camera_prim_path, top_camera_path=top_camera_path
            )
            if top_view_translate is None or top_view_rotation_deg is None:
                carb.log_error(
                    f"camera {camera_prim_path} is not covered by top view! Fail to generate calibration file."
                )
                return

            camera_params = await CameraCalibrationHelper.get_camera_params(camera_path=camera_prim_path)
            calibration_dot_infos = await self.get_validate_calibration_dot_infos(
                camera_prim_path=camera_prim_path, camera_params=camera_params
            )
            if calibration_dot_infos is None:
                carb.log_error(
                    f"camera {camera_prim_path} 's calibration dot is invalid! Fail to generate calibration file."
                )
                return
            # store the contour vertex information of each camera to a dict
            # create camera calibration cache to store extra information
            camera_calibration_cache_dict[camera_prim_path] = CameraCalibrationCache(
                top_view_rotation=top_view_rotation_deg,
                top_view_translation=top_view_translate,
                calibration_dot_infos=calibration_dot_infos,
                region_dict=region_dict,
                camera_params=camera_params,
                camera_path=camera_prim_path,
            )

        conversion_factor = self.calculate_conversion_factors(calibration_info_dict=camera_calibration_cache_dict)
        if not conversion_factor:
            carb.log_error("Fail to generate the scale factor and offset factor! Fail to generate calibration file.")
            return

        # refresh the pixel per meter factor.
        pixel_per_meter = conversion_factor.get("pixel_per_meter", None)

        if pixel_per_meter is None:
            carb.log_error("Fail to generate the pixel_per_meter factor! Fail to generate calibration file.")
            return

        CameraCalibrationHelper.update_pixel_per_meter(target_scale_factor=pixel_per_meter)
        offset = conversion_factor.get("offset", None)

        if offset is None:
            carb.log_error("Fail to generate the offset factor! Fail to generate calibration file.")
            return
        CameraCalibrationHelper.update_reference_origin_offset(reference_origin_offset=offset)
        # generate the calibration file
        CalibrationFileGenerator.generate_calibration_file(camera_calibration_cache_dict=camera_calibration_cache_dict)

    def refresh_fov_info(self, store_fov_to_file=False):
        """generate fov polygon data for each cameras in the stage"""
        # refresh the information of all camera
        if not self.camera_info_manager.refresh_camera_info(reset_camera_info=True):
            return
        # refresha camera fov info for all cameras
        self.camera_info_manager.refresh_camera_fov()
        # check whether the fov data need to be stored to file
        if store_fov_to_file:
            self.draw_fov_polygon()

    def calculate_contour_in_top_view(self, contour: List):
        """calculate contour in camera top view"""
        # get top_view_camera_path from setting
        top_view_camera_path = CameraCalibrationSettings.top_view_camera_path
        # check whether contour is None
        if contour is None:
            return None
        # if contour is not none, convert 3d contour vertex to 2d image coordinate
        _, contour_in_view_2d = SensorUtil.project_3d_to_2d_ortho(
            camera_path=top_view_camera_path, points=np.array([[vertex[0], vertex[1], vertex[2]] for vertex in contour])
        )
        # filter and validate vertex on contour
        contour_in_view_2d = [vertex for vertex in contour_in_view_2d if vertex is not None]
        camera_params_hole = [pos for pos in contour_in_view_2d if not pos is None]
        # cast the 2d image coordinate to integer
        formatted_contour = CalibrationDataProcessUtils.validate_contour(camera_params_hole)
        # check whether convert to image coorindate reduce the number of vertex
        return formatted_contour

    # visualzie camrea's fov on different images
    def draw_fov_polygon(self):
        """Generates and saves debug images with the FOV polygons of each camera overlaid on the top-view image."""
        # get fov polygon image folde
        debug_image_folder_path = CalibrationCacheFolderUtils.get_fov_polygon_directory()

        # create folder if path does not exist
        os.makedirs(debug_image_folder_path, exist_ok=True)
        # for each image, draw its FOV on topview image and save the
        camera_info_dict = self.camera_info_manager.get_camera_info_dict()

        for camera_path, camera_info in camera_info_dict.items():
            # get top view image path
            top_image_path = CalibrationCacheFolderUtils.get_top_view_image_path()
            # open top view image and draw fov polygon
            original_image = Image.open(top_image_path)
            mask_image = Image.new("L", original_image.size, 255)
            draw = ImageDraw.Draw(mask_image)
            region_dict = camera_info.contours

            # for each FOV polygon region, get their FOV outline and hole information
            for region_key in region_dict.keys():
                region = region_dict[region_key]
                outline = region.outline
                # generate formatted 2d projection on top camera view
                formatted_outline_contour = self.calculate_contour_in_top_view(contour=outline)

                if not formatted_outline_contour:
                    continue

                draw.polygon(formatted_outline_contour, fill=100)

                # get hole contour stored in the hole list
                holes = region.holes
                for hole in holes:
                    # generate formatted 2d projection on top camera view
                    formatted_hole_contour = self.calculate_contour_in_top_view(contour=hole)

                    if not formatted_hole_contour:
                        continue

                    draw.polygon(formatted_hole_contour, fill=255)

                # draw FOV polygon information on the image
                original_image = Image.composite(
                    original_image, Image.new("RGB", original_image.size, "white"), mask_image
                )

            camera_id = USDUtil.get_prim_name(prim_path=camera_path)
            image_file_name = f"{camera_id}.png"
            image_file_path = os.path.join(debug_image_folder_path, image_file_name)
            original_image.save(image_file_path)
            original_image.close()
            # inform user about the generated image file
            carb.log_info(
                "Camera:{camera_path} 's FOV has been stored in {image_file_path}".format(
                    camera_path=camera_path, image_file_path=image_file_path
                )
            )

    def capture_camera_images(self):
        """capture process and cache camera images"""
        asyncio.ensure_future(self.capture_and_process_camera_view_image())

    async def capture_and_process_camera_view_image(self):
        """capture and post process camera view images base on the requirement"""
        # apply default resolution during the camera calibration.
        target_camera_path_list = []
        top_view_camera_path = CameraCalibrationSettings.top_view_camera_path
        target_camera_path_list.append(top_view_camera_path)

        # check_whether output the camera view is necessary.
        if CameraCalibrationSettings.capture_camera_view_images_enabled:
            # get current activate camera_prim_list
            camera_prim_list = CameraGeneralUtil.get_target_camera_prims_under_root()
            camera_prim_path_list = [str(camera_prim.GetPrimPath()) for camera_prim in camera_prim_list]
            target_camera_path_list.extend(camera_prim_path_list)
        # NOTE:: currently assume all camera view is using the default camera resolution
        await CameraCalibrationHelper.store_camera_view_images(camera_path_list=target_camera_path_list)

        carb.log_info("All camera view images has been captured successfully")

        if CameraCalibrationSettings.show_fov_polygon_enabled:
            # draw fov contour on top view image make the debug process easier.
            self.refresh_fov_info(store_fov_to_file=True)
