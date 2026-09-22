import omni, carb
import omni.kit.app
import carb.eventdispatcher
import os
import omni
from pxr import Sdf
import omni.kit.commands

from omni.metropolis.utils.semantics_util import SemanticsUtils

from random import Random
from typing import Callable, List

from omni.metropolis.utils.triggers.core import TriggerBase, TriggersManager

from ..config_file_defines import PyroEventProperty

from ..incident_report import IncidentReport

from ..settings import IncidentSettings

from .pyro_event import PyroEvent

from .scene_tagging import SceneTaggingData, AttributeUSDTagger


class PyroEventManager:
    """
    This class is responsible for managing topple events in the scene.
    It exposes functions for adding topple events, triggering them, and observing them.
    It also holds the data for the incident report.
    """

    def __init__(
        self,
        scene_tagging_data_factory: Callable[[], SceneTaggingData],
        attribute_usd_tagger_factory: Callable[[], AttributeUSDTagger],
        pyro_event_factory: Callable[[str, str, float], PyroEvent],
        data_path: str,
        random_seed=123456,
        report: IncidentReport = None,
    ):
        self._scene_tagging_data: SceneTaggingData = None
        self.pyro_events: dict = None
        self.unflammed_items = None
        self.random = None
        self.triggers: dict = None  # (event name, trigger instance) pair
        self.report = report
        self.data_path = data_path
        self.pyro_settings_prim_path = Sdf.Path("/PyroDemonSettings")
        self.scene_tagging_data_factory = scene_tagging_data_factory
        self.attribute_usd_tagger_factory = attribute_usd_tagger_factory
        self.pyro_event_factory = pyro_event_factory

        self.setup(random_seed)

    def set_random_seed(self, random_seed):
        self.random = Random(random_seed)

    def destroy(self):
        self._scene_tagging_data: SceneTaggingData = None
        if self.pyro_events:
            carb.log_info(f"[IRI.PyroEventManager]Destroying {len(self.pyro_events)} pyro events")
            for event in self.pyro_events.values():
                event.destroy()
        self.pyro_events = None
        self.unflammed_items = None
        self.random = None
        if self.triggers:
            for trigger in self.triggers.values():
                trigger.destroy()
        self.triggers = None
        self.report = None

    def setup(self, random_seed):

        usd_tagger = self.attribute_usd_tagger_factory()
        self._scene_tagging_data = usd_tagger.Read()
        if not self._scene_tagging_data:
            carb.log_error("Could not read topple tags from scene")
            return

        self.unflammed_items = set()
        for flammable_item_collection in self._scene_tagging_data.flammable_item_prim_paths_by_type.values():
            self.unflammed_items.update(flammable_item_collection)

        self.pyro_events = {}

        self.triggers = {}

        self.random = Random(random_seed)

        file_path = os.path.join(self.data_path, "warehouse_fire_settings.usda")

        stage = omni.usd.get_context().get_stage()
        if not stage.GetPrimAtPath(self.pyro_settings_prim_path):
            carb.log_info("Creating pyro settings payload")
            result, payload_prim = omni.kit.commands.execute(
                "CreatePayload",
                path_to=self.pyro_settings_prim_path,
                asset_path=file_path,
                usd_context=omni.usd.get_context(),
            )

            if not result:
                carb.log_error("Failed to create pyro settings payload")
                return

        # stage = omni.usd.get_context().get_stage()
        # stage.DefinePrim(Sdf.Path('/World/PyroDemonSettings'), "Xform")

        # omni.kit.commands.execute(
        #     'AddPayload',
        #     stage=omni.usd.get_context().get_stage(),
        #     prim_path=Sdf.Path('/World/PyroDemonSettings'),
        #     payload=Sdf.Payload(file_path)
        # )

        # setup_pyro_settings()
        # stage = omni.usd.get_context().get_stage()
        # parent_prim = stage.DefinePrim("/World/PyroDemonSettings", "Xform")

        # # print("Pyro Demon file_path: ", file_path)
        # parent_prim.GetReferences().AddReference(file_path)
        # todo: there is a bug with omniverse where the file path will be omniverse://
        # so we need to spawn these assets a different way, or get them to fix the bug
        # https://jirasw.nvidia.com/browse/METROPERF-787

    def generate_pyro_event(
        self,
        name: str,
        selected_flammable_item_prim_path: str,
        pyro_nearby_radius: float = 0.0,
        trigger: TriggerBase = None,
    ):
        if selected_flammable_item_prim_path == IncidentSettings.RANDOM_FLAMMABLE_ITEM:
            selected_flammable_item_prim_path = self.select_random_unflammed_item()
        if selected_flammable_item_prim_path not in self.unflammed_items:
            carb.log_error(
                f"'{selected_flammable_item_prim_path}' is not a tagged prim. Generating pyro event '{name}' fails."
            )
            return
        carb.log_info(f"Generating pyro event: {name} {selected_flammable_item_prim_path}.")
        pyro_event = self.pyro_event_factory(name, selected_flammable_item_prim_path, pyro_nearby_radius)
        self.pyro_events[name] = pyro_event
        self.unflammed_items.difference_update(pyro_event.selected_flammable_item_prim_path)
        if trigger:
            trigger.add_callback(lambda t: self.trigger_pyro_event(name))
            self.triggers[name] = trigger
            carb.log_info(f"Set up trigger '{trigger.to_dict()}' for pyro event ' {name}'.")

    def generate_pyro_event_from_property(self, prop: PyroEventProperty):
        if prop.is_value_error():
            carb.log_error("Value has error. Generating pyro event fails.")
            return
        data_dict = prop.get_resolved_value()
        name = data_dict["name"]
        flammable_item_prim_path = data_dict["flammable_item"]["item"]
        nearby_radius = 1.0 # data_dict["flammable_item"]["flammable_nearby_radius"]
        trigger = TriggersManager.get_instance().create_trigger_by_dict(data_dict)
        self.generate_pyro_event(name, flammable_item_prim_path, nearby_radius, trigger)

    def select_random_unflammed_item(self):
        if not self.unflammed_items:
            return None
        return self.random.choice(list(self.unflammed_items))

    def trigger_pyro_event(self, name: str, trigger: TriggerBase = None):
        if name not in self.pyro_events:
            carb.log_warn(f"No pyro event named {name}. Triggering pyro event fails.")
            return
        pyro_event = self.pyro_events[name]
        pyro_event.trigger_pyro_event()

        # TODO:: move report to a separate class
        if self.report:
            event_data = {
                "event_type": "Fire Event",
                "flame_emitter": pyro_event.selected_flammable_item_prim_path,
                "pyro_nearby_radius": pyro_event.pyro_nearby_radius,
            }
            self.report.add_event_data(pyro_event.name, event_data)
            if trigger:
                self.report.add_trigger_data(pyro_event.name, trigger.to_dict())

        # stage = omni.usd.get_context().get_stage()
        # flaming_item_prim_path = pyro_event.selected_flammable_item_prim_path
        # SemanticsUtils.add_update_prim_metrosim_semantics([stage.GetPrimAtPath(flaming_item)], "flaming_item")
        # SemanticsUtils.add_update_semantics_timecode(flame_emitter, "flaming_item", "class", "", 60 * time)
