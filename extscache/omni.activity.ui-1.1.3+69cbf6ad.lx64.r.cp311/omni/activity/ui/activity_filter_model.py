# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ActivityFilterModel"]

import weakref
from dataclasses import dataclass
from typing import Dict, List, Set
from functools import partial
import omni.ui as ui
from .activity_model import ActivityModel


class ActivityFilterModel(ui.AbstractItemModel):
    """
    The model that takes the source model and filters out the items that are
    outside of the given time range.
    """

    def __init__(self, source: ActivityModel, **kwargs):
        super().__init__()

        self.__source: ActivityModel = source
        self.__subscription = self.__source.subscribe_item_changed_fn(
            partial(ActivityFilterModel._source_changed, weakref.proxy(self))
        )

        self.__timerange_begin = None
        self.__timerange_end = None

    def _source_changed(self, model, item):
        self._item_changed(item)

    @property
    def time_begin(self):
        return self.__source._time_begin

    @property
    def timerange_begin(self):
        return self.__timerange_begin

    @timerange_begin.setter
    def timerange_begin(self, value):
        if self.__timerange_begin != value:
            self.__timerange_begin = value
            self._item_changed(None)

    @property
    def timerange_end(self):
        return self.__timerange_end

    @timerange_end.setter
    def timerange_end(self, value):
        if self.__timerange_end != value:
            self.__timerange_end = value
            self._item_changed(None)

    def destroy(self):
        self.__source = None
        self.__subscription = None
        self.__timerange_begin = None
        self.__timerange_end = None

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        if self.__source is None:
            return []

        children = self.__source.get_item_children(item)

        if self.__timerange_begin is None or self.__timerange_end is None:
            return children

        result = []
        for child in children:
            for range in child.time_range:
                if max(self.__timerange_begin, range.begin) <= min(self.__timerange_end, range.end):
                    result.append(child)
                    break

        return result

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return self.__source.get_item_value_model_count(item)

    def get_item_value_model(self, item, column_id):
        """
        Return value model.
        """
        return self.__source.get_item_value_model(item, column_id)
