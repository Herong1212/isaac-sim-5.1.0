import carb
import omni.timeline
from typing import Union
from .global_time import get_global_time_s


class TimelineEvent:
    def __init__(
        self, 
        type: Union[int, omni.timeline.TimelineEventType], 
        payload: dict = None, 
        timestamp: float = None
    ):
        if isinstance(type, omni.timeline.TimelineEventType):
            type = int(type)
        self._type = type
        if payload is None:
            payload = {}
        self._payload = payload
        if timestamp is None:
            self._timestamp = get_global_time_s()
        else:
            self._timestamp = timestamp

    @classmethod
    def from_carb_event(self, event: carb.events.IEvent):
        return TimelineEvent(event.type, event.payload)
    
    @property
    def type(self) -> int:
        return self._type
    
    @property
    def payload(self) -> dict:
        return self._payload
    
    @property
    def timestamp(self) -> float:
        return self._timestamp