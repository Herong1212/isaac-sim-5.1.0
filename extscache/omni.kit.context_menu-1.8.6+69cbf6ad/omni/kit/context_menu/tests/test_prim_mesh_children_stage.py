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
from omni.kit.test_suite.helpers import (
    open_stage,
    get_test_data_path,
    select_prims,
    get_prims,
    wait_stage_loading,
    arrange_windows
    )


class CreatePrimMeshChildrenStage(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows("Stage", 768)
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()
        stage.SetDefaultPrim(stage.DefinePrim("/World"))
        stage.DefinePrim("/World/Red_Herring", "Scope")
        await wait_stage_loading()
        # expand treeview
        stage_window = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        stage_window.widget.set_expanded(None, True, True)
        await ui_test.human_delay(50)

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    ###############################################################
    #### this test fails as scroll_here_y doesn't work anymore ####
    ###############################################################
    async def __test_create_prim_children_mesh(self):
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
        await ui_test.human_delay()
        await ui_test.select_context_menu(f"Create/Scope", offset=ui_test.Vec2(10, 10))

        base_prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]

        # create mesh, no children
        await select_prims([])
        for mesh in menu_dict['Create']['Mesh']['_']:
            await stage_window.right_click(pos=safe_target)
            await ui_test.human_delay()
            await ui_test.select_context_menu(f"Create/Mesh/{mesh}", offset=ui_test.Vec2(10, 10))
            await ui_test.human_delay(10)

        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        created_prims = [x for x in prims if x not in base_prims]

        # create mesh with as child (should fail)
        await tree_widget.find(f"**/StringField[*].model.path=='/World/Red_Herring'").click()
        for prim_path in created_prims:
            widget = tree_widget.find(f"**/StringField[*].model.path=='{prim_path}'")
            widget.widget.scroll_here_y(0.5)
            await ui_test.human_delay(10)
            widget = tree_widget.find(f"**/StringField[*].model.path=='{prim_path}'")
            menu_pos = widget.position + ui_test.Vec2(10, 10)
            for mesh in menu_dict['Create']['Mesh']['_']:
                await stage_window.right_click(menu_pos)
                await ui_test.select_context_menu(f"Create/Mesh/{mesh}", offset=ui_test.Vec2(10, 10))
                await ui_test.human_delay(10)

        # verify
        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        final_prims = [x for x in prims if x not in base_prims]
        self.assertEqual(final_prims, ['/World/Cone', '/World/Cube', '/World/Cylinder', '/World/Disk', '/World/Plane', '/World/Sphere', '/World/Torus', '/World/Cone_01', '/World/Cube_01', '/World/Cylinder_01', '/World/Disk_01', '/World/Plane_01', '/World/Sphere_01', '/World/Torus_01', '/World/Cone_02', '/World/Cube_02', '/World/Cylinder_02', '/World/Disk_02', '/World/Plane_02', '/World/Sphere_02', '/World/Torus_02', '/World/Cone_03', '/World/Cube_03', '/World/Cylinder_03', '/World/Disk_03', '/World/Plane_03', '/World/Sphere_03', '/World/Torus_03', '/World/Cone_04', '/World/Cube_04', '/World/Cylinder_04', '/World/Disk_04', '/World/Plane_04', '/World/Sphere_04', '/World/Torus_04', '/World/Cone_05', '/World/Cube_05', '/World/Cylinder_05', '/World/Disk_05', '/World/Plane_05', '/World/Sphere_05', '/World/Torus_05', '/World/Cone_06', '/World/Cube_06', '/World/Cylinder_06', '/World/Disk_06', '/World/Plane_06', '/World/Sphere_06', '/World/Torus_06', '/World/Cone_07', '/World/Cube_07', '/World/Cylinder_07', '/World/Disk_07', '/World/Plane_07', '/World/Sphere_07', '/World/Torus_07'])

    async def test_create_prim_children_mesh_scope(self):
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
        await ui_test.human_delay()
        await ui_test.select_context_menu(f"Create/Scope", offset=ui_test.Vec2(10, 10))

        base_prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]

        # create mesh, no children
        for mesh in menu_dict['Create']['Mesh']['_']:
            await select_prims(["/World/Scope"])
            await stage_window.right_click(pos=safe_target)
            await ui_test.human_delay()
            await ui_test.select_context_menu(f"Create/Mesh/{mesh}", offset=ui_test.Vec2(10, 10))
            await ui_test.human_delay(10)

        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        created_prims = [x for x in prims if x not in base_prims]

        # verify
        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(prims, ['/World', '/World/Red_Herring', '/World/Scope', '/World/Cone', '/World/Cube', '/World/Cylinder', '/World/Disk', '/World/Plane', '/World/Sphere', '/World/Torus'])

    async def test_create_prim_children_default_prim(self):
        await wait_stage_loading()

        # setup
        stage = omni.usd.get_context().get_stage()
        stage_window = ui_test.find("Stage")
        tree_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_window.focus()

        # create Environment
        omni.kit.commands.execute(
            "CreatePrim",
            prim_path="/Environment",
            prim_type="Xform",
            select_new_prim=False,
            create_default_xform=True,
        )
        await ui_test.human_delay(10)

        # get context menu & create scope
        menu_pos = tree_widget.find(f"**/StringField[*].model.path=='/Environment'").position + ui_test.Vec2(10, 10)
        await stage_window.right_click(pos=menu_pos)
        menu_dict = await ui_test.get_context_menu()
        await ui_test.human_delay()
        await ui_test.select_context_menu(f"Create/Scope", offset=ui_test.Vec2(10, 10))
        await ui_test.human_delay(10)

        base_prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]

        # create mesh, no children
        for mesh in menu_dict['Create']['Mesh']['_']:
            await select_prims(["/World/Scope"])
            await ui_test.human_delay(10)
            menu_pos = tree_widget.find(f"**/StringField[*].model.path=='/Environment'").position + ui_test.Vec2(10, 10)
            await stage_window.right_click(pos=menu_pos)
            await ui_test.human_delay()
            await ui_test.select_context_menu(f"Create/Mesh/{mesh}", offset=ui_test.Vec2(10, 10))
            await ui_test.human_delay(10)

        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        created_prims = [x for x in prims if x not in base_prims]

        # verify
        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(prims, ['/World', '/World/Red_Herring', '/Environment', '/Environment/Scope', '/Environment/Cone', '/Environment/Cube', '/Environment/Cylinder', '/Environment/Disk', '/Environment/Plane', '/Environment/Sphere', '/Environment/Torus'])
