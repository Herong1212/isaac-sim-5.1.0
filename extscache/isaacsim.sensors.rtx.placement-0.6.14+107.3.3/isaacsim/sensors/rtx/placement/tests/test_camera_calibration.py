from pathlib import Path

import carb.settings
import numpy as np
import omni.kit
import omni.kit.test
import omni.usd
from omni.metropolis.utils.unit_test import *
from omni.metropolis.utils.simulation_util import SimulationUtil
from isaacsim.sensors.rtx.placement.camera_calibration.camera_calibration_manager import (
    CameraCalibrationManager,
)
from omni.metropolis.utils.sensor_util import SensorUtil
from isaacsim.sensors.rtx.placement.camera_calibration.calibration_helper import (
    CameraCalibrationHelper,
    CalibrationDotInfo,
)
from pxr import Usd
from ..settings import CameraCalibrationSettings
from ..utils import CameraGeneralUtil
from typing import List


# SAMPLE_CAMERA_DATASET = {
#     "1": {
#         position:
#     }
# }

class TestCalibration(omni.kit.test.AsyncTestCase):
    _test_scene_folder = "data/test_scenes"
    _test_calibration_scene_file_name = "test_camera_calibration_scene.usd"

    @staticmethod
    def get_test_stage_path(test_scene_file_name: str):
        """fetch the test stage path"""
        EXT_PATH = (
            omni.kit.app.get_app()
            .get_extension_manager()
            .get_extension_path_by_module("isaacsim.sensors.rtx.placement")
        )
        test_scene_file_path = os.path.join(EXT_PATH, TestCalibration._test_scene_folder, test_scene_file_name)

        carb.log_verbose("test_scene_path:" + str(test_scene_file_path))
        if not os.path.isfile(test_scene_file_path):
            carb.log_error("The target file is not an valid usd file")
        return test_scene_file_path


    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_calibration_setup(self):
        """
        Test if the calibration dot could be generated correctly
        """
        original_xform_type = SimulationUtil.update_xformOp_type(target_xform_type="Scale, Orient, Translate")
        default_stage_root_prim_path = "/Root"
        default_camera_resolution = (1920, 1080)
        default_clipping_height = 7.0  # remove the ceiling
        default_camera_num = 5
        default_top_camera_path = "/World/Top_Camera/Calibration_Top_Camera"

        async with TestStage():
            with context_create_example_sim_manager() as sim:
                # empty stage with no character
                prop = sim.get_config_file_property("character", "num")
                prop.set_value(0)
                # put 5 camera in the test stage
                prop_group = sim.get_config_file_property_group("sensor", "camera_group")
                prop_group.get_property("camera_num").set_value(default_camera_num)
                sim.set_up_simulation_from_config_file()
                await wait_for_simulation_set_up_done(sim)
                # get camera calibration manager singleton

                stage = omni.usd.get_context().get_stage()
                calibration_manager = CameraCalibrationManager.get_instance()
                # calculate the next free top camera path

                # generate the top view camera
                calibration_manager.create_top_view_camera(
                    root_prim_path=default_stage_root_prim_path,
                    clipping_height=default_clipping_height,
                    top_view_resolution=default_camera_resolution,
                )
                # after top view camera has been created
                # check whether the setting value has been updated
                self.assertEqual(default_top_camera_path, CameraCalibrationSettings.top_view_camera_path)

                # create calibration dot list:
                await calibration_manager.generate_calibration_dot_prim_async()

                # Then check whether each camera have matched calibration dots
                calibration_dot_root_path = CameraCalibrationSettings.calibration_prim_path
                calibration_dot_root_prim = stage.GetPrimAtPath(calibration_dot_root_path)

                calibration_cluster_prims = calibration_dot_root_prim.GetChildren()
                # get the number of camera calibration cluster within the stage
                calibration_groups_count = len(calibration_cluster_prims)
                # check whether each camera have calibration cluster
                self.assertEqual(calibration_groups_count, default_camera_num)

                # check the number of each calibration cluster
                for calibration_cluster_prims in calibration_cluster_prims:
                    calibration_dot_num = len(calibration_cluster_prims.GetChildren())
                    # help developer check existed calibration dot num
                    self.assertEqual(calibration_dot_num, CameraCalibrationSettings.calibration_prim_num)

                # check whether the offset and pixel per meter factor could be calculated
                SimulationUtil.update_xformOp_type(original_xform_type)

                # doublec check and get validated calibration info in dictioanry
                camera_prim_list = CameraGeneralUtil.get_target_camera_prims_under_root()
                camera_path_list = [str(camera_prim.GetPrimPath()) for camera_prim in camera_prim_list]

                all_calibration_dot_infos = []
                for camera_path in camera_path_list:
                    camera_params = await CameraCalibrationHelper.get_camera_params(camera_path=camera_path)
                    calibration_dot_infos = await calibration_manager.get_validate_calibration_dot_infos(
                        camera_prim_path=camera_path, camera_params=camera_params
                    )
                    all_calibration_dot_infos.extend(calibration_dot_infos)

                # the check whether the pixel_per_meter (scalefactor) and the offset are calculated correctly

                # calculate the conversion factors base on two different pipeline

                # set the value of the stage root in camera calibration setting panel
                CameraCalibrationSettings.scene_bounding_box_path = default_stage_root_prim_path
                conversion_factors_root = calibration_manager.calculate_conversion_factors_from_root()
                conversion_factors_dot = calibration_manager.calculate_conversion_factors_from_dots(
                    all_calibration_dot_infos=all_calibration_dot_infos
                )
                # compare the parameter generated from two different method
                root_offset = conversion_factors_root.get("offset", None)
                root_pixel_per_meter = conversion_factors_root.get("pixel_per_meter", None)

                dot_offset = conversion_factors_dot.get("offset", None)
                dot_pixel_per_meter = conversion_factors_dot.get("pixel_per_meter", None)
                # calculate the difference
                scale_diff = abs(root_pixel_per_meter - dot_pixel_per_meter)
                self.assertLess(scale_diff ,  1)
                offset_diff = root_offset[0] - dot_offset[0] + root_offset[1] - dot_offset[1]
                self.assertLess(offset_diff ,  1)

    async def test_calibration_projection_matrix(self):
        """set script that focusing on calibration projection matrix calculation"""

        original_xform_type = SimulationUtil.update_xformOp_type(target_xform_type="Scale, Orient, Translate")
        default_stage_root_prim_path = "/World/Ground"
        default_camera_resolution = (1920, 1080)
        default_clipping_height = 7.0  # remove the ceiling
        default_camera_num = 1
        target_scene = self.get_test_stage_path(self._test_calibration_scene_file_name)
        # On an empty scene
        async with TestStage(stage_path = target_scene):
            # get camera calibration manager singleton
            stage = omni.usd.get_context().get_stage()
            calibration_manager = CameraCalibrationManager.get_instance()
            # calculate the next free top camera path
            # generate the top view camera
            calibration_manager.create_top_view_camera(
                root_prim_path=default_stage_root_prim_path,
                clipping_height=default_clipping_height,
                top_view_resolution=default_camera_resolution,
            )
            await calibration_manager.generate_calibration_dot_prim_async()
            # Then check whether each camera have matched calibration dots
            camera_prim_list = CameraGeneralUtil.get_target_camera_prims_under_root()
            target_camera_prim = camera_prim_list[0]
            # we only need to test one camera within the list:
            target_camera_path = str(target_camera_prim.GetPrimPath())

            camera_params = await CameraCalibrationHelper.get_camera_params(camera_path=target_camera_path)
            calibration_dot_infos: List[CalibrationDotInfo] = (
                await calibration_manager.get_validate_calibration_dot_infos(
                    camera_prim_path=target_camera_path, camera_params=camera_params
                )
            )

            three_d_points = [calibration_dot_info.world_coord for calibration_dot_info in calibration_dot_infos]
            two_d_points = [
                calibration_dot_info.target_camera_image_coord for calibration_dot_info in calibration_dot_infos
            ]

            projection_matrix = SensorUtil.compute_camera_projection_matrix(
                three_d_points=three_d_points, two_d_points=two_d_points
            )
            # reset the projection matrix to make the comparation easier:
            projection_matrix_res = projection_matrix[..., :2] / projection_matrix[..., 2:3]

            # calculate the target camera's extrinsic matrix
            extrinsic_matrix = SensorUtil.calculate_3x4_extrinsic_matrix(camera_params=camera_params)
            # calculate the target camera's intrinsic matrix
            intrinsic_matrix = SensorUtil.calculate_3x3_intrinsic_matrix(camera_params=camera_params)
            #  recalculate the projection matrix from the extrinsic matrix and intrinsic matrix
            re_projection_matrix = intrinsic_matrix @ extrinsic_matrix
            # reset
            re_projection_matrix_res = re_projection_matrix[..., :2] / re_projection_matrix[..., 2:3]
            # calculate the diff
            diff_sum = np.sum(np.abs(re_projection_matrix_res - projection_matrix_res))
            # diff sum shall be smaller than one
            self.assertLess(diff_sum, 1)
