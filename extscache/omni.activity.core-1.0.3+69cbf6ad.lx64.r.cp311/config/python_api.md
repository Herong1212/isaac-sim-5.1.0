# Public API for module omni.activity.core:

## Classes

- class EventType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - BEGAN: omni.activity.core._activity.EventType
  - ENDED: omni.activity.core._activity.EventType
  - UPDATED: omni.activity.core._activity.EventType

- class IActivity(_IActivity, omni.core._core.IObject)
  - def __init__(self, arg0: omni.core._core.IObject)
  - def __init__(self)
  - def create_callback_to_pop(self, fn: typing.Callable[[INode], None]) -> int
  - def pump(self)
  - def push_event_dict(self, node_path: str, type: EventType, event_payload: capsule) -> bool
  - def remove_callback(self, id: int)
  - [property] def current_timestamp(self) -> int
  - [property] def enabled(self)
  - [enabled.setter] def enabled(self, arg1: bool)

- class IEvent(_IEvent, omni.core._core.IObject)
  - def __init__(self, arg0: omni.core._core.IObject)
  - def __init__(self)
  - [property] def event_timestamp(self) -> int
  - [property] def event_type(self) -> EventType
  - [property] def payload(self) -> carb.dictionary._dictionary.Item

- class INode(_INode, omni.core._core.IObject)
  - def __init__(self, arg0: omni.core._core.IObject)
  - def __init__(self)
  - def get_child(self, n: int) -> INode
  - def get_event(self, n: int) -> IEvent
  - [property] def child_count(self) -> int
  - [property] def event_count(self) -> int
  - [property] def name(self) -> str

## Functions

- def began(name: str, **kwargs)
- def disable()
- def enable()
- def ended(name: str, **kwargs)
- def get_instance() -> IActivity
- def progress(name: str, progress: float, **kwargs)
- def updated(name: str, **kwargs)
