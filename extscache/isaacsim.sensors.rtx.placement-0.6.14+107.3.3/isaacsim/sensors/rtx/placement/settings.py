from enum import Enum
from typing import Any
import carb
from omni.metropolis.utils.carb_util import CarbSettingProperty, CarbSettingMeta

PERSISTENT_SETTINGS_PREFIX = "/persistent"
EXTENSION_NAME = "isaacsim.sensors.rtx.placement"


class GeneralSetting(metaclass=CarbSettingMeta):
    """shared settings on both camera placement and camera calibration"""

    # camera parent prim path for camera calibration
    camera_parent_prim_path = CarbSettingProperty(default_value="/World/Cameras", is_persistent=True)
    # customized floor height during the camera placement
    customized_floor_height = CarbSettingProperty(default_value=0, is_persistent=True)
    # customized ceiling height during the camera placement
    customized_ceiling_height = CarbSettingProperty(default_value=-1, is_persistent=True)
    # need to check navmesh or not
    need_navmesh_check = CarbSettingProperty(default_value=True, is_persistent=True)


class CameraPlacementSettings(metaclass=CarbSettingMeta):
    """camera placement settings"""

    camera_placement_output_folder_path = CarbSettingProperty(default_value="", is_persistent=True)
    # max camera height during the camera placement
    max_camera_height = CarbSettingProperty(default_value=4.0, is_persistent=True)
    # min camera height during the camera placement
    min_camera_height = CarbSettingProperty(default_value=2.0, is_persistent=True)
    # max camera distance during the camera placement
    max_camera_distance = CarbSettingProperty(default_value=14, is_persistent=True)
    # min camera distance during the camera placement
    min_camera_distance = CarbSettingProperty(default_value=6.5, is_persistent=True)
    # max camera look down angle during the camera placement
    max_camera_look_down_angle = CarbSettingProperty(default_value=60.0, is_persistent=True)
    # min camera look down angle during the camera placement
    min_camera_look_down_angle = CarbSettingProperty(default_value=0.0, is_persistent=True)
    # focus height during the camera placement, (the height of the focus point)
    focus_height = CarbSettingProperty(default_value=0.5, is_persistent=True)
    # limit the FOV estimation based on camera distance
    limit_fov_by_distance = CarbSettingProperty(default_value=False, is_persistent=True)
    # the target coverage ratio during the camera placement
    target_coverage_ratio = CarbSettingProperty(default_value=0.9, is_persistent=True)
    # the raycast density during the camera placement
    raycast_density = CarbSettingProperty(default_value=250, is_persistent=True)
    # the estimated agent radius during the camera placement
    estimated_agent_radius = CarbSettingProperty(default_value=0.7, is_persistent=True)
    # distance step size used to sample the potential camera scope
    camera_distance_step_size = CarbSettingProperty(default_value=0.3, is_persistent=True)
    # the camera on navmesh during the camera placement
    camera_on_navmesh = CarbSettingProperty(default_value=True, is_persistent=True)
    # the minimum coverage increase during the camera placement
    min_coverage_increase = CarbSettingProperty(default_value=2, is_persistent=True)
    # the total camera number during the camera placement
    total_camera_number = CarbSettingProperty(default_value=-1, is_persistent=True)
    # the border checking index during the camera placement
    border_checking_index = CarbSettingProperty(default_value=0, is_persistent=True)
    # the patch size used to generate the patch grid on floor
    patch_size = CarbSettingProperty(default_value=0.5, is_persistent=True)
    # camera need to be placed on the navmesh
    camera_on_navmesh = CarbSettingProperty(default_value=True, is_persistent=True)
    # Stop camera placement if new camera can only see uncovered areas closer than this distance (m)
    min_view_distance = CarbSettingProperty(default_value=1, is_persistent=True)
    # the minimum number of camera that coverage any patch on the floor
    required_camera_per_patch = CarbSettingProperty(default_value=1, is_persistent=True)


class CameraCalibrationSettings(metaclass=CarbSettingMeta):
    """Settings for the camera calibration tool"""

    class PloygonType(Enum):
        Empty = 0
        SinglePolygon = 1
        MultiPolygon = 2

    # event path : camera info updated event
    Camera_Info_Updated_Event = "omni.repliator.agent.camera_calibration/Camera_Info_Updated_Event"
    camera_calibration_output_folder_path = CarbSettingProperty(default_value="", is_persistent=True)
    fov_contour_simplification_threshold = CarbSettingProperty(default_value=0, is_persistent=False)
    fov_area_filter_threshold = CarbSettingProperty(default_value=0, is_persistent=False)
    # top camera prim path
    top_view_camera_path = CarbSettingProperty(default_value="", is_persistent=False)
    # place info
    place_info = CarbSettingProperty(default_value="", is_persistent=True)
    # calibration dots' parent prim path
    calibration_prim_path = CarbSettingProperty(default_value="/World/Calibration_Dots", is_persistent=True)
    # NOTE:: this is the path of the parent prim of the generated top view camera
    top_camera_parent_prim_path = CarbSettingProperty(default_value="/World/Top_Camera", is_persistent=True)
    # prim path that contains the bunnding box of the interested area
    scene_bounding_box_path = CarbSettingProperty(default_value="", is_persistent=False)
    # the number of calibration dots
    calibration_prim_num = CarbSettingProperty(default_value=6, is_persistent=False)
    # whether show the fov polygon in the scene
    show_fov_polygon_enabled = CarbSettingProperty(default_value=False, is_persistent=False)
    # whether draw the camera view images
    capture_camera_view_images_enabled = CarbSettingProperty(default_value=False, is_persistent=False)
    # the seed used to generate the calibration dots
    # NOTE:: this value is different from the seed used in the camera placement
    raycast_seed = CarbSettingProperty(default_value=100, is_persistent=True)

    # ---------------------------- camera placement settings
    top_view_camera_prim_name = "Calibration_Top_Camera"
    # the recommended calibration density, value that smaller than this will be set to this value
    recommended_calibration_seed = 100
    # topview image of the stage
    top_image_name = "Top.png"
    # store debug datas into a seperate debugging folder.
    debug_data_folder_name = "Debug"
    # Debug Data :: fov polygon image directory
    fov_polygon_image_folder_name = "fieldOfViewPolygon"
    image_metadata_name = "imageMetadata.json"
    # the name of the sample calibration file
    sample_calibration_file_name = "calibration_template.json"
    # the name of the calibration info file
    default_calibration_file_name = "calibration.json"

    @staticmethod
    def get_top_view_image_name() -> str:
        """Get the filename for the top view camera image."""
        return CameraCalibrationSettings.top_image_name

    @staticmethod
    def get_debug_folder_name() -> str:
        """Get the name of the debug data folder."""
        return CameraCalibrationSettings.debug_data_folder_name

    @staticmethod
    def get_image_metadata_name() -> str:
        """Get the filename for image metadata."""
        return CameraCalibrationSettings.image_metadata_name

    @staticmethod
    def get_fov_polygon_image_folder_name() -> str:
        """Get the folder name for field of view polygon images."""
        return CameraCalibrationSettings.fov_polygon_image_folder_name

    @staticmethod
    def get_top_view_camera_prim_name() -> str:
        """Get the prim name for the top view camera."""
        return CameraCalibrationSettings.top_view_camera_prim_name

    @staticmethod
    def get_sample_calibration_file_name() -> str:
        """Get the filename for the sample calibration file."""
        return CameraCalibrationSettings.sample_calibration_file_name

    @staticmethod
    def get_default_calibration_file_name() -> str:
        """Get the filename for the default calibration file."""
        return CameraCalibrationSettings.default_calibration_file_name

    @staticmethod
    def get_setting_path(setting_name: str) -> str:
        """Get the full setting path for a given setting name.

        Args:
            setting_name: Name of the setting

        Returns:
            Full path to the setting
        """
        return f"{PERSISTENT_SETTINGS_PREFIX}/{EXTENSION_NAME}/{setting_name}"
    
