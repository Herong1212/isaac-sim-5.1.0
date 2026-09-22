from __future__ import annotations
import omni.activity.core._activity
import typing
import omni.core._core

__all__ = [
    "EventType",
    "IActivity",
    "IEvent",
    "INode",
    "began",
    "disable",
    "enable",
    "ended",
    "get_instance",
    "progress",
    "updated"
]


class EventType():
    """
    Members:

      BEGAN : /< The activity is started

      UPDATED : /< The activity is changed

      ENDED : /< The activity is finished
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    BEGAN: omni.activity.core._activity.EventType # value = <EventType.BEGAN: 0>
    ENDED: omni.activity.core._activity.EventType # value = <EventType.ENDED: 2>
    UPDATED: omni.activity.core._activity.EventType # value = <EventType.UPDATED: 1>
    __members__: dict # value = {'BEGAN': <EventType.BEGAN: 0>, 'UPDATED': <EventType.UPDATED: 1>, 'ENDED': <EventType.ENDED: 2>}
    pass
class IActivity(_IActivity, omni.core._core.IObject):
    """
    @brief The activity and the progress processor.
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def create_callback_to_pop(self, fn: typing.Callable[[INode], None]) -> int: 
        """
        Subscribes to event dispatching on the stream.

        See :class:`.Subscription` for more information on subscribing mechanism.

        Args:
            fn: The callback to be called on event dispatch.

        Returns:
            The subscription holder.
        """
    def pump(self) -> None: 
        """
        @brief Process the callback. Should be called once per frame.
        """
    def push_event_dict(self, node_path: str, type: EventType, event_payload: capsule) -> bool: 
        """
        @brief Push event to the system.

        TODO: eventPayload is a placeholder
        TODO: eventPayload should be carb::dictionary
        """
    def remove_callback(self, id: int) -> None: 
        """
        @brief Remove the callback.
        """
    @property
    def current_timestamp(self) -> int:
        """
        :type: int
        """
    @property
    def enabled(self) -> None:
        """
        :type: None
        """
    @enabled.setter
    def enabled(self, arg1: bool) -> None:
        pass
    pass
class IEvent(_IEvent, omni.core._core.IObject):
    """
    @brief The event contains custom data. It can be speed, progress, etc.
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    @property
    def event_timestamp(self) -> int:
        """
        :type: int
        """
    @property
    def event_type(self) -> EventType:
        """
        :type: EventType
        """
    @property
    def payload(self) -> carb.dictionary._dictionary.Item:
        """
        :type: carb.dictionary._dictionary.Item
        """
    pass
class INode(_INode, omni.core._core.IObject):
    """
    @brief Node can contain other nodes and events.
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def get_child(self, n: int) -> INode: 
        """
        @brief Get the child node
        """
    def get_event(self, n: int) -> IEvent: 
        """
        @brief Get the activity
        """
    @property
    def child_count(self) -> int:
        """
        :type: int
        """
    @property
    def event_count(self) -> int:
        """
        :type: int
        """
    @property
    def name(self) -> str:
        """
        :type: str
        """
    pass
class _IActivity(omni.core._core.IObject):
    pass
class _IEvent(omni.core._core.IObject):
    pass
class _INode(omni.core._core.IObject):
    pass
def began(name: str, **kwargs) -> None:
    """
    Send began typed activity event.

    Args:
        name: the name of the activity event.
    """
def disable() -> None:
    """
    Disable activity dispatching.
    """
def enable() -> None:
    """
    Enable activity dispatching.
    """
def ended(name: str, **kwargs) -> None:
    """
    Send end typed activity event.

    Args:
        name: the name of the activity event.
    """
def get_instance() -> IActivity:
    """
    Return the global IActivity singleton instance.
    """
def progress(name: str, progress: float, **kwargs) -> None:
    """
    Send progress payload in the activity event.

    Args:
        name: the name of the activity event.
        progress: the progress of the specified activity.
    """
def updated(name: str, **kwargs) -> None:
    """
    Send updated typed activity event.

    Args:
        name: the name of the activity event.
    """
