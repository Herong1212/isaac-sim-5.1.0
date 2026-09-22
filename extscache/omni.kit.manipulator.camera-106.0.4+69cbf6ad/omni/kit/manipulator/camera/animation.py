# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['AnimationEventStream']


import carb
import carb.eventdispatcher
import omni.kit.app
import traceback
from typing import Any, Callable


class AnimationEventStream:
    __g_instance = None

    @staticmethod
    def get_instance():
        if AnimationEventStream.__g_instance is None:
            AnimationEventStream.__g_instance = [AnimationEventStream(), 1]
        else:
            AnimationEventStream.__g_instance[1] = AnimationEventStream.__g_instance[1] + 1
        return AnimationEventStream.__g_instance[0]

    def __init__(self):
        self.__event_sub = None
        self.__callbacks = {}

    def __del__(self):
        self.destroy()

    def destroy(self):
        if AnimationEventStream.__g_instance and AnimationEventStream.__g_instance[0] == self:
            AnimationEventStream.__g_instance[1] = AnimationEventStream.__g_instance[1] - 1
            if AnimationEventStream.__g_instance[1] > 0:
                return
            AnimationEventStream.__g_instance = None

        self.__event_sub = None
        self.__callbacks = {}

    def __on_event(self, e: carb.eventdispatcher.Event):
        dt = e['dt']
        for _, callbacks in self.__callbacks.items():
            for cb_fn in callbacks:
                try:
                    cb_fn(dt)
                except Exception:
                    carb.log_error(traceback.format_exc())

    def __init(self):
        if self.__event_sub:
            return

        self.__event_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self.__on_event,
            observer_name="omni.kit.manipulator.camera.AnimationEventStream",
            order=omni.kit.app.UPDATE_ORDER_PYTHON_ASYNC_FUTURE_END_UPDATE
        )

    def add_animation(self, animation_fn: Callable, key: Any, remove_others: bool = True):
        if remove_others:
            self.__callbacks[key] = [animation_fn]
        else:
            prev_fns = self.__callbacks.get(key) or []
            if prev_fns:
                prev_fns.append(animation_fn)
            else:
                self.__callbacks[key] = [animation_fn]

        self.__init()

    def remove_animation(self, key: Any, animation_fn: Callable = None):
        if animation_fn:
            prev_fns = self.__callbacks.get(key)
            if prev_fns:
                try:
                    prev_fns.remove(animation_fn)
                except ValueError:
                    pass
        else:
            prev_fns = None

        if not prev_fns:
            try:
                del self.__callbacks[key]
            except KeyError:
                pass
            if not self.__callbacks:
                self.__event_sub = None
