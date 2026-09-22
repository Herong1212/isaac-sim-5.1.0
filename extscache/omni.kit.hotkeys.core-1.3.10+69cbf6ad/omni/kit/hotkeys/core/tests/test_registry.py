# pylint: disable=attribute-defined-outside-init
import omni.kit.test

from carb.eventdispatcher import get_eventdispatcher, Event
from omni.kit.hotkeys.core import get_hotkey_registry, HotkeyFilter, Hotkey, HotkeyRegistry, HOTKEY_CHANGED_GLOBAL_EVENT, HOTKEY_REGISTER_GLOBAL_EVENT, HOTKEY_DEREGISTER_GLOBAL_EVENT
from omni.kit.actions.core import get_action_registry

TEST_HOTKEY_EXT_ID = "omni.kit.hotkey.test.hotkey"
TEST_ACTION_EXT_ID = "omni.kit.hotkey.test.action"
TEST_ACTION_ID = "hotkey_test_action"
TEST_ANOTHER_ACTION_ID = "hotkey_test_action_another"
TEST_CONTEXT_NAME = "test_context@omni.kit.hotkey.test"
TEST_HOTKEY = "CTRL + T"
TEST_ANOTHER_HOTKEY = "SHIFT + T"
TEST_EDIT_HOTKEY = "T"
CHANGE_HOTKEY = "SHIFT + CTRL + T"


class TestRegistry(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._hotkey_registry = get_hotkey_registry()
        self._hotkey_registry.clear_storage()
        self._action_registry = get_action_registry()
        self._filter = HotkeyFilter(context=TEST_CONTEXT_NAME)
        self._register_payload = {}

        self._action = self._action_registry.register_action(TEST_ACTION_EXT_ID, TEST_ACTION_ID, lambda: print("this is a hotkey test"))
        self._another_action = self._action_registry.register_action(TEST_ACTION_EXT_ID, TEST_ANOTHER_ACTION_ID, lambda: print("this is another hotkey test"))

    # After running each test
    async def tearDown(self):
        self._hotkey_registry.deregister_all_hotkeys_for_extension(TEST_HOTKEY_EXT_ID)
        self._hotkey_registry.clear_storage()
        self._hotkey_registry = None
        self._action_registry.deregister_action(self._another_action)
        self._action_registry.deregister_action(self._action)
        self._action_registry = None

    async def test_register_global_hotkey(self):
        hotkey = self._hotkey_registry.get_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY)
        self.assertIsNone(hotkey)

        # Register a global hotkey
        self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ACTION_ID)

        hotkey = self._hotkey_registry.get_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY)
        self.assertEqual(hotkey.hotkey_ext_id, TEST_HOTKEY_EXT_ID)
        self.assertEqual(hotkey.action, self._action)
        self.assertEqual(hotkey.key_combination.as_string, TEST_HOTKEY)

        # Deregister the global hotkey
        self._hotkey_registry.deregister_hotkey(hotkey)
        hotkey = self._hotkey_registry.get_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY)
        self.assertIsNone(hotkey)

    async def test_register_local_hotkey(self):
        global_hotkey = self._hotkey_registry.get_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY)
        self.assertIsNone(global_hotkey)
        local_hotkey = self._hotkey_registry.get_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, filter=self._filter)
        self.assertIsNone(local_hotkey)

        # Register a local hotkey
        self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ACTION_ID, filter=self._filter)

        global_hotkey = self._hotkey_registry.get_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY)
        self.assertIsNone(global_hotkey)
        local_hotkey = self._hotkey_registry.get_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, filter=self._filter)
        self.assertEqual(local_hotkey.hotkey_ext_id, TEST_HOTKEY_EXT_ID)
        self.assertEqual(local_hotkey.action, self._action)
        self.assertEqual(local_hotkey.key_combination.as_string, TEST_HOTKEY)

        # Deregister the local hotkey
        self._hotkey_registry.deregister_hotkey(local_hotkey)
        hotkey = self._hotkey_registry.get_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, filter=self._filter)
        self.assertIsNone(hotkey)

    async def test_mixed_hotkey(self):
        # Register a global hotkey
        global_hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ACTION_ID)

        # Register a local hotkey
        local_hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ACTION_ID, filter=self._filter)

        self.assertNotEqual(global_hotkey, local_hotkey)

        discovered_global_hotkey = self._hotkey_registry.get_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY)
        self.assertEqual(global_hotkey, discovered_global_hotkey)

        discovered_local_hotkey = self._hotkey_registry.get_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, filter=self._filter)
        self.assertEqual(local_hotkey, discovered_local_hotkey)

        # Deregister the hotkeys
        self._hotkey_registry.deregister_hotkey(global_hotkey)
        self._hotkey_registry.deregister_hotkey(local_hotkey)

    async def test_deregister(self):
        # Register a global hotkey
        hotkey_1 = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ACTION_ID)
        self.assertIsNotNone(hotkey_1)
        # Register a local hotkey
        hotkey_2 = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ACTION_ID, filter=self._filter)
        self.assertIsNotNone(hotkey_2)
        # Register with another key, should since already action already defined
        hotkey_3 = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, "SHIFT+D", TEST_ACTION_EXT_ID, TEST_ACTION_ID)
        self.assertIsNone(hotkey_3)
        # Register with another extension id
        hotkey_4 = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID + "_another", TEST_ANOTHER_HOTKEY, TEST_ACTION_EXT_ID, TEST_ANOTHER_ACTION_ID, filter=self._filter)
        self.assertIsNotNone(hotkey_4)

        hotkeys = self._hotkey_registry.get_all_hotkeys_for_extension(TEST_HOTKEY_EXT_ID + "_another")
        self.assertEqual(len(hotkeys), 1)
        # Deregister hotkey_4
        self._hotkey_registry.deregister_all_hotkeys_for_extension(TEST_HOTKEY_EXT_ID + "_another")
        hotkeys = self._hotkey_registry.get_all_hotkeys_for_extension(TEST_HOTKEY_EXT_ID + "_another")
        self.assertEqual(len(hotkeys), 0)

        # Deregister hotkey_1
        hotkeys = self._hotkey_registry.get_all_hotkeys_for_extension(None)
        self.assertEqual(len(hotkeys), 1)
        self._hotkey_registry.deregister_all_hotkeys_for_extension(None)
        hotkeys = self._hotkey_registry.get_all_hotkeys_for_extension(None)
        self.assertEqual(len(hotkeys), 0)

        # Deregister hotkey_2
        hotkeys = self._hotkey_registry.get_all_hotkeys_for_filter(self._filter)
        self.assertEqual(len(hotkeys), 1)
        self._hotkey_registry.deregister_all_hotkeys_for_filter(self._filter)
        hotkeys = self._hotkey_registry.get_all_hotkeys_for_filter(self._filter)
        self.assertEqual(len(hotkeys), 0)

    async def test_discover_hotkeys(self):
        hotkeys = self._hotkey_registry.get_all_hotkeys_for_extension(TEST_HOTKEY_EXT_ID)
        self.assertEqual(len(hotkeys), 0)
        hotkeys = self._hotkey_registry.get_all_hotkeys_for_key(TEST_HOTKEY)
        self.assertEqual(len(hotkeys), 0)
        hotkeys = self._hotkey_registry.get_hotkeys(TEST_ACTION_EXT_ID, TEST_HOTKEY)
        self.assertEqual(len(hotkeys), 0)

        # Register a global hotkey
        global_hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ACTION_ID)
        self.assertIsNotNone(global_hotkey)

        # Register a local hotkey
        local_hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ACTION_ID, filter=self._filter)
        self.assertIsNotNone(local_hotkey)

        # Register with another key
        hotkey_1 = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, "SHIFT+D", TEST_ACTION_EXT_ID, TEST_ANOTHER_ACTION_ID)
        self.assertIsNotNone(hotkey_1)
        # Register with another extension id (should be failed since key + filter is same)
        hotkey_2 = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID + "_another", TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ANOTHER_ACTION_ID, filter=self._filter)
        self.assertIsNone(hotkey_2)

        hotkeys = self._hotkey_registry.get_all_hotkeys_for_extension(TEST_HOTKEY_EXT_ID)
        self.assertEqual(len(hotkeys), 3)

        hotkeys = self._hotkey_registry.get_all_hotkeys_for_extension(None)
        self.assertEqual(len(hotkeys), 2)

        hotkeys = self._hotkey_registry.get_all_hotkeys_for_key(TEST_HOTKEY)
        self.assertEqual(len(hotkeys), 2)

        hotkeys = self._hotkey_registry.get_hotkeys(TEST_HOTKEY_EXT_ID, TEST_HOTKEY)
        self.assertEqual(len(hotkeys), 2)

        self._hotkey_registry.deregister_hotkey(global_hotkey)
        self._hotkey_registry.deregister_hotkey(local_hotkey)
        self._hotkey_registry.deregister_hotkey(hotkey_1)
        self._hotkey_registry.deregister_hotkey(hotkey_2)

    async def test_event(self):
        self._register_event_sub = get_eventdispatcher().observe_event(
            event_name=HOTKEY_REGISTER_GLOBAL_EVENT, on_event=self._on_hotkey_register)
        self._deregister_event_sub = get_eventdispatcher().observe_event(
            event_name=HOTKEY_DEREGISTER_GLOBAL_EVENT, on_event=self._on_hotkey_deregister)
        self._change_event_sub = get_eventdispatcher().observe_event(
            event_name=HOTKEY_CHANGED_GLOBAL_EVENT, on_event=self._on_hotkey_changed)

        # Register hotkey event
        test_hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ACTION_ID)

        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()

        self.assertEqual(self._register_payload["hotkey_ext_id"], TEST_HOTKEY_EXT_ID)
        self.assertEqual(self._register_payload["key"], TEST_HOTKEY)
        self.assertEqual(self._register_payload["action_ext_id"], TEST_ACTION_EXT_ID)
        self.assertEqual(self._register_payload["action_id"], TEST_ACTION_ID)

        # Change hotkey
        error_code = self._hotkey_registry.edit_hotkey(test_hotkey, CHANGE_HOTKEY, None)
        self.assertEqual(error_code, HotkeyRegistry.Result.OK)
        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()

        self.assertEqual(self._changed_payload["hotkey_ext_id"], TEST_HOTKEY_EXT_ID)
        self.assertEqual(self._changed_payload["key"], CHANGE_HOTKEY)
        self.assertEqual(self._changed_payload["action_ext_id"], TEST_ACTION_EXT_ID)
        self.assertEqual(self._changed_payload["action_id"], TEST_ACTION_ID)

        # Change hotkey back
        self._hotkey_registry.edit_hotkey(test_hotkey, TEST_HOTKEY, None)
        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._changed_payload["key"], TEST_HOTKEY)

        # Deregister hotkey event
        self._hotkey_registry.deregister_hotkey(test_hotkey)

        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()

        self.assertEqual(self._deregister_payload["hotkey_ext_id"], TEST_HOTKEY_EXT_ID)
        self.assertEqual(self._deregister_payload["key"], TEST_HOTKEY)
        self.assertEqual(self._deregister_payload["action_ext_id"], TEST_ACTION_EXT_ID)
        self.assertEqual(self._deregister_payload["action_id"], TEST_ACTION_ID)

        self._register_event_sub = None
        self._deregister_event_sub = None
        self._change_event_sub = None

    async def test_error_code_global(self):
        hotkey = Hotkey(TEST_HOTKEY_EXT_ID, "CBL", TEST_ACTION_EXT_ID, TEST_ACTION_ID)
        registered_hotkey = self._hotkey_registry.register_hotkey(hotkey)
        self.assertIsNone(registered_hotkey)
        self.assertEqual(self._hotkey_registry.last_error, HotkeyRegistry.Result.ERROR_KEY_INVALID)

        registered_hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, "T", "", "")
        self.assertIsNone(registered_hotkey)
        self.assertEqual(self._hotkey_registry.last_error, HotkeyRegistry.Result.ERROR_NO_ACTION)

        registered_hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ACTION_ID)
        self.assertIsNotNone(registered_hotkey)
        self.assertEqual(self._hotkey_registry.last_error, HotkeyRegistry.Result.OK)
        registered_another = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ANOTHER_ACTION_ID)
        self.assertIsNone(registered_another)
        self.assertEqual(self._hotkey_registry.last_error, HotkeyRegistry.Result.ERROR_KEY_DUPLICATED)

        # Edit global hotkey
        registered_another = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_ANOTHER_HOTKEY, TEST_ACTION_EXT_ID, TEST_ANOTHER_ACTION_ID)
        self.assertIsNotNone(registered_another)
        error_code = self._hotkey_registry.edit_hotkey(registered_another, "ALT", None)
        self.assertEqual(error_code, HotkeyRegistry.Result.ERROR_KEY_INVALID)
        error_code = self._hotkey_registry.edit_hotkey(registered_another, TEST_HOTKEY, None)
        self.assertEqual(error_code, HotkeyRegistry.Result.ERROR_KEY_DUPLICATED)
        duplicated = self._hotkey_registry.get_hotkey_for_filter(TEST_HOTKEY, None)
        self.assertEqual(duplicated.action_ext_id, TEST_ACTION_EXT_ID)
        self.assertEqual(duplicated.action_id, TEST_ACTION_ID)
        error_code = self._hotkey_registry.edit_hotkey(registered_another, TEST_EDIT_HOTKEY, None)
        self.assertEqual(error_code, HotkeyRegistry.Result.OK)
        error_code = self._hotkey_registry.edit_hotkey(registered_another, "T", None)
        self.assertEqual(error_code, HotkeyRegistry.Result.OK)

    async def test_error_code_window(self):
        # Edit hotkey in window
        hotkey_filter = HotkeyFilter(windows=["Test Window"])

        registered_hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ACTION_ID, filter=hotkey_filter)
        self.assertIsNotNone(registered_hotkey)
        self.assertEqual(self._hotkey_registry.last_error, HotkeyRegistry.Result.OK)
        registered_another = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ANOTHER_ACTION_ID, filter=hotkey_filter)
        self.assertIsNone(registered_another)
        self.assertEqual(self._hotkey_registry.last_error, HotkeyRegistry.Result.ERROR_KEY_DUPLICATED)

        registered_another = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_ANOTHER_HOTKEY, TEST_ACTION_EXT_ID, TEST_ANOTHER_ACTION_ID, filter=hotkey_filter)
        self.assertEqual(self._hotkey_registry.last_error, HotkeyRegistry.Result.OK)
        self.assertIsNotNone(registered_another)
        error_code = self._hotkey_registry.edit_hotkey(registered_another, "ALT", hotkey_filter)
        self.assertEqual(error_code, HotkeyRegistry.Result.ERROR_KEY_INVALID)
        error_code = self._hotkey_registry.edit_hotkey(registered_another, TEST_HOTKEY, hotkey_filter)
        self.assertEqual(error_code, HotkeyRegistry.Result.ERROR_KEY_DUPLICATED)
        duplicated = self._hotkey_registry.get_hotkey_for_filter(TEST_HOTKEY, hotkey_filter)
        self.assertEqual(duplicated.action_ext_id, TEST_ACTION_EXT_ID)
        self.assertEqual(duplicated.action_id, TEST_ACTION_ID)
        error_code = self._hotkey_registry.edit_hotkey(registered_another, TEST_EDIT_HOTKEY, hotkey_filter)
        self.assertEqual(error_code, HotkeyRegistry.Result.OK)
        error_code = self._hotkey_registry.edit_hotkey(registered_another, "T", hotkey_filter)
        self.assertEqual(error_code, HotkeyRegistry.Result.OK)

    async def test_disable_hotkey(self):
        # Register a global hotkey
        self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ACTION_ID)

        hotkey = self._hotkey_registry.get_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY)
        self.assertIsNotNone(hotkey)

        # Disable
        self._hotkey_registry.disable_hotkey(hotkey)
        hotkey = self._hotkey_registry.get_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY)
        self.assertIsNone(hotkey)

        # Register again - since disabled, no hotkey registered
        hotkey = self._hotkey_registry.register_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY, TEST_ACTION_EXT_ID, TEST_ACTION_ID)
        self.assertIsNone(hotkey)

        # Restore - disabled hotkey will be available again
        self._hotkey_registry.restore_defaults()
        hotkey = self._hotkey_registry.get_hotkey(TEST_HOTKEY_EXT_ID, TEST_HOTKEY)
        self.assertIsNotNone(hotkey)

    def _on_hotkey_register(self, event: Event):
        self._register_payload = event

    def _on_hotkey_deregister(self, event: Event):
        self._deregister_payload = event

    def _on_hotkey_changed(self, event: Event):
        self._changed_payload = event
