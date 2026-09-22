import os
from pathlib import Path
from tempfile import TemporaryDirectory, NamedTemporaryFile

import omni.kit.test
from omni.kit import ui_test
from omni.kit.widget.filebrowser import TREEVIEW_PANE, LISTVIEW_PANE
from omni import ui

from ..test_helper import FilePickerTestHelper
from ..dialog import FilePickerDialog
from ..context_menu import BaseContextMenu
from .test_utils import time_logger

import omni.client


@time_logger
class TestContexMenu(omni.kit.test.AsyncTestCase):
    """Testing that the context menu system works as expected."""
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        self._window = ui.Window("test_context_menu", width=400, height=400)
        # wait as showing menus imediatlly can cause them to close
        await ui_test.human_delay(10)

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)
        ui.Workspace.show_window(self._window.title)
        self._window = None

    async def test_context_menu_built_correctly(self):
        """Testing that menu items built from menu dict are correct."""
        class _MockContextMenu(BaseContextMenu):
            def __init__(self, **kwargs):
                super().__init__(title="Mock Context menu", **kwargs)
                self._menu_dict = [
                    {
                        "name": "",
                    },
                    {
                        "name": "Item01_disabled",
                        "show_fn": [lambda context: True,]
                    },
                    {
                        "name": "",
                    },
                    {
                        "name": "Item02_invisible",
                        "show_fn": [lambda context: False,]
                    },
                    {
                        "name": "",
                    },
                    {
                        "name": "Item03_show",
                        "onclick_fn": lambda context: print(context),
                        "show_fn": [lambda context: True,]
                    },
                    {
                        "name": "",
                    },
                ]

        context_menu = _MockContextMenu()
        await ui_test.human_delay()
        context_menu.show(None, [])
        await ui_test.human_delay()

        menu_root = ui.Menu.get_current()
        menu_items = ui.Inspector.get_children(menu_root)
        # remove non-menu widgets
        menu_items = [
            item for item in menu_items if
            isinstance(item, omni.kit.widget.context_menu.ContextMenuWidgetExtension.uiMenuItem) or
            isinstance(item, ui.Separator)
        ]
        # separator should not be built if it is the first/last element
        self.assertNotIsInstance(menu_items[0], ui.Separator)
        # last item can be Separator but should be invisible
        self.assertIsInstance(menu_items[-1], ui.Separator)
        self.assertFalse(menu_items[-1].visible)

        # 2 separators should not be built next to each other
        # because the second item is invisbile, separator 0 and 1 are now next to each other, but we shoud only have
        # one separator built after item 01
        # the result of the built items are: [item 01(disabled), separator, item03]
        self.assertEqual(len(menu_items), 4)
        self.assertEqual(menu_items[0].text, "Item01_disabled")
        self.assertFalse(menu_items[0].enabled)
        self.assertIsInstance(menu_items[1], ui.Separator)
        self.assertEqual(menu_items[2].text, "Item03_show")
        self.assertTrue(menu_items[2].enabled)

    async def test_add_context_menu(self):
        """Testing the add_context_menu API."""
        class _MockContextMenu(BaseContextMenu):
            def __init__(self, **kwargs):
                super().__init__(title="Mock Context menu", **kwargs)
                self._menu_dict = [
                    {
                        "name": "Item01",
                        "onclick_fn": lambda context: print(context),
                        "show_fn": [lambda context: True,]
                    },
                    {
                        "name": "",
                        "_separator_test_add_": ""
                    },
                    {
                        "name": "Item02",
                        "onclick_fn": lambda context: print(context),
                        "show_fn": [lambda context: True,]
                    },
                    {
                        "name": "Item03",
                        "onclick_fn": lambda context: print(context),
                        "show_fn": [lambda context: True,]
                    },
                ]

        def _get_menu_names(menu_dict):
            names = []
            for item in menu_dict:
                names.append(item.get("name"))
            return names

        # test adding by explicit index (regardless of separator anchor position)
        context_menu = _MockContextMenu()
        original_names = _get_menu_names(context_menu._menu_dict)
        context_menu.add_menu_item("Item00", "", None, None, index=0)
        context_menu.add_menu_item("Item2.5", "", None, None, index=4)
        self.assertEqual(_get_menu_names(context_menu._menu_dict),
                        ['Item00', 'Item01', '', 'Item02', 'Item2.5', 'Item03'])

        # test adding by explicit index out of range
        context_menu.add_menu_item("Item-100", "", None, None, index=-100)
        context_menu.add_menu_item("Item999", "", None, None, index=999)
        self.assertEqual(_get_menu_names(context_menu._menu_dict),
                        ['Item-100', 'Item00', 'Item01', '', 'Item02', 'Item2.5', 'Item03', 'Item999'])

        # test add by separator name anchor
        context_menu.add_menu_item("before separator", "", None, None, index=0, separator_name="_separator_test_add_")
        context_menu.add_menu_item("first", "", None, None, index=-10, separator_name="_separator_test_add_")
        context_menu.add_menu_item("after separator", "", None, None, index=3, separator_name="_separator_test_add_")
        context_menu.add_menu_item("last", "", None, None, index=100, separator_name="_separator_test_add_")
        print(_get_menu_names(context_menu._menu_dict))
        self.assertEqual(_get_menu_names(context_menu._menu_dict),
                        ['first', 'Item-100', 'Item00', 'Item01', 'before separator', '', 'Item02', 'Item2.5',
                         'after separator', 'Item03', 'Item999', 'last'])

        # test add by non-existent separator name default to add to last
        context_menu.add_menu_item("non existent", "", None, None, index=1, separator_name="_dummy_")
        self.assertEqual(_get_menu_names(context_menu._menu_dict),
                        ['first', 'Item-100', 'Item00', 'Item01', 'before separator', '', 'Item02', 'Item2.5',
                         'after separator', 'Item03', 'Item999', 'last', 'non existent'])

        # test delete
        context_menu.delete_menu_item("Item2.5")
        self.assertEqual(_get_menu_names(context_menu._menu_dict),
                        ['first', 'Item-100', 'Item00', 'Item01', 'before separator', '', 'Item02',
                         'after separator', 'Item03', 'Item999', 'last', 'non existent'])

    async def test_context_menu_async_show_fn(self):
        """Testing that with async show fn menu item visibility updates correctly."""

        async def _async_show(context, menu_item):
            await ui_test.human_delay(8)
            menu_item.visible = True

        async def _async_hide(context, menu_item):
            await ui_test.human_delay(8)
            menu_item.visible = False

        class _MockAsyncShownFn(BaseContextMenu):
            def __init__(self, **kwargs):
                super().__init__(title="Mock Async Shown Fn", **kwargs)
                self._menu_dict = [
                    {
                        "name": "Item01_show",
                        "onclick_fn": lambda context: print(context),
                        "show_fn": [lambda context: True,]
                    },
                    {
                        "name": "",
                    },
                    {
                        "name": "Item02_async_show",
                        "onclick_fn": lambda context: print(context),
                        "show_fn": [lambda context: True,],
                        "show_fn_async": _async_show,
                    },
                    {
                        "name": "",
                    },
                    {
                        "name": "Item03_async_hide",
                        "onclick_fn": lambda context: print(context),
                        "show_fn": [lambda context: True,],
                        "show_fn_async": _async_hide,
                    },
                    {
                        "name": "",
                    },
                    {
                        "name": "Item04_show",
                        "onclick_fn": lambda context: print(context),
                        "show_fn": [lambda context: True,]
                    },
                ]

        context_menu = _MockAsyncShownFn()
        await ui_test.human_delay()
        context_menu.show(None, [])
        await ui_test.human_delay()

        menu_root = ui.Menu.get_current()
        menu_items = ui.Inspector.get_children(menu_root)

        # remove non-menu widgets
        menu_items = [
            item for item in menu_items if
            isinstance(item, omni.kit.widget.context_menu.ContextMenuWidgetExtension.uiMenuItem) or
            isinstance(item, ui.Separator)
        ]

        # before the aysnc shown fn finishes, all the 2 async items should be invisble
        async_show_item = menu_items[2]
        async_hide_item = menu_items[4]
        for item in (async_show_item, async_hide_item):
            self.assertFalse(item.visible)

        # by default, the separator after the async hide item will be built and will be visible
        separator_to_update = menu_items[5]
        self.assertTrue(separator_to_update.visible)

        await ui_test.human_delay(10)
        # after async fn finishes, visibility of menu item should be updated
        self.assertTrue(async_show_item.visible)
        self.assertFalse(async_hide_item.visible)
        # 2 separators should not be shown next to each other
        # since async_hide_item is now confirmed invisible, the separator after it should be updated to invisble
        # fixme - this isn't implimented... self.assertFalse(separator_to_update.visible)


@time_logger
class TestMenuOptions(omni.kit.test.AsyncTestCase):
    """Testing the context menu's options"""
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)

    async def test_Options_availablity(self):
        """Testing the context menu show up options correctly under different circumstances."""
        dialog = FilePickerDialog("test_rename_availablity", treeview_identifier="FilePicker")
        await ui_test.human_delay(10)
        dialog.add_connections({"ov-test": "omniverse://ov-test"})
        await ui_test.human_delay(10)
        with TemporaryDirectory() as tmpdir_fd:
            tmpdir = Path(tmpdir_fd).resolve()
            temp_fd = NamedTemporaryFile(dir=tmpdir, suffix=".mdl", delete=False)
            temp_fd.close()
            _, filename = os.path.split(temp_fd.name)

            async with FilePickerTestHelper(dialog._widget) as filepicker_helper:
                # rename should appear when connection is selected
                item = await filepicker_helper.get_item_async("FilePicker", "ov-test", pane=TREEVIEW_PANE)
                await item.right_click()
                context_menu = await ui_test.get_context_menu()
                context_options = context_menu["_"]
                self.assertTrue("Rename" in context_options)
                # rename should not appear when a file item is selected
                await filepicker_helper.select_items_async(str(tmpdir), [filename])
                item = await filepicker_helper.get_item_async("FilePicker", filename, pane=LISTVIEW_PANE)
                await ui_test.human_delay()
                await item.right_click()
                context_menu = await ui_test.get_context_menu()
                context_options = context_menu["_"]
                self.assertTrue("Rename" in context_options)
                # OMFP-2948: should not have the New Folder for connection point
                self.assertFalse("New Folder" in context_options)
                pane = await filepicker_helper.get_pane_async("FilePicker", pane=LISTVIEW_PANE)
                await pane.right_click()
                context_menu = await ui_test.get_context_menu()
                context_options = context_menu["_"]
                # OM-104870: Also need check other menu options
                self.assertTrue("New USD File" in context_options)
                self.assertTrue("Refresh" in context_options)
                self.assertTrue("Add Bookmark" in context_options)
                self.assertTrue("Copy URL Link" in context_options)

        dialog.destroy()

    # OMFP-2569: make sure login/logout menuitem is keep consisitent with the item's connect status
    async def test_LogIn_LogOut_availablity(self):
        """Testing the context menu show up LogIn/LogOut correctly under different circumstances."""
        dialog = FilePickerDialog("test_login_logout_availablity", treeview_identifier="FilePicker")
        await ui_test.human_delay(10)
        dialog.add_connections({"ov-test": "omniverse://ov-test"})
        await ui_test.human_delay(10)

        async with FilePickerTestHelper(dialog._widget) as filepicker_helper:
            # login should appear when connection is selected
            item = await filepicker_helper.get_item_async("FilePicker", "ov-test", pane=TREEVIEW_PANE)
            # simulate connected status
            dialog._widget._view._server_status_changed("omniverse://ov-test", omni.client.ConnectionStatus.CONNECTED)
            await ui_test.human_delay(30)
            await item.right_click()
            context_menu = await ui_test.get_context_menu()
            context_options = context_menu["_"]
            self.assertFalse("Log In" in context_options)
            self.assertTrue("Log Out" in context_options)

            # simulate disconnected status
            dialog._widget._view._server_status_changed("omniverse://ov-test", omni.client.ConnectionStatus.SIGNED_OUT)
            await ui_test.human_delay(30)
            await item.right_click()
            context_menu = await ui_test.get_context_menu()
            context_options = context_menu["_"]
            self.assertTrue("Log In" in context_options)
            self.assertFalse("Log Out" in context_options)

        dialog.destroy()

    async def test_Options_in_local_contextmenu(self):
        """Testing the local context menu show up options correctly under different circumstances."""
        dialog = FilePickerDialog("test_local_options", treeview_identifier="FilePicker")
        await ui_test.human_delay(10)

        async with FilePickerTestHelper(dialog._widget) as filepicker_helper:
            # rename should appear when connection is selected
            local_folders = dialog._widget._view.all_collection_items(collection="my-computer")
            # that means there is no local folder in test agent, stop this test
            if len(local_folders) == 0:
                return
            local_folder_name = local_folders[0].name
            item = await filepicker_helper.get_item_async("FilePicker", local_folder_name, pane=TREEVIEW_PANE)
            await item.right_click()
            await ui_test.human_delay(10)
            context_menu = await ui_test.get_context_menu()
            context_options = context_menu["_"]
            # TODO: why and when these menu items diappeared in my local build?
            self.assertTrue("New USD File" in context_options)
            self.assertTrue("Refresh" in context_options)
            self.assertTrue("Copy URL Link" in context_options)
            self.assertTrue("New Folder" in context_options)
            self.assertFalse("Add Bookmark" in context_options)
            self.assertFalse("Rename" in context_options)
            self.assertFalse("Edit" in context_options)
            self.assertFalse("Delete" in context_options)

        dialog.destroy()
