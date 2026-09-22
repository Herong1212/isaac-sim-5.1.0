## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-overridden-method
from omni.kit import ui_test
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)


class PrimMixedVariantProperty(AsyncTestCase):

    # Before running each test
    async def setUp(self):
        await arrange_windows()
        await open_stage(get_test_data_path(__name__, "usd_variants/ThreeDollyVariantStage.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_mixed_variant_property(self):
        await ui_test.find("Property").focus()

        # select single variant prim
        await select_prims(["/World/Dolly_Blueprint_ALL_VariantsPLB_viz_dual"])
        await ui_test.human_delay()

        # verify mixed is not shown
        widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_palettevariant'")
        self.assertEqual(widget.widget.enabled, True)
        self.assertEqual(widget.widget.visible, False)
        widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_boxvariant'")
        self.assertEqual(widget.widget.enabled, True)
        self.assertEqual(widget.widget.visible, False)

        # select two variant prims
        await select_prims(
            ["/World/Dolly_Blueprint_ALL_VariantsPLB_viz_dual", "/World/Dolly_Blueprint_ALL_VariantsPLB_viz_dual_01"]
        )
        await ui_test.human_delay()

        # verify mixed is shown
        widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_palettevariant'")
        self.assertEqual(widget.widget.enabled, True)
        self.assertEqual(widget.widget.visible, False)
        widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_boxvariant'")
        self.assertEqual(widget.widget.enabled, True)
        self.assertEqual(widget.widget.visible, True)

        # select two variant prims
        await select_prims(
            ["/World/Dolly_Blueprint_ALL_VariantsPLB_viz_dual_01", "/World/Dolly_Blueprint_ALL_VariantsPLB_viz_dual_02"]
        )
        await ui_test.human_delay()

        # verify mixed is shown
        widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_palettevariant'")
        self.assertEqual(widget.widget.enabled, True)
        self.assertEqual(widget.widget.visible, True)
        widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_boxvariant'")
        self.assertEqual(widget.widget.enabled, True)
        self.assertEqual(widget.widget.visible, False)

        # select all threee variant prims
        await select_prims(
            [
                "/World/Dolly_Blueprint_ALL_VariantsPLB_viz_dual",
                "/World/Dolly_Blueprint_ALL_VariantsPLB_viz_dual_01",
                "/World/Dolly_Blueprint_ALL_VariantsPLB_viz_dual_02",
            ]
        )
        await ui_test.human_delay()

        # verify mixed is shown
        widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_palettevariant'")
        self.assertEqual(widget.widget.enabled, True)
        self.assertEqual(widget.widget.visible, True)
        widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_boxvariant'")
        self.assertEqual(widget.widget.enabled, True)
        self.assertEqual(widget.widget.visible, True)

    async def test_mixed_variant_property_set_value(self):
        import omni.kit.commands

        await ui_test.find("Property").focus()

        # select all threee variant prims
        await select_prims(
            [
                "/World/Dolly_Blueprint_ALL_VariantsPLB_viz_dual",
                "/World/Dolly_Blueprint_ALL_VariantsPLB_viz_dual_01",
                "/World/Dolly_Blueprint_ALL_VariantsPLB_viz_dual_02",
            ]
        )

        # verify mixed is shown
        widget = ui_test.find("Property//Frame/**/*.identifier=='combo_variant_boxvariant'")
        items = [
            item.model.get_value_as_string()
            for item in widget.model.get_item_children(None)
            if item.model.get_value_as_string() != ""
        ]
        for item in items:
            # verify mixed is shown
            widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_boxvariant'")
            self.assertEqual(widget.widget.enabled, True)
            self.assertEqual(widget.widget.visible, True)

            widget = ui_test.find("Property//Frame/**/*.identifier=='combo_variant_boxvariant'")
            widget.model.set_value(item)
            await ui_test.human_delay()

            # verify mixed is not shown
            widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_boxvariant'")
            self.assertEqual(widget.widget.enabled, True)
            self.assertEqual(widget.widget.visible, False)

            # verify mixed is shown
            omni.kit.undo.undo()
            await ui_test.human_delay()
            widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_boxvariant'")
            self.assertEqual(widget.widget.enabled, True)
            self.assertEqual(widget.widget.visible, True)

            # verify mixed is not shown
            omni.kit.undo.redo()
            await ui_test.human_delay()
            widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_boxvariant'")
            self.assertEqual(widget.widget.enabled, True)
            self.assertEqual(widget.widget.visible, False)

            # verify mixed is shown
            omni.kit.undo.undo()
            await ui_test.human_delay()
            widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_boxvariant'")
            self.assertEqual(widget.widget.enabled, True)
            self.assertEqual(widget.widget.visible, True)

        # verify mixed is shown
        widget = ui_test.find("Property//Frame/**/*.identifier=='combo_variant_palettevariant'")
        items = [
            item.model.get_value_as_string()
            for item in widget.model.get_item_children(None)
            if item.model.get_value_as_string() != ""
        ]
        for item in items:
            # verify mixed is shown
            widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_palettevariant'")
            self.assertEqual(widget.widget.enabled, True)
            self.assertEqual(widget.widget.visible, True)

            widget = ui_test.find("Property//Frame/**/*.identifier=='combo_variant_palettevariant'")
            widget.model.set_value(item)
            await ui_test.human_delay()

            # verify mixed is not shown
            widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_palettevariant'")
            self.assertEqual(widget.widget.enabled, True)
            self.assertEqual(widget.widget.visible, False)

            # verify mixed is shown
            omni.kit.undo.undo()
            await ui_test.human_delay()
            widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_palettevariant'")
            self.assertEqual(widget.widget.enabled, True)
            self.assertEqual(widget.widget.visible, True)

            # verify mixed is not shown
            omni.kit.undo.redo()
            await ui_test.human_delay()
            widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_palettevariant'")
            self.assertEqual(widget.widget.enabled, True)
            self.assertEqual(widget.widget.visible, False)

            # verify mixed is shown
            omni.kit.undo.undo()
            await ui_test.human_delay()
            widget = ui_test.find("Property//Frame/**/*.identifier=='mixed_variant_palettevariant'")
            self.assertEqual(widget.widget.enabled, True)
            self.assertEqual(widget.widget.visible, True)
