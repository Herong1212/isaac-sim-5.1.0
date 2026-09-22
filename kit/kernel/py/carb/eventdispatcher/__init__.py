__copyright__ = "Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

"""This module contains bindings to C++ carb::eventdispatcher::IEventDispatcher interface.
"""

# This module depends on other modules. VSCode python language server scrapes
# modules in an isolated environment (ignoring PYTHONPATH set). `import` fails and for that we have separate code
# path to explicitly add it's folder to sys.path and import again.
try:
    import carb
except:
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..")))
    import carb

import asyncio
import inspect
from functools import lru_cache

import carb.variant

from ._eventdispatcher import *


@lru_cache()
def get_eventdispatcher_interface() -> IEventDispatcher:
    """Returns cached :class:`carb.eventdispatcher.IEventDispatcher` interface"""
    return acquire_eventdispatcher_interface()


def get_eventdispatcher() -> IEventDispatcher:
    """Returns cached :class:`carb.eventdispatcher.IEventDispatcher` interface (shorthand)."""
    return get_eventdispatcher_interface()


async def _next_event(
    self: IEventDispatcher,
    event_name: str,
    order: int = 0,
    filter: dict | None = None,
    observer_name: str | None = None,
):
    """Async wait for next event"""

    f = asyncio.Future()

    if not observer_name:
        frame = inspect.currentframe().f_back
        observer_name = f"{frame.f_code.co_name} at {frame.f_code.co_filename}:{frame.f_lineno}"

    def on_event(e: Event):
        if not f.done():
            f.set_result(e)

    sub = self.observe_event(
        order=order, event_name=event_name, on_event=on_event, filter=filter, observer_name=observer_name
    )
    event = await f
    return event


IEventDispatcher.next_event = _next_event


@lru_cache
def get_messagequeue_factory_interface() -> IMessageQueueFactory:
    """Returns cached :class:`carb.eventdispatcher.IMessageQueueFactory` interface"""
    return acquire_messagequeue_factory_interface()


def get_messagequeue_factory() -> IMessageQueueFactory:
    """Returns cached :class:`carb.eventdispatcher.IMessageQueueFactory` interface (shorthand)"""
    return get_messagequeue_factory_interface()


async def _push_and_wait(self, event_name, payload: dict = None):
    """Pushes a message to the message queue and does not return until the message is processed.

    Note, this function must be awaited. For a function that pushes a message without waiting, use push().

    Args:
        event_name: (str) The event name for the message
        payload: (dict) (optional) A dictionary that functions as the payload for the message.

    Returns:
        None

    Raises:
        IndexError: The message queue has been stopped.
        MemoryError: Failed to allocate memory for the message.
        RuntimeError: Any other error."""
    fut = asyncio.Future()
    self._push(event_name, payload, lambda stopped: fut.set_exception(IndexError) if stopped else fut.set_result(None))
    await fut
    return fut.result()


async def _pop(self, fn):
    """Waits until a message has been pushed to the queue and might be available. Returns after the message is handled.

    Note, this function must be awaited. The message is removed from the queue atomically before processing. In a
    single-owner-thread situation this function must be called within the context of the owning thread.

    If a task or thread is waiting on the message, the message will be considered 'completed' and unblock the waiting
    task/thread as soon as fn() returns, even if the carb.eventdispatcher.Event passed to the function is retained.

    This function returns once a message is processed. If the queue is stopped with stop() while awaiting, this function
    will stop waiting and will throw IndexError.

    Args:
        fn: (function) A function that is called with a carb.eventdispatcher.Event as the only parameter.

    Returns:
        None

    Raises:
        IndexError: The message queue has been stopped.
        RuntimeError: The calling thread is not the owner thread, or another error."""
    while True:
        if self.try_pop(fn):
            return
        fut = asyncio.Future()
        self._add_message_callback(lambda stopped: fut.set_exception(IndexError) if stopped else fut.set_result(None))
        # Try again after setting the message callback
        if self.try_pop(fn):
            return
        await fut


def _push(self, event_name, payload: dict = None):
    """Posts a message to the message queue without waiting for the message to be processed.

    Args:
        event_name: (str) The event name for the message.
        payload: (dict) (optional) A dictionary that functions as the payload for the message.

    Returns:
        None

    Raises:
        IndexError: The message queue has been stopped.
        MemoryError: Failed to allocate memory for the message.
        RuntimeError: Any other error.)"""
    return self._push(event_name, payload)


IMessageQueue.push_and_wait = _push_and_wait
IMessageQueue.pop = _pop
IMessageQueue.push = _push
