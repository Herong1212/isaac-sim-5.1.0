import unittest
import pathlib
import carb
import omni.kit.test
import omni.appwindow
import omni.ui as ui
from omni.kit import ui_test
from pxr import UsdShade
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.test_suite.helpers import arrange_windows


class TestMouseUIHelper(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        self._test_path = pathlib.Path(extension_path).joinpath("data").joinpath("tests")
        viewport_window = await arrange_windows()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def _simulate_mouse(self, data):
        mouse = omni.appwindow.get_default_app_window().get_mouse()
        input_provider = carb.input.acquire_input_provider()

        window_width = ui.Workspace.get_main_window_width()
        window_height = ui.Workspace.get_main_window_height()
        for type, x, y in data:
            input_provider.buffer_mouse_event(mouse, type, (x / window_width, y / window_height), 0, (x, y))
            await ui_test.human_delay(10)

    async def _simulate_mouse_steps(self, start_pos, end_pos, num_steps=8):
        mouse = omni.appwindow.get_default_app_window().get_mouse()
        input_provider = carb.input.acquire_input_provider()

        window_width = ui.Workspace.get_main_window_width()
        window_height = ui.Workspace.get_main_window_height()

        x_steps = (end_pos[0] - start_pos[0]) / num_steps
        y_steps = (end_pos[1] - start_pos[1]) / num_steps
        for i in range(0, num_steps):
            await self._simulate_mouse([ (carb.input.MouseEventType.MOVE, (start_pos[0]+x_steps*i), (start_pos[1]+y_steps*i))])
        await self._simulate_mouse([(carb.input.MouseEventType.MOVE, end_pos[0], end_pos[1])])

    async def _debug_capture(self, image_name: str): # pragma: no cover
        from pathlib import Path
        import omni.renderer_capture

        capture_next_frame = omni.renderer_capture.acquire_renderer_capture_interface().capture_next_frame_swapchain(image_name)
        await omni.kit.app.get_app().next_update_async()
        wait_async_capture = omni.renderer_capture.acquire_renderer_capture_interface().wait_async_capture()
        await omni.kit.app.get_app().next_update_async()

