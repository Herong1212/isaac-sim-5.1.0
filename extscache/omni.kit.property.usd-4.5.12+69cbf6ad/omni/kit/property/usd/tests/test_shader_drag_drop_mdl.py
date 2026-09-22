# pylint: disable=missing-function-docstring, missing-class-docstring
import omni.kit.test
import omni.kit.ui_test as ui_test
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
from omni.ui.tests.test_base import OmniUiTest
from pxr import Usd, UsdShade


class TestDragDropFileToMaterial(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await arrange_windows("Stage", 200)
        await open_stage(get_test_data_path(__name__, "usd/locate_file_material.usda"))
        await wait_stage_loading()

        self._usd_context = omni.usd.get_context()
        self._stage = self._usd_context.get_stage()

        self._material_path = "/World/Looks/OmniPBR"
        self._shader_path = "/World/Looks/OmniPBR/Shader"

    # After running each test
    async def tearDown(self):
        await super().tearDown()
        await wait_stage_loading()

    async def _select_prims(self, prim_paths):
        await select_prims(prim_paths)
        await wait_stage_loading()
        await ui_test.human_delay(10)

    def _get_prim_at_path(self, path):
        prim = self._stage.GetPrimAtPath(path)
        self.assertTrue(isinstance(prim, Usd.Prim) and prim.IsValid())
        return prim

    def _get_shader_from_material(self, path):
        prim = self._get_prim_at_path(path)
        self.assertTrue(prim.IsA(UsdShade.Material))

        shader = omni.usd.get_shader_from_material(prim, False)
        self.assertTrue(bool(shader))
        return shader

    async def _validate_initial_state(self):
        await self._select_prims([self._shader_path])
        shader = self._get_shader_from_material(self._material_path)
        source_asset = shader.GetSourceAsset("mdl")
        self.assertEqual(source_asset.path, "OmniPBR.mdl")

    async def _drag_and_drop(self, url, drag_target, names=None):
        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.drag_and_drop_tree_view(
                url, names=names if names else [], drag_target=drag_target, focus_treeview_items=False
            )
        await ui_test.human_delay(100)

    async def test_drag_drop_single_mdl_asset_path(self):
        await self._validate_initial_state()

        for widget_ref in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            widget_ref.widget.collapsed = widget_ref.widget.title not in ["Shader", "Info"]

        # drag file from content window
        property_widget = ui_test.find("Property//Frame/**/StringField[*].identifier=='sdf_asset_info:mdl:sourceAsset'")
        self.assertIsNotNone(property_widget)
        property_widget.widget.scroll_here_y(0.5)
        await ui_test.human_delay(10)

        url = get_test_data_path(__name__, "usd/TESTEXPORT.mdl")
        await self._drag_and_drop(url, property_widget.center)

        # verify asset
        shader = self._get_shader_from_material(self._material_path)
        source_asset = shader.GetSourceAsset("mdl")
        self.assertTrue(source_asset.path.endswith("/TESTEXPORT.mdl") or source_asset.path.endswith("\\TESTEXPORT.mdl"))

    async def test_drag_drop_single_png_asset_path(self):
        await self._validate_initial_state()

        success = False
        for widget_ref in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            widget_ref.widget.collapsed = widget_ref.widget.title not in ["Shader", "Inputs"]

            if widget_ref.widget.title == "Inputs":
                for sub_widget_ref in widget_ref.find_all("**/CollapsableFrame[*]"):
                    sub_widget_ref.widget.collapsed = False
                    string_field_widget_ref = sub_widget_ref.find(
                        "**/StringField[*].identifier=='sdf_asset_inputs:ao_texture'"
                    )

                    if string_field_widget_ref:
                        string_field_widget_ref.widget.scroll_here_y(0.0)
                        await ui_test.human_delay(10)

                        url = get_test_data_path(__name__, "usd/textures/granite_a_mask.png")
                        await self._drag_and_drop(url, string_field_widget_ref.center)

                        # verify material not changed
                        await self._validate_initial_state()

                        # verify asset
                        shader = self._get_shader_from_material(self._material_path)
                        prim = shader.GetPrim()
                        self.assertTrue(prim.IsValid())

                        asset_path = prim.GetAttribute("inputs:ao_texture").Get()
                        self.assertTrue(asset_path.path.endswith("textures/granite_a_mask.png"))
                        success = True
                        break

        self.assertTrue(success)

    async def test_drag_drop_multi_mdl_asset_path(self):
        await self._validate_initial_state()

        # drag file from content window
        property_widget = ui_test.find("Property//Frame/**/StringField[*].identifier=='sdf_asset_info:mdl:sourceAsset'")
        self.assertIsNotNone(property_widget)
        property_widget.widget.scroll_here_y(0.5)
        url = get_test_data_path(__name__, "usd")
        await self._drag_and_drop(url, property_widget.center, names=["TESTEXPORT.mdl", "TESTEXPORT2.mdl"])

        # verify material not changed
        await self._validate_initial_state()

    async def test_drag_drop_multi_png_asset_path(self):
        await self._validate_initial_state()

        # drag file from content window
        property_widget = ui_test.find("Property//Frame/**/StringField[*].identifier=='sdf_asset_inputs:ao_texture'")
        self.assertIsNotNone(property_widget)
        property_widget.widget.scroll_here_y(0.5)
        url = get_test_data_path(__name__, "usd/textures")
        await self._drag_and_drop(url, property_widget.center, names=["granite_a_mask.png", "granite_a_mask2.png"])

        # verify material not changed
        await self._validate_initial_state()

        # verify asset
        shader = self._get_shader_from_material(self._material_path)
        prim = shader.GetPrim()
        self.assertTrue(prim.IsValid())
        asset_path = prim.GetAttribute("inputs:ao_texture").Get()
        self.assertEqual(asset_path.path, "")
