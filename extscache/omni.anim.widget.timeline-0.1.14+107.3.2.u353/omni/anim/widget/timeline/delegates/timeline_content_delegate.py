import math

from omni import ui

from .. import models


class TimelineContentDelegate:
    def __init__(self):
        self._ui_container: ui.Container = None
        self._range_model: models.RangeModel = None
        self._timeline_grid_model: models.TimelineGridModel = None
        self._grid_frame: ui.Frame = None
        self._content_frame: ui.Frame = None
        self._time_display_model = None

    def build(
        self,
        range_model: models.RangeModel,
        timeline_grid_model: models.TimelineGridModel,
        time_display_model: ui.SimpleStringModel,
    ):
        self._range_model = range_model
        self._timeline_grid_model = timeline_grid_model
        self._time_display_model = time_display_model
        self._ui_container = ui.ZStack()
        with self._ui_container:
            self._background = ui.Frame(build_fn=self._build_background)
            self._grid_frame = ui.Frame(build_fn=self._build_grid)
            self._content_frame = ui.Frame(build_fn=self._build_content)

    def _build_background(self):
        ui.Rectangle()

    def _build_content(self):
        pass

    def _build_grid(self):
        if self._timeline_grid_model.large_tick_step == 0:
            return
        with ui.HStack():
            ui.Spacer(width=self._timeline_grid_model.frac_big_tick_size)
            for _ in range(
                0,
                math.ceil(self._range_model.view_range.length_inclusive),
                math.ceil(self._timeline_grid_model.large_tick_step),
            ):
                ui.Line(
                    width=self._timeline_grid_model.large_tick_width,
                    style_type_name_override="TimelineWidget.Grid.Line",
                    alignment=ui.Alignment.LEFT,
                )

    def _update_content(self):
        pass

    def update(self):
        if self._grid_frame:
            self._grid_frame.rebuild()
        if self._content_frame:
            self._update_content()

    def destroy(self):
        self.timeline_grid_model = None
        self._timeline_grid_model = None
        self._time_display_model = None
        if self._ui_container:
            self._ui_container.clear()
            self._ui_container.destroy()
            self._ui_container = None
