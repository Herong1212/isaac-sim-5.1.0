import carb
import omni.timeline
from random import Random
from typing import Callable, List

from omni.metropolis.utils.triggers.core import TriggerBase, TriggersManager

from ..config_file_defines import SpillEventProperty

from ..incident_report import IncidentReport

from ..settings import IncidentSettings

from .spill_event_iface import SpillEventBase

from .scene_tagging import SceneTaggingData, AttributeUSDTagger


class SpillEventManager:
    """
    This class is responsible for managing topple events in the scene.
    It exposes functions for adding topple events, triggering them, and observing them.
    It also holds the data for the incident report.
    """

    def __init__(
        self,
        attribute_usd_tagger_factory: Callable[[], AttributeUSDTagger],
        spill_event_factory: Callable[[str, str, float], SpillEventBase],
        random_seed=123456,
        report: IncidentReport = None,
    ):
        self._attribute_usd_tagger_factory: Callable[[], AttributeUSDTagger] = attribute_usd_tagger_factory
        self._scene_tagging_data: SceneTaggingData = None
        self.spill_events: dict = None
        self.random = None
        self.report = report
        self.spill_event_factory = spill_event_factory

        self.unspilled_items = []
        self.spillable_area_prim_paths = []

        timeline = omni.timeline.get_timeline_interface()
        self.timeline_sub = timeline.get_timeline_event_stream().create_subscription_to_pop(
            self.timeline_callback, name="SpillEventManager"
        )

        self.setup(random_seed)

    def set_random_seed(self, random_seed):
        self.random = Random(random_seed)

    def destroy(self):
        if self.spill_events:
            for event in self.spill_events.values():
                event.destroy()

        self.timeline_sub = None
        self.spill_events = None
        self.random = None
        self.report = None
        self._scene_tagging_data = None
        self.unspilled_items = []
        self.spillable_area_prim_paths = []

    def setup(self, random_seed):

        timeline = omni.timeline.get_timeline_interface()
        self.timeline_sub = timeline.get_timeline_event_stream().create_subscription_to_pop(
            lambda e, s=self: s.timeline_callback(e), name="SpillEventManager"
        )

        self.spill_events = {}

        self.random = Random(random_seed)
        usd_tagger = self._attribute_usd_tagger_factory()
        self._scene_tagging_data = usd_tagger.Read()
        if not self._scene_tagging_data:
            carb.log_error("Could not read spill tags from scene")
            return

        self.unspilled_items = []
        for _, prim_paths in self._scene_tagging_data.leakable_item_prim_paths_by_type.items():
            self.unspilled_items.extend(prim_paths)

        self.spillable_area_prim_paths = []
        for _, prim_paths in self._scene_tagging_data.spillable_area_prim_paths_by_type.items():
            self.spillable_area_prim_paths.extend(prim_paths)

    def generate_spill_event(
        self,
        name: str,
        selected_spillable_item: str,
        target_size: float = 1.0,
        leak_duration: float = 1.0,
        trigger: TriggerBase = None,
    ):
        if selected_spillable_item == IncidentSettings.RANDOM_LEAKABLE_ITEM:
            selected_spillable_item = self.select_random_spillable_item()
        if selected_spillable_item not in self.unspilled_items:
            carb.log_error(f"'{selected_spillable_item}' is not a tagged prim. Generating spill event '{name}' fails.")
            return
        carb.log_info(f"Generating spill event: {name}, {selected_spillable_item}.")
        spill_event = self.spill_event_factory(
            name, selected_spillable_item, self.spillable_area_prim_paths, target_size, leak_duration
        )
        spill_event.set_trigger(trigger)
        self.spill_events[name] = spill_event
        self.unspilled_items.remove(selected_spillable_item)
        if trigger:
            trigger.add_callback(lambda t: self.trigger_spill_event(name, t))
            carb.log_info(f"Set up trigger '{trigger.to_dict()}' for spill event: '{name}'.")

    def generate_spill_event_from_property(self, prop: SpillEventProperty):
        if prop.is_value_error():
            carb.log_error("Value has error. Generating spill event fails.")
            return
        data_dict = prop.get_resolved_value()
        name = data_dict["name"]
        spillable_item = data_dict["leakable_item"]["item"]
        target_size = data_dict["leakable_item"]["target_size"]
        leak_duration = data_dict["leakable_item"]["leak_duration"]
        trigger = TriggersManager.get_instance().create_trigger_by_dict(data_dict)
        self.generate_spill_event(name, spillable_item, target_size, leak_duration, trigger)

    def select_random_spillable_item(self):
        if len(self.unspilled_items) == 0:
            return None

        return self.random.choice(self.unspilled_items)

    def trigger_spill_event(self, name: str, trigger: TriggerBase = None):
        if name not in self.spill_events:
            carb.log_error(f"No spill event named {name}. Triggering spill event fails.")
            return
        spill_event = self.spill_events[name]
        spill_event.on_trigger_spill()

        # TODO:: move report to a separate class
        if self.report:
            event_data = {
                "event_type": "Spill Event",
                "spillable_item": spill_event.selected_leakable_item_path,
                "target_size": spill_event.target_size,
                "leak_duration": spill_event.leak_duration,
            }
            self.report.add_event_data(spill_event.name, event_data)
            if trigger:
                self.report.add_trigger_data(spill_event.name, trigger.to_dict())

    # def add_time_trigger(self, name: str, time: float):
    #     if name not in self.spill_events:
    #         carb.log_error("Spill event not found: " + name)
    #         return
    #     spill_event: SpillEvent = self.spill_events[name]

    #     def on_trigger_spill():
    #         spill_event.on_trigger_spill()
    #         carb.log_info("Spill event triggered: " + name)

    #     carb.log_info("Adding spill event time trigger: " + name + " at time: " + str(time))
    #     trigger_sub = self.time_triggers.add_time_trigger(name, time, on_trigger_spill)
    #     spill_event.set_trigger_sub(trigger_sub)

    #     self.incident_report_data["spill_events"][name] = {
    #         "time": time,
    #         "spillable_item": spill_event.selected_leakable_item,
    #     }

    def timeline_callback(self, e: carb.events.IEvent):
        # carb.log_info("SpillEventManager: Timeline callback")
        if e.type == omni.timeline.TimelineEventType.STOP.value:
            self.on_stop()

    def on_stop(self):
        # carb.log_info("SpillEventManager: On stop")
        for spill_event in self.spill_events.values():
            spill_event.on_reset_spill()
