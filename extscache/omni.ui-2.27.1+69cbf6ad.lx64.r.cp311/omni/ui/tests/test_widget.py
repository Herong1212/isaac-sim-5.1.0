## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["TestWidget"]

from .test_base import OmniUiTest
import omni.ui as ui


class TestWidget(OmniUiTest):
    """Testing ui.Widget"""

    async def test_identifier(self):
        """Testing identifer and name properties of ui.Widget"""
        window = await self.create_test_window()

        with window.frame:
            with ui.ZStack():
                rect_1 = ui.Rectangle(name="RECT1")
                rect_2 = ui.Rectangle(name="RECT 2")
                rect_3 = ui.Rectangle(name="RECT 3", identifier = "RECT 3")
                rect_4 = ui.Rectangle(name="RECT 4", identifier = "RECT 4 diverged")
                rect_5 = ui.Rectangle(name="RECT [5]")
                rect_6 = ui.Rectangle(name="RECT [6]", identifier = "RECT 6 [diverged]")

        self.assertEqual(rect_1.name, "RECT1")
        self.assertEqual(rect_1.identifier, "RECT1")

        self.assertEqual(rect_2.name, "RECT 2")
        self.assertEqual(rect_2.identifier, "RECT 2")

        self.assertEqual(rect_3.name, "RECT 3")
        self.assertEqual(rect_3.identifier, "RECT 3")

        self.assertEqual(rect_4.name, "RECT 4")
        self.assertEqual(rect_4.identifier, "RECT 4 diverged")

        self.assertEqual(rect_5.name, "RECT [5]")
        self.assertEqual(rect_5.identifier, "RECT [5]")

        self.assertEqual(rect_6.name, "RECT [6]")
        self.assertEqual(rect_6.identifier, "RECT 6 [diverged]")

        await self.finalize_test_no_image()
