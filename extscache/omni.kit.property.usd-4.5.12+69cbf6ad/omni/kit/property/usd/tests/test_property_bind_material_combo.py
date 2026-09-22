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
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from pxr import UsdShade


class PropertyBindMaterialCombo(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows("Stage", 64)
        await open_stage(get_test_data_path(__name__, "usd/bound_shapes.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_property_bind_material_combo(self):
        await ui_test.find("Content").focus()

        stage_window = ui_test.find("Stage")
        await stage_window.focus()

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        to_select = ["/World/Cube", "/World/Cone", "/World/Sphere", "/World/Cylinder"]

        await wait_stage_loading()

        await select_prims(to_select)
        await ui_test.human_delay()

        bound_materials = ["None", "/World/Looks/OmniGlass", "/World/Looks/OmniPBR", "/World/Looks/OmniSurface_Plastic"]
        for index in range(0, 4):
            # show combobox
            # NOTE: delay of 4 as that opens a new popup window
            topmost_button = sorted(
                ui_test.find_all("Property//Frame/**/Button[*].identifier=='combo_open_button'"),
                key=lambda f: f.position.y,
            )[0]
            await topmost_button.click(human_delay_speed=4)

            # activate menu item
            await ui_test.find(
                f"MaterialPropertyPopupWindow//Frame/**/Label[*].text=='{bound_materials[index]}'"
            ).click()

            # wait for material to load & UI to refresh
            await wait_stage_loading()

            # verify
            for prim_path in to_select:
                prim = stage.GetPrimAtPath(prim_path)
                bound_material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
                if bound_materials[index] != "None":
                    self.assertTrue(bound_material.GetPrim().IsValid())
                    self.assertTrue(bound_material.GetPrim().GetPrimPath().pathString == bound_materials[index])
                else:
                    self.assertFalse(bound_material.GetPrim().IsValid())
