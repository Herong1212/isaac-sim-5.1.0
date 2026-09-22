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
    "CollapsableFrame": {
        "background_color": 0xFF383838,
        "secondary_color": 0xFF4D4D4D,
        "color": 0xFFFFFFFF,
        "border_radius": 3,
        "margin": 1,
        "padding": 3,
    }
}


class TestCollapsableFrame(OmniUiTest):
    """Testing ui.CollapsableFrame"""

    async def test_general(self):
        """Testing general properties of ui.CollapsableFrame"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack(style=STYLE, height=0, spacing=3):
                with ui.CollapsableFrame("Frame1"):
                    ui.Label("Label in CollapsableFrame")
                with ui.CollapsableFrame("Frame2"):
                    ui.Label("First label, should not be displayed")
                    ui.Label("Second label, should be displayed")
                with ui.CollapsableFrame("Frame3"):
                    ui.Label("Long Label in CollapsableFrame. " * 9, word_wrap=True)

        await self.finalize_test()

    async def test_collapsing(self):
        """Testing the collapsing behaviour of ui.CollapsableFrame"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack(style=STYLE, height=0, spacing=3):
                frame1 = ui.CollapsableFrame("Frame1")
                with frame1:
                    ui.Label("Label in CollapsableFrame")
                frame2 = ui.CollapsableFrame("Frame2")
                with frame2:
                    ui.Label("Label in CollapsableFrame")
                frame3 = ui.CollapsableFrame("Frame3")
                with frame3:
                    ui.Label("Label in CollapsableFrame")
                frame4 = ui.CollapsableFrame("Frame4", collapsed=True)
                with frame4:
                    ui.Label("Label in CollapsableFrame")
                frame5 = ui.CollapsableFrame("Frame5")
                with frame5:
                    ui.Label("Label in CollapsableFrame")

        frame1.collapsed = True

        await omni.kit.app.get_app().next_update_async()

        frame2.collapsed = True
        frame3.collapsed = True

        await omni.kit.app.get_app().next_update_async()

        frame3.collapsed = False

        await self.finalize_test()

    async def test_collapsing_build_fn(self):
        """Testing the collapsing behaviour of ui.CollapsableFrame and delayed ui.Frame"""
        window = await self.create_test_window()

        def content():
            ui.Label("Label in CollapsableFrame")

        with window.frame:
            with ui.VStack(style=STYLE, height=0, spacing=3):
                frame1 = ui.CollapsableFrame("Frame1")
                with frame1:
                    ui.Frame(build_fn=content)
                frame2 = ui.CollapsableFrame("Frame2")
                with frame2:
                    ui.Frame(build_fn=content)
                frame3 = ui.CollapsableFrame("Frame3")
                with frame3:
                    ui.Frame(build_fn=content)
                frame4 = ui.CollapsableFrame("Frame4", collapsed=True)
                with frame4:
                    ui.Frame(build_fn=content)
                frame5 = ui.CollapsableFrame("Frame5")
                with frame5:
                    ui.Frame(build_fn=content)

        frame1.collapsed = True

        await omni.kit.app.get_app().next_update_async()

        frame2.collapsed = True
        frame3.collapsed = True

        await omni.kit.app.get_app().next_update_async()

        frame3.collapsed = False

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_nested(self):
        """Testing the collapsing behaviour of nested ui.CollapsableFrame"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack(style=STYLE, height=0, spacing=3):
                frame1 = ui.CollapsableFrame("Frame1")
                with frame1:
                    with ui.VStack(height=0, spacing=3):
                        ui.Label("Label in CollapsableFrame 1")

                        frame2 = ui.CollapsableFrame("Frame2")
                        with frame2:
                            with ui.VStack(height=0, spacing=3):
                                ui.Label("Label in CollapsableFrame 2")

                                frame3 = ui.CollapsableFrame("Frame3")
                                with frame3:
                                    ui.Label("Label in CollapsableFrame 3")

                frame4 = ui.CollapsableFrame("Frame4", collapsed=True)
                with frame4:
                    with ui.VStack(height=0, spacing=3):
                        ui.Label("Label in CollapsableFrame 4")

                        frame5 = ui.CollapsableFrame("Frame5")
                        with frame5:
                            ui.Label("Label in CollapsableFrame 5")

                        frame6 = ui.CollapsableFrame("Frame6", collapsed=True)
                        with frame6:
                            ui.Label("Label in CollapsableFrame 6")

                        frame7 = ui.CollapsableFrame("Frame7")
                        with frame7:
                            ui.Label("Label in CollapsableFrame 7")

        frame1.collapsed = True
        frame6.collapsed = False
        frame7.collapsed = True

        await omni.kit.app.get_app().next_update_async()

        frame1.collapsed = False
        frame2.collapsed = True
        frame3.collapsed = True
        frame4.collapsed = False
        frame5.collapsed = True

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()
