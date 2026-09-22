from ..incident_manager import IncidentManager
from ..config_file_loader import ConfigFileLoader

from .config_panel import ConfigPanel
from .event_panel import EventPanel

from omni.metropolis.utils.ui_util import UIStyleUtil

import omni.ui as ui
from omni.kit.menu.utils import MenuHelperWindow


class IncidentConfigFileWindow(MenuHelperWindow):
    def __init__(self, config_file_loader: ConfigFileLoader, incident_manager: IncidentManager):
        super().__init__(title="Event Config File", width=600, height=600, dockPreference=ui.DockPreference.RIGHT)
        self._config_file_loader = config_file_loader
        self._incident_manager = incident_manager

        self._config_panel = ConfigPanel(self._config_file_loader, self._incident_manager)
        self._event_panel = EventPanel(
            self._config_file_loader.CONFIG_FILE_CHANGED_EVENT, self._config_file_loader.CONFIG_FILE_SAVED_EVENT
        )
        self.frame.set_style(UIStyleUtil.DEFAULT_WINDOW_STYLE)
        self.frame.set_build_fn(self._build_ui)

    def destroy(self) -> None:
        self._config_panel.destroy()
        self._config_panel = None
        self._event_panel.destroy()
        self._event_panel = None

        if self._incident_manager:
            self._incident_manager.destroy()
            self._incident_manager = None
        self._config_file_loader = None

    def _build_ui(self):
        self.deferred_dock_in("Stage", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self.dock_order = 6
        with self.frame:
            with ui.ScrollingFrame():
                with ui.VStack(spacing=0, height=0):
                    self._config_panel.build_ui_frame()
                    self._event_panel.build_ui_frame()
                    self._config_file_loader.load_default_config_file()
