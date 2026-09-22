import carb
import omni.usd
import omni.kit.app
import omni.kit.test
from omni.kit import ui_test
from omni.kit.test_suite.helpers import get_test_data_path

class TestLibPaths(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_lib_paths(self):
        # get default settings
        master_mdl_list = await omni.kit.material.library.get_mdl_list_async()

        # add lib_paths
        omni.kit.material.library.add_to_mtl_lib([get_test_data_path(__name__, "mtl/")], is_private=True)

        # verify mdl_list has changed
        # NOTE: get_mdl_list_async will block until new material info has loaded
        mdl_list = await omni.kit.material.library.get_mdl_list_async()
        self.assertNotEqual(mdl_list, master_mdl_list)

        # remove lib path
        omni.kit.material.library.remove_from_mtl_lib([get_test_data_path(__name__, "mtl/")])

        # verify mdl_list has restored
        # NOTE: get_mdl_list_async will block until new material info has loaded
        mdl_list = await omni.kit.material.library.get_mdl_list_async()

        unique_items = {tuple(i) for i in master_mdl_list} ^ {tuple(i) for i in mdl_list}
        if unique_items:
            print(f"master_mdl_list:{master_mdl_list}")
            print(f"mdl_list:{mdl_list}")
            print(f"unique_items:{unique_items}")

        self.assertEqual(unique_items, set())

    async def test_usd_source_asset_list(self):
        # get the default list of registered USD Identifiers (from source asset)
        master_entries: list = omni.kit.material.library.get_mdl_usd_source_asset_list()
        master_length = len(master_entries)

        # add a top level entry into a new group
        success: bool = omni.kit.material.library.add_usd_source_asset_path_to_mtl_lib(
            source_asset_path="nvidia/core_definitions.mdl",
            source_asset_subid="scratched_metal_v2",
            group_name="Core Definitions",
            display_name="Metal")
        self.assertTrue(success, "Adding Metal from nvidia/core_definitions failed")
        # add a submenu entry into the same group
        success = omni.kit.material.library.add_usd_source_asset_path_to_mtl_lib(
            source_asset_path="nvidia/core_definitions.mdl",
            source_asset_subid="scratched_plastic_v2",
            group_name="Core Definitions",
            submenu_name="Submenu Test",
            display_name="Plastic")
        self.assertTrue(success, "Adding Metal from nvidia/core_definitions failed")
        # add an entry to an existing group
        success = omni.kit.material.library.add_usd_source_asset_path_to_mtl_lib(
            source_asset_path="nvidia/core_definitions.mdl",
            source_asset_subid="flex_material_v2",
            group_name="Base",
            display_name="Flex Material")
        self.assertTrue(success, "Adding Flex Material from nvidia/core_definitions failed")
        # check list size
        updated_entries: list = omni.kit.material.library.get_mdl_usd_source_asset_list()
        updated_length = len(updated_entries)
        self.assertEqual(updated_length, master_length + 3)

        # remove one entry
        success = omni.kit.material.library.remove_usd_source_asset_path_from_mtl_lib(
            source_asset_path="nvidia/core_definitions.mdl",
            source_asset_subid="scratched_metal_v2")
        self.assertTrue(success, "Removing Metal from nvidia/core_definitions failed")
        updated_entries2: list = omni.kit.material.library.get_mdl_usd_source_asset_list()
        updated_length2 = len(updated_entries2)
        self.assertEqual(updated_length2, master_length + 2)
