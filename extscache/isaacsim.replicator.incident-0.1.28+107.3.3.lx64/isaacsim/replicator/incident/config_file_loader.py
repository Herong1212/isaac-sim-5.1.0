import carb
import carb.eventdispatcher
from .settings import ExtInfos
from omni.metropolis.utils.config_file.core import ConfigFile, ConfigFileFormat


class ConfigFileLoader:
    """Helper class for incident config file laod/save and event notification"""

    CONFIG_FILE_CHANGED_EVENT = "isaacsim.replicator.incident.CONFIG_FILE_CHANGED"  # f(config_file)
    CONFIG_FILE_SAVED_EVENT = "isaacsim.replicator.incident.CONFIG_FILE_SAVED"      # f(config_file)

    def __init__(self, format: ConfigFileFormat):
        self._config_file_format = format
        self._config_file: ConfigFile = None
        self._config_file_path: str = ""

    def load_default_config_file(self):
        default_config_file_path = f"{ExtInfos.ext_path}/config/default_config.yaml"
        self.load_config_file(default_config_file_path)

    def load_config_file(self, file_path: str) -> bool:
        self._config_file_path = file_path
        self._config_file = self._config_file_format.load_config_file(file_path)
        # Dispatch change event regardless of loading result
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(
            event_name=ConfigFileLoader.CONFIG_FILE_CHANGED_EVENT,
            payload={"Payload": {"config_file": self._config_file}},
        )
        if self._config_file:
            return True
        else:
            return False

    def save_config_file(self) -> bool:
        if not self._config_file:
            carb.log_error("Unable to save due to no config file is loaded.")
            return False
        if not self._config_file.save():
            return False
        # Dispatch save event only when save succeeds
        carb.eventdispatcher.get_eventdispatcher().dispatch_event(
            event_name=ConfigFileLoader.CONFIG_FILE_SAVED_EVENT,
            payload={"Payload": {"config_file": self._config_file}},
        )
        return True

    def save_as_config_file(self, file_path) -> bool:
        if not self._config_file:
            carb.log_error("Unable to save as due to no config file is loaded.")
            return False
        if not self._config_file.save_as(file_path):
            return False
        # Load the new config file
        if not self.load_config_file(file_path):
            return False
        return True

    def get_config_file(self) -> ConfigFile:
        return self._config_file

    def get_config_file_path(self) -> str:
        return self._config_file_path