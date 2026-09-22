from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import open_stage, wait_stage_loading

from .utils import *
import omni.mdl.neuraylib   # interface the OV material backend
import omni.mdl.pymdlsdk    # low-level MDL python binding that matches the native SDK
import omni.mdl.pymdl       # high-level wrapper

class StructureTest(AsyncTestCase):

    # Before running each test
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()
        stage.SetDefaultPrim(stage.DefinePrim("/World"))
        await wait_stage_loading()

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()
        await omni.usd.get_context().close_stage_async()
        await wait_stage_loading()

    # ----------------------------------------------------------------------------------------------
    # Test Cases
    # ----------------------------------------------------------------------------------------------

    # access the MDL representation of a USD shade node when a scene is loaded
    async def test_inspect_mdl_entities(self):
        # open a simple scene with a mesh and a material assigned
        await open_stage(get_usd_scene_path('structures/structure_tests.usda'))
        await wait_stage_loading()

        # acquire neuray instance from OV
        ov_neuraylib = omni.mdl.neuraylib.get_neuraylib()
        ov_neuraylib_handle = ov_neuraylib.getNeurayAPI()

        # feed the neuray instance into the python binding
        neuray: omni.mdl.pymdlsdk.INeuray = omni.mdl.pymdlsdk.attach_ineuray(ov_neuraylib_handle)
        self.assertIsNotNone(neuray)

        # at this point we assume that if all MDL nodes are present in rtx.hydra, we have a valid connected graph
        shaderNodeList: list[str] = [
            "/World/Looks/extract_mat/main_indirect",
            "/World/Looks/extract_mat/extract",
            "/World/Looks/extract_mat/lookup",

            "/World/Looks/defaults_mat/main_defaults",
            "/World/Looks/defaults_mat/lookup",

            "/World/Looks/complex_construct_mat/main_indirect",
            "/World/Looks/complex_construct_mat/lookup",
            "/World/Looks/complex_construct_mat/construct_color",
            "/World/Looks/complex_construct_mat/checker_texture",

            "/World/Looks/complex_construct_2_mat/main_indirect",
            "/World/Looks/complex_construct_2_mat/lookup",
            # "/World/Looks/complex_construct_2_mat/checker_texture",  # not working at the moment because output ports in usd are not written
        ]

        # iterate over all nodes and check for valid snapshots
        for path in shaderNodeList:
            log_text: str = f"prim path: '{path}'"
            print(f"processing 'structure_tests.usda' {log_text}")

            # access a USD shader nodes MDL representation
            ov_entity = ov_neuraylib.createMdlEntity(path) # using the default scope name
            self.assertIsNotNone(ov_entity, log_text)
            self.assertTrue(ov_entity.valid(), log_text) # scene is loaded, material should be valid

            # create a snapshot from the entity
            ov_entity_snapshot = ov_neuraylib.createMdlEntitySnapshot(ov_entity)
            self.assertIsNotNone(ov_entity_snapshot, log_text)
            self.assertFalse(ov_entity_snapshot.dbName == "", log_text)

            # release created objects
            ov_neuraylib.destroyMdlEntitySnapshot(ov_entity_snapshot)
            ov_neuraylib.destroyMdlEntity(ov_entity)
