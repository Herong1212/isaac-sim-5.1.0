import math
from collections import deque
from functools import partial
from .test_base import OmniUiTest
import omni.ui as ui
from omni.ui import color as cl
import omni.kit.app

class TestPlot(OmniUiTest):
    """Testing ui.Plot"""

    async def test_plot_crash(self):
        window = await self.create_test_window(block_devices=False)
        with window.frame:
            plot = ui.Plot(ui.Type.LINE2D, -1.0, 1.0, 0.0, 0.0, width=360, height=100, style={"color": cl.red})
            self.assertTrue(plot is not None)
        await self.finalize_test_no_image()

    async def test_plot(self):
        import omni.kit.ui_test as ui_test
        window = await self.create_test_window(block_devices=False)
        with window.frame:
            data = deque([i / 100 for i in range(-100, 101)])
            plot = ui.Plot(ui.Type.LINE, -1.0, 1.0, *data, width=360, height=100, style={"color": cl.red})

        await ui_test.input.wait_n_updates_internal(update_count=4)
        data.rotate(10)
        plot.set_data(*data)
        await ui_test.input.wait_n_updates_internal(update_count=4)
        await self.finalize_test()

    async def test_plot_line2d(self):
        window = await self.create_test_window(block_devices=False)
        with window.frame:
            plot = ui.Plot(ui.Type.LINE2D, -10.0, 10.0, *[0.0, 1.0], style={"color": ui.color.white})
            plot.set_xy_data([(0,0), (1,1), (2,0)])
        await self.finalize_test()