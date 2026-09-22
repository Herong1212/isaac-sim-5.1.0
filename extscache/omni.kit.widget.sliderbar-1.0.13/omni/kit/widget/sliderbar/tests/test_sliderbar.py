import asyncio
import copy

import carb
import omni.kit.app
import omni.ui as ui
from omni.kit.widget.sliderbar import ArrowAlignment, SliderBar, TimeSliderBar
from omni.ui.tests.test_base import OmniUiTest


class TestSliderbar(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_sliderbar(self):
        slider_bar = SliderBar()
        slider_bar.set_current(5)
        slider_bar.set_start(2)
        slider_bar.set_end(10)
        self.assertEqual(slider_bar.get_current(), 5)
        self.assertEqual(slider_bar.get_start(), 2)
        self.assertEqual(slider_bar.get_end(), 10)
