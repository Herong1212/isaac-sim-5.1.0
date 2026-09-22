# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import datetime
import calendar
import omni.ui as ui

try:
    import dateutil.parser
    date_parser = dateutil.parser.parse
except ModuleNotFoundError:
    date_parser = datetime.datetime.fromisoformat

class DateModel(ui.AbstractValueModel):
    def __init__(self, _datetime: datetime.datetime = None):
        super().__init__()
        if _datetime:
            self._datetime = _datetime
        else:
            self._datetime = datetime.datetime.today()

    def set_value(self, dt_string: str):
        try:
            _datetime = date_parser(dt_string)
        except ValueError:
            return
        self._datetime = self._datetime.replace(year=_datetime.year, month=_datetime.month, day=_datetime.day)
        self._value_changed()

    def get_value_as_string(self):
        return self._datetime.strftime("%Y-%m-%d")

    @property
    def year(self):
        return self._datetime.year

    @year.setter
    def year(self, value):
        day = self._adjust_day(value, self._datetime.month)
        self._datetime = self._datetime.replace(year=value, day=day)
        self._value_changed()

    @property
    def month(self):
        return self._datetime.month

    @month.setter
    def month(self, value):
        day = self._adjust_day(self._datetime.year, value)
        self._datetime = self._datetime.replace(month=value, day=day)
        self._value_changed()

    @property
    def day(self):
        return self._datetime.day

    @day.setter
    def day(self, value):
        self._datetime = self._datetime.replace(day=value)
        self._value_changed()

    def _adjust_day(self, year, month):
        _, lastday = calendar.monthrange(year, month)
        cur_day = self._datetime.day
        return lastday if cur_day > lastday else cur_day


class TimeModel(ui.AbstractValueModel):
    def __init__(self, _datetime: datetime.datetime = None):
        super().__init__()
        if _datetime:
            self._datetime = _datetime
        else:
            self._datetime = datetime.datetime.now()

    def set_value(self, dt_string: str):
        try:
            _datetime = date_parser(dt_string)
        except ValueError:
            return
        self._datetime = self._datetime.replace(hour=_datetime.hour, minute=_datetime.minute, second=_datetime.second)
        self._value_changed()

    def get_value_as_string(self):
        return self._datetime.strftime("%H:%M:%S")

    @property
    def hour(self):
        return self._datetime.hour

    @hour.setter
    def hour(self, value):
        if value < 0:
            value = 23
        if value > 23:
            value = 0

        self._datetime = self._datetime.replace(hour=value)
        self._value_changed()

    @property
    def minute(self):
        return self._datetime.minute

    @minute.setter
    def minute(self, value):
        if value < 0:
            value = 59
        if value > 59:
            value = 0

        self._datetime = self._datetime.replace(minute=value)
        self._value_changed()

    @property
    def second(self):
        return self._datetime.second

    @second.setter
    def second(self, value):
        if value < 0:
            value = 59
        if value > 59:
            value = 0

        self._datetime = self._datetime.replace(second=value)
        self._value_changed()


class ZoneModel(ui.AbstractValueModel):
    def __init__(self, _datetime: datetime.datetime = None):
        super().__init__()
        if _datetime:
            self._datetime = _datetime
        else:
            self._datetime = datetime.datetime.now(tz=datetime.timezone.utc)

    def set_value(self, tz: datetime.timezone):
        self._datetime = self._datetime.astimezone(tz=tz)
        self._value_changed()

    def get_value_as_string(self):
        return self._datetime.tzname()

    @property
    def timezone(self):
        return self._datetime.tzinfo
