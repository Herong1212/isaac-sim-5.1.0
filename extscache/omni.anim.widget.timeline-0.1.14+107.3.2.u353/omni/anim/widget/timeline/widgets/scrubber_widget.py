import asyncio

import omni.kit.app
from omni import ui

from ..models import RangeModel, TimeDisplayValueModel, TimelineGridModel
from .timeline_widget_style import TimelineWidgetStyle


class Scrubber:
    def __init__(
        self,
        range_model: RangeModel,
        timeline_grid_model: TimelineGridModel,
        time_display_model: ui.SimpleStringModel = None,
    ):
        self._range_model = range_model
        self._timeline_grid_model = timeline_grid_model
        self._time_display_model = time_display_model

        self._style = TimelineWidgetStyle.get_style()

        self._frame_number_label = None
        self._frame_number_placer = None
        self._update_task: asyncio.Task = None

        if not self._range_model.current_time_model:
            raise ValueError("Range model has no current_time_model defined.")

        self._current_time_display_model = TimeDisplayValueModel(
            parent_model=self._range_model.current_time_model,
            time_display_model=self._time_display_model,
            fps_model=self._range_model.fps_model,
        )
        self._number_of_digits = self._get_number_of_digits(self._current_time_display_model.as_string)
        self._frame_number_width = self._get_frame_number_width(self._number_of_digits)

        self._placer = ui.Placer()
        with self._placer:
            self._ui_frame = ui.Frame(
                build_fn=self._build_ui, style=self._style, style_type_name_override="TimelineWidget.Scrubber"
            )

        self._current_time_sub = self._range_model.current_time_model.subscribe_value_changed_fn(
            self._on_current_time_changed
        )

        # initial update task on build
        self._update_task = asyncio.ensure_future(self._async_update())

    def destroy(self):
        if self._update_task:
            self._update_task.cancel()
            self._update_task = None
        self._current_time_display_model = None
        self._current_time_sub = None

        if self._placer:
            self._placer.destroy()
            self._placer = None
        if self._frame_number_placer:
            self._frame_number_placer.destroy()
            self._frame_number_placer = None

        self._frame_number_rectangle = None

    def __del__(self):
        self.destroy()

    def _build_ui(self):
        with ui.ZStack():
            ui.Rectangle(
                width=max(2, self._timeline_grid_model.frame_width),
                style_type_name_override="TimelineWidget.Scrubber.FrameShadowRectangle",
            )
            ui.Line(
                style_type_name_override="TimelineWidget.Scrubber.FrameLine",
                alignment=ui.Alignment.LEFT,
            )
            self._frame_number_placer = ui.Placer(
                offset_x=ui.Pixel(-self._frame_number_width * 0.5 + 0.5),
                width=self._frame_number_width,
            )
            with self._frame_number_placer:
                with ui.ZStack(content_clipping=True):
                    with ui.VStack():
                        ui.Rectangle(
                            height=14,
                            style_type_name_override="TimelineWidget.Scrubber",
                        )
                        ui.Triangle(
                            height=6,
                            style_type_name_override="TimelineWidget.Scrubber",
                            alignment=ui.Alignment.CENTER_BOTTOM,
                        )
                    self._frame_number_label = ui.Label(
                        self._current_time_display_model.get_value_as_string(),
                        style_type_name_override="TimelineWidget.FrameNumberLabel",
                        alignment=ui.Alignment.CENTER_TOP,
                    )
        self.update()

    def _on_current_time_changed(self, value_model: ui.AbstractValueModel):
        if not self._update_task or self._update_task.done():
            self._update_task = asyncio.ensure_future(self._async_update())

    @staticmethod
    def _get_frame_number_width(number_of_digits: int = 3):
        return max(number_of_digits, 3) * TimelineWidgetStyle.FONT_SIZE * 0.6

    @staticmethod
    def _get_number_of_digits(word):
        return max(3, len(word))

    async def _async_update_frame_number_width(self):
        number_of_digits = self._get_number_of_digits(self._current_time_display_model.as_string)
        if number_of_digits == self._number_of_digits:
            # No change
            return

        self._number_of_digits = number_of_digits

        if not self._frame_number_placer:
            # Not built yet.
            return

        await omni.kit.app.get_app().next_update_async()  # if not awaited the offset of the label can break
        self._frame_number_width = self._get_frame_number_width(self._number_of_digits)
        width = ui.Pixel(self._frame_number_width)
        self._frame_number_placer.width = width
        self._frame_number_placer.offset_x = ui.Pixel(-self._frame_number_width * 0.5 + 0.5)

    def get_frame_number(self):
        return self._current_time_display_model.as_float

    def _update_label(self):
        if not self._frame_number_label:
            return
        self._frame_number_label.text = self._current_time_display_model.get_value_as_string()

    def update(self):
        """Update when resizing window."""
        self._update_visibility()
        self._update_offset()

    def _update_visibility(self):
        if self._range_model.view_range.length == 0:
            self._ui_frame.visible = False
        else:
            self._ui_frame.visible = True

    def _update_offset(self):
        current_time = self._range_model.current_time
        self._placer.offset_x = self._timeline_grid_model.transform_timeline_to_position(current_time)

    async def _async_update(self):
        """Async update when updating from time change."""
        self._update_visibility()
        self._update_label()
        await self._async_update_frame_number_width()
        self._update_offset()
        self._update_task = None
