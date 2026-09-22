"""
Config file is designed to be a self-contained module and provides uniform APIs to modify or monitor the loaded value.

    - Overview:
        [ConfigFileFormat] is a class that help defines format and creation for [ConfigFile].
        It also allows other modules to register and deregister its custom [Section] classes.
        A [ConfigFile] consists of a list of [Section].
        Each [Section] defines a collection of [Property] and [PropertyGroup].
        [ConfigFile] and [Section] Defines the structure.
        Each [Property] and [PropertyGroup] manages the actual value and operations.

    - Self-validation:
        [Configfile] performs self-validation on creation including: file format checking, value type checking,
        value verification, auto-filling(missing properties, property groups, sections).
        It is guaranteed that when a config file object is successfully created, it is valid to operate on,
        (correct format, right version, no missings, no type errors).
        The actual validate logic is managed by each [Proeprty] or [ProeprtyGroup] instance, defined by [Section].

    - Interaction:
        It is expected to interact with ConfigFile object through its [Property] or [PropertyGroup] directly.
        Each [Property] and [PropertyGroup] tracks its own error and dirty states.
        Other modules can register listeners for each [Property] or [PropertyGroup] udpate.
        To monitor all [Property] and [PropertyGroup] udpate, register to [ConfigFile] update instead.

    - Flexibility:
        Each [Property] and [PropertyGroup] is configurable (e.g. if it is required, how to verify the value).
        Extend the base class to achieve unique behaviors (e.g. AutoDictProperty, SelectionPropertyGroup).
"""

from __future__ import annotations
import carb
from ..file_util import YamlFileUtil
from .property import *
from .section import *
from .util import *


@dataclass
class ConfigFile(UpdateNotifier):
    # File path
    file_path: str = None
    # Data
    header: str = None
    version: str = None
    sections: List[Section] = field(default_factory=lambda: [])

    def get_section(self, name: str):
        """
        Get section by the section name.
        """
        if not name:
            return None
        for sec in self.sections:
            if name == sec.name:
                return sec
        return None

    def get_property(self, section_name: str, property_name: str):
        section = self.get_section(section_name)
        if not section:
            return None
        return section.get_property(property_name)

    def get_property_group(self, section_name: str, property_group_name: str):
        section = self.get_section(section_name)
        if not section:
            return None
        return section.get_property_group(property_group_name)

    def is_dirty(self):
        """
        Check if any section is dirty.
        """
        return any(section.is_dirty() for section in self.sections)

    def reset_dirty(self):
        """
        Mark all properties in each section as not dirty.
        """
        for section in self.sections:
            section.reset_dirty()

    def to_yaml_data(self):
        """
        Get yaml data representation for the config file.
        """
        yaml_data = {"version": self.version}
        for section in self.sections:
            yaml_data.update(section.to_yaml_data())
        return yaml_data

    def save(self) -> bool:
        """
        Save the config file at its current file path.
        Return True if save succeeds.
        """
        if not self._save_impl(self.file_path):
            return False
        self.reset_dirty()
        return True

    def save_as(self, file_path: str) -> bool:
        """
        Create and save a copy of this config file into a new folder.
        Return True if save succeeds.
        """
        return self._save_impl(file_path)

    def _save_impl(self, file_path: str) -> bool:
        yaml_data = self.to_yaml_data()
        raw_yaml = ConfigFileUtil.add_header(yaml_data, self.header)
        if not YamlFileUtil.save_yaml(file_path, raw_yaml):
            carb.log_error(f"Save config file to {file_path} fails'.")
            return False
        return True


class ConfigFileFormat:
    """
    Class for hanlding config file format registery and instancing.
    Each instance represents a type of config file format.
    """

    def __init__(self, name: str, required_header: str, required_version: str):
        self._name = name  # The name for this format
        self._required_header: str = required_header
        self._required_version: str = required_version
        self._registered_sections: List[Section] = []

    def register_section(self, section_cls_list: List[Type[Section]]):
        for section_cls in section_cls_list:
            if section_cls not in self._registered_sections:
                self._registered_sections.append(section_cls)
                carb.log_info(f"Section {section_cls.name} is registered to Config File Format '{self._name}'.")
            else:
                carb.log_warn(
                    f"Section {section_cls.name} was registered to Config File Format '{self._name}' before. Skip registering."
                )

    def deregister_section(self, section_cls_list: List[Type[Section]]):
        for section_cls in section_cls_list:
            if section_cls not in self._registered_sections:
                carb.log_warn(f"Section {section_cls.name} is registered to Config File Format '{self._name}'.")
            else:
                self._registered_sections.remove(section_cls)
                carb.log_info(f"Section {section_cls.name} has removed from Config File Format '{self._name}'.")

    def load_config_file(self, file_path) -> ConfigFile:
        """
        Create a config file instance by file_path.
        Return None if wrong yaml or wrong sections.
        """
        # Yaml check
        raw_yaml = YamlFileUtil.load_yaml(file_path)
        if not raw_yaml:
            return None
        # Check header
        if self._required_header not in raw_yaml:
            carb.log_error(
                f"Yaml file {file_path} does not contain header:{self._required_header} for Config File Format '{self._name}'."
            )
            return None
        yaml_data = ConfigFileUtil.remove_header(raw_yaml, self._required_header)
        if not yaml_data:
            return None
        # Check version
        if not ConfigFileUtil.check_version(yaml_data, self._required_version):
            return None
        # Create sections
        sections = []
        for sec_class in self._registered_sections:
            sec = None
            if sec_class.name in yaml_data:
                sec = sec_class.create_instance(file_path, yaml_data[sec_class.name])
                if not sec:
                    carb.log_warn(f"Unable to create section '{sec_class.name}' for Config File Format '{self._name}'.")
                    continue
            elif sec_class.is_required:
                sec = sec_class.create_instance(file_path, None)  # For missing required sections
            if sec:
                sections.append(sec)
        # Create config file
        instance = ConfigFile(
            file_path=file_path, header=self._required_header, version=yaml_data["version"], sections=sections
        )
        for sec in instance.sections:
            # Config file monitors all present Properties udpates
            all_present_props = sec.get_all_present_properties()
            for prop in all_present_props:
                prop.register_update_func(instance.notify_update)
            # Config file also monitors all present PropertyGroups updates
            all_present_groups = sec.get_all_present_property_groups()
            for group in all_present_groups:
                group.register_update_func(instance.notify_update)
        return instance
