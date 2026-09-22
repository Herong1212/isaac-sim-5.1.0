import omni.kit.test
import omni.kit.app
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.actions.core import get_action_registry
import omni.ui as ui
import omni.kit.ui_test as ui_test
from omni.kit.ui_test import Vec2
from pathlib import Path

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")

ACTION_SHOW_WINDOW = "Show Actions Window"
ACTION_HIDE_WINDOW = "Hide Actions Window"

class TestActionsWindow(OmniUiTest):
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

        self._ext_id = "omni.kit.actions.window.tests"
        self.__register_test_actions()
 
        window = ui.Workspace.show_window("Actions")
        await omni.kit.app.get_app().next_update_async()
        window = ui.Workspace.get_window("Actions")
        await self.docked_test_window(window=window, width=1280, height=400, block_devices=False)

    async def tearDown(self):
        # Deregister all the test actions.
        self._action_registry.deregister_action(self._ext_id, ACTION_SHOW_WINDOW)
        self._action_registry.deregister_action(self._ext_id, ACTION_HIDE_WINDOW)

        self._action_registry = None

    async def test_1_general_window(self):
        # When startup, no actions loaded
        result_name = "test_action_window_general"
        try:
            from omni.kit.widget.searchfield import SearchField
            result_name += "_with_search"

            # Wait for search icon loaded
            for i in range(5):
                await omni.kit.app.get_app().next_update_async()
        except ImportError:
            pass
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name=f"{result_name}.png")

    async def test_2_search(self):
        try:
            from omni.kit.widget.searchfield import SearchField
            # Actions reloaded, we can see register actions now
            # Focus on search bar
            await ui_test.emulate_mouse_move_and_click(Vec2(50, 17))
            # Search "Show"
            await ui_test.emulate_char_press("Show\n")
            await ui_test.emulate_mouse_move_and_click(Vec2(0, 0))
            await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_action_window_search.png")
        except ImportError:
            pass

    async def test_3_search_clean(self):
        try:
            from omni.kit.widget.searchfield import SearchField
            # Focus on search bar
            await ui_test.emulate_mouse_move_and_click(Vec2(50, 17))
            # Clean search
            await ui_test.emulate_mouse_move_and_click(Vec2(1263, 17))
            await ui_test.emulate_mouse_move_and_click(Vec2(0, 0))

            await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_action_window_search_clean.png")
        except ImportError:
            pass

    def __register_test_actions(self):
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
