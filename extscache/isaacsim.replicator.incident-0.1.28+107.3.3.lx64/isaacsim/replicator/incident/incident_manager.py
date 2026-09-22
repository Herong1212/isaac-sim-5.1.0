import carb.events
import omni, carb
import carb.eventdispatcher
from typing import Callable, List

from omni.metropolis.utils.config_file.core import ConfigFile

from omni.metropolis.utils.timeline_end_extender import TimelineEndExtenderService

from .incident_report import IncidentReport

from .config_file_defines import ToppleEventProperty, PyroEventProperty, SpillEventProperty, IncidentEventSection

from .topple_demon.topple_demon import ToppleEventManager

from .pyro_demon.pyro_event_manager import PyroEventManager

from .spill_demon.spill_event_manager import SpillEventManager



ISAACSIM_REPLICATOR_INCIDENT_COMMAND_PATH = "/exts/isaacsim.replicator.incident/command_settings/command_file_path"


class IncidentManager:
    """
    Manager class for all types of incident events
    """

    SET_UP_INCIDENT_REQUEST_EVENT = carb.events.type_from_string("isaacsim.replicator.incident.SET_UP_INCIDENT_REQUEST")

    def __init__(
        self,
        topple_event_manager_factory: Callable[[int, IncidentReport], ToppleEventManager],
        pyro_event_manager_factory: Callable[[str], PyroEventManager],
        spill_event_manager_factory: Callable[[int], SpillEventManager],
        data_path: str,
    ):
        bus = omni.kit.app.get_app().get_message_bus_event_stream()
        self.incident_request_event_handle = bus.create_subscription_to_push_by_type(
            IncidentManager.SET_UP_INCIDENT_REQUEST_EVENT, self.setup_incidents_from_config_file
        )
        self.topple_event_manager = None
        self.pyro_event_manager = None
        self.data_path = data_path
        self.spill_event_manager = None

        self.topple_event_manager_factory = topple_event_manager_factory
        self.pyro_event_manager_factory = pyro_event_manager_factory
        self.spill_event_manager_factory = spill_event_manager_factory

        # Create report instance
        self._report = IncidentReport()

    def destroy(self):
        self.reset_incident_managers()
        TimelineEndExtenderService.deactivate_timeline_end_extender()

    def reset_incident_managers(self):
        if self.topple_event_manager:
            self.topple_event_manager.destroy()
            self.topple_event_manager = None
        if self.pyro_event_manager:
            self.pyro_event_manager.destroy()
            self.pyro_event_manager = None
        if self.spill_event_manager:
            self.spill_event_manager.destroy()
            self.spill_event_manager = None

    def setup_incidents_from_config_file(self, random_seed: int, incident_event_section: IncidentEventSection):
        TimelineEndExtenderService.activate_timeline_end_extender()
        # Reset the last set up (if it exists)
        self.reset_incident_managers()
        # Events set up
        incident_list = incident_event_section.get_property_group("event_list")
        for event_prop in incident_list.data_group:
            if isinstance(event_prop, ToppleEventProperty):
                if not self.topple_event_manager:
                    self.topple_event_manager = self.topple_event_manager_factory(
                        random_seed=random_seed, report=self._report
                    )
                self.topple_event_manager.generate_topple_event_from_property(event_prop)
            elif isinstance(event_prop, PyroEventProperty):
                if not self.pyro_event_manager:
                    self.pyro_event_manager = self.pyro_event_manager_factory(
                        data_path=self.data_path, random_seed=random_seed, report=self._report
                    )
                self.pyro_event_manager.generate_pyro_event_from_property(event_prop)
            elif isinstance(event_prop, SpillEventProperty):
                if not self.spill_event_manager:
                    self.spill_event_manager = self.spill_event_manager_factory(
                        random_seed=random_seed, report=self._report
                    )
                self.spill_event_manager.generate_spill_event_from_property(event_prop)
            else:
                carb.log_warn(f"Event '{event_prop.name}' is not recognized as a type of incident event.")

    def get_incident_report(self) -> IncidentReport:
        return self._report

    def get_dynamic_obstacle_prim_paths(self) -> List[str]:
        topple_event_manager = self.topple_event_manager
        if topple_event_manager:
            return topple_event_manager.get_dynamic_obstacle_prim_paths()
        return []
