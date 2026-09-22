import omni.usd
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class TestMaterialFilterWidget(MaterialPropertiesTestBase):
    async def setUp(self):
        await super().setUp()
        await arrange_windows("Property", 128)

        scene_file_path = self._get_scene_path("material_binding.usda")
        await self._load_scene(scene_file_path)
        await self._select_prims(["/World/Cube"])

    async def test_material_filter1_ui(self):
        # add filter func
        def filter_func(prim):
            if "PBR" in prim.GetPrimPath().pathString:
                return True
            return False

        omni.kit.material.library.add_materials_from_stage_filter_func(filter_func)

        # open material combobox
        topmost_button = sorted(
            ui_test.find_all("Property//Frame/**/Button[*].identifier=='combo_open_button'"), key=lambda f: f.position.y
        )[0]
        await topmost_button.click(human_delay_speed=4)
        await ui_test.human_delay(10)

        try:
            # verify list
            widget = ui_test.find("MaterialPropertyPopupWindow//Frame/**/TreeView[*]")
            mtl_list = [item.name_model.as_string for item in widget.model.get_item_children(None)]
            self.assertEqual(
                mtl_list,
                [
                    "$NONE$",
                    "/World/Looks/OmniPBR",
                    "/World/Looks/OmniPBR_ClearCoat",
                    "/World/Looks/OmniPBR_ClearCoat_Opacity",
                    "/World/Looks/OmniPBR_Opacity",
                ],
            )
        finally:
            # remove filter
            omni.kit.material.library.remove_materials_from_stage_filter_func(filter_func)

    async def test_material_filter2_ui(self):
        # add filter func
        def filter_func(prim):
            if "Glass" in prim.GetPrimPath().pathString:
                return True
            return False

        omni.kit.material.library.add_materials_from_stage_filter_func(filter_func)

        # open material combobox
        topmost_button = sorted(
            ui_test.find_all("Property//Frame/**/Button[*].identifier=='combo_open_button'"), key=lambda f: f.position.y
        )[0]
        await topmost_button.click(human_delay_speed=4)
        await ui_test.human_delay(10)

        try:
            # verify list
            widget = ui_test.find("MaterialPropertyPopupWindow//Frame/**/TreeView[*]")
            mtl_list = [item.name_model.as_string for item in widget.model.get_item_children(None)]
            self.assertEqual(mtl_list, ["$NONE$", "/World/Looks/OmniGlass", "/World/Looks/OmniGlass_Opacity"])
        finally:
            # remove filter
            omni.kit.material.library.remove_materials_from_stage_filter_func(filter_func)
