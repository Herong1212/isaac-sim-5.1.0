"Tests TimeValueModel and TimeDisplayValueModel model"

from unittest import mock

import carb
from omni import ui
from omni.anim.widget.timeline import TimeDisplayValueModel, TimeStringInputModel, TimeUnits, TimeValueModel
from omni.kit.preferences.animation import TimeDisplay
from omni.kit.test.async_unittest import AsyncTestCase, AsyncTestSuite, AsyncTextTestRunner, unittest


class TestTimeDisplayValueModel(AsyncTestCase):
    def setUp(self) -> None:
        super().setUp()
        self._time_value_model_frames = TimeValueModel(30, time_units=TimeUnits.FRAMES)
        self._time_value_model_seconds = TimeValueModel(1, time_units=TimeUnits.SECONDS)

        self._fps_model = ui.SimpleFloatModel(30.0)
        _seconds_display_model = ui.SimpleStringModel(TimeDisplay.SECONDS)
        _frames_display_model = ui.SimpleStringModel(TimeDisplay.FRAMES)
        _timecode_display_model = ui.SimpleStringModel(TimeDisplay.TIMECODE)

        self._time_display_seconds = TimeDisplayValueModel(
            self._time_value_model_seconds, time_display_model=_seconds_display_model, fps_model=self._fps_model
        )
        self._time_display_seconds_as_frames = TimeDisplayValueModel(
            self._time_value_model_seconds, time_display_model=_frames_display_model, fps_model=self._fps_model
        )
        self._time_display_seconds_as_timecode = TimeDisplayValueModel(
            self._time_value_model_seconds, time_display_model=_timecode_display_model, fps_model=self._fps_model
        )

        self._time_display_frames = TimeDisplayValueModel(
            self._time_value_model_frames, time_display_model=_frames_display_model, fps_model=self._fps_model
        )
        self._time_display_frames_as_seconds = TimeDisplayValueModel(
            self._time_value_model_frames, time_display_model=_seconds_display_model, fps_model=self._fps_model
        )
        self._time_display_frames_as_timecode = TimeDisplayValueModel(
            self._time_value_model_frames, time_display_model=_timecode_display_model, fps_model=self._fps_model
        )

    def test_value_models(self):
        self.assertEqual(self._time_value_model_frames.time_units, TimeUnits.FRAMES)
        self.assertEqual(self._time_value_model_seconds.time_units, TimeUnits.SECONDS)

    def test_display_value_models(self):
        # check fps
        self.assertEqual(self._time_display_frames.fps, 30)
        self.assertEqual(self._time_display_seconds.fps, 30)
        # check time display
        self.assertEqual(self._time_display_seconds.time_display, TimeDisplay.SECONDS)
        self.assertEqual(self._time_display_seconds_as_frames.time_display, TimeDisplay.FRAMES)
        self.assertEqual(self._time_display_seconds_as_timecode.time_display, TimeDisplay.TIMECODE)

        self.assertEqual(self._time_display_frames.time_display, TimeDisplay.FRAMES)
        self.assertEqual(self._time_display_frames_as_seconds.time_display, TimeDisplay.SECONDS)
        self.assertEqual(self._time_display_frames_as_timecode.time_display, TimeDisplay.TIMECODE)

        # check time units
        self.assertEqual(self._time_display_seconds.time_units, TimeUnits.SECONDS)
        self.assertEqual(self._time_display_seconds_as_frames.time_units, TimeUnits.SECONDS)
        self.assertEqual(self._time_display_seconds_as_timecode.time_units, TimeUnits.SECONDS)

        self.assertEqual(self._time_display_frames.time_units, TimeUnits.FRAMES)
        self.assertEqual(self._time_display_frames_as_seconds.time_units, TimeUnits.FRAMES)
        self.assertEqual(self._time_display_frames_as_timecode.time_units, TimeUnits.FRAMES)

        # check as string
        self.assertEqual(self._time_display_seconds.as_string, "1.0s")
        self.assertEqual(self._time_display_seconds_as_frames.as_string, "30")
        self.assertEqual(self._time_display_seconds_as_timecode.as_string, "00:00:01.00")

        self.assertEqual(self._time_display_frames.as_string, "30")
        self.assertEqual(self._time_display_frames_as_seconds.as_string, "1.0s")
        self.assertEqual(self._time_display_frames_as_timecode.as_string, "00:00:01.00")

    def test_set_value_as_unit(self):
        # check set value as unit
        seconds_value = 2
        frames_value = 20

        # set frames as seconds
        self._time_display_frames.set_value_as_unit(seconds_value, TimeUnits.SECONDS)
        self.assertEqual(self._time_display_frames.as_float, seconds_value * self._time_display_frames.fps)

        # set frames as frames
        self._time_display_frames.set_value_as_unit(10, TimeUnits.FRAMES)
        self.assertEqual(self._time_display_frames.as_float, 10)

        # set seconds as frames
        self._time_display_seconds.set_value_as_unit(frames_value, TimeUnits.FRAMES)
        self.assertEqual(self._time_display_seconds.as_float, frames_value / self._time_display_frames.fps)

        # set seconds as seconds
        self._time_display_seconds.set_value_as_unit(20, TimeUnits.SECONDS)
        self.assertEqual(self._time_display_seconds.as_float, 20)

    def test_time_string_input_model(self):
        # Frames parent model
        time_string_input_model = TimeStringInputModel(self._time_display_frames)
        self.assertEqual(time_string_input_model.as_string, "30")

        value, input_type = time_string_input_model.string_to_value("2s")
        self.assertEqual(value, 2)
        self.assertEqual(input_type, TimeDisplay.SECONDS)

        # if input is just numbers, uses parent display unit as type
        value, input_type = time_string_input_model.string_to_value("100")
        self.assertEqual(value, 100)
        self.assertEqual(input_type, TimeDisplay.FRAMES)

        value, input_type = time_string_input_model.string_to_value("00:00:01.29")
        self.assertEqual(value, 59)
        self.assertEqual(input_type, TimeDisplay.FRAMES)

        value, input_type = time_string_input_model.string_to_value("00:01.29")
        self.assertEqual(value, 59)
        self.assertEqual(input_type, TimeDisplay.FRAMES)

        # Seconds parent model
        time_string_input_model = TimeStringInputModel(self._time_display_seconds)
        self.assertEqual(time_string_input_model.as_string, "1.0s")

        value, input_type = time_string_input_model.string_to_value("2s")
        self.assertEqual(value, 2)
        self.assertEqual(input_type, TimeDisplay.SECONDS)

        value, input_type = time_string_input_model.string_to_value("100")
        self.assertEqual(value, 100)
        self.assertEqual(input_type, TimeDisplay.SECONDS)

        value, input_type = time_string_input_model.string_to_value("00:00:01.29")
        self.assertEqual(value, (1 + (29 / 30)))
        self.assertEqual(input_type, TimeDisplay.SECONDS)

        value, input_type = time_string_input_model.string_to_value("00:01.29")
        self.assertEqual(value, (1 + (29 / 30)))
        self.assertEqual(input_type, TimeDisplay.SECONDS)

        # test garbage input
        garbage = "garbage"
        time_string_input_model.as_string = garbage
        self.assertEqual(time_string_input_model.as_string, garbage)
        self.assertFalse(time_string_input_model.is_valid)
        with mock.patch("carb.log_error") as mock_log_warn:
            time_string_input_model.commit()
            mock_log_warn.assert_called_once_with(f"Cannot commit: {garbage}")


if __name__ == "__main__":
    from asyncio import ensure_future

    from omni.kit.test.async_unittest import AsyncTestSuite, AsyncTextTestRunner

    suite = AsyncTestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestTimeDisplayValueModel))
    runner = AsyncTextTestRunner()
    ensure_future(runner.run(suite))
