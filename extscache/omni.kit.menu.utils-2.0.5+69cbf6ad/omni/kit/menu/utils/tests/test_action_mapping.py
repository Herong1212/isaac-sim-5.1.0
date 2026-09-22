import carb
import omni.kit.test
from omni.kit import ui_test
from omni.kit.menu.utils import MenuItemDescription
from omni.kit.test_suite.helpers import wait_stage_loading


class TestActionMappingMenuUtils(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._menus = [
            MenuItemDescription(
                name="Test Hotkey Mapping",
                glyph="none.svg",
                hotkey=(
                    carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL | carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT,
                    carb.input.KeyboardInput.EQUAL,
                ),
            )
        ]
        omni.kit.menu.utils.add_menu_items(self._menus, "Test", 99)

    async def tearDown(self):
        omni.kit.menu.utils.remove_menu_items(self._menus, "Test")

    async def test_action_mapping(self):
        import re

        mapping_path = "/app/inputBindings/global/Test_Test_Hotkey_Mapping"
        menu_widget = ui_test.get_menubar()
        widget = menu_widget.find_menu("Test Hotkey Mapping")

        settings = carb.settings.get_settings()

        await wait_stage_loading(wait_frames=10)

        # verify initial value
        menu_text = re.sub(r"[^\x00-\x7F]+", "", widget.widget.text).replace(" ", "")
        self.assertTrue(menu_text == "TestHotkeyMapping")
        key_mapping = settings.get(mapping_path)
        self.assertTrue(key_mapping == ["Shift + Ctrl + Keyboard::="])
        hotkey_text = widget.widget.hotkey_text.replace(" ", "")
        self.assertTrue(hotkey_text == "Shift+Ctrl+=")

        # set to bad value..
        settings.set(mapping_path, "Nothingness")
        await wait_stage_loading(wait_frames=10)
        hotkey_text = widget.widget.hotkey_text.replace(" ", "")
        self.assertTrue(hotkey_text == "")

        # set to bad value.. (this crashes kit)
        # settings.set(mapping_path, ["Nothingness"])
        # await wait_stage_loading(wait_frames=10)
        # hotkey_text = widget.widget.hotkey_text.replace(" ", "")
        # self.assertTrue(hotkey_text == "")

        # set to good value..
        settings.set(mapping_path, ["Shift + Ctrl + Keyboard::O"])
        await wait_stage_loading(wait_frames=10)
        hotkey_text = widget.widget.hotkey_text.replace(" ", "")
        self.assertTrue(hotkey_text == "Shift+Ctrl+O")

        # set to good value..
        settings.set(mapping_path, ["Shift + Ctrl + Keyboard::="])
        await wait_stage_loading(wait_frames=10)
        hotkey_text = widget.widget.hotkey_text.replace(" ", "")
        self.assertTrue(hotkey_text == "Shift+Ctrl+=")
