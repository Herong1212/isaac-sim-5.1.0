## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from .test_base import OmniUiTest
from pathlib import Path
import asyncio
import sys
import omni.kit.app
import omni.ui as ui

CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.parent.parent.parent.joinpath("data")


class TestOverflow(OmniUiTest):
    # Testing ui.IntField for overflow exception
    async def test_int_overflow(self):
        from omni.kit import ui_test

        window = ui.Window("IntField", width=450, height=800)
        with window.frame:
            with ui.VStack():
                ui.Spacer(height=10)
                ui.IntField(model=ui.SimpleIntModel())
                ui.Spacer(height=10)

        widget = ui_test.find("IntField//Frame/**/IntField[*]")
        await widget.input("99999999999999999999999999999999999999999999")
        await ui_test.human_delay(500)

    # Testing ui.FloatField for overflow exception
    async def test_float_overflow(self):
        from omni.kit import ui_test

        window = ui.Window("FloatField", width=450, height=800)
        with window.frame:
            with ui.VStack():
                ui.Spacer(height=10)
                ui.FloatField(model=ui.SimpleFloatModel())
                ui.Spacer(height=10)

        widget = ui_test.find("FloatField//Frame/**/FloatField[*]")
        await widget.input("1.6704779438076223e-52")
        await ui_test.human_delay(500)
