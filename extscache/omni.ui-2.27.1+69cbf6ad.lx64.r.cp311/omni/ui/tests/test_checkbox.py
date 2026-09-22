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
from omni.ui import color as cl


class TestCheckBox(OmniUiTest):
    """Testing ui.CheckBox"""

    async def test_general(self):
        """Testing general properties of ui.CheckBox"""
        window = await self.create_test_window()

        no_border_style = {
            "CheckBox": {
                # The check color
                "color": cl.black,
                # The background color
                "background_color": cl.white,
                # The roundness of the check box
                "border_radius": 1,
            }
        }

        border_style = {
            "CheckBox": {
                # The check color
                "color": cl.black,
                # The background color
                "background_color": cl.white,
                # The border color
                "secondary_background_color": cl.blue,
                # The roundness of the check box
                "border_radius": 1,
                # The border size
                "border_width": 2,
            }
        }

        checked_style = {
            "CheckBox": {
                # The background color
                "background_color": cl.white,
                # The roundness of the check box
                "border_radius": 1,
            },
            "CheckBox:checked": {
                # The check color
                "color": cl.black,
                # The background color
                "background_color": cl.red,
                # The roundness of the check box
                "border_radius": 2,
            }
        }

        with window.frame:
            with ui.VStack(height=0):
                # Simple check box
                ui.CheckBox().model.set_value(False)
                ui.CheckBox().model.set_value(True)

                # Styled check box no border
                ui.CheckBox(enabled=True, style=no_border_style).model.set_value(False)
                ui.CheckBox(enabled=True, style=no_border_style).model.set_value(True)

                # Styled check box with border
                ui.CheckBox(enabled=True, style=border_style).model.set_value(False)
                ui.CheckBox(enabled=True, style=border_style).model.set_value(True)

                # Styled check box with different style in checked state
                ui.CheckBox(enabled=True, style=checked_style).model.set_value(False)
                ui.CheckBox(enabled=True, style=checked_style).model.set_value(True)

        await self.finalize_test()
