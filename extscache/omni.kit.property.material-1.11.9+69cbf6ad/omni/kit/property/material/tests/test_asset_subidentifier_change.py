import math

import omni.kit.undo
import omni.usd
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows
from pxr import UsdShade

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class TestInfoChange(MaterialPropertiesTestBase):
    async def setUp(self):
        await super().setUp()
        await arrange_windows("Property")

    async def test_clear_source_asset(self):
        omni.kit.window.property.managed_frame.set_collapsed_state("Shader/Info", False)

        scene_file_path = self._get_scene_path("reload.usda")
        await self._load_scene(scene_file_path)

        prim_path = "/World/Looks/mtl_test/construct_float"

        # select shader
        await self._select_prims([prim_path])
        await ui_test.human_delay(10)

        # change sourceAsset
        source_asset_widget = ui_test.find_first(
            "Property//Frame/**/StringField[*].identifier=='sdf_asset_info:mdl:sourceAsset'"
        )
        self.assertTrue(source_asset_widget)

        source_asset_widget.model.set_value("")
        await ui_test.human_delay(10)

        await self._dock_test_window(450, 275)
        await self._golden_image_compare("test_clear_source_asset.png")

    async def test_change_subidentifer(self):
        def validate_parameters(usdshade_shader, parameters, after_change):
            for name, (expected_value, expected) in parameters.items():
                usdshade_input = usdshade_shader.GetInput(name)
                if after_change and not expected:
                    self.assertFalse(usdshade_input)
                    continue

                self.assertTrue(usdshade_input)
                value = usdshade_input.Get()

                if isinstance(value, float):
                    self.assertTrue(math.isclose(expected_value, float(value), rel_tol=1e-05))
                else:
                    for i, v in enumerate(value):
                        self.assertTrue(math.isclose(expected_value[i], float(v), rel_tol=1e-05))

        def validate_connections(usdshade_shader, connections, after_change):
            for name, (connected_to, expected) in connections.items():
                usdshade_input = usdshade_shader.GetInput(name)

                if after_change and not expected:
                    self.assertFalse(usdshade_input)
                    continue

                self.assertTrue(usdshade_input)

                connected_sources = usdshade_input.GetConnectedSources()
                self.assertTrue(connected_sources)

                source_info_vector = connected_sources[0]
                self.assertTrue(len(source_info_vector) == 1)

                connection_source_info = source_info_vector[0]
                source_prim = connection_source_info.source.GetPrim()
                source_prim_path = source_prim.GetPath()

                is_input = connection_source_info.sourceType == UsdShade.AttributeType.Input
                source_name_prefix = UsdShade.Tokens.inputs if is_input else UsdShade.Tokens.outputs

                attr_name = f"{source_name_prefix}{connection_source_info.sourceName}"
                attr_path = source_prim_path.AppendProperty(attr_name)

                self.assertTrue(attr_path == connected_to)

        omni.kit.window.property.managed_frame.set_collapsed_state("Shader/Info", False)

        scene_file_path = self._get_scene_path("scratched_metal.usda")
        await self._load_scene(scene_file_path)

        prim_path = "/World/Looks/mtl_test/scratched_metal_v2"
        prim = self._get_prim_at_path(prim_path)

        await self._select_prims([prim_path])
        await ui_test.human_delay(10)

        usdshade_shader = UsdShade.Shader(prim)
        self.assertTrue(usdshade_shader)

        # parameters and connections to test, the second item (bool) in the tuple indicates if the value/connection should exist after the subIdentifier change.
        parameters = {"anisotropy": (0.45, False), "metal_color": ((1, 0, 0), False)}

        connections = {
            "anisotropy_rotation": ("/World/Looks/mtl_test/float_const.outputs:out", False),
            "normal": ("/World/Looks/mtl_test/normal.outputs:out", True),
        }

        # verify the expected parameters and connections exist.
        validate_parameters(usdshade_shader, parameters, False)
        validate_connections(usdshade_shader, connections, False)

        subidentifier_widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Info'").find(
            "**/Frame/ComboBox[*].identifier=='token_info:mdl:sourceAsset:subIdentifier'"
        )
        self.assertTrue(subidentifier_widget)

        # change subidentifer
        subidentifier_widget.model.set_value("dusty_diffuse")
        await ui_test.human_delay(10)

        validate_parameters(usdshade_shader, parameters, True)
        validate_connections(usdshade_shader, connections, True)
