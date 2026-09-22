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
from pxr import Usd, UsdRender, Plug
import carb


TEST_DATA_DIR = Path(
    carb.tokens.get_tokens_interface().resolve("${omni.usd.schema.omni_sensors}")
).joinpath("data").resolve()

USD_DATA_DIR = TEST_DATA_DIR.joinpath("usd")


class SensorSchemaTest(AsyncTestCase):
    async def setUp(self):
        super().setUp()

    async def tearDown(self):
        super().tearDown()

    async def test_plugin_loaded(self):
        """Test the plugin was loaded in Usd"""
        self.assertTrue(Plug.Registry().GetPluginWithName("omniSensor") is not None)

    async def test_schemas_registered(self):
        """Test sensor schemas were registered"""
        schema_registry = Usd.SchemaRegistry()

        prim_schemas_to_test = ("OmniSensor", "OmniRadar", "OmniLidar")
        for prim_schema in prim_schemas_to_test:
            tf_type = schema_registry.GetTypeFromSchemaTypeName(prim_schema)
            self.assertFalse(tf_type.isUnknown)

        api_schemas_to_test = ("OmniSensorAPI", "OmniSensorEncryptionAPI", "OmniSensorGenericLidarCoreAPI")
        for api_schema in api_schemas_to_test:
            tf_type = schema_registry.GetAPITypeFromSchemaTypeName(api_schema)
            self.assertFalse(tf_type.isUnknown)

    async def test_schemas_values_loaded(self):
        """Test opening a stage with sensor prims and proper values (default and authored)"""

        usd_context = omni.usd.get_context()
        await usd_context.open_stage_async(str(USD_DATA_DIR.joinpath("OmniSensorsTest.usda")))

        stage = usd_context.get_stage()

        d_prim = stage.GetPrimAtPath("/World/DasLidar")
        self.assertTrue(d_prim.IsValid())

        e_prim = stage.GetPrimAtPath("/World/ElRadar")
        self.assertTrue(e_prim.IsValid())

        d_tickrate = d_prim.GetAttribute("omni:sensor:tickRate")
        self.assertTrue(d_tickrate.IsValid())

        e_tickrate = e_prim.GetAttribute("omni:sensor:tickRate")
        self.assertTrue(e_tickrate.IsValid())

        self.assertEqual(10, d_tickrate.Get())
        self.assertEqual(2, e_tickrate.Get())


        drp_prim = stage.GetPrimAtPath("/Render/OmniSensorsLidar")
        self.assertTrue(drp_prim.IsValid())
        drp_prim = UsdRender.Product(drp_prim)
        self.assertTrue(bool(drp_prim))


        erp_prim = stage.GetPrimAtPath("/Render/OmniSensorsRadar")
        self.assertTrue(erp_prim.IsValid())
        erp_prim = UsdRender.Product(erp_prim)
        self.assertTrue(bool(erp_prim))

        drp_cam_rel = drp_prim.GetCameraRel().GetForwardedTargets()
        self.assertEqual(1, len(drp_cam_rel))

        erp_cam_rel = erp_prim.GetCameraRel().GetForwardedTargets()
        self.assertEqual(1, len(erp_cam_rel))

        self.assertTrue(stage.GetPrimAtPath(drp_cam_rel[0]), d_prim)
        self.assertTrue(stage.GetPrimAtPath(erp_cam_rel[0]), e_prim)
