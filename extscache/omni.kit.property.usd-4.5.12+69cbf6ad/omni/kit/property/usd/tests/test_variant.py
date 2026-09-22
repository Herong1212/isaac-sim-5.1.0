## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from omni.kit import ui_test
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from pxr import Gf, Vt


class PrimVariantColorProperty(AsyncTestCase):

    # Before running each test
    async def setUp(self):
        await arrange_windows()
        await open_stage(get_test_data_path(__name__, "usd_variants/variant.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_shader_material_subid_property(self):
        import omni.kit.commands

        await ui_test.find("Property").focus()

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        # select variant prim
        await select_prims(["/World"])
        await ui_test.human_delay()

        # verify displayColor is red
        prim = stage.GetPrimAtPath("/World/Sphere")
        attr = prim.GetAttribute("primvars:displayColor")
        self.assertEqual(attr.Get(), Vt.Vec3fArray(1, (Gf.Vec3f(1.0, 0.0, 0.0))))

        # change variant to blue
        variant_widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Variants'")
        combo_widget = variant_widget.find("Property//Frame/**/ComboBox[*]")
        combo_widget.model.set_value("blue")
        await ui_test.human_delay(100)
        # verify displayColor is blue
        self.assertEqual(attr.Get(), Vt.Vec3fArray(1, (Gf.Vec3f(0.0, 0.0, 1.0))))

        # NOTE: previous set_value will have refreshed property widget, so old values are not valid

        # change variant to red
        variant_widget = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Variants'")
        combo_widget = variant_widget.find("Property//Frame/**/ComboBox[*]")
        combo_widget.model.set_value("red")
        await ui_test.human_delay(100)
        # verify displayColor is red
        self.assertEqual(attr.Get(), Vt.Vec3fArray(1, (Gf.Vec3f(1.0, 0.0, 0.0))))
