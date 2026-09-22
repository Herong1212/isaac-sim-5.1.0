## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import os
import carb
import omni.kit.app
import omni.usd
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from pxr import Tf, UsdShade
from omni.kit.test_suite.helpers import get_test_data_path, select_prims, wait_stage_loading, arrange_windows
from omni.kit.material.library.test_helper import MaterialLibraryTestHelper


class TestContextMenuAssignMaterial(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        import omni.kit.material.library

        await arrange_windows()

        # wait for material to be preloaded so create menu is complete & menus don't rebuild during tests
        await omni.kit.material.library.get_mdl_list_async()
        await ui_test.human_delay(50)

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_assign_material(self):
        # new stage
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        stage = usd_context.get_stage()

        # setup
        await ui_test.find("Stage").focus()

        # create root prim
        rootname = "/World"
        stage.SetDefaultPrim(stage.DefinePrim(rootname))

        # create Looks folder
        omni.kit.commands.execute("CreatePrim", prim_path="{}/Looks".format(rootname), prim_type="Scope", select_new_prim=True)

        # create material
        kit_folder = carb.tokens.get_tokens_interface().resolve("${kit}")
        omni_pbr_mtl = os.path.normpath(kit_folder + "/mdl/core/Base/OmniPBR.mdl")
        mtl_path = omni.usd.get_stage_next_free_path(stage, "{}/Looks/{}".format(rootname, omni.usd.make_valid_identifier("OmniPBR")), False)
        omni.kit.commands.execute("CreateMdlMaterialPrim", mtl_url=omni_pbr_mtl, mtl_name="OmniPBR", mtl_path=mtl_path)

        # create sphere
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere", select_new_prim=True)

        # select prim
        await select_prims(["/World/Sphere"])

        # expand stage window...
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True").widget.set_expanded(None, True, True)

        # get prim
        prim = stage.GetPrimAtPath("/World/Sphere")

        # click on context menu item & assign ma
        viewport = ui_test.find("Viewport")
        await viewport.focus()
        await viewport.right_click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Assign Material")

        # assign material
        await ui_test.human_delay()
        async with MaterialLibraryTestHelper() as material_test_helper:
            await material_test_helper.handle_assign_material_dialog(1, 0)

        bound_material, relationship = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
        strength = UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(relationship)
        self.assertEqual(bound_material.GetPrim().GetPrimPath().pathString, mtl_path)
        self.assertEqual(strength, UsdShade.Tokens.weakerThanDescendants)

        # click on context menu item
        viewport = ui_test.find("Viewport")
        await viewport.focus()
        await viewport.right_click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Assign Material")

        # assign material with different strength
        await ui_test.human_delay()
        async with MaterialLibraryTestHelper() as material_test_helper:
            await material_test_helper.handle_assign_material_dialog(1, 1)

        bound_material, relationship = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
        strength = UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(relationship)
        self.assertEqual(bound_material.GetPrim().GetPrimPath().pathString, mtl_path)
        self.assertEqual(strength, UsdShade.Tokens.strongerThanDescendants)
