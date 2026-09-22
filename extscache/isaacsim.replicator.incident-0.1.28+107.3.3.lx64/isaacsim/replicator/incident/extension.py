import omni.ext
import os
import asyncio

from omni.kit.menu.utils import MenuHelperExtensionFull

from omni.metropolis.utils.config_file.core import ConfigFileFormat

from omni.metropolis.utils.triggers.core import TriggersManager

from .incident_manager import IncidentManager
from .scene_tagging_ui import SceneTaggingUIMenu

# from .spill_demon.spill_manipulator_ui import SpillDemonManipulatorUI
from .spill_demon.spill_scene_tagging_ui import SpillSceneTaggingUIMenu
from omni.kit.menu.utils import MenuHelperExtensionFull

from .ui_components.config_file_window import IncidentConfigFileWindow

from .composition_root import CompositionRoot

from .settings import GlobalValues, ExtInfos

from .config_file_loader import ConfigFileLoader

from .config_file_defines import IncidentGlobalSection, IncidentEventSection

from .incident_trigger import IncidentTrigger


_ext_instance = None


def get_instance():
    return _ext_instance


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class IncidentExt(omni.ext.IExt):
    """
    This extension holds a UI window for event scene tagging and managers for event types.
    """

    data_path: str = None

    def __init__(self):
        super().__init__()
        # self._topple_group_data_ui_window : ToppleGroupDataUIWindow = None
        # self._topple_ui_viewer_window : ToppleUIViewerWindow = None
        self._menu_helper_extension: MenuHelperExtensionFull = None
        self._tagger_window_idx = -1
        self._config_window_idx = -1
        self._incident_manager: IncidentManager = None
        self._config_file_loader: ConfigFileLoader = None
        self._composition_root: CompositionRoot = None

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.

    def on_startup(self, ext_id):
        print("[isaacsim.replicator.incident] started")

        global _ext_instance
        _ext_instance = self

        # Save ExtInfos
        ExtInfos.ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id)
        ExtInfos.ext_ver =  str(ext_id).split("-")[-1]

        IncidentExt.data_path = os.path.join( ExtInfos.ext_path , "data")

        self._menu_helper_extension = MenuHelperExtensionFull()

        self._tagger_window_idx = self._menu_helper_extension.menu_startup(
            lambda: SceneTaggingUIMenu(), "Event Scene Tagger", "Event Scene Tagger", "Tools/Action and Event Data Generation"
        )

        self._composition_root = CompositionRoot(IncidentExt.data_path)

        # Register incident trigger
        TriggersManager.get_instance().register_trigger_type([IncidentTrigger])

        # Incident Manager
        self._incident_manager = self._composition_root.create_incident_manager()
        GlobalValues.incident_manager = self._incident_manager

        # Define config file format
        GlobalValues.config_file_format = ConfigFileFormat(
            name="IRI config file format",
            required_header="isaacsim.replicator.incident",
            required_version=ExtInfos.ext_ver,
        )
        GlobalValues.config_file_format.register_section([IncidentGlobalSection, IncidentEventSection])

        # Config File Loader
        self._config_file_loader = ConfigFileLoader(GlobalValues.config_file_format)
        GlobalValues.incident_manager = self._config_file_loader

        # Config file window
        self._config_window_idx = self._menu_helper_extension.menu_startup(
            lambda: IncidentConfigFileWindow(self._config_file_loader, self._incident_manager),
            "Event Config File", "Event Config File", "Tools/Action and Event Data Generation", verbose=False
        )
        self._menu_helper_extension.show_window("", True, self._config_window_idx)


    def on_shutdown(self):
        print("[isaacsim.replicator.incident] shutdown")
        self._menu_helper_extension.menu_shutdown()
        self._tagger_window_idx = -1
        self._config_window_idx = -1
        self._incident_manager.destroy()
        self._incident_manager = None
        self._composition_root = None

        # Deregister incident config file format
        GlobalValues.config_file_format = None
        # Deregister incident trigger
        TriggersManager.get_instance().deregister_trigger_type([IncidentTrigger])

    def get_incident_manager(self):
        return self._incident_manager

    def create_incident_manager(self) -> IncidentManager:
        return self._composition_root.create_incident_manager()

    def hide_windows(self):
        self._menu_helper_extension.show_window("", False, self._tagger_window_idx)
        self._menu_helper_extension.show_window("", False, self._config_window_idx)