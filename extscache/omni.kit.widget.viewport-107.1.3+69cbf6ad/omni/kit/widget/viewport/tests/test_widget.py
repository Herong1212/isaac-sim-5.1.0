## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["TestWidgetAPI"]

from pathlib import Path

from pxr import Gf, Sdf, Usd, UsdGeom

import carb
from omni.kit.test import get_test_output_path
from omni.ui.tests.test_base import OmniUiTest
import omni.kit.commands
import omni.usd

from omni.kit.widget.viewport import ViewportWidget
from omni.kit.widget.viewport.display_delegate import ViewportDisplayDelegate, OverlayViewportDisplayDelegate


CURRENT_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.widget.viewport}/data")).absolute().resolve()
TEST_FILES_DIR = CURRENT_PATH.joinpath("tests")
USD_FILES_DIR = TEST_FILES_DIR.joinpath("usd")
OUTPUTS_DIR = Path(get_test_output_path())

TEST_WIDTH, TEST_HEIGHT = 360, 240


class TestWidgetAPI(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await omni.usd.get_context().new_stage_async()

    # After running each test
    async def tearDown(self):
        await super().tearDown()
        await self.linux_gpu_shutdown_workaround()

    async def linux_gpu_shutdown_workaround(self, usd_context_name : str = ""):
        await self.wait_n_updates(10)
        omni.usd.release_all_hydra_engines(omni.usd.get_context(usd_context_name))
        await self.wait_n_updates(10)

    async def open_usd_file(self, filename: str, resolved: bool = False):
        usd_context = omni.usd.get_context()
        usd_path = str(USD_FILES_DIR.joinpath(filename) if not resolved else filename)
        await usd_context.open_stage_async(usd_path)
        return usd_context

    def assertAlmostEqual(self, a, b, places: int = 4):
        if isinstance(a, (float, int)):
            super().assertAlmostEqual(a, b, places)
        else:
            for va, vb in zip(a, b):
                super().assertAlmostEqual(va, vb, places)

    async def test_widget_pre_open(self):
        """Test ViewportWidget creation with existing UsdContext and Usd.Stage and startup resolutin settings"""
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        usd_context = await self.open_usd_file("cube.usda")
        self.assertIsNotNone(usd_context.get_stage())
        usd_context_stage = usd_context.get_stage()

        settings = carb.settings.get_settings()
        viewport_widget = None
        try:
            settings.set("/app/renderer/resolution/width", 400)
            settings.set("/app/renderer/resolution/height", 400)
            await self.wait_n_updates(6)

            viewport_widget = ViewportWidget()
            viewport_api = viewport_widget.viewport_api

            # Test omni.usd.UsdContext and Usd.Stage properties
            self.assertEqual(viewport_api.usd_context, usd_context)
            self.assertEqual(viewport_api.stage, usd_context_stage)
            self.assertEqual(viewport_api.camera_path, Sdf.Path("/OmniverseKit_Persp"))

            # Test startup resolution
            self.assertEqual(viewport_api.resolution, (400, 400))
            self.assertEqual(viewport_api.resolution_scale, 1.0)

            # Test deprecated resolution API methods (not properties)
            self.assertEqual(viewport_api.resolution, viewport_api.get_texture_resolution())
            viewport_api.set_texture_resolution((200, 200))
            self.assertEqual(viewport_api.resolution, (200, 200))

            # Test deprecated camera API methods (not properties)
            self.assertEqual(viewport_api.camera_path, viewport_api.get_active_camera())
            viewport_api.set_active_camera(Sdf.Path("/OmniverseKit_Top"))
            self.assertEqual(viewport_api.camera_path, Sdf.Path("/OmniverseKit_Top"))

        finally:
            settings.destroy_item("/app/renderer/resolution/width")
            settings.destroy_item("/app/renderer/resolution/height")

            if viewport_widget:
                viewport_widget.destroy()
                del viewport_widget

            await self.wait_n_updates(6)
            await self.finalize_test_no_image()

    async def test_widget_post_open(self):
        """Test ViewportWidget adopts a change to the Usd.Stage after it is visible and startup resolution scale setting"""
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        settings = carb.settings.get_settings()
        viewport_widget = None
        try:
            settings.set("/app/renderer/resolution/width", 400)
            settings.set("/app/renderer/resolution/height", 400)
            settings.set("/app/renderer/resolution/multiplier", 0.5)
            await self.wait_n_updates(6)

            viewport_widget = ViewportWidget()
            viewport_api = viewport_widget.viewport_api

            # Test omni.usd.UsdContext and Usd.Stage properties
            usd_context = await self.open_usd_file("sphere.usda")
            self.assertIsNotNone(usd_context.get_stage())
            usd_context_stage = usd_context.get_stage()

            # Test display-delegate API
            await self.__test_display_delegate(viewport_widget)

            self.assertEqual(viewport_api.usd_context, usd_context)
            self.assertEqual(viewport_api.stage, usd_context_stage)
            self.assertEqual(viewport_api.camera_path, Sdf.Path("/OmniverseKit_Persp"))

            # Test startup resolution
            self.assertEqual(viewport_api.resolution, (200, 200))
            self.assertEqual(viewport_api.resolution_scale, 0.5)
        finally:
            settings.destroy_item("/app/renderer/resolution/width")
            settings.destroy_item("/app/renderer/resolution/height")
            settings.destroy_item("/app/renderer/resolution/multiplier")

            if viewport_widget:
                viewport_widget.destroy()
                del viewport_widget

            await self.wait_n_updates(6)
            await self.finalize_test_no_image()

    async def test_widget_custom_camera_saved(self):
        """Test ViewportWidget will absorb the stored Kit bound camera"""
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        usd_context = await self.open_usd_file("custom_camera.usda")
        self.assertIsNotNone(usd_context.get_stage())
        usd_context_stage = usd_context.get_stage()

        viewport_widget = ViewportWidget(resolution=(TEST_WIDTH, TEST_HEIGHT))

        viewport_api = viewport_widget.viewport_api
        self.assertEqual(viewport_api.usd_context, usd_context)
        self.assertEqual(viewport_api.stage, usd_context_stage)
        self.assertEqual(viewport_api.camera_path, Sdf.Path("/World/Camera"))

        cam_prim = viewport_api.stage.GetPrimAtPath(viewport_api.camera_path)
        self.assertTrue(bool(cam_prim))
        cam_geom = UsdGeom.Camera(cam_prim)
        self.assertTrue(bool(cam_geom))
        coi_prop = cam_prim.GetProperty("omni:kit:centerOfInterest")
        self.assertTrue(bool(coi_prop))
        coi_prop.Get()

        world_pos = viewport_api.transform.Transform(Gf.Vec3d(0, 0, 0))
        self.assertAlmostEqual(world_pos, Gf.Vec3d(250, 825, 800))
        self.assertAlmostEqual(coi_prop.Get(), Gf.Vec3d(0, 0, -1176.0633486339075))

        viewport_widget.destroy()
        del viewport_widget

        await self.finalize_test_no_image()

    async def test_widget_custom_camera_contructor(self):
        """Test ViewportWidget can be contructed with a specified Camera"""
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        usd_context = await self.open_usd_file("custom_camera.usda")
        self.assertIsNotNone(usd_context.get_stage())
        usd_context_stage = usd_context.get_stage()

        viewport_widget = ViewportWidget(resolution=(TEST_WIDTH, TEST_HEIGHT), camera_path="/World/Camera_01")

        viewport_api = viewport_widget.viewport_api
        self.assertEqual(viewport_api.usd_context, usd_context)
        self.assertEqual(viewport_api.stage, usd_context_stage)
        self.assertEqual(viewport_api.camera_path, Sdf.Path("/World/Camera_01"))

        cam_prim = viewport_api.stage.GetPrimAtPath(viewport_api.camera_path)
        self.assertTrue(bool(cam_prim))
        cam_geom = UsdGeom.Camera(cam_prim)
        self.assertTrue(bool(cam_geom))
        coi_prop = cam_prim.GetProperty("omni:kit:centerOfInterest")
        self.assertTrue(bool(coi_prop))
        coi_prop.Get()

        world_pos = viewport_api.transform.Transform(Gf.Vec3d(0, 0, 0))
        self.assertAlmostEqual(world_pos, Gf.Vec3d(350, 650, -900))
        self.assertAlmostEqual(coi_prop.Get(), Gf.Vec3d(0, 0, -1164.0446726822815))

        viewport_widget.destroy()
        del viewport_widget

        await self.finalize_test_no_image()

    async def test_implicit_cameras(self):
        """Test ViewportWidget creation with existing UsdContext and Usd.Stage"""
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        usd_context = await self.open_usd_file("cube.usda")
        self.assertIsNotNone(usd_context.get_stage())
        usd_context_stage = usd_context.get_stage()

        viewport_widget = ViewportWidget(resolution=(TEST_WIDTH, TEST_HEIGHT))

        viewport_api = viewport_widget.viewport_api
        self.assertEqual(viewport_api.usd_context, usd_context)
        self.assertEqual(viewport_api.stage, usd_context_stage)
        self.assertEqual(viewport_api.camera_path, Sdf.Path("/OmniverseKit_Persp"))

        time = Usd.TimeCode.Default()

        def test_default_camera_position(cam_path: str, expected_pos: Gf.Vec3d, expected_rot: Gf.Vec3d = None):
            prim = usd_context.get_stage().GetPrimAtPath(cam_path)
            camera = UsdGeom.Camera(prim) if prim else None
            self.assertTrue(bool(camera))

            world_xform = camera.ComputeLocalToWorldTransform(time)
            world_pos = world_xform.Transform(Gf.Vec3d(0, 0, 0))
            self.assertAlmostEqual(world_pos, expected_pos)

            if expected_rot:
                rot_prop = prim.GetProperty("xformOp:rotateXYZ")
                self.assertIsNotNone(rot_prop)

                rot_value = rot_prop.Get()
                self.assertAlmostEqual(rot_value, expected_rot)

        test_default_camera_position("/OmniverseKit_Persp", Gf.Vec3d(500, 500, 500), Gf.Vec3d(-35.26439, 45, 0))
        test_default_camera_position("/OmniverseKit_Front", Gf.Vec3d(0, 0, 50000), Gf.Vec3d(0, 0, 0))
        test_default_camera_position("/OmniverseKit_Top", Gf.Vec3d(0, 50000, 0), Gf.Vec3d(90, 0, 180))
        test_default_camera_position("/OmniverseKit_Right", Gf.Vec3d(-50000, 0, 0), Gf.Vec3d(0, -90, 0))

        output_file = str(OUTPUTS_DIR.joinpath("implicit_cameras_same.usda"))
        (result, err, saved_layers) = await usd_context.save_as_stage_async(output_file) # noqa PLW0612
        self.assertTrue(result)

        await omni.usd.get_context().new_stage_async()
        await usd_context.open_stage_async(output_file)

        test_default_camera_position("/OmniverseKit_Persp", Gf.Vec3d(500, 500, 500))
        test_default_camera_position("/OmniverseKit_Front", Gf.Vec3d(0, 0, 50000))
        test_default_camera_position("/OmniverseKit_Top", Gf.Vec3d(0, 50000, 0))
        test_default_camera_position("/OmniverseKit_Right", Gf.Vec3d(-50000, 0, 0))

        # Change OmniverseKit_Persp location
        omni.kit.commands.create(
            "TransformPrimCommand",
            path="/OmniverseKit_Persp",
            new_transform_matrix=Gf.Matrix4d().SetTranslate(Gf.Vec3d(-100, -200, -300)),
            old_transform_matrix=Gf.Matrix4d().SetTranslate(Gf.Vec3d(500, 500, 500)),
            time_code=time,
        ).do()

        # Change OmniverseKit_Front location
        omni.kit.commands.create(
            "TransformPrimCommand",
            path="/OmniverseKit_Front",
            new_transform_matrix=Gf.Matrix4d().SetTranslate(Gf.Vec3d(0, 0, 56789)),
            old_transform_matrix=Gf.Matrix4d().SetTranslate(Gf.Vec3d(0, 0, 50000)),
            time_code=time,
        ).do()

        # Change OmniverseKit_Top aperture
        UsdGeom.Camera(usd_context.get_stage().GetPrimAtPath("/OmniverseKit_Top")).GetHorizontalApertureAttr().Set(50000)

        output_file = str(OUTPUTS_DIR.joinpath("implicit_cameras_changed.usda"))
        (result, err, saved_layers) = await usd_context.save_as_stage_async(output_file) # noqa PLW0612
        self.assertTrue(result)

        await omni.usd.get_context().new_stage_async()
        await usd_context.open_stage_async(output_file)

        test_default_camera_position("/OmniverseKit_Persp", Gf.Vec3d(-100, -200, -300))
        test_default_camera_position("/OmniverseKit_Front", Gf.Vec3d(0, 0, 56789))
        # These haven"t changed and should be default
        test_default_camera_position("/OmniverseKit_Top", Gf.Vec3d(0, 50000, 0))
        test_default_camera_position("/OmniverseKit_Right", Gf.Vec3d(-50000, 0, 0))

        # Test ortho aperture change is picked up
        horiz_ap = UsdGeom.Camera(usd_context.get_stage().GetPrimAtPath("/OmniverseKit_Top")).GetHorizontalApertureAttr().Get()
        self.assertAlmostEqual(horiz_ap, 50000)

        # Test implicit camera creation for existing Z-Up scene
        #
        usd_context = await self.open_usd_file("implicit_cams_z_up.usda")
        self.assertIsNotNone(usd_context.get_stage())
        usd_context_stage = usd_context.get_stage()

        self.assertEqual(viewport_api.camera_path, Sdf.Path("/OmniverseKit_Top"))

        test_default_camera_position("/OmniverseKit_Persp", Gf.Vec3d(500, 500, 500), Gf.Vec3d(54.73561, 0, 135))
        test_default_camera_position("/OmniverseKit_Front", Gf.Vec3d(500, 0, 0), Gf.Vec3d(90, 0, 90))
        test_default_camera_position("/OmniverseKit_Top", Gf.Vec3d(0, 0, 25), Gf.Vec3d(0, 0, -90))
        test_default_camera_position("/OmniverseKit_Right", Gf.Vec3d(0, -50000, 0), Gf.Vec3d(90, 0, 0))

        # Test that creation of another ViewportWidget doesn"t affect existing implict caameras
        viewport_widget_2 = ViewportWidget(resolution=(TEST_WIDTH, TEST_HEIGHT))
        test_default_camera_position("/OmniverseKit_Persp", Gf.Vec3d(500, 500, 500), Gf.Vec3d(54.73561, 0, 135))
        viewport_widget_2.destroy()
        del viewport_widget_2

        # Test saving metadata to usd, so copy the input files to writeable temp files
        from shutil import copyfile
        tmp_layers = str(OUTPUTS_DIR.joinpath("layers.usda"))
        copyfile(str(USD_FILES_DIR.joinpath("layers.usda")), tmp_layers)
        copyfile(str(USD_FILES_DIR.joinpath("sublayer.usda")), str(OUTPUTS_DIR.joinpath("sublayer.usda")))
        # Open the copy and validate the default camera
        usd_context = await self.open_usd_file(tmp_layers, True)
        self.assertEqual(viewport_api.camera_path, Sdf.Path("/OmniverseKit_Persp"))

        # Switch to a known camera and re-validate
        viewport_api.camera_path = "/World/Camera"
        self.assertEqual(viewport_api.camera_path, Sdf.Path("/World/Camera"))

        # Save the file and re-open it
        # XXX: Need to dirty something in the stage for save to take affect
        stage = usd_context.get_stage()
        stage.GetPrimAtPath(viewport_api.camera_path).GetAttribute("focalLength").Set(51)
        # Move the target layer to a sub-layer and then attmept the save
        with Usd.EditContext(stage, stage.GetLayerStack()[-1]):
            await usd_context.save_stage_async()
            await self.wait_n_updates(1)
            await omni.usd.get_context().new_stage_async()

        # Re-open
        usd_context = await self.open_usd_file(tmp_layers, True)
        # Camera should match what was just saved
        self.assertEqual(viewport_api.camera_path, Sdf.Path("/World/Camera"))

        # Test dynmically switching Stage up-axis
        async def set_stage_axis(stage, cam_prim, up_axis: str, n_frames: int = 2):
            stage.SetMetadata(UsdGeom.Tokens.upAxis, up_axis)
            await self.wait_n_updates(n_frames)
            return UsdGeom.Xformable(cam_prim).GetLocalTransformation()

        await omni.usd.get_context().new_stage_async()
        usd_context = omni.usd.get_context()
        self.assertIsNotNone(usd_context)

        stage = usd_context.get_stage()
        self.assertIsNotNone(stage)

        cam_prim = stage.GetPrimAtPath(viewport_api.camera_path)
        self.assertIsNotNone(cam_prim)
        cam_xformable = UsdGeom.Xformable(cam_prim)
        self.assertIsNotNone(cam_xformable)
        self.assertEqual(cam_prim.GetPath().pathString, "/OmniverseKit_Persp")

        xform_y = await set_stage_axis(stage, cam_prim, "Y")
        xform_y1 = cam_xformable.GetLocalTransformation()
        self.assertEqual(xform_y, xform_y1)
        self.assertAlmostEqual(xform_y.ExtractRotation().GetAxis(), Gf.Vec3d(-0.59028449177967, 0.7692737418738016, 0.24450384215364918))

        xform_z = await set_stage_axis(stage, cam_prim, "Z")
        self.assertNotEqual(xform_y, xform_z)
        self.assertAlmostEqual(xform_z.ExtractRotation().GetAxis(), Gf.Vec3d(0.1870534627395223, 0.4515870066346049, 0.8723990930279281))

        xform_x = await set_stage_axis(stage, cam_prim, "X")
        self.assertNotEqual(xform_x, xform_z)
        self.assertNotEqual(xform_x, xform_y)
        self.assertAlmostEqual(xform_x.ExtractRotation().GetAxis(), Gf.Vec3d(0.541766002079245, 0.07132485246922922, 0.8374976802423478))

        texture_pixel, vp_api = viewport_api.map_ndc_to_texture((0, 0))
        self.assertAlmostEqual(texture_pixel, (0.5, 0.5))
        self.assertEqual(vp_api, viewport_api)

        # Test return of Viewport is None when NDC is out of bounds
        texture_pixel, vp_api = viewport_api.map_ndc_to_texture((-2, -2))
        self.assertIsNone(vp_api)

        # Test return of Viewport is None when NDC is out of bounds
        texture_pixel, vp_api = viewport_api.map_ndc_to_texture((2, 2))
        self.assertIsNone(vp_api)

        # Test camera is correctly positioned/labeled with new stage and Z or Y setting
        settings = carb.settings.get_settings()

        async def new_stage_with_up_setting(up_axis: str, n_frames: int = 2):
            settings.set("/persistent/app/stage/upAxis", up_axis)
            await self.wait_n_updates(n_frames)

            await omni.usd.get_context().new_stage_async()

            usd_context = omni.usd.get_context()
            self.assertIsNotNone(usd_context)

            stage = usd_context.get_stage()
            self.assertIsNotNone(stage)

            cam_prim = stage.GetPrimAtPath(viewport_api.camera_path)
            return UsdGeom.Xformable(cam_prim).GetLocalTransformation()

        # Switch to new stage as Z-up and test against values from previous Z-up
        try:
            xform_z = await new_stage_with_up_setting("Z")
            self.assertNotEqual(xform_y, xform_z)
            self.assertAlmostEqual(xform_z.ExtractRotation().GetAxis(), Gf.Vec3d(0.1870534627395223, 0.4515870066346049, 0.8723990930279281))
        finally:
            settings.destroy_item("/persistent/app/stage/upAxis")

        try:
            # Test again against default up as Y
            xform_y1 = await new_stage_with_up_setting("Y")
            self.assertEqual(xform_y, xform_y1)
            self.assertAlmostEqual(xform_y.ExtractRotation().GetAxis(), Gf.Vec3d(-0.59028449177967, 0.7692737418738016, 0.24450384215364918))
        finally:
            settings.destroy_item("/persistent/app/stage/upAxis")

        # Test opeinig a file with implicit cameras saved into it works properly
        usd_context = await self.open_usd_file("implcit_precision.usda")
        self.assertIsNotNone(usd_context.get_stage())
        test_default_camera_position("/OmniverseKit_Persp", Gf.Vec3d(-1500, 400, 500), Gf.Vec3d(-15, 751, 0))
        test_default_camera_position("/OmniverseKit_Front", Gf.Vec3d(0, 0, 50000), Gf.Vec3d(0, 0, 0))
        test_default_camera_position("/OmniverseKit_Top", Gf.Vec3d(0, 50000, 0), Gf.Vec3d(90, 0, 180))
        test_default_camera_position("/OmniverseKit_Right", Gf.Vec3d(-50000, 0, 0), Gf.Vec3d(0, -90, 0))

        await self.__test_camera_startup_values(viewport_widget)

        def get_tr(stage: Usd.Stage, cam: str):
            xf = UsdGeom.Camera(stage.GetPrimAtPath(f"/OmniverseKit_{cam}")).ComputeLocalToWorldTransform(0)
            return xf.ExtractTranslation()

        def get_rot(stage: Usd.Stage, cam: str):
            xf = UsdGeom.Camera(stage.GetPrimAtPath(f"/OmniverseKit_{cam}")).ComputeLocalToWorldTransform(0)
            # decomp = (Gf.Vec3d(-1, 0, 0), Gf.Vec3d(0, -1, 0), Gf.Vec3d(0, 0, 1))
            rotation = xf.ExtractRotation().Decompose(Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis())
            return rotation

        # Test re-opening ortho cameras keep orthogonal rotations
        usd_context = await self.open_usd_file("ortho_y.usda")
        stage = omni.usd.get_context().get_stage()
        self.assertTrue(Gf.IsClose(get_rot(stage, "Top"), Gf.Vec3d(-90, 0, -180), 0.00001))
        self.assertTrue(Gf.IsClose(get_rot(stage, "Front"), Gf.Vec3d(0, 0, 0), 0.00001))
        self.assertTrue(Gf.IsClose(get_rot(stage, "Right"), Gf.Vec3d(0, -90, 0), 0.00001))

        usd_context = await self.open_usd_file("ortho_z.usda")
        stage = omni.usd.get_context().get_stage()
        self.assertTrue(Gf.IsClose(get_rot(stage, "Top"), Gf.Vec3d(0, 0, -90), 0.00001))
        self.assertTrue(Gf.IsClose(get_rot(stage, "Front"), Gf.Vec3d(90, 90, 0), 0.00001))
        self.assertTrue(Gf.IsClose(get_rot(stage, "Right"), Gf.Vec3d(90, 0, 0), 0.00001))

        usd_context = await self.open_usd_file("cam_prop_declaration_only.usda")
        stage = omni.usd.get_context().get_stage()
        self.assertTrue(Gf.IsClose(get_tr(stage, "Persp"), Gf.Vec3d(-417, 100, -110), 0.00001))
        self.assertTrue(Gf.IsClose(get_tr(stage, "Top"), Gf.Vec3d(0, 50000, 0), 0.00001))
        self.assertTrue(Gf.IsClose(get_tr(stage, "Front"), Gf.Vec3d(0, 0, 50000), 0.00001))
        self.assertTrue(Gf.IsClose(get_tr(stage, "Right"), Gf.Vec3d(-50000, 0, 0), 0.00001))

        viewport_widget.destroy()
        del viewport_widget

        await self.finalize_test_no_image()

    async def test_dont_save_implicit_cameras(self):
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        self.assertIsNotNone(usd_context.get_stage())
        settings = carb.settings.get_settings()
        # Save current state so it restored
        shouldsave = settings.get("/app/omni.usd/storeCameraSettingsToUsdStage")
        try:
            settings.set("/app/omni.usd/storeCameraSettingsToUsdStage", False)
            output_file = str(OUTPUTS_DIR.joinpath("dont_save_implicit_cameras.usda"))
            (result, err, saved_layers) = await usd_context.save_as_stage_async(output_file) # noqa PLW0612
            self.assertTrue(result)
            usd_context = await self.open_usd_file(output_file, True)
            stage = usd_context.get_stage()
            self.assertFalse(stage.HasMetadataDictKey("customLayerData", "cameraSettings"))
        except Exception as e:
            raise e
        finally:
            settings.set("/app/omni.usd/storeCameraSettingsToUsdStage", shouldsave)
            await self.finalize_test_no_image()

    async def __test_camera_startup_values(self, viewport_widget):
        # await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)
        # viewport_widget = ViewportWidget(resolution=(TEST_WIDTH, TEST_HEIGHT))

        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()

        stage = usd_context.get_stage()
        self.assertIsNotNone(stage)

        persp = UsdGeom.Camera.Get(stage, "/OmniverseKit_Persp")
        self.assertIsNotNone(persp)
        self.assertAlmostEqual(persp.GetFocalLengthAttr().Get(), 18.147562, places=5)
        self.assertEqual(persp.GetFStopAttr().Get(), 0)

        top = UsdGeom.Camera.Get(stage, "/OmniverseKit_Top")
        self.assertIsNotNone(top)
        self.assertEqual(top.GetHorizontalApertureAttr().Get(), 5000)
        self.assertEqual(top.GetVerticalApertureAttr().Get(), 5000)

        # Test typed-defaults and creation
        settings = carb.settings.get_settings()
        try:
            perps_key = "/persistent/app/primCreation/typedDefaults/camera"
            ortho_key = "/persistent/app/primCreation/typedDefaults/orthoCamera"
            settings.set(perps_key + "/focalLength", 150)
            settings.set(perps_key + "/fStop", 22)
            settings.set(perps_key + "/clippingRange", (200, 2000))
            settings.set(perps_key + "/horizontalAperture", 1234)
            settings.set(ortho_key + "/horizontalAperture", 1000)
            settings.set(ortho_key + "/verticalAperture", 2000)
            settings.set(ortho_key + "/clippingRange", (20000.0, 10000000.0))

            await usd_context.new_stage_async()

            stage = usd_context.get_stage()
            self.assertIsNotNone(stage)

            persp = UsdGeom.Camera.Get(stage, "/OmniverseKit_Persp")
            self.assertIsNotNone(persp)
            self.assertAlmostEqual(persp.GetFocalLengthAttr().Get(), 150)
            self.assertAlmostEqual(persp.GetFStopAttr().Get(), 22)
            self.assertAlmostEqual(persp.GetHorizontalApertureAttr().Get(), 1234)
            self.assertAlmostEqual(persp.GetClippingRangeAttr().Get(), Gf.Vec2f(200, 2000))
            self.assertFalse(persp.GetVerticalApertureAttr().IsAuthored())

            top = UsdGeom.Camera.Get(stage, "/OmniverseKit_Top")
            self.assertIsNotNone(top)
            self.assertAlmostEqual(top.GetHorizontalApertureAttr().Get(), 1000)
            self.assertAlmostEqual(top.GetVerticalApertureAttr().Get(), 2000)
            # Test that the extension.toml default is used
            self.assertAlmostEqual(top.GetClippingRangeAttr().Get(), Gf.Vec2f(20000.0, 10000000.0))

        finally:
            # Reset now for all other tests
            settings.destroy_item(perps_key)
            settings.destroy_item(ortho_key)

            # viewport_widget.destroy()
            # del viewport_widget

    async def __test_display_delegate(self, viewport_widget):
        self.assertIsNotNone(viewport_widget.display_delegate)
        self.assertTrue(isinstance(viewport_widget.display_delegate, ViewportDisplayDelegate))

        def test_set_display_delegate(display_delegate):
            success = False
            try:
                viewport_widget.display_delegate = display_delegate
                success = True
            except RuntimeError:
                pass
            return success

        result = test_set_display_delegate(None)
        self.assertFalse(result)

        result = test_set_display_delegate(32)
        self.assertFalse(result)

        result = test_set_display_delegate(OverlayViewportDisplayDelegate(viewport_widget.viewport_api))
        self.assertTrue(result)

    async def test_ui_driven_resolution(self):
        """Test ViewportWidget driving the underlying Viewport texture resolution"""
        import omni.ui
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        # Need a Window otherwise the ui size calculations won't run
        window_flags = omni.ui.WINDOW_FLAGS_NO_RESIZE | omni.ui.WINDOW_FLAGS_NO_SCROLLBAR | omni.ui.WINDOW_FLAGS_NO_TITLE_BAR
        style = {"border_width": 0}
        window = omni.ui.Window("Test", width=TEST_WIDTH, height=TEST_HEIGHT, flags=window_flags, padding_x=0, padding_y=0)
        startup_resolution = TEST_WIDTH * 0.5, TEST_HEIGHT * 0.25
        with window.frame:
            window.frame.set_style(style)
            viewport_widget = ViewportWidget(resolution=startup_resolution, style=style)

        await self.wait_n_updates(8)
        current_res = viewport_widget.viewport_api.resolution

        self.assertEqual(current_res[0], startup_resolution[0])
        self.assertEqual(current_res[1], startup_resolution[1])

        viewport_widget.fill_frame = True
        await self.wait_n_updates(8)

        # Should match the ui.Frame which should be filling the ui.Window
        current_res = viewport_widget.viewport_api.resolution
        self.assertEqual(current_res[0], window.frame.computed_width)
        self.assertEqual(current_res[1], window.frame.computed_height)

        viewport_widget.fill_frame = False
        viewport_widget.expand_viewport = True
        await self.wait_n_updates(8)
        current_res = viewport_widget.viewport_api.resolution

        # Some-what arbitrary numbers from implementation that are know to be correct for 360, 240 ui.Frame
        self.assertEqual(current_res[0], 180)
        self.assertEqual(current_res[1], 120)

        full_resolution = viewport_widget.full_resolution
        self.assertEqual(full_resolution[0], startup_resolution[0])
        self.assertEqual(full_resolution[1], startup_resolution[1])

        # Test reversion to no fill or exapnd returns back to the resolution explicitly specified.
        viewport_widget.fill_frame = False
        viewport_widget.expand_viewport = False
        await self.wait_n_updates(8)
        current_res = viewport_widget.viewport_api.resolution
        self.assertEqual(current_res[0], startup_resolution[0])
        self.assertEqual(current_res[1], startup_resolution[1])

        # Set render resolution to x3
        viewport_widget.resolution = (TEST_WIDTH * 2.5, TEST_HEIGHT * 2.5)
        viewport_widget.expand_viewport = True
        # Set Window size to x2
        two_x_res = TEST_WIDTH * 2, TEST_HEIGHT * 2
        window.width, window.height = two_x_res
        await self.wait_n_updates(8)

        current_res = viewport_widget.viewport_api.resolution
        self.assertEqual(current_res[0], two_x_res[0])
        self.assertEqual(current_res[1], two_x_res[1])

        viewport_widget.destroy()
        del viewport_widget
        window.destroy()
        del window

        await self.finalize_test_no_image()

    async def __test_engine_creation_arguments(self, hydra_engine_options, verify_engine):
        viewport_widget, window = None, None
        try:
            import omni.ui
            await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

            # Need a Window otherwise the ui size calculations won't run
            window = omni.ui.Window("Test", width=TEST_WIDTH, height=TEST_HEIGHT)
            startup_resolution = TEST_WIDTH * 0.5, TEST_HEIGHT * 0.25
            with window.frame:
                viewport_widget = ViewportWidget(resolution=startup_resolution, width=TEST_WIDTH, height=TEST_HEIGHT,
                                                 hydra_engine_options=hydra_engine_options)

            await self.wait_n_updates(5)
            await verify_engine(viewport_widget.viewport_api._hydra_texture)
        finally:
            if viewport_widget is not None:
                viewport_widget.destroy()
                del viewport_widget
            if window is not None:
                window.destroy()
                del window
            await self.finalize_test_no_image()

    async def test_engine_creation_default_arguments(self):
        """Test default engine creation arguments"""
        hydra_engine_options = {}

        async def verify_engine(hydra_texture):
            settings = carb.settings.get_settings()
            tick_rate = settings.get(f"{hydra_texture.get_settings_path()}hydraTickRate")
            is_async = settings.get(f"{hydra_texture.get_settings_path()}async")
            is_async_ll = settings.get(f"{hydra_texture.get_settings_path()}asyncLowLatency")

            self.assertEqual(is_async, bool(settings.get("/app/asyncRendering")))
            self.assertEqual(is_async_ll, bool(settings.get("/app/asyncRenderingLowLatency")))
            self.assertEqual(tick_rate, int(settings.get("/persistent/app/viewport/defaults/tickRate")))

        await self.__test_engine_creation_arguments(hydra_engine_options, verify_engine)

    async def test_engine_creation_forward_arguments(self):
        """Test forwarding of engine creation arguments"""

        settings = carb.settings.get_settings()

        # Make sure the defaults are in a state that overrides from hydra_engine_options can be tested
        self.assertFalse(bool(settings.get("/app/asyncRendering")))
        self.assertFalse(bool(settings.get("/app/asyncRenderingLowLatency")))
        self.assertNotEqual(30, int(settings.get("/persistent/app/viewport/defaults/tickRate")))

        try:
            hydra_engine_options = {
                "is_async": True,
                "is_async_low_latency": True,
                "hydra_tick_rate": 30

            }

            async def verify_engine(hydra_texture):
                tick_rate = settings.get(f"{hydra_texture.get_settings_path()}hydraTickRate")
                is_async = settings.get(f"{hydra_texture.get_settings_path()}async")
                is_async_ll = settings.get(f"{hydra_texture.get_settings_path()}asyncLowLatency")

                self.assertEqual(is_async, hydra_engine_options.get("is_async"))
                self.assertEqual(is_async_ll, hydra_engine_options.get("is_async_low_latency"))
                self.assertEqual(tick_rate, hydra_engine_options.get("hydra_tick_rate"))

            await self.__test_engine_creation_arguments(hydra_engine_options, verify_engine)
        finally:
            settings.set("/app/asyncRendering", False)
            settings.destroy_item("/app/asyncRenderingLowLatency")
