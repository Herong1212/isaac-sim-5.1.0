import carb
from isaacsim.replicator.incident.ui_components.event_panel import EventPanel
from isaacsim.replicator.agent.core.simulation import SimulationManager
from ..ui_util import GLOBAL_VARIABLES, GLOBAL_EVENTS

class IncidentEventPanel(EventPanel):
    """Wraps EventPanel from IRI to IRA UI convention"""

    CONFIG_CHANGED_EVENT = "isaacsim.replicator.agent.ui.INICIDENT_EVENT_PANEL_CONFIG_FILE_CHANGED"
    CONFIG_SAVED_EVENT = "isaacsim.replicator.agent.ui.INICIDENT_EVENT_PANEL_CONFIG_FILE_SAVED"

    def __init__(self, events, variables):
        super().__init__(IncidentEventPanel.CONFIG_CHANGED_EVENT, IncidentEventPanel.CONFIG_SAVED_EVENT)
        self._variables = variables
        self._events = events
        self._events[GLOBAL_EVENTS.CONFIG_FILE_LOADED].append(self._notify_config_file_changed)
        self._events[GLOBAL_EVENTS.CONFIG_FILE_FAILED_LOADING].append(self._notify_config_file_changed)
        self._events[GLOBAL_EVENTS.CONFIG_FILE_SAVED].append(self._notify_config_file_saved)
        self._sim_manager: SimulationManager = self._variables[GLOBAL_VARIABLES.CORE_SIM_MANAGER]

    def _notify_config_file_changed(self):
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(
            event_name=IncidentEventPanel.CONFIG_CHANGED_EVENT,
            payload={"Payload": {"config_file": self._sim_manager.get_config_file()}},
        )

    def _notify_config_file_saved(self):
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(
            event_name=IncidentEventPanel.CONFIG_SAVED_EVENT,
            payload={"Payload": {"config_file": self._sim_manager.get_config_file()}},
        )

    def build_ui(self):
        super().build_ui()
        self._frame.collapsed = True