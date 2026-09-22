import carb

from typing import Callable, List

from random import Random

from omni.metropolis.utils.triggers.core import TriggerBase, TriggersManager

from ..incident_report import IncidentReport

from ..config_file_defines import ToppleEventProperty

from ..settings import IncidentSettings

from .topple_event_observer import ToppleEventObserverManager
from .topple_event_setup import ToppleEventSetup

from .scene_tagging import SceneTaggingData, AttributeUSDTagger

from ..sceneview_ui_helper import BBoxDrawerHelper


class ToppleEventManager:
    """
    This class is responsible for managing topple events in the scene.
    It exposes functions for adding topple events, triggering them, and observing them.
    It also holds the data for the incident report.
    """

    def __init__(
        self,
        attribute_usd_tagger_factory: Callable[[], AttributeUSDTagger],
        topple_event_observer_manager_factory: Callable[[], ToppleEventObserverManager],
        topple_event_setup_factory: Callable[[], ToppleEventSetup],
        random_seed: int = 123456,
        report: IncidentReport = None,
    ):
        self._scene_tagging_data: SceneTaggingData = None
        self.topple_events: dict = None
        self.untoppled_items = None
        self.random = None
        self.triggers: dict = None  # (event name, trigger instance) pair
        self.topple_event_observer_manager: ToppleEventObserverManager = None
        self.report = report
        self.attribute_usd_tagger_factory = attribute_usd_tagger_factory
        self.topple_event_observer_manager_factory = topple_event_observer_manager_factory
        self.topple_event_setup_factory = topple_event_setup_factory

        self.setup(random_seed)

    def set_random_seed(self, random_seed):
        self.random = Random(random_seed)

    def destroy(self):
        self._scene_tagging_data: SceneTaggingData = None
        if self.topple_events:
            for event in self.topple_events.values():
                event.destroy()

        self.topple_events = None
        self.untoppled_items = None
        self.random = None
        self.report = None
        for trigger in self.triggers.values():
            trigger.destroy()
        self.triggers = None
        if self.topple_event_observer_manager:
            self.topple_event_observer_manager.destroy()
        self.topple_event_observer_manager = None

    def setup(self, random_seed):
        self.topple_event_observer_manager = self.topple_event_observer_manager_factory()

        usd_tagger = self.attribute_usd_tagger_factory()
        self._scene_tagging_data = usd_tagger.Read()
        if not self._scene_tagging_data:
            carb.log_error("Could not read topple tags from scene")
            return

        self.untoppled_items = set()
        for loose_item_collection in self._scene_tagging_data.loose_item_prim_paths_by_type.values():
            self.untoppled_items.update(loose_item_collection)

        self.topple_events = {}

        self.triggers = {}

        self.random = Random(random_seed)

    def select_random_untoppled_item(self):
        if len(self.untoppled_items) < 1:
            carb.log_error("No available topple items to generate event with")
            return None

        # loose_item_idx = self.random.randint(0, len(self.untoppled_items)-1)
        return self.random.choice(sorted(list(self.untoppled_items)))  # noqa: C901, C414

    def generate_topple_event(
        self, name: str, selected_loose_item: str, topple_nearby_radius: float = 0.0, trigger: TriggerBase = None
    ):
        if selected_loose_item == IncidentSettings.RANDOM_LOOSE_ITEM:
            selected_loose_item = self.select_random_untoppled_item()
        if selected_loose_item not in self.untoppled_items:
            carb.log_error(f"'{selected_loose_item}' is not a tagged prim. Generating topple event '{name}' fails.")
            return
        carb.log_info(f"Generate topple event: {name}, {selected_loose_item}.")
        topple_event = self.topple_event_setup_factory(
            self._scene_tagging_data, name, selected_loose_item, self.random, topple_nearby_radius
        )
        self.topple_events[name] = topple_event

        self.untoppled_items.difference_update(topple_event.selected_loose_items)

        if trigger:
            trigger.add_callback(lambda t: self.trigger_topple_event(name, t))
            self.triggers[name] = trigger
            carb.log_info(f"Set up trigger '{trigger.to_dict()}' for topple event '{name}'.")

    def generate_topple_event_from_property(self, prop: ToppleEventProperty):
        if prop.is_value_error():
            carb.log_error("Value has error. Generating topple event fails.")
            return
        data_dict = prop.get_resolved_value()
        name = data_dict["name"]
        topple_item = data_dict["topple_item"]["item"]
        nearby_radius = data_dict["topple_item"]["topple_nearby_radius"]
        trigger = TriggersManager.get_instance().create_trigger_by_dict(data_dict)
        self.generate_topple_event(name, topple_item, nearby_radius, trigger)

    def trigger_topple_event(self, name: str, trigger: TriggerBase = None):
        if name not in self.topple_events:
            carb.log_error(f"No topple event named {name}. Triggering topple event fails.")
            return
        topple_events = self.topple_events[name]
        topple_events.trigger_topple_event()
        self.topple_event_observer_manager.add_observer(topple_events, self.report, trigger, lambda: None)

    def get_dynamic_obstacle_prim_paths(self) -> List[str]:
        obstacle_prim_paths = []
        for topple_event in self.topple_events.values():
            obstacle_prim_paths.extend(topple_event.selected_loose_items)
        return obstacle_prim_paths


class DebugDrawToppleEventManager(ToppleEventManager):
    def __init__(self, *args, **kwargs):
        self._bbox_drawer: BBoxDrawerHelper = None
        super().__init__(*args, **kwargs)

    def setup(self, random_seed):
        super().setup(random_seed)
        self._bbox_drawer = BBoxDrawerHelper("Debug Topple Demon Drawer")

    def generate_topple_event(self, name: str, selected_loose_item, topple_nearby_radius=0.0):
        super().generate_topple_event(name, selected_loose_item, topple_nearby_radius)
        self._bbox_drawer.draw_AABB_box_around_prim(selected_loose_item)

    def destroy(self):
        super().destroy()
        if self._bbox_drawer:
            self._bbox_drawer.destroy()
        self._bbox_drawer = None
