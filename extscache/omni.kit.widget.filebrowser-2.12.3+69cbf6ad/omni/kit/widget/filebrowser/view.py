# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
An abstract View class, subclassed by TreeView and GridView.
"""
import threading
import omni.kit.app
import omni.kit.async_engine as async_engine

from typing import Callable
from abc import abstractmethod
from .model import FileBrowserItem, FileBrowserModel

__all__ = ["FileBrowserView"]

class FileBrowserView:
    """
    Base class for :obj:`FileBrowserGridView` and :obj:`FileBrowserTreeView`.

    Args:
        model (:obj:`FileBrowserModel`): the model to use.
    """
    def __init__(self, model: FileBrowserModel):
        self._widget = None
        self._visible = True
        self._futures = []
        # Setting the property to setup the subscription
        self.model = model

        # Enables thread-safe reads/writes to shared data
        self._mutex_lock: threading.Lock = threading.Lock()
        self._refresh_pending = False

    @abstractmethod
    def build_ui(self):
        """ Build the UI. """
        pass

    @property
    def model(self):
        """ Return the model of the view. """
        return self._model

    @model.setter
    def model(self, model):
        self._model = model
        if self._model:
            self._model_subscription = self._model.subscribe_item_changed_fn(self._on_item_changed)
        else:
            self._model_subscription = None
        self._on_model_changed(self._model)

    @property
    def visible(self):
        """ Return visiblity of the view. """
        return self._visible

    @visible.setter
    def visible(self, visible: bool):
        if self._widget:
            self._widget.visible = visible
        self._visible = visible

    def set_root(self, item: FileBrowserItem):
        """ Set the root item. """
        if self._model:
            self._model.root = item

    @abstractmethod
    def refresh_ui(self, item: FileBrowserItem = None):
        """
        Update the UI.

        Args:
            item (:obj:`FileBrowserItem`): The item to refresh.
        """
        pass

    def _throttled_refresh_ui(self, item: FileBrowserItem = None, callback: Callable = None, throttle_frames: int = 1):
        """
        Refresh the view. Delays the redraw to a later frame so that multiple calls to this function
        are queued up and handled in one go. For example, when multiple files are copied to the current
        directory, it will trigger a refresh for each file. If there are many of them, it could swamp
        the render queue with unnecessary redraws. By queueing up these tasks, we can limit the redraws
        to once per frame.
        """
        if not self._visible:
            return
        self._futures = list(filter(lambda f: not f.done(), self._futures))

        future = async_engine.run_coroutine(
                self._throttled_refresh_ui_async(item, callback, throttle_frames))

        self._futures.append(future)

    async def _throttled_refresh_ui_async(self, item: FileBrowserItem, callback: Callable, throttle_frames: int = 1):
        # If there's already a pending redraw, then skip.
        with self._mutex_lock:
            if self._refresh_pending:
                return
            else:
                self._refresh_pending = True

        # NOTE: Wait a beat to absorb adjacent redraw events so that we build the grid only once.
        for _ in range(throttle_frames):
            await omni.kit.app.get_app().next_update_async()

        if callback:
            callback(item)

        with self._mutex_lock:
            self._refresh_pending = False

    @abstractmethod
    def select_and_center(self, item: FileBrowserItem):
        """
        Select and center the view on the given item.
        Args:
            item (:obj:`FileBrowserItem`): the item to set the new selection to.
        """
        pass

    @abstractmethod
    def _on_selection_changed(self, selections: [FileBrowserItem]):
        pass

    @abstractmethod
    def destroy(self):
        """ Destructor. """
        for future in self._futures:
            future.cancel()
        self._futures.clear()
        self._mutex_lock = None
        self._refresh_pending = False

    def _on_item_changed(self, model, item):
        """Called by the model when something is changed"""
        pass

    def _on_model_changed(self, model):
        """Called by the model when something is changed"""
        pass
