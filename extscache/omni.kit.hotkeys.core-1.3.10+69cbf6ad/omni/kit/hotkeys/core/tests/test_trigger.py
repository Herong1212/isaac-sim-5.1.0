import omni.kit.test
import omni.kit.ui_test as ui_test
import carb.input

from omni.kit.hotkeys.core import get_hotkey_context, get_hotkey_registry, HotkeyFilter, KeyCombination
from omni.kit.actions.core import get_action_registry

SETTING_ALLOW_LIST = "/exts/omni.kit.hotkeys.core/allow_list"

TEST_HOTKEY_EXT_ID = "omni.kit.hotkey.test.hotkey"
TEST_ACTION_EXT_ID = "omni.kit.hotkey.test.action"
TEST_CONTEXT_PRESS_ACTION_ID = "hotkey_test_context_press_action"
TEST_CONTEXT_RELEASE_ACTION_ID = "hotkey_test_context_release_action"
TEST_GLOBAL_PRESS_ACTION_ID = "hotkey_test_global_press_action"
TEST_GLOBAL_RELEASE_ACTION_ID = "hotkey_test_global_release_action"
TEST_CONTEXT_NAME = "test_context@omni.kit.hotkey.test"
TEST_HOTKEY = "CTRL+T"

_context_press_action_count = 0
_context_release_action_count = 0
_global_press_action_count = 0
_global_release_action_count = 0


def context_press_action_func():
    global _context_press_action_count
    _context_press_action_count += 1


def context_release_action_func():
    global _context_release_action_count
    _context_release_action_count += 1


def global_press_action_func():
    global _global_press_action_count
    _global_press_action_count += 1


def global_release_action_func():
    global _global_release_action_count
    _global_release_action_count += 1


class TestTrigger(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._hotkey_registry = get_hotkey_registry()
        self._hotkey_context = get_hotkey_context()
        self._action_registry = get_action_registry()
        self._filter = HotkeyFilter(context=TEST_CONTEXT_NAME)

        await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.T, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL)
        await ui_test.human_delay()
        self.assertEqual(_context_press_action_count, 0)
        self.assertEqual(_context_release_action_count, 0)
        self.assertEqual(_global_press_action_count, 0)
        self.assertEqual(_global_release_action_count, 0)

        # Hotkey with context
        self._action_registry.register_action(TEST_ACTION_EXT_ID, TEST_CONTEXT_PRESS_ACTION_ID, context_press_action_func)
        hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_CONTEXT_PRESS_ACTION_ID, filter=self._filter)
        self.assertIsNotNone(hotkey)

        # Hotkey with context with key released
        self._action_registry.register_action(TEST_ACTION_EXT_ID, TEST_CONTEXT_RELEASE_ACTION_ID, context_release_action_func)
        hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, KeyCombination(TEST_HOTKEY, trigger_press=False), TEST_ACTION_EXT_ID, TEST_CONTEXT_RELEASE_ACTION_ID, filter=self._filter)
        self.assertIsNotNone(hotkey)

        # Global pressed hotkey
        self._action_registry.register_action(TEST_ACTION_EXT_ID, TEST_GLOBAL_PRESS_ACTION_ID, global_press_action_func)
        hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_GLOBAL_PRESS_ACTION_ID)
        self.assertIsNotNone(hotkey)

        # Global released hotkey
        self._action_registry.register_action(TEST_ACTION_EXT_ID, TEST_GLOBAL_RELEASE_ACTION_ID, global_release_action_func)
        hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, KeyCombination(TEST_HOTKEY, trigger_press=False), TEST_ACTION_EXT_ID, TEST_GLOBAL_RELEASE_ACTION_ID)
        self.assertIsNotNone(hotkey)

    # After running each test
    async def tearDown(self):
        self._hotkey_context = None
        self._hotkey_registry.deregister_all_hotkeys_for_extension(TEST_HOTKEY_EXT_ID)
        self._hotkey_registry = None
        self._action_registry.deregister_all_actions_for_extension(TEST_ACTION_EXT_ID)
        self._action_registry = None

    async def test_hotkey_in_context(self):
        # Trigger hotkey in context
        self._hotkey_context.push(TEST_CONTEXT_NAME)

        await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.T, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL)
        await ui_test.human_delay()
        self.assertEqual(_context_press_action_count, 1)
        self.assertEqual(_context_release_action_count, 1)
        self.assertEqual(_global_press_action_count, 0)
        self.assertEqual(_global_release_action_count, 0)
        self._hotkey_context.pop()

        # Trigger hotkey in global
        await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.T, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL)
        await ui_test.human_delay()
        self.assertEqual(_context_press_action_count, 1)
        self.assertEqual(_context_release_action_count, 1)
        self.assertEqual(_global_press_action_count, 1)
        self.assertEqual(_global_release_action_count, 1)

    async def test_allow_list(self):
        global _global_press_action_count, _global_release_action_count
        settings = carb.settings.get_settings()
        try:
            # Do not trigger since key not in allow list
            settings.set(SETTING_ALLOW_LIST, ["F1"])
            await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.T, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL)
            await ui_test.human_delay()
            self.assertEqual(_global_press_action_count, 0)
            self.assertEqual(_global_release_action_count, 0)

            # Trigger since key in allow list
            settings.set(SETTING_ALLOW_LIST, ["CTRL + T"])
            await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.T, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL)
            await ui_test.human_delay()
            self.assertEqual(_global_press_action_count, 1)
            self.assertEqual(_global_release_action_count, 1)

            # Trigger since no allow list
            settings.set(SETTING_ALLOW_LIST, [])
            await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.T, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL)
            await ui_test.human_delay()
            self.assertEqual(_global_press_action_count, 2)
            self.assertEqual(_global_release_action_count, 2)
        finally:
            settings.set(SETTING_ALLOW_LIST, [])
            _global_press_action_count = 0
            _global_release_action_count = 0
