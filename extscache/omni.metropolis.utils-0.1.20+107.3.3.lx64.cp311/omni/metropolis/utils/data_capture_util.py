import omni.replicator.core as rep
from typing import get_type_hints, Tuple, List, Dict, Any, Optional, Callable
import omni.usd
from omni.metropolis.utils.usd_util import USDUtil
from omni.metropolis.utils.simulation_util import SimulationUtil
import carb
from PIL import Image
from functools import partial
import os
import asyncio
import inspect


class CameraDataCaptureHelper:

    @staticmethod
    def is_async_callable(func: Callable) -> bool:
        """
        Check if a callable is an async function, handling functools.partial
        and Pydantic objects.

        Args:
            func (Callable): The callable to check.

        Returns:
            bool: True if the callable is an async function, False otherwise.
        """
        # Handle functools.partial objects
        if isinstance(func, partial):
            func = func.func  # Get the original function from the partial object

        # Handle Pydantic models or objects with a __call__ method
        if hasattr(func, "__call__") and not inspect.isfunction(func):
            func = func.__call__

        # Check if the function is asynchronous
        return inspect.iscoroutinefunction(func)

    @staticmethod
    def check_function_params(func: Callable, param_name: str, param_type: Optional[type] = None) -> bool:
        """
        Check if a function has a specific parameter name or type.

        :param func: The function to inspect (can be a functools.partial object).
        :param param_name: The parameter name to check for.
        :param param_type: The parameter type to check for, including type hints.
        :return: True if the parameter exists and matches the criteria; False otherwise.
        """
        # Handle functools.partial objects
        if isinstance(func, partial):
            func = func.func  # Get the original function from the partial object

        # Get the function signature
        sig = inspect.signature(func)

        # Get type hints for the function
        type_hints = get_type_hints(func)

        for param in sig.parameters.values():
            # Check if the parameter name matches
            if param_name == param.name:
                # Check for type hints if provided
                if param_type:
                    # Check if the parameter has a type hint
                    hint = type_hints.get(param.name)
                    if hint and hasattr(hint, "__origin__") and hint.__origin__ is param_type:
                        return True
                else:
                    return True

        func_name = func.__name__
        carb.log_warn(f"Parameter: {func_name} either miss {param_name} or {param_name} has a wrong type")

        return False

    @staticmethod
    def is_camera_prim(prim_path: str) -> bool:
        """check whether the target prim path point to a camera prim"""
        stage = omni.usd.get_context().get_stage()
        camera_prim = stage.GetPrimAtPath(prim_path)
        if not USDUtil.is_valid_prim(prim=camera_prim):
            return False

        if not camera_prim.GetTypeName() == "Camera":
            return False

        return True

    @classmethod
    async def get_single_frame_annotator_data_from_camera(
        cls,
        camera_path_list: List[str],
        annotator_dict: Dict[str, Any],
        post_processing_fn: Optional[Callable] = None,
        camera_resolution: Tuple[int, int] = (1920, 1080),
        loading_frame=10,
    ):
        """
        get single frame annotator data from camera
        :param camera_path_list: list of camera path
        :param annotator_dict: dict of annotator name
        :param post_processing_fn: post processing function to handle the annotator data
        :param camera_resolution: camera resolution, by default is 1920x1080
        :param loading_frame: loading frame, for each camera, the number of frame to load the data. [this is used to avoid the blur image and incomplete data]
        """

        # check whethe the post processing fn takes valid input:
        if not (
            cls.check_function_params(func=post_processing_fn, param_name="camera_path")
            and cls.check_function_params(func=post_processing_fn, param_name="annotator_dict")
        ):
            carb.log_warn(
                "please use valid post processing function for camera prim based data capture ! Either camera_path or annotator_dict input in missing"
            )
            return None

        for camera_path in camera_path_list:
            if not cls.is_camera_prim(prim_path=camera_path):
                carb.log_warn("prim path {camera_path} is either not a camera or not valid prim")
                return None

        # create render product base on the first camera's path
        target_camera_path = camera_path_list[0]
        rp = rep.create.render_product(target_camera_path, camera_resolution)

        # attach the render product to the annotator
        for annotator_name, annotator in annotator_dict.items():
            annotator.attach(rp)
        # switch the render product input to different camera
        for camera_path in camera_path_list:
            rp.hydra_texture.set_camera_path(camera_path)
            await rep.orchestrator.step_async(rt_subframes=loading_frame)
            # if user input predefined post processing method
            if post_processing_fn is not None:
                # check whether the post processing function is async
                if cls.is_async_callable(post_processing_fn):
                    await post_processing_fn(camera_path=camera_path, annotator_dict=annotator_dict)
                else:
                    post_processing_fn(camera_path=camera_path, annotator_dict=annotator_dict)

        await rep.orchestrator.step_async(rt_subframes=loading_frame)
        await rep.orchestrator.stop_async()
        return rp

    @classmethod
    async def get_single_frame_annotator_data_from_pose(
        cls,
        camera_pose_list: List[Tuple[Tuple, Tuple]],
        annotator_dict: Dict[str, Any],
        post_processing_fn: Optional[Callable] = None,
        camera_resolution: Tuple[int, int] = (1920, 1080),
        loading_frame=10,
    ):
        """
        get single frame annotator data from camera pose
        :param camera_pose_list: list of camera pose to capture the data
        :param annotator_dict: dict of annotator name
        :param post_processing_fn: post processing function to handle the annotator data
        :param camera_resolution: camera resolution, by default is 1920x1080
        :param loading_frame: loading frame, for each camera, the number of frame to load the data. [this is used to avoid the blur image and incomplete data]
        """
        # check whether the input callable function is correct
        if not (
            cls.check_function_params(func=post_processing_fn, param_name="camera_id")
            and cls.check_function_params(func=post_processing_fn, param_name="annotator_dict")
        ):
            carb.log_warn(
                "please use valid post processing function for camera path based data capture ! Either camera_id or annotator_dict input is missing"
            )
            return None

        # instead of using existing camera in the stage, create a camera and set the parameter to default parameters
        dynamic_camera = rep.create.camera()
        rp = rep.create.render_product(dynamic_camera, camera_resolution)
        # attach the render product to the annotator
        for annotator_name, annotator in annotator_dict.items():
            annotator.attach(rp)

        # get current camera index
        curr_index = 0
        number_of_camera_pose = len(camera_pose_list)

        while curr_index < number_of_camera_pose:
            with dynamic_camera:
                # get_current_target_camera_pose.
                target_pose = camera_pose_list[curr_index]
                camera_pos, look_at_pos = target_pose
                # modify camera position to match the target camera poses
                rep.modify.pose(position=camera_pos, look_at=look_at_pos)
                await rep.orchestrator.step_async(rt_subframes=loading_frame)
                # if user input predefined post processing method
                if post_processing_fn is not None:

                    if cls.is_async_callable(post_processing_fn):
                        # check whether the post processing function is async
                        await post_processing_fn(camera_id=curr_index, annotator_dict=annotator_dict)
                    else:
                        post_processing_fn(camera_id=curr_index, annotator_dict=annotator_dict)

            curr_index = curr_index + 1
            # Since data capture process is async, print out current camera id during the process.
            carb.log_info(f"current camera id : {curr_index}")

        await rep.orchestrator.step_async(rt_subframes=loading_frame)
        await rep.orchestrator.stop_async()
        return rp

    @classmethod
    async def get_single_frame_annotator_data(
        cls, annotator_name_list: List[str], capture_annotator_data_async: Callable = None
    ):
        """get target annotator of target annotator"""
        # check whether all the prim path within the camera path list are camera_prim

        # disable capture on play
        origin_setting = SimulationUtil.get_capture_on_play()
        rep.orchestrator.set_capture_on_play(False)
        # initalize the annotator_list
        annotator_dict: Dict[str:Any] = {}
        for annotator_name in annotator_name_list:
            annotator_dict[annotator_name] = rep.AnnotatorRegistry.get_annotator(annotator_name)

        # fetch the created render product
        rp = await capture_annotator_data_async(annotator_dict=annotator_dict)

        # at the end of the data fetching, detach the renderproduct and destroy it.
        if rp is not None:
            for annotator_name, annotator in annotator_dict.items():
                annotator.detach(rp)
        # clean the annotator dict
        annotator_dict.clear()
        rp.destroy()
        rp = None

        # TODO:: destroy the camera after the simulation has been finished

        # recover the capture on play setting
        rep.orchestrator.set_capture_on_play(origin_setting)

        # delete the prim generated by replicator
        stage = omni.usd.get_context().get_stage()
        if stage.GetPrimAtPath("/Replicator"):
            omni.kit.commands.execute("DeletePrimsCommand", paths=["/Replicator"])
        # wait for one update to ensure the replicator prim is removed correctly
        await omni.kit.app.get_app().next_update_async()

    @classmethod
    async def capture_static_data_async(
        cls,
        annotator_name_list: List[str],
        post_processing_fn: Callable,
        camera_path_list: Optional[List[str]] = None,
        camera_pose_list: Optional[List[Tuple[Tuple, Tuple]]] = None,
        camera_resolution: Tuple[int, int] = (1920, 1080),
        loading_frame: Optional[int] = 10,
    ):
        """
        Asynchronously captures static data using either existing camera paths or user-defined camera poses.

        This method triggers data capture using the specified annotators from either:
        - A list of existing camera paths in the stage (`camera_path_list`), or
        - A list of custom camera poses (`camera_pose_list`), where a temporary camera is created
          and moved through each pose.

        After each capture, a user-provided post-processing function is called with relevant metadata.
        The function will receive either a `camera_path` (when using existing cameras) or a `camera_id`
        (when using custom poses), but never both. A warning is issued if both are provided.

        Args:
            annotator_name_list (List[str]):
                List of annotator names to be used during data capture.

            post_processing_fn (Callable):
                A function that processes the captured data after each frame. It will receive metadata
                including either "camera_path" or "camera_id".

            camera_path_list (Optional[List[str]], optional):
                List of prim paths to existing cameras. If provided, data will be captured using these cameras.

            camera_pose_list (Optional[List[Tuple[Tuple, Tuple]]], optional):
                List of custom camera poses, where each pose is a tuple of (position, rotation).
                If provided, a temporary camera will be created to move through each pose.

            camera_resolution (Tuple[int, int], optional):
                The resolution (width, height) of the camera. Default is (1920, 1080).

            loading_frame (Optional[int], optional):
                Number of frames to wait before capturing data to allow for scene loading. Default is 10.
        """

        if camera_path_list is not None and camera_pose_list is not None:
            carb.log_warn(
                "Error as Warning Message:; ambiguous parameter is received, both camera_path_list and camera_pos_list are inputted."
            )

        # disable capture on play, so that simulation would not be triggered automatically.
        # generate data base on existing cameras in the stage
        if camera_path_list is not None:
            capture_annotator_data_async_fn = partial(
                cls.get_single_frame_annotator_data_from_camera,
                camera_path_list=camera_path_list,
                post_processing_fn=post_processing_fn,
                loading_frame=loading_frame,
                camera_resolution=camera_resolution,
            )
            await cls.get_single_frame_annotator_data(
                annotator_name_list=annotator_name_list, capture_annotator_data_async=capture_annotator_data_async_fn
            )

        # generate data capture base on camera pose
        if camera_pose_list is not None:
            capture_annotator_data_async_fn = partial(
                cls.get_single_frame_annotator_data_from_pose,
                camera_pose_list=camera_pose_list,
                post_processing_fn=post_processing_fn,
                loading_frame=loading_frame,
                camera_resolution=camera_resolution,
            )
            await cls.get_single_frame_annotator_data(
                annotator_name_list=annotator_name_list, capture_annotator_data_async=capture_annotator_data_async_fn
            )
