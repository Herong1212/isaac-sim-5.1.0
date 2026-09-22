# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from enum import Enum
from functools import lru_cache
import typing
import carb
import omni.usd
from omni.kit.async_engine import run_coroutine


from pxr import Usd, Tf, Sdf, Gf, Trace


class EventType(Enum):
    CHANGE_INFO_ONLY = 0
    RESYNC = 1


class EventDispatcher:
    def __init__(self):
        self._path_to_callbacks = {}
        self._dispatch_set = set()
        self._notify_task = None

    def destroy(self):
        self.pump()
        self._path_to_callbacks = {}
        self._dispatch_set = {}
        if self._notify_task:
            self._notify_task.cancel()

    def subscribe_on_change(self, path, on_change: typing.Callable) -> carb.Subscription:
        key = Sdf.Path(path)
        callbacks = self._path_to_callbacks.setdefault(key, set())
        callbacks.add(on_change)

        def unsub_fn():
            callbacks.discard(on_change)
            if not callbacks:
                self._path_to_callbacks.pop(key)

        return carb.Subscription(unsub_fn)

    def on_changes(self, paths):
        if not self._path_to_callbacks:
            return

        self._dispatch_set.update(paths)

        # No changes
        if not self._dispatch_set:
            return

        # If task is created already
        if self._notify_task and not self._notify_task.done():
            return

        self._notify_task = run_coroutine(self.__async_pump())

    async def __async_pump(self):
        self.pump()
        self._notify_task = None

    def pump(self):
        # OMFP-2172: Swap them to avoid size changed during iteration.
        changed_paths, self._dispatch_set = self._dispatch_set, set()
        for path in changed_paths:
            self._dispatch_changed(path)

    def _send_callbacks(self, cb_path, changed_path):
        cb = self._path_to_callbacks.get(cb_path, None)
        if not cb:
            return

        for f in cb:
            f(changed_path)

    def _dispatch_changed(self, path):
        # Send callback for property path. Notify the property path subscription.
        self._send_callbacks(cb_path=path, changed_path=path)

        prim_path = path.GetPrimPath()
        if prim_path != path:
            # Send callback for property's prim path. Notify the prim path subscription for any property change.
            # Still pass 'path' not 'prim_path' as changed_path here
            self._send_callbacks(cb_path=prim_path, changed_path=path)


class UsdWatcher:
    """Internal. Utility class to wrap UsdNotice handling.

    It supports to subscribe specific paths.
    """

    _is_watcher_instanced = False

    @staticmethod
    def _is_instantiated():
        return UsdWatcher._is_watcher_instanced

    def __init__(self):
        self._stage = None

        self._change_info_only_dispatcher = EventDispatcher()
        self._resync_dispatcher = EventDispatcher()
        self._objects_changed = None
        UsdWatcher._is_watcher_instanced = True
        context = omni.usd.get_context()
        if context:
            self._attach_stage(context.get_stage())

    def _attach_stage(self, stage):
        """Internal: called when stage is attached."""
        if self._stage != stage:
            self._detach_stage()
            self._stage = stage
            if stage:
                self._objects_changed = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_prim_change, stage)

    def _detach_stage(self):
        """Internal: called when stage is closing."""
        if self._stage:
            # Pump old events
            self._change_info_only_dispatcher.pump()
            self._resync_dispatcher.pump()
            if self._objects_changed:
                self._objects_changed.Revoke()
                self._objects_changed = None
            self._stage = None

    def destroy(self):
        self._stage = None
        if self._objects_changed:
            self._objects_changed.Revoke()
            self._objects_changed = None

        if self._change_info_only_dispatcher:
            self._change_info_only_dispatcher.destroy()
            self._change_info_only_dispatcher = None

        if self._resync_dispatcher:
            self._resync_dispatcher.destroy()
            self._resync_dispatcher = None

    @Trace.TraceFunction
    def _on_prim_change(self, notice, stage):
        self._get_dispatcher(EventType.RESYNC).on_changes(notice.GetResyncedPaths())
        self._get_dispatcher(EventType.CHANGE_INFO_ONLY).on_changes(notice.GetChangedInfoOnlyPaths())

    def subscribe_to_resync_path(self, path: Sdf.Path, on_change: typing.Callable) -> carb.Subscription:
        return self._get_dispatcher(EventType.RESYNC).subscribe_on_change(path, on_change)

    def subscribe_to_change_info_path(self, path: Sdf.Path, on_change: typing.Callable) -> carb.Subscription:
        return self._get_dispatcher(EventType.CHANGE_INFO_ONLY).subscribe_on_change(path, on_change)

    def _get_dispatcher(self, event_type: EventType):
        if event_type == EventType.RESYNC:
            return self._resync_dispatcher
        else:
            return self._change_info_only_dispatcher


# USD Prim Watcher singleton getter
@lru_cache()
def get_watcher():
    """Singleton of UsdWatcher omni.usd module."""

    return UsdWatcher()
