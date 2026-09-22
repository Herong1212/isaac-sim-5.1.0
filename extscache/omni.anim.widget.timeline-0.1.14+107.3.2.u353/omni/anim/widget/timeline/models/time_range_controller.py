import carb

from .range_item import RangeItem
from .range_model import RangeModel


class TimeRangeController:
    """
    Keeps view range within bounds of max range.
    If view range is changed to be outside max range, max range expands.
    If max range is changed to be smaller than view range, view range is clamped to full range.
    If max range is readonly - clamps view range to max range.
    """

    def __init__(self, model: RangeModel):
        self._model = model
        self._value_changed_sub = self._model.subscribe_item_changed_fn(self._on_model_item_change)

    def _on_model_item_change(self, model: RangeModel, changed_item: RangeItem):
        # carb.log_info(f"{self.__class__.__name__}._on_model_item_change({model}, {changed_item})")
        if changed_item == model.max_range:
            if changed_item.start > model.view_range.start or changed_item.end < model.view_range.end:
                model.begin_edit(model.view_range)
                model.view_range.start_model.as_float = max(model.max_range.start, model.view_range.start)
                model.view_range.end_model.as_float = min(model.max_range.end, model.view_range.end)
                model.end_edit(model.view_range)
        elif changed_item == model.view_range:
            if model.max_range.read_only:
                changed_item.start_model.set_value(
                    min(max(changed_item.start, model.max_range.start), model.max_range.end)
                )
                changed_item.end_model.set_value(max(min(changed_item.end, model.max_range.end), model.max_range.start))
            elif changed_item.start < model.max_range.start or changed_item.end > model.max_range.end:
                model.begin_edit(model.max_range)
                model.max_range.start_model.as_float = min(model.max_range.start, model.view_range.start)
                model.max_range.end_model.as_float = max(model.max_range.end, model.view_range.end)
                model.end_edit(model.max_range)
