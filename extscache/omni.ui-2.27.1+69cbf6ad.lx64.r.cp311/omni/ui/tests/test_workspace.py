## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from .test_base import OmniUiTest
import carb.settings
import omni.appwindow
import omni.kit.app
import omni.kit.renderer
import omni.kit.test
import omni.ui as ui


class TestWorkspace(OmniUiTest):
    """Testing ui.Workspace"""

    async def test_workspace_show_window(self):
        ui.Workspace.clear()
        await self.create_test_area(256, 256)
        win_name = "Test Window"

        def show_window(value):
            if value:
                self.window = ui.Window(win_name, width=100, height=100)
                # add a callback to destroy the window when it is not visible
                self.window.set_visibility_changed_fn(on_visibility_changed)
            else:
                if self.window:
                    self.window.destroy()
                    self.window = None

        def on_visibility_changed(visible):
            if not visible:
                show_window(False)

        show_window(True)
        ui.Workspace.set_show_window_fn(win_name, show_window)

        await omni.kit.app.get_app().next_update_async()

        window_handle = ui.Workspace.get_window(win_name)
        self.assertTrue(window_handle.visible)

        window_handle.visible = False
        await omni.kit.app.get_app().next_update_async()

        # check the window has been destroyed
        window_handle = ui.Workspace.get_window(win_name)
        self.assertIsNone(window_handle.visible)

        window_handles = ui.Workspace.get_windows()
        window_handles=[win for win in window_handles if win.title==win_name]
        self.assertTrue(len(window_handles)==1)
        self.assertFalse(window_handle.visible)

        # run again to make sure the get_window and get_windows are working correctly
        window_handle = ui.Workspace.get_window(win_name)
        self.assertFalse(window_handle.visible)

        window_handles = ui.Workspace.get_windows()
        window_handles=[win for win in window_handles if win.title==win_name]
        self.assertTrue(len(window_handles)==1)
        self.assertFalse(window_handle.visible)

        # let's bring the window back
        ui.Workspace.show_window(win_name)
        await omni.kit.app.get_app().next_update_async()

        # check the window is created and visible is correct using get_window
        # this should call showWindowFn(show);
        window_handle = ui.Workspace.get_window(win_name)
        self.assertTrue(window_handle)
        self.assertTrue(window_handle.visible)

        # check the window is created and visible is correct using get_windows
        window_handles = ui.Workspace.get_windows()
        window_handles=[win for win in window_handles if win.title==win_name]
        self.assertTrue(len(window_handles)==1)
        self.assertTrue(window_handles[0].visible)

        # let's try destroy the window by calling show_window
        ui.Workspace.show_window(win_name, False)
        await omni.kit.app.get_app().next_update_async()

        window_handle = ui.Workspace.get_window(win_name)
        self.assertIsNone(window_handle.visible)

        window_handles = ui.Workspace.get_windows()
        window_handles=[win for win in window_handles if win.title==win_name]
        self.assertTrue(len(window_handles)==1)
        self.assertIsNone(window_handle.visible)

        self.finalize_test_no_image()
        ui.Workspace.clear()

    async def test_workspace_show_window2(self):
        ui.Workspace.clear()
        await self.create_test_area(256, 256)
        win_name = "Test Window"

        def show_window(value):
            if value:
                self.window = ui.Window(win_name, width=100, height=100)
                # add a callback to destroy the window when it is not visible
                self.window.set_visibility_changed_fn(on_visibility_changed)
            else:
                if self.window:
                    self.window.destroy()
                    self.window = None

        def on_visibility_changed(visible):
            if not visible:
                show_window(False)

        show_window(True)
        ui.Workspace.set_show_window_fn(win_name, show_window)

        await omni.kit.app.get_app().next_update_async()

        # this is to test that OmitWindow is implemented correctly
        self.window.visible = False
        await omni.kit.app.get_app().next_update_async()

        # check the window has been destroyed
        window_handle = ui.Workspace.get_window(win_name)
        self.assertIsNone(window_handle.visible)

        window_handles = ui.Workspace.get_windows()
        window_handles=[win for win in window_handles if win.title==win_name]
        self.assertTrue(len(window_handles)==1)
        self.assertIsNone(window_handle.visible)

        window_handle = ui.Workspace.get_window(win_name)
        self.assertIsNone(window_handle.visible)

        # now Let's create a new window
        window = ui.Window("Test Window", width=100, height=100)
        await omni.kit.app.get_app().next_update_async()
        window_handle = ui.Workspace.get_window(win_name)
        self.assertTrue(window_handle)
        self.assertTrue(window_handle.visible)

        window_handles = ui.Workspace.get_windows()
        window_handles=[win for win in window_handles if win.title==win_name]
        self.assertTrue(len(window_handles)==1)
        self.assertTrue(window_handles[0].visible)

        self.finalize_test_no_image()
        ui.Workspace.clear()

    async def test_workspace_show_window3(self):
        ui.Workspace.clear()
        await self.create_test_area(256, 256)
        win_name = "Extensions"

        def show_window(value):
            if value:
                self.window = ui.Window(win_name, width=100, height=100)
            else:
                if self.window:
                    self.window.destroy()
                    self.window = None

        ui.Workspace.set_show_window_fn(win_name, show_window)
        ui.Workspace.show_window(win_name, True)

        await omni.kit.app.get_app().next_update_async()

        window_handle = ui.Workspace.get_window(win_name)
        self.assertTrue(window_handle.visible)

        window_handles = ui.Workspace.get_windows()
        window_handles=[win for win in window_handles if win.title==win_name]
        self.assertTrue(len(window_handles)==1)
        self.assertTrue(window_handles[0].visible)

        window_handle.visible = False
        await omni.kit.app.get_app().next_update_async()
        # check window is not visible, but is not destroyed
        window_handle = ui.Workspace.get_window(win_name)
        self.assertFalse(window_handle.visible)

        window_handles = ui.Workspace.get_windows()
        window_handles=[win for win in window_handles if win.title==win_name]
        self.assertTrue(len(window_handles)==1)
        self.assertFalse(window_handles[0].visible)

        await omni.kit.app.get_app().next_update_async()
        ui.Workspace.show_window(win_name, True)

        window_handles = ui.Workspace.get_windows()
        window_handles=[win for win in window_handles if win.title==win_name]
        self.assertTrue(len(window_handles)==1)
        self.assertTrue(window_handles[0].visible)

        window_handle = ui.Workspace.get_window(win_name)
        self.assertTrue(window_handle)
        self.assertTrue(window_handle.visible)

        # destroy window by calling show_window
        show_window(False)
        await omni.kit.app.get_app().next_update_async()
        # check the window has been destroyed
        window_handle = ui.Workspace.get_window(win_name)
        self.assertIsNone(window_handle.visible)

        window_handles = ui.Workspace.get_windows()
        window_handles=[win for win in window_handles if win.title==win_name]
        self.assertTrue(len(window_handles)==1)
        self.assertIsNone(window_handle.visible)

        self.finalize_test_no_image()
        ui.Workspace.clear()

    async def test_window_selection(self):
        """Testing window selection callback"""
        ui.Workspace.clear()
        self.text = "null"

        def update_selection(selected):
            self.text = "Selected" if selected else "UnSelected"

        ui_main_window = ui.MainWindow()
        window1 = ui.Window("First Selection", width=100, height=100)
        window2 = ui.Window("Second Selection", width=100, height=100)
        window3 = ui.Window("Third Selection", width=100, height=100)
        await omni.kit.app.get_app().next_update_async()
        main_dockspace = ui.Workspace.get_window("DockSpace")
        window1.dock_in(main_dockspace, ui.DockPosition.SAME)
        window2.dock_in(main_dockspace, ui.DockPosition.SAME)
        window3.dock_in(main_dockspace, ui.DockPosition.SAME)
        await omni.kit.app.get_app().next_update_async()
        # add callback function to window2 to subscribe selection change in windows
        window2.set_selected_in_dock_changed_fn(lambda value: update_selection(value))
        await omni.kit.app.get_app().next_update_async()
        # select window2 to check if the callback is triggered
        window2.focus()
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self.text, "Selected")
        await omni.kit.app.get_app().next_update_async()
        # select window1 to check if the callback is triggered
        window1.focus()
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self.text, "UnSelected")

    async def test_workspace_nohide(self):
        """Testing window layout without hiding the windows"""
        ui.Workspace.clear()
        await self.create_test_area(256, 256)

        ui_main_window = ui.MainWindow()
        ui_main_window.main_menu_bar.visible = False
        window1 = ui.Window("First", width=100, height=100)
        window2 = ui.Window("Second", width=100, height=100)

        await omni.kit.app.get_app().next_update_async()

        main_dockspace = ui.Workspace.get_window("DockSpace")
        window1.dock_in(main_dockspace, ui.DockPosition.SAME)
        window2.dock_in(window1, ui.DockPosition.BOTTOM)

        await omni.kit.app.get_app().next_update_async()

        # Save the layout
        layout = ui.Workspace.dump_workspace()
        # Reference. Don't check directly because `dock_id` is random.
        # [
        #     {
        #         "dock_id": 3358485147,
        #         "children": [
        #             {
        #                 "dock_id": 1,
        #                 "position": "TOP",
        #                 "children": [
        #                     {
        #                         "title": "First",
        #                         "width": 100.0,
        #                         "height": 100.0,
        #                         "position_x": 78.0,
        #                         "position_y": 78.0,
        #                         "dock_id": 1,
        #                         "visible": True,
        #                         "selected_in_dock": False,
        #                     }
        #                 ],
        #             },
        #             {
        #                 "dock_id": 2,
        #                 "position": "BOTTOM",
        #                 "children": [
        #                     {
        #                         "title": "Second",
        #                         "width": 100.0,
        #                         "height": 100.0,
        #                         "position_x": 78.0,
        #                         "position_y": 78.0,
        #                         "dock_id": 2,
        #                         "visible": True,
        #                         "selected_in_dock": False,
        #                     }
        #                 ],
        #             },
        #         ],
        #     }
        # ]
        self.assertEqual(layout[0]["children"][0]["children"][0]["title"], "First")
        self.assertEqual(layout[0]["children"][1]["children"][0]["title"], "Second")

        window3 = ui.Window("Third", width=100, height=100)
        await omni.kit.app.get_app().next_update_async()
        window3.dock_in(window1, ui.DockPosition.LEFT)

        ui.Workspace.restore_workspace(layout, True)

        window3.position_x = 78
        window3.position_y = 78

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_workspace_nohide_invisible(self):
        """Testing window layout without hiding the windows"""
        ui.Workspace.clear()
        await self.create_test_area(256, 256)

        ui_main_window = ui.MainWindow()
        ui_main_window.main_menu_bar.visible = False
        window1 = ui.Window(
            "First Vis", width=100, height=100, position_x=0, position_y=0, flags=ui.WINDOW_FLAGS_NO_SCROLLBAR
        )
        window2 = ui.Window(
            "Second Invis", width=100, height=100, position_x=100, position_y=0, flags=ui.WINDOW_FLAGS_NO_SCROLLBAR
        )

        await omni.kit.app.get_app().next_update_async()

        window2.visible = False

        await omni.kit.app.get_app().next_update_async()

        # Save the layout
        layout = ui.Workspace.dump_workspace()
        # We have first window visible, the second is not visible

        window3 = ui.Window("Third Absent", width=100, height=100, position_x=0, position_y=100)
        await omni.kit.app.get_app().next_update_async()

        ui.Workspace.restore_workspace(layout, True)

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_dock_node_size(self):
        ui.Workspace.clear()
        await self.create_test_area(256, 256)

        ui_main_window = ui.MainWindow()
        ui_main_window.main_menu_bar.visible = False
        window1 = ui.Window("1", width=100, height=100)
        window2 = ui.Window("2", width=100, height=100)
        window3 = ui.Window("3", width=100, height=100)
        window4 = ui.Window("4", width=100, height=100)

        await omni.kit.app.get_app().next_update_async()

        main_dockspace = ui.Workspace.get_window("DockSpace")
        window1.dock_in(main_dockspace, ui.DockPosition.SAME)
        window2.dock_in(window1, ui.DockPosition.RIGHT)
        window3.dock_in(window1, ui.DockPosition.BOTTOM)
        window4.dock_in(window2, ui.DockPosition.BOTTOM)

        await omni.kit.app.get_app().next_update_async()

        self.assertEqual(ui.Workspace.get_dock_id_width(window1.dock_id), 126)
        self.assertEqual(ui.Workspace.get_dock_id_width(window2.dock_id), 126)
        self.assertEqual(ui.Workspace.get_dock_id_width(window3.dock_id), 126)
        self.assertEqual(ui.Workspace.get_dock_id_width(window4.dock_id), 126)
        self.assertEqual(ui.Workspace.get_dock_id_height(window1.dock_id), 124)
        self.assertEqual(ui.Workspace.get_dock_id_height(window2.dock_id), 124)
        self.assertEqual(ui.Workspace.get_dock_id_height(window3.dock_id), 124)
        self.assertEqual(ui.Workspace.get_dock_id_height(window4.dock_id), 124)

        ui.Workspace.set_dock_id_width(window1.dock_id, 50)
        ui.Workspace.set_dock_id_height(window1.dock_id, 50)
        ui.Workspace.set_dock_id_height(window4.dock_id, 50)

        await self.finalize_test()

        ui.Workspace.clear()

    def _window_visibility_callback(self, title, visible) -> None:
        self._visibility_changed_window_title = title
        self._visibility_changed_window_visible = visible

    def _window_visibility_callback2(self, title, visible) -> None:
        self._visibility_changed_window_title2 = title
        self._visibility_changed_window_visible2 = visible

    def _window_visibility_callback3(self, title, visible) -> None:
        self._visibility_changed_window_title3 = title
        self._visibility_changed_window_visible3 = visible

    async def test_workspace_window_visibility_callback(self):
        """Testing window visibility changed callback"""
        # test window create
        ui.Workspace.clear()
        self._visibility_changed_window_title = None
        self._visibility_changed_window_visible = False
        self._visibility_changed_window_title2 = None
        self._visibility_changed_window_visible2 = False
        self._visibility_changed_window_title3 = None
        self._visibility_changed_window_visible3 = False
        id1 = ui.Workspace.set_window_visibility_changed_callback(self._window_visibility_callback)

        id2 = ui.Workspace.set_window_visibility_changed_callback(self._window_visibility_callback2)
        id3 = ui.Workspace.set_window_visibility_changed_callback(self._window_visibility_callback3)

        window2 = ui.Window("visible_change", width=100, height=100)

        self.assertTrue(self._visibility_changed_window_title=="visible_change")
        self.assertTrue(self._visibility_changed_window_visible==True)

        # test window visible change to False
        self._visibility_changed_window_title = None
        self._visibility_changed_window_visible = True
        window2.visible = False
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(self._visibility_changed_window_title=="visible_change")
        self.assertTrue(self._visibility_changed_window_visible==False)

        # test window visible change to true
        self._visibility_changed_window_title = None
        self._visibility_changed_window_visible = False
        window2.visible = True
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(self._visibility_changed_window_title=="visible_change")
        self.assertTrue(self._visibility_changed_window_visible==True)

        # test another callback function change to false
        self._visibility_changed_window_title2 = None
        self._visibility_changed_window_visible2 = True
        window2.visible = False
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(self._visibility_changed_window_title2=="visible_change")
        self.assertTrue(self._visibility_changed_window_visible2==False)

        # test another callback function change change to true
        self._visibility_changed_window_title2 = None
        self._visibility_changed_window_visible2 = False
        window2.visible = True
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(self._visibility_changed_window_title2=="visible_change")
        self.assertTrue(self._visibility_changed_window_visible2==True)

        # Add more window visible change to true and wait more frames
        self._visibility_changed_window_title = None
        self._visibility_changed_window_visible = False
        window3 = ui.Window("visible_change3", width=100, height=100)
        for i in range(10):
            await omni.kit.app.get_app().next_update_async()
        self.assertTrue(self._visibility_changed_window_title=="visible_change3")
        self.assertTrue(self._visibility_changed_window_visible==True)

        # Add more window visible change to False
        self._visibility_changed_window_title = None
        self._visibility_changed_window_visible = False
        window3.visible = False
        for i in range(10):
            await omni.kit.app.get_app().next_update_async()
        self.assertTrue(self._visibility_changed_window_title=="visible_change3")
        self.assertTrue(self._visibility_changed_window_visible==False)

        # test remove_window_visibility_changed_callback
        self._visibility_changed_window_title = None
        self._visibility_changed_window_visible = True
        self._visibility_changed_window_title2 = None
        self._visibility_changed_window_visible2 = True
        ui.Workspace.remove_window_visibility_changed_callback(id1)

        window2.visible = False
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(self._visibility_changed_window_title==None)
        self.assertTrue(self._visibility_changed_window_visible==True)
        self.assertTrue(self._visibility_changed_window_title2=="visible_change")
        self.assertTrue(self._visibility_changed_window_visible2==False)

        # OM-60640: Notice that remove one change callback not effect other callbacks
        self._visibility_changed_window_visible = False
        self._visibility_changed_window_title2 = None
        self._visibility_changed_window_visible2 = False
        self._visibility_changed_window_title3 = None
        self._visibility_changed_window_visible3 = False
        window2.visible = True
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(self._visibility_changed_window_title==None)
        self.assertTrue(self._visibility_changed_window_visible==False)
        self.assertTrue(self._visibility_changed_window_title2=="visible_change")
        self.assertTrue(self._visibility_changed_window_visible2==True)
        self.assertTrue(self._visibility_changed_window_title3=="visible_change")
        self.assertTrue(self._visibility_changed_window_visible3==True)
        ui.Workspace.remove_window_visibility_changed_callback(id2)
        ui.Workspace.remove_window_visibility_changed_callback(id3)

    async def test_workspace_deferred_dock_in(self):
        """Testing window layout without hiding the windows"""
        ui.Workspace.clear()
        await self.create_test_area(256, 256)

        ui_main_window = ui.MainWindow()
        ui_main_window.main_menu_bar.visible = False
        window1 = ui.Window("First", width=100, height=100)
        window2 = ui.Window("Second", width=100, height=100)

        await omni.kit.app.get_app().next_update_async()

        main_dockspace = ui.Workspace.get_window("DockSpace")
        window1.dock_in(main_dockspace, ui.DockPosition.SAME)
        window2.dock_in(window1, ui.DockPosition.BOTTOM)

        await omni.kit.app.get_app().next_update_async()

        # Save the layout
        layout = ui.Workspace.dump_workspace()

        window2.deferred_dock_in("First")

        # Restore_workspace should reset deferred_dock_in
        ui.Workspace.restore_workspace(layout, True)

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_freeze(self):
        PRESENT_THREAD = "/exts/omni.kit.renderer.core/present/enabled"

        settings = carb.settings.get_settings()
        present_thread_enabled = settings.get(PRESENT_THREAD)
        settings.set(PRESENT_THREAD, True)

        window = await self.create_test_window()

        with window.frame:
            ui.Label("NVIDIA Omniverse")

        # Get IRenderer
        renderer = omni.kit.renderer.bind.get_renderer_interface()

        # Get default IAppWindow
        app_window_factory = omni.appwindow.acquire_app_window_factory_interface()
        app_window = app_window_factory.get_app_window()

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # Draw freeze the window
        renderer.draw_freeze_app_window(app_window, True)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        with window.frame:
            ui.Label("Something Else")

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

        renderer.draw_freeze_app_window(app_window, False)

        await omni.kit.app.get_app().next_update_async()
        settings.set(PRESENT_THREAD, present_thread_enabled)
        await omni.kit.app.get_app().next_update_async()

    async def test_disable_all_windows(self):
        ui.Workspace.clear()
        await self.create_test_area(200, 200)

        ui_main_window = ui.MainWindow()
        ui_main_window.main_menu_bar.visible = False
        window1 = ui.Window("1", width=100, height=100, position_x=0, position_y=0)
        window2 = ui.Window("2", width=100, height=100, position_x=100, position_y=0)
        window3 = ui.Window("3", width=100, height=100, position_x=0, position_y=100)
        window4 = ui.Window("4", width=100, height=100, position_x=100, position_y=100)

        await self.wait_n_updates()
        await self.capture_and_compare(golden_img_name="test_workspace_windows_active.png")

        for window in omni.ui.Workspace.get_windows():
            if hasattr(window, "set_active"):
                window.set_active(False)

        await self.wait_n_updates()
        await self.capture_and_compare(golden_img_name="test_workspace_windows_inactive.png")

        for window in omni.ui.Workspace.get_windows():
            if hasattr(window, "set_active"):
                window.set_active(True)

        await self.wait_n_updates()
        await self.capture_and_compare(golden_img_name="test_workspace_windows_reactive.png")

        ui.Workspace.clear()

class WorkspaceCallbacks(omni.kit.test.AsyncTestCase):
    def _window_created_callback(self, w) -> None:
        self._created = w

    async def test_window_creation_callback(self):
        """Testing window creation callback"""
        self._created = None
        ui.Workspace.set_window_created_callback(self._window_created_callback)
        window1 = ui.Window("First", width=100, height=100)
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(self._created == window1)
