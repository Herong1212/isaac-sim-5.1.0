import omni.kit.test
from omni.kit import ui_test

from ..samples import *


class TestSamples(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_combox_box(self):
        under_test = SimpleComboxBoxWindow()
        self.assertFalse(under_test.is_visible())
        under_test.destroy()

    async def test_custom_menu(self):
        under_test = SimpleCustomMenuWindow()
        self.assertFalse(under_test.is_visible())
        under_test.show()
        window = ui_test.find("Single custom menu view")
        button = ui_test.find("Single custom menu view//Frame/**/Button[*].text=='Left alignment Custom Menu'")
        await button.click()
        button = ui_test.find("Single custom menu view//Frame/**/Button[*].text=='Center alignment Custom Menu'")
        await button.click()
        button = ui_test.find("Single custom menu view//Frame/**/Button[*].text=='Right alignment Custom Menu'")
        await button.click()
        button = ui_test.find("Single custom menu view//Frame/**/Button[*].text=='Different widgets Menu'")
        await button.click()
        self.assertTrue(under_test.is_visible())
        under_test.show(False)
        under_test.destroy()

    async def test_multi_list_window(self):
        under_test = MultiListWindow()
        self.assertFalse(under_test.is_visible())
        under_test.destroy()

    async def test_grid_window(self):
        under_test = SimpleGridWindow()
        self.assertFalse(under_test.is_visible())
        under_test.destroy()

    async def test_single_list_window(self):
        under_test = SingleListWindow()
        self.assertFalse(under_test.is_visible())
        under_test.destroy()
