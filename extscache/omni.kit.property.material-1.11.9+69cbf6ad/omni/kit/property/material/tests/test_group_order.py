from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class TestMaterialGroupOrder(MaterialPropertiesTestBase):
    async def setUp(self):
        await super().setUp()
        await arrange_windows("Stage", 64)

    async def tearDown(self):
        await super().tearDown()

    async def test_material_group_order(self):
        scene_file_path = self._get_scene_path("ABrick.usda")
        await self._load_scene(scene_file_path)
        await self._select_prims(["/World/Looks/ABrick"])

        for widget_ref in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            widget_ref.widget.collapsed = True

            if (widget_ref.widget.title in ["Material and Shader", "Shader"]) or ("Surface" in widget_ref.widget.title):
                widget_ref.widget.collapsed = False

        await self._dock_test_window(300, 500)
        await self._golden_image_compare("test_material_group_order.png")
