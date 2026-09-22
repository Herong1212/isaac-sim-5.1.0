import carb
import omni
import omni.kit.test
import omni.usd
import omni.client
import omni.kit.widget.stage
import omni.kit.app
import omni.kit.ui_test as ui_test

from omni.kit.test_suite.helpers import arrange_windows
from ..stage_model import StageItemSortPolicy



class TestHeader(omni.kit.test.AsyncTestCase):

    async def setUp(self):
        self.app = omni.kit.app.get_app()
        await arrange_windows("Stage", 800, 600)

    async def tearDown(self):
        pass

    async def wait(self, frames=4):
        for i in range(frames):
            await self.app.next_update_async()

    async def test_name_header(self):
        stage_tree = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        self.assertTrue(stage_tree)
        stage_model = stage_tree.widget.model
        stage_model.set_items_sort_policy(StageItemSortPolicy.DEFAULT)
        name_label = stage_tree.find("**/Label[*].text=='Name (Old to New)'")
        self.assertTrue(name_label)

        await name_label.click()
        await self.wait()
        name_label = stage_tree.find("**/Label[*].text=='Name (A to Z)'")
        self.assertTrue(name_label)

        await name_label.click()
        await self.wait()
        name_label = stage_tree.find("**/Label[*].text=='Name (Z to A)'")
        self.assertTrue(name_label)

        await name_label.click()
        await self.wait()
        name_label = stage_tree.find("**/Label[*].text=='Name (New to Old)'")
        self.assertTrue(name_label)

        await name_label.click()
        await self.wait()
        name_label = stage_tree.find("**/Label[*].text=='Name (Old to New)'")
        self.assertTrue(name_label)

    async def test_visibility_header(self):
        stage_tree = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        self.assertTrue(stage_tree)
        stage_model = stage_tree.widget.model
        stage_model.set_items_sort_policy(StageItemSortPolicy.DEFAULT)
        self.assertEqual(stage_model.get_items_sort_policy(), StageItemSortPolicy.DEFAULT)

        visibility_image = stage_tree.find("**/Image[*].name=='visibility_header'")
        self.assertTrue(visibility_image)
        await visibility_image.click()
        await self.wait()
        self.assertEqual(stage_model.get_items_sort_policy(), StageItemSortPolicy.VISIBILITY_COLUMN_VISIBLE_TO_INVISIBLE)

        await visibility_image.click()
        await self.wait()
        self.assertEqual(stage_model.get_items_sort_policy(), StageItemSortPolicy.VISIBILITY_COLUMN_INVISIBLE_TO_VISIBLE)

        await visibility_image.click()
        await self.wait()
        self.assertEqual(stage_model.get_items_sort_policy(), StageItemSortPolicy.DEFAULT)

    async def test_type_header(self):
        stage_tree = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        self.assertTrue(stage_tree)
        stage_model = stage_tree.widget.model
        stage_model.set_items_sort_policy(StageItemSortPolicy.DEFAULT)
        self.assertEqual(stage_model.get_items_sort_policy(), StageItemSortPolicy.DEFAULT)

        type_label = stage_tree.find("**/Label[*].text=='Type'")
        self.assertTrue(type_label)
        await type_label.click()
        await self.wait()
        self.assertEqual(stage_model.get_items_sort_policy(), StageItemSortPolicy.TYPE_COLUMN_A_TO_Z)

        await type_label.click()
        await self.wait()
        self.assertEqual(stage_model.get_items_sort_policy(), StageItemSortPolicy.TYPE_COLUMN_Z_TO_A)

        await type_label.click()
        await self.wait()
        self.assertEqual(stage_model.get_items_sort_policy(), StageItemSortPolicy.DEFAULT)
