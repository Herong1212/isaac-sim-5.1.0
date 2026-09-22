## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

from pathlib import Path
from typing import Optional

import omni.kit
import omni.ui as ui
import omni.usd
from omni.ui.tests.test_base import OmniUiTest
from pxr import Sdf, Usd, UsdShade, UsdUI

from ..graph_window import GraphWindow
from ..shader_registry import ShaderRegistry
from ..usdshade_graph_model import UsdShadeGraphModel


class TestCommand(OmniUiTest):
    async def setUp(self):
        await super().setUp()
        await ShaderRegistry().Get("mdl").reload()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_create_usd_material_graph(self):
        """Create a new material which has a subgraph so we can test most of the commands"""

        await omni.kit.app.get_app().next_update_async()

        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()

        if stage.HasDefaultPrim():
            looks_path = stage.GetDefaultPrim().GetPath()
        else:
            looks_path = Sdf.Path.absoluteRootPath
        looks_path = looks_path.AppendChild("Looks")
        material_name = "MyMaterial"
        # Create a new material
        omni.kit.commands.execute(
            "NewUsdShadeMaterialCommand", parent_path=looks_path, identifier=material_name, select_new_prim=True
        )
        # check the stage has the new created material
        material_path = looks_path.AppendChild(material_name)
        material_prim = stage.GetPrimAtPath(material_path)
        self.assertTrue(material_prim.IsValid())

        # create a new nodegraph
        nodegraph_name = "MyNodeGraph"
        nodegraph_path = material_path.AppendChild(nodegraph_name)
        omni.kit.commands.execute(
            "NewUsdShadeNodeGraphCommand", parent_path=material_path, identifier=nodegraph_name, position=(100, 100)
        )
        nodegraph_prim = stage.GetPrimAtPath(nodegraph_path)
        self.assertTrue(nodegraph_prim.IsValid())

        # create a new usd shader node
        node_name = "data_lookup_float"
        source_asset = "nvidia/support_definitions.mdl"
        sub_identifier = "data_lookup_float"
        node_path = nodegraph_path.AppendChild(node_name)
        pos_val = (100, 200)
        omni.kit.commands.execute(
            "NewUsdShadeNodeCommand",
            parent_path=nodegraph_path,
            source_asset=source_asset,
            sub_identifier=sub_identifier,
            position=pos_val,
            node=ShaderRegistry().Get("mdl").get_node_by_asset_and_id(source_asset, sub_identifier),
        )
        node_prim = stage.GetPrimAtPath(node_path)
        input_attr = node_prim.GetAttribute("inputs:default_value")
        output_attr = node_prim.GetAttribute("outputs:out")

        self.assertTrue(node_prim.IsValid())
        self.assertTrue(input_attr.IsDefined())
        self.assertTrue(output_attr.IsDefined())

        # move the node position and test UsdUINodeGraphNodeSetCommand
        new_pos_val = (100, 300)
        omni.kit.commands.execute(
            "UsdUINodeGraphNodeSetCommand",
            attribute=UsdUI.Tokens.uiNodegraphNodePos,
            prim_path=node_path,
            value=new_pos_val,
            prev=pos_val,
        )
        pos_attr = node_prim.GetAttribute(UsdUI.Tokens.uiNodegraphNodePos)
        self.assertEqual(pos_attr.Get(), new_pos_val)

        # create an input shader
        omni.kit.commands.execute(
            "CreateInputPortCommand", prim_path=nodegraph_path, port_name="f", port_type=Sdf.ValueTypeNames.Float
        )
        source_attr = nodegraph_prim.GetAttribute("inputs:f")
        self.assertTrue(source_attr.IsDefined())
        # test connection
        omni.kit.commands.execute(
            "ConnectUsdShadeToSourceCommand", target=UsdShade.Input(input_attr), source=UsdShade.Input(source_attr)
        )
        # check connection works
        self.assertEqual(input_attr.GetConnections(), [source_attr.GetPath()])

        # create an output shader
        omni.kit.commands.execute(
            "CreateOutputPortCommand", prim_path=nodegraph_path, port_name="out", port_type=Sdf.ValueTypeNames.Float
        )
        target_attr = nodegraph_prim.GetAttribute("outputs:out")
        self.assertTrue(target_attr.IsDefined())
        # test connection
        omni.kit.commands.execute(
            "ConnectUsdShadeToSourceCommand", target=UsdShade.Output(target_attr), source=UsdShade.Output(output_attr)
        )
        # check connection works
        self.assertEqual(target_attr.GetConnections(), [output_attr.GetPath()])

        # test disconnection
        omni.kit.commands.execute("UsdShadeDisconnectSourceCommand", target=UsdShade.Output(target_attr))
        self.assertEqual(target_attr.GetConnections(), [])

    async def test_import_compound(self):
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()

        if stage.HasDefaultPrim():
            world_path = stage.GetDefaultPrim().GetPath()
        else:
            world_path = Sdf.Path.absoluteRootPath

        # Create a new texture shader which contains a compound
        texture_name = "file_texture"
        asset_file = Path(__file__).parent.joinpath("../../../../../data/shaders/texture_return.usda")
        omni.kit.commands.execute(
            "ImportCompoundCommand",
            parent_path=world_path,
            source_asset=str(asset_file).replace("\\", "/"),
            identifier=texture_name,
            position=(100, 100),
            attributes_to_set=None,
        )
        compound_path = world_path.AppendChild(texture_name)
        nodegraph_prim = stage.GetPrimAtPath(compound_path)
        self.assertEqual(nodegraph_prim.GetTypeName(), "NodeGraph")

        shader_path = compound_path.AppendChild(texture_name)
        shader_prim = stage.GetPrimAtPath(shader_path)
        self.assertTrue(shader_prim.IsValid())

    async def test_register_nodes(self):
        # Note, absolute paths should be avoided. Put your content into MDL search paths instead.
        source_asset = str(Path(__file__).parent.joinpath("../../../../../data/shaders/test_material.mdl"))
        sub_identifier = "test_material"
        category = "utils"

        # register shader
        self.assertTrue(
            ShaderRegistry().Get("mdl").register_node_by_asset_and_id(source_asset, sub_identifier, category)
        )
        await ShaderRegistry().Get("mdl").reload()
        nodes_with = ShaderRegistry().Get("mdl").nodes

        # verify shader has been added
        added = nodes_with[-1]
        self.assertEqual(added.sourceAsset, source_asset)
        self.assertEqual(added.subIdentifier, sub_identifier)
        self.assertEqual(added.category, category)

        # unregister shader
        self.assertTrue(ShaderRegistry().Get("mdl").deregister_node_by_asset_and_id(source_asset, sub_identifier))

        # verify shader has been removed.
        await ShaderRegistry().Get("mdl").reload()
        nodes_without = ShaderRegistry().Get("mdl").nodes
        self.assertEqual(len(nodes_with), len(nodes_without) + 1)
