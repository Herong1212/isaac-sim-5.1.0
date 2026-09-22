from pathlib import Path
import sys
import unittest

import carb.input
import omni.kit.app
import omni.kit.test
from omni.kit.test.teamcity import is_running_in_teamcity
from omni.ui.tests.test_base import OmniUiTest
import omni.kit.ui_test as ui_test
from omni.kit.ui_test import Vec2
import omni.ui as ui
import omni.usd

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")
TEST_WIDTH, TEST_HEIGHT = 600, 600


class TestSettingMenuWindow(OmniUiTest):
    async def setUp(self):
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)
        await omni.kit.app.get_app().next_update_async()

    async def test_navigation(self):
        await self.__show_subitem("menubar_setting_navigation.png", 86)

    async def test_selection(self):
        await self.__show_subitem("menubar_setting_selection.png", 106)

    async def test_grid(self):
        await self.__show_subitem("menubar_setting_grid.png", 126)

    async def test_gizmo(self):
        await self.__show_subitem("menubar_setting_gizmo.png", 146)

    @unittest.skipIf(
        (sys.platform == "linux" and is_running_in_teamcity()),
        "OM-64377: Delegate for RadioMenuCollection does not work in Linux",
    )
    async def test_viewport(self):
        await omni.usd.get_context().new_stage_async()
        from omni.kit.viewport.utility import get_active_viewport
        vp = get_active_viewport()

        try:
            await self.__show_subitem("menubar_setting_viewport.png", 166)

            # Change resolution to 1080p
            vp.resolution = (1920, 1080)
            await self.__show_subitem("menubar_setting_viewport_1080p.png", 166)
        finally:
            # Revert resolution
            vp.resolution = (1280, 720)
            await omni.kit.app.get_app().next_update_async()

    async def test_viewport_ui(self):
        await self.__show_subitem("menubar_setting_viewport_ui.png", 186)

    async def test_viewport_manipulate(self):
        await self.__show_subitem("menubar_setting_viewport_manipulator.png", 206)

    async def test_preference(self):
        async def show_preference():
            await ui_test.emulate_mouse_click()
            for _ in range(4):
                await omni.kit.app.get_app().next_update_async()
            pref_window = ui.Workspace.get_window("Preferences")
            self.assertIsNotNone(pref_window)
            self.assertTrue(pref_window.visible)
            pref_window.visible = False

        await self.__do_ui_test(show_preference, 256)

    async def test_reset_item(self):
        settings = carb.settings.get_settings()
        cam_vel = settings.get("/persistent/app/viewport/camMoveVelocity")
        in_enabled = settings.get("/persistent/app/viewport/camInertiaEnabled")

        settings.set("/persistent/app/viewport/camMoveVelocity", cam_vel * 2)
        settings.set("/persistent/app/viewport/camInertiaEnabled", not in_enabled)
        try:
            await self.__do_ui_test(ui_test.emulate_mouse_click, 225)

            self.assertEqual(settings.get("/persistent/app/viewport/camMoveVelocity"), cam_vel)
            self.assertEqual(settings.get("/persistent/app/viewport/camInertiaEnabled"), in_enabled)
        finally:
            settings.set("/persistent/app/viewport/camMoveVelocity", cam_vel)
            settings.set("/persistent/app/viewport/camInertiaEnabled", in_enabled)

    async def __show_subitem(self, golden_img_name: str, y: int) -> None:
        async def gloden_compare():
            await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name=golden_img_name)

        await self.__do_ui_test(gloden_compare, y)

    async def __do_ui_test(self, test_operation, y: int, frame_wait: int = 3) -> None:
        # Enable mouse input
        app = omni.kit.app.get_app()
        app_window = omni.appwindow.get_default_app_window()
        for device in [carb.input.DeviceType.MOUSE]:
            app_window.set_input_blocking_state(device, None)

        try:
            await ui_test.emulate_mouse_move(Vec2(20, 46), human_delay_speed=4)
            await ui_test.emulate_mouse_click()

            await ui_test.emulate_mouse_move(Vec2(20, y))

            for _ in range(frame_wait):
                await app.next_update_async()

            await test_operation()

        finally:
            for _ in range(frame_wait):
                await app.next_update_async()

            await ui_test.emulate_mouse_move(Vec2(300, 26))
            await ui_test.emulate_mouse_click()

            for _ in range(frame_wait):
                await app.next_update_async()
