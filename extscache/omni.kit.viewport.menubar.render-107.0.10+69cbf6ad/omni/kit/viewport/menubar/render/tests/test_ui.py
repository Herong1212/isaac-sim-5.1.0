import functools
from pathlib import Path
import tempfile
from unittest.mock import patch

import carb.input
import omni.kit.app
import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest
import omni.kit.ui_test as ui_test
from omni.kit.ui_test import Vec2
from omni.kit.viewport.window import ViewportWindow
import omni.ui as ui
import omni.usd
from omni.kit.viewport.menubar.render import get_instance as _get_menubar_extension
from omni.kit.viewport.menubar.render import SingleRenderMenuItemBase as _SingleRenderMenuItemBase

CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data")
TEST_DATA_PATH = DATA_PATH.joinpath("tests")
TEST_WIDTH, TEST_HEIGHT = 600, 500


class TestSettingMenuWindow(OmniUiTest):
    async def setUp(self):
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        self._vw = ViewportWindow('TestWindow', width=TEST_WIDTH, height=TEST_HEIGHT)
        self._viewport_api = self._vw.viewport_api

        await omni.kit.app.get_app().next_update_async()

    # After running each test
    async def tearDown(self):
        self._vw.destroy()
        del self._vw
        await super().tearDown()

    async def __show_render_menu(self, mouse_pos: Vec2 = None):
        await ui_test.emulate_mouse_move(mouse_pos if mouse_pos else Vec2(40, 40))
        await ui_test.emulate_mouse_click()
        await omni.kit.app.get_app().next_update_async()

    async def __close_render_menu(self):
        await ui_test.emulate_mouse_move(Vec2(TEST_WIDTH, TEST_HEIGHT))
        await ui_test.emulate_mouse_click()
        await self.wait_n_updates()

    async def test_render_menu_with_custom_type(self):
        """Test custom options area item. (This likely breaks order independent testing)"""
        menu_option_clicked = 0

        def _single_render_menu_item(*args, **kwargs):
            class SingleRenderMenuItem(_SingleRenderMenuItemBase):
                def _option_clicked(self):
                    nonlocal menu_option_clicked
                    menu_option_clicked += 1

            return SingleRenderMenuItem(*args, **kwargs)

        extension = _get_menubar_extension()
        self.assertIsNotNone(extension)
        try:
            await self.__show_render_menu()

            self.assertEqual(0, menu_option_clicked)

            # Simluate a click in options-area, but do it on Storm; not RTX
            await self.__show_render_menu(Vec2(218, 135))

            self.assertEqual(0, menu_option_clicked)

            extension.register_menu_item_type(
                functools.partial(_single_render_menu_item)
            )

            await self.wait_n_updates()
            await ui_test.emulate_mouse_click()
            await self.wait_n_updates()

            self.assertEqual(1, menu_option_clicked)
        finally:
            extension.register_menu_item_type(None)
            await self.__close_render_menu()
            await self.finalize_test_no_image()

    async def test_auto_manage_renderer_list(self):
        """Test auto management of the renderer menu based on extension load. (This likely breaks order independent testing)"""

        settings = carb.settings.get_settings()
        restore_value = settings.get("/renderer/enabled")
        try:
            async def change_available_renderers(golden_img_name: str, renderers: str = None):
                # Close the menu to avoid issues with golden images as menu shrink is animated over time
                if renderers:
                    settings.set("/renderer/enabled", renderers)
                await self.__show_render_menu()
                await self.capture_and_compare(
                    golden_img_dir=self._golden_img_dir, golden_img_name=golden_img_name
                )
                await self.__close_render_menu()

            await change_available_renderers("menubar_default_list_0.png")

            # Disable everything but RTX
            await change_available_renderers("menubar_rtx_only.png", "rtx")

            # Disable everything but Iray and Storm
            await change_available_renderers("menubar_pxr_iray_only.png", "pxr,iray")

            # Enable omni.hydra.index extension (Note it will enable RTX as well due to dependencies)
            omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate("omni.hydra.index", True)
            await change_available_renderers("menubar_all_shipping.png")

            # Disbale omni.hydra.index extension, and list should be back to menubar_default_list
            omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate("omni.hydra.index", False)
            await change_available_renderers("menubar_default_list_1.png")

        finally:
            settings.set("/renderer/enabled", restore_value if restore_value else "")
            await self.__close_render_menu()
            await self.finalize_test_no_image()

    async def test_auto_manage_renderer_list_startup(self):
        """Test auto management of the renderer menu based on startup."""

        await self.__show_render_menu()
        await self.capture_and_compare(
            golden_img_dir=self._golden_img_dir, golden_img_name="test_auto_manage_renderer_list_startup.png"
        )

    async def test_load_preset(self):
        """Test load preset"""

        from omni.kit.window.file_importer.test_helper import FileImporterTestHelper

        with patch("omni.rtx.window.settings.usd_serializer.USDSettingsSerialiser.load_from_usd") as mock_load_preset:
            # First preset menu item
            await self.__show_render_menu()
            await ui_test.emulate_mouse_move(Vec2(70, 200))
            await ui_test.emulate_mouse_move_and_click(Vec2(300, 200))
            mock_load_preset.assert_called_once()

            # Load preset from file
            await self.__show_render_menu()
            await ui_test.emulate_mouse_move(Vec2(70, 200))
            await ui_test.emulate_mouse_move_and_click(Vec2(300, 265))
            async with FileImporterTestHelper() as file_import_helper:
                await file_import_helper.wait_for_popup()

                preset_path = str(DATA_PATH.joinpath("presets").absolute()).replace("\\", "/")
                file_name = "draft.settings.usda"
                url = preset_path + "/" + file_name
                await file_import_helper.click_apply_async(filename_url=url)
                mock_load_preset.assert_called_with(url)

        await self.finalize_test_no_image()

    async def test_save_preset(self):
        """Test save preset"""

        await self.__show_render_menu()
        await ui_test.emulate_mouse_move_and_click(Vec2(70, 220))

        with patch("omni.rtx.window.settings.usd_serializer.USDSettingsSerialiser.save_to_usd") as mock_save_preset:
            from omni.kit.window.file_exporter.test_helper import FileExporterTestHelper
            with tempfile.TemporaryDirectory() as tempdir:
                file_name = "my_preset.settings.usd"
                url = tempdir.replace("\\", "/") + "/" + file_name
                async with FileExporterTestHelper() as file_export_helper:
                    await file_export_helper.wait_for_popup()
                    await file_export_helper.click_apply_async(filename_url=url)
                    mock_save_preset.assert_called_once_with(url)

        await self.finalize_test_no_image()

    async def test_preference(self):
        """Test preference"""

        await self.__show_render_menu()
        await ui_test.emulate_mouse_move_and_click(Vec2(70, 405))
        await ui_test.human_delay()

        pref_window = ui.Workspace.get_window("Preferences")
        self.assertIsNotNone(pref_window)
        self.assertTrue(pref_window.visible)
        pref_window.visible = False

        await self.finalize_test_no_image()

    async def test_expand_contract(self):
        """Test expand/contract menu"""

        # Hide other windows
        for title in ["Viewport", "Render Settings"]:
            window = ui.Workspace.get_window(title)
            window.visible = False

        # Hide text, icon only
        self._vw.width = 80
        await ui_test.human_delay()
        await self.capture_and_compare(
            golden_img_dir=self._golden_img_dir, golden_img_name="contract.png"
        )

        # Show both icon and text
        self._vw.width = 150
        await ui_test.human_delay()
        await self.capture_and_compare(
            golden_img_dir=self._golden_img_dir, golden_img_name="expand.png"
        )
