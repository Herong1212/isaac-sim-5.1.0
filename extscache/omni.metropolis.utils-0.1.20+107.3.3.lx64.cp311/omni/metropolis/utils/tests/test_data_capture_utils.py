from functools import partial
from typing import Dict, Any, Tuple, List
import carb.settings
import omni.kit
import omni.kit.test
import omni.usd
from omni.metropolis.utils.unit_test import *
from omni.metropolis.utils.usd_util import USDUtil, CameraUSDUtil
from omni.metropolis.utils.data_capture_util import CameraDataCaptureHelper


class CameraDataCaptureChecker:
    _default_camera_resolution: Tuple[int, int] = (1920, 1080)
    _default_camera_root_path = "/World/Cameras"

    @staticmethod
    def test_annotator_data_validity(annotator_dict: Dict[str, Any], format_checker: Dict[str, List[bool]]):
        """Test the validity of the annotator data"""
        for annotator_name in annotator_dict.keys():
            annotator_data = annotator_dict.get(annotator_name, None)
            is_valid_data = annotator_data is not None
            format_checker[annotator_name].append(is_valid_data)

    @classmethod
    def test_post_processing_camera(
        cls, camera_path: str, annotator_dict: Dict[str, Any], format_checker: Dict[str, List[bool]]
    ):
        """
        Test the post processing of the camera data captured from existing camera.
        [camera_path_list] is used as the input of "capture_static_data_async".
        camera_path: A "camera_path" input that points to an existing camera.
        """
        cls.test_annotator_data_validity(annotator_dict=annotator_dict, format_checker=format_checker)

    @classmethod
    def test_post_processing_pose(
        cls, camera_id: int, annotator_dict: Dict[str, Any], format_checker: Dict[str, List[bool]]
    ):
        """
        Test the post processing of the camera data captured from the camera pose.
        [camera_pose_list] is used as the input of "capture_static_data_async".
        camera_id: This input refers to the index of the camera pose in the pose list.
        """
        cls.test_annotator_data_validity(annotator_dict=annotator_dict, format_checker=format_checker)

    # NOTE :: this part of the code is used to test the existing camera based data caption
    @classmethod
    async def check_exist_camera_annotator_fetching(cls, format_checker: Dict[str, List[bool]]):
        """test whether the annotator fetching can work properly"""

        carb.log_warn("start test camera annotator fetching")
        camera_prim_list = USDUtil.filter_children_by_type(type_name="Camera", prim_path=cls._default_camera_root_path)
        camera_path_list = [str(camera_prim.GetPrimPath()) for camera_prim in camera_prim_list]
        annotator_name_list = format_checker.keys()
        post_processing_fn = partial(cls.test_post_processing_camera, format_checker=format_checker)
        await CameraDataCaptureHelper.capture_static_data_async(
            camera_path_list=camera_path_list,
            annotator_name_list=annotator_name_list,
            post_processing_fn=post_processing_fn,
            camera_resolution=cls._default_camera_resolution,
            loading_frame=5,
        )
        return format_checker

    # NOTE:: this part of the code is used to test the camera pose based data caption
    @classmethod
    async def check_pose_based_annotator_fetching(cls, format_checker: Dict[str, List[bool]]):
        """test whether the annotator fetching can work properly"""
        camera_prim_list = USDUtil.filter_children_by_type(type_name="Camera", prim_path=cls._default_camera_root_path)
        camera_pose_list = []
        for camera_prim in camera_prim_list:
            camera_pos_raw = USDUtil.get_prim_pos(prim=camera_prim)
            camera_look_at_pos = CameraUSDUtil.get_camera_focus_point(camera_prim=camera_prim)
            camera_pose = (
                (camera_pos_raw[0], camera_pos_raw[1], camera_pos_raw[2]),
                (camera_look_at_pos[0], camera_look_at_pos[1], camera_look_at_pos[2]),
            )
            camera_pose_list.append(camera_pose)

        annotator_name_list = format_checker.keys()
        post_processing_fn = partial(cls.test_post_processing_pose, format_checker=format_checker)
        await CameraDataCaptureHelper.capture_static_data_async(
            camera_pose_list=camera_pose_list,
            annotator_name_list=annotator_name_list,
            post_processing_fn=post_processing_fn,
            camera_resolution=cls._default_camera_resolution,
            loading_frame=5,
        )

        return format_checker


class TestDataCapture(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        # need to explicitly enable IRA core to avoid circular dependency
        extension_manager = omni.kit.app.get_app().get_extension_manager()
        extension_manager.set_extension_enabled_immediate("isaacsim.replicator.agent.core", True)

    async def tearDown(self):
        pass

    async def test_data_capture(self):
        """
        Test if the calibration dot could be generated correctly
        """
        default_camera_num = 5
        target_annotator_names = ["camera_params", "rgb"]
        # On an empty scene
        with context_create_example_sim_manager() as sim:
            # empty stage with no character
            prop = sim.get_config_file_property("character", "num")
            prop.set_value(0)
            # put 5 camera in the test stage
            prop_group = sim.get_config_file_property_group("sensor", "camera_group")
            prop_group.get_property("camera_num").set_value(default_camera_num)
            sim.set_up_simulation_from_config_file()
            await wait_for_simulation_set_up_done(sim)

            format_checker_dict: Dict[str, List[bool]] = {}
            for annotator_name in target_annotator_names:
                format_checker_dict[annotator_name] = []
            # test the exist camera annotator fetching
            format_checker_dict = await CameraDataCaptureChecker.check_exist_camera_annotator_fetching(
                format_checker=format_checker_dict
            )
            for annotator_name in target_annotator_names:
                is_all_data_valid = False not in format_checker_dict[annotator_name]
                self.assertTrue(is_all_data_valid)

            # reset the format checker dict for the next test
            format_checker_dict = {}
            for annotator_name in target_annotator_names:
                format_checker_dict[annotator_name] = []
            # test the pose based annotator fetching
            format_checker_dict = await CameraDataCaptureChecker.check_pose_based_annotator_fetching(
                format_checker=format_checker_dict
            )
            for annotator_name in target_annotator_names:
                is_all_data_valid = False not in format_checker_dict[annotator_name]
                self.assertTrue(is_all_data_valid)
