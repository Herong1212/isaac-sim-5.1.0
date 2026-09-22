import asyncio

import carb
import carb.settings
import omni.ext
import omni.kit.app
from typing import Callable

from omni.metropolis.utils.config_file.core import ConfigFileFormat
from isaacsim.replicator.incident.config_file_defines import IncidentEventSection
from isaacsim.replicator.incident.extension import get_instance as get_incident_ext_instance
from .agent_manager import AgentManager
from .settings import AssetPaths, Infos, GlobalValues
from .config_file import get_all_section_cls

_extension_instance = None
_ext_id = None
_ext_path = None
_ext_version = None


def get_instance():
    return _extension_instance


def get_ext_id():
    return _ext_id


def get_ext_path():
    return _ext_path


def get_ext_version():
    return _ext_version


class Main(omni.ext.IExt):

    def on_startup(self, ext_id):
        import warp

        warp.init()

        ext_manager = omni.kit.app.get_app().get_extension_manager()

        # Set up global variables
        global _extension_instance
        _extension_instance = self
        global _ext_id
        _ext_id = ext_id
        global _ext_path
        _ext_path = ext_manager.get_extension_path(ext_id)
        global _ext_version
        _ext_version = str(ext_id).split("-")[-1]
        # Init Infos
        Infos.ext_version = _ext_version
        Infos.ext_path = _ext_path
        # Handle async startup tasks
        if carb.settings.get_settings().get_as_bool(AssetPaths.USE_ISAAC_SIM_ASSET_ROOT_SETTING):
            AssetPaths.cache_isaac_sim_asset_root_path()
            if not AssetPaths.cached_isaac_sim_asset_root_path:
                carb.log_warn("Isaac Sim asset root path is not set. Will use fallback asset paths instead.")
        # Ensure the global agent manager instance is initialized
        self._agent_manager = AgentManager.get_instance()
        # Create config file format
        GlobalValues.config_file_format = ConfigFileFormat(
            name="IRA config file format", required_header="isaacsim.replicator.agent", required_version=_ext_version
        )
        # Register self-defined sections
        GlobalValues.config_file_format.register_section(get_all_section_cls())
        # TODO:: decouple with IRI
        GlobalValues.config_file_format.register_section([IncidentEventSection])

        # To avoid IRI UI shows on top of IRA UI
        incident_ext = get_incident_ext_instance()
        if incident_ext:
            incident_ext.hide_windows()

    def on_shutdown(self):
        global _extension_instance
        _extension_instance = None
        global _ext_id
        _ext_id = None
        global _ext_path
        _ext_path = None

        if self._agent_manager:
            self._agent_manager = None

        # Config file format
        self._config_file_format = None
