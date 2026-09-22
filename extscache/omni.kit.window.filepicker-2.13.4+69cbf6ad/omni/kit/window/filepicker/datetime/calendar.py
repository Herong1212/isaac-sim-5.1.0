# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import calendar
import omni.ui as ui
from .models import DateModel
from .style import select_circle_style, unselect_circle_style


class CalendarWidget:
    """
    Represents a calendar to show year month and day
    Keyword Args:
        model (DateModel): Widget model.
        width (int): Widget width. Default 160.
        height (int): Widget height. Default 140.
        year_min (int): min year in year combobox. default 2000,
        year_max (int): max year in year combobox. default 2050,
    """

    def __init__(
        self,
        model: DateModel,
        width: int = 175,
        height: int = 195,
        year_min: int = 2000,
        year_max: int = 2050
    ):
        self._model = model
        self._year_min = year_min
        self._year_max = year_max
        self._year_list = [str(year) for year in range(year_min, year_max)]
        self._month_list = calendar.month_name[1:]
        self._calendar = calendar.Calendar(calendar.SUNDAY)
        self._day_buttons = []
        self._week_days = None
        self._date_changing = False

        combox_height = 20
        self._cell_width = width / 7
        self._cell_height = (height - combox_height) / 7

        with ui.VStack(width=width, height=height, spacing=0):
            # Month and Year
            with ui.HStack(height=combox_height):
                self._month_combo = ui.ComboBox(0, *self._month_list, name="month", width=85)
                ui.Spacer()
                self._year_combo = ui.ComboBox(0, *self._year_list, name="year", width=60)
                self._month_combo.model.add_item_changed_fn(self._on_month_changed)
                self._year_combo.model.add_item_changed_fn(self._on_year_changed)
            # Week days
            self._week_days = ui.Frame()
            self._week_days.set_build_fn(self._build_week_days)

        self._on_date_changed(None)
        self._model.add_value_changed_fn(self._on_date_changed)

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._model = None
        self._week_days = None
        self._day_buttons.clear()

    def _build_week_days(self):
        self._day_buttons.clear()
        # add None for day 0, so the N day's button is buttons[N]
        self._day_buttons.append(None)
        with ui.VGrid(column_count=7, row_height=self._cell_height):
            week_day = ["S", "M", "T", "W", "T", "F", "S"]
            for i in range(7):
                ui.Label(week_day[i], name="week", alignment=ui.Alignment.CENTER)

            for day in self._calendar.itermonthdays(self._model.year, self._model.month):
                if day > 0:
                    with ui.ZStack(alignment=ui.Alignment.CENTER):
                        button = ui.Circle(
                            name="day",
                            alignment=ui.Alignment.CENTER,
                            mouse_released_fn=lambda x, y, b, f, d=day: self._on_day_changed(b, d)
                        )
                        ui.Label(str(day), name="week", alignment=ui.Alignment.CENTER)
                    self._day_buttons.append(button)
                else:
                    ui.Spacer()

        self._day_buttons[self._model.day].set_style(select_circle_style)

    def _on_month_changed(self, model, item):
        selected_month = model.get_item_value_model().as_int + 1
        if self._model.month == selected_month:
            return
        self._model.month = selected_month
        self._week_days.rebuild()

    def _on_year_changed(self, model, item):
        selected_year = model.get_item_value_model().as_int + self._year_min
        if self._model.year == selected_year:
            return
        self._model.year = selected_year
        self._week_days.rebuild()

    def _on_day_changed(self, b, day: int):
        if b != 0:
            return
        if self._model.day == day:
            return
        self._day_buttons[self._model.day].set_style(unselect_circle_style)
        self._day_buttons[day].set_style(select_circle_style)
        self._model.day = day

    @property
    def model(self):
        return self._model

    def _on_date_changed(self, model):
        if self._date_changing:
            return
        self._date_changing = True

        if self._model.year > self._year_max:
            self._model.year = self._year_max
        if self._model.year < self._year_min:
            self._model.year = self._year_min

        self._month_combo.model.get_item_value_model().set_value(self._model.month - 1)
        self._year_combo.model.get_item_value_model().set_value(self._model.year - self._year_min)
        self._week_days.rebuild()
        self._date_changing = False
