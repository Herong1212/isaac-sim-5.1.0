## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-overridden-method
import omni.kit.app
import omni.kit.test
import omni.usd
from omni.kit import ui_test
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import (
    arrange_windows,
    delete_prim_path_children,
    get_random_material_list,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
from pxr import UsdShade


class DragDropMaterialPropertyComboBox(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows("Stage", 64)
        await open_stage(get_test_data_path(__name__, "usd/bound_shapes.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    def _verify_material(self, stage, mtl_name, to_select):
        # verify material created
        prim_paths = [p.GetPrimPath().pathString for p in stage.Traverse()]
        self.assertTrue(f"/World/Looks/{mtl_name}" in prim_paths)
        self.assertTrue(f"/World/Looks/{mtl_name}/Shader" in prim_paths)

        # verify bound material
        if to_select:
            for prim_path in to_select:
                prim = stage.GetPrimAtPath(prim_path)
                bound_material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
                self.assertTrue(bound_material.GetPrim().IsValid())
                self.assertTrue(bound_material.GetPrim().GetPrimPath().pathString == f"/World/Looks/{mtl_name}")

    async def test_drag_drop_material_property_combobox(self, retry_count=0):
        from omni.kit.material.library.test_helper import MaterialLibraryTestHelper

        await ui_test.find("Content").focus()
        await ui_test.find("Stage").focus()

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        to_select = "/World/Cylinder"

        # select prim
        await select_prims([to_select])

        # wait for material to load & UI to refresh
        await wait_stage_loading(wait_frames=10)

        # drag to bottom of stage window
        # NOTE: Material binding is done on selected prim
        mdl_list = await get_random_material_list()

        property_widget = ui_test.find("Property//Frame/**/StringField[*].identifier=='combo_drop_target'")
        drag_target = property_widget.center

        async with ContentBrowserTestHelper() as content_browser_helper:
            for mtl_name, mdl_path, _ in mdl_list:
                await delete_prim_path_children("/World/Looks")

                await content_browser_helper.drag_and_drop_tree_view(mdl_path, drag_target=drag_target)

                # use create material dialog
                async with MaterialLibraryTestHelper() as material_test_helper:
                    try:
                        await material_test_helper.handle_create_material_dialog(mdl_path, mtl_name)
                    except MaterialLibraryTestHelper.DialogError as de:
                        if retry_count < 5:
                            print("dialog error... retrying...")
                            return await self.test_drag_drop_material_property_combobox(retry_count + 1)
                        raise de

                # wait for material to load & UI to refresh
                await wait_stage_loading()

                # verify
                self._verify_material(stage, mtl_name, [to_select])

        return True
