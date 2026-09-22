import typing

from omni import ui

from .. import widgets
from ..models import RangeModel, TimelineGridModel
from .timeline_content_delegate import TimelineContentDelegate


class TimelineViewDelegate:
    def __init__(
        self,
        timeline_content_delegate: typing.Optional[TimelineContentDelegate] = None,
        timeline_gutter_delegate: typing.Optional[TimelineContentDelegate] = None,
    ):
        self._scrubber: widgets.Scrubber = None
        self._timeline_widget: widgets.TimelineWidget = None
        self._frame_range_widget: widgets.RangeWidget = None
        self._timeline_content_delegate = timeline_content_delegate or TimelineContentDelegate()
        self._timeline_gutter_delegate = timeline_gutter_delegate

    def destroy(self):
        if self._scrubber:
            self._scrubber.destroy()
            self._scrubber = None
        if self._timeline_widget:
            self._timeline_widget.destroy()
            self._timeline_widget = None
        if self._timeline_content_delegate:
            self._timeline_content_delegate.destroy()
            self._timeline_content_delegate = None
        if self._timeline_gutter_delegate:
            self._timeline_gutter_delegate.destroy()
            self._timeline_gutter_delegate = None
        if self._frame_range_widget:
            self._frame_range_widget.destroy()
            self._frame_range_widget = None

    def resize(self, width: float):
        if self._frame_range_widget:
            self._frame_range_widget.on_width_changed(width)
        self.update()

    def update(self):
        if self._scrubber:
            self._scrubber.update()
        if self._timeline_widget:
            self._timeline_widget.update()
        if self._timeline_content_delegate:
            self._timeline_content_delegate.update()
        if self._timeline_gutter_delegate:
            self._timeline_gutter_delegate.update()

    def build_scrubber(
        self,
        range_model: RangeModel,
        timeline_grid_model: TimelineGridModel,
        time_display_model: ui.SimpleStringModel,
    ):
        self._scrubber = widgets.Scrubber(
            range_model=range_model,
            timeline_grid_model=timeline_grid_model,
            time_display_model=time_display_model,
        )

    def build_timeline_widget(
        self,
        range_model: RangeModel,
        timeline_grid_model: TimelineGridModel,
        time_display_model: ui.SimpleStringModel,
    ):
        self._timeline_widget = widgets.TimelineWidget(
            range_model=range_model,
            timeline_grid_model=timeline_grid_model,
            timeline_gutter_delegate=self._timeline_gutter_delegate,
            time_display_model=time_display_model,
        )

    def build_timeline_content(
        self,
        range_model: RangeModel,
        timeline_grid_model: TimelineGridModel,
        time_display_model: ui.SimpleStringModel,
    ):
        if self._timeline_content_delegate:
            self._timeline_content_delegate.build(
                range_model=range_model, timeline_grid_model=timeline_grid_model, time_display_model=time_display_model
            )

    def build_frame_range_widget(
        self,
        range_model: RangeModel,
        timeline_grid_model: TimelineGridModel,
        time_display_model: ui.SimpleStringModel,
    ):
        self._frame_range_widget = widgets.RangeWidget(range_model, time_display_model=time_display_model)
