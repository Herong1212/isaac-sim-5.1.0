# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from __future__ import annotations

import weakref
from weakref import ReferenceType
from typing import Any, Callable, Dict, List, Tuple, Type

from .toolbar_tool import ToolbarTool


class ToolbarRegistry:
    """A registry for managing toolbar tools in an application.

    This class holds a collection of ToolbarTool classes and provides mechanisms to register or unregister these tools, subscribe to changes in the registry, and retrieve a sorted list of registered tools.

    """

    class Subscription:
        """Represents a subscription to the toolbar registry change events.

        This class handles the lifecycle of a subscription to the toolbar registry, allowing for the registration and release of callback functions that listen for changes in the toolbar tool registry.

        Args:
            registry: ReferenceType[ToolbarRegistry]
                A weak reference to the ToolbarRegistry instance.
            id: str
                The unique identifier for this subscription."""

        def __init__(self, registry: ReferenceType[ToolbarRegistry], id: str):
            self._registry = registry
            self._id = id

        def __del__(self):
            self.release()

        def release(self):
            registry = self._registry()
            if self._id is not None and registry is not None:
                registry.unsubscribe_to_registry_change(self._id)
                self._id = None

    def __init__(self):
        self._tools: Dict[str, Type[ToolbarTool]] = {}
        self._change_subscribers: Dict[int, Callable] = {}
        self._next_change_subscriber_id: int = 1
        self._sorted_tools: List[Type[ToolbarTool]] = []
        self._sort_key: Callable[[Tuple[str, Type[ToolbarTool]]], Any] = None

    @property
    def tools(self) -> List[Type[ToolbarTool]]:
        """Gets a sorted list of all tool classes."""
        return self._sorted_tools

    def register_tool(self, tool_class: Type[ToolbarTool], id: str):
        """
        Registers a tool class to the registry.

        Args:
            tool_class (Type[ToolbarTool]): The class of the tool to be registered.
            id (str): Unique id of the tool. It must not already exist.
        """
        if id in self._tools:
            raise ValueError(f"{id} already exist!")

        self._tools[id] = tool_class
        self._notify_registry_changed()

    def unregister_tool(self, id: str):
        """
        Unregisters a tool class using its id.

        Args:
            id (str): The id used in `register_tool`
        """
        self._tools.pop(id, None)
        self._notify_registry_changed()

    def subscribe_to_registry_change(self, callback: Callable[[], None]) -> int:
        """
        Subscribes to registry changed event. Callback will be called when tool classes are registered or unregistered.

        Args:
            callback (Callable[[], None]): the callback to be called. It is called immediately before function returns.

        Return:
            An Subscription object. Call sub.release() to unsubscribe.

        """
        id = self._next_change_subscriber_id
        self._next_change_subscriber_id += 1
        self._change_subscribers[id] = callback
        self._notify_registry_changed(callback)
        return ToolbarRegistry.Subscription(weakref.ref(self), id)

    def unsubscribe_to_registry_change(self, id: int):
        """
        Called be Subscription.release to unsubscribe from registry changed event. Do not call this function directly.
        User should use Subscription object to unsubscribe.

        Args:
            id (int): id returned from subscribe_to_registry_change

        """
        self._change_subscribers.pop(id, None)

    def set_sort_key_function(self, key: Callable[[Tuple[str, Type[ToolbarTool]]], Any]):
        """
        Set a custom key function to sort the registered tool classes.

        Args:
            key (Callable[[Tuple[str, Type[ToolbarTool]]], Any]): key function used for sorting.

        """
        self._sort_key = key

    def _notify_registry_changed(self, callback: Callable[[], None] = None):
        self._sorted_tools = [value for key, value in sorted(self._tools.items(), key=self._sort_key)]

        if not callback:
            for sub in self._change_subscribers.values():
                sub()
        else:
            callback()
