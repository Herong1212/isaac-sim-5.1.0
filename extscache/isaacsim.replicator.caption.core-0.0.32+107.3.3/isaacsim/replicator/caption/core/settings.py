import carb
import os
from omni.metropolis.utils.carb_util import CarbSettingProperty, CarbSettingMeta

EXTENSION_NAME = "isaacsim.replicator.caption.core"
PERSISTENT_SETTINGS_PREFIX = "/persistent"
VERSION = "0.0.9"


class ReplicatorCaptionSettings(metaclass=CarbSettingMeta):
    EXT_PATH = None

    # setting value that record props' address/url path
    STAGE_INFO_ROOT_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/isaacsim.replicator.caption.core/props_folder_path"
    # target camera prim used to fetch scene information
    TARGET_CAMERA_PRIM_PATH = (
        f"{PERSISTENT_SETTINGS_PREFIX}/exts/isaacsim.replicator.caption.core/target_camera_prim_path"
    )
    # target camera prim used to fetch scene information
    OBJECT_NUMBER_THRESHOLD = (
        f"{PERSISTENT_SETTINGS_PREFIX}/exts/isaacsim.replicator.caption.core/object_number_threshold"
    )
    # default object threshold value
    CACHE_DATA_FOLDER = f"{PERSISTENT_SETTINGS_PREFIX}/exts/isaacsim.replicator.caption.core/cache_data_folder"

    CHARACTERS_PARENT_PATH = "/exts/isaacsim.replicator.caption.core/characters_parent_prim_path"

    CACHE_CONFIG_FILE_PATH = (
        f"{PERSISTENT_SETTINGS_PREFIX}/exts/isaacsim.replicator.caption.core/cache_config_file_path"
    )

    STAGE_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/isaacsim.replicator.caption.core/stage_path"

    MODEL_URL = f"{PERSISTENT_SETTINGS_PREFIX}/exts/isaacsim.replicator.caption.core/model_url"
    MODEL_NAME = f"{PERSISTENT_SETTINGS_PREFIX}/exts/isaacsim.replicator.caption.core/model_name"
    API_KEY = f"{PERSISTENT_SETTINGS_PREFIX}/exts/isaacsim.replicator.caption.core/api_key"

    DB_HOST = f"{PERSISTENT_SETTINGS_PREFIX}/exts/isaacsim.replicator.caption.core/db_host"
    DB_USERNAME = f"{PERSISTENT_SETTINGS_PREFIX}/exts/isaacsim.replicator.caption.core/db_username"
    DB_PASSWORD = f"{PERSISTENT_SETTINGS_PREFIX}/exts/isaacsim.replicator.caption.core/db_password"
    DB_DATABASE = f"{PERSISTENT_SETTINGS_PREFIX}/exts/isaacsim.replicator.caption.core/db_database"
    DB_COLLECTION = f"{PERSISTENT_SETTINGS_PREFIX}/exts/isaacsim.replicator.caption.core/db_collection"

    DATA_FILE_NAME = "object_data.json"
    DEFAULT_OBJECT_THRESHOLD = 25
    # NOTE:: does not activated by defautl
    # occlusion ratio threshold: this value is used when fetching object information from target camera view
    DEFAULT_OBJECT_OCCLUSION_THRESHOLD = 0.6
    DEFAULT_DATA_OUTPUT_FOLDER = "OUTPUT_PATH"
    # NOTE:: default annotator list to fetch object data
    # Default annotator list to fetch object data from the view:
    DEFAULT_ANNOTATOR_LIST = ["camera_params", "bounding_box_2d_tight_fast", "bounding_box_2d_loose_fast", "rgb"]
    # please add the uncessary object type in here: Object with such semantic label would be ignored automatically
    UNNECESSARY_TYPE_LIST = ["floor", "wall"]

    IMAGE_FOLDER_NAME = "Image"
    DATA_FOLDER_NAME = "Data"
    CAPTION_FOLDER_NAME = "Captions"

    class AnnotatorPrefix:
        class ObjectDetection:
            GENERIC = "object_info"
            AGENT = "agent_info"

        class Others:
            CUSTOMIZED = "customized"

    def __get_value_by_key(key, default_val):
        """get setting value via setting path"""
        val = carb.settings.get_settings().get(key)
        if not val:
            val = default_val
        return val

    def __set_value_by_key(key, new_value=None, default=None):
        """set setting value to new value, allow user to input default value"""
        if new_value is None:
            carb.settings.get_settings().set(key, default)
        else:
            carb.settings.get_settings().set(key, new_value)

    def get_props_folder_path():
        """get props/asset's folder path"""
        default_root_folder_path = ""
        return ReplicatorCaptionSettings.__get_value_by_key(
            ReplicatorCaptionSettings.STAGE_INFO_ROOT_PATH, default_root_folder_path
        )

    def set_props_folder_path(new_value):
        """set props/asset's folder path"""
        ReplicatorCaptionSettings.__set_value_by_key(
            key=ReplicatorCaptionSettings.STAGE_INFO_ROOT_PATH, new_value=new_value
        )

    def get_target_camera_prim_path():
        """get target camera prim path"""
        return ReplicatorCaptionSettings.__get_value_by_key(ReplicatorCaptionSettings.TARGET_CAMERA_PRIM_PATH, None)

    def set_target_camera_prim_path(new_value):
        """set target camera prim path"""
        return ReplicatorCaptionSettings.__set_value_by_key(
            key=ReplicatorCaptionSettings.TARGET_CAMERA_PRIM_PATH, new_value=new_value
        )

    def set_output_folder_path(new_value):
        """set output folder path"""
        return ReplicatorCaptionSettings.__set_value_by_key(
            key=ReplicatorCaptionSettings.CACHE_DATA_FOLDER, new_value=new_value
        )

    def get_object_number_threshold():
        """ "get threshold value of object number when generate scene graph"""
        default_value = ReplicatorCaptionSettings.DEFAULT_OBJECT_THRESHOLD
        return ReplicatorCaptionSettings.__get_value_by_key(
            ReplicatorCaptionSettings.OBJECT_NUMBER_THRESHOLD, default_value
        )

    def get_cache_folder_path():
        """ "get folder path to output cache information"""
        default_value = ReplicatorCaptionSettings.DEFAULT_DATA_OUTPUT_FOLDER
        return ReplicatorCaptionSettings.__get_value_by_key(ReplicatorCaptionSettings.CACHE_DATA_FOLDER, default_value)

    def get_image_folder_path(sub_dir_name: str = "Ground_Truth"):
        """get image folder path to store the view image"""
        cache_folder_path = ReplicatorCaptionSettings.get_cache_folder_path()
        image_folder_name = ReplicatorCaptionSettings.IMAGE_FOLDER_NAME
        image_folder_path = os.path.join(cache_folder_path, sub_dir_name, image_folder_name)
        return image_folder_path

    def get_data_folder_path(sub_dir_name: str = "Ground_Truth"):
        """get data folder path to store the json file that records object data"""
        cache_folder_path = ReplicatorCaptionSettings.get_cache_folder_path()
        data_folder_name = ReplicatorCaptionSettings.DATA_FOLDER_NAME
        data_folder_path = os.path.join(cache_folder_path, sub_dir_name, data_folder_name)
        return data_folder_path

    def get_scene_graph_folder_path(sub_dir_name: str = "Captions"):
        """get scene graph folder path to store the json file that records object data"""
        cache_folder_path = ReplicatorCaptionSettings.get_cache_folder_path()
        caption_folder_name = ReplicatorCaptionSettings.CAPTION_FOLDER_NAME
        scene_graph_folder_path = os.path.join(cache_folder_path, sub_dir_name, caption_folder_name)
        return scene_graph_folder_path

    def get_data_file_path(file_name: str = "world_graph_scene.json"):
        """get data folder path to store the json file that records object data"""
        cache_folder_path = ReplicatorCaptionSettings.get_cache_folder_path()
        data_file_path = os.path.join(cache_folder_path, file_name)
        return data_file_path

    def characters_parent_path():
        return ReplicatorCaptionSettings.__get_value_by_key(
            ReplicatorCaptionSettings.CHARACTERS_PARENT_PATH, "/World/Characters"
        )

    def get_default_config_file_path():
        return ReplicatorCaptionSettings.EXT_PATH + "/config/default_config.yaml"

    def default_stage_path():
        return ReplicatorCaptionSettings.EXT_PATH + "/data/test_caption.usda"

    def get_config_file_path():
        default_config_file = ReplicatorCaptionSettings.get_default_config_file_path()
        return ReplicatorCaptionSettings.__get_value_by_key(
            ReplicatorCaptionSettings.CACHE_CONFIG_FILE_PATH, default_config_file
        )

    def get_stage_path():
        default_stage_path = ReplicatorCaptionSettings.default_stage_path()
        return ReplicatorCaptionSettings.__get_value_by_key(ReplicatorCaptionSettings.STAGE_PATH, default_stage_path)

    model_url = CarbSettingProperty(default_value="https://integrate.api.nvidia.com/v1", is_persistent=True)
    model_name = CarbSettingProperty(default_value="meta/llama3-8b-instruct", is_persistent=True)
    api_key = CarbSettingProperty(default_value="placeholder", is_persistent=True)

    @staticmethod
    def get_model_url() -> str:
        return ReplicatorCaptionSettings.model_url

    @staticmethod
    def get_model_name() -> str:
        return ReplicatorCaptionSettings.model_name

    @staticmethod
    def get_api_key() -> str:
        return ReplicatorCaptionSettings.api_key

    db_host = CarbSettingProperty(default_value="sc-swgpu-mongo-dsbench-dev-rw.nvidia.com", is_persistent=True)
    db_username = CarbSettingProperty(default_value="dev_dsbench_usr", is_persistent=True)
    db_password = CarbSettingProperty(default_value="placeholder", is_persistent=True)
    db_database = CarbSettingProperty(default_value="dsbench", is_persistent=True)
    db_collection = CarbSettingProperty(default_value="usd_caption", is_persistent=True)

    @staticmethod
    def get_db_host() -> str:
        return ReplicatorCaptionSettings.db_host

    @staticmethod
    def get_db_username() -> str:
        return ReplicatorCaptionSettings.db_username

    @staticmethod
    def get_db_password() -> str:
        return ReplicatorCaptionSettings.db_password

    @staticmethod
    def get_db_database() -> str:
        return ReplicatorCaptionSettings.db_database

    @staticmethod
    def get_db_collection() -> str:
        return ReplicatorCaptionSettings.db_collection
