import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.ui as ui
import omni.kit.app

from ..datetime.date_widget import DateWidget
from ..datetime.time_widget import TimeWidget
from ..datetime.timezone_widget import TimezoneWidget
from ..datetime.models import ZoneModel
from .test_utils import time_logger
import datetime
import random
import pytz


@time_logger
class TestDatetimeWidget(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._window = ui.Window("test_datetime_widget", width=400, height=400)
        await ui_test.human_delay(10)

    async def tearDown(self):
        self._window.destroy()

    async def test_date(self):
        with self._window.frame:
            with ui.VStack():
                date_widget = DateWidget()
        await ui_test.human_delay(10)
        field = ui_test.WidgetRef(date_widget._date_field, "", self._window)
        await field.click()
        for _ in range(10):
            if date_widget._calendar is not None:
                break
            await omni.kit.app.get_app().next_update_async()

        calendar = date_widget._calendar
        # pick a random date and set on the UI
        min_date = datetime.date(calendar._year_min, 1, 1)
        max_date = datetime.date(calendar._year_max, 12, 31)
        date = min_date + datetime.timedelta(days=random.randint(0, (max_date - min_date).days))

        calendar._year_combo.model.get_item_value_model(None, 0).set_value(date.year - calendar._year_min)
        self.assertEqual(date_widget.model.year, date.year)
        calendar._month_combo.model.get_item_value_model(None, 0).set_value(date.month - 1)
        self.assertEqual(date_widget.model.month, date.month)
        # wait for week days rebuild
        await ui_test.human_delay(10)
        day_button = ui_test.WidgetRef(calendar._day_buttons[date.day], "")
        await ui_test.emulate_mouse_move_and_click(day_button.center)
        self.assertEqual(date_widget.model.day, date.day)

        date = min_date + datetime.timedelta(days=random.randint(0, (max_date - min_date).days))
        date_widget.model.set_value(f"{date.year}-{date.month:02d}-{date.day:02d}")
        self.assertEqual(date_widget.model._datetime.date(), date)

    async def test_time(self):
        with self._window.frame:
            with ui.HStack():
                time_widget = TimeWidget()
        await ui_test.human_delay(10)
        field = ui_test.WidgetRef(time_widget._time_field, "", self._window)
        await field.click()
        for _ in range(10):
            if time_widget._clock is not None:
                break
            await omni.kit.app.get_app().next_update_async()

        clock = time_widget._clock
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)

        old_hour = time_widget.model.hour
        old_minute = time_widget.model.minute

        if (old_hour < 12) != (hour < 12):
            day_widget = ui_test.WidgetRef(clock._day_down, "", self._window)
            await ui_test.emulate_mouse_move_and_click(day_widget.center)

        hour_sub_noon = hour - 12 if hour >= 12 else hour
        old_hour_sub_noon = old_hour - 12 if old_hour >= 12 else old_hour
        if hour_sub_noon >= old_hour_sub_noon:
            hour_widget = ui_test.WidgetRef(clock._hour_up, "", self._window)
            hour_diff = hour_sub_noon - old_hour_sub_noon
        else:
            hour_widget = ui_test.WidgetRef(clock._hour_down, "", self._window)
            hour_diff = old_hour_sub_noon - hour_sub_noon

        for _ in range(hour_diff):
            await ui_test.emulate_mouse_move_and_click(hour_widget.center)

        self.assertEqual(clock._half_day.text, "AM" if hour < 12 else "PM")
        self.assertEqual(clock._hour_0.text, str(hour // 10))
        self.assertEqual(clock._hour_1.text, str(hour % 10))

        if minute >= old_minute:
            minute_widget = ui_test.WidgetRef(clock._minute_up, "", self._window)
            minute_diff = minute - old_minute
        else:
            minute_widget = ui_test.WidgetRef(clock._minute_down, "", self._window)
            minute_diff = old_minute - minute

        for _ in range(minute_diff):
            await ui_test.emulate_mouse_move_and_click(minute_widget.center)

        self.assertEqual(clock._minute_0.text, str(minute // 10))
        self.assertEqual(clock._minute_1.text, str(minute % 10))

    async def test_zone(self):
        dt = datetime.datetime.now(tz=datetime.timezone.utc)
        zone_model = ZoneModel(dt)
        with self._window.frame:
            with ui.HStack():
                timezone_widget = TimezoneWidget(zone_model)
        await ui_test.human_delay(10)

        tz_idx = random.randint(0, len(timezone_widget._timezones) - 1)
        timezone_widget._timezone_combo.model.get_item_value_model(None, 0).set_value(tz_idx)
        self.assertEqual(
            zone_model.timezone,
            dt.astimezone(pytz.timezone(timezone_widget._timezones[tz_idx])).tzinfo
        )