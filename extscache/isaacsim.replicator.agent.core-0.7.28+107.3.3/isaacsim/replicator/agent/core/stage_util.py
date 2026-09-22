from enum import Enum

import carb
import omni.usd
import omni.client
from isaacsim.core.utils import prims, semantics
from isaacsim.core.utils.rotations import lookat_to_quatf
from pxr import Gf, Sdf, Usd, UsdGeom

from .randomization.randomizer_util import RandomizerUtil
from .settings import Settings, AssetPaths, PrimPaths

from omni.anim.people.scripts.custom_command.populate_anim_graph import populate_anim_graph


class StageUtil:
    def open_stage(usd_path: str, ignore_unsave=True):
        if not Usd.Stage.IsSupportedFile(usd_path):
            raise ValueError("Only USD files can be loaded")
        import carb.settings
        import omni.kit.window.file

        IGNORE_UNSAVED_CONFIG_KEY = "/app/file/ignoreUnsavedStage"
        old_val = carb.settings.get_settings().get(IGNORE_UNSAVED_CONFIG_KEY)
        carb.settings.get_settings().set(IGNORE_UNSAVED_CONFIG_KEY, ignore_unsave)
        omni.kit.window.file.open_stage(usd_path, omni.usd.UsdContextInitialLoadSet.LOAD_ALL)
        carb.settings.get_settings().set(IGNORE_UNSAVED_CONFIG_KEY, old_val)

    # Set the xform transformation type to be Scale, Orient, Trans, and return the original order
    # NOTE::I am planning to move this part to the util extension, since the camera calibration require the same feature
    def set_xformOpType_SOT():
        xformoptype_setting_path = "/persistent/app/primCreation/DefaultXformOpType"
        original_xform_order_setting = carb.settings.get_settings().get(xformoptype_setting_path)
        carb.settings.get_settings().set(xformoptype_setting_path, "Scale, Orient, Translate")
        return original_xform_order_setting

    def recover_xformOpType(original_xform_order_setting):
        xformoptype_setting_path = "/persistent/app/primCreation/DefaultXformOpType"
        carb.settings.get_settings().set(xformoptype_setting_path, original_xform_order_setting)

    def fetch_semantic_label(target_prim, target_semantic_type: str = "class"):
        """fetch first semantic label with target type from the prim"""
        semantic_label = None
        # fetch all sematic labels attached on the object
        semantic_label_dict = semantics.get_semantics(target_prim)
        for key, type_to_vlaue in semantic_label_dict.items():
            semantic_type, semantic_value = tuple(type_to_vlaue)
            # ignore the case difference
            if str(semantic_type).lower() == target_semantic_type.lower():
                semantic_label = semantic_value
                break
        return semantic_label


class CameraUtil:
    def get_camera_name_by_index(i):
        if i == 0:
            return "Camera"
        elif i < 10:
            return "Camera_0" + str(i)
        else:
            return "Camera_" + str(i)

    def has_a_valid_name(name):
        if name == "Camera":
            return True
        # if name starts with "Camera"
        if name.startswith("Camera_"):
            return True
        return False

    def get_camera_name(camera_prim):
        return camera_prim.GetName()

    def get_camera_name_without_prefix(camera_prim):
        camera_name = None
        name = CameraUtil.get_camera_name(camera_prim)
        if name != None and CameraUtil.has_a_valid_name(name):
            if name == "Camera":
                return ""
            camera_name = name.split("_")[1]
        # camera_name will be None if invalid
        return camera_name

    def get_cameras_in_stage():
        camera_list = []
        # get camera root prim in the stage:
        camera_root_prim = CameraUtil.get_camera_root_prim()

        # if the camera root prim is not valid: return an emtpy list
        if camera_root_prim is None:
            return camera_list

        # all child camera prim would be added to the list:
        for camera_prim in camera_root_prim.GetChildren():
            if camera_prim.GetTypeName() == "Camera":
                camera_list.append(camera_prim)

        # then we sorted the camera prim base on their prim Name
        camera_list = sorted(camera_list, key=lambda camera: camera.GetName())
        return camera_list

    def set_camera(camera_prim, spawn_location=None, spawn_rotation=None, focallength=None):
        if spawn_location is None:
            spawn_location = Gf.Vec3d(0.0)

        if (not RandomizerUtil.aim_at_characters()) or (spawn_rotation is None):
            # Camera height is fixed in 5 by default
            camera_pos = Gf.Vec3d(spawn_location[0], spawn_location[1], 5)
        else:
            camera_pos = Gf.Vec3d(spawn_location[0], spawn_location[1], spawn_location[2])

        if spawn_rotation is None:
            # Camera will be always looking at the origin when it spawns
            spawn_rotation = Gf.Quatd(lookat_to_quatf(Gf.Vec3d(0.0), camera_pos, Gf.Vec3d(0, 0, 1)))

        camera_prim.GetAttribute("xformOp:orient").Set(spawn_rotation)
        camera_prim.GetAttribute("xformOp:translate").Set(camera_pos)

        if focallength is not None:
            camera_prim.GetAttribute("focalLength").Set(focallength)

    def spawn_camera(spawn_path=None, spawn_location=None, spawn_rotation=None, focallength=None):
        # set xformOp order to Scale, Orient, Translate, and store the setting
        original_xform_order_setting = StageUtil.set_xformOpType_SOT()
        stage = omni.usd.get_context().get_stage()
        camera_path = ""
        if spawn_path:
            camera_path = spawn_path
        else:
            camera_path = Sdf.Path(
                omni.usd.get_stage_next_free_path(stage, PrimPaths.cameras_parent_path() + "/Camera", False)
            )

        omni.kit.commands.execute("CreatePrimCommand", prim_type="Camera", prim_path=camera_path, select_new_prim=False)
        camera_prim = stage.GetPrimAtPath(camera_path)
        CameraUtil.set_camera(camera_prim, spawn_location, spawn_rotation, focallength)

        # set the xform setting back to original value
        StageUtil.recover_xformOpType(original_xform_order_setting)
        return camera_prim

    def delete_camera_prim(cam_name):
        stage = omni.usd.get_context().get_stage()
        if not Sdf.Path.IsValidPathString(PrimPaths.cameras_parent_path()):
            carb.log_error(str(PrimPaths.cameras_parent_path()) + "is not a valid prim path")
            return
        camera_prim = stage.GetPrimAtPath("{}/{}".format(PrimPaths.cameras_parent_path(), cam_name))
        if camera_prim and camera_prim.IsValid() and camera_prim.IsActive():
            prims.delete_prim(camera_prim.GetPath())

    def delete_camera_prims():
        camera_root_prim = CameraUtil.get_camera_root_prim()
        for camera_prim in camera_root_prim.GetChildren():
            if camera_prim and camera_prim.IsValid() and camera_prim.IsActive():
                prims.delete_prim(camera_prim.GetPath())

    def get_camera_root_prim():
        stage = omni.usd.get_context().get_stage()
        if not Sdf.Path.IsValidPathString(PrimPaths.cameras_parent_path()):
            carb.log_error(str(PrimPaths.cameras_parent_path()) + "is not a valid prim path")
            return None
        camera_root_prim = stage.GetPrimAtPath(PrimPaths.cameras_parent_path())
        if camera_root_prim and camera_root_prim.IsValid() and camera_root_prim.IsActive():
            return camera_root_prim

        carb.log_warn("No valid camera root prim exist.")
        return None


class StereoCamUtil:

    RIGHT_CAMERA_PREFIX = "_R"

    class Camera_Type(Enum):
        left_camera = 0
        right_camera = 1
        unknown = 2

    def get_camera_type(target_prim_path: str):
        """check whether the camera is a left camrea"""
        # In this demo version:  We use original camera set to generate stereo camera pair
        if target_prim_path.endswith(StereoCamUtil.RIGHT_CAMERA_PREFIX):
            return StereoCamUtil.Camera_Type.right_camera
        else:
            return StereoCamUtil.Camera_Type.left_camera

    def get_paired_stereo_camera_path(target_prim_path):
        """get target_camera_path as input, either left or right, get paired stereo camera path"""
        if StereoCamUtil.get_camera_type(target_prim_path) == StereoCamUtil.Camera_Type.left_camera:
            return target_prim_path + StereoCamUtil.RIGHT_CAMERA_PREFIX
        if StereoCamUtil.get_camera_type(target_prim_path) == StereoCamUtil.Camera_Type.right_camera:
            left_camera_prim_path = target_prim_path[: -len(StereoCamUtil.RIGHT_CAMERA_PREFIX)]
            return left_camera_prim_path


class LidarCamUtil:
    def get_lidar_name_by_index(i):
        if i == 0:
            return "Lidar"
        elif i < 10:
            return "Lidar_0" + str(i)
        else:
            return "Lidar_" + str(i)

    # check lidar name base on format
    def has_a_valid_name(name):
        if name == "Lidar":
            return True
        # if name starts with "Lidar"
        if name.startswith("Lidar_"):
            return True
        return False

    def get_lidar_name(lidar_prim):
        return lidar_prim.GetName()

    # return the actual name of the lidar camera, should be the part after "Lidar_"
    def get_lidar_name_without_prefix(lidar_prim):
        lidar_name = None
        name = LidarCamUtil.get_lidar_name(lidar_prim)
        # Return none if not a valid name
        if name != None and LidarCamUtil.has_a_valid_name(name):
            if name == "Lidar":
                return ""
            lidar_name = name.split("_")[1]
        return lidar_name

    # get lidar camera root prim
    def get_lidar_camera_root_prim():
        stage = omni.usd.get_context().get_stage()
        # if the lidar camera root prim does not exist, return empty list
        if not Sdf.Path.IsValidPathString(PrimPaths.lidar_cameras_parent_path()):
            carb.log_error(str(PrimPaths.lidar_cameras_parent_path()) + "is not a valid prim path")
            return None
        # fetch and return lidar camera root prim
        lidar_root_prim = stage.GetPrimAtPath(PrimPaths.lidar_cameras_parent_path())
        if lidar_root_prim and lidar_root_prim.IsValid() and lidar_root_prim.IsActive():
            return lidar_root_prim

        carb.log_warn("No valid camera root prim exist.")
        return None

    # get all camera prims under lidar camera root prim
    def get_lidar_cameras_in_stage():
        lidar_camera_list = []
        # get lidar camera root prim
        camera_root_prim = LidarCamUtil.get_lidar_camera_root_prim()
        # if the camera root prim is not valid: return an emtpy list
        if camera_root_prim is None:
            return lidar_camera_list

        # all child camera prim would be added to the list:
        for lidar_camera_prim in camera_root_prim.GetChildren():
            if lidar_camera_prim.GetTypeName() == "Camera":
                lidar_camera_list.append(lidar_camera_prim)

        lidar_camera_list = sorted(lidar_camera_list, key=lambda camera: camera.GetName())
        return lidar_camera_list

    # get all the lidar cameras that has a matching camera in stage
    def get_valid_lidar_cameras_in_stage():
        valid_lidar_camera_list = []
        lidar_camera_list = LidarCamUtil.get_lidar_cameras_in_stage()

        # For matching names with Lidar
        camera_list = CameraUtil.get_cameras_in_stage()

        # Check if they have a matching camera
        for lidar_camera in lidar_camera_list:
            lidar_name = LidarCamUtil.get_lidar_name_without_prefix(lidar_camera)
            has_match = False
            for camera in camera_list:
                if lidar_name == CameraUtil.get_camera_name_without_prefix(camera):
                    has_match = True
                    valid_lidar_camera_list.append(lidar_camera)
            if not has_match:
                carb.log_warn(LidarCamUtil.get_lidar_name(lidar_camera) + " has no matching camera")
        return valid_lidar_camera_list

    def spawn_lidar_camera(spawn_path=None, spawn_location=None, spawn_rotation=None, focallength=None):

        # ensure the default orientation system is base on orient system :
        original_xform_order_setting = StageUtil.set_xformOpType_SOT()

        stage = omni.usd.get_context().get_stage()

        camera_path = ""
        if spawn_path:
            camera_path = spawn_path
        else:
            camera_path = Sdf.Path(
                omni.usd.get_stage_next_free_path(stage, PrimPaths.lidar_cameras_parent_path() + "/Lidar", False)
            )

        camera_name = str(camera_path).replace(PrimPaths.lidar_cameras_parent_path(), "")
        camera_prim = stage.GetPrimAtPath(camera_path)

        lidar_config = "Example_Solid_State"
        _, sensor = omni.kit.commands.execute(
            "IsaacSensorCreateRtxLidar",
            path=camera_name,
            parent=PrimPaths.lidar_cameras_parent_path(),
            config=lidar_config,
        )

        camera_prim = stage.GetPrimAtPath(camera_path)
        CameraUtil.set_camera(camera_prim, spawn_location, spawn_rotation, focallength)

        # set the xform setting back to original value
        StageUtil.recover_xformOpType(original_xform_order_setting)
        return camera_prim

    # Delete one lidar camera prim by the given name
    def delete_lidar_camera_prim(cam_name):
        stage = omni.usd.get_context().get_stage()
        if not Sdf.Path.IsValidPathString(PrimPaths.lidar_cameras_parent_path()):
            carb.log_error(str(PrimPaths.lidar_cameras_parent_path()) + "is not a valid prim path")
            return
        lidar_camera_prim = stage.GetPrimAtPath("{}/{}".format(PrimPaths.lidar_cameras_parent_path(), cam_name))
        if lidar_camera_prim and lidar_camera_prim.IsValid() and lidar_camera_prim.IsActive():
            prims.delete_prim(lidar_camera_prim.GetPath())

    # Delete all lidar camera prims in the stage
    def delete_lidar_camera_prims():
        stage = omni.usd.get_context().get_stage()
        if not Sdf.Path.IsValidPathString(PrimPaths.lidar_cameras_parent_path()):
            carb.log_error(str(PrimPaths.lidar_cameras_parent_path()) + "is not a valid prim path")
            return
        lidar_camera_root_prim = stage.GetPrimAtPath(PrimPaths.lidar_cameras_parent_path())
        if lidar_camera_root_prim and lidar_camera_root_prim.IsValid() and lidar_camera_root_prim.IsActive():
            for lidar_camera_prim in lidar_camera_root_prim.GetChildren():
                if lidar_camera_prim and lidar_camera_prim.IsValid() and lidar_camera_prim.IsActive():
                    prims.delete_prim(lidar_camera_prim.GetPath())


class CharacterUtil:
    def get_character_skelroot_by_root(character_prim):
        for prim in Usd.PrimRange(character_prim):
            if prim.GetTypeName() == "SkelRoot":
                return prim
        return None

    def get_character_name_by_index(i):
        if i == 0:
            return "Character"
        elif i < 10:
            return "Character_0" + str(i)
        else:
            return "Character_" + str(i)

    def get_character_name(character_prim):
        # For characters under /World/Characters, names are root names
        # For the rest, names are skelroot names
        prim_path = prims.get_prim_path(character_prim)
        if prim_path.startswith(PrimPaths.characters_parent_path()):
            return prim_path.split("/")[3]
        else:
            return prim_path.split("/")[-1]

    def get_character_pos(character_prim):
        matrix = omni.usd.get_world_transform_matrix(character_prim)
        return matrix.ExtractTranslation()

    def get_characters_root_in_stage(count=-1, count_invisible=False):
        stage = omni.usd.get_context().get_stage()
        character_list = []
        character_root_path = PrimPaths.characters_parent_path()

        if stage is None:
            return []

        folder_prim = stage.GetPrimAtPath(character_root_path)

        if folder_prim is None or (not folder_prim.IsValid()) or (not folder_prim.IsActive()):
            return []

        children = folder_prim.GetAllChildren()
        for c in children:
            if len(character_list) >= count and count != -1:  # Get all if count is -1
                break
            if count_invisible == True or UsdGeom.Imageable(c).ComputeVisibility() != UsdGeom.Tokens.invisible:
                character_list.append(c)
        return character_list

    def get_characters_in_stage(count=-1, count_invisible=False):
        # Get a list of SkelRoot prims as characters
        stage = omni.usd.get_context().get_stage()
        character_root_path = PrimPaths.characters_parent_path()
        character_root = stage.GetPrimAtPath(character_root_path)
        character_list = []
        for prim in Usd.PrimRange(character_root):
            if len(character_list) >= count and count != -1:  # Get all if count is -1
                break
            if prim.GetTypeName() == "SkelRoot":
                if count_invisible == True or UsdGeom.Imageable(prim).ComputeVisibility() != UsdGeom.Tokens.invisible:
                    character_list.append(prim)
        return character_list

    def load_character_usd_to_stage(character_usd_path, spawn_location, spawn_rotation, character_stage_name):
        # ensure the default orientation system is base on orient system :
        original_xform_order_setting = StageUtil.set_xformOpType_SOT()
        stage = omni.usd.get_context().get_stage()
        # This automatically append number to the character name
        character_stage_name = omni.usd.get_stage_next_free_path(
            stage,
            f"{PrimPaths.characters_parent_path()}/{character_stage_name}",
            False,
        )
        # Load usd into stage and set character translation and rotation.
        prim = prims.create_prim(character_stage_name, "Xform", usd_path=character_usd_path)
        prim.GetAttribute("xformOp:translate").Set(
            Gf.Vec3d(float(spawn_location[0]), float(spawn_location[1]), float(spawn_location[2]))
        )
        if type(prim.GetAttribute("xformOp:orient").Get()) == Gf.Quatf:
            prim.GetAttribute("xformOp:orient").Set(
                Gf.Quatf(Gf.Rotation(Gf.Vec3d(0, 0, 1), float(spawn_rotation)).GetQuat())
            )
        else:
            prim.GetAttribute("xformOp:orient").Set(Gf.Rotation(Gf.Vec3d(0, 0, 1), float(spawn_rotation)).GetQuat())

        # set the xform setting back to original value
        StageUtil.recover_xformOpType(original_xform_order_setting)
        return prim

    def load_default_biped_to_stage():
        stage = omni.usd.get_context().get_stage()
        parent_path = PrimPaths.characters_parent_path()
        parent_prim = stage.GetPrimAtPath(parent_path)
        if not parent_prim.IsValid():
            prims.create_prim(parent_path, "Xform")
            carb.log_info(f"Character parent prim is created at: {parent_path}.")
            parent_prim = stage.GetPrimAtPath(parent_path)

        biped_prim_path = PrimPaths.biped_prim_path()
        biped_prim = stage.GetPrimAtPath(biped_prim_path)

        if Settings.skip_biped_setup():
            carb.log_info("Skip setting up Biped.")
            return biped_prim

        if not biped_prim.IsValid():
            prim = prims.create_prim(
                biped_prim_path,
                "Xform",
                usd_path=AssetPaths.default_biped_asset_path(),
            )
            prim.GetAttribute("visibility").Set("invisible")
            carb.log_info(
                f"Biped prim is created at: {biped_prim_path}, usd_path = {AssetPaths.default_biped_asset_path()}."
            )
            biped_prim = stage.GetPrimAtPath(biped_prim_path)

        populate_anim_graph()

        return biped_prim

    def get_anim_graph_from_character(character_prim):
        for prim in Usd.PrimRange(character_prim):
            if prim.GetTypeName() == "AnimationGraph":
                return prim
        return None

    def get_default_biped_character():
        stage = omni.usd.get_context().get_stage()
        return stage.GetPrimAtPath(PrimPaths.biped_prim_path())

    def setup_animation_graph_to_character(character_skelroot_list: list, anim_graph_prim):
        """
        Add animation graph for input characters in stage.
        Remove previous one if it exists
        """
        if anim_graph_prim is None or anim_graph_prim.IsValid() == False:
            carb.log_error("Unable to find an animation graph on stage.")
            return

        anim_graph_path = anim_graph_prim.GetPrimPath()
        paths = [Sdf.Path(prim.GetPrimPath()) for prim in character_skelroot_list]
        omni.kit.commands.execute("RemoveAnimationGraphAPICommand", paths=paths)
        omni.kit.commands.execute(
            "ApplyAnimationGraphAPICommand", paths=paths, animation_graph_path=Sdf.Path(anim_graph_path)
        )

    def setup_python_scripts_to_character(character_skelroot_list: list, python_script_path):
        """
        Add behavior script for input characters in stage.
        Remove previous one if it exists.
        """
        paths = [Sdf.Path(prim.GetPrimPath()) for prim in character_skelroot_list]
        omni.kit.commands.execute("RemoveScriptingAPICommand", paths=paths)
        omni.kit.commands.execute("ApplyScriptingAPICommand", paths=paths)
        for prim in character_skelroot_list:
            attr = prim.GetAttribute("omni:scripting:scripts")
            attr.Set([r"{}".format(python_script_path)])

    # Delete one character prim bt the given name
    def delete_character_prim(char_name):
        stage = omni.usd.get_context().get_stage()
        if not Sdf.Path.IsValidPathString(PrimPaths.characters_parent_path()):
            carb.log_error(str(PrimPaths.characters_parent_path()) + " is not a valid prim path")
            return

        character_prim = stage.GetPrimAtPath("{}/{}".format(PrimPaths.characters_parent_path(), char_name))
        if character_prim and character_prim.IsValid() and character_prim.IsActive():
            prims.delete_prim(character_prim.GetPath())

    # Delete all character prims in the stage
    def delete_character_prims():
        """
        Delete previously loaded character prims. Also deletes the default skeleton and character animations if they
        were loaded using load_default_skeleton_and_animations. Also deletes state corresponding to characters
        loaded onto stage.
        """
        stage = omni.usd.get_context().get_stage()
        if not Sdf.Path.IsValidPathString(PrimPaths.characters_parent_path()):
            carb.log_error(str(PrimPaths.characters_parent_path()) + " is not a valid prim path")
            return

        character_root_prim = stage.GetPrimAtPath(PrimPaths.characters_parent_path())
        if character_root_prim and character_root_prim.IsValid() and character_root_prim.IsActive():
            for character_prim in character_root_prim.GetChildren():
                if character_prim and character_prim.IsValid() and character_prim.IsActive():
                    prims.delete_prim(character_prim.GetPath())


class RobotUtil:
    WORLD_SETTINGS = {"physics_dt": 1.0 / 30.0, "stage_units_in_meters": 1.0, "rendering_dt": 1.0 / 30.0}

    def get_robot_name_by_index(robot_type, i):
        if i == 0:
            return robot_type
        elif i < 10:
            return robot_type + "_0" + str(i)
        else:
            return robot_type + "_" + str(i)

    def get_robot_name(robot_prim):
        # For robots under /World/Robots, names are root names
        prim_path = prims.get_prim_path(robot_prim)
        if prim_path.startswith(PrimPaths.robots_parent_path()):
            return prim_path.split("/")[3]

    def get_robot_pos(robot_prim):
        matrix = omni.usd.get_world_transform_matrix(robot_prim)
        return matrix.ExtractTranslation()

    def get_robots_in_stage(count=-1, robot_type_name=None):
        robot_xform = prims.get_prim_at_path(PrimPaths.robots_parent_path())
        if not robot_xform.IsValid() or not robot_xform.IsActive():
            return []
        prims_under_robots = prims.get_prim_children(robot_xform)
        robot_list = []
        for prim in prims_under_robots:
            if len(robot_list) >= count and count != -1:  # Get all if count is -1
                break
            path = prims.get_prim_path(prim)
            if robot_type_name == None:
                robot_list.append(prim)
            else:
                if path.startswith(PrimPaths.robots_parent_path() + "/" + robot_type_name):
                    robot_list.append(prim)
        return robot_list

    # Get all the cameras on the given robot
    def get_cameras_on_robot(robot_prim):
        stage = omni.usd.get_context().get_stage()
        robot_path = prims.get_prim_path(robot_prim)
        camera_list = []
        for prim in stage.Traverse():
            path = prims.get_prim_path(prim)
            if prim.GetTypeName() == "Camera" and path.startswith(robot_path):
                camera_list.append(prim)
        return camera_list

    # Get all the lidar cameras on the given robot
    def get_lidar_cameras_on_robot(robot_prim):
        stage = omni.usd.get_context().get_stage()
        robot_path = prims.get_prim_path(robot_prim)
        camera_list = []
        for prim in stage.Traverse():
            path = prims.get_prim_path(prim)
            if prim.GetTypeName() == "Camera" and path.startswith(robot_path) and "LIDAR" in path.split("/")[-1]:
                camera_list.append(prim)
        return camera_list

    # Get all the cameras on all the robots in the stage
    def get_robot_cameras():
        cameras = [cam for robot in RobotUtil.get_robots_in_stage() for cam in RobotUtil.get_cameras_on_robot(robot)]
        return cameras

    # Get the fisrt n cameras on all the robots in the stage
    def get_n_robot_cameras(n):
        cameras = [
            cam for robot in RobotUtil.get_robots_in_stage() for cam in RobotUtil.get_cameras_on_robot(robot)[:n]
        ]
        return cameras

    # Get all the lidar cameras on all the robots in the stage
    def get_robot_lidar_cameras():
        lidars = [
            lidar for robot in RobotUtil.get_robots_in_stage() for lidar in RobotUtil.get_lidar_cameras_on_robot(robot)
        ]
        return lidars

    # Get all the lidar cameras on all the robots in the stage
    def get_n_robot_lidar_cameras(n):
        lidars = [
            lidar
            for robot in RobotUtil.get_robots_in_stage()
            for lidar in RobotUtil.get_lidar_cameras_on_robot(robot)[:n]
        ]
        return lidars

    def spawn_robot(spawn_type, spawn_location, spawn_rotation=0, spawn_path=None):

        # ensure the default orientation system is base on orient system :
        original_xform_order_setting = StageUtil.set_xformOpType_SOT()
        stage = omni.usd.get_context().get_stage()

        # This automatically append number to the robot name
        robot_stage_name = omni.usd.get_stage_next_free_path(
            stage, f"{PrimPaths.robots_parent_path()}/{spawn_type}", False
        )
        if spawn_path:
            robot_stage_name = spawn_path
        # Create a prim in the stage and set the translation and rotation.
        prim = prims.create_prim(robot_stage_name, "Xform")
        prim.GetAttribute("xformOp:translate").Set(
            Gf.Vec3d(float(spawn_location[0]), float(spawn_location[1]), float(spawn_location[2]))
        )
        if type(prim.GetAttribute("xformOp:orient").Get()) == Gf.Quatf:
            prim.GetAttribute("xformOp:orient").Set(
                Gf.Quatf(Gf.Rotation(Gf.Vec3d(0, 0, 1), float(spawn_rotation)).GetQuat())
            )
        else:
            prim.GetAttribute("xformOp:orient").Set(Gf.Rotation(Gf.Vec3d(0, 0, 1), float(spawn_rotation)).GetQuat())

        # set the xform setting back to original value
        StageUtil.recover_xformOpType(original_xform_order_setting)

        return prim

    # Delete one character prim bt the given name
    def delete_robot_prim(robot_name):
        stage = omni.usd.get_context().get_stage()
        if not Sdf.Path.IsValidPathString(PrimPaths.robots_parent_path()):
            carb.log_error(str(PrimPaths.robots_parent_path()) + " is not a valid prim path")
            return

        robot_prim = stage.GetPrimAtPath("{}/{}".format(PrimPaths.robots_parent_path(), robot_name))
        if robot_prim and robot_prim.IsValid() and robot_prim.IsActive():
            prims.delete_prim(robot_prim.GetPath())

    # Delete all character prims in the stage
    def delete_robot_prims():
        """
        Delete previously loaded character prims. Also deletes the default skeleton and character animations if they
        were loaded using load_default_skeleton_and_animations. Also deletes state corresponding to characters
        loaded onto stage.
        """
        stage = omni.usd.get_context().get_stage()
        if not Sdf.Path.IsValidPathString(PrimPaths.robots_parent_path()):
            carb.log_error(str(PrimPaths.robots_parent_path()) + " is not a valid prim path")
            return

        robot_root_prim = stage.GetPrimAtPath(PrimPaths.robots_parent_path())
        if robot_root_prim and robot_root_prim.IsValid() and robot_root_prim.IsActive():
            for robot_prim in robot_root_prim.GetChildren():
                if robot_prim and robot_prim.IsValid() and robot_prim.IsActive():
                    prims.delete_prim(robot_prim.GetPath())


class AgentUtil:
    def get_all_agents_positions():
        """
        Get all agent positions in stage.
        """
        positions = []
        # Characters
        characters = CharacterUtil.get_characters_root_in_stage()
        for char in characters:
            positions.append(CharacterUtil.get_character_pos(char))
        # Robots
        robots = RobotUtil.get_robots_in_stage(-1)
        for robot in robots:
            positions.append(RobotUtil.get_robot_pos(robot))
        return positions
