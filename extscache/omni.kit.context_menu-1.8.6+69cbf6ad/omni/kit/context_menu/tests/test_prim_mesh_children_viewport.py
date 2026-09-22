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


class CreatePrimMeshChildrenViewport(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows("Stage")
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()
        stage.SetDefaultPrim(stage.DefinePrim("/World"))
        await wait_stage_loading()

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_create_prim_nochildren_mesh(self):
        await wait_stage_loading()

        # setup
        stage = omni.usd.get_context().get_stage()
        viewport_window = ui_test.find("Viewport")
        await viewport_window.focus()

        base_prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]

        # create light to be parent
        await viewport_window.right_click()
        menu_dict = await ui_test.get_context_menu()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Create/Light/Distant Light", offset=ui_test.Vec2(10, 10))

        # select light
        await ui_test.human_delay(10)
        await viewport_window.click()
        await ui_test.human_delay(10)

        # create meshes
        for mesh in menu_dict['Create']['Mesh']['_']:
            await viewport_window.right_click()
            await ui_test.human_delay()
            await ui_test.select_context_menu(f"Create/Mesh/{mesh}", offset=ui_test.Vec2(10, 10))
            await ui_test.human_delay(10)

        # verify
        prims = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        final_prims = [x for x in prims if x not in base_prims]
        self.assertEqual(final_prims, ['/World/DistantLight', '/World/Cone', '/World/Cube', '/World/Cylinder', '/World/Disk', '/World/Plane', '/World/Sphere', '/World/Torus'])
