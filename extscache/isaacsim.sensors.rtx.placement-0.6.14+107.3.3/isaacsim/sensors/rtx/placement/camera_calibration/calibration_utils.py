import copy
import os
import carb
import json
import numpy as np
import omni.kit.mesh.raycast
import omni.ui as ui
import omni.usd
from omni.metropolis.utils.carb_util import CarbUtil
from omni.metropolis.utils.simulation_util import SimulationUtil
from omni.usd.commands import DeletePrimsCommand
from omni.metropolis.utils.sensor_util import SensorUtil
from PIL import Image
from pxr import Gf, Sdf, Tf, Usd, UsdGeom, UsdSkel
from omni.metropolis.utils.usd_util import USDUtil, CameraUSDUtil
from .contour_polygon import FOV, FOVStatus
from ..settings import CameraCalibrationSettings, GeneralSetting
from ..utils import CameraGeneralUtil
from typing import Any, Dict


class CameraRayCastUtils:
    @staticmethod
    def get_calibration_dot(start_point, end_point):
        """Raycast across the far and near clipping platform"""
        raycast = omni.kit.mesh.raycast.get_mesh_raycast_interface()
        raycast.set_bvh_refresh_rate(omni.kit.mesh.raycast.BvhRefreshRate.FAST, True)
        dist = CarbUtil.dist3(start_point, end_point)
        dir = CarbUtil.normalize3(CarbUtil.sub3(end_point, start_point))
        hit_result = raycast.closestRaycast(start_point, dir, dist)
        if hit_result and (hit_result.position is not None):
            return hit_result.position
        else:
            return start_point

    # This is the order of the vertex on the near/far platform:

    # corner_1           # corner_3

    # corner_2           # corner_4
    @staticmethod
    def uniform_slice_platform_matrix(platform, seed):
        """seperate the near and far clip platform uniformaly"""
        corner_1 = platform[0]
        corner_2 = platform[1]
        corner_3 = platform[2]
        dist_v = CarbUtil.length3(CarbUtil.sub3(corner_1, corner_2))
        dist_h = CarbUtil.length3(CarbUtil.sub3(corner_1, corner_3))

        dir_v = CarbUtil.normalize3(CarbUtil.sub3(corner_2, corner_1))
        dir_h = CarbUtil.normalize3(CarbUtil.sub3(corner_3, corner_1))
        vector_length_v = dist_v / seed
        vector_length_h = dist_h / seed

        step_v = CarbUtil.scale3(dir_v, vector_length_v)
        step_h = CarbUtil.scale3(dir_h, vector_length_h)

        result_list = []

        for i in range(1, seed):
            row = []
            start_point = CarbUtil.add3(corner_1, CarbUtil.scale3(step_v, i))
            for i in range(1, seed):
                curr_point = CarbUtil.add3(start_point, CarbUtil.scale3(step_h, i))
                row.append(curr_point)
            result_list.append(row)

        return result_list

    @classmethod
    def generate_dot_point_pair_matrix(cls, platform_one, platform_two, seed):
        """get the both end of raycast line generated from camera"""
        dot_set_upper = cls.uniform_slice_platform_matrix(platform_one, seed)
        dot_set_lower = cls.uniform_slice_platform_matrix(platform_two, seed)
        return dot_set_upper, dot_set_lower

    @staticmethod
    def check_hit_point_height(pos, height):
        """check whether the platform height is within the threshold
        ( brutal way of checking whether the raycast hit the ground   )"""
        if pos[2] > height + 0.1 or pos[2] < height - 0.1:
            return False
        return True

    @classmethod
    def get_hit_information_mesh_matrix(cls, camera_path, seed):
        """record hit resultiformation within a 2d matrix"""
        point_list = []
        point_list = CameraUSDUtil.get_camera_frustum_corners(camera_path=camera_path)
        if not point_list or len(point_list) < 8:
            return None

        upper_patform = point_list[:4]
        lower_patform = point_list[-4:]
        dot_upper_matrix, dot_lower_matrix = cls.generate_dot_point_pair_matrix(upper_patform, lower_patform, seed)
        row = len(dot_upper_matrix)
        col = len(dot_upper_matrix[0])
        result_matrix = [[carb.Float3() for _ in range(col)] for _ in range(row)]

        for i in range(row):
            for j in range(col):
                hit_dot = cls.get_calibration_dot(dot_upper_matrix[i][j], dot_lower_matrix[i][j])
                result_matrix[i][j] = hit_dot

        return result_matrix


class CameraFovUtils:
    @staticmethod
    def sign_2d_matrix(result_hit_matrix):
        """give a 2d matrix that records dense raycasting hit points from target camera, mark the hit result with different index"""
        rows = len(result_hit_matrix)
        cols = len(result_hit_matrix[0])
        result_matrix = [[0 for _ in range(cols)] for _ in range(rows)]
        for i in range(rows):
            for j in range(cols):
                coord = result_hit_matrix[i][j]

                # mark accessible point with 0
                # mark inaccesiible point with -1

                if not GeneralSetting.need_navmesh_check:
                    # if we are using height threshold to define the ground
                    if coord[2] - GeneralSetting.customized_floor_height < 0.25:
                        result_matrix[i][j] = FOVStatus.ACCESSIBLE.value
                    else:
                        result_matrix[i][j] = FOVStatus.INACCESSIBLE.value
                else:
                    # if we are using navmesh to define the ground
                    if not SimulationUtil.validate_navmesh_point(coord, 0.06):
                        result_matrix[i][j] = FOVStatus.INACCESSIBLE.value
                    else:
                        result_matrix[i][j] = FOVStatus.ACCESSIBLE.value

        return result_matrix

    @classmethod
    def get_camera_fov_contours(
        cls,
        camera_path,
        calibration_seed,
        contour_index=0,
        size_threshold=0,
    ):
        """calculate camera's FOV contour information"""
        result_hit_matrix = CameraRayCastUtils.get_hit_information_mesh_matrix(camera_path, calibration_seed)
        if not result_hit_matrix:
            return None
        # mark the FOV region base on navmesh information and raycast result
        signed_matrix = cls.sign_2d_matrix(result_hit_matrix=result_hit_matrix)
        # calculate the outline contour information
        region_dict = FOV.build_contour_group(result_hit_matrix, signed_matrix, contour_index, size_threshold)
        return region_dict


class CalibrationSetUpUtils:
    @staticmethod
    def remove_calibration_dot_prim(calibration_dots_parent_path):
        """clean the old calibration dot prim set"""
        stage = omni.usd.get_context().get_stage()
        root_prim = stage.GetPrimAtPath(calibration_dots_parent_path)
        remove_path_list = []
        if root_prim is not None and root_prim.IsValid() and root_prim.IsActive():
            for prim in root_prim.GetChildren():
                if prim and prim.IsValid() and prim.IsActive():
                    remove_path_list.append(prim.GetPath())

        DeletePrimsCommand(remove_path_list).do()

    @staticmethod
    def spawn_calibration_dot_prim(calibration_dots_parent_path, random_pick_set, camera_name):
        """generate calibration dot prim in the scene"""
        stage = omni.usd.get_context().get_stage()
        for dot in random_pick_set:
            xform_path = Sdf.Path(
                omni.usd.get_stage_next_free_path(stage, f"{calibration_dots_parent_path}/{camera_name}/spot", False)
            )
            parent_path = Sdf.Path(xform_path).GetParentPath()
            CameraGeneralUtil.ensure_parent_prim_exists(target_prim_path=parent_path, filter_fn=lambda prim: prim.IsA(UsdGeom.Xformable), default_prim_type="Xform")
            omni.kit.commands.execute(
                "CreatePrimCommand", prim_type="Xform", prim_path=xform_path, select_new_prim=False
            )
            dot_prim = stage.GetPrimAtPath(xform_path)
            dot_prim.GetAttribute("xformOp:translate").Set(Gf.Vec3d(dot[0], dot[1], dot[2]))

    @staticmethod
    def is_orthographic_projection_camera(camera_path):
        """check whether target camera is a orthographic camera"""
        stage = omni.usd.get_context().get_stage()
        camera_prim = stage.GetPrimAtPath(camera_path)
        # check whether the prim is valid or not
        if not USDUtil.is_valid_prim(prim=camera_prim):
            return False
        projection_type = camera_prim.GetAttribute("projection").Get()
        result = str(projection_type) == "orthographic"
        return result

    @classmethod
    def is_valid_top_view_camera_type(cls):
        """check whether top view camera's type is valid"""
        top_view_camera_path = CameraCalibrationSettings.top_view_camera_path
        # check if camera's projection type is correct:
        if not cls.is_orthographic_projection_camera(top_view_camera_path):
            carb.log_error("Top camera's projection type need to be set to orthographic")
            return False
        return True

    @staticmethod
    def calculate_top_camera_parameter(top_view_resolution, root_prim_path):
        """calculate the position and horizontal aperture for a orthographic top camera"""

        def estimate_HA(x_distance, y_distance, screen_width, screen_height):
            """estimate the HA of the orthographic camera from the x, y span"""
            hA = max(x_distance / 2 * 20, y_distance / 2 * 20 * screen_width / screen_height)
            return hA

        def calculate_scene_width_length(min_point, max_point):
            """calculate the scene's x,y direction span"""
            min_x, min_y, min_z = min_point
            max_x, max_y, max_z = max_point
            x_distance = max_x - min_x
            y_distance = max_y - min_y
            return x_distance, y_distance

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(root_prim_path)
        purposes = [UsdGeom.Tokens.default_]
        screen_width, screen_height = top_view_resolution
        # get scene bounding box
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), purposes)
        bound = bbox_cache.ComputeWorldBound(prim)
        range = bound.ComputeAlignedBox()
        bbox_center = bound.ComputeCentroid()
        bbox_max = range.GetMax()
        bbox_min = range.GetMin()
        # calculate the horizontal aperture base on scene's x and y size
        x_distance, y_distance = calculate_scene_width_length(bbox_min, bbox_max)
        HA = estimate_HA(x_distance, y_distance, screen_width, screen_height)
        position = [bbox_center[0], bbox_center[1], 100]
        return position, HA

    @staticmethod
    def get_top_view_camera_prim_path(current_stage=None):
        """get a valid prim path of top view camera"""
        # parent prim name of the top view camera
        top_camera_parent_path = CameraCalibrationSettings.top_camera_parent_prim_path
        # get top view camera's prim name
        top_camera_prim_name = CameraCalibrationSettings.get_top_view_camera_prim_name()
        # get default top view camera's path
        top_view_camera_path = "{parent_prim_path}/{prim_name}".format(
            parent_prim_path=top_camera_parent_path, prim_name=top_camera_prim_name
        )
        # get next valid path according to current stage info
        camera_path = Sdf.Path(omni.usd.get_stage_next_free_path(current_stage, Sdf.Path(top_view_camera_path), False))
        return camera_path

    @classmethod
    def spawn_top_view_camera(cls) -> Usd.Prim:
        # ensure the default orientation system is base on orient system :
        xformoptype_setting_path = "/persistent/app/primCreation/DefaultXformOpType"
        original_xform_order_setting = carb.settings.get_settings().get(xformoptype_setting_path)
        carb.settings.get_settings().set(xformoptype_setting_path, "Scale, Orient, Translate")
        stage = omni.usd.get_context().get_stage()
        top_view_camera_path = cls.get_top_view_camera_prim_path(current_stage=stage)
        # update the top camera path value after prim has been generated successfully.

                # fetch the parent path of the camera prim
        camera_parent_prim_path = Sdf.Path(top_view_camera_path).GetParentPath()
        # ensure the camera parent prim is a valid xformable prim
        CameraGeneralUtil.ensure_parent_prim_exists(target_prim_path=camera_parent_prim_path, filter_fn=lambda prim: prim.IsA(UsdGeom.Xformable), default_prim_type="Xform")

        omni.kit.commands.execute(
            "CreatePrimCommand", prim_type="Camera", prim_path=top_view_camera_path, select_new_prim=False,
        )
        carb.log_info(f"Spawn top view camera at {top_view_camera_path}")
        CameraCalibrationSettings.top_view_camera_path = str(top_view_camera_path)
        # set the xform setting back to original value
        carb.settings.get_settings().set(xformoptype_setting_path, original_xform_order_setting)
        top_view_camera_prim = stage.GetPrimAtPath(top_view_camera_path)
        return top_view_camera_prim


class CalibrationDataProcessUtils:
    @staticmethod
    def extract_place_info():
        """extract valid place info into a list of dict"""
        place_info_str = CameraCalibrationSettings.place_info
        result_list = []
        # split the name string via "/"
        items = place_info_str.split("/")
        for item in items:
            # try to extract key and value
            key, value = item.split("=")
            # remove space
            key = key.strip()
            value = value.strip()

            # Check if key or value is empty or "None"
            if not key or not value or key.lower() == "none" or value.lower() == "none":
                carb.log_warn(
                    f"Warning: '{item}' has empty key or value, or contains 'None'. Please provide valid key and value."
                )
                continue

            # add the post processed value to the array
            result_list.append({"name": key, "value": value})

        return result_list

    @classmethod
    def refine_place_info(cls):
        """refine place info, remove invalid parts"""
        dict_list = cls.extract_place_info()
        if not dict_list:
            return ""

        result_str = ""
        for item in dict_list:
            # Make sure both 'name' and 'value' are present
            if "name" in item and "value" in item:
                key = item["name"]
                value = item["value"]
                # Append key=value to result_str
                result_str += f"{key}={value}/"

        # Remove the trailing slash
        if result_str.endswith("/"):
            result_str = result_str[:-1]

        return result_str

    @staticmethod
    def fetch_and_reformat_camera_params(
        camera_path: str, annotator_dict: Dict[str, Any], camera_info_dict: Dict[str, Any]
    ):
        """fetch target camera's parameter and reformat the camera params to fit the utils' input"""
        camera_params_anno_dict = annotator_dict["camera_params"]
        # wait three frames to ensure the camera params are fetched by camera_params annotator.
        camera_params_data = camera_params_anno_dict.get_data()
        # clear the dict, ensure it is empty
        camera_info_dict.clear()
        reformated_params = SensorUtil.reformat_camera_params(camera_params=camera_params_data)

        copied_reformat_params = copy.deepcopy(reformated_params)
        camera_info_dict.update(copied_reformat_params)

    @classmethod
    def fetch_camera_view_image(cls, camera_path: str, annotator_dict: Dict[str, Any]):
        """fetch target camera's rgb information and update the camera metadata"""
        output_folder_path = CameraCalibrationSettings.camera_calibration_output_folder_path
        rgb_anno = annotator_dict["rgb"]
        # wait three frames to ensure the camera params are fetched by camera_params annotator.
        rgb_image = Image.fromarray(rgb_anno.get_data(), "RGBA").convert("RGB")
        # get the camera prim name from the camera path.
        camera_id = USDUtil.get_prim_name(prim_path=camera_path)
        # generate the camera view image name.
        top_view_camera_path = CameraCalibrationSettings.top_view_camera_path
        # check whether the cameera is top view camera.

        image_name = ""
        metadata = None
        # if camera is the top camera, apply different naming convention
        if (camera_path) == str(top_view_camera_path):
            image_name = CameraCalibrationSettings.get_top_view_image_name()
            metadata = cls.generate_image_meta_data(
                sensor_id=camera_id, image_file_name=image_name, view_type="plan-view"
            )
        else:
            image_name = "{camera_id}.png".format(camera_id=camera_id)
            metadata = cls.generate_image_meta_data(
                sensor_id=camera_id, image_file_name=image_name, view_type="camera-view"
            )

        camera_view_image_path = os.path.join(output_folder_path, image_name)
        rgb_image.save(camera_view_image_path, quality=90)
        carb.log_info(
            "{camera_path} 's view image has been stored in {image_file_path}".format(
                camera_path=camera_path, image_file_path=camera_view_image_path
            )
        )
        metadata_file_path = CalibrationCacheFolderUtils.get_metadata_path()
        metadata_list = [metadata]
        cls.add_images_metadata(metadata_file_path, metadata_list)

    @staticmethod
    def add_images_metadata(file_path, new_images):
        """
        Add new image data to the JSON file. If the file does not exist, create an empty JSON file and add the data.
        :param file_path: JSON file's path.
        :param new_images: A list of image data that we want to add to the metadata file.
        """
        # Check if the file exists
        if not os.path.isfile(file_path):
            # If the file does not exist, create an empty JSON structure
            carb.log_info(f"File {file_path} does not exist. Creating a new file.")
            data = {"images": []}
        else:
            # If the file exists, read current data
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

        # Ensure the "images" key is present in the data
        if "images" not in data:
            data["images"] = []

        # Add new image data to the list
        data["images"].extend(new_images)

        # Write the updated list to the JSON file
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def validate_contour(polygon_contour):
        """double check the contour after convert to 2d platform"""
        if len(polygon_contour) < 3:
            # if the number of vertex less than 3
            return []

        for point in polygon_contour:
            # if the number of coordinate less than 3
            if len(point) < 2:
                return []
            x, y = point
            if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
                return []

        formatted_contour = [(int(point[0]), int(point[1])) for point in polygon_contour]
        return formatted_contour

    @classmethod
    def generate_image_meta_data(cls, image_file_name="", sensor_id="", view_type="plan-view"):
        """generate formatted image information for different type of cameras"""
        # get place information from user input
        image_dict = {}
        # if image is a top view image
        if view_type == "plan-view":
            place_info = cls.refine_place_info()
            image_dict = {"place": str(place_info), "view": view_type, "fileName": str(image_file_name)}
        # if image is a camera view image
        elif view_type == "camera-view":
            image_dict = {"sensorId": sensor_id, "view": view_type, "fileName": str(image_file_name)}
        return image_dict

    @classmethod
    def round_floats_in_nested_dict(cls, data, precision=6):
        """Recursively rounds all float-like values in a nested dictionary or list."""
        if isinstance(data, dict):
            return {key: cls.round_floats_in_nested_dict(value, precision) for key, value in data.items()}
        elif isinstance(data, list):
            return [cls.round_floats_in_nested_dict(item, precision) for item in data]
        elif isinstance(data, (int, float, np.float32, np.float64)):
            rounded_value = round(float(data), precision)
            return 0.0 if rounded_value == -0.0 else rounded_value
        return data  # Return other types unchanged

    @staticmethod
    def check_camera_path_and_folder_path():
        """helper method, check whether camera path and folder path are valid"""
        current_folder_path = CameraCalibrationSettings.camera_calibration_output_folder_path
        current_camera_prim_path = CameraCalibrationSettings.top_view_camera_path
        stage = omni.usd.get_context().get_stage()
        if (
            not current_folder_path
            or current_folder_path == ""
            or not USDUtil.is_valid_prim(stage=stage, prim_path=current_camera_prim_path)
        ):
            return False
        return True

    @staticmethod
    def check_place_info():
        """
        Helper method to check whether the format of the place info string is correct.
        Returns True if there is at least one valid key-value pair, otherwise False.
        """
        place_info_str = CameraCalibrationSettings.place_info

        # Split the place info string by "/"
        items = place_info_str.split("/")

        for item in items:
            try:
                # Try to extract key and value
                key, value = map(str.strip, item.split("="))

                # Check if key and value are non-empty and not "none"
                if key and value and key.lower() != "none" and value.lower() != "none":
                    return True
            except ValueError:
                continue

        return False


class CalibrationCacheFolderUtils:
    @staticmethod
    def get_top_view_image_path():
        """get top view image's file path"""
        # get output data folder
        output_folder_path = CameraCalibrationSettings.camera_calibration_output_folder_path
        # get top view image name
        top_view_image_name = CameraCalibrationSettings.get_top_view_image_name()
        return os.path.join(output_folder_path, top_view_image_name)

    @staticmethod
    def get_metadata_path():
        """return metadata file path"""
        # get output data folder
        output_folder_path = CameraCalibrationSettings.camera_calibration_output_folder_path
        # get image meta data path
        image_metadata_name = CameraCalibrationSettings.get_image_metadata_name()
        return os.path.join(output_folder_path, image_metadata_name)

    @staticmethod
    def get_debug_folder_path():
        """return path toward debug data folder"""
        # get output data folder
        output_folder_path = CameraCalibrationSettings.camera_calibration_output_folder_path
        # debug data folder is the folder to store debug information, such as polygons rendered on the topview image
        debug_data_folder_name = CameraCalibrationSettings.get_debug_folder_name()
        # ensure the debug folder exist in the device
        debug_folder_path = os.path.join(output_folder_path, debug_data_folder_name)
        return debug_folder_path

    @classmethod
    def get_fov_polygon_directory(cls):
        """Returns the path to the directory where FOV polygon visualization images are stored."""
        # Retrieve the base debug folder path
        debug_base_path = cls.get_debug_folder_path()
        # Retrieve the folder name for storing FOV polygon images
        fov_polygon_folder_name = CameraCalibrationSettings.get_fov_polygon_image_folder_name()
        # Construct the full path to the FOV polygon images directory
        fov_polygon_directory_path = os.path.join(debug_base_path, fov_polygon_folder_name)

        return fov_polygon_directory_path

    @staticmethod
    def get_calibration_sample_file_path():
        """get the sample file path"""
        EXT_PATH = (
            omni.kit.app.get_app()
            .get_extension_manager()
            .get_extension_path_by_module("isaacsim.sensors.rtx.placement")
        )
        sample_file_name = CameraCalibrationSettings.get_sample_calibration_file_name()
        sample_file_path = os.path.join(EXT_PATH, "data", sample_file_name)
        return sample_file_path

    @staticmethod
    def get_calibration_file_path():
        """get calibraiton file path"""
        output_folder_path = CameraCalibrationSettings.camera_calibration_output_folder_path
        default_calibration_file_name = CameraCalibrationSettings.get_default_calibration_file_name()
        target_calibration_file_path = os.path.join(output_folder_path, default_calibration_file_name)
        return target_calibration_file_path
