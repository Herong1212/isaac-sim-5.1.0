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
from omni.ui import color as cl


class TestMultiField(OmniUiTest):
    """Testing ui.Frame"""

    async def test_column_count(self):
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack():
                f = ui.MultiFloatDragField(0.1, 0.2, 0.3, h_spacing=5, name="colorField")
                f.column_count = 3

        await self.finalize_test()

    async def test_column_count_smaller(self):
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack():
                f = ui.MultiFloatDragField(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, h_spacing=5, name="colorField")
                f.column_count = 2

        await self.finalize_test()

    async def test_column_count_larger(self):
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack():
                f = ui.MultiFloatDragField(0.1, 0.2, 0.3, h_spacing=5, name="colorField")
                f.column_count = 5

        await self.finalize_test()