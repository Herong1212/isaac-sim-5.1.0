import omni.kit.app
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.kit.window.extensions

from .utils import open_window_and_sync

# pylint: disable=protected-access


class TestMenus(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await open_window_and_sync(False)

    async def tearDown(self):
        if omni.kit.app.get_app().get_extension_manager().is_extension_enabled("omni.kit.window.extensions"):
            instance = omni.kit.window.extensions.get_instance()()
            instance.show_window(False)

    async def test_menu_filter(self):
        instance = omni.kit.window.extensions.get_instance()()
        ext_list_widget_model = instance._window._exts_list_widget._model

        # get group list, before filtering
        all_items = {group.name: len(group.items) for group in ext_list_widget_model.get_item_children(None)}

        # enable filter "Enabled"
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='filter'").click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Enabled")
        await ui_test.human_delay(10)

        # get filtered group list
        filtered_items = {group.name: len(group.items) for group in ext_list_widget_model.get_item_children(None)}
        self.assertNotEqual(all_items, filtered_items)

        # disable filter "Enabled"
        await ui_test.select_context_menu("Enabled")
        await ui_test.human_delay(10)

        # get filtered group list
        filtered_items = {group.name: len(group.items) for group in ext_list_widget_model.get_item_children(None)}
        self.assertEqual(all_items, filtered_items)

        # close the menu as filter is persistent
        instance._window._exts_list_widget.close_filter_menu()
        await ui_test.human_delay(10)

    async def test_menu_sortby(self):
        pass
