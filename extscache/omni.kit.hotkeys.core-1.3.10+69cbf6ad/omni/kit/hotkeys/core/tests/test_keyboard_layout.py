import omni.kit.test
import omni.kit.ui_test as ui_test
import carb.input

from omni.kit.hotkeys.core import get_hotkey_context, get_hotkey_registry, HotkeyFilter
from omni.kit.actions.core import get_action_registry

TEST_HOTKEY_EXT_ID = "omni.kit.hotkey.test.hotkey"
TEST_ACTION_EXT_ID = "omni.kit.hotkey.test.action"
TEST_CONTEXT_PRESS_ACTION_ID = "hotkey_test_context_press_action"
TEST_CONTEXT_RELEASE_ACTION_ID = "hotkey_test_context_release_action"
TEST_GLOBAL_PRESS_ACTION_ID_UNDO = "hotkey_test_global_press_action_undo"
TEST_GLOBAL_RELEASE_ACTION_ID = "hotkey_test_global_release_action"
TEST_GLOBAL_PRESS_ACTION_ID_REDO = "hotkey_test_global_press_action_redo"
TEST_CONTEXT_NAME = "test_context@omni.kit.hotkey.test"
TEST_HOTKEY_UNDO = "CTRL+Z"
TEST_HOTKEY_REDO = "CTRL+Y"

_global_press_action_undo_count = 0
_global_press_action_redo_count = 0


def global_press_action_undo_func():
    global _global_press_action_undo_count
    _global_press_action_undo_count += 1


def global_press_action_redo_func():
    global _global_press_action_redo_count
    _global_press_action_redo_count += 1


class TestKeyboardLayout(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._hotkey_registry = get_hotkey_registry()
        self._hotkey_context = get_hotkey_context()
        self._action_registry = get_action_registry()
        self._filter = HotkeyFilter(context=TEST_CONTEXT_NAME)

        self._action_registry.register_action(TEST_ACTION_EXT_ID, TEST_GLOBAL_PRESS_ACTION_ID_UNDO, global_press_action_undo_func)
        self._action_registry.register_action(TEST_ACTION_EXT_ID, TEST_GLOBAL_PRESS_ACTION_ID_REDO, global_press_action_redo_func)
        self._hotkey_registry.clear_storage()

        await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.Z, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL)
        await ui_test.human_delay()

    # After running each test
    async def tearDown(self):
        self._hotkey_context = None
        self._hotkey_registry.deregister_all_hotkeys_for_extension(TEST_HOTKEY_EXT_ID)
        self._hotkey_registry = None
        self._action_registry.deregister_all_actions_for_extension(TEST_ACTION_EXT_ID)
        self._action_registry = None

    async def test_hotkey_register_with_new_layout(self):
        self._hotkey_registry.switch_layout("German QWERTZ")

        # With new keyboard layout, key combination should be changed when register
        hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY_UNDO, TEST_ACTION_EXT_ID, TEST_GLOBAL_PRESS_ACTION_ID_UNDO)
        self.assertIsNotNone(hotkey)
        self.assertEqual(hotkey.key_combination.as_string, "CTRL + Y")

        await self.__verify_trigger_undo(carb.input.KeyboardInput.Z, False)
        await self.__verify_trigger_undo(carb.input.KeyboardInput.Y, True)

    async def test_hotkey_switch_layout(self):
        self._hotkey_registry.switch_layout("U.S. QWERTY")

        # Global pressed hotkey
        undo_hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY_UNDO, TEST_ACTION_EXT_ID, TEST_GLOBAL_PRESS_ACTION_ID_UNDO)
        redo_hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY_REDO, TEST_ACTION_EXT_ID, TEST_GLOBAL_PRESS_ACTION_ID_REDO)
        self.assertIsNotNone(undo_hotkey)
        self.assertIsNotNone(redo_hotkey)

        # Trigger hotkey in global, default layout, should trigger
        await self.__verify_trigger_undo(carb.input.KeyboardInput.Z, True)
        await self.__verify_trigger_redo(carb.input.KeyboardInput.Y, True)

        # Switch layout
        self._hotkey_registry.switch_layout("German QWERTZ")
        self.assertEqual(undo_hotkey.key_combination.as_string, "CTRL + Y")
        self.assertEqual(redo_hotkey.key_combination.as_string, "CTRL + Z")

        # Trigger with new key mapping
        await self.__verify_trigger_redo(carb.input.KeyboardInput.Z, True)
        await self.__verify_trigger_undo(carb.input.KeyboardInput.Y, True)

        # Switch layout back to default
        self._hotkey_registry.switch_layout("U.S. QWERTY")
        self.assertEqual(undo_hotkey.key_combination.as_string, "CTRL + Z")
        self.assertEqual(redo_hotkey.key_combination.as_string, "CTRL + Y")

        # Trigger with default key mapping
        await self.__verify_trigger_redo(carb.input.KeyboardInput.Y, True)
        await self.__verify_trigger_undo(carb.input.KeyboardInput.Z, True)

    async def test_user_hotkey(self):
        self._hotkey_registry.switch_layout("U.S. QWERTY")

        hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, "CTRL + M", TEST_ACTION_EXT_ID, TEST_GLOBAL_PRESS_ACTION_ID_UNDO)
        self.assertIsNotNone(hotkey)

        self._hotkey_registry.edit_hotkey(hotkey, "CTRL + Z", None)
        self.assertEqual(hotkey.key_combination.as_string, "CTRL + Z")
        self._hotkey_registry.switch_layout("German QWERTZ")
        self.assertEqual(hotkey.key_combination.as_string, "CTRL + Z")

    async def __verify_trigger_undo(self, key, should_trigger):
        saved_count = _global_press_action_undo_count
        await ui_test.emulate_keyboard_press(key, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL)
        await ui_test.human_delay()
        if should_trigger:
            self.assertEqual(_global_press_action_undo_count, saved_count + 1)
        else:
            self.assertEqual(_global_press_action_undo_count, saved_count)

    async def __verify_trigger_redo(self, key, should_trigger):
        saved_count = _global_press_action_redo_count
        await ui_test.emulate_keyboard_press(key, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL)
        await ui_test.human_delay()
        if should_trigger:
            self.assertEqual(_global_press_action_redo_count, saved_count + 1)
        else:
            self.assertEqual(_global_press_action_redo_count, saved_count)
