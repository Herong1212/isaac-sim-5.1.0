# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add suport for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
import asyncio
import os
import pprint
import sys
from pathlib import Path

import carb
import omni.usd
import omni.UsdMdl as UsdMdl
from pxr import Ar, Ndr, Sdf, Sdr, UsdShade


class UsdMdlTestBase(omni.kit.test.AsyncTestCase):
    ext_root_path = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.usd.mdl}"))
    data_path = ext_root_path.joinpath("data")
    mdl_path = data_path.joinpath("mdl")
    resources_path = data_path.joinpath("resources")

    debug = False
    debug_value = False

    # Before running each test
    async def setUp(self):
        context = omni.usd.get_context()
        self.assertIsNotNone(context)

        context.new_stage()
        self.stage = context.get_stage()
        self.assertIsNotNone(self.stage)

    # After running each test
    async def tearDown(self):
        pass

    async def wait(self, count=20):
        for i in range(count):
            await omni.kit.app.get_app().next_update_async()

    def create_prim(self, prim_path, prim_type):
        prim = self.stage.DefinePrim(prim_path, prim_type)
        self.assertIsNotNone(prim)
        return prim

    def createTempDir(self):
        carb_fs = carb.filesystem.acquire_filesystem()
        temp_dir = carb_fs.make_temp_directory()
        self.assertTrue(os.path.exists(temp_dir))
        return temp_dir

    def get_module_path(self, mdl_module):
        module_path = str(UsdMdlTestBase.mdl_path.joinpath(mdl_module))
        self.assertTrue(os.path.exists(module_path))

        return Sdf.AssetPath(module_path, Ar.GetResolver().Resolve(module_path))

    def create_usdshade_shader(self, prim_path="/World/Shader", mdl_module="", subidentifier=""):

        prim = self.create_prim(prim_path, "Shader")

        usdshade_shader = UsdShade.Shader(prim)
        self.assertIsNotNone(usdshade_shader)

        if mdl_module and subidentifier:
            source_asset = self.get_module_path(mdl_module)

            res = usdshade_shader.SetSourceAsset(source_asset, UsdMdl.Tokens.Mdl)
            self.assertTrue(res)

            res = usdshade_shader.SetSourceAssetSubIdentifier(subidentifier, UsdMdl.Tokens.Mdl)
            self.assertTrue(res)

        return usdshade_shader

    def validate_node(self, mdl_module, subidentifier):
        usdshade_shader = self.create_usdshade_shader(mdl_module=mdl_module, subidentifier=subidentifier)

        sdr_node = UsdMdl.RegistryUtils.GetShaderNodeForPrim(usdshade_shader.GetPrim())
        self.assertIsNotNone(sdr_node)

        return sdr_node

    def debug_dump_sdr(self, fp=sys.stdout, only_sdr_node=False):
        def _print_metadata(metadata, fp, prefix):
            if not metadata:
                return

            for k, v in metadata.items():
                val = self.evalStr(v)
                if isinstance(val, dict):
                    print(f"{prefix}{k}: " + "{", file=fp)
                    _print_metadata(val, fp, prefix + "\t")
                    print(f"{prefix}" + "}", file=fp)
                else:
                    print(f"{prefix}{k}: {v}", file=fp)

        def _print_sdr_property(name, prop, fp, prefix="\t\t"):
            print(f"{prefix}name: {name}", file=fp)

            sdf_type = prop.GetTypeAsSdfType()
            print(f"{prefix}\ttype: {sdf_type[0]} \t {sdf_type[1]}", file=fp)
            print(f"{prefix}\tdefault value: {prop.GetDefaultValue()}", file=fp)
            print(f"{prefix}\thelp: {prop.GetHelp()}", file=fp)
            print(f"{prefix}\timplementation name: {prop.GetImplementationName()}", file=fp)
            print(f"{prefix}\tlabel: {prop.GetLabel()}", file=fp)
            print(f"{prefix}\toptions: {prop.GetOptions()}", file=fp)
            print(f"{prefix}\tpage: {prop.GetPage()}", file=fp)

            metadata = prop.GetMetadata()
            if metadata:
                print(f"{prefix}\tmetadata:", file=fp)
                _print_metadata(metadata, fp, prefix + "\t\t")

            hints = prop.GetHints()
            if hints:
                print(f"{prefix}\thints:", file=fp)
                _print_metadata(hints, fp, prefix + "\t\t")

        def _print_sdr_node(sdr_node, fp, prefix="\t"):
            print(f"sdr node: {sdr_node.GetName()}", file=fp)
            print(f"{prefix}version: {sdr_node.GetVersion()}", file=fp)
            print(f"{prefix}context: {sdr_node.GetContext()}", file=fp)
            print(f"{prefix}family: {sdr_node.GetFamily()}", file=fp)
            print(f"{prefix}identifier: {sdr_node.GetIdentifier()}", file=fp)
            print(f"{prefix}source type: {sdr_node.GetSourceType()}", file=fp)
            print(f"{prefix}uri: {sdr_node.GetResolvedImplementationURI()}", file=fp)
            print(f"{prefix}help: {sdr_node.GetHelp()}", file=fp)
            print(f"{prefix}pages: {sdr_node.GetPages()}", file=fp)
            print(f"{prefix}primvars: {sdr_node.GetPrimvars()}", file=fp)
            print(f"{prefix}label: {sdr_node.GetLabel()}", file=fp)
            print(f"{prefix}asset id inputs: {sdr_node.GetAssetIdentifierInputNames()}", file=fp)
            print(f"{prefix}primvar props: {sdr_node.GetAdditionalPrimvarProperties()}", file=fp)

            metadata = sdr_node.GetMetadata()
            if metadata:
                print(f"{prefix}metadata:", file=fp)
                _print_metadata(metadata, fp, prefix + "\t")

            if not only_sdr_node:
                print(f"{prefix}inputs:", file=fp)
                for name in sdr_node.GetInputNames():
                    _print_sdr_property(name, sdr_node.GetInput(name), fp)

                print(f"{prefix}outputs:", file=fp)
                for name in sdr_node.GetOutputNames():
                    _print_sdr_property(name, sdr_node.GetOutput(name), fp)

            print("\n\n", file=fp)

        print("\n\ndebug_dump_sdr()")
        sdr = Sdr.Registry()

        for sdr_node_id in sdr.GetNodeIdentifiers(filter=Ndr.VersionFilterAllVersions):
            sdr_node = sdr.GetShaderNodeByIdentifier(sdr_node_id)

            if (not sdr_node) or (sdr_node.GetSourceType() != UsdMdl.Tokens.Mdl):
                continue

            _print_sdr_node(sdr_node, fp)

    def debug_print(self, sdr_node):
        def print_metadata(metadata):
            to_print = {}
            for k, v in metadata.items():
                to_print[k] = self.evalStr(v)
            pprint.pprint(to_print, indent=2)

        print(f"\n\ndebug_print()\tsdr node name: {sdr_node.GetName()}")

        sdr_node_metadata = sdr_node.GetMetadata()
        print("\nsdr_node_metadata:")
        print_metadata(self.evalStr(sdr_node.GetMetadata()))

        print("\ninputs:")
        for name in sdr_node.GetInputNames():
            print(f"sdr property name: {name}")
            sdr_property = sdr_node.GetInput(name)
            print(f"\tdefault value: {sdr_property.GetDefaultValue()}")
            print(f"\thints:")
            print_metadata(self.evalStr(sdr_property.GetHints()))
            print(f"\tmetadata:")
            print_metadata(self.evalStr(sdr_property.GetMetadata()))

        print("\noutputs:")
        for name in sdr_node.GetOutputNames():
            print(f"sdr property name: {name}")
            sdr_property = sdr_node.GetOutput(name)
            print(f"\thints:")
            print_metadata(self.evalStr(sdr_property.GetHints()))
            print(f"\tmetadata:")
            print_metadata(self.evalStr(sdr_property.GetMetadata()))

    def evalStr(self, s):
        if isinstance(s, str):
            try:
                s = eval(s)
            except:
                pass

        return s

    def isClose(self, a, b):
        if (a is not None) and (b is not None):
            self.assertTrue(abs(a - b) < 1e-7)

    def validateValue(self, sdr, to_check, key=None, prefix=""):
        if self.debug_value:
            print(f"{prefix}validateValue()\tkey: {key}\tsdr: {sdr}\tto_check: {to_check}")

        a = self.evalStr(sdr)
        b = self.evalStr(to_check)

        if isinstance(b, dict):
            for k, v in b.items():
                self.validateValue(a.get(k, None), v, key=k, prefix=prefix + "\t")

        elif isinstance(b, tuple) or isinstance(b, list):
            for i in range(len(b)):
                self.validateValue(a[i], b[i], key=key, prefix=prefix + "\t")

        # special case for symbol due to long mangled name
        elif (key == UsdMdl.Metadata.Symbol) or (key == UsdMdl.Metadata.ArrayDeferredSizeSymbol):
            self.assertTrue(a.endswith(b))

        # special case for long mangled name
        elif (key == UsdMdl.Metadata.ExpressionValue) and isinstance(a, str):
            self.assertTrue(a.endswith(b))

        elif isinstance(b, Sdf.AssetPath):
            aAssetPath = a
            if isinstance(a, str):
                aAssetPath = Sdf.AssetPath(a.replace("@", ""))
            aAssetPath = os.path.normpath(aAssetPath.path)
            bAssetPath = os.path.normpath(b.path)
            self.assertTrue(aAssetPath.endswith(bAssetPath))

        elif (
            isinstance(b, bool)
            or isinstance(b, int)
            or isinstance(b, str)
            or isinstance(b, type)
            or isinstance(b, Sdf.AssetPath)
        ):
            self.assertTrue(a == b)

        else:
            self.isClose(a, b)

    def validate_property(self, name, sdr_node, value_type_name, is_input, metadata, default_value=None, options=None):
        if self.debug_value:
            print(f"\n\nvalidate_property()\t{name}")

        if is_input:
            sdr_property = sdr_node.GetInput(name)
        else:
            sdr_property = sdr_node.GetOutput(name)

        self.assertIsNotNone(sdr_property)

        sdf_type = sdr_property.GetTypeAsSdfType()
        type_name = sdf_type[0]
        if (type_name == Sdf.ValueTypeNames.Token) and sdf_type[1]:
            type_name = sdf_type[1]

        self.assertTrue(type_name == value_type_name)

        if isinstance(default_value, list):
            self.assertTrue(sdr_property.IsArray())
            self.assertTrue(sdr_property.GetArraySize() == len(default_value))

        if default_value:
            self.validateValue(sdr_property.GetDefaultValue(), default_value)

        if options:
            self.validate_property_options(sdr_property, options)

        sdr_metadata = sdr_property.GetMetadata()

        self.validateValue(sdr_metadata, metadata)

    def validate_property_options(self, sdr_property, options_to_check):
        options = sdr_property.GetOptions()
        self.assertIsNotNone(options)

        self.assertTrue(len(options), len(options_to_check))

        for option in options_to_check:
            self.assertTrue(option in options)

    def validate_mdl(
        self,
        mdl_module,
        subidentifier,
        value_type_name,
        default_value,
        metadata,
        input_metadata=None,
        options=None,
        checkOutputs=True,
    ):
        sdr_node = self.validate_node(mdl_module, subidentifier)

        if self.debug:
            self.debug_print(sdr_node)
            return

        if checkOutputs:
            for outputName in sdr_node.GetOutputNames():
                self.validate_property(outputName, sdr_node, value_type_name, False, metadata)

        if input_metadata:
            metadata.update(input_metadata)

        self.validate_property("param", sdr_node, value_type_name, True, metadata, default_value, options=options)

    def get_sdr_node(self, source_asset, subidentifier):
        sdr_node = UsdMdl.RegistryUtils.GetShaderNode(source_asset, subidentifier)
        self.assertIsNotNone(sdr_node)
        return sdr_node