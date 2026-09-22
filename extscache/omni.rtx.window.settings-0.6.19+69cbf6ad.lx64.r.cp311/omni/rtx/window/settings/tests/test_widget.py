import os
import shutil
import carb
import omni.kit.test
import omni.usd
import tempfile
import rtx.settings
from pathlib import Path
from tempfile import TemporaryDirectory
from omni.rtx.window.settings.rtx_settings_widget import RTXSettingsWidget
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.test_suite.helpers import wait_for_viewport_ready, arrange_windows


class TestWidget(OmniUiTest):
    async def setUp(self):
        await super().setUp()
        # We need to trigger Iray load to get the default render-settings values written to carb.settings
        # Viewports state is valid without any open stage, and only loads renderer when stage is opened.
        await omni.usd.get_context().new_stage_async()
        await wait_for_viewport_ready()

    # After running each test
    async def tearDown(self):
        pass

    async def test_widget(self):
        import omni.ui as ui
        from omni.kit import ui_test
        from omni.kit.test_suite.helpers import get_test_data_path, wait_stage_loading

        golden_img_dir = Path(get_test_data_path(__name__, "golden_img"))

        await wait_stage_loading()

        # this window should not exist
        window = ui.Workspace.get_window("Render Settings")
        self.assertEqual(window, None)

        window = ui.Window("My Render Settings", width=500, height=500)
        settings_widget = RTXSettingsWidget(window.frame)
        settings_widget.build_ui()
        settings_widget.build_stacks()

        await self.docked_test_window(window=window, width=500, height=500, block_devices=False)
        await ui_test.human_delay(50)

        try:
            await self.finalize_test(golden_img_dir=golden_img_dir, golden_img_name="test_widget.png")
        finally:
            await ui_test.human_delay(50)

    async def test_widget_save_overwrite(self):
        import omni.ui as ui
        from omni.kit import ui_test
        from omni.kit.test_suite.helpers import get_test_data_path, wait_stage_loading, wait_for_window
        from omni.kit.window.file_exporter.test_helper import FileExporterTestHelper

        await wait_stage_loading()

        # this window should not exist
        window = ui.Workspace.get_window("Render Settings")
        self.assertEqual(window, None)

        window = ui.Window("My Render Settings", width=500, height=500)
        settings_widget = RTXSettingsWidget(window.frame)
        settings_widget.build_ui()
        settings_widget.build_stacks()

        await wait_for_window("My Render Settings")

        # NOTE: Although hamburger menus are not context menus, they behave very much like one.
        # click menu button (only hamburger menu will have style with URL)
        await ui_test.find_all("My Render Settings//Frame/**/Button[*].style!=None")[0].click()

        tmpdir = tempfile.mkdtemp()
        output_file = f"{tmpdir}/test.settings.usd"

        # save settings
        async with FileExporterTestHelper() as file_export_helper:
            await ui_test.select_context_menu("Save Settings")
            await file_export_helper.wait_for_popup()
            await file_export_helper.click_apply_async(filename_url=output_file)
            await ui_test.human_delay(10)
            # verify there is no overwrite dialog
            self.assertEqual(ui.Workspace.get_window("Overwrite"), None)

        # verify file exists
        self.assertTrue(os.path.exists(output_file))

        # click menu button (only hamburger menu will have style with URL)
        await ui_test.find_all("My Render Settings//Frame/**/Button[*].style!=None")[0].click()

        # save settings again, should get overwrite dialog
        async with FileExporterTestHelper() as file_export_helper:
            await ui_test.select_context_menu("Save Settings")
            await file_export_helper.wait_for_popup()
            await file_export_helper.click_apply_async(filename_url=output_file)
            # verify there is overwrite dialog
            await wait_for_window("Overwrite")
            await ui_test.find_all("Overwrite//Frame/**/Button[*].name=='confirm_button'")[0].click()

        # delete temp home dir
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)
