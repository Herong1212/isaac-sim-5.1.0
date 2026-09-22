import typing

import carb
import carb.tokens
from omni import ui

from .range_item import RangeItem
from .time_units import TimeUnits
from .time_value_model import TimeValueModel


class RangeRootItem(ui.AbstractItem):
    def __init__(
        self,
        view_range_item: RangeItem,
        fps_model: ui.SimpleFloatModel,
        max_range_item: typing.Optional[RangeItem] = None,
        current_time_model: typing.Optional[TimeValueModel] = None,
    ) -> None:
        super().__init__()
        self.view_range = view_range_item
        self.max_range = max_range_item
        self.current_time_model = current_time_model
        self.fps_model = fps_model
        if self.max_range:
            self._children = (self.max_range, self.view_range)
        else:
            self._children = (self.view_range,)

    def __repr__(self):
        return f"<{self.__class__.__name__}(current_time={self.current_time_model}, fps={self.fps_model}, children={self._children})>"

    @property
    def children(self) -> typing.Tuple[RangeItem, ...]:
        return self._children


class RangeModel(ui.AbstractItemModel):
    """
    A Range model with a view range and optional maximum range for limiting the view range.
    Time is represented in Seconds by default.
    Default fps is 30.
    """

    def __init__(
        self,
        start: float = 0,
        end: float = 100,
        min: typing.Optional[float] = None,
        max: typing.Optional[float] = None,
        time_units: str = TimeUnits.SECONDS,
        current_time: typing.Union[float, TimeValueModel] = 0,
        fps: typing.Union[float, ui.SimpleFloatModel] = 30,
        max_range_read_only=False,
    ):
        super().__init__()
        self._time_units = time_units

        current_time_model = self._init_current_time_model(current_time)
        fps_model = self._init_fps_model(fps)
        view_range_item = self._init_view_range_item(start, end, time_units, fps_model)
        max_range_item = self._init_max_range_item(min, max, time_units, fps_model, max_range_read_only)

        self._root_item = self._init_root_item(current_time_model, fps_model, view_range_item, max_range_item)
        self._editing = None

    def _init_current_time_model(self, current_time: typing.Union[float, TimeValueModel]) -> TimeValueModel:
        if isinstance(current_time, TimeValueModel):
            return current_time
        if isinstance(current_time, (float, int)):
            return TimeValueModel(value=current_time, time_units=self._time_units)
        raise ValueError(f"Invalid type for current_time: {type(current_time)}")

    def _init_fps_model(self, fps: typing.Union[float, ui.SimpleFloatModel]) -> ui.SimpleFloatModel:
        if isinstance(fps, ui.SimpleFloatModel):
            return fps
        if isinstance(fps, (float, int)):
            return ui.SimpleFloatModel(default_value=fps)
        raise ValueError(f"Invalid type for current_time: {type(fps)}")

    def _init_root_item(
        self,
        current_time_model: TimeValueModel,
        fps_model: ui.SimpleFloatModel,
        view_range_item: RangeItem,
        max_range_item: typing.Optional[RangeItem],
    ) -> RangeRootItem:
        return RangeRootItem(
            current_time_model=current_time_model,
            fps_model=fps_model,
            view_range_item=view_range_item,
            max_range_item=max_range_item,
        )

    def _init_view_range_item(
        self,
        start: float,
        end: float,
        time_units: TimeUnits,
        fps: typing.Optional[typing.Union[float, ui.SimpleFloatModel]],
    ) -> RangeItem:
        return RangeItem("View Range", start=start, end=end, time_units=time_units, fps=fps)

    def _init_max_range_item(
        self,
        start: float,
        end: float,
        time_units: TimeUnits,
        fps: typing.Optional[typing.Union[float, ui.SimpleFloatModel]],
        read_only: bool = True,
    ) -> typing.Optional[RangeItem]:
        if start is None or end is None:
            return None
        return RangeItem("Max Range", start=start, end=end, time_units=time_units, fps=fps, read_only=read_only)

    @property
    def fps(self) -> float:
        if self._root_item.fps_model:
            return self._root_item.fps_model.as_float
        return 0

    @property
    def fps_model(self) -> ui.SimpleFloatModel:
        return self._root_item.fps_model

    @property
    def time_units(self) -> str:
        return self._time_units

    @property
    def current_time(self) -> typing.Optional[float]:
        if not self._root_item.current_time_model:
            return None
        return self._root_item.current_time_model.as_float

    @current_time.setter
    def current_time(self, value: float):
        if not self._root_item.current_time_model:
            raise ValueError("No current time model defined.")
        self._root_item.current_time_model.as_float = value

    @property
    def current_time_model(self) -> typing.Optional[TimeValueModel]:
        return self._root_item.current_time_model

    @property
    def max_range(self) -> typing.Optional[RangeItem]:
        return self._root_item.max_range

    @property
    def view_range(self) -> RangeItem:
        return self._root_item.view_range

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._children = None

    @property
    def is_editing(self) -> bool:
        return bool(self._editing)

    def begin_edit(self, item: RangeItem) -> None:
        carb.log_verbose(f"Begin edit {item}")
        self._editing = item

    def end_edit(self, item: RangeItem) -> None:
        carb.log_verbose(f"End edit {item}")
        self._editing = None
        self._item_changed(item)

    def can_item_have_children(self, parent_item: typing.Optional[RangeItem] = None) -> bool:
        if parent_item is None:
            return True
        return False

    def get_item_children(self, parent_item: typing.Optional[RangeItem] = None) -> typing.Iterable[RangeItem]:
        if parent_item is None:
            return self._root_item.children
        return ()

    def get_item_value_model(
        self, item: typing.Optional[RangeItem] = None, column_id: int = 0
    ) -> typing.Optional[ui.AbstractValueModel]:
        if item is None:
            if column_id == 0:
                return self._root_item.current_time_model
            if column_id == 1:
                return self._root_item.fps_model
            return None

        if column_id == 0:
            return item.name_model
        if column_id == 1:
            return item.start_model
        if column_id == 2:
            return item.end_model

        return None

    def get_item_value_model_count(self, item: typing.Optional[RangeItem] = None) -> int:
        """
        Returns the number of columns this model item contains.
        """
        if item is None:
            return 3
        return item.value_model_count

    def __repr__(self):
        return f"<{self.__class__.__name__}{self._root_item}>"

    @property
    def zoomed(self) -> bool:
        if not self.max_range:
            return False
        return self.start != self.min or self.end != self.max

    @property
    def start(self) -> float:
        return self.view_range.start

    @start.setter
    def start(self, value):
        self.view_range.start_model.set_value(value)

    @property
    def end(self) -> float:
        return self.view_range.end

    @end.setter
    def end(self, value: float):
        self.view_range.end_model.set_value(value)

    def set_range(self, start: float, end: float):
        if start > end:
            raise ValueError(f"View start is greater than view end: {start}, {end}")

        self.start = start
        self.end = end
        self._item_changed(self.view_range)

    def set_max_range(self, start: float, end: float):
        if start > end:
            raise ValueError(f"Scene start is greater than view end: {start}, {end}")
        if self.max_range is None:
            raise ValueError(f"Full range not defined in model.")
        self.min = start
        self.max = end
        self._item_changed(self.max_range)

    @property
    def min(self) -> typing.Optional[float]:
        if self.max_range:
            return self.max_range.start

    @min.setter
    def min(self, value: float):
        if self.max_range:
            self.max_range.start_model.set_value(value)

    @property
    def max(self) -> typing.Optional[float]:
        if self.max_range:
            return self.max_range.end

    @max.setter
    def max(self, value: float):
        if self.max_range:
            self.max_range.end_model.set_value(value)

    @property
    def is_valid(self):
        return all(
            (
                self.view_range.is_valid,
                (
                    self.max_range is None
                    or (
                        self.max_range.is_valid
                        and self.view_range.start >= self.max_range.start
                        and self.view_range.end <= self.max_range.end
                    )
                ),
            )
        )
