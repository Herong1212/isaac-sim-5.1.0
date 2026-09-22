import omni.ui as ui
import omni.usd
from omni.kit import ui_test
from omni.kit.material.library.listbox_widget import MaterialListBoxWidget
from omni.kit.test_suite.helpers import arrange_windows, wait_stage_loading

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class TestMaterialWidget(MaterialPropertiesTestBase):
    async def setUp(self):
        await super().setUp()
        await arrange_windows()

    async def _build_test_stage(self):
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        omni.kit.property.material.tests.create_test_stage()

    async def test_material_ui(self):
        await self._build_test_stage()
        await self._dock_test_window(450, 285)
        self._usd_context.get_selection().set_selected_prim_paths(["/LightPivot_01/AreaLight/Backside"], True)
        await ui_test.human_delay(10)
        await self._golden_image_compare("test_material_ui.png")
        await self._select_prims([])

    async def test_material_multiselect_ui(self):
        await self._build_test_stage()
        await self._dock_test_window(450, 520)
        self._usd_context.get_selection().set_selected_prim_paths(
            ["/LightPivot_01/AreaLight/Backside", "/LightPivot_01/AreaLight/EmissiveSurface"], True
        )
        await ui_test.human_delay(10)
        await self._golden_image_compare("test_material_multiselect_ui.png")
        await self._select_prims([])

    async def _create_window(self, name_field_model_value: str, list_box_search: str = ""):
        window = await self.create_test_window(width=460, height=380)

        with window.frame:
            with ui.VStack(width=0, height=0):
                with ui.HStack(width=0, height=0):
                    name_field = ui.StringField(width=400, height=20, enabled=False)
                    name_field.model.set_value(name_field_model_value)

                await ui_test.human_delay(10)

                listbox_widget = MaterialListBoxWidget(icon_path=None, index=0, on_click_fn=None, theme={})
                listbox_widget.set_parent(name_field)
                listbox_widget.build_ui()
                # material loading is async so allow for loading
                await ui_test.human_delay(50)

                if list_box_search:
                    listbox_widget._search_updated(list_box_search)
                    await wait_stage_loading()
                    await ui_test.human_delay(10)

        return window

    async def test_material_popup_full_ui(self):
        scene_file_path = self._get_scene_path("material_binding.usda")
        await self._load_scene(scene_file_path)

        test_window = await self._create_window("TEST")
        self.assertIsNotNone(test_window)
        # cursor flashes on linux
        await self._golden_image_compare("test_material_popup1_ui.png", threshold=0.011)
        await self._select_prims([])

    async def test_material_popup_search_ui(self):
        scene_file_path = self._get_scene_path("material_binding.usda")
        await self._load_scene(scene_file_path)

        test_window = await self._create_window("SEARCH", "PBR")
        self.assertIsNotNone(test_window)
        # cursor flashes on linux
        await self._golden_image_compare("test_material_popup2_ui.png", threshold=0.011)
        await self._select_prims([])

    async def test_material_description_ui(self):
        omni.kit.window.property.managed_frame.set_collapsed_state("Material and Shader/Description", False)

        scene_file_path = self._get_scene_path("material_binding.usda")
        await self._load_scene(scene_file_path)

        await self._dock_test_window(700, 310)
        await self._select_prims(["/World/Looks/OmniPBR"])

        for w in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            w.widget.collapsed = True

            if (w.widget.title in ["Material and Shader", "Shader", "Description"]) or ("Surface" in w.widget.title):
                w.widget.collapsed = False

        await ui_test.human_delay(50)
        await self._golden_image_compare("test_material_description_ui.png")
        await self._select_prims([])

    async def test_material_ordering(self):
        scene_file_path = self._get_scene_path("ordering_test.usda")
        await self._load_scene(scene_file_path)

        for i in range(1, 4):
            await self._dock_test_window(450, 550)
            await self._select_prims([f"/World/Looks/diffuse_0{i}/Shader"])

            for w in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
                w.widget.collapsed = w.widget.title not in ["Shader", "Inputs", "A group", "A subgroup"]

            await self._golden_image_compare(f"test_material_ordering{i}_ui.png")
            await self._select_prims([])

    async def test_material_bound_missing(self):
        scene_file_path = self._get_scene_path("bad_mtl_on_world.usda")
        await self._load_scene(scene_file_path)

        await self._dock_test_window(450, 550)
        await self._select_prims(["/World"])
        await self._golden_image_compare("test_material_bound_missing_1.png")
        await self._select_prims([])

    async def test_material_bound_missing_inherited(self):
        scene_file_path = self._get_scene_path("bad_mtl_on_world.usda")
        await self._load_scene(scene_file_path)

        await self._dock_test_window(450, 550)
        await self._select_prims(["/World/grill"])
        await self._golden_image_compare("test_material_bound_missing_2.png")
        await self._select_prims([])
