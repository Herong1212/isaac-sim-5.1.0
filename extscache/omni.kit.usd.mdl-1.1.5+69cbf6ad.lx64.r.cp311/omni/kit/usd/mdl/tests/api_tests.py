import asyncio
import re

import omni.UsdMdl as UsdMdl
from pxr import Sdf

from .lib.base import UsdMdlTestBase


class Api_Tests(UsdMdlTestBase):
    async def test_api_get_overloads_not_connected(self):
        mdl_module = "overload.mdl"
        subidentifier = "test_overload(int,int)"

        usdshade_shader = self.create_usdshade_shader(mdl_module=mdl_module, subidentifier=subidentifier)

        source_asset = self.get_module_path(mdl_module)

        res = usdshade_shader.SetSourceAsset(source_asset, "mdl")
        self.assertTrue(res)

        res = usdshade_shader.SetSourceAssetSubIdentifier(subidentifier, "mdl")
        self.assertTrue(res)

        prim = usdshade_shader.GetPrim()
        self.assertIsNotNone(prim)

        overloads = UsdMdl.RegistryUtils.GetOverloads(prim)
        self.assertIsNotNone(overloads)
        self.assertTrue(len(overloads) == 5)

        expected = [
            "test_overload(int,int)",
            "test_overload(int,int,SimpleStruct)",
            "test_overload(float,float)",
            "test_overload(int,float)",
            "test_overload(float,int)",
        ]

        for sdr_node in overloads:
            sdr_node_identifier = sdr_node.GetIdentifier()
            sdr_node_subidentifier = sdr_node.GetSubIdentifier()
            self.assertTrue(expected.count(sdr_node_subidentifier) == 1)

    async def test_api_get_overloads_connected(self):
        nodegraph_path = "/World/NodeGraph"
        usdshade_nodegraph_prim = self.create_prim(nodegraph_path, "NodeGraph")

        source_usdshade_shader = self.create_usdshade_shader(
            prim_path=f"{nodegraph_path}/source", mdl_module="int.mdl", subidentifier="test_int"
        )

        dest_usdshade_shader = self.create_usdshade_shader(
            prim_path=f"{nodegraph_path}/dest", mdl_module="overload.mdl", subidentifier="test_overload(int,int)"
        )

        inputA = dest_usdshade_shader.CreateInput("a", Sdf.ValueTypeNames.Int)

        self.assertIsNotNone(inputA)

        inputB = dest_usdshade_shader.CreateInput("b", Sdf.ValueTypeNames.Int)

        self.assertIsNotNone(inputB)

        inputB.GetAttr().Set(11)

        outputInt = source_usdshade_shader.CreateOutput(UsdMdl.Tokens.DefaultOutputPortName, Sdf.ValueTypeNames.Int)

        self.assertIsNotNone(outputInt)

        self.assertTrue(inputA.ConnectToSource(outputInt))

        root_shader = self.create_usdshade_shader(
            prim_path=f"{nodegraph_path}/root", mdl_module="int.mdl", subidentifier="test_int"
        )

        root_in = root_shader.CreateInput("a", Sdf.ValueTypeNames.Int)

        self.assertIsNotNone(root_in)

        dest_out = dest_usdshade_shader.CreateOutput(UsdMdl.Tokens.DefaultOutputPortName, Sdf.ValueTypeNames.Int)
        self.assertIsNotNone(dest_out)

        self.assertTrue(root_in.ConnectToSource(dest_out))

        prim = dest_usdshade_shader.GetPrim()
        self.assertIsNotNone(prim)

        overloads = UsdMdl.RegistryUtils.GetOverloads(prim, True)
        self.assertIsNotNone(overloads)
        self.assertTrue(len(overloads) == 2)

        expected = [
            "test_overload(int,int)",
            "test_overload(int,int,SimpleStruct)",
        ]

        for sdr_node in overloads:
            sdr_node_identifier = sdr_node.GetIdentifier()
            sdr_node_subidentifier = sdr_node.GetSubIdentifier()
            self.assertTrue(expected.count(sdr_node_subidentifier) == 1)

    async def test_api_find_shader_node_for_prim(self):
        mdl_module = "color.mdl"
        subidentifier = "test_color(color)"

        usdshade_shader = self.create_usdshade_shader(mdl_module=mdl_module, subidentifier=subidentifier)

        sdr_node = UsdMdl.RegistryUtils.FindShaderNodeForPrim(usdshade_shader.GetPrim())
        self.assertIsNotNone(sdr_node)

        expected = "test_color"
        sdr_node_identifier = sdr_node.GetIdentifier()
        sdr_node_subidentifier = sdr_node.GetSubIdentifier()
        self.assertTrue(expected == sdr_node_subidentifier)

    async def test_api_find_shader_node_for_prim_with_parameter(self):
        mdl_module = "find_overload.mdl"
        subidentifier = "test_find_overload"

        usdshade_shader = self.create_usdshade_shader(mdl_module=mdl_module, subidentifier=subidentifier)

        inputA = usdshade_shader.CreateInput("a", Sdf.ValueTypeNames.Int)
        self.assertIsNotNone(inputA)
        inputA.Set(11)

        sdr_node = UsdMdl.RegistryUtils.FindShaderNodeForPrim(usdshade_shader.GetPrim())
        self.assertIsNotNone(sdr_node)

        expected = "test_find_overload(int,float)"
        sdr_node_identifier = sdr_node.GetIdentifier()
        sdr_node_subidentifier = sdr_node.GetSubIdentifier()
        self.assertTrue(expected == sdr_node_subidentifier)

    async def test_api_get_subidentifier_from_identifier(self):
        mdl_module = "math.mdl"
        subidentifier = "test_add(float,float)"

        usdshade_shader = self.create_usdshade_shader(mdl_module=mdl_module, subidentifier=subidentifier)

        sdr_node = UsdMdl.RegistryUtils.FindShaderNodeForPrim(usdshade_shader.GetPrim())
        self.assertIsNotNone(sdr_node)

        sdr_node_identifier = sdr_node.GetIdentifier()
        sdr_node_subidentifier = UsdMdl.RegistryUtils.GetSubIdentifierFromIdentifier(sdr_node_identifier)

        self.assertTrue(subidentifier == sdr_node_subidentifier)

    async def test_api_add_module_to_registry(self):
        # Note because we are testing to make sure the module is not loaded this module cannot be loaded by any of the other tests
        mdl_module = "add_module_int.mdl"

        source_asset = self.get_module_path(mdl_module)

        self.assertFalse(UsdMdl.RegistryUtils.IsModuleLoaded(source_asset))

        self.assertTrue(UsdMdl.RegistryUtils.AddModuleToRegistry(source_asset))
        self.assertTrue(UsdMdl.RegistryUtils.IsModuleLoaded(source_asset))

    async def test_api_add_modules_to_registry(self):
        # Note because we are testing to make sure the modules are not loaded these modules cannot be loaded by any of the other tests
        mdl_modules = ["add_module_bool.mdl", "add_module_float.mdl"]
        assetPaths = []

        for mdl_module in mdl_modules:
            assetPaths.append(self.get_module_path(mdl_module))
            self.assertFalse(UsdMdl.RegistryUtils.IsModuleLoaded(assetPaths[-1]))

        self.assertTrue(UsdMdl.RegistryUtils.AddModulesToRegistry(assetPaths))

        for assetPath in assetPaths:
            self.assertTrue(UsdMdl.RegistryUtils.IsModuleLoaded(assetPath))

    async def test_api_get_subidentifiers_for_asset(self):
        mdl_module = "overload.mdl"

        source_asset = self.get_module_path(mdl_module)
        subIdentifiers = UsdMdl.RegistryUtils.GetSubIdentifiersForAsset(source_asset)
        self.assertIsNotNone(subIdentifiers)

        expected = [
            "test_overload(int,int)",
            "test_overload(int,int,SimpleStruct)",
            "test_overload(float,float)",
            "test_overload(float,int)",
            "test_overload(int,float)",
            "SimpleStruct(int,float)",
            "SimpleStruct(SimpleStruct)",
            "SimpleStruct.i",
            "SimpleStruct.f",
        ]

        self.assertTrue(len(expected) == len(subIdentifiers))
        for subIdentifier in subIdentifiers:
            self.assertTrue(expected.count(subIdentifier) == 1)

    async def test_api_get_shader_node(self):
        mdl_module = "int.mdl"
        subidentifier = "test_int"

        source_asset = self.get_module_path(mdl_module)

        self.assertTrue(UsdMdl.RegistryUtils.AddModuleToRegistry(source_asset))
        sdr_node = UsdMdl.RegistryUtils.GetShaderNode(source_asset, subidentifier)
        self.assertIsNotNone(sdr_node)

    async def test_api_get_shader_node_from_prim(self):
        mdl_module = "int.mdl"
        subidentifier = "test_int"

        self.validate_node(mdl_module, subidentifier)

    async def test_api_get_shader_node_material(self):
        # OMPE-28754: test different subidentifier syntax
        # 1. with args
        # 2. without args.

        mdl_module = "material.mdl"
        source_asset = self.get_module_path(mdl_module)
        self.assertTrue(UsdMdl.RegistryUtils.AddModuleToRegistry(source_asset))

        # case 1: with args
        subidentifier = "diffuse(color,float,float3)"
        sdr_node = self.get_sdr_node(source_asset, subidentifier)
        args = [sdr_node.GetModuleUsdIdentifier(), sdr_node.GetNameWithSignature()]

        # case 2: without args
        subidentifier = "diffuse"
        sdr_node = self.get_sdr_node(source_asset, subidentifier)
        no_args = [sdr_node.GetModuleUsdIdentifier(), sdr_node.GetNameWithSignature()]

        # validate that mdl module load metadata is the same for each.
        self.assertTrue(args == no_args)

    async def test_api_get_identifier_for_asset(self):
        # hash is not wrapped, nor is it guaranteed to be repeatable, so the best we can do is check to see if it matches a pattern
        # 2771459770120540286<test_int><mdl>
        pattern = r"\d+<test_int><\w+>"

        mdl_module = "int.mdl"
        subidentifier = "test_int"

        assetPath = self.get_module_path(mdl_module)
        identifier = UsdMdl.RegistryUtils.GetIdentifierForAsset(assetPath, subidentifier)

        self.assertTrue(re.match(pattern, identifier))