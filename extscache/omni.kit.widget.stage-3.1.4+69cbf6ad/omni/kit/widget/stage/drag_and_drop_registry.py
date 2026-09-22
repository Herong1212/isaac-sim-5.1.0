__all__ = ["DragAndDropRegistry"]

from carb import log_warn
from dataclasses import dataclass
from typing import Any, Callable

from .singleton import Singleton

@dataclass
class DropHandler:
    filter_fn: Callable[[Any], bool]
    handler_fn: Callable[[Any, Any], None]


@Singleton
class DragAndDropRegistry:
    """A singleton registry that manages drag-n-drop handlers registered from other extensions, keyed by handler name."""

    def __init__(self):
        """Creates the registry instance."""
        self._drop_handler_actions =  {}

    def register_drop_handler(
        self,
        name: str,
        filter_fn: Callable[[Any], bool],
        handler_fn: Callable[[Any, Any], None]
    ):
        """
        API for registering a drop handler.
        If a drop handler is already registered with the given name, it will be overriden by this new handler.

        Args:
            name (str): The name for the registered drop handler.
            filter_fn (Callable[[Any], bool]): The filter function for whether the drop event should be accepted.
            handler_fn (Callable[[Any, Any], None]): The handler function for drop event.
        """
        if name in self._drop_handler_actions:
            log_warn("Overriding drop handler with name: {}".format(name))
        self._drop_handler_actions[name] = DropHandler(filter_fn, handler_fn)

    def deregister_drop_handler(
        self,
        name: str
    ):
        """
        API for deregistering a drop handler.
        If a drop handler is not registered with the given name, no operation will be performed.

        Args:
            name (str): The name of the drop handler to be removed.
        """
        if not name in self._drop_handler_actions:
            log_warn("omni.kit.widget.stage: Attempting to deregister drop handler for '{}', but none is found.".format(name))
        else:
            del self._drop_handler_actions[name]

    def handle_drop_payload(
        self,
        source: Any,
        item: Any
    ) -> bool:
        """
        Handles a drop payload with all registered handlers until it is processed. Returns whether it has been processed.
        Loops through all registered handlers, once one of the drop handler has accepted the drop event, applies the
        corresponding handler function to the drop payload and returns True. If no handler has accepted the drop payload,
        returns False indicating that the drop payload is NOT handled.

        Args:
            source (Any): Source for the drop event.
            item (Any): Item related to the drop event.

        Returns:
            bool: Whether the drop payload has been handled by any of the registered drop handler.
        """
        for handler in self._drop_handler_actions.values():
            if handler.filter_fn(source):
                handler.handler_fn(source, item)
                return True
        return False
    
    def drop_accepted(self, source):
        for handler in self._drop_handler_actions.values():
            if handler.filter_fn(source):
                return True
        return False
