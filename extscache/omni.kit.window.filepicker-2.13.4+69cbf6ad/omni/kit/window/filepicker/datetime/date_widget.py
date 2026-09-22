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
from .calendar import CalendarWidget
from .models import DateModel
from .style import default_datetime_window_style


class DateWidget:
    def __init__(self, model: DateModel = None, **kwargs):
        """
        Date Widget.
        Keyword Args:
        model (DateModel): Widget model.
        width (int): Input field width of widget. Default 80.
        style (dict): Widget style.
        """
        if model:
            self._model = model
        else:
            self._model = DateModel()

        width = kwargs.get("width", 80)
        self._style = kwargs.get("style", {})
        self._date_field = ui.StringField(self._model, width=width)
        self._model.add_begin_edit_fn(self._on_begin_edit)
        self._window = None
        self._calendar = None

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._model = None
        self._date_field = None
        if self._window:
            self._window.destroy()
            self._window = None
        if self._calendar:
            self._calendar.destroy()
            self._calendar = None

    @property
    def model(self):
        return self._model

    def _on_begin_edit(self, model):
        if self._window and self._window.visible:
            return

        flags = ui.WINDOW_FLAGS_POPUP | ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_MOVE | ui.WINDOW_FLAGS_NO_RESIZE
        # Create and show the window with fields and calendar
        self._window = ui.Window(
            "Calendar",
            flags=flags,
            auto_resize=True,
            padding_x=0,
            padding_y=0,
        )
        self._window.frame.style = default_datetime_window_style
        with self._window.frame:
            with ui.VStack(style=self._style):
                with ui.HStack(height=0):
                    date_field = ui.StringField(self._model, width=self._date_field.computed_content_width)
                    date_field.focus_keyboard()
                    blank_area = ui.Rectangle(name="blank")
                    blank_area.set_mouse_pressed_fn(self._on_blank_clicked)
                ui.Spacer(height=2)
                with ui.ZStack(height=0):
                    ui.Rectangle()
                    self._calendar = CalendarWidget(self._model)
        self._window.position_x = self._date_field.screen_position_x
        self._window.position_y = self._date_field.screen_position_y

    async def _destroy_window_async(self):
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._calendar:
            self._calendar.destroy()
            self._calendar = None
        if self._window:
            self._window.destroy()
            self._window = None

    def _on_blank_clicked(self, x, y, b, m):
        self._window.visible = False
        asyncio.ensure_future(self._destroy_window_async())
