import pathlib
import asyncio

import carb
import carb.settings
import carb.tokens

import omni.kit.app
import omni.kit.test

from omni.kit.hydra_texture import create_hydra_texture
import omni.usd
from typing import Callable

from pxr import Gf, UsdRender

EXTENSION_FOLDER_PATH = pathlib.Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
DATA_DIR = EXTENSION_FOLDER_PATH.joinpath("data/tests")


class HydraTextureTest(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._settings = carb.settings.acquire_settings_interface()

        self._usd_context_name = ''
        self._usd_context = omni.usd.get_context(self._usd_context_name)

        # Attach the HydraEngine that the test has setup to run (if not already attached)
        # hd_engine_name = self._settings.get("/renderer/active") or "pxr"
        # if hd_engine_name not in self._usd_context.get_attached_hydra_engine_names():
        #     omni.usd.create_hydra_engine(hd_engine_name, self._usd_context)

        await self._usd_context.new_stage_async()

    async def tearDown(self):
        self._settings = None
        await self.wait_n_updates(6)

    async def wait_n_updates(self, n_frames: int = 3):
        app = omni.kit.app.get_app()
        for i in range(n_frames):
            await app.next_update_async()

    async def _open_test_file(self, test_usd_asset: str):
        test_usd_asset = DATA_DIR.joinpath(test_usd_asset)
        # print("Opening '%s'" % (test_usd_asset))
        return await self._usd_context.open_stage_async(str(test_usd_asset))

    async def _create_hydra_texture_test(self, filename: str, texture_test: Callable,
                                         renderer: str = 'pxr', res_x: int = 320, res_y: int = 320,
                                         engine_options: dict | None = None,
                                         tx_name: str | None = None,
                                         cam_path: str | None = None):
        wait_iterations = 6
        try:
            if renderer not in self._usd_context.get_attached_hydra_engine_names():
                omni.usd.create_hydra_engine(renderer, self._usd_context)

            if filename:
                await self._open_test_file(filename)

            if engine_options is None:
                engine_options = {"is_async": False}

            hydra_texture = create_hydra_texture(
                tx_name or "test_viewport",
                res_x,
                res_y,
                self._usd_context_name,
                cam_path if cam_path else "/test_cam",
                renderer,
                **engine_options
            )

            return await texture_test(hydra_texture)
        finally:
            await self.wait_n_updates(6)

    # test1 - test1g simulate possible failure on low memory Linux configs from
    # bad gpu-foundation shutdown and startup.
    async def test_1_simple_context_attach(self):
        """Test HydraTexture open/close across multiple tests 01"""
        async def no_more_test(hydra_texture):
            pass
        await self._create_hydra_texture_test('simple_cubes_mat.usda', no_more_test)

    async def test_1b_simple_context_attach(self):
        """Test HydraTexture open/close across multiple tests 02"""
        async def no_more_test(hydra_texture):
            pass
        await self._create_hydra_texture_test('simple_cubes_mat.usda', no_more_test)

    async def test_1c_simple_context_attach(self):
        """Test HydraTexture open/close across multiple tests 03"""
        async def no_more_test(hydra_texture):
            pass
        await self._create_hydra_texture_test('simple_cubes_mat.usda', no_more_test)

    async def test_1d_simple_context_attach(self):
        """Test HydraTexture open/close across multiple tests 04"""
        async def no_more_test(hydra_texture):
            pass
        await self._create_hydra_texture_test('simple_cubes_mat.usda', no_more_test)

    async def test_1e_simple_context_attach(self):
        """Test HydraTexture open/close across multiple tests 05"""
        async def no_more_test(hydra_texture):
            pass
        await self._create_hydra_texture_test('simple_cubes_mat.usda', no_more_test)

    async def test_1f_simple_context_attach(self):
        """Test HydraTexture open/close across multiple tests 06"""
        async def no_more_test(hydra_texture):
            pass
        await self._create_hydra_texture_test('simple_cubes_mat.usda', no_more_test)

    async def test_1g_simple_context_attach(self):
        """Test HydraTexture open/close across multiple tests 07"""
        async def no_more_test(hydra_texture):
            pass
        await self._create_hydra_texture_test('simple_cubes_mat.usda', no_more_test)

    async def test_2_drawable_changed(self):
        """Test HydraTexture emits an event of EVENT_TYPE_DRAWABLE_CHANGED"""
        drawable_result = asyncio.Future()
        async def drawable_changed_test(hydra_texture):
            def on_drawable_changed(event: carb.events.IEvent):
                if event.type != omni.hydratexture.EVENT_TYPE_DRAWABLE_CHANGED:
                    carb.log_error("Wrong event captured for DRAWABLE_CHANGED!")
                    return

                result_handle = event.payload['result_handle']
                aov_info = hydra_texture.get_aov_info(result_handle)
                self.assertEqual(aov_info[0]['name'], 'LdrColor')

                ldr_info = hydra_texture.get_aov_info(result_handle, 'LdrColor')
                self.assertEqual(ldr_info[0]['name'], 'LdrColor')

                ldr_info = hydra_texture.get_aov_info(result_handle, 'LdrColor', include_texture=True)
                self.assertEqual(ldr_info[0]['name'], 'LdrColor')
                ldr_tex = ldr_info[0]['texture']
                self.assertEqual(ldr_tex['resolution'][0], 640)
                self.assertEqual(ldr_tex['resolution'][1], 320)
                self.assertIsNotNone(ldr_tex.get('rp_resource'))

                # Avoid any dependency on another extension for TextureFormat.RGBA8_UNORM
                # Test the valus is not None, and use introspection about pybind enum type
                # generation to test the value is correct.
                tex_format = ldr_tex.get('format')
                self.assertIsNotNone(tex_format)
                self.assertEqual(tex_format, tex_format.RGBA8_UNORM)

                frame_info = hydra_texture.get_frame_info(result_handle)
                self.assertIsNotNone(frame_info['view'])
                self.assertIsNotNone(frame_info['projection'])
                self.assertIsNotNone(frame_info['fps'])
                self.assertIsNotNone(frame_info['resolution'])
                self.assertIsNotNone(frame_info['progression'])
                self.assertIsNotNone(frame_info['frame_number'])
                self.assertIsNotNone(frame_info['device_mask'])

                # metadata key should always be available (but may be None)
                try:
                    frame_info.get("metadata")
                except Exception as e:
                    self.assertTrue(False)

                nonlocal drawable_result
                # EVENT_TYPE_DRAWABLE_CHANGED can be called multiple times before yielding for async loop
                if not drawable_result.done():
                    drawable_result.set_result(True)

            return hydra_texture.get_event_stream().create_subscription_to_push_by_type(
                omni.hydratexture.EVENT_TYPE_DRAWABLE_CHANGED,
                on_drawable_changed,
                name="Viewport Texture drawable change",
            )

        drawable_change_sub = await self._create_hydra_texture_test('simple_cubes_mat.usda', drawable_changed_test,
                                                                    res_x = 640, res_y = 320)
        result = await drawable_result
        drawable_change_sub = None
        self.assertTrue(result)

    async def __test_custom_product(self, settings):
        # Build up the custom RenderProduct
        custom_prod_path = '/Render/renderproduct_custom'
        custom_var_path = '/Render/rendervar_custom'
        custom_cam_path = '/test_cam_custom'
        custom_resolution = Gf.Vec2i(512, 512)

        # XXX: This used to be handled entirely by set_render_product_path and usd-abi
        # But usd-abi now validates portions of the RenderProduct.
        # So just set up the complete UsdRender.Product and UsdRender.Var and validate it ourselves along the way.
        async def setup_custom_product(stage):
            custom_prod = UsdRender.Product.Define(stage, custom_prod_path)
            self.assertIsNotNone(custom_prod)

            custom_var = UsdRender.Var.Define(stage, custom_var_path)
            self.assertIsNotNone(custom_var)

            ordered_vars = custom_prod.GetOrderedVarsRel()
            self.assertIsNotNone(ordered_vars)
            ordered_vars.SetTargets([custom_var_path])
            self.assertEqual([sdf_path.pathString for sdf_path in ordered_vars.GetForwardedTargets()], [custom_var_path])

            camera_rel = custom_prod.GetCameraRel()
            self.assertIsNotNone(camera_rel)
            camera_rel.SetTargets([custom_cam_path])
            self.assertEqual([sdf_path.pathString for sdf_path in camera_rel.GetForwardedTargets()], [custom_cam_path])

            res_attr = custom_prod.GetResolutionAttr()
            self.assertIsNotNone(res_attr)
            res_attr.Set(custom_resolution)

            source_name = custom_var.GetSourceNameAttr()
            self.assertIsNotNone(source_name)
            source_name.Set('LdrColor')

            # Wait one frame to make sure Usd edits are absorbed
            return await self.wait_n_updates(1)

        async def product_test(hydra_texture):
            dflt_path = hydra_texture.get_render_product_path()

            # Compare the default path against a few possiblities (based on settings)
            if settings.get("/exts/omni.kit.hydra_texture/renderProduct/path/useForTextureName"):
                # Name and RenderProduct path should match
                self.assertEqual(dflt_path, hydra_texture.get_render_product_path())
            elif settings.get("/exts/omni.kit.hydra_texture/renderProduct/path/filtering"):
                # implicit RenderProduct path should reduce to constant value including name
                self.assertEqual(dflt_path, "/Render/OmniverseKit/HydraTextures/scoped_name")
            else:
                # Wild west, implicit RenderProduct path should be prefix + texture-name
                self.assertEqual(dflt_path, f"/Render/OmniverseKit/CustomHydraTextures/{hydra_texture.get_name()}".replace("//", "/"))

            stage = self._usd_context.get_stage()
            rp_prim = stage.GetPrimAtPath(dflt_path)
            self.assertIsNotNone(rp_prim)
            self.assertTrue(rp_prim.IsValid())
            self.assertTrue(rp_prim.IsA(UsdRender.Product))

            await setup_custom_product(stage)
            stage, rp_prim = None, None

            # Move the product to a custom one keeping width, height, and camera
            success = hydra_texture.set_render_product_path(custom_prod_path, keep_camera=True, keep_resolution=True)
            cstm_path = hydra_texture.get_render_product_path()

            self.assertTrue(success)
            self.assertNotEqual(dflt_path, cstm_path)

            self.assertEqual(hydra_texture.get_camera_path(), '/test_cam')
            self.assertEqual(hydra_texture.get_width(), 320)
            self.assertEqual(hydra_texture.get_height(), 320)

            # Move the product to a custom one, reading width, height, and camera
            success = hydra_texture.set_render_product_path(custom_prod_path)
            cstm_path = hydra_texture.get_render_product_path()
            self.assertTrue(success)
            self.assertNotEqual(dflt_path, cstm_path)

            # XXX: Can't test this here, needs to process the Viewport
            # self.assertEqual(hydra_texture.get_camera_path(), custom_cam_path)
            self.assertEqual(hydra_texture.get_width(), custom_resolution[0])
            self.assertEqual(hydra_texture.get_height(), custom_resolution[1])

            # Move it back to the default
            success = hydra_texture.set_render_product_path(dflt_path)
            self.assertTrue(success)
            self.assertEqual(dflt_path, hydra_texture.get_render_product_path())

            # Move it to an RenderProduct that exists in the on-disk stage
            on_disk_product_path = "/Render/renderproduct1"
            hydra_texture.set_render_product_path(on_disk_product_path)
            self.assertEqual(on_disk_product_path, hydra_texture.get_render_product_path())

            # Test that RenderProduct preservation[on] for close/open works
            #
            settings.set("/exts/omni.kit.hydra_texture/stage/load/preserve/renderProduct", True)
            settings.set("/exts/omni.kit.hydra_texture/stage/load/preserve/resolution", False)
            settings.set("/exts/omni.kit.hydra_texture/stage/load/preserve/camera", False)
            await self._usd_context.close_stage_async()
            await self._open_test_file("custom_product.usda")

            reopened_path = hydra_texture.get_render_product_path()
            self.assertEqual(reopened_path, on_disk_product_path)
            self.assertNotEqual(reopened_path, cstm_path)
            self.assertNotEqual(reopened_path, dflt_path)

            # Should ignore any local overides in favor of twhat the RenderProduct specifies
            self.assertEqual(hydra_texture.get_width(), 240)
            self.assertEqual(hydra_texture.get_height(), 180)
            self.assertEqual(hydra_texture.get_camera_path(), '/test_cam_2')

            # Set some overides on the HydraTexture to test preservation next
            hydra_texture.set_width(320), hydra_texture.set_height(320)
            hydra_texture.set_camera_path("/test_cam")
            self.assertEqual(hydra_texture.get_width(), 320)
            self.assertEqual(hydra_texture.get_height(), 320)
            await self.wait_n_updates()

            # Test that RenderProduct preservation[off] for close/open works
            #
            settings.set("/exts/omni.kit.hydra_texture/stage/load/preserve/renderProduct", False)
            settings.set("/exts/omni.kit.hydra_texture/stage/load/preserve/resolution", True)
            settings.set("/exts/omni.kit.hydra_texture/stage/load/preserve/camera", True)
            await self._usd_context.close_stage_async()
            await self._open_test_file("custom_product.usda")

            reopened_path = hydra_texture.get_render_product_path()
            self.assertEqual(reopened_path, dflt_path)
            self.assertNotEqual(reopened_path, cstm_path)
            self.assertNotEqual(reopened_path, on_disk_product_path)

            self.assertEqual(hydra_texture.get_width(), 320)
            self.assertEqual(hydra_texture.get_height(), 320)
            self.assertEqual(hydra_texture.get_camera_path(), '/test_cam')

        settings.set("/exts/omni.kit.hydra_texture/renderProduct/path/useForTextureName", True)
        await self._create_hydra_texture_test("custom_product.usda", product_test, tx_name="scoped_name")
        await self._create_hydra_texture_test("custom_product.usda", product_test, tx_name="/Render/OmniverseKit/HydraTextures/scoped_name")
        await self._create_hydra_texture_test("custom_product.usda", product_test, tx_name="/Render/scoped_name")

        settings.set("/exts/omni.kit.hydra_texture/renderProduct/path/useForTextureName", False)
        await self._create_hydra_texture_test("custom_product.usda", product_test, tx_name="scoped_name")
        await self._create_hydra_texture_test("custom_product.usda", product_test, tx_name="/Render/OmniverseKit/HydraTextures/scoped_name")
        await self._create_hydra_texture_test("custom_product.usda", product_test, tx_name="/Render/scoped_name")

        settings.set("/exts/omni.kit.hydra_texture/renderProduct/path/filtering", False)
        settings.set("/exts/omni.kit.hydra_texture/renderProduct/path/prefix", "OmniverseKit/CustomHydraTextures/")
        await self._create_hydra_texture_test("custom_product.usda", product_test, tx_name="scoped_name")
        await self._create_hydra_texture_test("custom_product.usda", product_test, tx_name="/Render/OmniverseKit/HydraTextures/scoped_name")
        await self._create_hydra_texture_test("custom_product.usda", product_test, tx_name="/Render/scoped_name")

    async def test_3_custom_product(self):
        """Test assignment and query of a custom RenderProduce on the HydraTexture"""

        # Store initial settings for restoration on exit
        settings = carb.settings.get_settings()
        initial_values = {}
        for key in ["stage/load/preserve/renderProduct", "stage/load/preserve/resolution", "stage/load/preserve/camera",
                    "renderProduct/path/prefix", "renderProduct/path/filtering", "renderProduct/path/useForTextureName"]:
            key = f"/exts/omni.kit.hydra_texture/renderProduct/path/{key}"
            initial_values[key] = settings.get(key)

        try:
            await self.__test_custom_product(settings)
        finally:
            for k, v in initial_values.items():
                settings.set(k, v)

        # Test assignment of a custom product
        async def nested_product_test(hydra_texture):
            self.assertEqual( hydra_texture.get_render_product_path(),
                "/Render/OmniverseKit/CustomHydraTextures/nested_prod_test")

            nested_prod_path = "/World/nova_carter_sensors_stripped/Render/BackHawkLeftCameraRp"
            nested_cam_path = "/World/nova_carter_sensors_stripped/Nova_Carter_ROS/chassis_link/back_hawk/left/camera_left"
            hydra_texture.set_render_product_path(nested_prod_path)

            await self.wait_n_updates()
            self.assertEqual(hydra_texture.get_render_product_path(), nested_prod_path)
            self.assertEqual(hydra_texture.get_camera_path(), nested_cam_path)

            hydra_texture.set_render_product_path("/Does/not/exist")
            await self.wait_n_updates()
            self.assertEqual(hydra_texture.get_render_product_path(), nested_prod_path)


        await self._create_hydra_texture_test("payload/stage.usda", nested_product_test, tx_name="nested_prod_test")

    async def test_tick_rate_creation(self):
        """Test arguments passed to create_hydra_texture"""
        engine_options = {
            "is_async": False,
            "hydra_tick_rate": 30
        }
        async def check_engine_tick_rate(hydra_texture):
            settings = carb.settings.get_settings()
            tick_rate = settings.get(f"{hydra_texture.get_settings_path()}hydraTickRate")
            is_async = settings.get(f"{hydra_texture.get_settings_path()}async")

            self.assertEqual(tick_rate, engine_options.get("hydra_tick_rate"))
            self.assertEqual(is_async, engine_options.get("is_async"))

        await self._create_hydra_texture_test('simple_cubes_mat.usda', check_engine_tick_rate, engine_options=engine_options)

    async def test_async_engine_creation(self):
        """Test arguments passed to create_hydra_texture"""
        engine_options = {
            "is_async": True,
        }
        async def check_engine_async(hydra_texture):
            settings = carb.settings.get_settings()
            is_async = settings.get(f"{hydra_texture.get_settings_path()}async")
            self.assertEqual(is_async, engine_options.get("is_async"))

        await self._create_hydra_texture_test('simple_cubes_mat.usda', check_engine_async, engine_options=engine_options)


    async def test_reopen_camera_path(self):
        """Test opening a stage doesn't keep/add any previous camera paths"""
        settings = carb.settings.get_settings()
        async_rendering = settings.get("/app/asyncRendering")

        async def loop_opens_test(hydra_texture):
            scenes_and_cameras = ["camera_0", "camera_1"]
            for i in range(10):
                index = 1 if (i % 2 == 0) else 0
                camera = scenes_and_cameras[index]

                real_cam_path = f"/World/{camera}"
                gone_cam_path = f"/World/{scenes_and_cameras[not index]}"
                if i == 0:
                    hydra_texture.camera_path = real_cam_path

                await self._open_test_file(f"{camera}.usda")
                await self.wait_n_updates(6)

                stage = self._usd_context.get_stage()
                self.assertTrue(stage.GetPrimAtPath(real_cam_path).IsValid(), f"{real_cam_path} should exist in {camera}.usda")
                self.assertFalse(stage.GetPrimAtPath(gone_cam_path).IsValid(), f"{gone_cam_path} should not exist in {camera}.usda")

        try:
            settings.set("/app/asyncRendering", True)
            await self._create_hydra_texture_test(None, loop_opens_test)
        finally:
            settings.set("/app/asyncRendering", async_rendering)

    # There isn't a great mechanism for having a test fail mean success; which whould allow
    # these two tests that a failure wont result in a crash.
    # Until then, hopefully these can be run on new test additions or manually.
    #
    # async def test_0_disabled_test_failure_wont_crash(self):
    #     self.assertTrue(False)
    # async def test_z_disabled_test_failure_wont_crash(self):
    #     self.assertTrue(False)
