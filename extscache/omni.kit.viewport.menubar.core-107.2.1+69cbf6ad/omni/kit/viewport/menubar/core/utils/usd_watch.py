# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["start", "stop", "subscribe"]

import asyncio
from collections import defaultdict
import concurrent.futures
from dataclasses import dataclass
from functools import partial
from typing import Callable, Dict, List, Optional, Union
import weakref

from pxr import Sdf, Tf, Trace, Usd
import omni.kit.app
from omni.kit.async_engine import run_coroutine

# The watch object is one per session
__watch: Optional["_USDWatch"] = None


def start():
    """Starts watch"""
    global __watch
    if not __watch:
        __watch = _USDWatch()


def stop():
    """Stops watch"""
    global __watch
    if __watch:
        __watch.destroy()
        __watch = None


def subscribe(stage: Usd.Stage, path: Sdf.Path, callback: Callable[[], None]):
    """
    Lets execute the callback when the given attribute is changed. The
    callback will be executed while the returned object is alive. If returned
    object is None, the watch is not started.
    """
    return __watch.subscribe(stage, path, callback) if __watch else None


class _USDWatch:
    """
    The object that holds a single Tf.Notice.Listener and executes callbacks
    when specific attribute is changed.
    """

    @dataclass
    class _USDWatchCallbackHandler:
        """Holds the callbacks"""

        changed_fn: Callable[[], None]

    def __init__(self):
        self.__listener: Optional[Tf.Notice.Listener] = None
        # The storage with all registered callbacks
        self.__callbacks: Dict[Usd.Stage, Dict[Sdf.Path, Callable[[], None]]] = defaultdict(dict)

        # The storage with all dirty attributes
        self.__dirty_attr_paths: Dict[Usd.Stage, List[Sdf.Path]] = defaultdict(list)
        # The task where the dirty attributes are computed
        self.__prim_changed_task_or_future: Union[asyncio.Task, concurrent.futures.Future, None] = None

    def destroy(self):
        """Should be executed before the object is killed"""
        self.clear_all()

    def clear_all(self):
        """Stop Tf.Notice and clear callbacks"""
        if self.__listener:
            self.__listener.Revoke()
            self.__listener = None

        self.__callbacks.clear()

    def subscribe(self, stage: Usd.Stage, path: Sdf.Path, callback: Callable[[], None]):
        """
        Lets execute the callback when the given attribute is changed. The
        callback will be executed while the returned object is alive.
        """

        if not self.__listener:
            self.__listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_usd_changed, None)

        handler = self._USDWatchCallbackHandler(callback)
        self.__callbacks[stage][path] = weakref.proxy(handler, partial(self._unsubscribe, stage, path))

        return handler

    def _unsubscribe(self, stage: Usd.Stage, path: Sdf.Path, dead):
        """Stop the subscription of the given attribute"""
        callbacks = self.__callbacks.get(stage, None)
        if callbacks is None:
            return

        callbacks.pop(path)
        if not callbacks:
            # Remove the stage if empty
            self.__callbacks.pop(stage)

        if not self.__callbacks:
            # Stop the USD listener if there are no callbacks
            self.clear_all()

    def _update_dirty(self):
        """
        Execute the callbacks for the dirty items that was collected from
        TfNotice. It can be called any time to pump changes.
        """
        dirty_attr_paths = self.__dirty_attr_paths
        self.__dirty_attr_paths = defaultdict(list)

        for stage, dirty_paths in dirty_attr_paths.items():
            callbacks = self.__callbacks.get(stage, None)
            if not callbacks:
                continue

            for path in set(dirty_paths):
                callback = callbacks.get(path, None)
                if callback:
                    callback.changed_fn()

    @Trace.TraceFunction
    def _on_usd_changed(self, notice: Tf.Notice, stage: Usd.Stage):
        """Called by Usd.Notice.ObjectsChanged"""
        if stage not in self.__callbacks:
            return

        dirty_prims_paths: List[Sdf.Path] = []

        for p in notice.GetChangedInfoOnlyPaths():
            if p.IsPropertyPath() or p.IsPrimPath():
                dirty_prims_paths.append(p)

        for p in notice.GetResyncedPaths():
            if p.IsPropertyPath() or p.IsPrimPath():
                dirty_prims_paths.append(p)

        if not dirty_prims_paths:
            return

        self.__dirty_attr_paths[stage] += dirty_prims_paths

        # Update in the next frame. We need it because we want to accumulate the affected prims
        if self.__prim_changed_task_or_future is None or self.__prim_changed_task_or_future.done():
            self.__prim_changed_task_or_future = run_coroutine(self.__delayed_prim_changed())

    @Trace.TraceFunction
    async def __delayed_prim_changed(self):
        await omni.kit.app.get_app().next_update_async()

        # Pump the changes to the camera list.
        self._update_dirty()

        self.__prim_changed_task_or_future = None
