"Tests for frame range model"

from omni import ui
from omni.anim.widget.timeline import RangeModel, TimelineGridModel, TimeUnits
from omni.kit.preferences.animation import TimeDisplay, set_time_display
from omni.kit.test.async_unittest import AsyncTestCase, AsyncTestSuite, AsyncTextTestRunner, unittest


class TestBaseTimelineGridModel(AsyncTestCase):
    def setUp(self) -> None:
        super().setUp()

        self._frame_range_model = RangeModel(0, 99, 0, 99, time_units=TimeUnits.USD_TIMECODE)  # inclusive length
        self._seconds_range_model = RangeModel(0, 0.9, time_units=TimeUnits.SECONDS, fps=10)

    def test_grid_calcuations_for_frames(self):
        time_display_model = ui.SimpleStringModel(TimeDisplay.FRAMES.value)
        grid_model = TimelineGridModel(self._frame_range_model, time_display_model=time_display_model)
        width = 100
        expected_large_tick_step = 50
        expected_frame_numbers_label_size = 16.8
        grid_model.on_container_width_changed(container_width=width)
        self.assertEqual(grid_model.frame_width, 1.0)
        self.assertEqual(
            grid_model.get_frame_numbers_label_size(self._frame_range_model.start, self._frame_range_model.end),
            expected_frame_numbers_label_size,
        )
        self.assertGreaterEqual(grid_model.small_tick_width, grid_model.MIN_SMALL_TICK_WIDTH)
        self.assertGreaterEqual(grid_model.large_tick_width, grid_model._get_min_large_tick_width())
        self.assertEqual(grid_model.large_tick_step, expected_large_tick_step)

    def test_grid_calcuations_for_seconds(self):
        time_display_model = ui.SimpleStringModel(TimeDisplay.FRAMES.value)
        grid_model = TimelineGridModel(self._seconds_range_model, time_display_model=time_display_model)
        width = 100
        expected_large_tick_step = 50
        expected_frame_numbers_label_size = 33.6
        grid_model.on_container_width_changed(container_width=width)
        self.assertEqual(grid_model.range_length_inclusive, 1)
        self.assertEqual(grid_model.pixels_per_time_unit, 100)
        self.assertEqual(grid_model.frame_width, 10)
        self.assertEqual(grid_model.transform_timeline_to_position(0.5), 50)
        self.assertEqual(grid_model.transform_position_to_timeline(50), 0.5)
        # self.assertEqual(grid_model.get_frame_numbers_label_size(self._frame_range_model.start, self._frame_range_model.end), expected_frame_numbers_label_size)
        # self.assertEqual(grid_model.large_tick_step, expected_large_tick_step)
        # self.assertGreaterEqual(grid_model.small_tick_width, grid_model.MIN_SMALL_TICK_WIDTH)
        # self.assertGreaterEqual(grid_model.large_tick_width, grid_model._get_min_large_tick_width())


if __name__ == "__main__":
    from asyncio import ensure_future

    from omni.kit.test.async_unittest import AsyncTestSuite, AsyncTextTestRunner

    suite = AsyncTestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestBaseTimelineGridModel))
    runner = AsyncTextTestRunner()
    ensure_future(runner.run(suite))
