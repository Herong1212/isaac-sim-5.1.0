"""
    Definitions of basic [Section].
"""

from abc import ABC
from dataclasses import dataclass
from typing import ClassVar, List
import carb

from .property import *
from .util import ConfigFileError


@dataclass
class Section(ABC):
    """
    Base class to represent a section in config file.
        - Inherient this class to define specific [Property] and [PropertyGroup].
    """

    # Class description (to be filled up by sub classes)
    name: ClassVar[str]
    is_required: ClassVar[bool]
    # internal variables
    _config_file_path: str

    @classmethod
    def create_instance(cls, file_path: str, yaml_data: dict):
        """
        Create Section instance from given yaml.
        Return None if property check or proeprty group check fails.
        Will perform auto fill up for present and required properties and property groups.
        """
        try:
            instance = cls(file_path)
            # Set up Properties
            all_props = instance.get_all_properties()
            for prop in all_props:
                if yaml_data:
                    prop.setup_by_yaml(yaml_data)
                if not prop.is_setup() and prop.is_required:
                    prop.setup_by_default()
            # Set up PropertyGroups
            all_groups = instance.get_all_property_groups()
            for group in all_groups:
                if yaml_data:
                    group.setup_by_yaml(yaml_data)
                if not group.is_setup() and group.is_required:
                    group.setup_by_default()
        except ConfigFileError as ex:
            carb.log_error(ex)
            return None
        return instance

    def get_property(self, name: str) -> Property:
        """
        Get Property from the section by name.
        """
        if not name:
            return None
        all_properties = self.get_all_properties()
        for prop in all_properties:
            if prop.name == name:
                return prop
        return None

    def get_all_properties(self) -> List[Property]:
        """
        Get all Properties from the section.
        """
        result = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if attr and isinstance(attr, Property):
                result.append(attr)
        return result

    def get_all_present_properties(self) -> List[Property]:
        """
        Get all present Properties in this section instance.
        Properties are present if their values are set (not None).
        """
        all_properties = self.get_all_properties()
        return [prop for prop in all_properties if prop.is_setup()]

    def get_property_group(self, name) -> PropertyGroup:
        """
        Get property group by section by name.
        """
        all_groups = self.get_all_property_groups()
        for group in all_groups:
            if group.name == name:
                return group
        return None

    def get_all_property_groups(self) -> List[PropertyGroup]:
        """
        Get all PropertyGroups from the section.
        """
        result = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if attr and isinstance(attr, PropertyGroup):
                result.append(attr)
        return result

    def get_all_present_property_groups(self) -> List[PropertyGroup]:
        all_groups = self.get_all_property_groups()
        return [group for group in all_groups if group.is_setup()]

    def to_yaml_data(self) -> dict:
        """
        Get yaml data representation for the section.
        """
        data = {}
        props = self.get_all_present_properties()
        for prop in props:
            data.update(prop.to_yaml_data())
        groups = self.get_all_present_property_groups()
        for group in groups:
            data.update(group.to_yaml_data())
        return {self.name: data}

    def is_dirty(self) -> bool:
        """
        Check if any Property or PropertyGroup is dirty
        """
        if any(prop.is_value_dirty() for prop in self.get_all_present_properties()):
            return True
        return any(group.is_dirty() for group in self.get_all_present_property_groups())

    def reset_dirty(self):
        """
        Reset all properties dirty states.
        """
        all_properties = self.get_all_present_properties()
        for prop in all_properties:
            prop.reset_dirty()
        all_groups = self.get_all_present_property_groups()
        for group in all_groups:
            group.reset_dirty()
