from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import open_stage, wait_stage_loading

from .utils import *
import omni.mdl.neuraylib   # interface the OV material backend
import omni.mdl.pymdlsdk    # low-level MDL python binding that matches the native SDK
import omni.mdl.pymdl       # high-level wrapper
import pxr
import omni.client

class UsdResolutionTest(AsyncTestCase):

    # Before running each test
    async def setUp(self):
        # pxr.Tf.Debug.SetDebugSymbolsByName("OMNI_USD_RESOLVER", True)
        # pxr.Tf.Debug.SetDebugSymbolsByName("OMNI_USD_RESOLVER_MDL", True)
        pass

    # After running each test
    async def tearDown(self):
        await closeStage()

    # ----------------------------------------------------------------------------------------------
    # Test Cases
    # ----------------------------------------------------------------------------------------------

    # check the search path setup
    async def test_search_path_setup(self):
        await open_stage(get_usd_scene_path('usd_resolution/global_core_defs.usda'))
        await wait_stage_loading()

        # make sure the test content is not inside a search path
        search_paths: list[str] = omni.client.get_default_search_paths()
        listing: str = "Client Library Search Paths:\n"
        for sp in search_paths:
            listing += f"   {sp}\n"
        carb.log_info(listing)
        for sp in search_paths:
            self.assertFalse('/omni.mdl.neuraylib/data/tests/' in sp)

        # check the base url
        base_url: str = omni.client.get_base_url()
        carb.log_info(f"Client Library Base Url: {base_url}")

    # address a local module using a weak relative path in USD
    # the module should be found but after looking through the search paths
    # this is the inefficient way which should be identified by the validator
    async def test_weak_relative(self):
        # open a simple scene with a mesh and a material assigned
        await open_stage(get_usd_scene_path('usd_resolution/weak_relative.usda'))
        await wait_stage_loading()
        ov_neuraylib = omni.mdl.neuraylib.get_neuraylib()
        ov_entity = ov_neuraylib.createMdlEntity("/World/Looks/Material/Shader")
        # if the entity and its module is valid a matching module has been found, can not tell how efficient here
        self.assertIsNotNone(ov_entity)
        self.assertTrue(ov_entity.valid())
        ov_module = ov_entity.getMdlModule()
        self.assertIsNotNone(ov_module)
        self.assertTrue(ov_module.valid())
        carb.log_info(f"Qualified Name: {ov_module.qualifiedName}")
        ov_neuraylib.destroyMdlEntity(ov_entity)

    # address a local module using a strict relative path in USD
    # the module should be anchored to stage without any looking through the search paths
    # this is the most efficient way to reference a local resource
    async def test_strict_relative(self):
        # open a simple scene with a mesh and a material assigned
        await open_stage(get_usd_scene_path('usd_resolution/strict_relative.usda'))
        await wait_stage_loading()
        ov_neuraylib = omni.mdl.neuraylib.get_neuraylib()
        ov_entity = ov_neuraylib.createMdlEntity("/World/Looks/Material/Shader")
        # if the entity and its module is valid a matching module has been found, can not tell how efficient here
        self.assertIsNotNone(ov_entity)
        self.assertTrue(ov_entity.valid())
        ov_module = ov_entity.getMdlModule()
        self.assertIsNotNone(ov_module)
        self.assertTrue(ov_module.valid())
        carb.log_info(f"Qualified Name: {ov_module.qualifiedName}")
        ov_neuraylib.destroyMdlEntity(ov_entity)

    # address a local module using a strict relative path in USD
    # the module does not exist locally but it does exist in a search path
    # resolution needs to fail because we explicitly address local content
    async def test_strict_relative_missing(self):
        # open a simple scene with a mesh and a material assigned
        await open_stage(get_usd_scene_path('usd_resolution/strict_relative_missing.usda'))
        await wait_stage_loading()
        ov_neuraylib = omni.mdl.neuraylib.get_neuraylib()
        ov_entity = ov_neuraylib.createMdlEntity("/World/Looks/Material/ShaderMissingModule")
        self.assertIsNotNone(ov_entity)
        self.assertFalse(ov_entity.valid())  # invalid because module is missing
        ov_module = ov_entity.getMdlModule()
        self.assertIsNone(ov_module)  # module is None
        ov_neuraylib.destroyMdlEntity(ov_entity)

    # in USD we reference a an MDL module `nvidia/core_definitions.mdl` (global)
    # need to resolve to the core_definition module in the search path and NOT to the local module
    async def test_global_core_defs(self):
        # open a simple scene with a mesh and a material assigned
        await open_stage(get_usd_scene_path('usd_resolution/global_core_defs.usda'))
        await wait_stage_loading()
        ov_neuraylib = omni.mdl.neuraylib.get_neuraylib()
        ov_entity = ov_neuraylib.createMdlEntity("/World/Looks/Material/Shader")
        self.assertIsNotNone(ov_entity)
        self.assertTrue(ov_entity.valid())
        ov_module = ov_entity.getMdlModule()
        self.assertIsNotNone(ov_module)
        self.assertTrue(ov_module.valid())
        carb.log_info(f"Qualified Name: {ov_module.qualifiedName}")
        # check if the module qualifier contains the test folder, in that case, it's the copy and wrong
        self.assertFalse('::data::tests::usd::usd_resolution::' in ov_module.qualifiedName)  # no local path
        ov_neuraylib.destroyMdlEntity(ov_entity)

    # in USD we reference a an MDL module `./nvidia/core_definitions.mdl`
    # need to resolve to the local core_definition module and NOT in the search path
    async def test_shadow_searchpath_module_local(self):
        # open a simple scene with a mesh and a material assigned
        await open_stage(get_usd_scene_path('usd_resolution/local_core_defs.usda'))
        await wait_stage_loading()
        ov_neuraylib = omni.mdl.neuraylib.get_neuraylib()
        ov_entity = ov_neuraylib.createMdlEntity("/World/Looks/Material/Shader")
        self.assertIsNotNone(ov_entity)
        self.assertTrue(ov_entity.valid())
        ov_module = ov_entity.getMdlModule()
        self.assertIsNotNone(ov_module)
        self.assertTrue(ov_module.valid())
        carb.log_info(f"Qualified Name: {ov_module.qualifiedName}")
        # check if the module qualifier contains the test folder, in that case, it's the copy and right
        self.assertTrue('::data::tests::usd::usd_resolution::' in ov_module.qualifiedName)  # a local path
        ov_neuraylib.destroyMdlEntity(ov_entity)
