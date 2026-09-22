## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ['TestManipulatorUSDCamera']


from ..usd_camera_manipulator import UsdCameraManipulator
from ..model import CameraManipulatorModel, _flatten_matrix

import omni.usd
import omni.kit.test
import carb.settings

from pxr import Gf, Sdf, UsdGeom

from pathlib import Path
from typing import List, Sequence
import sys
import unittest


TESTS_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.manipulator.camera}/data")).absolute().resolve()
USD_FILES = TESTS_PATH.joinpath("tests", "usd")


class TestManipulatorUSDCamera(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self.stage = omni.usd.get_context().get_stage()
        super().setUp()

    # After running each test
    async def tearDown(self):
        super().tearDown()

    def __reset_initial_xf(self, usd_manip, initial_transform_item, prim):
        # Reset the initial transform to the current transform
        matrix = omni.usd.get_world_transform_matrix(prim)
        usd_manip.model.set_floats(initial_transform_item, _flatten_matrix(matrix))
        # This synthesizes the start of a new event
        usd_manip._set_context('', prim.GetPath())

    def __setup_usdmanip_tumble_test(self, prim_path: Sdf.Path):
        usd_manip = UsdCameraManipulator(prim_path=prim_path)
        usd_manip.model = CameraManipulatorModel()

        usd_manip._on_began(usd_manip.model)

        cam_prim = self.stage.GetPrimAtPath(prim_path)
        self.assertTrue(bool(cam_prim))

        initial_transform_item = usd_manip.model.get_item('initial_transform')
        tumble_item = usd_manip.model.get_item('tumble')
        transform_item = usd_manip.model.get_item('transform')

        self.__reset_initial_xf(usd_manip, initial_transform_item, cam_prim)
        usd_manip.model.set_floats(transform_item, _flatten_matrix(Gf.Matrix4d(1)))
        usd_manip.on_model_updated(transform_item)

        return (usd_manip, cam_prim, initial_transform_item, tumble_item)

    async def __test_tumble_camera(self, prim_path: Sdf.Path, rotations: List[Sequence[float]], epsilon: float = 1.0e-5):
        (usd_manip, cam_prim,
         initial_transform_item, tumble_item) = self.__setup_usdmanip_tumble_test(prim_path)

        rotateYXZ = cam_prim.GetAttribute('xformOp:rotateYXZ')
        self.assertIsNotNone(rotateYXZ)
        cur_rot = Gf.Vec3d(rotateYXZ.Get())
        self.assertTrue(Gf.IsClose(cur_rot, Gf.Vec3d(0, 0, 0), epsilon))

        is_linux = sys.platform.startswith('linux')

        for index, rotation in enumerate(rotations):
            usd_manip.model.set_floats(tumble_item, [-90, 0, 0])
            usd_manip.model._item_changed(tumble_item)
            self.__reset_initial_xf(usd_manip, initial_transform_item, cam_prim)

            cur_rot = Gf.Vec3d(rotateYXZ.Get())
            is_equal = Gf.IsClose(cur_rot, Gf.Vec3d(rotation), epsilon)
            if is_equal:
                continue

            # Linux and Windows are returning different results for some rotations that are essentially equivalent
            is_equal = True
            for current, expected in zip(cur_rot, rotation):
                if not Gf.IsClose(current, expected, epsilon):
                    expected = abs(expected)
                    is_equal = (expected == 180) or (expected == 360)
                    if not is_equal:
                        break

            self.assertTrue(is_equal,
                            msg=f"Rotation values differ: current: {cur_rot}, expected: {rotation}")

    async def __test_camera_YXZ_edit(self, rotations: List[Sequence[float]]):
        camera = UsdGeom.Camera.Define(self.stage, '/Camera')
        cam_prim = camera.GetPrim()
        cam_prim.CreateAttribute('omni:kit:centerOfInterest', Sdf.ValueTypeNames.Vector3d,
                                 True, Sdf.VariabilityUniform).Set(Gf.Vec3d(0, 0, -10))

        await self.__test_tumble_camera(cam_prim.GetPath(), rotations)

    async def test_camera_rotate(self):
        '''Test rotation values in USD (with controllerUseSRT set to False)'''
        await self.__test_camera_YXZ_edit([
            (0, -90, 0),
            (0, 180, 0),
            (0, 90, 0),
            (0, 0, 0)
        ])

    async def test_camera_rotate_SRT(self):
        '''Test rotation accumulation in USD with controllerUseSRT set to True'''
        settings = carb.settings.get_settings()
        try:
            settings.set('/persistent/app/camera/controllerUseSRT', True)
            await self.__test_camera_YXZ_edit([
                (0, -90, 0),
                (0, -180, 0),
                (0, -270, 0),
                (0, -360, 0)
            ])
        finally:
            settings.destroy_item('/persistent/app/camera/controllerUseSRT')

    async def test_camera_yup_in_zup(self):
        '''Test Viewport rotation of a camera from a y-up layer, referenced in a z-up stage'''

        await omni.usd.get_context().open_stage_async(str(USD_FILES.joinpath('yup_in_zup.usda')))
        self.stage = omni.usd.get_context().get_stage()

        await self.__test_tumble_camera(Sdf.Path('/World/yup_ref/Camera'),
            [
                (0, -90, 0),
                (0, 180, 0),
                (0, 90, 0),
                (0, 0, 0)
            ]
        )

    async def test_camera_zup_in_yup(self):
        '''Test Viewport rotation of a camera from a z-up layer, referenced in a y-up stage'''

        await omni.usd.get_context().open_stage_async(str(USD_FILES.joinpath('zup_in_yup.usda')))
        self.stage = omni.usd.get_context().get_stage()

        await self.__test_tumble_camera(Sdf.Path('/World/zup_ref/Camera'),
            [
                (0, 0, -90),
                (0, 0, 180),
                (0, 0, 90),
                (0, 0, 0)
            ]
        )
