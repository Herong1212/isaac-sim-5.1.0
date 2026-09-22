"""
    Definitions of basic [Property] and [PropertyGroup].
"""

from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass, field, replace
from typing import Generic, List, Type, TypeVar

import carb
from ..common_util import UpdateNotifier
from ..file_util import FileUtil
from .util import PropertyVerifyUtil, ConfigFileError


T = TypeVar("T")


@dataclass
class Property(UpdateNotifier, Generic[T]):
    """
    Base class to represent a (key, value) pair in each section of config file.
        - It maintains dirty state (if it gets modified) and error state (if the value fails the verify functions).
        - It requires default value during initilization for self default setup.
    """

    value_type: Type[T] = type(None)  # For type querying
    # Data
    name: str = None
    value: T = None  # Value staying' None' means this Property is not initialized
    default_value: T = None
    # States
    is_dirty: bool = False  # If this property is marked dirty
    is_error: bool = False  # If this property value is an error
    # Configurations
    is_required: bool = True
    verify_funcs: list = field(default_factory=lambda: [])  # func(name, value) -> bool

    def __post_init__(self):
        # When type needs default_factory during setup
        if self.value is None:
            if self.value_type == list:
                self.value = []
            elif self.value_type == dict:
                self.value = {}
        if self.default_value is None:
            if self.value_type == list:
                self.default_value = []
            elif self.value_type == dict:
                self.default_value = {}

    def get_value_type(self):
        return self.value_type

    def setup_by_yaml(self, yaml_data: dict):
        if self.name in yaml_data:
            self.set_value(yaml_data[self.name], set_dirty=False)

    def setup_by_default(self):
        self.set_value(self.default_value)

    def set_value(self, new_val: T, set_dirty=True, set_error=True):
        """
        Set value to the property.
        Update dirty and error states accordingly.
        Raise type error if needed.
        """
        if new_val is None:
            self.value = None
            return
        if not isinstance(new_val, self.value_type):
            raise TypeError(
                f"""Input value '{type(new_val)}' does not match with desired type '{self.value_type}'
                for property '{self.name}'.
                Setting property value fails."""
            )
        if self.value == new_val:
            return
        self.value = new_val
        # Update dirty state
        if set_dirty:
            self.is_dirty = True
        # Vefify error
        if set_error:
            self.is_error = False
            for func in self.verify_funcs:
                self.is_error |= not func(self.name, self.value)
        # Notify update
        self.notify_update(self)

    def get_value(self):
        return self.value

    def to_yaml_data(self) -> dict:
        """
        Get the YAML representation for this property.
        Overwrite this method to translate custom classes into YAML.
        """
        return {self.name: self.value}

    def get_resolved_value(self):
        """
        Resolved value is used for value verification, calculations or other operations.
        Overwrite this method to apply resolving rules.
        """
        return self.value

    def is_setup(self):
        if self.value_type in [list, dict]:
            return len(self.value) >= 0
        else:
            return self.value is not None

    def is_value_dirty(self):
        return self.is_dirty

    def is_value_error(self):
        return self.is_error

    def reset_dirty(self):
        self.is_dirty = False


@dataclass
class RelativePathProperty(Property):
    """
    Property class to implement relative path logic.
        - It takes root path as an additional init argument.
        - To obtain full path, get its resolved value.
    """

    value_type: Type[T] = str
    value: str = None
    relative_to_path: str = None

    def set_value(self, new_val: str, set_dirty=True, set_error=True):
        super().set_value(new_val, set_dirty=set_dirty, set_error=set_error)
        # Additional value verification
        self.is_error = False
        self.is_error |= not self.verify_relative_path_exist(self.name, self.value)

    def get_resolved_value(self):
        return FileUtil.get_absolute_path(self.relative_to_path, self.value)

    def verify_relative_path_exist(self, name, value):
        try:
            if PropertyVerifyUtil.verify_path_exist(name, value, log_error=False):
                return True

            full_path = self.get_resolved_value()
            if PropertyVerifyUtil.verify_path_exist(name, full_path, log_error=False):
                return True
        except:
            carb.log_error(f"'{self.get_value()}' is not a existing file path.")
            return False
        carb.log_error(f"'{self.get_value()}' is not a existing file path.")
        return False


@dataclass
class AutoDictProperty(Property):
    """
    Property class to ensure its dict value follows the default_value structure.
        - Missing items with be auto filled up with default_value.
        - Items outside default_value will be removed.
    """

    value_type: Type[T] = dict
    value: dict = field(default_factory=lambda: {})
    default_value: dict = field(default_factory=lambda: {})

    def setup_by_yaml(self, yaml_data: dict):
        if self.name in yaml_data:
            self._set_dict_to_value(yaml_data[self.name])
            # Dirty state can be trigged due to forced structure
            if self.get_value() != yaml_data[self.name]:
                self.is_dirty = True

    def set_value(self, new_val: dict, set_dirty=True, set_error=True):
        if self.default_value is None:
            self.default_value = {}
        if new_val is None:
            new_val = self.default_value.copy()
        if self.value == new_val:
            return
        # Set value
        self._set_dict_to_value(new_val)
        # Update dirty state
        if set_dirty:
            self.is_dirty = True
        # Update error state
        if set_error:
            self.is_error = False
            for func in self.verify_funcs:
                self.is_error |= not func(self.name, self.value)
        # Notify update
        self.notify_update(self)

    def _set_dict_to_value(self, data: dict):
        """
        Set a dict input to value and ensure it follows default_value structure.
        """
        if not self.default_value:
            self.value = data
            return
        if not data:
            self.value = self.default_value.copy()
            return
        self.value = self.default_value.copy()
        for key, value in data.items():
            if key in self.value and value is not None:
                self.value[key] = data[key]


@dataclass
class PropertyGroup(UpdateNotifier):
    """
    Base class to manage relationship among a group of Properties.
    It stores all possible default Property values to perform group logic.
    """

    # Configurations
    name: str = None
    is_required: bool = True
    default_values: dict = field(default_factory=lambda: {})

    def get_default_values(self) -> dict:
        return self.default_values

    @abstractmethod
    def is_setup(self) -> bool:
        return False

    @abstractmethod
    def setup_by_default(self):
        return

    @abstractmethod
    def setup_by_yaml(self, yaml_data: dict):
        """
        Set up properties by input yaml.
        """
        return

    @abstractmethod
    def is_dirty(self) -> bool:
        return False

    @abstractmethod
    def reset_dirty(self):
        pass

    @abstractmethod
    def to_yaml_data(self) -> dict:
        return


@dataclass
class OrPropertyGroup(PropertyGroup):
    """
    Class to achieve 'or' logic between two groups of Properties.
        - Only 1 group of Properties can be accessed at a time.
        - default_values defines as each property name to its default value.
    """

    # Data
    group_a: List[Property] = None
    group_b: List[Property] = None
    # States
    mode: int = -1  # -1 means not setup; 0 means A; 1 means B;
    is_mode_dirty: bool = False

    def __post_init__(self):
        # Monitor all its Properties updates
        props = self.group_a + self.group_b
        for prop in props:
            prop.register_update_func(self.notify_update)

    def setup_by_default(self):
        # group_a is the default group
        self.set_mode(0)
        # Auto setup all properties
        props = self.get_all_present_properties()
        for prop in props:
            prop.set_value(self.default_values[prop.name])

    def is_setup(self) -> bool:
        return self.get_mode() in [0, 1]

    def setup_by_yaml(self, yaml_data: dict):
        names_a = [p.name for p in self.group_a]
        names_b = [p.name for p in self.group_b]
        for key, value in yaml_data.items():
            if key in names_a:
                if self.get_mode() == 1:
                    raise ConfigFileError("Input yaml has conflicting keyword.")
                self.set_mode(0, set_dirty=False, notify_update=False)
                self.get_property(key).set_value(value, set_dirty=False)
            if key in names_b:
                if self.get_mode() == 0:
                    raise ConfigFileError("Input yaml has conflicting keyword.")
                self.set_mode(1, set_dirty=False, notify_update=False)
                self.get_property(key).set_value(value, set_dirty=False)
        if not self.is_setup():
            return
        # Set up missing properties
        props = self.get_all_present_properties()
        for prop in props:
            if not prop.is_setup():
                prop.set_value(self.default_values[prop.name])

    def get_property(self, name: str) -> Property:
        if self.get_mode() == -1:
            return None
        props = self.get_all_present_properties()
        for prop in props:
            if prop.name == name:
                return prop
        return None

    def get_all_present_properties(self) -> List[Property]:
        if self.get_mode() not in [0, 1]:
            return None
        return self.group_a if self.get_mode() == 0 else self.group_b

    def is_dirty(self) -> bool:
        prop_dirty: bool = False
        for prop in self.get_all_present_properties():
            if prop.is_value_dirty():
                prop_dirty = True
                break
        return prop_dirty or self.is_mode_dirty

    def reset_dirty(self):
        self.is_mode_dirty = False
        props = self.group_a + self.group_b
        for prop in props:
            prop.reset_dirty()

    def to_yaml_data(self) -> dict:
        data = {}
        props = self.get_all_present_properties()
        for prop in props:
            data.update(prop.to_yaml_data())
        return data

    def get_mode(self):
        return self.mode

    def set_mode(self, new_mode, set_dirty=True, notify_update=True):
        # Update mode
        if new_mode not in [0, 1]:
            carb.log_error(f"Unable to set mode for PropertyGroup {self.name} due to invalid input: {new_mode}.")
            self.mode = -1
            return
        if new_mode == self.mode:
            return
        self.mode = new_mode
        # Mark dirty
        if set_dirty:
            self.is_mode_dirty = True
        # Notify update
        if notify_update:
            self.notify_update(self)


@dataclass
class SelectionPropertyGroup(PropertyGroup):
    """
    Class to achieve content selection logic (like combo box).
        - content_prop changes value by selection_prop.
        - default_values defines as each selection value to its content value.
        - selection_prop and content_prop default values are changed by selection.
        - custom selection: index is set to len(default_values) when selection_prop falls outside the default values.
    """

    # Data
    selection_prop: Property = None
    content_prop: Property = None
    # States
    index: int = -1

    def __post_init__(self):
        # Monitor both selection and content updates
        self.selection_prop.register_update_func(self.notify_update)
        self.content_prop.register_update_func(self.notify_update)

    def is_setup(self) -> bool:
        return self.index >= 0

    def setup_by_default(self):
        self.set_selection(0)

    def setup_by_yaml(self, yaml_data: dict):
        selection = None
        if self.selection_prop.name in yaml_data:
            selection = yaml_data.get(self.selection_prop.name)
        # Update index
        if selection in self.default_values:
            self._set_index(list(self.default_values.keys()).index(selection))
        else:
            self._set_index(len(self.default_values))  # Mark it as custom selection
        # Update selection
        if yaml_data:
            self.selection_prop.setup_by_yaml(yaml_data)
        if not self.selection_prop.is_setup():
            self.selection_prop.setup_by_default()
        # Update content
        if yaml_data:
            self.content_prop.setup_by_yaml(yaml_data)
        if not self.content_prop.is_setup():
            self.content_prop.setup_by_default()

    def is_dirty(self) -> bool:
        return self.selection_prop.is_value_dirty() or self.content_prop.is_value_dirty()

    def reset_dirty(self) -> bool:
        self.selection_prop.reset_dirty()
        self.content_prop.reset_dirty()

    def to_yaml_data(self) -> dict:
        data = {}
        data.update(self.selection_prop.to_yaml_data())
        data.update(self.content_prop.to_yaml_data())
        return data

    def _set_index(self, index):
        if index == self.index:
            return
        self.index = index
        # Update default values by selection
        if self.index < 0 or self.index >= len(self.default_values):
            self.selection_prop.default_value = None
            self.content_prop.default_value = None
        else:
            key, value = list(self.default_values.items())[self.index]
            self.selection_prop.default_value = key
            self.content_prop.default_value = value

    def set_selection(self, index):
        if index < 0 or index > len(self.default_values):
            raise ConfigFileError(
                f"""Index ({index}) falls out of range for ProeprtyGroup {self.name}.
                                  Set selection fails."""
            )
        # Update index
        self._set_index(index)
        # Update property values
        if self.index < len(self.default_values):
            selection_value, content_value = list(self.default_values.items())[index]
            self.selection_prop.set_value(selection_value)
            self.content_prop.set_value(content_value)

    def is_custom_selection(self):
        return self.index == len(self.default_values)

    def get_current_index(self):
        return self.index

    def get_all_selection_values(self) -> list:
        return list(self.default_values.keys())

    def setup_by_custom_value(self, selection_value, content_value):
        self._set_index(len(self.default_values))  # Mark it as custom selection
        self.selection_prop.set_value(selection_value)
        self.content_prop.set_value(content_value)


@dataclass
class ListPropertyGroup(PropertyGroup):
    """
    Base class to handle a list of Property.

    Example:
        my_list_property:
            - prop_01: value_01
            - prop_02: value_02
            ...
    """

    ref_group: List[Property] = field(default_factory=lambda: [])
    # Data
    data_group: List[Property] = field(default_factory=lambda: [])

    # Internal state
    is_list_dirty: bool = False

    def is_setup(self) -> bool:
        for prop in self.data_group:
            if not prop.is_setup():
                return False
        return True

    def setup_by_default(self):
        for prop in self.data_group:
            prop.setup_by_default()

    def setup_by_yaml(self, yaml_data: dict):
        if self.name not in yaml_data:
            return
        if not isinstance(yaml_data[self.name], list):
            carb.log_warn(f"'{self.name}' data in input yaml is not a list.")
            return
        # Clear last load
        self.clear_list()
        list_data = list(yaml_data[self.name])
        # Identify the reference property in the list
        for item in list_data:
            if not isinstance(item, dict):
                carb.log_warn(f"Unable to parse '{item}' into dict for '{self.name}''s input.")
                continue
            for ref_prop in self.ref_group:
                if ref_prop.name in item:
                    new_prop = replace(ref_prop)
                    new_prop.setup_by_yaml(item)
                    self.add_to_list(new_prop)

    def add_to_list(self, prop: Property):
        if prop in self.data_group:
            carb.log_warn(f"Property \'{prop.name}\' alreay exists in List \'{self.name}\'.")
            return
        self.data_group.append(prop)
        # Register listener
        prop.register_update_func(self.notify_update)
        # Mark dirty
        self.is_list_dirty = True
        # Notify update
        self.notify_update(self)

    def remove_from_list(self, prop: Property):
        if prop not in self.data_group:
            carb.log_warn(f"Property \'{prop.name}\' does not exist in List \'{self.name}\'.")
            return
        self.data_group.remove(prop)
        # Deregister listener
        prop.deregister_update_func(self.notify_update)
        # Mark dirty
        self.is_list_dirty = True
        # Notify update
        self.notify_update(self)

    def replace_from_list(self, idx: int, prop: Property):
        if idx < 0 or idx >= len(self.data_group):
            return
        # Deregister old property
        old_prop = self.data_group[idx]
        old_prop.deregister_update_func(self.notify_update)
        # Replace with the new one
        self.data_group[idx] = prop
        prop.register_update_func(self.notify_update)
        # Mark dirty
        self.is_list_dirty = True
        # Notify update
        self.notify_update(self)

    def clear_list(self):
        # Deregister listener
        for prop in self.data_group:
            prop.deregister_update_func(self.notify_update)
        # Clear list
        self.data_group.clear()
        # Mark dirty
        self.is_list_dirty = True
        # Notify update
        self.notify_update(self)

    def is_dirty(self) -> bool:
        if self.is_list_dirty:
            return True
        for prop in self.data_group:
            if prop.is_value_dirty():
                return True
        return False

    def reset_dirty(self):
        for prop in self.data_group:
            prop.reset_dirty()
        self.is_list_dirty = False

    def to_yaml_data(self) -> dict:
        list_data = []
        for prop in self.data_group:
            list_data.append(prop.to_yaml_data())
        return {self.name: list_data}
