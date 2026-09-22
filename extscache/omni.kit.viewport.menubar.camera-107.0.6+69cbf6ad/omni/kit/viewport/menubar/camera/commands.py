# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import Union

import carb
import omni.kit.commands
import omni.usd
from pxr import Gf, Sdf, Usd, UsdGeom

CAMERA_LOCK_NAME = "omni:kit:cameraLock"


class DuplicateCameraCommand(omni.kit.commands.Command):
    """
    Duplicates a camera at a specific time

    Args:
        camera_path (str): name of the camera to duplicate.
        time (float): Time at which to duplicate, or None to use active time
        usd_context_name (str): The name of a valid omni.UsdContext to target
        new_camera_path (str): Path to create the new camera at (None for automatic path)
    """

    def __init__(self, camera_path: str = "", time: float = None, usd_context_name: str = '', new_camera_path: str = None):
        self.__camera_path = camera_path
        self.__usd_context_name = usd_context_name
        self.__time = time if time is not None else omni.timeline.get_timeline_interface().get_current_time()
        self.__new_camera_path = new_camera_path

    def do(self):
        if not self.__camera_path:
            return

        usd_context = omni.usd.get_context(self.__usd_context_name)
        if not usd_context:
            raise RuntimeError(f'UsdContext "{self.__usd_context_name}" could not be found')

        stage = usd_context.get_stage()
        if not stage:
            raise RuntimeError(f'UsdContext "{self.__usd_context_name}" has no stage')

        old_prim = stage.GetPrimAtPath(self.__camera_path)
        if not old_prim:
            raise RuntimeError(f'Could not find camera prim at "{self.__camera_path}"')

        if self.__new_camera_path is None:
            target_path = omni.usd.get_stage_next_free_path(stage, "/Camera", True)
        else:
            target_path, self.__new_camera_path = self.__new_camera_path, None

        omni.kit.commands.execute(
            "CreatePrimWithDefaultXformCommand",
            prim_path=target_path,
            prim_type="Camera",
            create_default_xform=False,
            stage=stage
        )
        new_prim = stage.GetPrimAtPath(target_path)
        if not new_prim:
            raise RuntimeError(f'Could not find duplicated prim at "{target_path}"')

        # Save the created camera path now so any failure below won't kill our undo
        self.__new_camera_path = target_path

        timecode = self.__time * stage.GetTimeCodesPerSecond()
        for attr in old_prim.GetAttributes():
            attr_name = attr.GetName()
            # Skip over any xformOp property (they are not duplicated but created below)
            if UsdGeom.Xformable.IsTransformationAffectedByAttrNamed(attr_name):
                continue
            # Skip over the locked property
            if attr_name == CAMERA_LOCK_NAME:
                continue
            value = attr.Get(timecode)
            if value is not None:
                new_prim.CreateAttribute(attr.GetName(), attr.GetTypeName()).Set(value)

        # Now create the transform, taking the original world-space of the source camera and putting it into
        # the new camera's parent's space.  We do this always so that TransformPrim can create the correct
        # rotation ordering now.
        parent_xformable = UsdGeom.Xformable(new_prim.GetParent())
        if parent_xformable:
            parent_world_xform = omni.usd.get_world_transform_matrix(parent_xformable.GetPrim(), timecode)
        else:
            parent_world_xform = Gf.Matrix4d(1)

        old_camera_prim_world_mtx = omni.usd.get_world_transform_matrix(old_prim, timecode)
        new_camera_prim_local_mtx = old_camera_prim_world_mtx * parent_world_xform.GetInverse()
        omni.kit.commands.execute(
            "TransformPrim", path=new_prim.GetPath(),
            new_transform_matrix=new_camera_prim_local_mtx,
            usd_context_name=self.__usd_context_name
        )

        # These won't be undone, but that's ok..undo will delete the prim
        omni.usd.editor.set_no_delete(new_prim, False)
        omni.usd.editor.set_hide_in_stage_window(new_prim, False)

    def undo(self):
        pass


class SetViewportCameraCommand(omni.kit.commands.Command):
    """
    Sets a Viewport's actively bound camera to camera at given path

    Args:
        camera_path (Union[str, Sdf.Path): New camera path to bind to viewport.
        viewport_api: the viewport to target.
    """
    def __init__(self, camera_path: Union[str, Sdf.Path], viewport_api, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__viewport_api = viewport_api
        self.__prev_camera = viewport_api.camera_path
        self.__target_camera = camera_path

    @staticmethod
    def read_camera_path(viewport_api) -> Sdf.Path:
        stage = viewport_api.stage
        if stage:
            # TODO: 104 Put in proper namespace and per viewport
            # camera_path = stage.GetMetadataByDictKey("customLayerData", f"cameraSettings:{viewport_api.id}:boundCamera") or
            # Fallback to < 103.1 boundCamera
            camera_path = stage.GetMetadataByDictKey("customLayerData", "cameraSettings:boundCamera")
            if camera_path:
                prim = stage.GetPrimAtPath(camera_path)
                if prim and UsdGeom.Camera(prim):
                    return prim.GetPath()
        return None

    def __save_to_file(self, camera_path: str):
        viewport_api = self.__viewport_api
        stage = viewport_api.stage
        # Allow (but warn) the case if no Usd.Stage
        if not stage:
            carb.log_warn("No Usd.Stage to set boundCamera to")
            return
        # Error if not root-layer
        layer = stage.GetRootLayer()
        if not layer:
            carb.log_error("No Usd.Layer to set boundCamera to")
            return
        # Move the EditTarget to the root-layer and set meta-data there
        with Usd.EditContext(stage, Usd.EditTarget(layer)):
            # TODO: 104 Put in proper namespace and per viewport
            # stage.SetMetadataByDictKey("customLayerData", f"cameraSettings:{viewport_api.id}boundCamera", camera_path)
            # Save the legacy version for opening in versions < 103.1
            stage.SetMetadataByDictKey("customLayerData", "cameraSettings:boundCamera", camera_path)

    def do(self):
        self.__viewport_api.camera_path = self.__target_camera
        self.__save_to_file(str(self.__target_camera))

    def undo(self, look_through=None):
        # Set the viewport to use the previous camera
        self.__viewport_api.camera_path = self.__prev_camera
        self.__save_to_file(str(self.__prev_camera))


class DuplicateViewportCameraCommand(omni.kit.commands.Command):
    """
    Duplicates a Viewport's actively bound camera and bind active camera to the duplicated one.

    Args:
        viewport_api: The viewport to target
    """

    def __init__(self, viewport_api, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__viewport_api = viewport_api

    def do(self):
        viewport_api = self.__viewport_api
        new_camera_path = omni.usd.get_stage_next_free_path(viewport_api.stage, "/Camera", True)
        omni.kit.commands.execute("DuplicateCameraCommand", camera_path=viewport_api.camera_path, usd_context_name=viewport_api.usd_context_name, new_camera_path=new_camera_path)
        omni.kit.commands.execute("SetViewportCameraCommand", camera_path=new_camera_path, viewport_api=viewport_api)

    def undo(self):
        pass


def register_commands():
    return omni.kit.commands.register_all_commands_in_module(__name__)


def unregister_commands(cmds):
    omni.kit.commands.unregister_module_commands(cmds)
