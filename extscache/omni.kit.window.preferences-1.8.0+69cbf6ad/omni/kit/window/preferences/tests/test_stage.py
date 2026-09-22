## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import carb
import omni.usd
import omni.kit.app
from omni.kit.test.async_unittest import AsyncTestCase


class PreferencesTestDragDropImport(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        from omni.kit import ui_test

        carb.settings.get_settings().set("/persistent/app/stage/dragDropImport", "reference")
        omni.kit.window.preferences.show_preferences_window()

        for page in omni.kit.window.preferences.get_page_list():
            if page.get_title() == "Stage":
                omni.kit.window.preferences.select_page(page)
                await ui_test.human_delay(50)
                break

    # After running each test
    async def tearDown(self):
        carb.settings.get_settings().set("/persistent/app/stage/dragDropImport", "reference")


    async def test_l1_app_stage_drag_drop_import(self):
        from omni.kit import ui_test

        frame = ui_test.find("Preferences//Frame/**/CollapsableFrame[*].identifier=='preferences_builder_Import'")
        import_combo = frame.find("**/ComboBox[*]")
        import_combo.widget.scroll_here_y(0.5)
        await ui_test.human_delay(50)
        index_model = import_combo.model.get_item_value_model(None, 0)

        import_list = import_combo.model.get_item_children(None)
        for index, item in enumerate(import_list):
            index_model.set_value(item.model.value)
            await ui_test.human_delay(50)
            self.assertEqual(carb.settings.get_settings().get('/persistent/app/stage/dragDropImport'), item.model.as_string)

    async def test_default_meters_zero(self):
        from omni.kit import ui_test

        # get widgets
        await ui_test.human_delay(10)
        frame = ui_test.find("Preferences//Frame/**/CollapsableFrame[*].identifier=='preferences_builder_New Stage'")
        widget = frame.find("**/FloatSlider[*].identifier=='default_meters_per_unit'")

        # set to 0.5
        widget.model.set_value(0.5)
        await ui_test.human_delay(10)

        # set to 0.0 - This is not allowed as minimum if 0.01
        widget.model.set_value(0.0)
        await ui_test.human_delay(10)

        # verify
        self.assertAlmostEqual(widget.model.get_value_as_float(), 0.5)
