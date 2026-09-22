# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui
from .models import TimeModel


class ClockWidget:
    """
    Represents a clock to show hour minute and second
    Keyword Args:
        model (TimeModel): Widget model.
        width (int): Widget width. Default 160.
        height (int): Widget height. Default 32.
    """

    def __init__(
        self,
        model: TimeModel,
        width: int = 160,
        height: int = 32,
    ):
        self._model = model
        self._time_changing = False

        with ui.HStack(width=width, height=height, spacing=2):
            self._hour_0 = ui.Label("0", name="number", width=0, height=0)
            self._hour_1 = ui.Label("0", name="number", width=0, height=0)

            # Spin for hour
            with ui.VStack():
                ui.Spacer()
                self._hour_up = ui.Triangle(
                    name="spinner",
                    width=14,
                    height=10,
                    alignment=ui.Alignment.CENTER_TOP,
                    mouse_pressed_fn=(lambda x, y, key, m: self._on_hour_clicked(key, 1)),
                )
                ui.Spacer(height=6)
                self._hour_down = ui.Triangle(
                    name="spinner",
                    width=14,
                    height=10,
                    alignment=ui.Alignment.CENTER_BOTTOM,
                    mouse_pressed_fn=(lambda x, y, key, m: self._on_hour_clicked(key, -1)),
                )
                ui.Spacer()

            ui.Spacer(width=4)
            # Colon between hour and minute
            with ui.VStack(width=8):
                ui.Spacer()
                ui.Circle(name="clock", width=4, height=4)
                ui.Spacer()
                ui.Circle(name="clock", width=4, height=4)
                ui.Spacer()

            # 2 digits for minute
            self._minute_0 = ui.Label("0", name="number", width=0, height=0)
            self._minute_1 = ui.Label("0", name="number", width=0, height=0)

            # Spin for minute
            with ui.VStack():
                ui.Spacer()
                self._minute_up = ui.Triangle(
                    name="spinner",
                    width=14,
                    height=10,
                    alignment=ui.Alignment.CENTER_TOP,
                    mouse_pressed_fn=(lambda x, y, key, m: self._on_minute_clicked(key, 1)),
                )
                ui.Spacer(height=6)
                self._minute_down = ui.Triangle(
                    name="spinner",
                    width=14,
                    height=10,
                    alignment=ui.Alignment.CENTER_BOTTOM,
                    mouse_pressed_fn=(lambda x, y, key, m: self._on_minute_clicked(key, -1)),
                )
                ui.Spacer()

            # Lable for half-day
            with ui.VStack():
                ui.Spacer(height=ui.Percent(50))
                self._half_day = ui.Label("PM", name="morning", width=0)

            # Spin for half-day
            with ui.VStack():
                ui.Spacer(height=ui.Percent(50))
                ui.Spacer(height=3)
                self._day_down = ui.Triangle(
                    name="spinner",
                    width=14,
                    height=10,
                    alignment=ui.Alignment.CENTER_BOTTOM,
                    mouse_pressed_fn=(lambda x, y, key, m: self._on_half_day_clicked(key)),
                )

        self._on_time_changed(None)
        self._model.add_value_changed_fn(self._on_time_changed)

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._model = None

    def _on_hour_clicked(self, key, step):
        if key == 0:
            self._model.hour += step

    def _on_minute_clicked(self, key, step):
        if key == 0:
            self._model.minute += step

    def _on_half_day_clicked(self, key):
        if key != 0:
            return

        hour = self._model.hour
        if hour < 12:
            hour += 12
        else:
            hour -= 12

        self._model.hour = hour

    @property
    def model(self):
        return self._model

    def _on_time_changed(self, model):
        if self._time_changing:
            return
        self._time_changing = True
        self._hour_0.text = str(self._model.hour // 10)
        self._hour_1.text = str(self._model.hour % 10)
        self._minute_0.text = str(self._model.minute // 10)
        self._minute_1.text = str(self._model.minute % 10)
        self._half_day.text = "AM" if self._model.hour < 12 else "PM"
        self._time_changing = False
