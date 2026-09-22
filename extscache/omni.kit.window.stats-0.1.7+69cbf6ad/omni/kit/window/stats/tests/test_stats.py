import asyncio
import carb
import unittest
import carb
import omni.kit.test
import omni.usd
import omni.ui as ui
from omni.kit import ui_test


class TestStats(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_stats_window(self):
        stats_window = ui_test.find("Statistics")
        stats_window.widget.visible = True
        await stats_window.focus()

        line_count = [0, 0, 0]
        for index in range(0, 3):
            # can't use widget.click as open combobox has no readable size and clicks goto stage window
            stats_window.find("**/ComboBox[*]").model.get_item_value_model(None, 0).set_value(index)
            await ui_test.human_delay(10)
            for widget in stats_window.find_all("**/Label[*]"):
                line_count[index] += len(widget.widget.text.split('\n'))

        self.assertNotEqual(line_count[0], 0)
        self.assertNotEqual(line_count[1], 0)
        self.assertNotEqual(line_count[2], 0)
