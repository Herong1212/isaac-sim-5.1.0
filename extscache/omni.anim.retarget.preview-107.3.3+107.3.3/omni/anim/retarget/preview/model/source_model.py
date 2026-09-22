# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


import enum
from contextlib import suppress

import omni.ui as ui
import omni.usd
from pxr import Usd, Tf
from typing import Callable, Optional, Union


class ObjectSource(enum.Enum):
    MAIN_STAGE = 1
    URL = 2


class SourceModel(ui.AbstractValueModel):
    """ Simple class to track where a prim came from and where it is stored now
    """
    def __init__(self):
        super().__init__()
        self.source_path_in_stage = ""
        self.source_stage = None
        self.target_path_in_stage = None
        self._source_type = None
        self._source_url = None
        self._exists_in_main_stage = False
        self.display_text = None
        self.payload = None

    @property
    def is_external(self) -> bool:
        return self._source_type == ObjectSource.URL

    @property
    def path_name(self) -> str:
        if self.source_path_in_stage is None:
            return None
        return self.source_path_in_stage.split('/')[-1]

    def get_value_as_string(self) -> str:
        if self.display_text is not None:
            return self.display_text
        if self.is_external and self.source_path_in_stage is not None:
            return '[External source] ' + self.source_path_in_stage
        elif not self.is_external and not self._exists_in_main_stage:
            return '[Removed] ' + self.source_path_in_stage
        return self.source_path_in_stage

    def set_source_path_in_stage(self, value: str, stage: Optional[Usd.Stage] = None):
        # Add support for prefix with files here
        self.source_path_in_stage = value
        self.source_stage = stage
        self._value_changed()

    @property
    def exists_in_source_stage(self):
        return self._exists_in_main_stage

    def set_removed(self, removed: bool = True):
        self._exists_in_main_stage = not removed
        self._value_changed()

    def is_read_only(self) -> bool:
        '''
        Returns True if the source prim exists in the source stage.
        Currently,  only the main stage is supported, prims that were loaded from files are always read-only.
        '''
        return self.is_external or not self.exists_in_source_stage

    @property
    def source_url(self) -> str:
        return self._source_url

    @property
    def source_type(self) -> ObjectSource:
        return self._source_type

    def is_empty(self):
        return self._source_type is None or self.source_url == ""

    def set_source_url(self, value: str, exists: bool = True):
        self._source_url = value
        if value is None:
            self._source_type = ObjectSource.MAIN_STAGE
            self._exists_in_main_stage = exists
        else:
            self._source_type = ObjectSource.URL
            self._exists_in_main_stage = False
        self._value_changed()


class SourceItemModel(ui.AbstractItem):
    def __init__(self, model: SourceModel = None):
        super().__init__()
        if model is None:
            self.model = SourceModel()
        else:
            self.model = model


class SourceSetModel(ui.AbstractItemModel):
    """ Creates an ordered set of Sources
    """
    def __init__(self, source_context: omni.usd.UsdContext = None):
        super().__init__()
        if source_context is None:
            self._source_context = omni.usd.get_context()
        else:
            self._source_context = source_context
        self._sources = []
        self._current_index = ui.SimpleIntModel()
        self._current_index.add_value_changed_fn(self._current_index_changed)
        self._usd_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._process_usd_change, None)
        self._prim_delete_callbacks = []

    def add_prim_delete_callback_fn(self, callback):
        self._prim_delete_callbacks.append(callback)

    def remove_prim_delete_callback_fn(self, callback):
        if callback in self._prim_delete_callbacks:
            with suppress(ValueError):
                self._prim_delete_callbacks.remove(self._prim_delete_callbacks.index(callback))

    def _current_index_changed(self, model):
        item = None
        index = model.as_int
        if 0 <= index < len(self._sources):
            item = self._sources[index][0]
        self._item_changed(item)

    def add_source(self, source: Union[SourceModel, SourceItemModel], set_current: bool = True):
        if isinstance(source, SourceModel):
            item = SourceItemModel(source)
            source_model = source
        else:
            item = source
            source_model = source.model
        callback_id = source_model.add_value_changed_fn(self._on_source_changed)
        self._sources.append((item, callback_id))
        # TODO: sort?
        if set_current:
            idx_new = len(self._sources) - 1
            if idx_new != self._current_index.as_int:
                # _item_changed is also triggered by _current_index_changed
                self._current_index.set_value(idx_new)
            else:
                self._item_changed(item)
        else:
            self._item_changed(item)

    def find_source(self, condition_callback: Callable[[SourceModel], bool]) -> list:
        sources_indices = []
        for i, pair in enumerate(self._sources):
            source = pair[0].model
            if condition_callback(source):
                sources_indices.append((source, i))
        return sources_indices

    def clear(self):
        self._clear_sources()
        self._item_changed(None)

    @property
    def current_index(self):
        return self._current_index.as_int

    def get_current_source(self) -> SourceModel:
        if self.current_index >= len(self._sources):
            return None
        return self._sources[self.current_index][0].model

    def get_item_children(self, parentItem):
        return [x[0] for x in self._sources]

    def get_item_value_model(self, item, column_id: int = 0) -> ui.AbstractValueModel:
        if item is None:
            return self._current_index
        return item.model

    def set_current(self, index: int) -> bool:
        if 0 <= index < len(self._sources):
            self._current_index.set_value(index)
            self._item_changed(None)
            return True
        return False

    def _on_source_changed(self, source: SourceModel):
        self._item_changed(SourceItemModel(source))

    def _clear_sources(self):
        for source, callback in self._sources:
            source.model.remove_value_changed_fn(callback)
            if source.model.payload is not None:
                if hasattr(source.model.payload, 'destroy'):
                    source.model.payload.destroy()
        self._sources = []

    def _process_usd_change(self, objects, stage):
        def check_and_process(source:SourceModel, modified_paths):
            if not source.is_external and source.exists_in_source_stage and source.source_stage == stage:
                prim = stage.GetPrimAtPath(source.source_path_in_stage)
                if not prim.IsValid():
                    # We can detect rename/move only when paths contain the old and the new paths, nothing else
                    if len(modified_paths) == 2:
                        if modified_paths[0] == source.source_path_in_stage and stage.GetPrimAtPath(modified_paths[1]).IsValid():
                            source.set_source_path_in_stage(str(modified_paths[1]), source.source_stage)
                            return
                        elif modified_paths[1] == source.source_path_in_stage \
                            and stage.GetPrimAtPath(modified_paths[0]).IsValid():
                            source.set_source_path_in_stage(str(modified_paths[0]), source.source_stage)
                            return
                    # It's a deletion
                    # Run callbacks ahead of the removal so that the source is
                    ## still "live" for the callbacks
                    for callback in self._prim_delete_callbacks:
                        callback(source)
                    source.set_removed()

        # We only care about deletion and rename/move in the context stage
        context_stage = omni.usd.get_context().get_stage()
        if context_stage == stage:
            paths = objects.GetResyncedPaths()
            if not len(paths):
                return

            obj_path = str(paths[0])
            if "." in obj_path:
                # property change, not object change
                return

            for item in self._sources:
                check_and_process(item[0].model, paths)

    def destroy(self):
        self._clear_sources()
        if self._usd_listener:
            self._usd_listener.Revoke()
        self._usd_listener = None
