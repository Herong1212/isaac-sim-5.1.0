from unittest.mock import patch

import omni.kit.app
import omni.ui as ui
from omni.kit.ui_test.query import MenuRef, WindowRef
import omni.kit.ui_test as ui_test
from omni.ui.tests.test_base import OmniUiTest


class TestOptionsMenu(OmniUiTest):
    async def setUp(self):
        await super().setUp()

        window = ui.Workspace.get_window("Hotkeys")
        window.visible = True  # just in case another test has turned it off
        await self.docked_test_window(window=window, width=1280, height=800, block_devices=False)

        window._search_bar._SearchBar__show_options()    # noqa: PLW0212
        self._menu = window._search_bar._SearchBar__options_menu    # noqa: PLW0212

        await omni.kit.app.get_app().next_update_async()

        menu_ref = MenuRef(self._menu._OptionsMenu__context_menu, "")    # noqa: PLW0212
        self._menu_items = menu_ref.find_all("**/")

    async def test_import(self):
        """Test import hotkey preset"""
        self.assertEqual(self._menu_items[0].widget.text, "Import Preset")
        await self._menu_items[0].click()

        for _ in range(4):
            await omni.kit.app.get_app().next_update_async()

        dialog = self._menu._OptionsMenu__import_dialog    # noqa: PLW0212
        self.assertIsNotNone(dialog)

        dialog.set_current_directory("test")
        dialog.set_filename("test_import.json")

        import_window = ui.Workspace.get_window("Import")
        window_ref = WindowRef(import_window, "")

        import_btn_ref = window_ref.find_all("**/Button[*].text=='import'")[0]

        with (
            patch("omni.client.stat", side_effect=self._mock_stat_file_impl),
            patch("omni.kit.hotkeys.core.HotkeyRegistry.import_storage") as mock_import
        ):
            await import_btn_ref.click()
            mock_import.assert_called_once()

    async def test_export(self):
        """Test export hotkey presets"""
        self.assertEqual(self._menu_items[1].widget.text, "Export Preset")
        await self._menu_items[1].click()

        for _ in range(4):
            await omni.kit.app.get_app().next_update_async()

        dialog = self._menu._OptionsMenu__export_dialog    # noqa: PLW0212
        self.assertIsNotNone(dialog)

        dialog.set_current_directory("test")
        dialog.set_filename("test_import.json")

        export_window = ui.Workspace.get_window("Export As")
        window_ref = WindowRef(export_window, "")

        export_btn_ref = window_ref.find_all("**/Button[*].text=='Export'")[0]

        with (
            patch("omni.client.stat", side_effect=self._mock_stat_file_not_found_impl),
            patch("omni.kit.hotkeys.core.HotkeyRegistry.export_storage") as mock_export
        ):
            await export_btn_ref.click()
            mock_export.assert_called_once()

    async def test_restore(self):
        """Test restore hotkeys defaults"""
        self.assertEqual(self._menu_items[2].widget.text, "Restore Defaults")
        await self._menu_items[2].click()

        for _ in range(4):
            await omni.kit.app.get_app().next_update_async()

        warning_window = ui.Workspace.get_window("###Hotkey_WARNING_Restore Defaults")
        window_ref = WindowRef(warning_window, "")

        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        btn_ref = window_ref.find_all("**/Button[*].text=='Yes'")[0]

        with patch("omni.kit.hotkeys.core.HotkeyRegistry.restore_defaults") as mock_restore:
            await btn_ref.click()
            mock_restore.assert_called_once()

    async def test_layout(self):
        """Test switching keyboard layout"""
        self.assertEqual(self._menu_items[3].widget.text, "Keyboard Layouts")
        await ui_test.emulate_mouse_move(self._menu_items[3].center)

        layout_menu_items = self._menu_items[3].find_all("**/")
        with patch("omni.kit.hotkeys.core.HotkeyRegistry.switch_layout") as mock_switch_layout:
            await layout_menu_items[0].click()
            mock_switch_layout.assert_called_once()

    def _mock_stat_file_impl(self, url: str):
        return (omni.client.Result.OK, None)

    def _mock_stat_file_not_found_impl(self, url: str):
        return (omni.client.Result.ERROR_NOT_FOUND, None)
