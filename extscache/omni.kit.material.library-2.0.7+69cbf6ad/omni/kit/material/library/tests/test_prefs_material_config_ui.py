## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import os
import tempfile
import posixpath
import shutil
import omni.kit.test
import carb
import omni.usd
import omni.kit.app
from pathlib import Path
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from omni.kit.window.file_importer.test_helper import FileImporterTestHelper


class PreferencesTestMaterialConfigPage(AsyncTestCase):
    # run only once at the beginning
    @classmethod
    def setUpClass(cls):
        # test config file path
        ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        data_tests_dir = Path(ext_path) / "data/tests"
        test_config_file_path = data_tests_dir / "material.config.toml"
        test_config_carb_file_path = data_tests_dir / "material.config.carb.toml"

        # create temp home dir
        cls._temp_home = Path(tempfile.mkdtemp())
        cls._temp_home = cls._temp_home.as_posix()

        # copy test config files to the temp home
        cls._temp_kit_shared_dir = posixpath.join(cls._temp_home, "Documents/Kit/shared")
        if not os.path.exists(cls._temp_kit_shared_dir):
            os.makedirs(cls._temp_kit_shared_dir)
        shutil.copy(test_config_file_path, cls._temp_kit_shared_dir)
        shutil.copy(test_config_carb_file_path, cls._temp_kit_shared_dir)

        # temporary wipe out material config in settings
        settings = carb.settings.get_settings()
        cls._curr_material_config = settings.get("/materialConfig")
        settings.set("/materialConfig", {})


    # run only once at the end
    @classmethod
    def tearDownClass(cls):
        # remove settings used in tests
        settings = carb.settings.get_settings()
        settings.destroy_item("/materialConfigTests")

        # restore material config in settings
        settings.set("/materialConfig", {})
        settings.set("/materialConfig", cls._curr_material_config)

        # delete temp home dir
        if os.path.exists(cls._temp_home):
            shutil.rmtree(cls._temp_home)


    # before running each test
    async def setUp(self):
        super().setUp()

        # new stage
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()

        # temporary set ${shared_documents} path
        carb_tokens = carb.tokens.get_tokens_interface()
        self._original_shared_dir = carb_tokens.resolve("${shared_documents}")
        carb_tokens.set_value("shared_documents", self._temp_kit_shared_dir)

        # show preferences window
        omni.kit.window.preferences.show_preferences_window()
        await ui_test.human_delay(10)
        window = omni.ui.Workspace.get_window("Preferences")
        window.position_x = 0
        window.position_y = 0
        window.width = 1440
        window.height = 880

    # after running each test
    async def tearDown(self): # pragma: no cover
        super().tearDown()
        carb.tokens.get_tokens_interface().set_value("shared_documents", self._original_shared_dir)
        omni.kit.window.preferences.hide_preferences_window()

    async def test_material_config_page(self):
        import omni.kit.material.library.material_config_utils as mc_utils

        # select preferences page
        pages = omni.kit.window.preferences.get_page_list()
        for page in pages:
            if page.get_title() == "Material":
                omni.kit.window.preferences.select_page(page)
                await ui_test.human_delay(50)

        # collapse other frames that are not relevant
        for w in ui_test.find_all("Preferences//Frame/**/CollapsableFrame[*]"):
            if w.widget.title not in ["Material Search Path", "Custom Paths (requires app restart)"]:
                w.widget.collapsed = True
        await ui_test.human_delay(10)

        # click "+"
        await ui_test.human_delay(10)
        widget = ui_test.find("Preferences//Frame/**/Button[*].identifier=='material_config_plus'")
        await widget.click()

        # select file
        async with FileImporterTestHelper() as file_helper:
            await file_helper.wait_for_popup()
            await file_helper.click_apply_async(filename_url=self._temp_kit_shared_dir)
        await ui_test.human_delay(10)

        # click "save"
        await ui_test.human_delay(10)
        widget = ui_test.find("Preferences//Frame/**/Button[*].identifier=='material_config_save'")
        await widget.click()

        # click "delete"
        await ui_test.human_delay(10)

        # handle both as there is more than one found (?)
        for widget in ui_test.find_all("Preferences//Frame/**/Button[*].identifier=='material_config_delete'"):
            await widget.click()

            # click "save"
            await ui_test.human_delay(10)
            widget = ui_test.find("Preferences//Frame/**/Button[*].identifier=='material_config_save'")
            await widget.click()

            # click "+"
            await ui_test.human_delay(10)
            widget = ui_test.find("Preferences//Frame/**/Button[*].identifier=='material_config_plus'")
            await widget.click()

            # select file
            async with FileImporterTestHelper() as file_helper:
                await file_helper.wait_for_popup()
                await file_helper.click_apply_async(filename_url=self._temp_kit_shared_dir)
            await ui_test.human_delay(10)

            # click "reset"
            await ui_test.human_delay(10)
            widget = ui_test.find("Preferences//Frame/**/Button[*].identifier=='material_config_reset'")
            await widget.click()

        await ui_test.human_delay(10)
