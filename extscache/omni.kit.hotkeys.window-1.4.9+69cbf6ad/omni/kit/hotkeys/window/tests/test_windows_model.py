from omni.kit.test import AsyncTestCase
from ..model.windows_model import WindowsModel


class TestWindowsModel(AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_model(self):
        model = WindowsModel("Hotkeys")
        self.assertEqual(model.get_item_value_model_count(), 1)
        items = model.get_item_children()
        self.assertEqual(model.get_item_value_model(None), "")
        self.assertEqual(model.get_item_value_model(items[1]).as_string, items[1].window_title)
        self.assertEqual(model.get_item_children(items[0]), [])

        self.assertTrue("Hotkeys" in [item.window_title for item in items])
        self.assertEqual(model.selected_windows, ["Hotkeys"])

        # Note, there will always be "" as first item
        # Search a window
        model.search(["hot"])
        items = model.get_item_children()
        print([w.window_title for w in items])
        self.assertEqual(len(items), 2)

        # Search a un-exist window
        model.search(["un-exist"])
        items = model.get_item_children()
        self.assertEqual(len(items), 1)
