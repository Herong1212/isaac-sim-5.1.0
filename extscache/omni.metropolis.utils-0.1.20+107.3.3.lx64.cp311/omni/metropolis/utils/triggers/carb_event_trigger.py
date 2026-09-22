import carb

from .core import *


@dataclass
class CarbEventTrigger(TriggerBase):
    type_name: ClassVar[str] = "carb_event"
    event_name: str = "default carb event name"
    payload: dict = field(default_factory=lambda: {}, init=False)

    def __post_init__(self):
        # Observe a carb event
        self._event_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            observer_name=f"{self.event_name} observer", event_name=self.event_name, on_event=self.on_event
        )

    def destroy(self):
        self._event_sub.reset()
        super().destroy()

    def on_event(self, e: carb.eventdispatcher.Event):
        if "Payload" in e:
            self.payload = e["Payload"]
        self.trigger()
