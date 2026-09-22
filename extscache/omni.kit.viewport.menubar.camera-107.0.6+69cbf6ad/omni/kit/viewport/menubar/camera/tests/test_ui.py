import functools
from pathlib import Path

import carb.input
import omni.kit.app
import omni.appwindow
import omni.kit.test
import omni.kit.ui_test as ui_test
from omni.kit.ui_test import Vec2
from omni.kit.viewport.menubar.camera import get_instance as _get_menubar_extension
from omni.kit.viewport.menubar.camera import SingleCameraMenuItemBase
from omni.kit.viewport.utility import get_active_viewport, get_active_viewport_window
from omni.ui.tests.test_base import OmniUiTest
import omni.usd
import omni.ui as ui
from pxr import Sdf, Usd, UsdGeom


CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")
TEST_WIDTH, TEST_HEIGHT = 850, 300


class ToggleExpansionState():
    def __init__(self):
        self.__settings = carb.settings.get_settings()
        self.__key = "/persistent/exts/omni.kit.viewport.menubar.camera/expand"
        self.__restore_value = self.__settings.get(self.__key)

    def set(self, value: bool):  # noqa: A003
        self.__settings.set(self.__key, value)

    def __del__(self):
        self.__settings.set(self.__key, self.__restore_value)


class TestCameraMenuWindow(OmniUiTest):
    async def setUp(self):
        await super().setUp()

        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()
        context = omni.usd.get_context()

        # Create a new stage to show camera parameters
        await context.new_stage_async()

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        await self.wait_n_updates()

        self._viewport_window = get_active_viewport_window()
        self._viewport_window.position_x = 0
        self._viewport_window.position_y = 0

    async def tearDown(self):
        await super().tearDown()

    async def finalize_test(self, golden_img_name: str):
        await self.wait_n_updates()
        await super().finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name=golden_img_name)
        await self.wait_n_updates()

    async def test_general(self):
        await self.finalize_test(golden_img_name="menubar_camera.png")

    async def test_lock(self):
        viewport = get_active_viewport()
        viewport.camera_path = UsdGeom.Camera.Define(viewport.stage, '/NewCamera').GetPath()

        path = Sdf.Path(viewport.camera_path).AppendProperty("omni:kit:cameraLock")
        omni.kit.commands.execute(
            'ChangePropertyCommand',
            prop_path=path,
            value=True,
            prev=False,
            timecode=Usd.TimeCode.Default(),
            type_to_create_if_not_exist=Sdf.ValueTypeNames.Bool
        )

        try:
            await omni.kit.app.get_app().next_update_async()
            await self.finalize_test(golden_img_name="menubar_camera_locked.png")
        finally:
            omni.kit.commands.execute(
                'ChangePropertyCommand',
                prop_path=path,
                value=False,
                prev=False,
                timecode=Usd.TimeCode.Default(),
                type_to_create_if_not_exist=Sdf.ValueTypeNames.Bool
            )

    async def test_collapsed(self):
        """Test collapse/expand functionality of additional camera properties"""
        expand_state = ToggleExpansionState()

        try:
            expand_state.set(False)
            await self.finalize_test(golden_img_name="menubar_camera_collpased.png")

            expand_state.set(True)
            await self.finalize_test(golden_img_name="menubar_camera_expanded.png")
        finally:
            del expand_state
            await self.wait_n_updates()

    async def test_resize_4_in_1(self):
        restore_width = self._viewport_window.width
        expand_state = ToggleExpansionState()
        expand_state.set(True)
        await self.wait_n_updates(2)

        try:
            # resize 1: contract settings
            self._viewport_window.width = 200
            await self.wait_n_updates(5)
            await self.finalize_test(golden_img_name="menubar_camera_resize_contract_settings.png")

            # resize 2: contract text
            self._viewport_window.width = 60
            await self.wait_n_updates(5)
            await self.finalize_test(golden_img_name="menubar_camera_resize_contract_text.png")

            # resize 3 : expand text
            self._viewport_window.width = 200
            await self.wait_n_updates(5)
            await self.finalize_test(golden_img_name="menubar_camera_resize_expand_text.png")

            # resize 4 : expand settings
            self._viewport_window.width = restore_width
            await self.wait_n_updates(5)
            await self.finalize_test(golden_img_name="menubar_camera_resize_expand_settings.png")

        finally:
            del expand_state
            self._viewport_window.width = restore_width
            await self.wait_n_updates()

    async def test_user_menu_item(self):

        def __create_first(viewport_context, root):
            ui.MenuItem("This is first custom menu item")

        def __create_second(viewport_context, root):
            ui.MenuItem("This is second custom menu item")

        expand_state = ToggleExpansionState()
        instance = omni.kit.viewport.menubar.camera.get_instance()
        try:
            instance.register_menu_item(__create_second, order=20)
            instance.register_menu_item(__create_first, order=10)
            expand_state.set(True)

            await self.__click_root_menu_item()
            await self.finalize_test(golden_img_name="menubar_camera_custom.png")
            await ui_test.emulate_mouse_click()

            expand_state.set(False)
            await self.__click_root_menu_item()
            await self.finalize_test(golden_img_name="menubar_camera_custom_collapsed.png")

        finally:
            await ui_test.emulate_mouse_click()

            instance.deregister_menu_item(__create_first)
            instance.deregister_menu_item(__create_second)
            del expand_state

            await self.wait_n_updates()

    async def __click_root_menu_item(self):
        # Enable mouse input
        app_window = omni.appwindow.get_default_app_window()
        for device in [carb.input.DeviceType.MOUSE]:
            app_window.set_input_blocking_state(device, None)

        await ui_test.emulate_mouse_move(Vec2(40, 40))
        await ui_test.emulate_mouse_click()
        await self.wait_n_updates()

    async def test_camera_menu_with_custom_type(self):

        menu_option_clicked = 0

        def _single_camera_menu_item(*args, **kwargs):
            class SingleCameraMenuItem(SingleCameraMenuItemBase):
                def _option_clicked(self):
                    nonlocal menu_option_clicked
                    menu_option_clicked += 1

            return SingleCameraMenuItem(*args, **kwargs)

        await self.__click_root_menu_item()

        self.assertEqual(0, menu_option_clicked)

        await ui_test.emulate_mouse_move(Vec2(140, 110))
        await ui_test.emulate_mouse_click()
        await self.wait_n_updates()

        self.assertEqual(0, menu_option_clicked)

        extension = _get_menubar_extension()
        try:
            extension.register_menu_item_type(
                functools.partial(_single_camera_menu_item)
            )
            await self.wait_n_updates()
            await ui_test.emulate_mouse_click()
            await self.wait_n_updates()

            self.assertEqual(1, menu_option_clicked)
        finally:
            extension.register_menu_item_type(None)

            # Call it again to hide popup menu window
            await self.__click_root_menu_item()

    async def test_external_cam_change(self):
        # Get the Viewport and change the active camera
        viewport = get_active_viewport()
        orig_cam_path = viewport.camera_path
        new_cam_path = Sdf.Path('/OmniverseKit_Top')
        self.assertNotEqual(orig_cam_path, new_cam_path)

        try:
            viewport.camera_path = new_cam_path

            # Change should be reflected in UI
            await self.wait_n_updates(10)
            await self.finalize_test(golden_img_name="menubar_camera_external_cam_change.png")
        finally:
            viewport.camera_path = orig_cam_path
