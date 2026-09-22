# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['TestCommands']

import carb
from omni.kit.test import AsyncTestCase
import omni.kit.undo
import omni.usd
from pxr import Gf, Sdf, UsdGeom


# Test that the Viewport-level commands reach the proper methods
class TestViewportAPI:
    def __init__(self, usd_context_name, cam_path: str = None):
        self.usd_context_name = usd_context_name
        self.usd_context = omni.usd.get_context()
        self.stage = self.usd_context.get_stage()
        self.__camera_path = cam_path

    @property
    def camera_path(self):
        return self.__camera_path

    @camera_path.setter
    def camera_path(self, cam_path):
        self.__camera_path = cam_path


class TestCommands(AsyncTestCase):
    async def setUp(self):
        self.usd_context_name = ''
        self.usd_context = omni.usd.get_context(self.usd_context_name)
        await self.usd_context.new_stage_async()
        self.stage = self.usd_context.get_stage()

        self.stage.SetDefaultPrim(UsdGeom.Xform.Define(self.stage, '/World').GetPrim())

    async def tearDown(self):
        self.usd_context = None
        self.stage = None

    async def test_duplicate_camera(self):
        def get_num_xform_ops(cam: UsdGeom.Camera):
            xform_ops = cam.GetOrderedXformOps()
            return len(xform_ops) if xform_ops else 0

        cam_path = '/World/TestCamera'
        new_camera = UsdGeom.Camera.Define(self.stage, '/World/TestCamera')
        # This camera has no xformOps
        self.assertEqual(0, get_num_xform_ops(new_camera))

        omni.kit.commands.execute("DuplicateCameraCommand", camera_path=cam_path)

        # Should have duplicated to '/World/Camera'
        dup_camera_path = '/World/Camera'
        dup_camera = UsdGeom.Camera(self.stage.GetPrimAtPath(dup_camera_path))
        # Validate the new camera
        self.assertIsNotNone(dup_camera)
        self.assertTrue(bool(dup_camera))
        # Should have 3 xformOps, in order to honor the defaut camera roation order
        self.assertEqual(3, get_num_xform_ops(dup_camera))

        # Test duplication of implicit camera
        omni.kit.commands.execute("DuplicateCameraCommand", camera_path='/OmniverseKit_Persp')
        # Test both of these meta-data entries are true for an implicit Camera
        self.assertTrue(omni.usd.editor.is_hide_in_stage_window(self.stage.GetPrimAtPath('/OmniverseKit_Persp')))
        self.assertTrue(omni.usd.editor.is_no_delete(self.stage.GetPrimAtPath('/OmniverseKit_Persp')))
        num_xfops_1 = get_num_xform_ops(new_camera)

        # Should have duplicated to '/World/Camera_1'
        dup_camera_path = '/World/Camera_01'
        dup_camera = UsdGeom.Camera(self.stage.GetPrimAtPath(cam_path))
        # Validate the new camera
        self.assertIsNotNone(dup_camera)
        self.assertTrue(bool(dup_camera))
        # Should have same number of xformOps now
        self.assertEqual(num_xfops_1, get_num_xform_ops(dup_camera))
        # Test both of these meta-data entries are false after duplicating an implicit Camera
        self.assertFalse(omni.usd.editor.is_hide_in_stage_window(dup_camera.GetPrim()))
        self.assertFalse(omni.usd.editor.is_no_delete(dup_camera.GetPrim()))

    async def test_duplicate_camera_unlocked(self):
        cam_path = '/World/TestCamera'
        cam_lock = 'omni:kit:cameraLock'
        usd_camera = UsdGeom.Camera.Define(self.stage, '/World/TestCamera')

        prop = usd_camera.GetPrim().CreateAttribute(cam_lock, Sdf.ValueTypeNames.Bool, True)
        prop.Set(True)
        # Make sure the lock attribute is present and set to true
        self.assertTrue(usd_camera.GetPrim().GetAttribute(cam_lock).Get())
        omni.kit.commands.execute("DuplicateCameraCommand", camera_path=cam_path)

        cam_path = '/World/Camera'
        # Should have duplicated to '/World/Camera'
        new_camera = UsdGeom.Camera(self.stage.GetPrimAtPath(cam_path))
        # Validate the new camera
        self.assertIsNotNone(new_camera)
        self.assertTrue(bool(new_camera))
        # Make sure the lock attribute wasn't copied over
        self.assertFalse(new_camera.GetPrim().GetAttribute(cam_lock).IsValid())

        # Nothing should have affected the original
        self.assertTrue(usd_camera.GetPrim().GetAttribute(cam_lock).Get())

    async def test_duplicate_camera_with_name(self):
        cam_path = '/World/TestCamera'
        UsdGeom.Camera.Define(self.stage, '/World/TestCamera')

        new_cam_path = '/World/TestDuplicatedCamera'
        omni.kit.commands.execute("DuplicateCameraCommand", camera_path=cam_path, new_camera_path=new_cam_path)

        # Should have duplicated to '/World/TestDuplicatedCamera'
        camera = UsdGeom.Camera(self.stage.GetPrimAtPath(new_cam_path))
        # Validate the new camera
        self.assertIsNotNone(camera)
        self.assertTrue(bool(camera))

        # Undo the command
        omni.kit.undo.undo()
        # Camera should no longer be valid (its been deleted)
        self.assertFalse(bool(camera))

    async def test_duplicate_viewport_camera(self):
        cam_path = '/World/TestCamera'
        UsdGeom.Camera.Define(self.stage, cam_path)

        viewport_api = TestViewportAPI(self.usd_context_name, cam_path)
        omni.kit.commands.execute("DuplicateViewportCameraCommand", viewport_api=viewport_api)

        # Should have duplicated to '/World/Camera'
        new_cam_path = '/World/Camera'

        camera = UsdGeom.Camera(self.stage.GetPrimAtPath(new_cam_path))
        # Validate the new camera
        self.assertIsNotNone(camera)
        self.assertTrue(bool(camera))

        self.assertEqual(viewport_api.camera_path, new_cam_path)

        # Undo the command
        omni.kit.undo.undo()
        # Viewport should have been reset
        self.assertEqual(viewport_api.camera_path, cam_path)
        # Camera should no longer be valid (its been deleted)
        self.assertFalse(bool(camera))

    async def __test_duplicate_viewport_camera_hierarchy(self, rot_order: str = None):
        settings = carb.settings.get_settings()
        try:
            default_prim = self.stage.GetDefaultPrim()
            root_path = default_prim.GetPath().pathString if default_prim else ''

            parent_paths = (f'{root_path}/Xform0', f'{root_path}/Xform0/Xform1')
            cam_path = f'{parent_paths[1]}/TestCamera'

            UsdGeom.Xform.Define(self.stage, parent_paths[0])
            omni.kit.commands.execute("TransformPrimSRTCommand", path=parent_paths[0], new_translation=Gf.Vec3d(10, 10, 10))

            UsdGeom.Xform.Define(self.stage, parent_paths[1])
            omni.kit.commands.execute("TransformPrimSRTCommand", path=parent_paths[1], new_translation=Gf.Vec3d(10, 10, 10), new_rotation_euler=Gf.Vec3d(90, 0, 0))

            UsdGeom.Camera.Define(self.stage, cam_path)
            omni.kit.commands.execute("TransformPrimSRTCommand", path=cam_path, new_translation=Gf.Vec3d(10, 10, 10), new_rotation_euler=Gf.Vec3d(90, 0, 0))

            # Set the rotation order now to test that moving from an existing order to a new one works
            if rot_order:
                settings.set('/persistent/app/primCreation/DefaultCameraRotationOrder', rot_order)

            viewport_api = TestViewportAPI(self.usd_context_name, cam_path)
            omni.kit.commands.execute("DuplicateViewportCameraCommand", viewport_api=viewport_api)

            # Should have duplicated to '/World/Camera'
            new_cam_path = f'{root_path}/Camera'

            camera = UsdGeom.Camera(self.stage.GetPrimAtPath(new_cam_path))
            # Validate the new camera
            self.assertIsNotNone(camera)
            self.assertTrue(bool(camera))
            self.assertEqual(viewport_api.camera_path, new_cam_path)

            src_xform = omni.usd.get_world_transform_matrix(self.stage.GetPrimAtPath(cam_path))
            dst_xform = omni.usd.get_world_transform_matrix(self.stage.GetPrimAtPath(new_cam_path))

            self.assertTrue(Gf.IsClose(src_xform, dst_xform, 1.0e-5))

            if rot_order:
                self.assertTrue(f'xformOp:rotate{rot_order}' in camera.GetXformOpOrderAttr().Get())

        finally:
            if rot_order:
                settings.destroy_item('/persistent/app/primCreation/DefaultCameraRotationOrder')

    async def test_duplicate_viewport_camera_hierarchy(self):
        await self.__test_duplicate_viewport_camera_hierarchy()

    async def test_duplicate_viewport_camera_hierarchy_with_order(self):
        """Test duplictaing a camera that is nested in a transformed honors default camera rotation order"""
        await self.__test_duplicate_viewport_camera_hierarchy('XYZ')

        # Test again with a different order and also without a default prim
        await self.usd_context.new_stage_async()
        self.stage = self.usd_context.get_stage()
        await self.__test_duplicate_viewport_camera_hierarchy('ZYX')

    async def test_set_viewport_camera(self):
        cam_path = '/World/TestCamera'
        cam_path2 = '/World/TestCamera2'
        UsdGeom.Camera.Define(self.stage, cam_path)
        UsdGeom.Camera.Define(self.stage, cam_path)

        viewport_api = TestViewportAPI(self.usd_context_name, cam_path)
        omni.kit.commands.execute("SetViewportCameraCommand", camera_path=cam_path2, viewport_api=viewport_api)

        # Should now be set to cam_path2
        self.assertEqual(viewport_api.camera_path, cam_path2)

        # Undo the command
        omni.kit.undo.undo()
        # Should now be set to cam_path
        self.assertEqual(viewport_api.camera_path, cam_path)
