# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pathlib import Path

from omni.kit.test import AsyncTestCase
import omni.usd
from pxr import Usd, Plug, Gf
import carb


TEST_DATA_DIR = Path(
    carb.tokens.get_tokens_interface().resolve("${omni.usd.schema.omni_lens_distortion}")
).joinpath("data").resolve()


USD_DATA_DIR = TEST_DATA_DIR.joinpath("usd")


class SensorSchemaTest(AsyncTestCase):
    async def setUp(self):
        super().setUp()

    async def tearDown(self):
        super().tearDown()

    @property
    def lens_api_schemas(self):
        yield from (
            "OmniLensDistortionFthetaAPI", 
            "OmniLensDistortionKannalaBrandtK3API", 
            "OmniLensDistortionRadTanThinPrismAPI", 
            "OmniLensDistortionLutAPI",
            "OmniLensDistortionOpenCvFisheyeAPI",
            "OmniLensDistortionOpenCvPinholeAPI"
        )

    async def test_plugin_loaded(self):
        """Test the plugin was loaded in Usd"""
        self.assertTrue(
            Plug.Registry().GetPluginWithName("omniLensDistortion") is not None
        )

    async def test_schemas_registered(self):
        """Test sensor schemas were registered"""
        schema_registry = Usd.SchemaRegistry()

        for api_schema in self.lens_api_schemas:
            tf_type = schema_registry.GetAPITypeFromSchemaTypeName(api_schema)
            self.assertFalse(tf_type.isUnknown)

    async def test_schemas_values_loaded(self):
        """Test opening a stage with sensor prims and proper values (default and authored)"""

        usd_context = omni.usd.get_context()
        await usd_context.open_stage_async(
            str(USD_DATA_DIR.joinpath("OmniLensDistortionTest.usda"))
        )

        # Check that we get correct default/overloaded values from the loaded layer
        stage = usd_context.get_stage()

        cam1 = stage.GetPrimAtPath("/World/Camera1")
        self.assertTrue(cam1.IsValid())

        cam2 = stage.GetPrimAtPath("/World/Camera2")
        self.assertTrue(cam2.IsValid())

        cam3 = stage.GetPrimAtPath("/World/Camera3")
        self.assertTrue(cam3.IsValid())

        cam4 = stage.GetPrimAtPath("/World/Camera4")
        self.assertTrue(cam4.IsValid())

        cam5 = stage.GetPrimAtPath("/World/Camera5")
        self.assertTrue(cam5.IsValid())

        cam6 = stage.GetPrimAtPath("/World/Camera6")
        self.assertTrue(cam6.IsValid())

        t_poly, t_kb, t_thin, t_lut, t_cv, t_cvp = self.lens_api_schemas

        self.assertTrue(cam1.HasAPI(t_poly))
        self.assertTrue(cam2.HasAPI(t_kb))
        self.assertTrue(cam3.HasAPI(t_thin))
        self.assertTrue(cam4.HasAPI(t_lut))
        self.assertTrue(cam5.HasAPI(t_cv))
        self.assertTrue(cam6.HasAPI(t_cvp))

        attr = cam1.GetAttribute("omni:lensdistortion:ftheta:maxFov")
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get(), 200.0)

        attr = cam2.GetAttribute("omni:lensdistortion:kannalaBrandtK3:maxFov")
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get(), 120.0)

        attr = cam3.GetAttribute("omni:lensdistortion:radTanThinPrism:s2")
        self.assertTrue(attr.IsValid())
        self.assertTrue(Gf.IsClose(attr.Get(), 0.00019, 1.0e-6))

        attr = cam4.GetAttribute("omni:lensdistortion:lut:rayEnterDirectionTexture")
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get().path, "dir.exr")

        attr = cam4.GetAttribute("omni:lensdistortion:lut:rayExitPositionTexture")
        self.assertTrue(attr.IsValid())
        self.assertEqual(attr.Get().path, "pos.exr")

        attr = cam5.GetAttribute("omni:lensdistortion:opencvFisheye:fx")
        self.assertTrue(attr.IsValid())
        self.assertTrue(Gf.IsClose(attr.Get(), 800, 1.0e-6))

        attr = cam5.GetAttribute("omni:lensdistortion:opencvFisheye:fy")
        self.assertTrue(attr.IsValid())
        self.assertTrue(Gf.IsClose(attr.Get(), 700, 1.0e-6))

        attr = cam6.GetAttribute("omni:lensdistortion:opencvPinhole:k1")
        self.assertTrue(attr.IsValid())
        self.assertTrue(Gf.IsClose(attr.Get(), 1.5, 1.0e-6))

        # Check we can apply the API and get the default value
        cam1.ApplyAPI(t_thin)
        self.assertTrue(cam1.HasAPI(t_thin))
        attr = cam1.GetAttribute("omni:lensdistortion:radTanThinPrism:s2")
        self.assertTrue(attr.IsValid())
        self.assertTrue(Gf.IsClose(attr.Get(), 0.00019, 1.0e-6))
