import omni.ui as ui
from omni.kit.menu.utils import MenuHelperWindow
from isaacsim.replicator.agent.ui.agent_sdg.character_panel import CharacterPanel
from isaacsim.replicator.agent.ui.agent_sdg.config_panel import ConfigPanel
from isaacsim.replicator.agent.ui.agent_sdg.replicator_panel import ReplicatorPanel
from isaacsim.replicator.agent.ui.agent_sdg.robot_panel import RobotPanel
from isaacsim.replicator.agent.ui.agent_sdg.response_panel import ResponsePanel
from isaacsim.replicator.agent.ui.agent_sdg.incident_event_panel import IncidentEventPanel
from isaacsim.replicator.agent.ui.settings import *
from isaacsim.replicator.agent.ui.ui_components.style import AGENT_SDG_STYLE
from isaacsim.replicator.agent.ui.ui_util import *


class AgentSDGWindow(MenuHelperWindow):
    def __init__(self, sim_manager):
        super().__init__(title="Actor SDG", width=600, height=600, dockPreference=ui.DockPreference.RIGHT)

        # Initialize global properties
        # - Global properties will be passed to each panel by reference
        # - Each panel communicate by these shared properties
        self.setup_events()
        self.setup_variables()
        # SimulationManager object
        self.variables[GLOBAL_VARIABLES.CORE_SIM_MANAGER] = sim_manager
        self.frame.set_style(AGENT_SDG_STYLE)
        self.frame.set_build_fn(self._build_ui)

    def destroy(self) -> None:
        # GC for the window
        self._config_panel = None
        self._scene_panel = None
        self._response_panel = None
        self._sensor_panel = None
        self._character_panel = None
        self._robot_panel._command_editor = None
        self._robot_panel._command_selection = None
        self._robot_panel = None
        self._replicator_panel = None
        self._incident_event_panel = None


    def setup_events(self):
        self.events = {}
        for event in GLOBAL_EVENTS:
            self.events[event] = EventHandler()

    def setup_variables(self):
        self.variables = {}
        for var in GLOBAL_VARIABLES:
            self.variables[var] = 0

    def _build_ui(self):
        self.deferred_dock_in("Stage", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self.dock_order = 3
        with self.frame:
            with ui.ScrollingFrame():
                with ui.VStack(spacing=0, height=0):
                    # Initialize panels
                    self._config_panel = ConfigPanel(self.events, self.variables)
                    self._replicator_panel = ReplicatorPanel(self.events, self.variables)
                    self._character_panel = CharacterPanel(self.events, self.variables)
                    self._robot_panel = RobotPanel(self.events, self.variables)
                    self._response_panel = ResponsePanel(self.events, self.variables)
                    self._incident_event_panel = IncidentEventPanel(self.events, self.variables)
                    # Build panels
                    self._config_panel.build_ui_frame()
                    self._replicator_panel.build_ui_frame()
                    self._character_panel.build_ui_frame()
                    self._robot_panel.build_ui_frame()
                    self._response_panel.build_ui_frame()
                    self._incident_event_panel.build_ui_frame()
                    # Start from config panel
                    self._config_panel.on_start()
