# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from omni.kit.test import AsyncTestCase
import omni.usd
import carb
from pxr import Gf, Usd, UsdRender
import os


class RtxUsdRenderSettingsTest(AsyncTestCase):
    async def setUp(self):
        self.__settings = carb.settings.get_settings()
        self.__usd_context_name = ''
        self.__usd_context = omni.usd.get_context(self.__usd_context_name)
        await self.__usd_context.new_stage_async()
        self.__is_usdrt_test = bool(self.__settings.get("/app/useFabricSceneDelegate"))

    async def tearDown(self):
        super().tearDown()

    def assertEqual(self, a, b, epsilon = 1.0e-5, *args, **kwargs):
        self.assertTrue(Gf.IsClose(a, b, epsilon), *args, **kwargs)

    def __get_stage_for_inspection(self, stage: Usd.Stage):
        if not self.__is_usdrt_test:
            return stage

        try:
            from pxr import UsdUtils
            import usdrt.Usd as UsdRtUsd

            stage_id = UsdUtils.StageCache.Get().GetId(stage).ToLongInt()
            fabric_active_for_stage = UsdRtUsd.Stage.StageWithHistoryExists(stage_id)
            if fabric_active_for_stage:
                return UsdRtUsd.Stage.Attach(stage_id)
        except ModuleNotFoundError:
            pass

        carb.log_warn(f"usdrt.Usd.Stage unavailable for {stage}")
        return None


    async def test_schema_loadable(self):
        """Test that the usd schema is accessible and loadable as a pxr.Usd.Stage"""
        # Validate the token-resolution to load generatedSchema.usda functions
        #
        schema_path = carb.tokens.get_tokens_interface().resolve("${omni.usd.schema.render_settings.rtx}")
        self.assertTrue(bool(schema_path))

        schema_path = os.path.join(schema_path, "usd_plugins", "generatedSchema.usda")
        self.assertTrue(os.path.isfile(schema_path))

        # Validate the stage and that it has children
        #
        usd_stage = Usd.Stage.Open(schema_path)
        self.assertTrue(bool(usd_stage))

        stage = usd_stage # self.__get_stage_for_inspection(usd_stage)
        self.assertTrue(bool(stage))

        root_prim = stage.GetPrimAtPath("/")
        self.assertTrue(bool(root_prim) and root_prim.IsValid())
        self.assertTrue(len(root_prim.GetAllChildren()) > 0)

        # Validate that any schema in the "auto apply list" exists as a prim in the schema's usd file
        #
        auto_applied_schemas = self.__settings.get("/exts/omni.usd.schema.render_settings.rtx/renderProduct/apiSchemas/autoApply")
        for schema_name in auto_applied_schemas:
            schema_prim = stage.GetPrimAtPath(f"/{schema_name}")
            self.assertTrue(bool(schema_prim) and schema_prim.IsValid())


    async def __test_usd_file_open(self, usd_file_path: str, vp_0_settings: dict, vp_1_settings: dict):
            await self.__usd_context.open_stage_async(usd_file_path)
            await self.wait_n_updates()

            usd_stage = self.__usd_context.get_stage()
            self.assertTrue(bool(usd_stage))

            stage = self.__get_stage_for_inspection(usd_stage)
            self.assertTrue(bool(stage))

            if self.__is_usdrt_test:
                import usdrt.Usd as UsdRtUsd
                instance_type = UsdRtUsd.Prim
                attr_type = UsdRtUsd.Attribute
            else:
                instance_type = Usd.Prim
                attr_type = Usd.Attribute

            rp_0 = stage.GetPrimAtPath("/Render/OmniverseKit/HydraTextures/omni_kit_widget_viewport_ViewportTexture_0")
            self.assertTrue(bool(rp_0) and rp_0.IsValid())

            rp_1 = stage.GetPrimAtPath("/Render/OmniverseKit/HydraTextures/omni_kit_widget_viewport_ViewportTexture_1")
            self.assertTrue(bool(rp_1) and rp_1.IsValid())

            def validate_usd_settings():
                for rp, attrs in zip((rp_0, rp_1), (vp_0_settings, vp_1_settings)):
                    for k, v in attrs.items():
                        usd_attr = rp.GetAttribute(k)

                        # Validate the values are expected
                        self.assertTrue(bool(usd_attr) and usd_attr.IsValid(), msg=f"Usd.Attribute {k} was not found")
                        self.assertEqual(usd_attr.Get(), v, msg=f"Usd.Attribute {k} did not have the same value {v}")

                        # Validate the types are expected
                        self.assertTrue(isinstance(rp, instance_type))
                        self.assertTrue(isinstance(usd_attr, attr_type))

            # Validate settings on open are restored as expected
            #
            validate_usd_settings()

            # Edit the global-carb-settings equivalent
            #
            self.__settings.set("/rtx/post/tvNoise/enableScanlines", False)
            self.__settings.set("/rtx/post/tvNoise/scanlineSpread", 11.12)
            self.__settings.set("/rtx/post/tvNoise/grainAmount", 1.23)
            await self.wait_n_updates()

            # Validate the global-carb-settings have been applied to both UsdRender.Products
            #
            for settings in (vp_0_settings, vp_1_settings):
                settings["omni:rtx:post:tvNoise:scanlines:enabled"] = 0
                settings["omni:rtx:post:tvNoise:scanlines:spread"] = 11.12
                settings["omni:rtx:post:tvNoise:filmGrain:amount"] = 1.23

            validate_usd_settings()

    async def test_schemas_applied(self):
        """Test opening usd files and how settings are loaded / applied based on serialization and legacy metadata"""
        usd_files = os.path.join(carb.tokens.get_tokens_interface().resolve("${omni.usd.schema.render_settings.rtx}"),
                                 "data", "tests", "usd")

        from omni.kit.viewport.window import ViewportWindow
        viewport_windows = [ViewportWindow("a"), ViewportWindow("b")]
        try:
            carb_settings = {
                "omni:rtx:post:tvNoise:enabled": 1,
                "omni:rtx:post:tvNoise:scanlines:enabled": 1,
                "omni:rtx:post:tvNoise:scanlines:spread": 0.1234567,
            }
            await self.__test_usd_file_open(os.path.join(usd_files, "carb-settings-tv-noise.usda"), carb_settings, carb_settings)

            carb_settings = {
                "omni:rtx:post:tvNoise:enabled": 1,
                "omni:rtx:post:tvNoise:scanlines:enabled": 1,
                "omni:rtx:post:tvNoise:scanlines:spread": 0.1234567,
                "omni:rtx:post:tvNoise:filmGrain:amount": 0.06,
            }

            vp_0 = carb_settings.copy()
            vp_0["omni:rtx:post:tvNoise:filmGrain:amount"] = 5
            vp_0["omni:rtx:post:tvNoise:scanlines:enabled"] = 0

            vp_1 = carb_settings.copy()
            vp_1["omni:rtx:post:tvNoise:scanlines:spread"] = 3

            await self.__test_usd_file_open(os.path.join(usd_files, "two-viewports.usda"), vp_0, vp_1)
        finally:
            for vp_window in viewport_windows:
                vp_window.destroy()
            viewport_windows = None

    async def __test_dlss_render_settings(self, exec_mode: int, per_prod: bool, settings):
        # Set the global execMode
        settings.set("/rtx/post/dlss/execMode", exec_mode)
        # Set a unique staticRatio
        settings.set("/rtx/post/dlss/manualScaling", 1.0 - (exec_mode/10.0))

        await self.wait_n_updates()

        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        viewport_api = omni.kit.viewport.utility.get_active_viewport()

        usd_stage = usd_context.get_stage()
        self.assertTrue(bool(usd_stage))

        stage = self.__get_stage_for_inspection(usd_stage)
        self.assertTrue(bool(stage))

        rndr_prod_prim = stage.GetPrimAtPath(viewport_api.render_product_path)
        self.assertTrue(bool(rndr_prod_prim))

        if self.__is_usdrt_test:
            from usdrt import UsdRender as UsdRtRender
            self.assertTrue(rndr_prod_prim.IsA(UsdRtRender.Product))
        else:
            self.assertTrue(rndr_prod_prim.IsA(UsdRender.Product))

        settings_to_attr = {
            "/rtx/post/dlss/manualScaling": "omni:rtx:post:dlss:manualScaling",
            "/rtx/post/dlss/execMode": "omni:rtx:post:dlss:execMode",
        }
        # self.assertTrue(False)

    async def test_dlss_render_settings(self):
        """Test DLSS render settings that exist on UsdRender.Product"""
        settings = carb.settings.get_settings()

        for exec_mode in range(5):
            await self.__test_dlss_render_settings(exec_mode, True, settings)
