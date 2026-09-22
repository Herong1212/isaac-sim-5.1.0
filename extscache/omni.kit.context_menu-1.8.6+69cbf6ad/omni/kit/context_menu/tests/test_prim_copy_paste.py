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
import omni.kit.app
import omni.usd
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from pxr import Sdf, UsdShade
from omni.kit.viewport.utility import get_ui_position_for_prim
from omni.kit.test_suite.helpers import (
    open_stage,
    get_test_data_path,
    select_prims,
    get_prims,
    wait_stage_loading,
    arrange_windows
    )


class PrimMeshCopyPaste(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        self._viewport_window = await arrange_windows("Stage", 768)
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()
        stage.SetDefaultPrim(stage.DefinePrim("/World"))
        await wait_stage_loading()
        # expand treeview
        stage_window = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        stage_window.widget.set_expanded(None, True, True)

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()
        await omni.usd.get_context().new_stage_async()


    async def test_prim_copy_paste(self):
        async def find_menu_item(menu_path: str):
            from omni import ui
            from omni.kit.ui_test.menu import _find_menu_item, _find_context_menu_item
            return await self.retry_until_success(lambda: _find_context_menu_item(menu_path, ui.Menu.get_current(), _find_menu_item))

        await wait_stage_loading()

        # setup
        stage = omni.usd.get_context().get_stage()
        stage_window = ui_test.find("Stage")
        safe_target = stage_window.position + ui_test.Vec2(stage_window.size.x / 2, stage_window.size.y - 32)
        tree_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_window.focus()

        # get context menu & create scope
        await stage_window.right_click(pos=safe_target)
        menu_dict = await ui_test.get_context_menu()
        await ui_test.select_context_menu("Create/Scope", offset=ui_test.Vec2(10, 10))

        base_prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]

        # create mesh, no children
        await select_prims([])
        await stage_window.right_click(pos=safe_target)
        await ui_test.select_context_menu("Create/Mesh/Sphere", offset=ui_test.Vec2(10, 10))

        # wait for VP to be ready
        await wait_stage_loading()

        prim_pos, valid = get_ui_position_for_prim(self._viewport_window, "/World/Sphere")
        self.assertTrue(valid)

        viewport = ui_test.find("Viewport")
        await viewport.focus()

        # open VP context menu & copy prim
        await viewport.right_click(pos=ui_test.Vec2(prim_pos[0], prim_pos[1] + 30))
        await ui_test.select_context_menu("Copy", offset=ui_test.Vec2(10, 10))

        # copy VP context menu & paste here
        await viewport.right_click(pos=ui_test.Vec2(prim_pos[0] + 50, prim_pos[1] + 50))
        await ui_test.select_context_menu("Paste Here", offset=ui_test.Vec2(10, 10))

        # verify
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath("/World/Sphere_01")
        self.assertTrue(prim.IsValid())

        # clear VP context menu clipboard
        await viewport.right_click(pos=ui_test.Vec2(prim_pos[0] + 50, prim_pos[1] + 50))
        item = await find_menu_item("Clear Clipboard")
        item.call_triggered_fn()
        omni.kit.context_menu.close_menu()
