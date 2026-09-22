# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import asyncio
import omni.kit.app
import omni.ui as ui
from .clock import ClockWidget
from .models import TimeModel
from .style import default_datetime_window_style


class TimeWidget:
    def __init__(self, model: TimeModel = None, **kwargs):
        """
        Time Widget.
        Keyword Args:
        model (TimeModel): Widget model.
        width (int): Input field width of widget. Default 60.
        style (dict): Widget style.
        """
        if model:
            self._model = model
        else:
            self._model = TimeModel()

        width = kwargs.get("width", 60)
        self._style = kwargs.get("style", {})
        self._time_field = ui.StringField(self._model, width=width)
        self._model.add_begin_edit_fn(self._on_begin_edit)
        self._window = None
        self._clock = None

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._model = None
        self._time_field = None
        if self._window:
            self._window.destroy()
            self._window = None
        if self._clock:
            self._clock.destroy()
            self._clock = None

    @property
    def model(self):
        return self._model

    def _on_begin_edit(self, model):
        if self._window and self._window.visible:
            return

        # Create and show the window with fields and calendar
        flags = ui.WINDOW_FLAGS_POPUP | ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_MOVE | ui.WINDOW_FLAGS_NO_RESIZE
        self._window = ui.Window(
            "Clock",
            flags=flags,
            auto_resize=True,
            padding_x=0,
            padding_y=0,
        )
        self._window.frame.style = default_datetime_window_style
        with self._window.frame:
            with ui.VStack(style=self._style):
                with ui.HStack(height=0):
                    time_field = ui.StringField(self._model, width=self._time_field.computed_content_width)
                    time_field.focus_keyboard()
                    blank_area = ui.Rectangle(name="blank")
                    blank_area.set_mouse_pressed_fn(self._on_blank_clicked)
                ui.Spacer(height=4)
                with ui.ZStack():
                    ui.Rectangle()
                    self._clock = ClockWidget(self._model)
        self._window.position_x = self._time_field.screen_position_x
        self._window.position_y = self._time_field.screen_position_y

    async def _destroy_window_async(self):
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._clock:
            self._clock.destroy()
            self._clock = None
        if self._window:
            self._window.destroy()
            self._window = None

    def _on_blank_clicked(self, x, y, b, m):
        self._window.visible = False
        asyncio.ensure_future(self._destroy_window_async())
