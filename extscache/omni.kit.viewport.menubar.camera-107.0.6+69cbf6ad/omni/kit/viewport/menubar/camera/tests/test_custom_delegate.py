from pathlib import Path
from typing import Optional, TYPE_CHECKING

import carb.settings
import omni.kit.ui_test as ui_test
from omni.kit.ui_test import Vec2
from omni.kit.viewport.menubar.camera import AbstractCameraButtonDelegate, AbstractCameraMenuItemDelegate
from omni.kit.viewport.utility import get_active_viewport_window
from omni.ui.tests.test_base import OmniUiTest
import omni.usd
import omni.ui as ui
from pxr import Sdf

if TYPE_CHECKING:
    from omni.kit.widget.viewport.api import ViewportAPI

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")
TEST_WIDTH, TEST_HEIGHT = 300, 300


class MyButtonDelegate(AbstractCameraButtonDelegate):
    def build_widget(self, parent_id: int, viewport_api: "ViewportAPI", camera_path: Sdf.Path) -> Optional[ui.Widget]:
        widget = ui.HStack()
        with widget:
            ui.Spacer(width=4)
            ui.Label("Custom", style={"color": 0xFFFF00FF})
        return widget

    def on_parent_destroyed(self, parent_id: int) -> None:
        return

    def on_camera_path_changed(self, parent_id: int, camera_path: Sdf.Path):
        return


class MyItemDelegate(AbstractCameraMenuItemDelegate):
    def build_widget(self, parent_id: int, viewport_api: "ViewportAPI", camera_path: Sdf.Path) -> Optional[ui.Widget]:
        widget = ui.HStack()
        with widget:
            ui.Spacer(width=4)
            ui.Label("Custom", style={"color": 0xFF0000FF})
        return widget

    def on_parent_destroyed(self, parent_id: int) -> None:
        return

    def on_camera_path_changed(self, parent_id: int, camera_path: Sdf.Path):
        return


class ToggleExpansionState():
    def __init__(self):
        self.__settings = carb.settings.get_settings()
        self.__key = "/persistent/exts/omni.kit.viewport.menubar.camera/expand"
        self.__restore_value = self.__settings.get(self.__key)

    def set(self, value: bool):  # noqa: A003
        self.__settings.set(self.__key, value)

    def __del__(self):
        self.__settings.set(self.__key, self.__restore_value)


class TestCameraCustomDelegate(OmniUiTest):
    async def setUp(self):
        await super().setUp()

        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()
        context = omni.usd.get_context()

        self.__button_delegate = MyButtonDelegate()
        self.__item_delegate = MyItemDelegate()

        # Create a new stage to show camera parameters
        await context.new_stage_async()

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        await self.wait_n_updates()

        self._viewport_window = get_active_viewport_window()
        self._viewport_window.position_x = 0
        self._viewport_window.position_y = 0

    async def tearDown(self):
        self.__button_delegate.destroy()
        self.__item_delegate.destroy()
        await super().tearDown()

    async def finalize_test(self, golden_img_name: str):
        await self.wait_n_updates()
        await super().finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name=golden_img_name)
        await self.wait_n_updates()

    async def test_custom_button_delegate(self):
        expand_state = ToggleExpansionState()
        expand_state.set(False)
        await ui_test.emulate_mouse_move_and_click(Vec2(40, 40))
        await self.wait_n_updates()
        try:
            await self.finalize_test(golden_img_name="menubar_custom_button_delegate.png")
        finally:
            del expand_state
            await ui_test.emulate_mouse_move_and_click(Vec2(0, 0))
