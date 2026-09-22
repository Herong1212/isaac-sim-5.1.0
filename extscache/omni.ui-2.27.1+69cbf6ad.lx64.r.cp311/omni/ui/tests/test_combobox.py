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
import omni.kit.app
import omni.ui as ui
from omni.ui import color as cl


class TestComboBox(OmniUiTest):
    """Testing ui.ComboBox"""

    async def test_general(self):
        """Testing general look of ui.ComboBox"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack():
                # Simple combo box
                style = {
                    "background_color": cl.black,
                    "border_color": cl.white,
                    "border_width": 1,
                    "padding": 0,
                }

                for i in range(8):
                    style["padding"] = i * 2
                    ui.ComboBox(0, f"{i}", "B", style=style, height=0)

        await self.finalize_test()
