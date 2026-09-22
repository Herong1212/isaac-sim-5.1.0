import os
import tempfile
from pathlib import Path

import carb
import omni.kit.app
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.kit.window.extensions
import omni.ui as ui
from omni.kit.test_suite.helpers import get_test_data_path
from omni.kit.window.file_exporter.test_helper import FileExporterTestHelper
from omni.ui.tests.test_base import OmniUiTest

from .utils import open_window_and_sync

# pylint: disable=protected-access


class TestWidgetTemplate(OmniUiTest):
    async def setUp(self):
        await open_window_and_sync(False)

    async def tearDown(self):
        omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate(
            "omni.kit.window.extensions", True
        )
        if omni.kit.app.get_app().get_extension_manager().is_extension_enabled("omni.kit.window.extensions"):
            instance = omni.kit.window.extensions.get_instance()()
            instance.show_window(False)

    async def test_uninstall(self):
        instance = omni.kit.window.extensions.get_instance()()
        ext_manager = omni.kit.app.get_app().get_extension_manager()

        instance._window._exts_list_widget._model.filter_by_text(["omni.kit.window.extensions"])
        await ui_test.human_delay(50)

        # verify extension is enabled
        self.assertTrue(ext_manager.is_extension_enabled("omni.kit.window.extensions"))

        # disable extension
        await ui_test.find("Extensions//Frame/**/.identifier=='toggle_button'").click()
        await ui_test.human_delay(50)

        # verify extension is disabled
        self.assertFalse(ext_manager.is_extension_enabled("omni.kit.window.extensions"))

    async def test_buttons(self):
        instance = omni.kit.window.extensions.get_instance()()

        # filter omni.kit.window.extensions
        instance._window._exts_list_widget._model.filter_by_text(["omni.kit.window.extensions"])
        await ui_test.human_delay(50)

        # click on omni.kit.window.extensions
        await ui_test.find("Extensions//Frame/**/Label[*].identifier=='Title'").click()
        await ui_test.human_delay(10)

        # click "open doc"
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='OpenDoc'").click()
        await ui_test.human_delay(10)

        # click "open folder"
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='OpenFolder'").click()
        await ui_test.human_delay(10)

        # click "open config"
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='OpenConfig'").click()
        await ui_test.human_delay(10)

        # click "copy_ext_id"
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='copy_ext_id'").click()
        await ui_test.human_delay(10)

        # click export
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='Export'").click()
        await ui_test.human_delay(10)

        with tempfile.TemporaryDirectory() as tmp_dir:
            export_path = f"{tmp_dir}/"
            exported_path = "xxx"
            async with FileExporterTestHelper() as file_export_helper:
                await file_export_helper.click_apply_async(filename_url=export_path)
                await ui_test.human_delay(50)

            # verify file was exported
            for dirpath, _, filenames in os.walk(tmp_dir):
                for filename in filenames:
                    if "omni.kit.window.extensions" in filename:
                        exported_path = f"{dirpath}/{filename}".replace("\\", "/")

            self.assertTrue(os.path.isfile(exported_path))

    async def test_tabs(self):
        instance = omni.kit.window.extensions.get_instance()()

        # filter omni.kit.window.extensions
        instance._window._exts_list_widget._model.filter_by_text(["omni.kit.window.extensions"])
        await ui_test.human_delay(50)

        # click on omni.kit.window.extensions
        await ui_test.find("Extensions//Frame/**/Label[*].identifier=='Title'").click()
        await ui_test.human_delay(10)

        # click on all tabs
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='tab_changelog'").click()
        await ui_test.human_delay(10)

        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='tab_dependencies'").click()
        await ui_test.human_delay(10)

        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='tab_packages'").click()
        await ui_test.human_delay(10)

        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='tab_developer'").click()
        await ui_test.human_delay(10)

    # NOTE: importing zip file doesn't work on anything anymore, both windows and linux crash
    async def __test_update(self):
        instance = omni.kit.window.extensions.get_instance()()

        # filter omni.kit.window.extensions
        ext_manager = omni.kit.app.get_app().get_extension_manager()
        ext_info_widget = instance._window._ext_info_widget
        instance._window._exts_list_widget._model.filter_by_text(["omni.kit.test_suite.helpers"])
        await ui_test.human_delay(50)

        # verify single versions
        version_count = 0
        for ext in ext_manager.get_extensions():
            if ext["name"] == "omni.kit.test_suite.helpers":
                version_count += 1
        self.assertGreaterEqual(version_count, 1)

        # cannot get ui.Menu position, so use button instead
        import_ext = f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/tests/omni.kit.test_suite.helpers-1.0.0.zip"
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='options'").click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Import Extension")
        await ui_test.human_delay(10)

        # import 1.0.0
        async with FileExporterTestHelper() as file_export_helper:
            await file_export_helper.click_apply_async(filename_url=import_ext)
            await ui_test.human_delay(50)

        # verify multiple versions
        version_count = 0
        for ext in ext_manager.get_extensions():
            if ext["name"] == "omni.kit.test_suite.helpers":
                version_count += 1
        self.assertEqual(version_count, 2)

        # click on omni.kit.test_suite.helpers
        await ui_test.find("Extensions//Frame/**/Label[*].identifier=='Title'").click()
        await ui_test.human_delay(10)

        # check version selected
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='version_selector'").click()
        await ui_test.human_delay(10)

        # select 1.0.0
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='version_selector'").click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("1.0.0", offset=ui_test.Vec2(10, 10))
        await ui_test.human_delay(10)

        # verify its correct version...
        self.assertEqual(ext_info_widget._selected_version, (1, 0, 0, "", ""))

        # click update
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='update_button'").click()
        await ui_test.human_delay(50)

        # verify its correct version...
        latest_version = (1, 0, 0, "", "")
        for ext in ext_manager.get_extensions():
            if ext["name"] == "omni.kit.test_suite.helpers" and ext["version"] > latest_version:
                latest_version = ext["version"]
        self.assertEqual(ext_info_widget._selected_version, latest_version)

        # select 1.0.0
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='version_selector'").click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("1.0.0", offset=ui_test.Vec2(10, 10))
        await ui_test.human_delay(10)
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='version_selector'").click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("UNINSTALL", offset=ui_test.Vec2(10, 10))
        await ui_test.human_delay(10)

    async def test_miscellaneous(self):
        instance = omni.kit.window.extensions.get_instance()()
        instance._window._show_properties()
        await ui_test.human_delay(10)

        prop_frame = ui_test.find("Extensions//Frame/**/ScrollingFrame[*].identifier=='exts_properties_widget'")
        misc_frame = prop_frame.find("/**/CollapsableFrame[*].title=='Miscellaneous'")
        misc_frame.widget.collapsed = False
        misc_frame.widget.scroll_here_y(0.5)

        # don't know what these are supposed todo, so no asserts
        for w in misc_frame.find_all("/**/Button[*]"):
            if w.widget.text in [
                "Copy all exts as CSV",
                "Copy enabled exts as .kit file (top level)",
                "Copy enabled exts as .kit file (all)",
            ]:
                await w.click()
                await ui_test.human_delay(50)
            else:  # pragma: no cover
                carb.log_error(f"button {w.widget.text} not tested")

    async def test_datafetcher(self):
        # need to select extension that is not local
        instance = omni.kit.window.extensions.get_instance()()
        ext_list_widget_model = instance._window._exts_list_widget._model
        for group in ext_list_widget_model.get_item_children(None):
            if isinstance(group, omni.kit.window.extensions.exts_list_widget.ExtSampleGroupItem):
                for item in group.items:
                    if not item.is_local:
                        ext_list_widget_model.filter_by_text([item.fullname])
                        await ui_test.human_delay(50)

                        # click on extension
                        await ui_test.find("Extensions//Frame/**/Label[*].identifier=='Title'").click()
                        await ui_test.human_delay(10)
                        break

        ext_list_widget_model = None
        await ui_test.human_delay(50)

    async def test_featured(self):
        instance = omni.kit.window.extensions.get_instance()()
        ext_list_widget_model = instance._window._exts_list_widget._model

        # enable filter "App"
        await ui_test.find("Extensions//Frame/**/Button[*].identifier=='filter'").click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Featured")
        await ui_test.human_delay(10)

        # get filtered group list
        filtered_items = {group.name: len(group.items) for group in ext_list_widget_model.get_item_children(None)}

        # close the menu as filter is persistent
        instance._window._exts_list_widget.close_filter_menu()
        await ui_test.human_delay(10)

        # verify there are 1 featured extension 'omni.kit.window.extensions' which is in test toml
        self.assertEqual(filtered_items, {"Core": 1, "Sample": 0, "Internal": 0, "Deprecated": 0})
        ext_list_widget_model = None

    async def test_custom_menu(self):
        # don't include at top as test_uninstall unloads extension and the wrong versions are referenced
        from omni.kit.window.extensions import ExtsWindowExtension
        from omni.kit.window.extensions.ext_info_widget import PageBase

        class OneExtensionPage(PageBase):
            def __init__(self):
                pass

            def build_tab(self, ext_info, ext_item: bool):
                ui.Button(name="create", width=22, height=22, identifier="create")
                ui.Spacer(width=2)

            def destroy(self):
                pass

            def sort_index(self):
                return "1stMenuBefore"

        class TwoExtensionPage(PageBase):
            def __init__(self):
                pass

            def build_tab(self, ext_info, ext_item: bool):
                ui.Button(name="create", width=22, height=22, identifier="create")
                ui.Spacer(width=2)

            def destroy(self):
                pass

            def sort_index(self):
                return "2ndMenuBefore"

        class ThreeExtensionPage(PageBase):
            def __init__(self):
                pass

            def build_tab(self, ext_info, ext_item: bool):
                ui.Button(name="create", width=22, height=22, identifier="create")
                ui.Spacer(width=2)

            def destroy(self):
                pass

            def sort_index(self):
                return "3ndMenuBefore"

        class FourExtensionPage(PageBase):
            def __init__(self):
                pass

            def build_tab(self, ext_info, ext_item: bool):
                ui.Button(name="create", width=22, height=22, identifier="create")
                ui.Spacer(width=2)

            def destroy(self):
                pass

            def sort_index(self):
                return "99LastMenu"

        # close filter menu
        instance = omni.kit.window.extensions.get_instance()()
        instance._window._exts_list_widget.close_filter_menu()
        await ui_test.human_delay(10)

        # add custom menu icons
        ExtsWindowExtension.add_menu_to_info_widget(OneExtensionPage)
        ExtsWindowExtension.add_menu_to_info_widget(TwoExtensionPage)
        ExtsWindowExtension.add_menu_to_info_widget(ThreeExtensionPage)
        ExtsWindowExtension.add_menu_to_info_widget(FourExtensionPage)

        # filter extensions
        instance._window._exts_list_widget._model.filter_by_text(["my.hovercraft.is.full.of.eels"])

        # hide scrolling frame as they contain numbers and will break test
        for w in ui_test.find_all("Extensions//Frame/**/ScrollingFrame[*]"):
            w.widget.visible = False
        await ui_test.human_delay(150)

        # take golden image
        golden_img_dir = Path(get_test_data_path(__name__, "golden_img"))
        await self.finalize_test(golden_img_dir=golden_img_dir, golden_img_name="test_custom_menus.png")
        await ui_test.human_delay(50)

        # cleanup
        ExtsWindowExtension.remove_menu_from_info_widget(OneExtensionPage)
        ExtsWindowExtension.remove_menu_from_info_widget(TwoExtensionPage)
        ExtsWindowExtension.remove_menu_from_info_widget(ThreeExtensionPage)
        ExtsWindowExtension.remove_menu_from_info_widget(FourExtensionPage)
        await ui_test.human_delay(50)
