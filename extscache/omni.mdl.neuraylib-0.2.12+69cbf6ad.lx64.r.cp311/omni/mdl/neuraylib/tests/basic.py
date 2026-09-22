from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import open_stage, wait_stage_loading

from .utils import *
import omni.mdl.neuraylib   # interface the OV material backend
import omni.mdl.pymdlsdk    # low-level MDL python binding that matches the native SDK
import omni.mdl.pymdl       # high-level wrapper


class EntityTest(AsyncTestCase):

    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        await closeStage()

    # ----------------------------------------------------------------------------------------------
    # Test Cases
    # ----------------------------------------------------------------------------------------------

    # test if the database scope name can be determined correctly depending the active renderer
    async def test_default_scope_name(self):
        await openNewStage()
        # acquire neuray instance from OV
        ov_neuraylib = omni.mdl.neuraylib.get_neuraylib()
        scope_name:str = ov_neuraylib.getCurrentDefaultScope()
        print(f"Default Neuray DB Scope of the active renderer: {scope_name}")

        if isRendererRtx():
            self.assertEqual(scope_name, "rtx_scope0")

        if isRendererIray():
            self.assertEqual(scope_name, "iray_scope")

    # access the MDL representation of a USD shade node when a scene is loaded
    async def test_inspect_mdl_entity(self):
        # open a simple scene with a mesh and a material assigned
        await open_stage(get_usd_scene_path('basic.usda'))
        await wait_stage_loading()

        # acquire neuray instance from OV
        ov_neuraylib = omni.mdl.neuraylib.get_neuraylib()
        ov_neuraylib_handle = ov_neuraylib.getNeurayAPI()

        # feed the neuray instance into the python binding
        neuray: omni.mdl.pymdlsdk.INeuray = omni.mdl.pymdlsdk.attach_ineuray(ov_neuraylib_handle)
        self.assertIsNotNone(neuray)

        # create a standard module
        # test if we can access the module from it's DB name
        ov_df_module = ov_neuraylib.createMdlModule("df.mdl")
        self.assertIsNotNone(ov_df_module)
        self.assertTrue(ov_df_module.valid())
        self.assertEqual(ov_df_module.qualifiedName, "::df")  # NOSONAR - This is not part of a IP address
        ov_neuraylib.destroyMdlModule(ov_df_module)
        print("Create standard module passed")

        # access a USD shader nodes MDL representation
        usd_prim_path:str = "/World/Looks/OmniSurfaceLite/Shader"
        ov_entity = ov_neuraylib.createMdlEntity(usd_prim_path) # using the default scope name
        self.assertIsNotNone(ov_entity)
        self.assertTrue(ov_entity.valid()) # scene is loaded, material should be valid

        # check if the default scope name was used correctly
        if isRendererRtx():
            self.assertEqual(ov_entity.dbScopeName, "rtx_scope0")

        if isRendererIray():
            self.assertEqual(ov_entity.dbScopeName, "iray_scope")

        # get the module from the entity
        ov_module = ov_entity.getMdlModule()
        self.assertIsNotNone(ov_module)
        self.assertTrue(ov_module.valid())

        # test if we can access the module from it's DB name
        ov_module2 = ov_neuraylib.createMdlModuleFromDbName(ov_module.dbName)
        self.assertIsNotNone(ov_module2)
        self.assertTrue(ov_module2.valid())
        ov_neuraylib.destroyMdlModule(ov_module2)
        print("Create module from db Name passed")

        # create a snapshot from the entity
        ov_entity_snapshot = ov_neuraylib.createMdlEntitySnapshot(ov_entity)
        self.assertIsNotNone(ov_entity_snapshot)

         # scopename of module, entity and snapshot are equal
        self.assertEqual(ov_entity_snapshot.dbScopeName, ov_module.dbScopeName)
        self.assertEqual(ov_entity.dbScopeName, ov_module.dbScopeName)

        # print some information
        # TODO make this test cases eventually
        print(f"MdlEntity:")
        print(f"  uniquePrimPath: {ov_entity.uniquePrimPath}")
        print(f"  dbScopeName: {ov_entity.dbScopeName}")
        print(f"  valid: {ov_entity.valid()}")
        print(f"  simpleNameWithSignature: {ov_entity.simpleNameWithSignature}")
        print(f"  module:")
        print(f"    valid: {ov_module.valid()}")
        print(f"    dbScopeName: {ov_module.dbScopeName}")
        print(f"    dbName: {ov_module.dbName}")
        print(f"    qualifiedName: {ov_module.qualifiedName}")
        print(f"MdlEntitySnapshot:")
        print(f"    dbScopeName: {ov_entity_snapshot.dbScopeName}")
        print(f"    dbName: {ov_entity_snapshot.dbName}")

        # release created objects
        ov_neuraylib.destroyMdlEntitySnapshot(ov_entity_snapshot)
        ov_neuraylib.destroyMdlEntity(ov_entity)
