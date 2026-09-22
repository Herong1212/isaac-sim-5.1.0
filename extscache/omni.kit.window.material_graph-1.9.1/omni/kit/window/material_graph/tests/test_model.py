## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from pathlib import Path

import omni.kit
import omni.usd
from omni.ui.tests.test_base import OmniUiTest
from pxr import Usd, UsdShade

from ..usdshade_graph_model import UsdShadeGraphModel

CURRENT_PATH = Path(__file__).parent.joinpath("../../../../../data/tests")


class TestMaterialGraphModel(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._usd_file_path = CURRENT_PATH.absolute().resolve().joinpath("graph_model_test.usda")

    # After running each test
    async def tearDown(self):
        self._usd_file_dir = None
        await super().tearDown()

    async def test_model(self):
        stage = Usd.Stage.Open(str(self._usd_file_path))
        await omni.usd.get_context().open_stage_async(str(self._usd_file_path))
        material = UsdShade.Material.Get(stage, "/World/Looks/PreviewSurfaceTexture")
        material_prim = material.GetPrim()
        self.assertTrue(material_prim.IsValid())

        model = UsdShadeGraphModel([material_prim])
        # check the nodes
        nodes_graph = model[material_prim].nodes
        nodes_usd = material_prim.GetChildren()
        nodes_graph_paths = sorted([p.GetPath() for p in nodes_graph])
        nodes_usd_paths = sorted([p.GetPath() for p in nodes_usd])
        self.assertEqual(nodes_graph_paths, nodes_usd_paths)

        # check the ports
        texture_prim = nodes_usd[0]
        attributes_usd = texture_prim.GetAttributes()
        attributes_graph = model[texture_prim].ports
        attributes_usd_name = sorted(
            [
                p.GetName()
                for p in attributes_usd
                if not p.GetName().startswith("info:") and not p.GetName().startswith("ui:nodegraph:node:")
            ]
        )
        attributes_graph_name = sorted([p.GetName() for p in attributes_graph])
        self.assertEqual(attributes_usd_name, attributes_graph_name)

        # check the inputs
        for attr in attributes_usd:
            inputs_usd_path = attr.GetConnections()
            if len(inputs_usd_path) > 0:
                inputs_graph = model[attr].inputs
                inputs_graph_path = [p.GetPath() for p in inputs_graph]
                self.assertEqual(inputs_usd_path, inputs_graph_path)

        # check the outputs
        for attr in material_prim.GetAttributes():
            inputs_usd_paths = attr.GetConnections()
            for input_usd_path in inputs_usd_paths:
                output_usd = stage.GetAttributeAtPath(input_usd_path)
                output_graph = model[attr].outputs
                self.assertEqual([output_usd], output_graph)
