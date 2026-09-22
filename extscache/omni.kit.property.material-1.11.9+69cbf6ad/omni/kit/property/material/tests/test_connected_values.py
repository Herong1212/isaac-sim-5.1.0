import omni.usd
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class TestMaterialConnectedValues(MaterialPropertiesTestBase):
    async def setUp(self):
        await super().setUp()
        await arrange_windows("Stage", 64, topleft_width=600.0)

    async def test_connected_value1(self):
        omni.kit.window.property.managed_frame.set_collapsed_state("Shader/Outputs", False)
        omni.kit.window.property.managed_frame.set_collapsed_state("Shader/Info", True)

        scene_file_path = self._get_scene_path("connected_values1.usda")
        await self._load_scene(scene_file_path)

        await self._dock_test_window(600, 600)
        await self._select_prims(["/World/Looks/Material/scratched_metal_v2"])
        await self._golden_image_compare("connected1_1.png")
        await self._select_prims([])

        await self._dock_test_window(600, 500)
        await self._select_prims(["/World/Looks/Material/add"])
        await self._golden_image_compare("connected1_2.png")
        await self._select_prims([])

    async def test_connected_value2(self):
        scene_file_path = self._get_scene_path("connected_values2.usda")
        await self._load_scene(scene_file_path)

        await self._dock_test_window(600, 600)
        await self._select_prims(["/World/Looks/Material"])

        for w in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            w.widget.collapsed = True

            if (w.widget.title in ["Material and Shader", "Shader"]) or ("Surface" in w.widget.title):
                w.widget.collapsed = False

        await self._golden_image_compare("connected2_1.png")
        await self._select_prims([])

        await self._dock_test_window(600, 600)
        await self._select_prims(["/World/Looks/Material"])
        widget = ui_test.find("Property//Frame/**/.identifier=='drag_per_channel_inputs:edge_color'")
        models = [w.model for w in widget.find_all("**/FloatSlider[*]")]
        for model in models:
            model.set_value(0.25)
        await ui_test.human_delay(10)

        await self._golden_image_compare("connected2_2.png")
