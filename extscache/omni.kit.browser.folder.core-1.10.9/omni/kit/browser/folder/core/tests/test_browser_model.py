from pathlib import Path

import carb.settings
import omni.kit.test

# Import extension python module we are testing with absolute import path, as if we are external user (other extension)
from ..models import TreeFolderBrowserModel

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")
ENV_ROOT_FOLDER = f"{TEST_DATA_PATH}/env_filter"
SETTING_ENV_ROOT = "/exts/omni.kit.browser.folder.core/test/env_root"
ROOT_FOLDER = f"{TEST_DATA_PATH}/root"
NEW_SUB_FOLDER = f"{ROOT_FOLDER}/new_sub"
NEW_ROOT_FOLDER = f"{TEST_DATA_PATH}/new_root"


# Having a test class derived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class TestTreeFolderBrowserModel(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        pass

    async def test_filter_folder(self):
        settings = carb.settings.get_settings()
        settings.set(SETTING_ENV_ROOT, [ENV_ROOT_FOLDER])
        browser_model = TreeFolderBrowserModel(
            setting_folders=SETTING_ENV_ROOT,
            ignore_folder_names=["*props*", "SubUSDs"],
        )
        for i in range(10):
            await omni.kit.app.get_app().next_update_async()

        folder = browser_model.get_root_folder(ENV_ROOT_FOLDER)
        await folder.start_traverse()
        collection_items = browser_model.get_item_children(None)
        category_items = browser_model.get_item_children(collection_items[0])
        detail_items = browser_model.get_item_children(category_items[0])
        self.assertEqual(len(detail_items), 1)
        self.assertEqual(detail_items[0].name, "b.usd")

        browser_model.destroy()
        browser_model = None

    async def test_refresh_category_only(self):
        """Test traverse folder without changes, only refresh category item to change load status"""
        settings = carb.settings.get_settings()
        setting_folders = "/persistent/exts/omni.kit.browser.folder.core.test/tree_folders"
        settings.set(setting_folders, [ROOT_FOLDER, NEW_ROOT_FOLDER])
        setting_folders_hide_in_category = "/exts/omni.kit.browser.folder.core/tree_folders_hide_in_category"
        settings.set(setting_folders_hide_in_category, ["new_root"])

        model = TreeFolderBrowserModel(
            setting_folders=setting_folders,
            setting_folders_hide_in_category=setting_folders_hide_in_category,
        )

        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        first_folder = model.get_root_folder(ROOT_FOLDER)
        model.start_traverse(first_folder)
        second_folder = model.get_root_folder(NEW_ROOT_FOLDER)
        model.start_traverse(second_folder)
        while not first_folder.prepared or not second_folder.prepared:
            await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # Generate category items
        collection_items = model.get_item_children(None)
        model.get_item_children(collection_items[0])

        changed_items = []
        # First _item_changed with loading=True and second with loading=False
        expected_loading_status = [True, False]
        expected_item_name = "root"
        def __on_item_changed(m, item):
            self.assertEqual(item.loading, expected_loading_status[len(changed_items)])
            self.assertEqual(item.name, expected_item_name)
            changed_items.append(item)

        sub = model.subscribe_item_changed_fn(__on_item_changed)
        # Traverse again, only refresh category items twice for loading status changed
        await self._traverse_folder(model, first_folder)
        self.assertEqual(len(changed_items), 2)

        changed_items = []
        expected_item_name = "new_root"
        # Traverse again, only refresh category items twice for loading status changed
        await self._traverse_folder(model, second_folder)
        self.assertEqual(len(changed_items), 2)

        sub = None
        model.destroy()

    async def test_custom_folder(self):
        settings = carb.settings.get_settings()
        setting_folders = "/persistent/exts/omni.kit.browser.folder.core.test/tree_folders"
        settings.set(setting_folders, [ROOT_FOLDER])
        setting_custom_folders = "/persistent/exts/omni.kit.browser.folder.core.test/custom_folders"
        settings.set(setting_custom_folders, [NEW_ROOT_FOLDER])

        model = TreeFolderBrowserModel(
            setting_folders=setting_folders,
            custom_folders_setting=setting_custom_folders,
        )

        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        collection_items = model.get_item_children(None)
        category_items = model.get_item_children(collection_items[0])
        self.assertEqual(len(category_items), 3)
        self.assertEqual(category_items[1].name, "new_root")
        self.assertEqual(category_items[2].name, "root")

        # Add a new custom folder
        settings.set(setting_custom_folders, [NEW_ROOT_FOLDER, ENV_ROOT_FOLDER])
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
        category_items = model.get_item_children(collection_items[0])
        self.assertEqual(len(category_items), 4)
        self.assertEqual(category_items[1].name, "env_filter")
        self.assertEqual(category_items[2].name, "new_root")
        self.assertEqual(category_items[3].name, "root")

        # Remove a custom folder
        settings.set(setting_custom_folders, [ENV_ROOT_FOLDER])
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
        category_items = model.get_item_children(collection_items[0])
        self.assertEqual(len(category_items), 3)
        self.assertEqual(category_items[1].name, "env_filter")
        self.assertEqual(category_items[2].name, "root")

    async def _traverse_folder(self, model: TreeFolderBrowserModel, folder) -> None:
        model.start_traverse(folder, force=True)
        await omni.kit.app.get_app().next_update_async()
        while not folder.prepared:
            await omni.kit.app.get_app().next_update_async()
