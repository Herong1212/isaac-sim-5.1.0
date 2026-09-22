"Tests for frame range model"

from pathlib import Path
from unittest.mock import Mock

import omni.kit.app
import omni.usd
from omni import ui
from omni.anim.widget.timeline import StageRangeModel, TimeValueModel
from omni.kit.test.async_unittest import AsyncTestCase, unittest


class TestStageRangeModel(AsyncTestCase):
    async def setUp(self) -> None:
        super().setUp()
        self._usd_context = omni.usd.get_context()
        self._timeline = self._usd_context.get_timeline()
        self._fps = self._timeline.set_time_codes_per_second(10)
        self._timeline.set_start_time(1.0)
        self._timeline.set_end_time(2.0)
        self._timeline.set_current_time(1.5)
        self._timeline.clear_tentative_time()
        await omni.kit.app.get_app().next_update_async()
        self._range_model = StageRangeModel(self._usd_context)

    @property
    def timeline_current_time(self) -> float:
        return self._timeline.get_current_time() * self._timeline.get_time_codes_per_seconds()

    @property
    def timeline_tentative_time(self) -> float:
        return self._timeline.get_tentative_time() * self._timeline.get_time_codes_per_seconds()

    async def test_init(self):
        self.assertEqual(self._range_model.min, 10)
        self.assertEqual(self._range_model.max, 20)
        self.assertEqual(self._range_model.start, 10)
        self.assertEqual(self._range_model.end, 20)
        self.assertTrue(self._range_model.is_valid)
        self.assertEqual(self._range_model.fps, 10)
        self.assertEqual(self._range_model.current_time, 15)
        self.assertIsNone(self._range_model.tentative_time, None)
        self.assertIsInstance(self._range_model.current_time_model, TimeValueModel)
        self.assertIsInstance(self._range_model.fps_model, ui.SimpleFloatModel)

    async def test_setters(self):
        self._range_model.current_time = 1.2
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._range_model.current_time, self.timeline_current_time)

        self._range_model.tentative_time = 1.6
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._range_model.tentative_time, self.timeline_tentative_time)

    async def test_timeline_events(self):
        self._timeline.set_current_time(0.1)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._range_model.current_time, 1)

        self._timeline.set_tentative_time(0.2)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._range_model.tentative_time, 2)

        self._timeline.clear_tentative_time()
        await omni.kit.app.get_app().next_update_async()
        self.assertIsNone(self._range_model.tentative_time)

        self._timeline.set_time_codes_per_second(60)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._range_model.fps, 60)

    async def test_zoom_behavior(self):
        # set so zoomed is false
        self._range_model.set_range(0, 10)
        self._range_model.set_max_range(0, 10)
        await omni.kit.app.get_app().next_update_async()
        self.assertFalse(self._range_model.zoomed)

        # changing start time when not zoomed should update both min and start
        self._timeline.set_start_time(-0.1)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._range_model.min, -1)
        self.assertEqual(self._range_model.start, -1)
        self.assertFalse(self._range_model.zoomed)

        # same with end time
        self._timeline.set_end_time(1.1)
        await omni.kit.app.get_app().next_update_async()
        self.assertFalse(self._range_model.zoomed)
        self.assertEqual(self._range_model.max, 11)
        self.assertEqual(self._range_model.end, 11)

        # zoomed is true
        self._range_model.set_max_range(0, 10)
        self._range_model.set_range(1, 9)
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(self._range_model.zoomed)

        # changing start time when zoomed should update only min
        self._timeline.set_start_time(-0.1)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._range_model.min, -1)
        self.assertEqual(self._range_model.start, 1)
        self.assertTrue(self._range_model.zoomed)

        # same with end time
        self._timeline.set_end_time(1.1)
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(self._range_model.zoomed)
        self.assertEqual(self._range_model.max, 11)
        self.assertEqual(self._range_model.end, 9)

    async def test_stage_change(self):
        test_path = Path(__file__).parent
        data_path = test_path / "data"
        test_file_path = data_path / "test_stage.usd"
        await omni.usd.get_context().open_stage_async(str(test_file_path))
        self.assertEqual(self._range_model.min, 10)
        self.assertEqual(self._range_model.max, 80)
        self.assertEqual(self._range_model.start, 10)
        self.assertEqual(self._range_model.end, 80)
        self.assertTrue(self._range_model.is_valid)
        self.assertEqual(self._range_model.fps, 30)


if __name__ == "__main__":
    unittest.main(verbosity=2)
