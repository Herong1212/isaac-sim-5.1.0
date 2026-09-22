import weakref
import unittest
import pathlib
import omni.kit.test
import omni.ui as ui
import carb
from omni.kit import ui_test
from pxr import Usd, Sdf, UsdGeom, UsdShade
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.test_suite.helpers import open_stage, get_test_data_path, select_prims, wait_stage_loading


class TestTextureColorSpaceWidget(OmniUiTest):

    # Before running each test
    async def setUp(self):
        await open_stage(get_test_data_path(__name__, "usd/color_map_types.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_texture_color_space_widget(self):
        usd_context = omni.usd.get_context()

        # verify non-raw values
        await select_prims(["/World/Sphere"])
        await wait_stage_loading()
        await select_prims(["/World/Looks/OmniPBR/Shader"])
        await wait_stage_loading()

        widgets = ui_test.find_all("Property//Frame/**/ComboBox[*]")
        excpect_values = {
            "colorspace_inputs:diffuse_texture": 0,
            "colorspace_inputs:reflectionroughness_texture": 0,
            "colorspace_inputs:metallic_texture": 0,
            "colorspace_inputs:ORM_texture": 0,
            "colorspace_inputs:ao_texture": 0,
            "colorspace_inputs:emissive_color_texture": 0,
            "colorspace_inputs:emissive_mask_texture": 0,
            "colorspace_inputs:opacity_texture": 0,
            "colorspace_inputs:normalmap_texture": 0,
            "colorspace_inputs:detail_normalmap_texture": 0,
        }
        for w in widgets:
            if w.widget.identifier.startswith("colorspace_inputs:"):
                self.assertEqual(excpect_values[w.widget.identifier], w.model.get_item_value_model(None, 0).as_int)
                del excpect_values[w.widget.identifier]
        self.assertEqual(excpect_values, {})

        # verify raw values
        await select_prims(["/World/Cone"])
        await wait_stage_loading()
        await select_prims(["/World/Looks/OmniPBR_raw_types/Shader"])
        await wait_stage_loading()

        widgets = ui_test.find_all("Property//Frame/**/ComboBox[*]")
        excpect_values = {
            "colorspace_inputs:diffuse_texture": 2,
            "colorspace_inputs:reflectionroughness_texture": 1,
            "colorspace_inputs:metallic_texture": 1,
            "colorspace_inputs:ORM_texture": 0,
            "colorspace_inputs:ao_texture": 1,
            "colorspace_inputs:emissive_color_texture": 0,
            "colorspace_inputs:emissive_mask_texture": 0,
            "colorspace_inputs:opacity_texture": 1,
            "colorspace_inputs:normalmap_texture": 1,
            "colorspace_inputs:detail_normalmap_texture": 0,
        }
        for w in widgets:
            if w.widget.identifier.startswith("colorspace_inputs:"):
                self.assertEqual(excpect_values[w.widget.identifier], w.model.get_item_value_model(None, 0).as_int)
                del excpect_values[w.widget.identifier]
        self.assertEqual(excpect_values, {})
