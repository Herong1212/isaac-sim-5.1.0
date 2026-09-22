# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add suport for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
import omni.kit.test
from omni.kit.test_suite.helpers import open_stage, wait_stage_loading
import omni.kit.commands
from omni.kit import ui_test
from unittest import skipIf

# Import extension python module we are testing with absolute import path, as if we are external user (other extension)
import omni.mdl.usd_converter
from ..usd_converter import find_tokens
from omni.mdl import pymdlsdk
from omni.mdl import pymdl
from omni.mdl.neuraylib import register_extension_content, deregister_extension_content

import omni.usd

import shutil
import pathlib
import os
import carb
import carb.settings
import carb.tokens

from pathlib import Path
from pxr import Usd, UsdShade, Sdf
from os import walk

import asyncio

# Do not enable these tests here
# instead add the test dependency `omni.usd.fileformat.sbsar` in the config/extension.toml
try:
    import usd.fileformat.sbsar
    RUN_SUBSTANCE_TESTS: bool = True
except:
    RUN_SUBSTANCE_TESTS: bool = False

class RestoreDefaultExportSettings(object):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        carb.settings.get_settings().set("exts/omni.mdl.usd_converter/allowRelativeExports", True)
        carb.settings.get_settings().set("exts/omni.mdl.usd_converter/allowRelativeExportUpwardLevels", -1)

# Having a test class derived from omni.kit.test.AsyncTestCase declared on the root of module
# will make it auto-discoverable by omni.kit.test
class Test(omni.kit.test.AsyncTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._test_data = str(pathlib.Path(__file__).parent.joinpath("data"))
        self._test_data_usd = str(pathlib.Path(self._test_data).joinpath("usd"))
        self._test_data_mdl = str(pathlib.Path(self._test_data).joinpath("mdl"))

    # Before running each test
    async def setUp(self):
        self._usd_context = omni.usd.get_context()
        await self._usd_context.new_stage_async()
        self._stage = self._usd_context.get_stage()

    # After running each test
    async def tearDown(self):
        self._stage = None
        self._usd_context = None

    async def _load_scene(self, scene_file_path: str) -> None:
        await open_stage(scene_file_path, self._usd_context)
        await wait_stage_loading()
        self._stage = self._usd_context.get_stage()

    # compute the absolute path of the stage
    def get_local_test_scene_path(self, relative_path: str) -> str:
        return self._test_data_usd + "/" + relative_path

    # Actual test, notice it is "async" function, so "await" can be used if needed
    async def test_mdl_to_usd(self):

        # Disable standard path to ensure reproducible results locally and in TC
        NO_STD_PATH = "/app/mdl/nostdpath"
        settings = carb.settings.get_settings()
        settings.set_bool(NO_STD_PATH, True)

        filter_import = False
        tokens = find_tokens('mdl::ZA0OmniGlass_2Emdl::OmniGlass::converted_27', filter_import)
        result = (tokens == {'ZA0OmniGlass_2Emdl', 'converted_27', 'mdl', 'OmniGlass'})
        self.assertEqual(result, True)

        filter_import = True
        tokens = find_tokens('import ::state::normal;\n', filter_import)
        result = (tokens == {'state', 'normal'})
        self.assertEqual(result, True)

        filter_import = False
        tokens = find_tokens('    anno::author("NVIDIA CORPORATION"),\n', filter_import)
        result = (tokens == {'anno', 'author'})
        self.assertEqual(result, True)

        filter_import = True
        tokens = find_tokens('    anno::author("NVIDIA CORPORATION"),\n', filter_import)
        result = (len(tokens) == 0)
        self.assertEqual(result, True)

        output_path = pathlib.Path(omni.kit.test.get_test_output_path()).joinpath(self._testMethodName)
        output_path.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            output_dir: str = str(output_path)
            test_search_path = self._test_data_mdl
            fn = "core_definitions.usda"

            ADD_MDL_PATH = "/app/mdl/additionalUserPaths"
            settings = carb.settings.get_settings()
            mdl_custom_paths: list[str] = settings.get(ADD_MDL_PATH) or []
            mdl_custom_paths.append(test_search_path)
            mdl_custom_paths.append(output_dir)
            mdl_custom_paths = list(set(mdl_custom_paths))
            settings.set_string_array(ADD_MDL_PATH, mdl_custom_paths)

            result = omni.mdl.usd_converter.mdl_to_usd(
                moduleName="nvidia/core_definitions.mdl",
                targetFolder=output_dir,
                targetFilename=fn,
                output=omni.mdl.usd_converter.mdl_usd.OutputType.MATERIAL_AND_GEOMETRY)
            self.assertEqual(result, True)

            fn = "tutorials.usda"
            source_file = str(pathlib.Path(self._test_data_mdl).joinpath('nvidia/sdk_examples/tutorials.mdl'))
            module = source_file
            if os.path.exists(module):
                result = omni.mdl.usd_converter.mdl_to_usd(
                    moduleName=module,
                    targetFolder=output_dir,
                    targetFilename=fn,
                    searchPath=test_search_path)
                self.assertEqual(result, True)

            fn = "test_types.usda"
            source_file = str(pathlib.Path(self._test_data_mdl).joinpath('test/test_types.mdl'))
            module = source_file
            if os.path.exists(module):
                result = omni.mdl.usd_converter.mdl_to_usd(
                    moduleName=module,
                    targetFolder=output_dir,
                    targetFilename=fn,
                    searchPath=test_search_path)
                self.assertEqual(result, True)

            # Example: 'mdl::OmniSurface::OmniSurfaceBase::OmniSurfaceBase'
            # Return: 'OmniSurface/OmniSurfaceBase.mdl'
            result = omni.mdl.usd_converter.mdl_usd.prototype_to_source_asset('mdl::OmniSurface::OmniSurfaceBase::OmniSurfaceBase')
            self.assertEqual(result, 'OmniSurface/OmniSurfaceBase.mdl')

            result = omni.mdl.usd_converter.mdl_usd.parse_ov_resource_name('mdl::resolvedPath_texture_raw')
            self.assertEqual(result, 'resolvedPath')

            scene_file_path = self.get_local_test_scene_path("simple_bitmap/simple_bitmap.usda")
            await self._load_scene(scene_file_path)

            primPath = '/World/Looks/Material__42'
            prim = self._stage.GetPrimAtPath(primPath)

            omni.mdl.usd_converter.is_shader_resolved(self._stage, materialPrim=prim)

            output = str(pathlib.Path(output_dir).joinpath('output.mdl'))
            await omni.mdl.usd_converter.usd_to_mdl(path=output, prim=prim)

            result = omni.mdl.usd_converter.build_shader_node_for_material(prim)
            self.assertEqual(result, True)

    def _setup_converter_context(self) -> omni.mdl.usd_converter.mdl_usd.ConverterContext:
        ovNeurayLib = omni.mdl.neuraylib.get_neuraylib()
        dbScopeName: str =  ovNeurayLib.getCurrentDefaultScope()
        neuray: pymdlsdk.INeuray = pymdlsdk.attach_ineuray(ovNeurayLib.getNeurayAPI())
        trans: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(ovNeurayLib.createReadingTransaction(dbScopeName))
        self.assertTrue(trans.is_open())
        context = omni.mdl.usd_converter.mdl_usd.ConverterContext()
        context.set_neuray(neuray)
        context.set_dbScopeName(dbScopeName)
        context.set_transaction(trans)
        context.ov_neuray = ovNeurayLib
        return context

    def _destroy_converter_context(self, context: omni.mdl.usd_converter.mdl_usd.ConverterContext):
        context.transaction.abort()
        context.set_transaction(None)

    async def test_searchpath_replacement_mappings(self):
        context: omni.mdl.usd_converter.mdl_usd.ConverterContext = self._setup_converter_context()
        await asyncio.sleep(3)
        test_cases: list = [
            ("file:/E:/kit/_build/mdl/Base", "::Z73file_3A::Z18E_3A::kit::'_build'::'mdl'::Base", "", "Z73file_3A::Z18E_3A::kit::'_build'::'mdl'::Base::", ""),
            ("file:/E:/kit/_build/mdl/Base/", "::Z73file_3A::Z18E_3A::kit::'_build'::'mdl'::Base", "", "Z73file_3A::Z18E_3A::kit::'_build'::'mdl'::Base::", ""),
            ("file:/buildAgent/'work space'/mdl/Base", "::Z73file_3A::buildAgent::Z20_27work_20space_27::'mdl'::Base", "", "Z73file_3A::buildAgent::Z20_27work_20space_27::'mdl'::Base::", ""),
            ("omniverse://content.ov.nvidia.com/Library/Materials", "::Z82omniverse_3A_2F::Z1Ccontent_2Eov_2Envidia_2Ecom::Library::Materials", "", "Z82omniverse_3A_2F::Z1Ccontent_2Eov_2Envidia_2Ecom::Library::Materials::", ""),
            ("omniverse://content.ov.nvidia.com/Library/Materials/", "::Z82omniverse_3A_2F::Z1Ccontent_2Eov_2Envidia_2Ecom::Library::Materials", "", "Z82omniverse_3A_2F::Z1Ccontent_2Eov_2Envidia_2Ecom::Library::Materials::", ""),
        ]
        for case in test_cases:
            search_path_uri: str = case[0]
            produced: omni.mdl.usd_converter.mdl_usd.PostProcessExportedModule.Replacement_mapping = \
                omni.mdl.usd_converter.mdl_usd.omni.mdl.usd_converter.mdl_usd.PostProcessExportedModule.Replacement_mapping.compute_for_search_path(search_path_uri, context)
            self.assertEqual(produced.import_search, case[1], f"[search path mapping] import_search for uri: '{search_path_uri}'")
            self.assertEqual(produced.import_replace, case[2], f"[search path mapping] import_replace for uri: '{search_path_uri}'")
            self.assertEqual(produced.usage_search, case[3], f"[search path mapping] usage_search for uri: '{search_path_uri}'")
            self.assertEqual(produced.usage_replace, case[4], f"[search path mapping] usage_replace for uri: '{search_path_uri}'")
        self._destroy_converter_context(context)


    async def test_import_parsing(self):
        context: omni.mdl.usd_converter.mdl_usd.ConverterContext = self._setup_converter_context()
        test_cases_spec: list = [
            # (input line, expected module set, is manged, search path)
            ("import m::*, n::*;", { "m::*", "n::*" }, False, ""),
            ("import ::m::*, n::*;", { "::m::*", "n::*" }, False, ""),
            ("import ::m::*, ::n::*;", { "::m::*", "::n::*" }, False, ""),
            ("import .::m::*, .::n::*;", { ".::m::*", ".::n::*" }, False, ""),
            ("import m::a, m::b, n::d;", { "m::a", "m::b", "n::d" }, False, ""),
            ("import ::m::a, m::b, ::n::d;", { "::m::a", "m::b", "::n::d" }, False, ""),
            ("import .::m::a, .::m::b, n::d;", { ".::m::a", ".::m::b", "n::d" }, False, ""),
            # TODO these cases are failing: ("using m import *;", { "m" }, False, ""),
            # TODO these cases are failing: ("using ::m import *;", { "::m" }, False, ""),
            # TODO these cases are failing: ("using .::m import *;", { ".::m" }, False, ""),
            # TODO these cases are failing: ("using ..::m import *;", { "..::m" }, False, ""),
            # TODO these cases are failing: ("using ..::..::m import *;", { "..::..::m" }, False, ""),
            # TODO these cases are failing: ("using m import a, b;", { "m" }, False, ""),
            # TODO these cases are failing: ("using ::m import a, b;", { "::m" }, False, ""),
            # TODO these cases are failing: ("using .::m import a, b;", { ".::m" }, False, ""),
            ("import ::nvidia::core_definitions::*;", { "::nvidia::core_definitions::*" }, False, ""),
            ("import .::some::thing::local::*;", { ".::some::thing::local::*" }, False, ""),
        ]
        test_cases_mangled = [
            # path with MDL module filename mangled
            ("import ::Z73file_3A::Z16C_3A::Temp::usd_water2::usd_vmat_water2::ZDEZ8Dcubanroyalpalmbark_5F2Emdl;", { "::Z73file_3A::Z16C_3A::Temp::usd_water2::usd_vmat_water2::ZDEZ8Dcubanroyalpalmbark_5F2Emdl" }, True, "file:/C:/Temp/usd_water2/usd_vmat_water2/Z8Dcubanroyalpalmbark_2Emdl"),
            # search path on windows
            ("import ::Z73file_3A::Z18E_3A::mdl::nvidia::core_definitions::*;", { "::Z73file_3A::Z18E_3A::mdl::nvidia::core_definitions::*" }, True, "file:/E:/mdl"),
            # search path on unix
            ("import ::Z73file_3A::buildAgent::work::mdl::nvidia::core_definitions::*;", { "::Z73file_3A::buildAgent::work::mdl::nvidia::core_definitions::*" }, True, "file:/buildAgent/work/mdl"),
            # stage path on windows
            ("import ::Z73file_3A::Z18E_3A::Z4Fkit_2D2::kit::foo::..::'_build'::mdl::Material__42::Material__42;", { "::Z73file_3A::Z18E_3A::Z4Fkit_2D2::kit::foo::..::'_build'::mdl::Material__42::Material__42" }, True, ""),
            ("import ::Z21file_3A_2F_2F::Z17D_3A::gitlab::Z4Fkit_2D2::kit::'_build'::Z0Awindows_2Dx86_5F64::foo;", { "::Z21file_3A_2F_2F::Z17D_3A::gitlab::Z4Fkit_2D2::kit::'_build'::Z0Awindows_2Dx86_5F64::foo" }, True, ""),
            # stage path on unix
            ("import ::Z73file_3A::buildAgent::work::_builtpackages::_build::Z2Flinux_2Dx86_5F64::release::exts::Material__42::*;", { "::Z73file_3A::buildAgent::work::_builtpackages::_build::Z2Flinux_2Dx86_5F64::release::exts::Material__42::*" }, True, ""),
            # TODO add network paths on windows
            # TODO add omniverse:/ and https:/
        ]

        test_cases = test_cases_spec + test_cases_mangled
        for i in range(len(test_cases)):
            # parse the imports and get the set of modules per line
            line: str = test_cases[i][0]
            expected: set = test_cases[i][1]
            produced: set = omni.mdl.usd_converter.mdl_usd.find_identifiers(line)
            self.assertEqual(expected, produced, f"[parsing] input: '{line}' \nexpected: {expected}\nproduced: {produced}")

            expected_is_mangled: bool = test_cases[i][2]
            module_identifier: str
            for module_identifier in produced:
                # detect if an identifier is mangled
                produced_is_mangled: bool = omni.mdl.usd_converter.mdl_usd.is_identifier_mangled(module_identifier, context)
                self.assertEqual(expected_is_mangled, produced_is_mangled, f"[is mangled] input: '{line}' \nexpected: {expected}\nproduced: {produced}")

                # TODO ideas to continue
                # only if the identifier is mangled, we put into the replacement map
                # first match the `unmangled_module_identifier` against search paths. if there is a hit:
                # - mangle the search path to get the prefix to cut off
                # - conditionally replace in the source code: if the line starts with "import" or "using", keep the leading "::"
                #   if not, also strip the leading "::"
                if produced_is_mangled:
                    search_path: str = test_cases[i][3]
                    if search_path != "":
                        self.assertTrue('\\' not in search_path, f"[search path] URI not valid: {search_path}")
                        unmangled_module_identifier: str = context.ov_neuray._unmangleUri(module_identifier, "::")
                        mangled_search_path = context.ov_neuray._mangleUri(search_path, "::") # todo not existing yet
                        self.assertTrue(unmangled_module_identifier.startswith(search_path), f"[search path] URI input: '{unmangled_module_identifier}' \nshould start with: {search_path}")
                        self.assertTrue(module_identifier.startswith(mangled_search_path), f"[search path] Mangled input: '{module_identifier}' \nshould start with: {mangled_search_path}")
        self._destroy_converter_context(context)

    async def test_mangling_reversibility(self):
        context: omni.mdl.usd_converter.mdl_usd.ConverterContext = self._setup_converter_context()
        test_cases = [
            # MDL module with a filename mangled
            ("file:/C:/Temp/usd_water2/usd_vmat_water2/.cubanroyalpalmbark.mdl", "::Z73file_3A::Z16C_3A::Temp::usd_water2::usd_vmat_water2::Z63_2Ecubanroyalpalmbark_2Emdl"),
            ("file:/C:/Temp/usd_water2/usd_vmat_water2/Z8Dcubanroyalpalmbark_2Emdl.mdl", "::Z73file_3A::Z16C_3A::Temp::usd_water2::usd_vmat_water2::ZF1Z8Dcubanroyalpalmbark_5F2Emdl_2Emdl"),
            ("file:/E:/kit/_build/mdl/Base", "::Z73file_3A::Z18E_3A::kit::_build::mdl::Base"),
            ("file:/buildAgent/'work space'/mdl/Base", "::Z73file_3A::buildAgent::Z20_27work_20space_27::mdl::Base"),
            ("omniverse://content.ov.nvidia.com/Library/Materials", "::Z82omniverse_3A_2F::Z1Ccontent_2Eov_2Envidia_2Ecom::Library::Materials")
        ]

        for i in range(len(test_cases)):

            uri: str = test_cases[i][0]
            expected_module_identifier: str = test_cases[i][1]

            module_identifier: str = context.ov_neuray._mangleUri(uri, "::")
            # print(f"* Module identifier:            {module_identifier}")
            self.assertEqual(expected_module_identifier, module_identifier, f"[magling] input: '{uri}' \nexpected: {expected_module_identifier}\nproduced: {module_identifier}")

            unmangled_module_identifier: str = context.ov_neuray._unmangleUri(module_identifier, "::")
            # print(f"  Unmangled module identifier:  {unmangled_module_identifier}")                        
            self.assertEqual(uri, unmangled_module_identifier, f"[parsing] input: '{uri}' \nexpected: {uri}\nproduced: {unmangled_module_identifier}")

        self._destroy_converter_context(context)

    async def test_usd_to_mdl(self):
        # open a simple scene with a mesh and a material assigned
        scene_file_path: str = self.get_local_test_scene_path("scene.usda")
        await self._load_scene(scene_file_path)

        mat_prim = self._stage.GetPrimAtPath('/World/Looks/Material')
        self.assertIsNotNone(mat_prim)

        output_path = pathlib.Path(omni.kit.test.get_test_output_path()).joinpath(self._testMethodName)
        output_path.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            path: str = str(pathlib.Path(output_path).joinpath('output.mdl'))
            prim: Usd.Prim = mat_prim
            forceNotOV: bool = False
            result = await omni.mdl.usd_converter.usd_to_mdl(path, prim, forceNotOV)
            self.assertTrue(result)
            carb.log_info(f"Material converted to MDL module: {path}")
            # Load the exported MDL module back in OV
            ovNeurayLib = omni.mdl.neuraylib.get_neuraylib()
            self.assertIsNotNone(ovNeurayLib)
            dbScopeName: str =  ovNeurayLib.getCurrentDefaultScope()
            ovModule = ovNeurayLib.createMdlModule(path, dbScopeName)
            self.assertIsNotNone(ovModule)
            self.assertTrue(ovModule.valid())
            ovNeurayLib.destroyMdlModule(ovModule)

    async def test_usd_to_mdl_local_module(self):
        scene_file_path: str = self.get_local_test_scene_path("simple_bitmap/simple_bitmap.usda")
        await self._load_scene(scene_file_path)

        mat_prim = self._stage.GetPrimAtPath('/World/Looks/Material__42')
        self.assertIsNotNone(mat_prim)

        # Create a temp folder in the data folder
        opath = pathlib.Path()
        opath = opath.joinpath(self._test_data)
        opath = opath.joinpath('TEMP')
        temp_dir = str(opath)
        shutil.rmtree(opath, ignore_errors=True)

        # Copy the MDL module to the output folder
        material_src_folder: str = self.get_local_test_scene_path("simple_bitmap/Materials")
        material_dst_folder: str = str(pathlib.Path(temp_dir).joinpath("Materials"))
        copied_dst_folder = shutil.copytree(material_src_folder, material_dst_folder)
        if not copied_dst_folder == material_dst_folder:
            carb.log_error(f"Invalid return folder from copytree(): {copied_dst_folder}")
        self.assertTrue(copied_dst_folder == material_dst_folder)

        path: str = str(pathlib.Path(temp_dir).joinpath('output.mdl'))
        prim: Usd.Prim = mat_prim
        forceNotOV: bool = False
        result = await omni.mdl.usd_converter.usd_to_mdl(path, prim, forceNotOV)
        self.assertTrue(result)
        carb.log_info(f"Material converted to MDL module: {path}")
        # Load the exported MDL module back in OV
        ovNeurayLib = omni.mdl.neuraylib.get_neuraylib()
        self.assertIsNotNone(ovNeurayLib)
        dbScopeName: str =  ovNeurayLib.getCurrentDefaultScope()
        ovModule = ovNeurayLib.createMdlModule(path, dbScopeName)
        self.assertIsNotNone(ovModule)
        if not ovModule.valid():
            carb.log_error(f"Invalid MDL module: {path}")
            output_dir = omni.kit.test.get_test_output_path()
            shutil.copy(path, output_dir)
            carb.log_error(f"MDL module copied to: {output_dir}")

        self.assertTrue(ovModule.valid())
        ovNeurayLib.destroyMdlModule(ovModule)

        # Delete the temp folder
        shutil.rmtree(opath, ignore_errors=True)

    async def test_expand_mdl_material_parameters(self):
        # set up the test
        self._stage = Usd.Stage.CreateInMemory()
        mtl_path = omni.usd.get_stage_next_free_path(self._stage, "/World/Looks/TestMaterial", False)
        mat_prim = self._stage.DefinePrim(mtl_path, "Material")
        material_prim = UsdShade.Material.Get(self._stage, mat_prim.GetPath())
        shader_mtl_path = self._stage.DefinePrim("{}/Shader".format(mtl_path), "Shader")
        shader_prim = UsdShade.Shader.Get(self._stage, shader_mtl_path.GetPath())
        shader_out = shader_prim.CreateOutput("out", Sdf.ValueTypeNames.Token)
        material_prim.CreateSurfaceOutput("mdl").ConnectToSource(shader_out)
        shader_out.SetRenderType("material")
        shader_prim.GetImplementationSourceAttr().Set(UsdShade.Tokens.sourceAsset)
        shader_prim.SetSourceAsset(Sdf.AssetPath("data/mdl/test/simple_texture.mdl"), "mdl")
        shader_prim.SetSourceAssetSubIdentifier("test_types", "mdl")

        # create a parameter with known value, confirming mdl_usd function won't override it
        test_value = 3.0
        shader_prim.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(test_value)

        # run the test
        result = await omni.mdl.usd_converter.expand_mdl_material_parameters(
            moduleName=str(pathlib.Path(self._test_data_mdl).joinpath('test/simple_texture.mdl')),
            stage=self._stage,
            materialPrim=material_prim)

        # check we get the expected
        self.assertTrue(result)
        self.assertTrue(bool(shader_prim.GetInput("diffuse_texture")))
        self.assertTrue(bool(shader_prim.GetInput("roughness")))
        self.assertEqual(shader_prim.GetInput("roughness").Get(), test_value)
        self.assertTrue(bool(shader_prim.GetInput("normal")))

    async def test_build_shader_node_for_material(self):
        path = pathlib.Path()
        path = path.joinpath(self._test_data_usd)
        path = path.joinpath('simple_tiny_multiple_outputs')
        path = path.joinpath('simple_tiny.usda')

        # open a simple scene with a mesh and a material assigned
        scene_file_path: str = str(path)
        await self._load_scene(scene_file_path)

        usd_prim_path:str = '/World/Looks/Material__42'
        prim = self._stage.GetPrimAtPath(usd_prim_path)

        self.assertIsNotNone(prim)

        # run the test
        result = omni.mdl.usd_converter.build_shader_node_for_material(prim)
        self.assertTrue(result)



    async def base_export_test(self,
                             scene_path: str,
                             usd_prim_path: str,
                             out_module_name: str,
                             out_material_name: str, # will be checked, can not be specified
                             out_additional_files: list[str] = []):
        context: omni.mdl.usd_converter.mdl_usd.ConverterContext = self._setup_converter_context()

        # open a simple scene with a mesh and a material assigned
        await self._load_scene(scene_path)

        prim = self._stage.GetPrimAtPath(usd_prim_path)
        self.assertIsNotNone(prim)

        # create the ouput folder and run the export
        # run the test
        output_path = pathlib.Path(omni.kit.test.get_test_output_path()).joinpath(self._testMethodName)
        output_dir: str = str(output_path)
        if output_path.exists():
            shutil.rmtree(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        output_module_filename: str = str(output_path.joinpath(out_module_name))
        prim: Usd.Prim = prim
        forceNotOV: bool = False
        result = await omni.mdl.usd_converter.usd_to_mdl(output_module_filename, prim, forceNotOV)
        self.assertTrue(result)

        # check if all expected files are there
        filenames = next(walk(output_dir), (None, None, []))[2]
        self.assertTrue(out_module_name in filenames)
        for resource in out_additional_files:
            self.assertTrue(resource in filenames, f"'{resource}' in '{filenames}'")
        self.assertTrue(len(filenames) == len(out_additional_files) + 1)

        # copy additional files
        source_dir: Path = Path(os.path.dirname(scene_path))

        # try to load the exported module
        # we test locally only here
        output_uri = omni.client.make_url(
            scheme='file',
            path=output_path.joinpath(out_module_name).as_posix()
        )

        ovModule = context.ov_neuray.createMdlModule(output_uri, context.db_scope_name)
        self.assertIsNotNone(ovModule)
        self.assertTrue(ovModule.valid())
        context.ov_neuray.destroyMdlModule(ovModule)
        self._destroy_converter_context(context)

        # create a new stage on load the exported materials
        _, _, content = await omni.client.read_file_async(self.get_local_test_scene_path('plain/plain.usda'))
        content_text: str = memoryview(content).tobytes().decode("utf-8")
        content_text = content_text.replace("{{SOURCE_ASSET}}", f"./{out_module_name}")
        content_text = content_text.replace("{{SUB_IDENTIFIER}}", out_material_name)
        result = await omni.client.write_file_async(f"{output_path}/import.usda", bytes(content_text.encode("utf-8")))
        self.assertEqual(result, omni.client.Result.OK)

        await self._load_scene(f"{output_path}/import.usda")


    async def test_export_mangling_local_content_no_resource(self):
        scene_path: str = self.get_local_test_scene_path('mangling/mangling_local_content_no_resource.usda')
        usd_prim_path: str = '/World/Looks/Material'
        out_module_name: str = 'mangling_local_content_no_resource.mdl'
        out_material_name: str = "Material"

        await self.base_export_test(scene_path, usd_prim_path, out_module_name, out_material_name, [])

    async def test_export_mangling_local_content_textured_default(self):
        scene_path: str = self.get_local_test_scene_path('mangling/mangling_local_content_textured_default.usda')
        usd_prim_path: str = '/World/Looks/Material'
        out_module_name: str = 'mangling_local_content_textured_default.mdl'
        out_material_name: str = "Material"
        out_additional_files: list[str] = [
            'mangling_local_content_textured_default_tile.1001.png'
        ]
        await self.base_export_test(scene_path, usd_prim_path, out_module_name, out_material_name, out_additional_files)

    async def test_export_mangling_local_content_textured_preset(self):
        scene_path: str = self.get_local_test_scene_path('mangling/mangling_local_content_textured_preset.usda')
        usd_prim_path: str = '/World/Looks/Material'
        out_module_name: str = 'mangling_local_content_textured_preset.mdl'
        out_material_name: str = "Material"
        out_additional_files: list[str] = [
            'mangling_local_content_textured_preset_tile.1003.png'
        ]
        await self.base_export_test(scene_path, usd_prim_path, out_module_name, out_material_name, out_additional_files)

    async def test_export_mangling_local_content_textured_preset_folded(self):
        scene_path: str = self.get_local_test_scene_path('mangling/mangling_local_content_textured_preset_folded.usda')
        usd_prim_path: str = '/World/Looks/Material'
        out_module_name: str = 'mangling_local_content_textured_preset_folded.mdl'
        out_material_name: str = "Material"
        out_additional_files: list[str] = [
            # no addional files. the body texture belongs to the original module which we are only referencing
        ]
        await self.base_export_test(scene_path, usd_prim_path, out_module_name, out_material_name, out_additional_files)

    async def test_export_mangling_local_content_textured_body(self):
        scene_path: str = self.get_local_test_scene_path('mangling/mangling_local_content_textured_body.usda')
        usd_prim_path: str = '/World/Looks/Material'
        out_module_name: str = 'mangling_local_content_textured_body.mdl'
        out_material_name: str = "Material"
        out_additional_files: list[str] = [
            # no addional files. the body texture belongs to the original module which we are only referencing
        ]
        await self.base_export_test(scene_path, usd_prim_path, out_module_name, out_material_name, out_additional_files)

    async def test_udim_searchpath_png(self):
        scene_path: str = self.get_local_test_scene_path('udim/from_search_path.usda')
        usd_prim_path: str = '/World/Looks/OmniSurface_png'
        out_module_name: str = 'from_search_path_png.mdl'
        out_material_name: str = "OmniSurface_png"
        out_additional_files: list[str] = [
            'from_search_path_png_tile.1001.png',
            'from_search_path_png_tile.1002.png',
            'from_search_path_png_tile.1003.png',
            'from_search_path_png_tile.1004.png',
            'from_search_path_png_tile.1005.png',
            'from_search_path_png_tile.1006.png',
        ]
        await self.base_export_test(scene_path, usd_prim_path, out_module_name, out_material_name, out_additional_files)

    async def test_udim_searchpath_exr(self):
        scene_path: str = self.get_local_test_scene_path('udim/from_search_path.usda')
        usd_prim_path: str = '/World/Looks/OmniSurface_exr'
        out_module_name: str = 'from_search_path_exr.mdl'
        out_material_name: str = "OmniSurface_exr"
        out_additional_files: list[str] = [
            'from_search_path_exr_tile.1001.exr',
            'from_search_path_exr_tile.1002.exr',
            'from_search_path_exr_tile.1003.exr',
            'from_search_path_exr_tile.1004.exr',
            'from_search_path_exr_tile.1005.exr',
            'from_search_path_exr_tile.1006.exr',
        ]
        await self.base_export_test(scene_path, usd_prim_path, out_module_name, out_material_name, out_additional_files)

    async def test_udim_local_content_png(self):
        scene_path: str = self.get_local_test_scene_path('udim/from_local_content.usda')
        usd_prim_path: str = '/World/Looks/main_png'
        out_module_name: str = 'from_local_content_png.mdl'
        out_material_name: str = "main_png"
        out_additional_files: list[str] = [
            'from_local_content_png_tile.1001.png',
            'from_local_content_png_tile.1002.png',
            'from_local_content_png_tile.1003.png',
            'from_local_content_png_tile.1004.png',
            'from_local_content_png_tile.1005.png',
            'from_local_content_png_tile.1006.png',
        ]
        await self.base_export_test(scene_path, usd_prim_path, out_module_name, out_material_name, out_additional_files)

    async def test_udim_local_content_exr(self):
        scene_path: str = self.get_local_test_scene_path('udim/from_local_content.usda')
        usd_prim_path: str = '/World/Looks/main_exr'
        out_module_name: str = 'from_local_content_exr.mdl'
        out_material_name: str = "main_exr"
        out_additional_files: list[str] = [
            'from_local_content_exr_tile.1001.exr',
            'from_local_content_exr_tile.1002.exr',
            'from_local_content_exr_tile.1003.exr',
            'from_local_content_exr_tile.1004.exr',
            'from_local_content_exr_tile.1005.exr',
            'from_local_content_exr_tile.1006.exr',
        ]
        await self.base_export_test(scene_path, usd_prim_path, out_module_name, out_material_name, out_additional_files)

    async def test_extension_content(self):
        # usually constant data for common extensions
        ext_id = omni.kit.app.get_app().get_extension_manager().get_extension_id_by_module(__name__)
        ext_dir = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id))
        ext_name = omni.ext.get_extension_name(ext_id)
        ext_content_dir: Path = ext_dir.joinpath('omni', 'mdl', 'usd_converter', 'tests', 'data', 'extension_content')
        ext_content_mdl_dir: Path = ext_content_dir.joinpath('mdl')
        # selecting this folder yields the following modules in the search path addressable as USD source asset:
        #   -   nvidia/ProjectXYZ/basic.mdl
        # and the corresponding MDL qualified module names:
        #   -   ::nvidia::ProjectXYZ::basic

        # allow extension content to be found via search path, done when loading the extension
        # NOTE keep the returned links in order to unregister on shutdown
        linkedContentPaths: list[str] = register_extension_content(ext_name, str(ext_content_mdl_dir))
        self.assertNotEqual(len(linkedContentPaths), 0)

        # the regual test
        scene_path: str = self.get_local_test_scene_path('extension_content_scene.usda')
        usd_prim_path: str = '/World/Looks/Material'
        out_module_name: str = 'extension_content_scene.mdl'
        out_material_name: str = "Material"
        out_additional_files: list[str] = []
        await self.base_export_test(scene_path, usd_prim_path, out_module_name, out_material_name, out_additional_files)

        # remove the extension content, usually done when unloading the extension
        removed: bool = deregister_extension_content(ext_name, linkedContentPaths)
        self.assertTrue(removed)


    # OM-87920: export MDLs from substance
    @skipIf(not RUN_SUBSTANCE_TESTS, "Skip some tests in CI. No external dependencies allowed.")
    async def test_substance_local(self):
        scene_path: str = self.get_local_test_scene_path('substance/substance.usda')
        usd_prim_path: str = '/World/Stone_tiles/PBR_Materials_Tiles/tiles_025'
        out_module_name: str = 'substance_export_local.mdl'
        out_material_name: str = "tiles_025"
        out_additional_files: list[str] = [
            'substance_export_local_0_ao_texture.png',
            'substance_export_local_0_diffuse_texture.png',
            'substance_export_local_0_metallic_texture.png',
            'substance_export_local_0_normalmap_texture.png',
            'substance_export_local_0_reflectionroughness_texture.png',
        ]
        await self.base_export_test(scene_path, usd_prim_path, out_module_name, out_material_name, out_additional_files, [])

    @skipIf(not RUN_SUBSTANCE_TESTS, "Skip some tests in CI. No external dependencies allowed.")
    async def test_substance_nucleus(self):
        scene_path: str = 'omniverse://kit-test-content.ov.nvidia.com/Projects/omni.mdl_tests/usd_converter/substance/substance.usda'
        usd_prim_path: str = '/World/Stone_tiles/PBR_Materials_Tiles/tiles_025'
        out_module_name: str = 'substance_export_nucleus.mdl'
        out_material_name: str = "tiles_025"
        out_additional_files: list[str] = [
            'substance_export_nucleus_0_ao_texture.png',
            'substance_export_nucleus_0_diffuse_texture.png',
            'substance_export_nucleus_0_metallic_texture.png',
            'substance_export_nucleus_0_normalmap_texture.png',
            'substance_export_nucleus_0_reflectionroughness_texture.png',
        ]
        await self.base_export_test(scene_path, usd_prim_path, out_module_name, out_material_name, out_additional_files, [])

    # exporting MDL modules that reference content local to the scene is limited
    # we try to make exports relative but can fall back to absolute pahts
    # we allow to limit the number of upward steps to allow to create the same output as with the old demangling
    async def test_export_mangling_local_content_textured_default_limit_relative_upward_levels(self):
        with RestoreDefaultExportSettings() as settings_override:
            carb.settings.get_settings().set("exts/omni.mdl.usd_converter/allowRelativeExportUpwardLevels", 0)

            scene_path: str = self.get_local_test_scene_path('mangling/mangling_local_content_textured_default.usda')
            usd_prim_path: str = '/World/Looks/Material'
            out_module_name: str = 'mangling_local_content_textured_default_relative.mdl'
            out_material_name: str = "Material"
            out_additional_files: list[str] = [
                'mangling_local_content_textured_default_relative_tile.1001.png'
            ]
            await self.base_export_test(scene_path, usd_prim_path, out_module_name, out_material_name, out_additional_files)

    # exporting MDL modules that reference content local to the scene is limited
    # we try to make exports relative but can fall back to absolute pahts
    # but we can force to use absolute paths
    async def test_export_mangling_local_content_textured_default_force_absolute(self):
        with RestoreDefaultExportSettings() as settings_override:
            carb.settings.get_settings().set("exts/omni.mdl.usd_converter/allowRelativeExports", False)

            scene_path: str = self.get_local_test_scene_path('mangling/mangling_local_content_textured_default.usda')
            usd_prim_path: str = '/World/Looks/Material'
            out_module_name: str = 'mangling_local_content_textured_default_absolute.mdl'
            out_material_name: str = "Material"
            out_additional_files: list[str] = [
                'mangling_local_content_textured_default_absolute_tile.1001.png'
            ]
            await self.base_export_test(scene_path, usd_prim_path, out_module_name, out_material_name, out_additional_files)

    async def base_expand_test(self, scene_file: str, materials: list[str], shaders: list[str], simplify_after_expand : bool = False):
        # Load stage
        await self._load_scene(scene_file)

        self.assertIsNotNone(self._stage, 'Invalid stage')

        for material_name in materials:
            material_prim = self._stage.GetPrimAtPath(material_name)
            self.assertIsNotNone(material_prim)

            result = omni.mdl.usd_converter.build_shader_node_for_material(material_prim, simplify_after_expand)

        for prim in self._stage.Traverse():
            if UsdShade.Shader(prim):
                if not prim.GetPath() in shaders:
                    carb.log_error(f"{prim.GetPath()} not found after expanding {material_name} from stage {scene_file}")
                self.assertTrue(prim.GetPath() in shaders)

        return result

    async def test_expand_graph_simple(self):
        testpath = pathlib.Path(self._test_data_usd)

        scene_file = "omniverse://kit-test-content.ov.nvidia.com/Projects/omni.mdl_tests/usd_converter/expand_graph/test.usd"
        materials = ['/World/Looks/OmniPBRBase']
        shaders = [
            '/World/Looks/OmniPBRBase/Shader',
            '/World/Looks/OmniPBRBase/clearcoat_geometry_normal',
            '/World/Looks/OmniPBRBase/geometry_normal'
        ]
        carb.log_info(scene_file)
        result = await self.base_expand_test(scene_file, materials, shaders)

        scene_file = str(testpath.joinpath("expand_graph").joinpath("test.usd"))
        carb.log_info(scene_file)
        result = await self.base_expand_test(scene_file, materials, shaders)

    async def test_expand_graph(self):
        testpath = pathlib.Path(self._test_data_usd)

        scene_file = "omniverse://kit-test-content.ov.nvidia.com/Projects/omni.mdl_tests/usd_converter/simple_bitmap/simple_bitmap.usda"
        materials = ['/World/Looks/Material__42']
        shaders = [
            '/World/Looks/Material__42/Shader',
            '/World/Looks/Material__42/Diffuse',
            '/World/Looks/Material__42/s',
            '/World/Looks/Material__42/texmap_bump',
            '/World/Looks/Material__42/texmap_coat_bump'
        ]
        carb.log_info(scene_file)
        result = await self.base_expand_test(scene_file, materials, shaders)

        scene_file = str(testpath.joinpath("simple_bitmap").joinpath("simple_bitmap.usda"))
        carb.log_info(scene_file)
        result = await self.base_expand_test(scene_file, materials, shaders)

        scene_file = "omniverse://kit-test-content.ov.nvidia.com/Projects/omni.mdl_tests/usd_converter/simple_tiny_multiple_outputs/simple_tiny.usda"
        materials = ['/World/Looks/Material__42']
        shaders = [
            '/World/Looks/Material__42/Shader',
            '/World/Looks/Material__42/Diffuse'
        ]
        carb.log_info(scene_file)
        result = await self.base_expand_test(scene_file, materials, shaders)

        scene_file = str(testpath.joinpath("simple_tiny_multiple_outputs").joinpath("simple_tiny.usda"))
        carb.log_info(scene_file)
        result = await self.base_expand_test(scene_file, materials, shaders)

        scene_file = "omniverse://kit-test-content.ov.nvidia.com/Projects/omni.mdl_tests/usd_converter/Collected_ONELILAC/ONELILAC.usda"
        materials = ['/World/Looks/Material__141', '/World/Looks/Material__167', '/World/Looks/Material__143', '/World/Looks/Material__35']
        shaders = [
            '/World/Looks/Material__141/UsdPreviewSurface',
            '/World/Looks/Material__141/Shader',
            '/World/Looks/Material__141/Diffuse',
            '/World/Looks/Material__141/s',
            '/World/Looks/Material__141/texmap_bump',
            '/World/Looks/Material__141/texmap_coat_bump',
            '/World/Looks/Material__167/Shader',
            '/World/Looks/Material__167/frontMtl',
            '/World/Looks/Material__167/Diffuse',
            '/World/Looks/Material__167/s',
            '/World/Looks/Material__167/color1',
            '/World/Looks/Material__167/color2',
            '/World/Looks/Material__167/Reflection',
            '/World/Looks/Material__167/x',
            '/World/Looks/Material__167/s0',
            '/World/Looks/Material__167/reflection_glossiness',
            '/World/Looks/Material__167/x1',
            '/World/Looks/Material__167/x2',
            '/World/Looks/Material__167/s3',
            '/World/Looks/Material__167/texmap_bump',
            '/World/Looks/Material__167/texmap_coat_bump',
            '/World/Looks/Material__167/backMtl',
            '/World/Looks/Material__167/Diffuse4',
            '/World/Looks/Material__167/s5',
            '/World/Looks/Material__167/color16',
            '/World/Looks/Material__167/color27',
            '/World/Looks/Material__167/Reflection8',
            '/World/Looks/Material__167/x9',
            '/World/Looks/Material__167/s10',
            '/World/Looks/Material__167/reflection_glossiness11',
            '/World/Looks/Material__167/x12',
            '/World/Looks/Material__167/x13',
            '/World/Looks/Material__167/s14',
            '/World/Looks/Material__167/texmap_bump15',
            '/World/Looks/Material__167/texmap_coat_bump16',
            '/World/Looks/Material__167/front_tint',
            '/World/Looks/Material__167/s17',
            '/World/Looks/Material__167/color118',
            '/World/Looks/Material__167/color219',
            '/World/Looks/Material__143/UsdPreviewSurface',
            '/World/Looks/Material__143/Shader',
            '/World/Looks/Material__143/frontMtl',
            '/World/Looks/Material__143/Diffuse',
            '/World/Looks/Material__143/s',
            '/World/Looks/Material__143/color1',
            '/World/Looks/Material__143/color2',
            '/World/Looks/Material__143/Reflection',
            '/World/Looks/Material__143/x',
            '/World/Looks/Material__143/s0',
            '/World/Looks/Material__143/reflection_glossiness',
            '/World/Looks/Material__143/x1',
            '/World/Looks/Material__143/x2',
            '/World/Looks/Material__143/s3',
            '/World/Looks/Material__143/texmap_bump',
            '/World/Looks/Material__143/texmap_coat_bump',
            '/World/Looks/Material__143/backMtl',
            '/World/Looks/Material__143/Diffuse4',
            '/World/Looks/Material__143/s5',
            '/World/Looks/Material__143/color16',
            '/World/Looks/Material__143/color27',
            '/World/Looks/Material__143/Reflection8',
            '/World/Looks/Material__143/x9',
            '/World/Looks/Material__143/s10',
            '/World/Looks/Material__143/reflection_glossiness11',
            '/World/Looks/Material__143/x12',
            '/World/Looks/Material__143/x13',
            '/World/Looks/Material__143/s14',
            '/World/Looks/Material__143/texmap_bump15',
            '/World/Looks/Material__143/texmap_coat_bump16',
            '/World/Looks/Material__143/front_tint',
            '/World/Looks/Material__143/s17',
            '/World/Looks/Material__143/color118',
            '/World/Looks/Material__143/color219',
            '/World/Looks/Material__35/Shader',
            '/World/Looks/Material__35/Diffuse',
            '/World/Looks/Material__35/s',
            '/World/Looks/Material__35/Reflection',
            '/World/Looks/Material__35/x',
            '/World/Looks/Material__35/s0',
            '/World/Looks/Material__35/reflection_glossiness',
            '/World/Looks/Material__35/x1',
            '/World/Looks/Material__35/x2',
            '/World/Looks/Material__35/s3',
            '/World/Looks/Material__35/texmap_bump',
            '/World/Looks/Material__35/texmap_coat_bump'
        ]
        carb.log_info(scene_file)
        result = await self.base_expand_test(scene_file, materials, shaders)

        # Same scene on disk
        # Same materials and shader outputs
        scene_file = str(testpath.joinpath("Collected_ONELILAC").joinpath("ONELILAC.usda"))
        carb.log_info(scene_file)
        simplify_after_expand : bool = False
        for simplify_after_expand in [False, True]:
            result = await self.base_expand_test(scene_file, materials, shaders, simplify_after_expand)
            self.assertTrue(result, 'Test failed')
