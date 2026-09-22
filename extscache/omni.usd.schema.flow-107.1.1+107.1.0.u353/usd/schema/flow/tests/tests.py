# Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pathlib import Path

import omni.kit.test
from pxr import Plug, Tf, Usd

CURRENT_PATH = Path(__file__).parent.parent.parent.parent.parent
SCHEMA_RESOURCES_DIR = CURRENT_PATH.joinpath("schema").joinpath("resources")
SCHEMA_PATH = SCHEMA_RESOURCES_DIR.joinpath("schema.usda")
GENERATED_SCHEMA_PATH = SCHEMA_RESOURCES_DIR.joinpath("generatedSchema.usda")


class FlowSchemaTests(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_flow_types(self):
        reg = Usd.SchemaRegistry()

        flow_schema_plugin = Plug.Registry().GetPluginWithName("flowSchema")
        self.assertTrue(flow_schema_plugin is not None)

        expected_schema_types = [
            "FlowSchemaFlowAdvectionChannelParams",
            "FlowSchemaFlowAdvectionCombustionParams",
            "FlowSchemaFlowDebugVolumeParams",
            "FlowSchemaFlowEmitterBox",
            "FlowSchemaFlowEmitterMesh",
            "FlowSchemaFlowEmitterNanoVdb",
            "FlowSchemaFlowEmitterPoint",
            "FlowSchemaFlowEmitterSphere",
            "FlowSchemaFlowEmitterTexture",
            "FlowSchemaFlowOffscreen",
            "FlowSchemaFlowPressureParams",
            "FlowSchemaFlowRayMarchCloudParams",
            "FlowSchemaFlowRayMarchColormapParams",
            "FlowSchemaFlowRayMarchParams",
            "FlowSchemaFlowRender",
            "FlowSchemaFlowShadowParams",
            "FlowSchemaFlowSimulate",
            "FlowSchemaFlowSparseNanoVdbExportParams",
            "FlowSchemaFlowSummaryAllocateParams",
            "FlowSchemaFlowVorticityParams",
        ]

        for prim_type in expected_schema_types:

            ret_val = flow_schema_plugin.DeclaresType(Tf.Type(prim_type))
            self.assertTrue(ret_val)

            type_name = reg.GetConcreteSchemaTypeName(Tf.Type(prim_type))
            self.assertTrue(type_name)

            self.assertTrue(reg.IsConcrete(type_name))
            self.assertTrue(not reg.IsAppliedAPISchema(type_name))

    async def test_schema(self):

        # Better be safe and use only ASCII range chars in the schema.usda
        with open(SCHEMA_PATH, "r", encoding="ascii") as schema_file:
            schema_file.read()

    async def test_generated_schema(self):

        # Better be safe and use only ASCII range chars in the schema.usda
        with open(GENERATED_SCHEMA_PATH, "r", encoding="ascii") as schema_file:
            schema_file.read()
