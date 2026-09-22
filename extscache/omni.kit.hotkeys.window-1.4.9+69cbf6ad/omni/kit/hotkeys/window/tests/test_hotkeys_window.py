from pathlib import Path
from omni.kit.actions.core import get_action_registry
import omni.kit.app
import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.hotkeys.core import get_hotkey_registry, HotkeyFilter
import omni.ui as ui
import omni.kit.ui_test as ui_test
from omni.kit.ui_test import Vec2

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")

ACTION_SHOW_WINDOW = "Show"
ACTION_HIDE_WINDOW = "Hide"


class TestHotkeysWindow(OmniUiTest):
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()
        self._action_registry = None

        self._ext_id = "hotkeys"
        self.__register_test_hotkeys()

        window = ui.Workspace.get_window("Hotkeys")
        window.visible = True  # just in case another test has turned it off
        await self.docked_test_window(window=window, width=1280, height=400, block_devices=False)

    async def tearDown(self):
        # Deregister all the test hotkeys
        self._hotkey_registry.deregister_hotkey(self._ext_id, "CTL+S")
        self._hotkey_registry.deregister_hotkey(self._ext_id, "ALT+H")

        # Deregister all the test actions.
        self._action_registry.deregister_action(self._ext_id, ACTION_SHOW_WINDOW)
        self._action_registry.deregister_action(self._ext_id, ACTION_HIDE_WINDOW)

        self._action_registry = None

    async def test_1_general_window(self):
        # When startup, no actions loaded
        # Expand
        await ui_test.emulate_mouse_move_and_click(Vec2(13, 67))

        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_hotkey_window_general_with_search.png")

    async def test_2_search(self):
        # Actions reloaded, we can see register actions now
        # Focus on search bar
        await ui_test.emulate_mouse_move_and_click(Vec2(50, 17))
        # Search "Show"
        await ui_test.emulate_char_press("Show\n")
        await ui_test.emulate_mouse_move_and_click(Vec2(0, 0))
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_hotkey_window_search.png")

    async def test_3_search_clean(self):
        # Focus on search bar
        await ui_test.emulate_mouse_move_and_click(Vec2(50, 17))
        # Clean search
        await ui_test.emulate_mouse_move_and_click(Vec2(1214, 17))
        await ui_test.emulate_mouse_move_and_click(Vec2(0, 0))

        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_hotkey_window_search_clean.png")

    def __register_test_hotkeys(self):
        self._action_registry = get_action_registry()

        self._action_registry.register_action(
            self._ext_id,
            ACTION_SHOW_WINDOW,
            lambda: None,
            display_name=ACTION_SHOW_WINDOW,
            description=ACTION_SHOW_WINDOW,
            tag="Actions",
        )

        self._action_registry.register_action(
            self._ext_id,
            ACTION_HIDE_WINDOW,
            lambda: None,
            display_name=ACTION_HIDE_WINDOW,
            description=ACTION_HIDE_WINDOW,
            tag="Actions",
        )

        self._context_filter = HotkeyFilter(context="Test Context")
        self._window_filter = HotkeyFilter(windows=["Viewport"])
        self._hotkey_registry = get_hotkey_registry()
        self._hotkey_registry.register_hotkey(self._ext_id, "CTL+S", self._ext_id, ACTION_SHOW_WINDOW)
        self._hotkey_registry.register_hotkey(self._ext_id, "ALT+H", self._ext_id, ACTION_HIDE_WINDOW)
        self._hotkey_registry.register_hotkey(self._ext_id, "H", self._ext_id, ACTION_HIDE_WINDOW, filter=self._context_filter)
        self._hotkey_registry.register_hotkey(self._ext_id, "S", self._ext_id, ACTION_SHOW_WINDOW, filter=self._context_filter)
        self._hotkey_registry.register_hotkey(self._ext_id, "H", self._ext_id, ACTION_HIDE_WINDOW, filter=self._window_filter)
        self._hotkey_registry.register_hotkey(self._ext_id, "S", self._ext_id, ACTION_SHOW_WINDOW, filter=self._window_filter)
