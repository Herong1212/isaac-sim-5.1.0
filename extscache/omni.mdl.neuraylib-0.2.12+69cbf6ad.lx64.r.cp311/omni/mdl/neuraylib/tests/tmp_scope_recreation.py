from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test import get_test_output_path

import os
import uuid
import shutil
from .utils import *

from omni.kit.test_suite.helpers import open_stage, wait_stage_loading

import omni.mdl.pymdlsdk as pymdlsdk
import omni.mdl.neuraylib
class TmpScopeTest(AsyncTestCase):

    # ----------------------------------------------------------------------------------------------
    # Test Cases
    # ----------------------------------------------------------------------------------------------

    # test if the database scope name can be determined correctly depending the active renderer
    def test_create_and_destroy_temporary_scope(self):
        name: str = omni.mdl.neuraylib.create_temporary_db_scope(resolveResources=True)
        log_info(f"Created scope: '{name}'")
        self.assertNotEqual(name, "")
        deleted: bool = omni.mdl.neuraylib.destroy_temporary_db_scope(name)
        log_info(f"Deleted scope: '{name}' successfully: {deleted}")
        self.assertTrue(deleted)
        deleted = omni.mdl.neuraylib.destroy_temporary_db_scope(name)
        self.assertFalse(deleted)  # already deleted
        deleted = omni.mdl.neuraylib.destroy_temporary_db_scope(name + "XYZ")
        self.assertFalse(deleted)  # never existed
        deleted = omni.mdl.neuraylib.destroy_temporary_db_scope("rtx_scope0")
        self.assertFalse(deleted)  # not a temporary scope (only naming convention)

    async def exportMdl(self, neuray: pymdlsdk.INeuray, transaction: pymdlsdk.ITransaction, instance: pymdlsdk.IMaterial_instance, filename: str):
        mdlFactory: pymdlsdk.IMdl_factory = neuray.get_api_component(pymdlsdk.IMdl_factory)
        context: pymdlsdk.IMdl_execution_context = mdlFactory.create_execution_context()

        moduleName: str = f"mdl::new_module_{str(uuid.uuid4()).replace('-', '_')}"
        moduleBuilder: pymdlsdk.IMdl_module_builder = mdlFactory.create_module_builder(transaction, moduleName, pymdlsdk.Mdl_version.MDL_VERSION_1_6, pymdlsdk.Mdl_version.MDL_VERSION_LATEST, context)
        ef: pymdlsdk.IExpression_factory = mdlFactory.create_expression_factory(transaction)
        emptyAnnoBlock: pymdlsdk.IAnnotation_block = ef.create_annotation_block()
        call: pymdlsdk.IFunction_call = instance.get_interface(pymdlsdk.IFunction_call)
        moduleBuilder.clear_module(context)
        result = moduleBuilder.add_variant(
            "Main",
            call.get_function_definition(),
            call.get_arguments(),
            emptyAnnoBlock,
            emptyAnnoBlock,
            True,
            context)
        if result != 0:
            carb.log_error("Error: Failed to add variant to module builder")
            for i in range(context.get_messages_count()):
                carb.log_error(context.get_message(i).get_string())
            return False

        impExpApi: pymdlsdk.IMdl_impexp_api = neuray.get_api_component(pymdlsdk.IMdl_impexp_api)
        context.set_option("bundle_resources", True)
        result = impExpApi.export_module(transaction, moduleName, filename, context)
        if result < 0:
            carb.log_error("Error: Failed to export module")
            return False
        return True


    async def recreate_material(self, scene: str, materialRootPrimPath: str = '/World/Looks/Material/Shader', expected_resource_count_original: int = 0, expected_resource_count_receated: int = 0, expected_module_count: int = 0, report_missing_resources: bool = False):
        sceneFilePath: str = get_usd_scene_path(scene)
        log_info(f"Loading test scene started: {sceneFilePath}")
        await open_stage(sceneFilePath)
        await wait_stage_loading()
        log_info(f"Loading test scene complete: {sceneFilePath}")

        ov_neuraylib = omni.mdl.neuraylib.get_neuraylib()

        # access the material in the renderer context
        ov_entity = ov_neuraylib.createMdlEntity(materialRootPrimPath)
        ov_entity_snapshot = ov_neuraylib.createMdlEntitySnapshot(ov_entity)
        self.assertIsNotNone(ov_entity_snapshot)

        # create a temporary scope
        log_info(f"Recreate Material in temporary scope: {materialRootPrimPath}")
        tmpDbScopeName: str = omni.mdl.neuraylib.create_temporary_db_scope(resolveResources=True)
        self.assertNotEqual(tmpDbScopeName, "")
        log_info(f"Source Scope: {ov_entity_snapshot.dbScopeName}")
        log_info(f"Temporary Scope: {tmpDbScopeName}")
        # recreate the material in that temp scope
        tmpMaterialDbName: str = omni.mdl.neuraylib.recreate_material_in_scope(ov_entity_snapshot, tmpDbScopeName)
        self.assertNotEqual(tmpMaterialDbName, "")

        # test if the material are equal by just compiling and compairing the hashes
        log_info(f"Compare recreated against original material: {materialRootPrimPath}")
        srcTransaction: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(ov_neuraylib.createReadingTransaction(ov_entity_snapshot.dbScopeName))
        srcMaterialInstance: pymdlsdk.IMaterial_instance = srcTransaction.access_as(pymdlsdk.IMaterial_instance, ov_entity_snapshot.dbName)
        self.assertTrue(srcMaterialInstance.is_valid_interface())
        srcCompiledMaterialInstance: pymdlsdk.ICompiled_material = srcMaterialInstance.create_compiled_material(0)
        srcCompiledMaterialClass: pymdlsdk.ICompiled_material = srcMaterialInstance.create_compiled_material(1)
        self.assertTrue(srcCompiledMaterialInstance.is_valid_interface())
        self.assertTrue(srcCompiledMaterialClass.is_valid_interface())

        tmpTransaction: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(ov_neuraylib.createEditingTransaction(tmpDbScopeName))
        tmpMaterialInstance: pymdlsdk.IMaterial_instance = tmpTransaction.edit_as(pymdlsdk.IMaterial_instance, tmpMaterialDbName)
        self.assertTrue(tmpMaterialInstance.is_valid_interface())
        tmpCompiledMaterialInstance: pymdlsdk.ICompiled_material = tmpMaterialInstance.create_compiled_material(0)
        tmpCompiledMaterialClass: pymdlsdk.ICompiled_material = tmpMaterialInstance.create_compiled_material(1)
        self.assertTrue(tmpCompiledMaterialInstance.is_valid_interface())
        self.assertTrue(tmpCompiledMaterialClass.is_valid_interface())

        log_info(f"Instance Hash Original:  {str(srcCompiledMaterialInstance.get_hash())}")
        log_info(f"Instance Hash Recreated: {str(tmpCompiledMaterialInstance.get_hash())}")
        log_info(f"Class Hash Original:  {str(srcCompiledMaterialClass.get_hash())}")
        log_info(f"Class Hash Recreated: {str(tmpCompiledMaterialClass.get_hash())}")

        srcResourceUris: list[str] = omni.mdl.neuraylib.get_graph_resources_uri_masks(srcTransaction, ov_entity_snapshot.dbName, report_missing_resources)
        log_info("Resource URI masks Original: \n - " +'\n - '.join(srcResourceUris))
        tmpResourceUris: list[str] = omni.mdl.neuraylib.get_graph_resources_uri_masks(tmpTransaction, tmpMaterialDbName, report_missing_resources)
        log_info("Resource URI masks Recreated: \n - " +'\n - '.join(tmpResourceUris))

        srcResourceUris: list[str] = omni.mdl.neuraylib.get_graph_resources_uris(srcTransaction, ov_entity_snapshot.dbName, report_missing_resources)
        log_info("Resource URIs Original: \n - " +'\n - '.join(srcResourceUris))
        tmpResourceUris: list[str] = omni.mdl.neuraylib.get_graph_resources_uris(tmpTransaction, tmpMaterialDbName, report_missing_resources)
        log_info("Resource URIs Recreated: \n - " +'\n - '.join(tmpResourceUris))
        self.assertEqual(len(srcResourceUris), expected_resource_count_original)
        self.assertEqual(len(tmpResourceUris), expected_resource_count_receated)

        srcModuleUris: list[str] = omni.mdl.neuraylib.get_module_uris(srcTransaction, ov_entity_snapshot.dbName)
        log_info("Modules Original: \n - " +'\n - '.join(srcModuleUris))
        tmpModuleUris: list[str] = omni.mdl.neuraylib.get_module_uris(tmpTransaction, tmpMaterialDbName)
        log_info("Modules Recreated: \n - " +'\n - '.join(tmpModuleUris))
        self.assertEqual(len(srcModuleUris), expected_module_count)
        self.assertEqual(len(tmpModuleUris), expected_module_count)

        neuray: pymdlsdk.INeuray = pymdlsdk.attach_ineuray(ov_neuraylib.getNeurayAPI())
        sceneName: str = os.path.splitext(os.path.basename(scene))[0]
        output_dir: str = os.path.join(get_test_output_path(), sceneName)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        await self.exportMdl(neuray, tmpTransaction, tmpMaterialInstance, os.path.join(output_dir, sceneName + ".mdl"))

        # clean up
        srcMaterialInstance = None
        srcCompiledMaterialInstance = None
        srcCompiledMaterialClass = None
        tmpMaterialInstance = None
        tmpCompiledMaterialInstance = None
        tmpCompiledMaterialClass = None

        srcTransaction.abort()
        tmpTransaction.abort()
        ov_neuraylib.destroyMdlEntitySnapshot(ov_entity_snapshot)
        ov_neuraylib.destroyMdlEntity(ov_entity)
        await closeStage()

        # delete the temporary scope
        deleted: bool = omni.mdl.neuraylib.destroy_temporary_db_scope(tmpDbScopeName)
        self.assertTrue(deleted)

    async def test_recreate_material_simple(self):
        await self.recreate_material(
            scene = 'basic.usda',
            materialRootPrimPath = '/World/Looks/OmniSurfaceLite/Shader',
            expected_resource_count_original = 0,
            expected_resource_count_receated = 0,
            expected_module_count = 6)

    async def test_recreate_material_texture_usd_valid(self):
        await self.recreate_material(
            scene = 'interop/TexturesMDL/textures-Usd-Valid.usda',
            expected_resource_count_original = 5,
            expected_resource_count_receated = 5,
            expected_module_count = 1)

    async def test_recreate_material_texture_default(self):
        await self.recreate_material(scene = 'interop/TexturesMDL/textures-Mdl-1-6-ParamRelativeExisting.usda',
            expected_resource_count_original = 4,
            expected_resource_count_receated = 4,
            expected_module_count = 1)

    async def test_recreate_material_texture_body(self):
        await self.recreate_material(scene = 'interop/TexturesMDL/textures-Mdl-1-6-BodyRelativeExisting.usda',
            expected_resource_count_original = 4,
            expected_resource_count_receated = 4,
            expected_module_count = 1)

    async def test_recreate_material_texture_body_incl_missing(self):
        await self.recreate_material(scene = 'interop/TexturesMDL/textures-Mdl-1-6-BodyRelativeExisting.usda',
            expected_resource_count_original = 6,
            expected_resource_count_receated = 6,
            expected_module_count = 1,
            report_missing_resources = True)

    async def test_recreate_material_texture_default_udim(self):
        await self.recreate_material(scene = 'interop/TexturesMDL/Udim/Udim_param.usda',
            expected_resource_count_original = 3,
            expected_resource_count_receated = 3,
            expected_module_count = 1)

    async def test_recreate_material_texture_body_udim(self):
        await self.recreate_material(scene = 'interop/TexturesMDL/Udim/Udim_body.usda',
            expected_resource_count_original = 3,
            expected_resource_count_receated = 3,
            expected_module_count = 1)

    async def test_recreate_material_lp_default(self):
        await self.recreate_material(scene = 'interop/LightProfiles/example_lp.usda',
            expected_resource_count_original = 1,
            expected_resource_count_receated = 1,
            expected_module_count = 1)

    async def test_recreate_material_mbsdf_body(self):
        await self.recreate_material(scene = 'interop/BsdfMeasurements/example_mbsdf.usda',
            expected_resource_count_original = 1,
            expected_resource_count_receated = 1,
            expected_module_count = 1)

    async def test_recreate_material_deep_hierarchy(self):
        await self.recreate_material(scene = 'interop/DeepHierarchy/Dependencies.usda',
            expected_resource_count_original = 2,
            expected_resource_count_receated = 2,
            expected_module_count = 4)

    async def test_load_module_to_temp_scope(self):
        scope_name = omni.mdl.neuraylib.create_temporary_db_scope(resolveResources=True)
        neuraylib = omni.mdl.neuraylib.get_neuraylib()
        mdl_module = neuraylib.createMdlModule("OmniPBR.mdl", scope_name)
        self.assertTrue(mdl_module.valid())
        neuraylib.destroyMdlModule(mdl_module)
        self.assertTrue(omni.mdl.neuraylib.destroy_temporary_db_scope(scope_name))

    async def test_inlined_resources(self):
        moduleFilePath: str = get_usd_scene_path('interop/DeepHierarchy/materials/A.mdl')
        moduleFilePath = make_uri_with_scheme(moduleFilePath)
        log_info(f"\n\nLoading MDL: {moduleFilePath}")

        ov_neuraylib = omni.mdl.neuraylib.get_neuraylib()
        tmpDbScopeName: str = omni.mdl.neuraylib.create_temporary_db_scope(resolveResources=True)
        ov_mdl_module = ov_neuraylib.createMdlModule(moduleFilePath, tmpDbScopeName)

        srcTransaction: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(
            ov_neuraylib.createReadingTransaction(tmpDbScopeName))

        def list_module_resources(module, resourcesFound):
            for i in range(module.get_resources_count()):
                resource: pymdlsdk.IValue_resource = module.get_resource(i)
                resourcesFound.append(resource.get_file_path())
            for i in range(module.get_import_count()):
                import_module: pymdlsdk.IModule = srcTransaction.access_as(pymdlsdk.IModule, module.get_import(i))
                list_module_resources(import_module, resourcesFound)
                import_module = None

        mdl_module: pymdlsdk.IModule = srcTransaction.access_as(pymdlsdk.IModule, ov_mdl_module.dbName)
        resourcesFound: list[str] = []
        list_module_resources(mdl_module, resourcesFound)
        for r in resourcesFound:
            log_info(f"Resource found: {r}")
        self.assertEqual(len(resourcesFound), 3)
        mdl_module = None

        srcTransaction.abort()
        ov_neuraylib.destroyMdlModule(ov_mdl_module)
        omni.mdl.neuraylib.destroy_temporary_db_scope(tmpDbScopeName)

    async def test_resource_identifier(self):
        identifier: str = "mdl::file:/E:/gitlab/kit/Texture.png_texture_auto"
        uri, colorspace, gamma = omni.mdl.neuraylib.parse_scene_identifier_texture(identifier)
        self.assertEqual(uri, "file:/E:/gitlab/kit/Texture.png")
        self.assertEqual(colorspace, "auto")
        self.assertEqual(gamma, 0.0)
        identifier = "mdl::omniverse://ov-content.nvidia.com/examples/Texture.png_texture_sRGB"
        uri, colorspace, gamma = omni.mdl.neuraylib.parse_scene_identifier_texture(identifier)
        self.assertEqual(uri, "omniverse://ov-content.nvidia.com/examples/Texture.png")
        self.assertEqual(colorspace, "sRGB")
        self.assertEqual(gamma, 2.2)
        identifier = "mdl::omniverse://ov-content.nvidia.com/examples/Texture.png_texture_raw"
        uri, colorspace, gamma = omni.mdl.neuraylib.parse_scene_identifier_texture(identifier)
        self.assertEqual(uri, "omniverse://ov-content.nvidia.com/examples/Texture.png")
        self.assertEqual(colorspace, "raw")
        self.assertEqual(gamma, 1.0)
        identifier: str = "mdl::file:/E:/gitlab/kit/LightProfile.ies_lp"
        uri = omni.mdl.neuraylib.parse_scene_identifier_light_profile(identifier)
        self.assertEqual(uri, "file:/E:/gitlab/kit/LightProfile.ies")
        identifier: str = "mdl::file:/E:/gitlab/kit/BsdfMeasurement.mbsdf_mbsdf"
        uri = omni.mdl.neuraylib.parse_scene_identifier_bsdf_measurement(identifier)
        self.assertEqual(uri, "file:/E:/gitlab/kit/BsdfMeasurement.mbsdf")

        identifier: str = "mdl::file:/E:/gitlab/kit/Texture.png_texture_invalidColorSpace"
        uri, colorspace, gamma = omni.mdl.neuraylib.parse_scene_identifier_texture(identifier)
        self.assertIsNone(uri)
        self.assertIsNone(colorspace)
        self.assertIsNone(gamma)
