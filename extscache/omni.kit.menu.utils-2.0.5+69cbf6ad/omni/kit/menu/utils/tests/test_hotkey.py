import carb
import omni.kit.app
import omni.kit.test
from omni.kit.actions.core import get_action_registry
from omni.kit.hotkeys.core import get_hotkey_registry
from omni.kit.menu.utils import MenuItemDescription


def test_hotkey():
    print("test hotkey triggered!")


class TestActionMappingMenuUtils(omni.kit.test.AsyncTestCase):
    async def test_hotkey(self):
        action_registry = get_action_registry()
        actions_tag = "Test hotkey Actions"
        extension_id = "menu.test"
        action_registry.register_action(
            extension_id,
            "Test Hotkey",
            test_hotkey,
            display_name="Test hotkey",
            description="Test hotkey",
            tag=actions_tag,
        )
        try:
            hotkey_registry = get_hotkey_registry()
            hotkey_text = "ALT + M"

            # No this hotkey first
            hotkeys = hotkey_registry.get_all_hotkeys_for_key(hotkey_text)
            self.assertEqual(len(hotkeys), 0)

            menus = [
                MenuItemDescription(
                    name="Test Hotkey",
                    onclick_action=(extension_id, "Test Hotkey"),
                    hotkey=(carb.input.KEYBOARD_MODIFIER_FLAG_ALT, carb.input.KeyboardInput.M),
                )
            ]
            omni.kit.menu.utils.add_menu_items(menus, "Test", 99, True)

            # Hotkey defined with menu item
            await omni.kit.app.get_app().next_update_async()
            hotkeys = hotkey_registry.get_all_hotkeys_for_key(hotkey_text)
            self.assertEqual(len(hotkeys), 1)

            omni.kit.menu.utils.remove_menu_items(menus, "Test")
            for desc in menus:
                desc.destroy()

            # Hotkey removed
            await omni.kit.app.get_app().next_update_async()
            hotkeys = hotkey_registry.get_all_hotkeys_for_key(hotkey_text)
            self.assertEqual(len(hotkeys), 0)
        finally:
            action_registry.deregister_all_actions_for_extension(extension_id)
