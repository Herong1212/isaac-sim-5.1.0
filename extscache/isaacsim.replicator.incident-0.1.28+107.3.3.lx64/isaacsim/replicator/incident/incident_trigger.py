import carb
from typing import ClassVar
from dataclasses import dataclass, field
from omni.metropolis.utils.triggers.core import TriggerBase
from .event_defines import IncidentData, IncidentCarbEventHelper


@dataclass
class IncidentTrigger(TriggerBase):
    """
    IncidentTrigger is a specialized carb event trigger
    that only observes incident carb events and receives incident data.
    """

    type_name: ClassVar[str] = "physical_event"
    incident_name: str = "default event name"
    incident_data: IncidentData = field(default_factory=lambda: IncidentData(), init=False)

    def __post_init__(self):
        self._event_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            observer_name=f"{self.incident_name} observer",
            event_name=IncidentCarbEventHelper.carb_event_name(self.incident_name),
            on_event=self.on_incident_event,
        )

    def on_incident_event(self, e: carb.eventdispatcher.Event):
        if "event_data" in e["Payload"]:
            self.incident_data = e["Payload"]["event_data"]
        self.trigger()

    def destroy(self):
        self._event_sub = None
        super().destroy()
