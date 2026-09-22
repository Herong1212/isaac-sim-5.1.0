## Copyright (c) 2018-2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from .test_base import OmniUiTest
import omni.kit.app
import omni.ui as ui
import asyncio


class TestTooltip(OmniUiTest):
    """Testing tooltip"""

    async def test_general(self):
        """Testing general properties of ui.Label"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            # Simple text
            label = ui.Label("Hello world", tooltip="This is a tooltip")

        ref = ui_test.WidgetRef(label, "")

        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move(ref.center)
        await asyncio.sleep(1.0)

        await self.finalize_test()

    async def test_property(self):
        """Testing general properties of ui.Label"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            # Simple text
            label = ui.Label("Hello world")
            label.tooltip = "This is a tooltip"

            self.assertEqual(label.tooltip, "This is a tooltip")

        ref = ui_test.WidgetRef(label, "")

        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move(ref.center)
        await asyncio.sleep(1.0)

        await self.finalize_test()

    async def test_delay(self):
        """Testing general properties of ui.Label"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            # Simple text
            label = ui.Label("Hello world", tooltip="This is a tooltip")

        ref = ui_test.WidgetRef(label, "")

        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move(ref.center)
        await asyncio.sleep(0.2)

        await self.finalize_test()
        await ui_test.emulate_mouse_move(ui_test.Vec2(ref.center.x, ref.center.y + 50))  # get rid of tooltip
        await asyncio.sleep(0.2)

    async def test_tooltip_in_separate_window(self):
        """Testing tooltip on a separate window"""
        import omni.kit.ui_test as ui_test

        win = await self.create_test_window(block_devices=False)
        with win.frame:
            with ui.VStack():
                ui.Spacer()
                # create a new frame which is on a separate window
                with ui.Frame(separate_window=True):
                    style = {"BezierCurve": {"color": omni.ui.color.red, "border_width": 2}}
                    curve = ui.BezierCurve(style=style, tooltip="This is a tooltip")

        ref = ui_test.WidgetRef(curve, "")
        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move(ref.center)
        await asyncio.sleep(1.0)

        await self.finalize_test()
