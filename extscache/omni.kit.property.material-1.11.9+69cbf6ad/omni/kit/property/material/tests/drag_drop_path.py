## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

import os

import omni.usd
from omni.kit import ui_test
from omni.kit.material.library.test_helper import MaterialLibraryTestHelper
from omni.kit.test_suite.helpers import arrange_windows
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper

from .test_base import MaterialPropertiesTestBase
from .utils import time_logger


@time_logger
class DragDropFilePropertyMaterialPath(MaterialPropertiesTestBase):
    DRAG_DROP_MATERIAL_PATH_SETTING = "/persistent/app/material/dragDropMaterialPath"

    # Before running each test
    async def setUp(self):
        await super().setUp()
        scene_file_path = self._get_scene_path("bound_material.usda")
        await self._load_scene(scene_file_path)
        await arrange_windows("Stage", 64)

    # After running each test
    async def tearDown(self):
        self._settings.set(self.DRAG_DROP_MATERIAL_PATH_SETTING, "absolute")
        await super().tearDown()

    async def test_l1_drag_drop_path_drop_target_absolute(self):
        self._settings.set(self.DRAG_DROP_MATERIAL_PATH_SETTING, "absolute")
        await ui_test.find("Stage").focus()
        await ui_test.find("Content").focus()

        # create prims
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere")
        await self._select_prims(["/World/Sphere"])

        # drag file from content window
        property_widget = ui_test.find_first("Property//Frame/**/Button[*].identifier=='preview_drop_target'")
        self.assertIsNotNone(property_widget)

        async with ContentBrowserTestHelper() as content_browser_helper:
            mdl_path = self._get_mdl_path("badname.mdl")
            await content_browser_helper.drag_and_drop_tree_view(mdl_path, drag_target=property_widget.center)

        # verify prims
        prim = self._get_prim_at_path("/World/Looks/Ue4basedMDL")
        shader = self._get_shader_from_material(prim)
        self.assertTrue(bool(shader), "/World/Looks/Ue4basedMDL not found")
        asset = shader.GetSourceAsset("mdl")
        self.assertTrue(os.path.isabs(asset.path))

    async def test_l1_drag_drop_path_combo_absolute(self):
        self._settings.set(self.DRAG_DROP_MATERIAL_PATH_SETTING, "absolute")
        await ui_test.find("Stage").focus()
        await ui_test.find("Content").focus()

        # create prims
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere")
        await self._select_prims(["/World/Sphere"])

        # drag file from content window
        property_widget = ui_test.find_first("Property//Frame/**/StringField[*].identifier=='combo_drop_target'")
        self.assertIsNotNone(property_widget)

        async with ContentBrowserTestHelper() as content_browser_helper:
            mdl_path = self._get_mdl_path("badname.mdl")
            await content_browser_helper.drag_and_drop_tree_view(mdl_path, drag_target=property_widget.center)

        # verify prims
        prim = self._get_prim_at_path("/World/Looks/Ue4basedMDL")
        shader = self._get_shader_from_material(prim)
        self.assertTrue(bool(shader), "/World/Looks/Ue4basedMDL not found")
        asset = shader.GetSourceAsset("mdl")
        self.assertTrue(os.path.isabs(asset.path))

    async def test_l1_drag_drop_path_asset_absolute(self):
        self._settings.set(self.DRAG_DROP_MATERIAL_PATH_SETTING, "absolute")
        await ui_test.find("Stage").focus()
        await ui_test.find("Content").focus()

        # create prims
        await self._select_prims(["/World/Looks/OmniHair/Shader"])

        for widget_ref in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            widget_ref.widget.collapsed = widget_ref.widget.title not in ["Shader", "Info"]
        await ui_test.human_delay(50)

        # drag file from content window
        property_widget = ui_test.find_first(
            "Property//Frame/**/StringField[*].identifier=='sdf_asset_info:mdl:sourceAsset'"
        )

        self.assertIsNotNone(property_widget)
        async with ContentBrowserTestHelper() as content_browser_helper:
            mdl_path = self._get_mdl_path("OmniHairTest.mdl")
            await content_browser_helper.drag_and_drop_tree_view(mdl_path, drag_target=property_widget.center)

        await ui_test.human_delay(50)

        # verify prims
        prim = self._get_prim_at_path("/World/Looks/OmniHair")
        shader = self._get_shader_from_material(prim)
        asset = shader.GetSourceAsset("mdl")
        self.assertTrue(os.path.isabs(asset.path))

    async def test_l1_drag_drop_path_drop_target_relative(self):
        self._settings.set(self.DRAG_DROP_MATERIAL_PATH_SETTING, "relative")
        await ui_test.find("Stage").focus()
        await ui_test.find("Content").focus()

        # create prims
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere")
        await self._select_prims(["/World/Sphere"])

        # drag file from content window
        property_widget = ui_test.find_first("Property//Frame/**/Button[*].identifier=='preview_drop_target'")
        self.assertIsNotNone(property_widget)

        async with ContentBrowserTestHelper() as content_browser_helper:
            mdl_path = self._get_mdl_path("badname.mdl")
            await content_browser_helper.drag_and_drop_tree_view(mdl_path, drag_target=property_widget.center)

        # verify prims
        prim = self._get_prim_at_path("/World/Looks/Ue4basedMDL")
        shader = self._get_shader_from_material(prim)
        self.assertTrue(bool(shader), "/World/Looks/Ue4basedMDL not found")
        asset = shader.GetSourceAsset("mdl")
        self.assertFalse(os.path.isabs(asset.path))

    async def test_l1_drag_drop_path_combo_relative(self):
        self._settings.set(self.DRAG_DROP_MATERIAL_PATH_SETTING, "relative")
        await ui_test.find("Stage").focus()
        await ui_test.find("Content").focus()

        # create prims
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere")
        await self._select_prims(["/World/Sphere"])

        # drag file from content window
        property_widget = ui_test.find_first("Property//Frame/**/StringField[*].identifier=='combo_drop_target'")
        self.assertIsNotNone(property_widget)

        async with ContentBrowserTestHelper() as content_browser_helper:
            mdl_path = self._get_mdl_path("badname.mdl")
            await content_browser_helper.drag_and_drop_tree_view(mdl_path, drag_target=property_widget.center)

        # verify prims
        prim = self._get_prim_at_path("/World/Looks/Ue4basedMDL")
        shader = self._get_shader_from_material(prim)
        self.assertTrue(bool(shader), "/World/Looks/Ue4basedMDL not found")
        asset = shader.GetSourceAsset("mdl")
        self.assertFalse(os.path.isabs(asset.path))

    async def test_l1_drag_drop_path_asset_relative(self):
        self._settings.set(self.DRAG_DROP_MATERIAL_PATH_SETTING, "relative")
        await ui_test.find("Stage").focus()
        await ui_test.find("Content").focus()

        await self._select_prims(["/World/Looks/OmniHair/Shader"])

        # drag file from content window
        property_widget = ui_test.find_first(
            "Property//Frame/**/StringField[*].identifier=='sdf_asset_info:mdl:sourceAsset'"
        )
        self.assertIsNotNone(property_widget)

        async with ContentBrowserTestHelper() as content_browser_helper:
            mdl_path = self._get_mdl_path("OmniHairTest.mdl")
            await content_browser_helper.drag_and_drop_tree_view(mdl_path, drag_target=property_widget.center)

        # verify prims
        prim = self._get_prim_at_path("/World/Looks/OmniHair")
        shader = self._get_shader_from_material(prim)
        asset = shader.GetSourceAsset("mdl")
        self.assertFalse(os.path.isabs(asset.path))

    async def test_l1_drag_drop_path_drop_target_multi_absolute(self):
        self._settings.set(self.DRAG_DROP_MATERIAL_PATH_SETTING, "absolute")
        await ui_test.find("Stage").focus()
        await ui_test.find("Content").focus()

        # new stage
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        # create prims
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere")
        await self._select_prims(["/World/Sphere"])

        # drag file from content window
        property_widget = ui_test.find_first("Property//Frame/**/Button[*].identifier=='preview_drop_target'")
        self.assertIsNotNone(property_widget)

        mdl_path = self._get_mdl_path("multi_hair.mdl")

        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.drag_and_drop_tree_view(mdl_path, drag_target=property_widget.center)

        async with MaterialLibraryTestHelper() as material_test_helper:
            await material_test_helper.handle_create_material_dialog(mdl_path, "OmniHair_Green")

        # verify prims
        shader = omni.usd.get_shader_from_material(stage.GetPrimAtPath("/World/Looks/OmniHair_Green"), False)
        self.assertTrue(bool(shader), "/World/Looks/OmniHair_Green not found")
        asset = shader.GetSourceAsset("mdl")
        self.assertTrue(os.path.isabs(asset.path))

        # verify prims
        prim = self._get_prim_at_path("/World/Looks/OmniHair_Green")
        shader = self._get_shader_from_material(prim)
        self.assertTrue(bool(shader), "/World/Looks/OmniHair_Green not found")
        asset = shader.GetSourceAsset("mdl")
        self.assertTrue(os.path.isabs(asset.path))

    async def test_l1_drag_drop_path_drop_target_multi_relative(self):
        self._settings.set(self.DRAG_DROP_MATERIAL_PATH_SETTING, "relative")
        await ui_test.find("Stage").focus()
        await ui_test.find("Content").focus()

        # create prims
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere")
        await self._select_prims(["/World/Sphere"])

        # drag file from content window
        property_widget = ui_test.find_first("Property//Frame/**/Button[*].identifier=='preview_drop_target'")
        self.assertIsNotNone(property_widget)

        mdl_path = self._get_mdl_path("multi_hair.mdl")
        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.drag_and_drop_tree_view(mdl_path, drag_target=property_widget.center)

        async with MaterialLibraryTestHelper() as material_test_helper:
            await material_test_helper.handle_create_material_dialog(mdl_path, "OmniHair_Green")

        # verify prims
        prim = self._get_prim_at_path("/World/Looks/OmniHair_Green")
        shader = self._get_shader_from_material(prim)
        self.assertTrue(bool(shader), "/World/Looks/OmniHair_Green not found")
        asset = shader.GetSourceAsset("mdl")
        self.assertFalse(os.path.isabs(asset.path))
