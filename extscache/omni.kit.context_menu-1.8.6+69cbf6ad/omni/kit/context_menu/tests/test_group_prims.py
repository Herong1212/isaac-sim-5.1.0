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
import omni.kit.undo
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from pxr import Tf, UsdShade
from omni.kit.test_suite.helpers import get_test_data_path, select_prims,  get_prims, wait_stage_loading, arrange_windows
from omni.kit.material.library.test_helper import MaterialLibraryTestHelper


class TestContextMenuGroupPrims(AsyncTestCase):
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

    async def test_group_prims(self):
        # new stage
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        stage = usd_context.get_stage()

        # setup
        stage = omni.usd.get_context().get_stage()
        stage_window = ui_test.find("Stage")
        safe_target = stage_window.position + ui_test.Vec2(stage_window.size.x / 2, stage_window.size.y - 32)
        tree_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_window.focus()

        # create root prim
        rootname = "/World"
        stage.SetDefaultPrim(stage.DefinePrim(rootname))

        ## create prim
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere")
        await ui_test.human_delay()

        # verify prims were created
        prim_list = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertTrue(prim_list == ['/World', '/World/Sphere'])

        # group sphere & world
        await select_prims(['/World', '/World/Sphere'])

        # get context menu & create scope
        await stage_window.right_click(pos=safe_target)
        menu_dict = await ui_test.get_context_menu()
        await ui_test.human_delay()
        await ui_test.select_context_menu(f"Group Selected", offset=ui_test.Vec2(10, 10))

        # verify prims were not grouped
        prim_list = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertTrue(prim_list == ['/World', '/World/Sphere'])

        # select sphere
        await select_prims(["/World/Sphere"])

        # get context menu & create scope
        await stage_window.right_click(pos=safe_target)
        menu_dict = await ui_test.get_context_menu()
        await ui_test.human_delay()
        await ui_test.select_context_menu(f"Group Selected", offset=ui_test.Vec2(10, 10))

        # verify prims were grouped
        prim_list = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertTrue(prim_list == ['/World', '/World/Group', '/World/Group/Sphere'])

        # ungroup the prims
        await select_prims(['/World/Group'])

        # get context menu & create scope
        await stage_window.right_click(pos=safe_target)
        menu_dict = await ui_test.get_context_menu()
        await ui_test.human_delay()
        await ui_test.select_context_menu(f"Ungroup Selected", offset=ui_test.Vec2(10, 10))

        # verify prims were ungrouped
        prim_list = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertTrue(prim_list == ['/World', '/World/Sphere'])
