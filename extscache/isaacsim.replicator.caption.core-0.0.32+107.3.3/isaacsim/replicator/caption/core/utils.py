import subprocess
import requests
import json
import os
from pathlib import Path

import carb
import numpy as np
import omni
import omni.usd
import Semantics
from pxr import Usd, UsdGeom
from omni.metropolis.utils.file_util import YamlFileUtil

from .settings import ReplicatorCaptionSettings, VERSION


class Utils:
    def get_object_reference(prim_path: str = "", stage=None):
        """check the object reference url, return true if it is from the target asset path"""
        asset_path = None
        if stage is None:
            stage = omni.usd.get_context().get_stage()
        if not prim_path:
            return asset_path

        # get prim from prim path
        prim = stage.GetPrimAtPath(prim_path)
        # if the prim is a payload prim
        try:
            ref_and_layers = omni.usd.get_composed_payloads_from_prim(prim, False)
        except:
            return None
        if len(ref_and_layers) == 0:
            # else if the prim is a reference prim
            ref_and_layers = omni.usd.get_composed_references_from_prim(prim, False)
        if len(ref_and_layers) > 0:
            ref, layer = ref_and_layers[0]
            asset_path = ref.assetPath
        else:
            return asset_path

        # if asset path is still none, return
        if asset_path is None:
            return asset_path

        # ensure the output is an obsolute path
        if not Utils.is_abs(asset_path):
            # get current stage's url path:
            asset_info = layer.GetAssetInfo()
            if asset_info is None and os.path.isabs(asset_path):
                return asset_path
            elif asset_info is None:
                return None
            current_stage_url = asset_info["url"]
            # get full asset path:
            asset_path = omni.client.combine_urls(current_stage_url, asset_path)

        return asset_path

    def get_current_stage_url():
        """get current stage's url"""
        return omni.usd.get_context().get_stage_url()

    def is_abs(path):
        """check whether the target path is an absolute path"""
        parts = omni.client.break_url(path)
        return Path(parts.path).is_absolute() and bool(parts.scheme)

    def get_captioned_props_list():
        """get all target usd file path with the props folder"""
        usd_file_list = []
        target_asset_folder = ReplicatorCaptionSettings.get_props_folder_path()
        result, file_list = omni.client.list("{}/".format(target_asset_folder))
        if result != omni.client.Result.OK:
            carb.log_error("Unable to get character assets from provided asset path.")
            return usd_file_list
        # Prune items from folder list that are not directories.

        # in this example extension we assume that object is under the first level of the target asset path.
        for file in file_list:
            relative_path = file.relative_path
            post_fix = file.relative_path[file.relative_path.rfind(".") + 1 :].lower()
            if post_fix == "usd" or post_fix == "usda":
                # get the absolute path
                usd_file_list.append(relative_path)
                # compose the full path
                full_usd_path = omni.client.combine_urls("{}/".format(target_asset_folder), relative_path)
                usd_file_list.append(full_usd_path)

        return usd_file_list

    def store_as_json_file(file_path: str, info_data: dict):
        """store a dict in to json file"""
        # get target file's folder:
        folder_path = os.path.dirname(file_path)
        # check whether target folder exist:
        Utils.check_folder_exist(folder_path=folder_path, create_one=True)
        try:
            # attempt to store the info
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(info_data, file, ensure_ascii=False, indent=4, default=Utils.numpy_encoder)
            print(f"[IRC] The JSON has been successfully saved to '{file_path}'.")
        except Exception as e:
            print(f"Error saving the dictionary to '{file_path}': {e}")
        pass

    def load_json_file(file_path: str):
        """load json file from target path"""
        # check whether json file exist
        folder_path = os.path.dirname(file_path)
        if not os.path.exists(folder_path):
            print(f"Warning: The folder '{folder_path}' does not exist.")
            return None

        # if the file does not exist
        if not os.path.isfile(file_path):
            print(f"Warning: Fail to read and the file. '{file_path}' does not exist.")
            return None

        # read the json file
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data
        except Exception as e:
            print(f"Error reading the file '{file_path}': {e}")
            return None

    def get_prim_attribute(prim, attribute):
        """get current prim attribute value"""
        if prim.HasAttribute(str(attribute)):
            prim_value = prim.GetAttribute(str(attribute)).Get()
            return prim_value
        else:
            return None

    def filter_dict_by_keys(data_dict, keys_to_keep):
        """
        only keepe the key-value pairs that are recoreded in keys_to_keep 。
        """
        keys_to_keep = set(keys_to_keep)

        for key in list(data_dict.keys()):
            if key not in keys_to_keep:
                data_dict.pop(key)

        return data_dict

    def check_folder_exist(folder_path: str, create_one: bool = False):
        """check whether current folder exist"""
        if not os.path.exists(folder_path):
            carb.log_info(f"Folder '{folder_path}' does not exist.")
            if create_one:
                # create folder on target path
                os.makedirs(folder_path)
                carb.log_info(f"Folder '{folder_path}' created.")
        else:
            carb.log_info(f"Folder '{folder_path}' already exists.")

    def get_prim_position(prim):
        """helper function get prim transform in the stage"""
        prim_transform = omni.usd.get_world_transform_matrix(prim)
        # get prim position from transformation matrix
        prim_translation = prim_transform.ExtractTranslation()
        return prim_translation

    def camera_path_to_id(camera_path):
        """get camera id from camera path"""
        # replace all the "/" sign in camera path with "_"
        camera_path = str(camera_path).replace("/", "_")
        if camera_path.startswith("_") or camera_path.startswith("/"):
            return camera_path[1:]
        return camera_path

    def is_valid_camera_path(prim_path: str):
        """check whether target prim path is valid camera path"""
        if prim_path is None or str(prim_path) == "":
            return False
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(str(prim_path))
        if (prim is None) or (not prim.IsValid()) or (not prim.IsActive()):
            return False

        return prim.GetTypeName() == "Camera"

    def edit_all_prims_properties(target_prim_list, target_property_name, target_property_value):
        """batch manipulate prim's property value"""
        # set all character's target property
        for target_prim in target_prim_list:
            if not target_prim.HasAttribute(target_property_name):
                carb.log_info(
                    "Warning as Message:: {target_prim_path} do not have attribute :: {target_property_name}".format(
                        target_prim_path=str(target_prim.GetPrimPath()), target_property_name=target_property_name
                    )
                )
                continue
            target_prim.GetAttribute(target_property_name).Set(target_property_value)

    def get_prim_semantic_label(target_prim):
        """get semantic label of the objects"""
        # get current character prim list in the stage
        semantics_data = None
        if not target_prim.HasAPI(Semantics.SemanticsAPI):
            return semantics_data

        # get target object's "class" value
        for name in target_prim.GetPropertyNames():
            if str(name).startswith("semantic:Semantics") and str(name).endswith("params:semanticType"):
                semantics_type = target_prim.GetAttribute(str(name))
                # if str(semantics_type.Get()).lower() == "class":
                semantics_data_name = str(name)[:-4] + "Data"
                semantics_data = target_prim.GetAttribute(str(semantics_data_name)).Get()

        # lowercase the semantic label
        semantics_data = str(semantics_data).lower()
        return semantics_data

    def get_prim_bbox_scale(prim):
        """get prim bbox scale"""
        box_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        bound = box_cache.ComputeWorldBound(prim)
        range = bound.ComputeAlignedBox()
        bboxMin = range.GetMin()
        bboxMax = range.GetMax()
        x_min, y_min, z_min = bboxMax[0], bboxMax[1], bboxMax[2]
        x_max, y_max, z_max = bboxMin[0], bboxMin[1], bboxMin[2]
        scale_x = x_max - x_min
        scale_y = y_max - y_min
        scale_z = z_max - z_min

        return (scale_x, scale_y, scale_z)

    def get_prim_corners(prim):
        """fetch prim corners"""
        bound = UsdGeom.Imageable(prim).ComputeWorldBound(0, "default")
        bound_range = bound.ComputeAlignedBox()
        result = []
        for i in range(8):
            result.append(bound_range.GetCorner(i))
        corners = np.array(result)
        return corners

    def convert_to_camera_space(world_transform, camera_view_matrix):
        """convert world space transform to camera space"""
        camera_view_transform = np.matmul(world_transform, camera_view_matrix)
        return camera_view_transform

    def world_translate_to_camera(pt, camera_view):
        """convert a 3d dot into camera space"""
        homo_translate = np.array([pt[0], pt[1], pt[2], 1])
        camera_space = homo_translate @ camera_view
        return camera_space

    def numpy_encoder(obj):
        """help the writer to output data in correct format"""
        if isinstance(obj, np.void):
            return Utils.convert_to_serialized_dict(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.generic):
            return obj.item()

        return obj

    def extent_dimension(extents):
        """extend the demension of input data to fit the format of helper method parameter"""
        extents_batch = {
            "x_min": np.expand_dims(extents["x_min"], axis=0),
            "x_max": np.expand_dims(extents["x_max"], axis=0),
            "y_min": np.expand_dims(extents["y_min"], axis=0),
            "y_max": np.expand_dims(extents["y_max"], axis=0),
            "z_min": np.expand_dims(extents["z_min"], axis=0),
            "z_max": np.expand_dims(extents["z_max"], axis=0),
            "transform": np.expand_dims(extents["transform"], axis=0),
        }
        return extents_batch

    def capture_usd_info(prim_path, stage, verbose=False):
        """
        Capture the prim path and its corresponding usd path.

        prim_path (str): The path to the prim.
        stage (Usd.Stage): The stage object.
        verbose (bool): Whether to output verbose information.
        """

        # usd_path = Utils.get_object_reference(prim_path, stage)

        def get_parent_prim(prim, stage):
            """
            Iteratively search for the parent prim that has a valid usd path.
            """
            prim_path = str(prim.GetPath())
            usd_path = Utils.get_object_reference(prim_path, stage)
            if prim_path.count("/") <= 2 or usd_path is not None:
                return prim_path, usd_path
            else:
                parent_prim = prim.GetParent()
                final_prim, usd_path = get_parent_prim(parent_prim, stage)
                return final_prim, usd_path

        prim = stage.GetPrimAtPath(prim_path)
        final_prim_path, usd_path = get_parent_prim(prim, stage)
        if usd_path is None:
            usd_path = "None"
            if verbose:
                print(f"[Warning] {prim_path} has no usd path.".format(prim_path=final_prim_path))

        return final_prim_path, usd_path

    def enable_semantics(prim, semantic_label, semantic_class="object"):
        """
        Enables the semantics API on the prim and sets the semantic label and class.

        prim (Usd.Prim): The prim to enable semantics on.
        semantic_label (str): The semantic label to set.
        semantic_class (str): The semantic class to set.
        """
        if not prim.HasAPI(Semantics.SemanticsAPI):
            sem = Semantics.SemanticsAPI.Apply(prim, "Semantics")
            sem.CreateSemanticTypeAttr()
            sem.CreateSemanticDataAttr()
        else:
            # sem = Semantics.SemanticsAPI.Get(prim, "Semantics")
            return
        sem.GetSemanticTypeAttr().Set(semantic_class)
        sem.GetSemanticDataAttr().Set(semantic_label)


def check_prim_character(prim):
    """check whether the prim is a character

    prim (Usd.Prim): The prim to check.
    """
    is_character = False
    for p in Usd.PrimRange(prim):
        if p.GetTypeName() == "SkelRoot":
            is_character = True
            break

    return is_character


def get_annotate_semantic_label(semantic_label_dict):
    """get semantic label of the objects, given the semantic label dict"""
    sem_name = list(semantic_label_dict.values())[0]
    sem_label = sem_name.split("~~~")[-1]
    return sem_label


def retrieve_api_token():
    """
    Retrieves the API token from the Azure OpenAI service.
    """

    if not os.getenv("SSA_CLIENT_ID") or not os.getenv("SSA_CLIENT_SECRET"):
        print(
            "[Warning] Please set the environment variables SSA_CLIENT_ID and SSA_CLIENT_SECRET for object caption generation"
        )

    ssa_client_id = os.getenv("SSA_CLIENT_ID")
    ssa_client_secret = os.getenv("SSA_CLIENT_SECRET")

    url = "https://5kbfxgaqc3xgz8nhid1x1r8cfestoypn-trofuum-oc.ssa.nvidia.com/token"

    # Basic Authentication tuple: (username, password)
    auth = (ssa_client_id, ssa_client_secret)

    # The same headers as in curl
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # The form data (POST body)
    data = {"grant_type": "client_credentials", "scope": "openai-readwrite"}

    # Send POST request
    response = requests.post(url, auth=auth, headers=headers, data=data)

    # Check status and print response
    if response.status_code == 200:
        print("[IRC] Azure OpenAI retrieved successfully")
    else:
        print(f"[Error] Request failed with status code {response.status_code}")
        print(response.text)
        return None

    return response.json()


def update_nested_configs(original, new_values):
    """
    Recursively update a nested dictionary with new values, retaining all existing keys and values not mentioned in the new dictionary.

    Args:
        original (dict): The original nested dictionary to be updated.
        new_values (dict): The dictionary containing the new values.

    Returns:
        dict: The updated nested dictionary.
    """
    for key, value in new_values.items():
        if isinstance(value, dict) and isinstance(original.get(key), dict):
            # If both are dictionaries, recurse into them
            original[key] = update_nested_configs(original[key], value)
        else:
            # Otherwise, update or add the key-value pair
            original[key] = value
    return original


class ConfigFileReader:
    """
    Read and load the config file from the target path.

    Attributes:
        configs (dict): The dictionary containing the caption configuration.

    """

    def __init__(self):
        self.configs = self.load_defaults()
        config_file_path = ReplicatorCaptionSettings.get_config_file_path()
        self.load_config(config_file_path)

    def load_config(self, config_path):
        """load config file from target path.

        config_path (str): The path to the config file.
        """
        if not os.path.exists(config_path):
            raise Exception(f"Config file does not exist at {config_path}")

        read_configs = YamlFileUtil.load_yaml(config_path)

        self.check_configs(read_configs)

        # update configs
        self.configs = update_nested_configs(self.configs, read_configs)

        # always set export_world to False in case of old config files
        self.configs["isaacsim.replicator.caption.core"]["caption_configs"]["export_world"] = False

    def load_defaults(self):
        """load default config values.

        Returns:
            dict: The dictionary containing the default caption configuration.
                version (str): The version of the config file.
                camera_prim_path (str): The path to the camera prim. Can be updated from UI.
                scene_path (str): The path to the scene.
                caption_configs (dict): The dictionary containing the caption configuration.
                    pruning_ratio (float): the ratio of preserved edges after pruning. Default is 1.0.
                    global_caption (bool): whether to generate global caption. Default is False.
                    qa_caption (bool): whether to generate question and answer caption. Default is False.
                    brief_caption (bool): whether to generate brief caption. Default is False.
                    visualize_caption (bool): whether to generate visualized caption image. Default is True.
                    max_object_capacity (int): the maximum number of objects in the scene graph. Default is 100.
                    save_full_scene_graph (bool): whether to save full scene graph. Default is False.
                    save_pruned_scene_graph (bool): whether to save pruned scene graph. Default is True.
                    export_edges (bool): whether to export edges. Default is True.
                    caption_only (bool): whether to only use prims with its usd object caption avaialble online. Default is True.
                    export_world (bool): whether to export world 3d locations. Default is False.
                    attach_label_to_usd (bool): whether to attach prim path basename as semantic label of the prim. Default is False.
                    use_ai_label (bool): whether to use AI semantic label for PrimNode, default is False.
                    verbose (bool): whether to output verbose information of scene graph construction. Default is False.
                    random_seed (int): the random seed for scene graph pruning when pruning ratio < 1.0. Default is 0.
                output_path (str): The path to the output folder.

        """
        default_dict = {
            "isaacsim.replicator.caption.core": {
                "version": VERSION,
                "camera_prim_path": None,
                "scene_path": None,
                "caption_configs": {
                    "save_full_scene_graph": True,
                    "save_pruned_scene_graph": True,
                    "attach_label_to_usd": False,
                    "use_ai_label": False,
                    "visualize_caption": True,
                    "max_object_capacity": 100,
                    "export_edges": True,
                    "caption_only": True,
                    "global_caption": False,
                    "qa_caption": False,
                    "brief_caption": False,
                    "pruning_ratio": 1.0,
                    "export_world": True,
                    "verbose": False,
                    "random_seed": 0,
                },
                "output_path": None,
            }
        }

        return default_dict

    def get_configs(self):
        """
        A getter of the configs attribute.
        """
        return self.configs

    def check_configs(self, read_configs):
        """check if the config values are valid.

        read_configs (dict): The dictionary containing caption configuration.
        """
        # check extension title
        if "isaacsim.replicator.caption.core" not in read_configs:
            raise Exception(
                "Config file does not contain the correct extension title, expecting isaacsim.replicator.caption.core"
            )

        # check config version
        if "version" not in read_configs["isaacsim.replicator.caption.core"]:
            raise Exception("Config file does not contain the correct version number")

        if read_configs["isaacsim.replicator.caption.core"]["version"] != VERSION:
            raise Exception(
                f"Config file version {read_configs['isaacsim.replicator.caption.core']['version']} does not match the current version {VERSION}"
            )

        # check if there's wrong key in the config file
        for key in read_configs["isaacsim.replicator.caption.core"]:
            if key not in self.configs["isaacsim.replicator.caption.core"]:
                raise Exception(f"Config file contains invalid key: {key}")

        for key in read_configs["isaacsim.replicator.caption.core"]["caption_configs"]:
            if key not in self.configs["isaacsim.replicator.caption.core"]["caption_configs"]:
                raise Exception(f"Config file contains invalid key: {key}")
