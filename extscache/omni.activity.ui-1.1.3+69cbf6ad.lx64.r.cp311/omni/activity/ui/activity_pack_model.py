# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ActivityPackModel"]

from .activity_model import ActivityModel
from .activity_model import ActivityModelItem
from .activity_model import TimeRange
from collections import defaultdict
from functools import partial
from typing import List, Dict, Optional
import omni.ui as ui
import weakref


class ActivityPackModelItem(ui.AbstractItem):
    def __init__(self, parent: "ActivityPackModelItem", parent_model: "ActivityPackModel", packed=True):
        super().__init__()

        self._is_packed = packed

        self._time_ranges: List[TimeRange] = []

        self._children: List[ActivityPackModelItem] = []
        self._parent: ActivityPackModelItem = parent
        self._parent_model: ActivityPackModel = parent_model
        self._children_dirty = True

        # Time range when the item is active
        self._timerange_dirty = True
        self.__total_time: int = 0

        self.name_model = ui.SimpleStringModel("Empty")

    def destroy(self):
        for child in self._children:
            child.destroy()

        self._time_ranges = []
        self._children = []
        self._parent = None
        self._parent_model = None

    def extend_with_range(self, time_range: TimeRange):
        if not self._add_range(time_range):
            return False

        self._children_dirty = True

        return True

    def dirty(self):
        self._children_dirty = True
        self._timerange_dirty = True

    def get_children(self) -> List["ActivityPackModelItem"]:
        self._update_children()
        return self._children

    @property
    def time_range(self) -> List[TimeRange]:
        self._update_timerange()
        return self._time_ranges

    @property
    def total_time(self):
        """Return the time ranges when the item  was active"""
        if not self._timerange_dirty:
            # Recache
            _ = self.time_range

        return self.__total_time

    def _add_range(self, time_range: TimeRange):
        """
        Try to fit the given range to the current item. Return true if it's
        inserted.
        """
        if not self._time_ranges:
            self._time_ranges.append(time_range)
            return True

        # Check if it fits after the last
        last = self._time_ranges[-1]
        if last.end <= time_range.begin:
            self._time_ranges.append(time_range)
            return True

        # Check if it fits before the first
        first = self._time_ranges[0]
        if time_range.end <= first.begin:
            # prepend
            self._time_ranges.insert(0, time_range)
            return True

        ranges_count = len(self._time_ranges)
        if ranges_count <= 1:
            # Checked all the combinations
            return False

        def _binary_search(array, time_range):
            left = 0
            right = len(array) - 1

            while left <= right:
                middle = left + (right - left) // 2
                if array[middle].end < time_range.begin:
                    left = middle + 1
                elif array[middle].end > time_range.begin:
                    right = middle - 1
                else:
                    return middle
            return left - 1

        i = _binary_search(self._time_ranges, time_range) + 1

        if i > 0 and i < ranges_count:
            if time_range.end <= self._time_ranges[i].begin:
                # Insert after i-1 or before i
                self._time_ranges.insert(i, time_range)
                return True

        return False

    def _create_child(self):
        child = ActivityPackModelItem(weakref.proxy(self), self._parent_model)
        self._children.append(child)
        return child

    def _pack_range(self, time_range: TimeRange):
        if self._parent:  # Don't pack items if it's not a leaf
            for child in self._children:
                if child.extend_with_range(time_range):
                    # Successfully packed
                    return child

        # Can't be packed. Create a new one.
        child = self._create_child()
        child.extend_with_range(time_range)
        return child

    def _add_subchild(self, subchild: ActivityModelItem) -> Optional["ActivityPackModelItem"]:
        child = None

        if self._is_packed:
            subchild_time_range = subchild.time_range

            for time_range in subchild.time_range:
                added_to_child = self._pack_range(time_range)
                child = added_to_child

            self._parent_model._index_subitem_timegrange_count[subchild] = len(subchild_time_range)

        elif subchild not in self._parent_model._index_subitem_timegrange_count:
            subchild_time_range = subchild.time_range

            child = self._create_child()
            for time_range in subchild_time_range:
                child.extend_with_range(time_range)

            self._parent_model._index_subitem_timegrange_count[subchild] = len(subchild_time_range)

        return child

    def _search_time_range(self, time_range, low, high):
        # Classic binary search
        if high >= low:

            mid = (high + low) // 2

            # If element is present at the middle itself
            if self._time_ranges[mid].begin == time_range.begin:
                return mid

            # If element is smaller than mid, then it can only
            # be present in left subarray
            elif self._time_ranges[mid].begin > time_range.begin:
                return self._search_time_range(time_range, low, mid - 1)

            # Else the element can only be present in right subarray
            else:
                return self._search_time_range(time_range, mid + 1, high)

        else:
            # Element is not present in the array
            return None

    def _update_timerange(self):
        if not self._parent_model:
            return
        if not self._timerange_dirty:
            return
        self._timerange_dirty = False

        dirty_subitems = self._parent_model._index_dirty.pop(self, [])
        for subitem in dirty_subitems:
            time_range_count_done = self._parent_model._index_subitem_timegrange_count.get(subitem, 0)

            subitem_time_range = subitem.time_range
            # Check the last one. It could be changed
            if time_range_count_done:
                time_range = subitem_time_range[time_range_count_done - 1]
                i = self._search_time_range(time_range, 0, len(self._time_ranges) - 1)

                if i is not None and i < len(self._time_ranges) - 1:
                    if time_range.end > self._time_ranges[i + 1].begin:
                        # It's changed so it itersects the next range. Repack.
                        self._time_ranges.pop(i)
                        self._parent._pack_range(time_range)

            for time_range in subitem_time_range[time_range_count_done:]:
                self._parent._pack_range(time_range)

            self._parent_model._index_subitem_timegrange_count[subitem] = len(subitem_time_range)

    def _update_children(self):
        if not self._children_dirty:
            return
        self._children_dirty = False

        already_checked = set()
        for range in self._time_ranges:
            subitem = range.item
            if subitem in already_checked:
                continue
            already_checked.add(subitem)

            # Check child count
            child_count_already_here = self._parent_model._index_child_count.get(subitem, 0)

            subchildren = subitem.children
            if subchildren:
                # Don't touch already added
                for subchild in subchildren[child_count_already_here:]:
                    child = self._add_subchild(subchild)
                    self._parent_model._index[subchild] = child
                    subchild._packItem = child
                self._parent_model._index_child_count[subitem] = len(subchildren)

    def __repr__(self):
        return "<ActivityPackModelItem " + str(self._time_ranges) + ">"


class ActivityPackModel(ActivityModel):
    """Activity model that packs the given submodel"""

    def __init__(self, submodel: ActivityModel, **kwargs):
        self._submodel = submodel
        self._destroy_submodel = kwargs.pop("destroy_submodel", None)

        # Replace on_timeline_changed
        self.__on_timeline_changed_sub = self._submodel.subscribe_timeline_changed(
            partial(ActivityPackModel.__on_timeline_changed, weakref.proxy(self))
        )

        super().__init__(**kwargs)

        self._time_begin = self._submodel._time_begin
        self._time_end = self._submodel._time_end

        # Index for fast access
        self._index: Dict[ActivityModelItem, ActivityPackModelItem] = {}
        self._index_child_count: Dict[ActivityModelItem, int] = {}
        self._index_subitem_timegrange_count: Dict[ActivityModelItem, int] = {}
        self._index_dirty: Dict[ActivityPackModelItem, List[ActivityModelItem]] = defaultdict(list)

        self._root = ActivityPackModelItem(None, weakref.proxy(self), packed=False)

        self.__subscription = self._submodel.subscribe_item_changed_fn(
            partial(ActivityPackModel._subitem_changed, weakref.proxy(self))
        )

    def _subitem_changed(self, submodel, subitem):
        item = self._index.get(subitem, None)
        if item is None or item == self._root:
            # Root
            self._root.dirty()
            self._item_changed(None)
        elif item:
            self._dirty_item(item, subitem)
            self._item_changed(item)

    def _dirty_item(self, item, subitem):
        item.dirty()
        self._index_dirty[item].append(subitem)

    def destroy(self):
        super().destroy()

        self.__on_timeline_changed_sub = None
        self.__on_model_changed_sub = None

        self._index: Dict[ActivityModelItem, ActivityPackModelItem] = {}
        self._index_child_count: Dict[ActivityModelItem, int] = {}
        self._index_subitem_timegrange_count: Dict[ActivityModelItem, int] = {}
        self._index_dirty: Dict[ActivityPackModelItem, List[ActivityModelItem]] = defaultdict(list)

        self._root.destroy()

        if self._destroy_submodel:
            self._submodel.destroy()
        self._submodel = None
        self.__subscription = None

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        if self._submodel is None:
            return []
        if item is None:
            if not self._root.time_range:
                # Add the initial timerange once we have it
                self._submodel._root.update_flags()
                root_time_range = self._submodel._root.time_range
                if root_time_range:
                    self._root.extend_with_range(root_time_range[0])
                    self._root.dirty()

            children = self._root.get_children()
        else:
            children = item.get_children()

        return children

    def __on_timeline_changed(self):
        self._time_end = self._submodel._time_end

        if self._on_timeline_changed:
            self._on_timeline_changed()
