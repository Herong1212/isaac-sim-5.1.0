# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ActivityProgressModel"]

import weakref
from functools import partial
import omni.ui as ui
import omni.activity.core
import time
from urllib.parse import unquote
from .activity_model import ActivityModel, SECOND_MULTIPLIER


moving_window = 20


class ActivityProgressModel(ui.AbstractItemModel):
    """
    The model that takes the source model and filters out the items that are
    outside of the given time range.
    """
    def __init__(self, source: ActivityModel, **kwargs):
        super().__init__()

        self._flattened_children = []
        self._latest_item = None

        self.usd_loaded_sum = 0
        self.usd_sum = 0
        self.usd_progress = 0
        self.usd_size = 0
        self.usd_speed = 0

        self.texture_loaded_sum = 0
        self.texture_sum = 0
        self.texture_progress = 0
        self.texture_size = 0
        self.texture_speed = 0

        self.material_loaded_sum = 0
        self.material_sum = 0
        self.material_progress = 0

        self.total_loaded_sum = 0
        self.total_sum = 0
        self.total_progress = 0

        self.start_loading = False
        self.finish_loading = False
        self.total_duration = 0

        current_time = time.time()
        self.prev_usd_update_time = current_time
        self.prev_texture_update_time = current_time
        self.texture_data = [(0, current_time)]
        self.usd_data = [(0, current_time)]

        self.__source: ActivityModel = source
        self.__subscription = self.__source.subscribe_item_changed_fn(
            partial(ActivityProgressModel._source_changed, weakref.proxy(self))
        )

        self.activity = omni.activity.core.get_instance()
        self._load_data_from_source(self.__source)

    def update_USD(self, item):
        self.usd_loaded_sum = item.loaded_children_num
        self.usd_sum = len(item.children)
        self.usd_progress = 0 if self.usd_sum == 0 else self.usd_loaded_sum / float(self.usd_sum)

        loaded_size = item.children_size * 0.000001
        if loaded_size != self.usd_size:
            current_time = time.time()
            self.usd_data.append((loaded_size, current_time))
            if len(self.usd_data) > moving_window:
                self.usd_data.pop(0)
            prev_size, prev_time = self.usd_data[0]
            self.usd_speed = (loaded_size - prev_size) / (current_time - prev_time)
            self.prev_usd_update_time = current_time
            self.usd_size = loaded_size

    def update_textures(self, item):
        self.texture_loaded_sum = item.loaded_children_num
        self.texture_sum = len(item.children)
        self.texture_progress = 0 if self.texture_sum == 0 else self.texture_loaded_sum / float(self.texture_sum)

        loaded_size = item.children_size * 0.000001
        if loaded_size != self.texture_size:
            current_time = time.time()
            self.texture_data.append((loaded_size, current_time))
            if len(self.texture_data) > moving_window:
                self.texture_data.pop(0)
            prev_size, prev_time = self.texture_data[0]
            if current_time == prev_time:
                return
            self.texture_speed = (loaded_size - prev_size) / (current_time - prev_time)
            self.prev_texture_update_time = current_time
            self.texture_size = loaded_size

    def update_materials(self, item):
        self.material_loaded_sum = item.loaded_children_num
        self.material_sum = len(item.children)
        self.material_progress = 0 if self.material_sum == 0 else self.material_loaded_sum / float(self.material_sum)

    def update_total(self):
        self.total_sum = self.usd_sum + self.texture_sum + self.material_sum
        self.total_loaded_sum = self.usd_loaded_sum + self.texture_loaded_sum + self.material_loaded_sum
        self.total_progress = 0 if self.total_sum == 0 else self.total_loaded_sum / float(self.total_sum)

    def _load_data_from_source(self, model):
        if not model or not model.get_item_children(None):
            return
        for child in model.get_item_children(None):
            name = child.name_model.as_string
            if name == "Materials":
                self.update_materials(child)
            elif name in ["USD", "Textures"]:
                items = model.get_item_children(child)
                for item in items:
                    item_name = item.name_model.as_string
                    if item_name == "Read":
                        self.update_USD(item)
                    elif item_name == "Load":
                        self.update_textures(item)
        self.update_total()

        if model._time_begin and model._time_end:
            self.total_duration = int((model._time_end - model._time_begin) / float(SECOND_MULTIPLIER))

    def _source_changed(self, model, item):
        name = item.name_model.as_string
        if name in ["Read", "Load", "Materials"]:
            if name == "Read":
                self.update_USD(item)
            elif name == "Load":
                self.update_textures(item)
            elif name == "Materials":
                self.update_materials(item)
            self.update_total()
            # telling the tree root that the list is changing
            self._item_changed(None)

    def finished_loading(self):
        if self.__source._time_begin and self.__source._time_end:
            self.total_duration = int((self.__source._time_end - self.__source._time_begin) / float(SECOND_MULTIPLIER))
        else:
            self.total_duration = self.duration
        self.finish_loading = True
        # sometimes ASSETS_LOADED isn't called when stage is completely finished loading,
        # so we force progress to be 1 when we decided that it's finished loading.
        self.usd_loaded_sum = self.usd_sum
        self.usd_progress = 1
        self.texture_loaded_sum = self.texture_sum
        self.texture_progress = 1
        self.material_loaded_sum = self.material_sum
        self.material_progress = 1
        self.total_loaded_sum = self.total_sum
        self.total_progress = 1
        self._item_changed(None)

    @property
    def time_begin(self):
        return self.__source._time_begin

    @property
    def duration(self):
        if not self.start_loading and not self.finish_loading:
            return 0
        elif self.finish_loading:
            return self.total_duration
        elif self.start_loading and not self.finish_loading:
            current_timestamp = self.activity.current_timestamp
            duration = (current_timestamp - self.time_begin) / float(SECOND_MULTIPLIER)
        return int(duration)

    @property
    def latest_item(self):
        if self.finish_loading:
            return None
        if hasattr(self.__source, "_flattened_children") and self.__source._flattened_children:
            item = self.__source._flattened_children[0]
            name = item.name_model.as_string
            short_name = unquote(name.split("/")[-1])
            return short_name
        else:
            return ""

    def get_data(self):
        return self.__source.get_data()

    def destroy(self):
        self.__source = None
        self.__subscription = None
        self.texture_data = []
        self.usd_data = []

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        if item is None and hasattr(self.__source, "_flattened_children"):
            return self.__source._flattened_children
        return []

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return self.__source.get_item_value_model_count(item)

    def get_item_value_model(self, item, column_id):
        """
        Return value model.
        """
        return self.__source.get_item_value_model(item, column_id)
