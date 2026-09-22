## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
# pylint: disable=missing-function-docstring, missing-class-docstring
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


class PrimScrollPosition(AsyncTestCase):

    # Before running each test
    async def setUp(self):
        omni.kit.window.property.managed_frame.reset_collapsed_state()
        await arrange_windows()
        await open_stage(get_test_data_path(__name__, "usd/sphere.usda"))

    # After running each test
    async def tearDown(self):
        omni.kit.window.property.managed_frame.reset_collapsed_state()
        await select_prims([])
        await wait_stage_loading()

    async def test_scroll_lock(self):
        import omni.kit.window.property as p

        await ui_test.find("Property").focus()
        w = p.get_window()

        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Raw USD Properties", False)

        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere")
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere")
        omni.kit.commands.execute("CreatePrim", prim_type="DomeLight")

        await select_prims(["/World/Sphere"])
        w.properties_frame.scroll_y = 999
        await ui_test.human_delay(50)

        await select_prims(["/World/Sphere_01"])
        await ui_test.human_delay(50)
        # verify scrollpos is > 0
        self.assertGreater(w.properties_frame.scroll_y, 10)

        await select_prims(["/World/Sphere_02"])
        await ui_test.human_delay(50)
        # verify scrollpos is > 0
        self.assertGreater(w.properties_frame.scroll_y, 10)

        await select_prims(["/World/DomeLight"])
        await ui_test.human_delay(50)
        # verify scrollpos is == 0
        self.assertAlmostEqual(w.properties_frame.scroll_y, 0)

    async def test_scroll_lock_layers(self):
        import omni.kit.window.property as p
        from omni.kit.widget.layers.layer_item import LayerItem

        await ui_test.find("Property").focus()
        w = p.get_window()

        await ui_test.find("Layer").focus()
        # select prim to crearte 'LayerItem in payload
        await ui_test.find("Layer//Frame/**/TreeView[*]").find(
            "**/Label[*].text=='Root Layer (Authoring Layer)'"
        ).click()
        await ui_test.human_delay(50)

        await ui_test.find("Property").focus()
        # select prim now 'LayerItem is a payload
        self.assertTrue(isinstance(w._payload(), LayerItem))

        # verify selecting prim doesn't throw error
        await select_prims(["/World/Sphere"])
        await ui_test.human_delay(50)
