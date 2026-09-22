# Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb
import omni.usd
import omni.kit.usd.layers as layers

from pxr import Sdf, Usd, Tf, UsdGeom
from typing import List

from .constants import *
from .utils import (
    get_user_shared_root_path, get_bound_camera_property_path,
    get_following_user_property_path, get_selection_property_path
)


class PeerUserSharedData:
    """
    Data abstraction to manage peer user data inside presence layer.
    """

    def __init__(
        self, usd_context: omni.usd.UsdContext,
        shared_stage: Usd.Stage,
        user_info: layers.LiveSessionUser
    ):
        # Shared stage is the one in the live session folder with name users.live that holds all
        # shared data for all users. Peer users camera will be replicated into the local session layer
        # with path self.session_layer_camera_path if peer user is bound to the builtin camera.
        self.shared_stage = shared_stage
        self.user_info = user_info
        self.usd_context = usd_context

        user_name_identifier = omni.usd.make_valid_identifier(user_info.user_name.split('@')[0])
        self.__replication_root_path = LOCAL_SESSION_LAYER_SHARED_DATA_ROOT_PATH.AppendElementString(
            f"{user_name_identifier}_{user_info.user_id}"
        )

        self.__replication_camera_path = self.__replication_root_path.AppendElementString(
            f"{user_name_identifier}_Camera_{user_info.user_id}"
        )

        # Creates corresponding replication inside local session layer.
        stage = self.usd_context.get_stage()
        target_layer = stage.GetSessionLayer()
        with Usd.EditContext(stage, target_layer):
            prim = stage.DefinePrim(self.__replication_root_path, "Scope")
            omni.usd.editor.set_hide_in_stage_window(prim, True)
            omni.usd.editor.set_hide_in_ui(prim, True)

        # Creates user namespace inside shared stage
        self.shared_root_path = get_user_shared_root_path(self.user_id)
        prim_spec = Sdf.CreatePrimInLayer(self.shared_stage.GetRootLayer(), SESSION_SHARED_LAYER_ROOT_PATH)
        prim_spec.specifier = Sdf.SpecifierDef
        prim_spec = Sdf.CreatePrimInLayer(self.shared_stage.GetRootLayer(), self.shared_root_path)
        prim_spec.specifier = Sdf.SpecifierDef

        # The property that can be used to check which camera the user is bound to.
        # Every user can bind two kinds of cameras:
        # 1. Builtin cameras.
        # 2. Cameras in the USD.
        # If it's builtin cameras, the property value must be in the list of SHARED_BUILT_IN_CAMERA_LIST.
        # If it's camera in the USD, the property value points to the camera path in the stage.
        self.__bound_camera_property_path = get_bound_camera_property_path(self.user_id)

        self.__selections_property_path = get_selection_property_path(self.user_id)
        self.__following_user_property_path = get_following_user_property_path(self.user_id)

        self.__shared_stage_builtin_camera_paths = {}
        for camera_name in SHARED_BUILT_IN_CAMERA_LIST:
            self.__shared_stage_builtin_camera_paths[camera_name] = self.shared_root_path.AppendElementString(camera_name)

        self.__current_bound_camera_property_value: str = None
        self.__current_selection_paths: List[Sdf.Path] = []
        self.__current_following_user: str = None

        self.update_bound_camera()

    @property
    def user_id(self):
        return self.user_info.user_id

    @property
    def user_name(self):
        return self.user_info.user_name

    def destroy(self):
        if self.usd_context.get_stage():
            layers.LayerUtils.remove_prim_spec(
                self.usd_context.get_stage().GetSessionLayer(),
                self.__replication_root_path
            )

        self.shared_stage = None
        self.usd_context = None

    def update_bound_camera(self):
        latest_bound_camera_path = self.__get_bound_camera_path_from_usd()
        if latest_bound_camera_path != self.__current_bound_camera_property_value:
            self.__current_bound_camera_property_value = latest_bound_camera_path
            if not self.is_bound_to_builtin_camera():
                layers.LayerUtils.remove_prim_spec(
                    self.usd_context.get_stage().GetSessionLayer(),
                    self.__replication_camera_path
                )
            else:
                self.replicate_bound_camera_to_local()
                with Sdf.ChangeBlock():
                    self.__hide_prim_and_set_display_name()

            return True

        return False

    def update_selections(self):
        latest_selections = self.__get_selections_from_usd()
        if latest_selections != self.__current_selection_paths:
            self.__current_selection_paths = latest_selections
            return True

        return False

    def update_following_user(self):
        latest_following_user = self.__get_following_user_from_usd()
        if latest_following_user != self.__current_following_user:
            self.__current_following_user = latest_following_user
            return True

        return False

    @carb.profiler.profile
    def replicate_bound_camera_to_local(self, property_names: List[str] = []):
        builtin_camera_name = self.__bound_camera_property_value
        path = self.__shared_stage_builtin_camera_paths.get(builtin_camera_name, None)
        if not path:
            return

        shared_data_stage = self.shared_stage
        stage = self.usd_context.get_stage()
        bound_camera_prim = self.shared_stage.GetPrimAtPath(path)
        if not bound_camera_prim:
            return

        bound_camera_path = bound_camera_prim.GetPath()
        target_path = self.__replication_camera_path
        target_layer = stage.GetSessionLayer()
        with Sdf.ChangeBlock():
            Sdf.CreatePrimInLayer(target_layer, target_path)
            if property_names:
                for property_name in property_names:
                    source_property_path = bound_camera_path.AppendProperty(property_name)
                    target_property_path = target_path.AppendProperty(property_name)
                    Sdf.CopySpec(
                        shared_data_stage.GetRootLayer(), source_property_path,
                        target_layer, target_property_path
                    )
            else:
                Sdf.CopySpec(shared_data_stage.GetRootLayer(), bound_camera_path, target_layer, target_path)

    def is_bound_to_builtin_camera(self):
        if self.__current_following_user:
            return False

        builtin_camera_name = self.__bound_camera_property_value
        path = self.__shared_stage_builtin_camera_paths.get(builtin_camera_name, None)

        return path is not None

    def is_bound_camera_property_affected(self, changed_path: Sdf.Path):
        changed_path = Sdf.Path(changed_path)

        return changed_path == self.__bound_camera_property_path

    def is_selection_property_affected(self, changed_path: Sdf.Path):
        changed_path = Sdf.Path(changed_path)

        return changed_path == self.__selections_property_path

    def is_following_user_property_affected(self, changed_path: Sdf.Path):
        changed_path = Sdf.Path(changed_path)

        return changed_path == self.__following_user_property_path

    def is_builtin_camera_affected(self, changed_path: Sdf.Path):
        """Checks if the changes to path will influence the builtin camera prim if user is bound to builtin camera."""
        changed_path = Sdf.Path(changed_path)

        builtin_camera_name = self.__bound_camera_property_value
        path = self.__shared_stage_builtin_camera_paths.get(builtin_camera_name, None)
        # Not bound to builtin camera
        if not path:
            return False

        return changed_path.GetPrimPath() == path

    def get_bound_camera_prim(self) -> Usd.Prim:
        """Returns the bound camera in the local stage. It will return None if it's following other user."""
        if self.__current_following_user:
            return None

        if self.is_bound_to_builtin_camera():
            camera_path = self.__replication_camera_path
        elif Sdf.Path.IsValidPathString(self.__bound_camera_property_value):
            camera_path = Sdf.Path(self.__bound_camera_property_value)
        else:
            camera_path = None

        if not camera_path:
            return None

        stage = self.usd_context.get_stage()

        return stage.GetPrimAtPath(camera_path)

    @property
    def __bound_camera_property_value(self) -> str:
        """
        Returns property value of bound camera path in shared stage. In order to support binding to both builtin cameras
        and non-builtin cameras. The property value can be builtin camera name listed in the SHARED_BUILT_IN_CAMERA_LIST,
        or the prim path in the local stage.
        """

        if self.__current_bound_camera_property_value is None:
            self.__current_bound_camera_property_value = self.__get_bound_camera_path_from_usd()

        return self.__current_bound_camera_property_value

    @property
    def following_user_id(self) -> str:
        """The user id that this user is currently following."""

        if self.__current_following_user is None:
            self.__current_following_user = self.__get_following_user_from_usd()

        return self.__current_following_user

    @property
    def selections(self) -> List[Sdf.Path]:
        if self.__current_selection_paths is None:
            self.__current_selection_paths = self.__get_selections_from_usd()

        return self.__current_selection_paths

    def __get_following_user_from_usd(self):
        following_user_property = self.shared_stage.GetRootLayer().GetAttributeAtPath(self.__following_user_property_path)
        if not following_user_property:
            return ""

        return str(following_user_property.default).strip()

    def __get_bound_camera_path_from_usd(self):
        camera_path_property = self.shared_stage.GetRootLayer().GetAttributeAtPath(self.__bound_camera_property_path)
        if not camera_path_property:
            return ""

        return str(camera_path_property.default).strip()

    def __get_selections_from_usd(self):
        selections_property = self.shared_stage.GetRootLayer().GetAttributeAtPath(self.__selections_property_path)
        if not selections_property:
            return []

        selections = selections_property.default
        selections = [Sdf.Path(selection) for selection in selections if Sdf.Path.IsValidPathString(str(selection))]

        return selections

    def __hide_prim_and_set_display_name(self):
        stage = self.usd_context.get_stage()
        prim = self.get_bound_camera_prim()
        if not prim:
            return

        prim = prim.GetPrim()
        with Sdf.ChangeBlock():
            with Usd.EditContext(stage, stage.GetSessionLayer()):
                omni.usd.editor.set_hide_in_stage_window(prim, True)
                omni.usd.editor.set_hide_in_ui(prim, True)
                omni.usd.editor.set_display_name(prim, self.user_info.user_name)
                prim.CreateAttribute("omni:kit:cameraLock", Sdf.ValueTypeNames.Bool).Set(True)
