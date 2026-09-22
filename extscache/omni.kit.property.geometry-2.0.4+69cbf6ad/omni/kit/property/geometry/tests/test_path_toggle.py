## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
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


class PropertyPathAddMenu(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows("Stage", 64)

        omni.kit.window.property.managed_frame.reset_collapsed_state()
        omni.kit.window.property.managed_frame.set_collapsed_state("Geometry/Refinement", True)
        omni.kit.window.property.managed_frame.set_collapsed_state("Geometry/Extra Properties", True)
        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Kind", True)
        omni.kit.window.property.managed_frame.set_collapsed_state("Property/Raw USD Properties", True)

        await open_stage(get_test_data_path(__name__, "geometry_test.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()
        omni.kit.window.property.managed_frame.reset_collapsed_state()

    async def test_property_path_rendering(self):
        await ui_test.find("Property").focus()
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        # select cube
        await select_prims(["/World/Cube"])
        await ui_test.human_delay()

        # verify not set
        prim = stage.GetPrimAtPath("/World/Cube")
        attr = prim.GetAttribute("primvars:wireframe")
        self.assertFalse(attr.IsValid())

        # click "Add"
        add_widget = [w for w in ui_test.find_all("Property//Frame/**/Button[*]") if w.widget.text.endswith("Add")][0]
        await add_widget.click()

        # select wireframe
        await ui_test.select_context_menu("Rendering/Set Wireframe Mode")

        # verify set
        self.assertTrue(attr.IsValid())
        self.assertTrue(attr.Get())

        # click "Add"
        add_widget = [w for w in ui_test.find_all("Property//Frame/**/Button[*]") if w.widget.text.endswith("Add")][0]
        await add_widget.click()

        # select wireframe
        await ui_test.select_context_menu("Rendering/Clear Wireframe Mode")

        # verify cleared
        self.assertTrue(attr.IsValid())
        self.assertFalse(attr.Get())

        # undo
        omni.kit.undo.undo()
        omni.kit.undo.undo()

        # verify not set
        self.assertFalse(attr.IsValid())

    async def test_curve_rendering(self):
        await ui_test.find("Property").focus()

        # select curve
        await select_prims(["/World/Curve"])
        await ui_test.human_delay()

    async def test_points_rendering(self):
        await ui_test.find("Property").focus()

        # select points
        await select_prims(["/World/Points"])
        await ui_test.human_delay()

    async def test_property_mesh_bounds(self):
        await ui_test.find("Property").focus()

        # select cube
        await select_prims(["/World/Cube"])
        await ui_test.human_delay()

        # find size drag widget
        frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Geometry'")
        frame = frame.find("/**/CollapsableFrame[*].title=='Mesh'")
        for w in frame.find_all("/**/FloatDrag[*]"):
            w.widget.model.set_value(50)
            await ui_test.human_delay(10)

    async def test_instanceable(self):
        await ui_test.find("Property").focus()
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        # select cube
        await select_prims(["/World/Cube"])
        await ui_test.human_delay()

        # verify not set
        prim = stage.GetPrimAtPath("/World/Cube")
        self.assertFalse(prim.IsInstanceable())

        # click "Add"
        add_widget = [w for w in ui_test.find_all("Property//Frame/**/Button[*]") if w.widget.text.endswith("Add")][0]
        await add_widget.click()

        # select instanceable
        await ui_test.select_context_menu("Instanceable")

        # verify set
        self.assertTrue(prim.IsInstanceable())

        # undo
        omni.kit.undo.undo()

        # verify not set
        self.assertFalse(prim.IsInstanceable())
