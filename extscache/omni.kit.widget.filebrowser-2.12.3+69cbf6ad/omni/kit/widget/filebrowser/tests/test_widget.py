## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.client
import omni.kit.app

from omni.kit import ui_test
from unittest.mock import  patch
from ..model import FileBrowserModel, FileBrowserItemFactory
from ..widget import FileBrowserWidget

async def after_redraw_async(frames=1):
    for _ in range(frames + 1):
        await omni.kit.app.get_app().next_update_async()

class TestWidget(omni.kit.test.AsyncTestCase):
    """Testing FileBrowserWidget basic fuction"""
    async def setUp(self):
        self._throttle_frames = 4

    async def tearDown(self):
        # Wait a few frames for delayed item changed events to clear the system
        await after_redraw_async(self._throttle_frames)

    async def test_widget_find_views(self):
        """OM-115384: Testing FileBrowserWidget, ui_test could find views by frame name"""
        import omni.ui as ui
        window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_DOCKING
        self._window = ui.Window("test_find_window", width=1200, height=900, flags=window_flags)
        with self._window.frame:
            under_test = FileBrowserWidget("findview")
            under_test.toggle_grid_view(True)
            grid_view = ui_test.find("test_find_window//Frame/**/GridViewFrame")
            table_view = ui_test.find("test_find_window//Frame/**/TableViewFrame")
            self.assertTrue(grid_view.widget.visible)
            self.assertFalse(table_view.widget.visible)

            under_test.toggle_grid_view(False)
            grid_view = ui_test.find("test_find_window//Frame/**/GridViewFrame")
            table_view = ui_test.find("test_find_window//Frame/**/TableViewFrame")
            self.assertFalse(grid_view.widget.visible)
            self.assertTrue(table_view.widget.visible)
            under_test.destroy()
        self._window = None

    async def test_widget_refreshes_views(self):
        """Testing FileBrowserWidget._auto_refresh_item updates views"""
        from .. import TREEVIEW_PANE, LISTVIEW_PANE
        import omni.ui as ui
        from tempfile import TemporaryDirectory
        window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_DOCKING
        self._window = ui.Window("test_window", width=1200, height=900, flags=window_flags)
        with self._window.frame, TemporaryDirectory() as test_url, TemporaryDirectory() as test_url2:
            udim_url = "C://texture_1001.jpg"
            udim_url2 = "C://texture_1002.jpg"
            model = FileBrowserModel("C:", "C:")
            watched = FileBrowserItemFactory.create_group_item("watched", test_url)
            udim_item = FileBrowserItemFactory.create_udim_item("udim", udim_url, 0,1,1)
            udim_item2 = FileBrowserItemFactory.create_udim_item("udim2", udim_url2,1,2,1)
            udim_item.populate_udim(model.root)
            model.root.add_child(watched)
            model.root.add_child(udim_item)
            model.root.add_child(udim_item2)

            under_test = FileBrowserWidget("test")
            under_test.add_model_as_subtree(model)
            under_test._on_selection_changed(TREEVIEW_PANE, [watched])

            # teat some widget's attribute and method
            under_test.show_udim_sequence=True
            self.assertTrue(under_test.show_udim_sequence)
            self.assertEqual(under_test.get_root(), under_test._models.root)
            self.assertEqual(under_test.get_root(TREEVIEW_PANE), under_test._models.root)
            self.assertEqual(under_test.get_root(LISTVIEW_PANE), under_test._listview_model.root)

            # test notification and toggle
            under_test.show_notification()
            self.assertTrue(under_test._notification_frame.visible)
            under_test.hide_notification()
            self.assertFalse(under_test._notification_frame.visible)
            under_test.toggle_grid_view(True)
            self.assertTrue(under_test.show_grid_view)

            # test create item
            item_create_from_widget = under_test.create_grouping_item("watched2", test_url2)
            self.assertEqual(item_create_from_widget.name, "watched2")

            # test set item info
            under_test.set_item_info(item_create_from_widget, "info")
            self.assertEqual(item_create_from_widget.alert[1], "info")
            under_test.set_item_warning(item_create_from_widget, "warning")
            self.assertEqual(item_create_from_widget.alert[1], "warning")
            await after_redraw_async(self._throttle_frames)
            under_test.set_item_error(item_create_from_widget, "error")
            self.assertEqual(item_create_from_widget.alert[1], "error")
            await after_redraw_async(self._throttle_frames)
            under_test.clear_item_alert(item_create_from_widget)
            self.assertEqual(item_create_from_widget.alert, None)
            await after_redraw_async(self._throttle_frames)

            # test tree view select
            under_test.set_selections([item_create_from_widget], TREEVIEW_PANE)
            self.assertEqual(under_test.get_selected_item(), item_create_from_widget)
            await after_redraw_async(self._throttle_frames)
            under_test.select_and_center(item_create_from_widget, TREEVIEW_PANE)
            under_test.set_expanded(item_create_from_widget, True, True)
            self.assertEqual(under_test.get_selected_item(), item_create_from_widget)
            await after_redraw_async(self._throttle_frames)

            # test listview select
            under_test.select_and_center(watched, LISTVIEW_PANE)
            under_test.toggle_grid_view(False)
            self.assertFalse(under_test.show_grid_view)
            under_test.select_and_center(item_create_from_widget, LISTVIEW_PANE)
            under_test._on_selection_changed(LISTVIEW_PANE, [item_create_from_widget])
            self.assertEqual(under_test.get_selected_item(), item_create_from_widget)
            await after_redraw_async(self._throttle_frames)
            under_test.delete_child(item_create_from_widget)
            await after_redraw_async(self._throttle_frames)
            under_test.destroy()
