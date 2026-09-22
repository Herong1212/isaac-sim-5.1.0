## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from .test_base import OmniUiTest
import omni.ui as ui
import omni.kit.app


STYLE = {
    "ScrollingFrame": {"background_color": 0xFF000000, "secondary_color": 0xFFFFFFFF, "scrollbar_size": 10},
    "Label": {"color", 0xFFFFFFFF},
}


class TestScrollingFrame(OmniUiTest):
    """Testing ui.ScrollingFrame"""

    async def test_general(self):
        """Testing general properties of ui.ScrollingFrame"""
        window = await self.create_test_window()

        with window.frame:
            with ui.ScrollingFrame(
                style=STYLE,
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
            ):
                with ui.VStack():
                    for i in range(50):
                        ui.Label(f"Label in ScrollingFrame {i}")

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_scroll(self):
        """Testing precize scroll position"""
        window = await self.create_test_window()

        with window.frame:
            with ui.ScrollingFrame(
                style=STYLE,
                scroll_y=256,
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
            ):
                with ui.VStack():
                    for i in range(50):
                        ui.Label(f"Label in ScrollingFrame {i}")

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_size(self):
        """Testing size of child"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack(style=STYLE):
                with ui.ScrollingFrame(
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                ):
                    ui.Rectangle(style={"background_color": "black", "border_color": "red", "border_width": 1})

                with ui.HStack():
                    with ui.ScrollingFrame(
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    ):
                        ui.Rectangle(style={"background_color": "black", "border_color": "red", "border_width": 1})

                    with ui.ScrollingFrame(
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    ):
                        ui.Rectangle(style={"background_color": "black", "border_color": "red", "border_width": 1})

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_scroll_end(self):
        """Testing max scroll x/y of ui.ScrollingFrame"""
        window = await self.create_test_window()

        with window.frame:
            scrolling_frame = ui.ScrollingFrame(
                style=STYLE,
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
            )
            with scrolling_frame:
                with ui.VStack():
                    for i in range(50):
                        ui.Label(f"Label in ScrollingFrame {i}")

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        scrolling_frame.scroll_y = scrolling_frame.scroll_y_max

        await omni.kit.app.get_app().next_update_async()
        await self.finalize_test()
