import omni.kit.app
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.kit.window.extensions

from .utils import open_window_and_sync

# pylint: disable=protected-access


class TestAPITemplate(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate(
            "omni.kit.window.extensions", True
        )
        await open_window_and_sync(False)

    async def tearDown(self):
        if omni.kit.app.get_app().get_extension_manager().is_extension_enabled("omni.kit.window.extensions"):
            instance = omni.kit.window.extensions.get_instance()()
            instance.show_window(False)

    async def test_api_show_window(self):
        instance = omni.kit.window.extensions.get_instance()()

        instance.show_window(False)
        await ui_test.human_delay(10)
        instance.show_window(False)
        await ui_test.human_delay(10)
        instance.show_window(True)
        await ui_test.human_delay(10)
        instance.show_window(True)
        await ui_test.human_delay(10)
        instance.show_window(False)
        await ui_test.human_delay(10)
        instance.show_window(True)

        await ui_test.human_delay(50)

    async def test_api_keyword(self):
        instance = omni.kit.window.extensions.get_instance()()
        filter_count = 0

        def filter_on_menu(item):
            nonlocal filter_count

            filter_count += 1
            return "menu" in item.name.lower()

        # add Menus filter
        instance.add_searchable_keyword("@menu", "Menus", filter_on_menu, None)
        await ui_test.human_delay(10)

        # select Menus filter
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='filter'").click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Menus")
        await ui_test.human_delay(50)

        # remove Menus filter
        instance.remove_searchable_keyword("@menu")

        # verify custom filter was used
        self.assertGreater(filter_count, 0)

    async def test_api_tab(self):
        from omni.kit.window.extensions.common import ExtensionCommonInfo
        from omni.kit.window.extensions.ext_info_widget import PageBase

        instance = omni.kit.window.extensions.get_instance()()

        cheese_usage = {}

        class CheesePage(PageBase):
            def build_tab(self, ext_info, ext_item: ExtensionCommonInfo):
                nonlocal cheese_usage

                cheese_usage["build_tab"] = True

            def destroy(self):  # pragma: no cover
                nonlocal cheese_usage

                cheese_usage["destroy"] = True

            @staticmethod
            def get_tab_name():
                nonlocal cheese_usage

                cheese_usage["get_tab_name"] = True
                return "CHEESE"

        # add cheese tab
        instance.add_tab_to_info_widget(CheesePage)

        # filter omni.kit.window.extensions
        instance._window._exts_list_widget._model.filter_by_text(["omni.kit.window.extensions"])
        await ui_test.human_delay(50)

        # click on omni.kit.window.extensions
        await ui_test.find("Extensions//Frame/**/Label[*].identifier=='Title'").click()
        await ui_test.human_delay(10)

        # click on cheese tab
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='tab_cheese'").click()
        await ui_test.human_delay(50)

        # remove cheese tab
        instance.remove_tab_from_info_widget(CheesePage)
        await ui_test.human_delay(10)

        self.assertEqual(cheese_usage, {"get_tab_name": True, "build_tab": True})
