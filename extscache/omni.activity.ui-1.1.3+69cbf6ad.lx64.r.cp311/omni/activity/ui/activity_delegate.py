# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ActivityDelegate"]

from ..bar._bar import AbstractActivityBarDelegate
from ..bar._bar import ActivityBar
from .activity_model import SECOND_MULTIPLIER
from .activity_pack_model import ActivityPackModelItem
from .activity_model import TimeRange
from functools import partial
from omni.ui import color as cl
from typing import List
import omni.ui as ui
import weakref
import carb


class ActivityBarDelegate(AbstractActivityBarDelegate):
    def __init__(self, ranges: List[TimeRange], hide_label: bool = False):
        super().__init__()
        self._hide_label = hide_label
        self._ranges = ranges

    def get_label(self, index):
        if self._hide_label:
            # Can't return None because it's derived from C++
            return ""
        else:
            # use short name
            item = self._ranges[index].item
            name = item.name_model.as_string
            short_name = name.split("/")[-1]
            # the number of children
            children_num = len(item.children)
            label_text = short_name if children_num == 0 else short_name + " (" + str(children_num) + ")"
            return label_text

    def get_tooltip_text(self, index):
        time_range = self._ranges[index]
        elapsed = time_range.end - time_range.begin
        item = time_range.item
        name = item.name_model.as_string
        tooltip_name = time_range.metadata.get("name", None) or name
        if name in ["Read", "Load", "Resolve"]:
            # the size of children
            size = item.children_size * 0.000001
        else:
            size = time_range.item.size * 0.000001
        return f"{tooltip_name}\n{elapsed / SECOND_MULTIPLIER:.2f}s\n{size:.2f} MB"


class ActivityDelegate(ui.AbstractItemDelegate):
    """
    The delegate for the TreeView for the activity chart. Instead of text, it
    shows the activity on the timeline.
    """

    def __init__(self, **kwargs):
        super().__init__()

        # Called to collapse/expand
        self._on_expand = kwargs.pop("on_expand", None)

        # Map between the range and range delegate
        self._activity_bar_map = {}

        self._activity_bar = None

    def destroy(self):
        self._activity_bar_map = {}
        self._activity_bar = None

    def build_branch(self, model, item, column_id, level, expanded):  # pragma: no cover
        """Create a branch widget that opens or closes subtree"""
        pass

    def __on_double_clicked(self, weak_item, weak_range_item, x, y, button, modifier):
        if button != 0:
            return

        if not self._on_expand:
            return

        item = weak_item()
        if not item:
            return

        range_item = weak_range_item()
        if not range_item:
            return

        # shift + double click will expand all
        recursive = True if modifier & carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT else False
        self._on_expand(item, range_item, recursive)

    def __on_selection(self, time_range, model, item_id):
        if item_id is None:
            return

        item = time_range[item_id].item
        if not item:
            return

        model.selection = item

    def select_range(self, item, model):
        model.selection = item
        if item in self._activity_bar_map:
            (_activity_bar, i) = self._activity_bar_map[item]
            _activity_bar.selection = i

    def build_widget(self, model, item, column_id, level, expanded):
        """Create a widget per item"""
        if not isinstance(item, ActivityPackModelItem):
            return

        if column_id != 0:
            return

        time_range = item.time_range
        if time_range:
            first_range = time_range[0]
            first_item = first_range.item
            with ui.VStack():
                if level == 1:
                    ui.Spacer(height=2)
                _activity_bar = ActivityBar(
                    time_limit=(model._time_begin, model._time_end),
                    time_ranges=[(t.begin, t.end) for t in time_range],
                    colors=[t.metadata["color"] for t in time_range],
                    delegate=ActivityBarDelegate(time_range),
                    height=25,
                    mouse_double_clicked_fn=partial(
                        ActivityDelegate.__on_double_clicked,
                        weakref.proxy(self),
                        weakref.ref(item),
                        weakref.ref(first_item),
                    ),
                    selection_changed_fn=partial(ActivityDelegate.__on_selection, weakref.proxy(self), time_range, model),
                )
            for i, t in enumerate(time_range):
                self._activity_bar_map[t.item] = (_activity_bar, i)
