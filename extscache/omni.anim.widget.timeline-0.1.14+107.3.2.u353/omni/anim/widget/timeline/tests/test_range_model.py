"Tests for frame range model"

from unittest.mock import Mock

import omni.kit.app
from omni import ui
from omni.anim.widget.timeline import RangeModel, TimeValueModel
from omni.kit.test.async_unittest import AsyncTestCase, unittest


class TestRangeModel(AsyncTestCase):
    async def setUp(self) -> None:
        super().setUp()
        self._range_model = RangeModel(0, 100, 0, 100, fps=30, current_time=10)
        self._unbounded_range_model = RangeModel(0, 100, fps=30, current_time=10)

    async def test_init(self):
        self.assertEqual(self._range_model.min, 0)
        self.assertEqual(self._range_model.max, 100)
        self.assertEqual(self._range_model.start, 0)
        self.assertEqual(self._range_model.end, 100)
        self.assertTrue(self._range_model.is_valid)
        self.assertEqual(self._range_model.fps, 30)
        self.assertIsInstance(self._range_model.current_time_model, TimeValueModel)
        self.assertIsInstance(self._range_model.fps_model, ui.SimpleFloatModel)

        self.assertIsNone(self._unbounded_range_model.max_range)
        self.assertIsNone(self._unbounded_range_model.min)
        self.assertIsNone(self._unbounded_range_model.max)

    async def test_setters(self):
        self._range_model.min = -10
        self._range_model.max = 110
        self._range_model.start = 5
        self._range_model.end = 90
        self._range_model.current_time = 20
        await omni.kit.app.get_app().next_update_async()

        self.assertEqual(self._range_model.min, -10)
        self.assertEqual(self._range_model.max, 110)
        self.assertEqual(self._range_model.start, 5)
        self.assertEqual(self._range_model.end, 90)
        self.assertEqual(self._range_model.current_time, 20)

    async def test_range_validity(self):
        self._range_model.start = 100
        self._range_model.end = 0
        self.assertFalse(self._range_model.is_valid)

    async def test_range_zoom(self):
        self.assertFalse(self._range_model.zoomed)
        self._range_model.start = 25
        self._range_model.end = 75
        self.assertTrue(self._range_model.zoomed)
        # unbound is never 'zoomed'
        self.assertFalse(self._unbounded_range_model.zoomed)

    async def test_range_setters(self):
        self._range_model.set_range(-10, 110)
        self.assertEqual(self._range_model.start, -10)
        self.assertEqual(self._range_model.end, 110)
        self.assertRaises(ValueError, self._range_model.set_range, 90, 60)

        self._range_model.set_max_range(-10, 110)
        self.assertEqual(self._range_model.min, -10)
        self.assertEqual(self._range_model.max, 110)

        self.assertIsNone(self._unbounded_range_model.max_range)
        self.assertRaises(ValueError, self._unbounded_range_model.set_max_range, 0, 100)
        self.assertRaises(ValueError, self._unbounded_range_model.set_max_range, 90, 60)

    async def test_model_manipulation(self):
        mock_item_changed = Mock()
        _item_change_sub = self._range_model.subscribe_item_changed_fn(mock_item_changed)
        self._range_model.begin_edit(self._range_model.view_range)
        self.assertTrue(self._range_model.is_editing)
        self._range_model.start = 10
        mock_item_changed.assert_not_called()
        self._range_model.end_edit(self._range_model.view_range)
        mock_item_changed.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
