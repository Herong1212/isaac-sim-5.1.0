import omni.kit.app
import omni.kit.test
import omni.kit.window.extensions

from .utils import open_window_and_sync

# pylint: disable=protected-access


class TestDefaultFilter(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await open_window_and_sync(False)

    async def tearDown(self):
        omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate(
            "omni.kit.window.extensions", True
        )
        if omni.kit.app.get_app().get_extension_manager().is_extension_enabled("omni.kit.window.extensions"):
            instance = omni.kit.window.extensions.get_instance()()
            instance.show_window(False)

    async def test_default_filter(self):
        instance = omni.kit.window.extensions.get_instance()()
        ext_list_widget_model = instance._window._exts_list_widget._model

        # NOTE: /exts/omni.kit.window.extensions/featuredExts is set to ['omni.kit.window.extensions']
        # and   /exts/omni.kit.window.extensions/default_filter is set to ['featured']
        # so only 1 extension should be listed.

        # get filtered group list
        filtered_items = {group.name: len(group.items) for group in ext_list_widget_model.get_item_children(None)}

        # verify there are 1 featured extension 'omni.kit.window.extensions' which is in test toml
        self.assertEqual(filtered_items, {"Core": 1, "Sample": 0, "Internal": 0, "Deprecated": 0})
