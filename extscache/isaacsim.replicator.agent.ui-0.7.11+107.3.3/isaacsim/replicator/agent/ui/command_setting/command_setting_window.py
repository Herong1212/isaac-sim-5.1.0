import omni.ui as ui
from omni.kit.menu.utils import MenuHelperWindow
from isaacsim.replicator.agent.ui.command_setting.general_setting_panel import GeneralCommandSettingPanel
from isaacsim.replicator.agent.ui.command_setting.custom_command_panel import CustomCommandPanel
from isaacsim.replicator.agent.ui.command_setting.command_randomization_panel import CommandRandomizationPanel
from isaacsim.replicator.agent.ui.settings import *
from isaacsim.replicator.agent.ui.ui_components.style import AGENT_SDG_STYLE
from isaacsim.replicator.agent.ui.ui_util import *


class CommandSettingWindow(MenuHelperWindow):
    def __init__(self, sim_manager):
        super().__init__(title="Command Setting", width=600, height=600, dockPreference=ui.DockPreference.RIGHT)
        # Initialize global properties
        # - Global properties will be passed to each panel by reference
        # - Each panel communicate by these shared properties
        self.setup_events()
        self.setup_variables()
        # SimulationManager object
        self.variables[GLOBAL_VARIABLES.CORE_SIM_MANAGER] = sim_manager
        self.frame.set_style(AGENT_SDG_STYLE)
        self.frame.set_build_fn(self._build_ui)

    def setup_events(self):
        self.events = {}
        for event in GLOBAL_EVENTS:
            self.events[event] = EventHandler()

    def setup_variables(self):
        self.variables = {}
        for var in GLOBAL_VARIABLES:
            self.variables[var] = 0

    def destroy(self) -> None:
        self._custom_command_panel = None
        self._command_randomization_panel = None

    def _build_ui(self):
        self.deferred_dock_in("Stage", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self.dock_order = 4
        with self.frame:
            with ui.ScrollingFrame():
                with ui.VStack(spacing=0, height=0):
                    self._general_setting_panel = GeneralCommandSettingPanel()
                    self._general_setting_panel.build_ui_frame()
                    self._custom_command_panel = CustomCommandPanel()
                    self._custom_command_panel.build_ui_frame()
                    # Initialize panels
                    self._command_randomization_panel = CommandRandomizationPanel(self.events, self.variables)
                    # Build panels
                    self._command_randomization_panel.build_ui_frame()
