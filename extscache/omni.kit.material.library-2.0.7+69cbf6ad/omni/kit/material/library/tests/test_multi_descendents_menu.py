## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

import os

import carb
import omni.kit.app
import omni.kit.test
import omni.ui as ui
import omni.usd
from omni.kit import ui_test
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from omni.kit.ui_test import Vec2
from omni.kit.viewport.utility import get_ui_position_for_prim
from pxr import UsdShade


class MultipleDescendentsMenuTest(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        self.__viewport_window = await arrange_windows()
        await open_stage(get_test_data_path(__name__, "usd/multi-material-object-cube-component.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_drag_drop_menu_material_viewport(self):
        def is_extension_loaded(extansion_name: str) -> bool:
            """
            Returns True if the extension with the given name is loaded.
            """

            def is_ext(id: str, extension_name: str) -> bool:
                id_name = id.split("-")[0]
                return id_name == extension_name

            app = omni.kit.app.get_app_interface()
            ext_manager = app.get_extension_manager()
            extensions = ext_manager.get_extensions()

            loaded = next((ext for ext in extensions if is_ext(ext["id"], extansion_name) and ext["enabled"]), None)

            return not not loaded

        # custom menu find function as menu uses custom class and "/" in menu names & kind_text
        def find_menu_item(query, menu_root, kind):
            import re

            for item in ui.Inspector.get_children(menu_root):
                if isinstance(item, ui.MenuItem) or isinstance(item, ui.Menu):
                    kind_text = item.kind_text if hasattr(item, "kind_text") else ""
                    if kind_text == kind:
                        name = re.sub(r"[^\x00-\x7F]+", " ", item.text).lstrip()
                        if query == name.replace("/", "_"):
                            return item


        stage = omni.usd.get_context().get_stage()

        ui_test_window = ui_test.find("Viewport")
        await ui_test_window.focus()

        # create material
        kit_folder = carb.tokens.get_tokens_interface().resolve("${kit}")
        omni_pbr_mtl = os.path.normpath(kit_folder + "/mdl/core/Base/OmniPBR.mdl")
        mtl_path = omni.usd.get_stage_next_free_path(stage, "/World/Looks/OmniPBR", False)
        omni.kit.commands.execute("CreateMdlMaterialPrim", mtl_url=omni_pbr_mtl, mtl_name="OmniPBR", mtl_path=mtl_path)

        await wait_stage_loading()
        await select_prims([mtl_path])
        await ui_test.human_delay(10)

        # get widget
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        mtl_widget = stage_widget.find("**/Label[*].text=='OmniPBR'")

        # get target prim
        multiple_descendents_prim = "/World/pCube1"
        drag_target, valid = get_ui_position_for_prim(self.__viewport_window, multiple_descendents_prim)
        drag_target = Vec2(drag_target[0], drag_target[1])
        for descendent in ["/World/pCube1/front1", "/World/pCube1/side1", "/World/pCube1/back", "/World/pCube1/side2", "/World/pCube1/top1", "/World/pCube1/bottom"]:
            # drag/drop OmniPBR to pCube1
            await mtl_widget.drag_and_drop(drag_target)
            await ui_test.human_delay(10)

            # select menu item
            await ui_test.select_context_menu(f"_World_pCube1/{descendent.replace('/', '_')}", offset=ui_test.Vec2(10, 10), find_fn=lambda q, m: find_menu_item(q, m, ""))
            await ui_test.human_delay(10)

            # verify binding changed
            prim = stage.GetPrimAtPath(descendent)
            bound_material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
            self.assertTrue(bound_material.GetPrim().IsValid() == True)
            self.assertTrue(bound_material.GetPrim().GetPrimPath().pathString == "/World/Looks/OmniPBR")

            # undo
            omni.kit.undo.undo()
            await ui_test.human_delay(10)

        # drag/drop OmniPBR to pCube1
        await mtl_widget.drag_and_drop(drag_target)
        await ui_test.human_delay(10)

        # select menu item
        await ui_test.select_context_menu("_World_pCube1", offset=ui_test.Vec2(10, 10), find_fn=lambda q, m: find_menu_item(q, m, "component"))

        # verify binding changed
        prim = stage.GetPrimAtPath("/World/pCube1")
        bound_material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
        self.assertTrue(bound_material.GetPrim().IsValid() == True)
        self.assertTrue(bound_material.GetPrim().GetPrimPath().pathString == "/World/Looks/OmniPBR")
