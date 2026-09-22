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


class CreatePrimShapeChildren(AsyncTestCase):
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

    async def test_create_prim_children_shape(self):
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

        # create shape, no children
        await select_prims([])
        for shape in menu_dict['Create']['Shape']['_']:
            await stage_window.right_click(pos=safe_target)
            await ui_test.human_delay()
            await ui_test.select_context_menu(f"Create/Shape/{shape}", offset=ui_test.Vec2(10, 10))
            await ui_test.human_delay(10)

        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        created_prims = [x for x in prims if x not in base_prims]

        # create shape with as child (should fail)
        await tree_widget.find(f"**/StringField[*].model.path=='/World/Red_Herring'").click()
        for prim_path in created_prims:
            widget = tree_widget.find(f"**/StringField[*].model.path=='{prim_path}'")
            widget.widget.scroll_here_y(0.5)
            await ui_test.human_delay(10)
            widget = tree_widget.find(f"**/StringField[*].model.path=='{prim_path}'")
            menu_pos = widget.position + ui_test.Vec2(10, 10)
            for shape in menu_dict['Create']['Shape']['_']:
                await stage_window.right_click(menu_pos)
                await ui_test.select_context_menu(f"Create/Shape/{shape}", offset=ui_test.Vec2(10, 10))
                await ui_test.human_delay(10)

        # verify
        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        final_prims = [x for x in prims if x not in base_prims]
        self.assertEqual(final_prims, ['/World/Capsule', '/World/Cone', '/World/Cube', '/World/Cylinder', '/World/Sphere', '/World/Capsule_01', '/World/Cone_01', '/World/Cube_01', '/World/Cylinder_01', '/World/Sphere_01', '/World/Capsule_02', '/World/Cone_02', '/World/Cube_02', '/World/Cylinder_02', '/World/Sphere_02', '/World/Capsule_03', '/World/Cone_03', '/World/Cube_03', '/World/Cylinder_03', '/World/Sphere_03', '/World/Capsule_04', '/World/Cone_04', '/World/Cube_04', '/World/Cylinder_04', '/World/Sphere_04', '/World/Capsule_05', '/World/Cone_05', '/World/Cube_05', '/World/Cylinder_05', '/World/Sphere_05'])


    async def test_create_prim_children_shape_scope_empty(self):
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

        # create shape, no children
        for shape in menu_dict['Create']['Shape']['_']:
            await select_prims(["/World/Scope"])
            await stage_window.right_click(pos=safe_target)
            await ui_test.human_delay()
            await ui_test.select_context_menu(f"Create/Shape/{shape}", offset=ui_test.Vec2(10, 10))
            await ui_test.human_delay(10)

        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        created_prims = [x for x in prims if x not in base_prims]

        # verify
        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(prims, ['/World', '/World/Red_Herring', '/World/Scope', '/World/Capsule', '/World/Cone', '/World/Cube', '/World/Cylinder', '/World/Sphere'])


    async def test_create_prim_children_shape_xform_empty(self):
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
        await ui_test.select_context_menu(f"Create/Xform", offset=ui_test.Vec2(10, 10))

        base_prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]

        # create shape, no children
        for shape in menu_dict['Create']['Shape']['_']:
            await select_prims(["/World/Xform"])
            await stage_window.right_click(pos=safe_target)
            await ui_test.human_delay()
            await ui_test.select_context_menu(f"Create/Shape/{shape}", offset=ui_test.Vec2(10, 10))
            await ui_test.human_delay(10)

        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        created_prims = [x for x in prims if x not in base_prims]

        # verify
        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(prims, ['/World', '/World/Red_Herring', '/World/Xform', '/World/Capsule', '/World/Cone', '/World/Cube', '/World/Cylinder', '/World/Sphere'])


    async def test_create_prim_children_shape_scope_hover(self):
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

        # create shape, no children
        for shape in menu_dict['Create']['Shape']['_']:
            await select_prims(["/World/Scope"])
            #await stage_window.right_click(pos=safe_target)
            stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
            await stage_widget.find(f"**/StringField[*].model.path=='/World/Scope'").right_click()
            await ui_test.human_delay()
            await ui_test.select_context_menu(f"Create/Shape/{shape}", offset=ui_test.Vec2(10, 10))
            await ui_test.human_delay(10)

        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        created_prims = [x for x in prims if x not in base_prims]

        # verify
        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(prims, ['/World', '/World/Red_Herring', '/World/Scope', '/World/Scope/Capsule', '/World/Scope/Cone', '/World/Scope/Cube', '/World/Scope/Cylinder', '/World/Scope/Sphere'])


    async def test_create_prim_children_shape_xform_hover(self):
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
        await ui_test.select_context_menu(f"Create/Xform", offset=ui_test.Vec2(10, 10))

        base_prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]

        # create shape, no children
        for shape in menu_dict['Create']['Shape']['_']:
            await select_prims(["/World/Xform"])
            #await stage_window.right_click(pos=safe_target)
            stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
            await stage_widget.find(f"**/StringField[*].model.path=='/World/Xform'").right_click()
            await ui_test.human_delay()
            await ui_test.select_context_menu(f"Create/Shape/{shape}", offset=ui_test.Vec2(10, 10))
            await ui_test.human_delay(10)

        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        created_prims = [x for x in prims if x not in base_prims]

        # verify
        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(prims, ['/World', '/World/Red_Herring', '/World/Xform', '/World/Xform/Capsule', '/World/Xform/Cone', '/World/Xform/Cube', '/World/Xform/Cylinder', '/World/Xform/Sphere'])
