## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.ui as ui
from omni.ui.tests.test_base import OmniUiTest
from .. import HighlightLabel
from pathlib import Path
import sys

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")

TEST_WIDTH = 400
TEST_HEIGHT = 200
CUSTOM_UI_STYLE = {
    "HighlightLabel": {"color": 0xFFFFFFFF},
    "HighlightLabel::highlight": {"color": 0xFF0000FF},
}

class HightlightLabelTestCase(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_general(self):
        """Testing general look of SearchField"""
        window = await self.create_test_window(width=TEST_WIDTH, height=TEST_HEIGHT)
        with window.frame:
            with ui.VStack(spacing=10):
                HighlightLabel("No highlight")
                HighlightLabel("Highlight All", highlight="Highlight All")
                HighlightLabel("Highlight 'gh'", highlight="gh")
                label = HighlightLabel("Highlight 't' via property")
                label.highlight = "t"
                HighlightLabel("Highlight 'H' MATCH Case", highlight="H", match_case=True)
                HighlightLabel("Match Case All", highlight="Match Case All", match_case=True)
                HighlightLabel("Highlight style CUSTOM", highlight="style", style=CUSTOM_UI_STYLE)

        await self.docked_test_window(window=window, width=TEST_WIDTH, height=TEST_HEIGHT)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="highlight_label.png")