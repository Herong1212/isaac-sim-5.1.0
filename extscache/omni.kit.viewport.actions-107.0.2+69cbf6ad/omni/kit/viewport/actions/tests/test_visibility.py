# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from omni.kit.viewport.actions.visibility import VisibilityEdit

import carb
import omni.kit.app
import omni.kit.test
import omni.timeline

from pxr import Sdf, Usd, UsdGeom

from functools import partial
from pathlib import Path

TEST_DATA_PATH = Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
).resolve().absolute().joinpath("data", "tests")

USD_TEST_DATA_PATH = TEST_DATA_PATH.joinpath("usd")


class TestVisibilitySetting(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        super().setUp()
        self.usd_context = omni.usd.get_context()
        await self.usd_context.new_stage_async()

    # After running each test
    async def tearDown(self):
        super().tearDown()

    @staticmethod
    def __is_in_set(prim_set: set, prim: Usd.Prim, prim_path: Sdf.Path) -> bool:  # pragma: no cover
        return prim.GetTypeName() in prim_set

    @staticmethod
    def __make_callback(prim_set: set):
        return prim_set

    async def test_hide_show_skeletons(self):
        usd_path = USD_TEST_DATA_PATH.joinpath("visibility.usda")
        success, error = await self.usd_context.open_stage_async(str(usd_path))
        self.assertTrue(success, error)
        stage = self.usd_context.get_stage()

        is_skel_test = self.__make_callback({"SkelRoot"})
        vis_edit = VisibilityEdit(stage, types_to_show=None, types_to_hide=is_skel_test)
        vis_edit.run()

        # Skeleton should still be set to invisible
        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/SkelRoot")).ComputeVisibility()
        self.assertEqual(str(visibility), "invisible")

        # Everything else should be have kept inherited
        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Mesh")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Cone")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Cube")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Cylinder")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Sphere")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Capsule")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_03/Cube")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_03/Points")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_04/Cube")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_04/Points")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        vis_edit = VisibilityEdit(stage, types_to_show=is_skel_test, types_to_hide=None)
        vis_edit.run()

        # Skeleton should still be restored to inherited
        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/SkelRoot")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        # Everything else should have kept inherited
        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Mesh")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Cone")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Cube")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Cylinder")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Sphere")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Capsule")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_03/Cube")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_04/Cube")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_03/Points")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_04/Points")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

    async def test_hide_show_meshes(self):
        usd_path = USD_TEST_DATA_PATH.joinpath("visibility.usda")
        success, error = await self.usd_context.open_stage_async(str(usd_path))
        self.assertTrue(success, error)

        stage = self.usd_context.get_stage()

        is_in_mesh = self.__make_callback({"Mesh", "Cone", "Cube", "Cylinder", "Sphere", "Capsule"})
        vis_edit = VisibilityEdit(stage, types_to_show=None, types_to_hide=is_in_mesh)
        vis_edit.run()

        # Skeleton should still be visible
        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/SkelRoot")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        # Points should have kept inherited
        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_03/Points")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_04/Points")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        # Everything else should be off or inherited
        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Mesh")).ComputeVisibility()
        self.assertEqual(str(visibility), "invisible")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Cone")).ComputeVisibility()
        self.assertEqual(str(visibility), "invisible")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Cube")).ComputeVisibility()
        self.assertEqual(str(visibility), "invisible")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Cylinder")).ComputeVisibility()
        self.assertEqual(str(visibility), "invisible")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Sphere")).ComputeVisibility()
        self.assertEqual(str(visibility), "invisible")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Capsule")).ComputeVisibility()
        self.assertEqual(str(visibility), "invisible")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_03/Cube")).ComputeVisibility()
        self.assertEqual(str(visibility), "invisible")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_04/Cube")).ComputeVisibility()
        self.assertEqual(str(visibility), "invisible")

        vis_edit = VisibilityEdit(stage, types_to_show=is_in_mesh, types_to_hide=None)
        vis_edit.run()

        # Skeleton should still be visible
        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/SkelRoot")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        # Points should have kept inherited
        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_03/Points")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_04/Points")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        # Everything else should be restored to inherited
        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Mesh")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Cone")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Cube")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Cylinder")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Sphere")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Capsule")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_03/Cube")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshInstances_04/Cube")).ComputeVisibility()
        self.assertEqual(str(visibility), "inherited")

    async def test_hide_show_meshes_instanceable_references(self):
        usd_path = USD_TEST_DATA_PATH.joinpath("referenced", "scene.usda")
        success, error = await self.usd_context.open_stage_async(str(usd_path))
        self.assertTrue(success, error)

        stage = self.usd_context.get_stage()

        is_in_mesh = self.__make_callback({"Mesh", "Cone", "Cube", "Cylinder", "Sphere", "Capsule"})
        vis_edit = VisibilityEdit(stage, types_to_show=None, types_to_hide=is_in_mesh)
        vis_edit.run()

        visibility_a = UsdGeom.Imageable(stage.GetPrimAtPath("/World/envs/env_0/bolt0/M20_Bolt_Tight_Visual")).ComputeVisibility()
        visibility_b = UsdGeom.Imageable(stage.GetPrimAtPath("/World/envs/env_1/bolt0/M20_Bolt_Tight_Visual")).ComputeVisibility()
        self.assertEqual(str(visibility_a), 'invisible')
        self.assertEqual(str(visibility_b), 'invisible')

        vis_edit = VisibilityEdit(stage, types_to_show=is_in_mesh, types_to_hide=None)
        vis_edit.run()

        visibility_a = UsdGeom.Imageable(stage.GetPrimAtPath("/World/envs/env_0/bolt0/M20_Bolt_Tight_Visual")).ComputeVisibility()
        visibility_b = UsdGeom.Imageable(stage.GetPrimAtPath("/World/envs/env_1/bolt0/M20_Bolt_Tight_Visual")).ComputeVisibility()
        self.assertEqual(str(visibility_a), 'inherited')
        self.assertEqual(str(visibility_b), 'inherited')

    async def __test_hide_show_hide_camera_at_time(self):
        usd_path = USD_TEST_DATA_PATH.joinpath("cam_visibility.usda")
        success, error = await self.usd_context.open_stage_async(str(usd_path))
        self.assertTrue(success, error)

        stage = self.usd_context.get_stage()

        # Default should be visible
        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Camera_Frontal_50mm")).ComputeVisibility()
        self.assertEqual(str(visibility), 'inherited')

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Camera_Focal_Headlight_50mm")).ComputeVisibility()
        self.assertEqual(str(visibility), 'inherited')

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Camera_Establishing_28mm")).ComputeVisibility()
        self.assertEqual(str(visibility), 'inherited')

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Camera")).ComputeVisibility()
        self.assertEqual(str(visibility), 'inherited')

        # Hide cameras
        is_camera = self.__make_callback({"Camera"})
        vis_edit = VisibilityEdit(stage, types_to_show=None, types_to_hide=is_camera)
        vis_edit.run()

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Camera_Frontal_50mm")).ComputeVisibility()
        self.assertEqual(str(visibility), 'invisible')

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Camera_Focal_Headlight_50mm")).ComputeVisibility()
        self.assertEqual(str(visibility), 'invisible')

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Camera_Establishing_28mm")).ComputeVisibility()
        self.assertEqual(str(visibility), 'invisible')

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Camera")).ComputeVisibility()
        self.assertEqual(str(visibility), 'invisible')

        # Show cameras
        vis_edit = VisibilityEdit(stage, types_to_show=is_camera, types_to_hide=None)
        vis_edit.run()

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Camera_Frontal_50mm")).ComputeVisibility()
        self.assertEqual(str(visibility), 'inherited')

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Camera_Focal_Headlight_50mm")).ComputeVisibility()
        self.assertEqual(str(visibility), 'inherited')

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Camera_Establishing_28mm")).ComputeVisibility()
        self.assertEqual(str(visibility), 'inherited')

        visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/Camera")).ComputeVisibility()
        self.assertEqual(str(visibility), 'inherited')

    async def test_hide_show_hide_camera(self):
        """Test show and hide of camera works at default time"""
        await self.__test_hide_show_hide_camera_at_time()

    async def test_hide_show_hide_camera_at_time(self):
        """Test show and hide of camera works at user time"""
        try:
            omni.timeline.get_timeline_interface().set_current_time(100)
            await self.__test_hide_show_hide_camera_at_time()
        finally:
            omni.timeline.get_timeline_interface().set_current_time(0)

    async def test_camera_visibility_stage_window_hidden(self):
        """Test show and hide of prims that accounts for objects hidden in stage window"""
        usd_path = USD_TEST_DATA_PATH.joinpath("stage_window_hidden.usda")
        success, error = await self.usd_context.open_stage_async(str(usd_path))
        self.assertTrue(success, error)

        stage = self.usd_context.get_stage()

        # Default should be visible
        def test_visibility(expected):
            if isinstance(expected, str):
                expected = [expected] * 4

            visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/CameraA")).ComputeVisibility()
            self.assertEqual(str(visibility), expected[0])

            visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/CameraB")).ComputeVisibility()
            self.assertEqual(str(visibility), expected[1])

            visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshA")).ComputeVisibility()
            self.assertEqual(str(visibility), expected[2])

            visibility = UsdGeom.Imageable(stage.GetPrimAtPath("/World/MeshB")).ComputeVisibility()
            self.assertEqual(str(visibility), expected[3])

        test_visibility('inherited')

        # Hide all camera and mesh
        prim_test = self.__make_callback({"Camera", "Mesh"})
        vis_edit = VisibilityEdit(stage, types_to_show=None, types_to_hide=prim_test)
        vis_edit.run()
        test_visibility('invisible')

        # Revert back and re-test
        vis_edit = VisibilityEdit(stage, types_to_show=prim_test, types_to_hide=None)
        vis_edit.run()
        test_visibility('inherited')

        settings = carb.settings.get_settings()
        igswh = settings.get('/exts/omni.kit.viewport.actions/visibilityToggle/ignoreStageWindowHidden')
        try:
            settings.set('/exts/omni.kit.viewport.actions/visibilityToggle/ignoreStageWindowHidden', True)

            vis_edit = VisibilityEdit(stage, types_to_show=None, types_to_hide=prim_test)
            vis_edit.run()
            test_visibility(['invisible', 'inherited', 'invisible', 'inherited'])

            # Revert back and re-test
            vis_edit = VisibilityEdit(stage, types_to_show=prim_test, types_to_hide=None)
            vis_edit.run()
            test_visibility('inherited')
        finally:
            settings.set('/exts/omni.kit.viewport.actions/visibilityToggle/ignoreStageWindowHidden', igswh)
