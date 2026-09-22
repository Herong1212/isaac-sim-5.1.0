import random

import omni.usd
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger

# NOTE: These are code coverage tests then actual verify values tests as those could break overtime as materials are modified.


@time_logger
class TestMaterialUI(MaterialPropertiesTestBase):
    async def setUp(self):
        await super().setUp()
        await arrange_windows("Property", 128)

        scene_file_path = self._get_scene_path("material_binding.usda")
        await self._load_scene(scene_file_path)
        await self._select_prims(["/World/Cube"])

    async def test_material_infoid(self):
        await self._select_prims(["/World/Looks/PreviewSurface/Shader"])
        await ui_test.human_delay(10)

    async def test_material_change_subid(self):
        omni.kit.window.property.managed_frame.set_collapsed_state("Shader/Info", False)
        await self._select_prims(["/World/Looks/mtl_diffuse/add"])
        await ui_test.human_delay(50)

        widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Info'")
        self.assertIsNotNone(widget)
        combo_widget = widget.find("**/Frame/ComboBox[*].identifier=='token_info:mdl:sourceAsset:subIdentifier'")
        self.assertIsNotNone(combo_widget)
        combo_list = combo_widget.model.get_item_children(None)
        combo_list = [item.token for item in combo_list]
        combo_list = random.sample(combo_list, 10)  # NOSONAR - No security issue, not used for encryption

        for item in combo_list:
            widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Info'")
            self.assertIsNotNone(widget)
            combo_widget = widget.find("**/Frame/ComboBox[*].identifier=='token_info:mdl:sourceAsset:subIdentifier'")
            self.assertIsNotNone(combo_widget)
            combo_widget.model.set_value(item)
            await ui_test.human_delay(10)
            omni.kit.undo.undo()
            await ui_test.human_delay(10)

    async def test_material_props_layout(self):
        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Raw USD Properties", False)
        await self._select_prims(["/World/Looks/mtl_diffuse/add"])
        await ui_test.human_delay(10)

    async def test_material_matrix(self):
        await self._select_prims(["/World/Looks/mtl_matrix/matrix_float4x4"])
        await ui_test.human_delay(10)

    async def test_material_nodegraph(self):
        await self._select_prims(["/World/Looks/OmniSurface"])
        await ui_test.human_delay(10)

    async def test_material_backdrop(self):
        await self._select_prims(["/World/Looks/Backdrop/backdrop"])
        await ui_test.human_delay(10)

    async def test_material_source_asset(self):
        await self._select_prims(["/World/Looks/OmniSurfaceID/Shader"])
        await ui_test.human_delay(10)
        await self._select_prims(["/World/Looks/OmniSurfaceID/sdr_node"])
        await ui_test.human_delay(10)

    async def test_material_output_array(self):
        await self._select_prims(["/World/Looks/mtl_array/test_color_array"])
        await ui_test.human_delay(10)

    async def test_material_sdr_node(self):
        await self._select_prims(["/World/Looks/SimpleRman/pxrsurface1"])
        await ui_test.human_delay(10)
        await self._select_prims(["/World/Looks/SimpleRman/pxrsurface1_preview"])
        await ui_test.human_delay(10)

    async def test_material_metadata(self):
        await self._select_prims(["/World/Looks/OmniGlass"])
        await ui_test.human_delay(10)


# fixme:
# material collections
