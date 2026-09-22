import weakref
import platform
import unittest
import pathlib
import omni.kit.test
import omni.ui as ui
import carb
from pxr import Usd, Sdf, UsdGeom
from omni.ui.tests.test_base import OmniUiTest
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows, wait_stage_loading, get_test_data_path


class TestMaterialFilterWidget(OmniUiTest):
    async def setUp(self):
        await super().setUp()
        await arrange_windows("Property", 128)

    async def tearDown(self):
        await super().tearDown()

    async def test_material_filter1_ui(self):
        usd_context = omni.usd.get_context()
        await usd_context.open_stage_async(get_test_data_path(__name__, "usd/material_binding.usda"))
        await omni.kit.app.get_app().next_update_async()

        # add filter func
        def filter_func(prim):
            if "PBR" in prim.GetPrimPath().pathString:
                return True
            return False

        omni.kit.material.library.add_materials_from_stage_filter_func(filter_func)

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World/Cube"], True)
        await wait_stage_loading()

        # open material combobox
        topmost_button = sorted(ui_test.find_all("Property//Frame/**/Button[*].identifier=='combo_open_button'"), key=lambda f: f.position.y)[0]
        await topmost_button.click(human_delay_speed=4)
        await ui_test.human_delay(10)

        try:
            # verify list
            widget = ui_test.find(f"MaterialPropertyPopupWindow//Frame/**/TreeView[*]")
            mtl_list = [item.name_model.as_string for item in widget.model.get_item_children(None)]
            self.assertEqual(mtl_list, ['$NONE$', '/World/Looks/OmniPBR', '/World/Looks/OmniPBR_ClearCoat', '/World/Looks/OmniPBR_ClearCoat_Opacity', '/World/Looks/OmniPBR_Opacity'])
        finally:
            # remove filter
            omni.kit.material.library.remove_materials_from_stage_filter_func(filter_func)

    async def test_material_filter2_ui(self): #fixme
        usd_context = omni.usd.get_context()
        await usd_context.open_stage_async(get_test_data_path(__name__, "usd/material_binding.usda"))
        await omni.kit.app.get_app().next_update_async()

        # add filter func
        def filter_func(prim):
            if "Glass" in prim.GetPrimPath().pathString:
                return True
            return False

        omni.kit.material.library.add_materials_from_stage_filter_func(filter_func)

        # Select the prim.
        usd_context.get_selection().set_selected_prim_paths(["/World/Cube"], True)
        await wait_stage_loading()

        # open material combobox
        topmost_button = sorted(ui_test.find_all("Property//Frame/**/Button[*].identifier=='combo_open_button'"), key=lambda f: f.position.y)[0]
        await topmost_button.click(human_delay_speed=4)
        await ui_test.human_delay(10)

        try:
            # verify list
            widget = ui_test.find(f"MaterialPropertyPopupWindow//Frame/**/TreeView[*]")
            mtl_list = [item.name_model.as_string for item in widget.model.get_item_children(None)]
            self.assertEqual(mtl_list, ['$NONE$', '/World/Looks/OmniGlass', '/World/Looks/OmniGlass_Opacity'])
        finally:
            # remove filter
            omni.kit.material.library.remove_materials_from_stage_filter_func(filter_func)
