## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import carb
import omni.usd
import omni.kit.app
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test


class PreferencesTestDragDropImport(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        carb.settings.get_settings().set("/persistent/app/material/dragDropMaterialPath", "Absolute")
        omni.kit.window.preferences.show_preferences_window()

        for page in omni.kit.window.preferences.get_page_list():
            if page.get_title() == "Material":
                omni.kit.window.preferences.select_page(page)
                await ui_test.human_delay(50)
                break

    # After running each test
    async def tearDown(self):
        carb.settings.get_settings().set("/persistent/app/material/dragDropMaterialPath", "Absolute")
        omni.kit.window.preferences.hide_preferences_window()

    async def test_app_material_drag_drop_path(self):
        frame = ui_test.find("Preferences//Frame/**/CollapsableFrame[*].identifier=='preferences_builder_Material'")
        # OM-91518: should use underline instead of the slash of ComboBox widget identifier
        import_combo = frame.find("**/ComboBox[*].identifier=='_persistent_app_material_dragDropMaterialPath'")
        index_model = import_combo.model.get_item_value_model(None, 0)

        import_list = import_combo.model.get_item_children(None)
        for index, item in enumerate(import_list):
            index_model.set_value(item.model.value)
            await ui_test.human_delay(50)
            self.assertEqual(carb.settings.get_settings().get('/persistent/app/material/dragDropMaterialPath'), item.model.as_string)
