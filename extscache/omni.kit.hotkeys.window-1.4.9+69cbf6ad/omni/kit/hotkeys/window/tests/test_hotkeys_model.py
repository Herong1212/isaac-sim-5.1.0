# pylint: disable=protected-access
from pathlib import Path
from typing import Tuple
from omni.ui.tests.test_base import OmniUiTest
import omni.kit.app
import omni.kit.test
import omni.ui as ui

from omni.kit.actions.core import get_action_registry
from omni.kit.hotkeys.core import get_hotkey_registry, KeyCombination, HotkeyRegistry

from ..window.hotkeys_window import HotkeysWindow
from ..model.hotkey_item import USER_HOTKEY_EXT_ID, HotkeyDetailItem

TEST_ACTION_EXT_ID = "test.hotkey.model"
TEST_ACTION_ID = "new"
TEST_ANOTHER_ACTION_ID = "another"
CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")


class TestHotkeysModel(OmniUiTest):
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

        # Hide original hotkeys window
        self.__origin_hotkeys_window = ui.Workspace.get_window("Hotkeys")
        self.__origin_hotkeys_window.visible = False
        await omni.kit.app.get_app().next_update_async()

        # Create new hotkeys window
        self.__window = HotkeysWindow("Model")
        await self.docked_test_window(window=self.__window, width=1280, height=400, block_devices=False)

        self.__window._search_bar.visible = False
        self._model = self.__window._hotkeys_model

        self.__register_actions()
        self.__action_executed = 0
        self.__model_changed = 0

    async def tearDown(self):
        self._action_registry.deregister_all_actions_for_extension(TEST_ACTION_EXT_ID)
        self._hotkey_registry.deregister_all_hotkeys_for_extension(USER_HOTKEY_EXT_ID)
        self._hotkey_registry.clear_storage()
        self.__window.visible = False
        self.__window.destroy()
        self.__window = None

        self.__origin_hotkeys_window.visible = True

        await super().tearDown()

    async def test_1_add_global_empty_hotkey(self):
        await self.__add_empty_global_hotkey()

        # Wait for icons loaded
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="hotkeys_model_add_global_empty.png", threshold=.03)

    async def test_2_save_global_empty_hotkey(self):
        (item, _) = await self.__add_save_empty_global_hotkey(KeyCombination("N"))
        await self.__wait_for_icons()
        self._model.execute(item)
        self.assertEqual(self.__action_executed, 1)
        self.assertEqual(self._model.get_item_by_key(KeyCombination("N"), None).hotkey, item.hotkey)
        self.assertIsNone(self._model.get_item_by_key(KeyCombination("A"), None))

        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="hotkeys_model_save_global_empty.png", threshold=.03)

    async def test_3_delete_global_hotkey(self):
        await self.__add_save_empty_global_hotkey(KeyCombination("N"))
        filter_items = self._model.get_item_children(None)
        global_filter_item = filter_items[0]
        hotkey_items = self._model.get_item_children(global_filter_item)
        hotkey_counts = len(hotkey_items)
        # Delete the new global hotkey
        hotkey_to_delete = self._model.get_item_by_key(KeyCombination("N"), None)
        self._model.delete_hotkey_item(hotkey_to_delete)

        await omni.kit.app.get_app().next_update_async()

        filter_items = self._model.get_item_children(None)
        global_filter_item = filter_items[0]
        hotkey_items = self._model.get_item_children(global_filter_item)
        self.assertEqual(len(hotkey_items), hotkey_counts - 1)
        self.assertIsNone(self._model.get_item_by_key(KeyCombination("N"), None))

    async def test_4_edit_global_hotkey(self):
        await self.__add_save_edit_empty_global_hotkey(KeyCombination("N"))
        # Wait for icons loaded
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="hotkeys_model_edit_global_empty.png", threshold=.03)

    async def test_5_retore_global_hotkey(self):
        await self.__add_save_edit_empty_global_hotkey(KeyCombination("N"))
        model = self.__window._hotkeys_model
        filter_items = model.get_item_children(None)
        global_filter_item = filter_items[0]
        hotkey_items = model.get_item_children(global_filter_item)
        model.restore_item_key(hotkey_items[0])
        await self.__wait_for_icons()
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="hotkeys_model_restore_global_hotkey.png", threshold=.03)

    async def test_6_add_window_filter(self):
        await self.__add_window_filter()
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="hotkeys_model_add_window_filter.png", threshold=.03)

    async def test_7_edit_window_filter(self):
        result = await self.__add_save_window_filter(KeyCombination("T"))
        self.assertEqual(result, HotkeyRegistry.Result.OK)
        await self.__wait_for_icons()
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="hotkeys_model_edit_window_filter.png", threshold=.03)

    async def test_8_save_global_duplicated(self):
        key_combination = KeyCombination("T")
        (_, result) = await self.__add_save_empty_global_hotkey(key_combination)
        self.assertEqual(result, HotkeyRegistry.Result.OK)
        (item, result) = await self.__add_save_empty_global_hotkey(key_combination, action=self._another_action)
        self.assertEqual(result, HotkeyRegistry.Result.ERROR_KEY_DUPLICATED)
        model = self.__window._hotkeys_model
        duplicated_key = self._hotkey_registry.get_hotkey_for_filter(key_combination, item.hotkey.filter)
        model.replace_item_key(key_combination, item, duplicated_key)

        await self.__wait_for_icons()

        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="hotkeys_model_save_global_duplicated.png", threshold=.03)

    async def test_clear_empty_hotkey(self):

        def __on_model_changed(m, i):
            self.__model_changed += 1

        sub = self._model.subscribe_item_changed_fn(__on_model_changed)  # noqa: PLW0612

        # No empty hotkey, nothing happens
        self._model.clear_empty_hotkey()
        self.assertEqual(self.__model_changed, 0)

        # Add a empty hotkey then clear
        filter_items = self._model.get_item_children(None)
        window_filter_item = filter_items[1]

        added_item = self._model.add_empty_hotkey(window_filter_item)
        self.assertIsNotNone(added_item)
        self.assertEqual(self.__model_changed, 1)
        await omni.kit.app.get_app().next_update_async()
        self._model.clear_empty_hotkey()
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self.__model_changed, 2)

        sub = None  # noqa: F841

    async def __add_window_filter(self):
        model = self.__window._hotkeys_model
        model.add_window_filter()
        await omni.kit.app.get_app().next_update_async()

    async def __add_save_window_filter(self, key_combination) -> HotkeyRegistry.Result:
        await self.__add_window_filter()
        model = self.__window._hotkeys_model
        filter_items = model.get_item_children(None)
        window_filter_item = filter_items[1]
        model.edit_hotkey_filter_item(window_filter_item, window_title="Hotkeys")
        model.add_empty_hotkey(window_filter_item)
        model.save_empty_action(self._new_action)
        result = model.save_empty_hotkey(key_combination)
        await omni.kit.app.get_app().next_update_async()

        return result

    async def __add_empty_global_hotkey(self) -> HotkeyDetailItem:
        model = self.__window._hotkeys_model
        filter_items = model.get_item_children(None)
        global_filter_item = filter_items[0]
        item = model.add_empty_hotkey(global_filter_item)

        await omni.kit.app.get_app().next_update_async()
        return item

    async def __add_save_empty_global_hotkey(self, key_combination, action=None) -> Tuple[HotkeyDetailItem, HotkeyRegistry.Result]:
        item = await self.__add_empty_global_hotkey()
        model = self.__window._hotkeys_model
        if action is None:
            action = self._new_action
        model.save_empty_action(action)
        result = model.save_empty_hotkey(key_combination)
        await omni.kit.app.get_app().next_update_async()
        return (item, result)

    async def __add_save_edit_empty_global_hotkey(self, key_combination) -> Tuple[HotkeyDetailItem, HotkeyRegistry.Result]:
        (item, result) = await self.__add_save_empty_global_hotkey(key_combination)
        model = self.__window._hotkeys_model
        filter_items = model.get_item_children(None)
        global_filter_item = filter_items[0]
        hotkey_items = model.get_item_children(global_filter_item)
        result = model.edit_hotkey_item(hotkey_items[0], key_text="P")
        await omni.kit.app.get_app().next_update_async()

        return (item, result)

    def __register_actions(self):
        self._action_registry = get_action_registry()

        self._new_action = self._action_registry.register_action(
            TEST_ACTION_EXT_ID,
            TEST_ACTION_ID,
            self._test_action,
            display_name="Model test",
            description="MODEL TEST",
            tag="Actions",
        )

        self._another_action = self._action_registry.register_action(
            TEST_ACTION_EXT_ID,
            TEST_ANOTHER_ACTION_ID,
            lambda: None,
            display_name="Another model test",
            description="ANOTHER MODEL TEST",
            tag="Actions",
        )

        self._hotkey_registry = get_hotkey_registry()

    async def __wait_for_icons(self):
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

    def _test_action(self):
        self.__action_executed += 1
