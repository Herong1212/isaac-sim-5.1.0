import math

import carb
from pxr import Gf
from typing import Optional, Any, Union, List
import re


class CarbUtil:
    IDENTITY_ROT = carb.Float4(0, 0, 0, 1)

    """
    ------------------------Carb vector utility functions ------------------------
    """

    @staticmethod
    def clamp(f, lower, upper):
        return min(max(lower, f), upper)

    @staticmethod
    def equal3(a, b):
        return a.x == b.x and a.y == b.y and a.z == a.z

    @staticmethod
    def add3(a, b):
        return carb.Float3(a[0] + b[0], a[1] + b[1], a[2] + b[2])

    @staticmethod
    def add4(a, b):
        return carb.Float4(a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3])

    @staticmethod
    def sub3(a, b):
        return carb.Float3(a[0] - b[0], a[1] - b[1], a[2] - b[2])

    @staticmethod
    def sub4(a, b):
        return carb.Float4(a[0] - b[0], a[1] - b[1], a[2] - b[2], a[3] - b[3])

    @staticmethod
    def length3(v):
        return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

    @staticmethod
    def length4(v):
        return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2] + v[3] * v[3])

    @staticmethod
    def scale3(v, f):
        return carb.Float3(v[0] * f, v[1] * f, v[2] * f)

    @staticmethod
    def scale4(v, f):
        return carb.Float4(v[0] * f, v[1] * f, v[2] * f, v[3] * f)

    @staticmethod
    def dot3(a, b):
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

    @staticmethod
    def dot4(a, b):
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3]

    @staticmethod
    def cross3(a, b):
        return carb.Float3(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x)

    @staticmethod
    def dist3(a, b):
        return CarbUtil.length3(CarbUtil.sub3(b, a))

    @staticmethod
    def lerp3(a, b, t):
        return CarbUtil.add3(a, CarbUtil.scale3(CarbUtil.sub3(b, a), t))

    @staticmethod
    def lerp4(a, b, t):
        return CarbUtil.add4(a, CarbUtil.scale4(CarbUtil.sub4(b, a), t))

    @staticmethod
    def nlerp4(a, b, t):
        return CarbUtil.normalize4(CarbUtil.lerp4(a, b, t))

    @staticmethod
    def normalize3(v):
        gf_v = Gf.Vec3d(v.x, v.y, v.z)
        gf_v_normalized = gf_v.GetNormalized()
        return carb.Float3(gf_v_normalized[0], gf_v_normalized[1], gf_v_normalized[2])

    @staticmethod
    def normalize4(v):
        length = CarbUtil.length4(v)
        if length > 0.001:
            return CarbUtil.scale4(v, 1 / length)
        else:
            return CarbUtil.IDENTITY_ROT


class CarbSettingUtil:
    @staticmethod
    def get_value_by_key(key: str, fallback_value: Any = None, override_setting: bool = False) -> Any:
        """Get a value from carb settings, falling back to a default if not found.

        Args:
            key: The settings key to look up
            fallback_value: The default value to use and store if key not found
            override_setting: Whether to override the existing value
        """
        settings = carb.settings.get_settings()

        # Try to get existing value
        if (value := settings.get(key)) is not None and value != "":
            return value

        # Store and return fallback value
        if override_setting:
            settings.set(key, fallback_value)
        return fallback_value

    @staticmethod
    def set_value_by_key(key: str, new_value: Any) -> None:
        """Set a value in carb settings.

        Args:
            key: The settings key to set
            new_value: The value to store. Can be any type supported by carb settings
                (bool, int, float, str, list, dict)

        Note:
            If the key already exists, its value will be overwritten
            If the key doesn't exist, it will be created with the new value
        """
        carb.settings.get_settings().set(key, new_value)

    @staticmethod
    def has_key(key: str) -> bool:
        """Check if a key exists in carb settings.

        Args:
            key: The settings key to check

        Returns:
            bool: True if the key exists and has a non-None value
        """
        return (value := carb.settings.get_settings().get(key)) is not None

    @staticmethod
    def remove_key(key: str) -> None:
        """Remove a setting value from carb settings.

        Args:
            key: The settings key to remove

        Note:
            If the key doesn't exist, this operation will silently succeed
        """
        carb.settings.get_settings().destroy_item(key)


class CarbSettingMeta(type):
    """Metaclass to manage Carb setting properties."""

    def __new__(cls, name, bases, class_dict):
        # Create the new class
        new_class = super().__new__(cls, name, bases, class_dict)

        # Ensure _carb_setting_paths is initialized before descriptors are processed
        if not hasattr(new_class, "_carb_setting_paths"):
            new_class._carb_setting_paths = {}  # Initialize it properly

        # Inject helper methods
        def get_setting_path(cls, property_name: str):
            """Fetch the setting path for a given property name."""
            return cls._carb_setting_paths.get(property_name, None)

        def get_all_setting_paths(cls):
            """Fetch all registered setting paths."""
            return cls._carb_setting_paths

        def remove_setting_property(cls, property_name: str):
            """Remove the setting property from Carb settings and class variables."""

            if not property_name in cls.__dict__:
                return
            descriptor = cls.__dict__[property_name]
            # if target property is not an CarbSettingProperty instance
            if not isinstance(descriptor, CarbSettingProperty):
                return

            setting_path = cls._carb_setting_paths.pop(property_name, None)
            if not setting_path:
                return
            # double check whether the carb setting exist
            if hasattr(cls, property_name):
                # remove the target descriptor within the class
                delattr(cls, property_name)
                # call the api to remove the carb setting binded with the property
                CarbSettingUtil.remove_key(key=setting_path)
                carb.log_verbose(
                    f"Successfully removed setting property '{property_name}' "
                    f"and its Carb settings key '{setting_path}'."
                )

        # Attach methods to the class
        new_class.get_setting_path = classmethod(get_setting_path)
        new_class.get_all_setting_paths = classmethod(get_all_setting_paths)
        new_class.remove_setting_property = classmethod(remove_setting_property)

        return new_class

    def __setattr__(cls, name, value):
        """Intercept `=` at the class level and redirect it to the descriptor's `__set__` method."""
        if name in cls.__dict__:
            descriptor = cls.__dict__[name]
            if isinstance(descriptor, CarbSettingProperty):
                descriptor.__set__(None, value)  # Use descriptor __set__
                return
        super().__setattr__(name, value)


class CarbSettingProperty:
    """
    Descriptor that automatically generates a Carb settings key based on:
    - Extension name (via fetch_extension_name())
    - The class it belongs to
    - The variable name
    - Ensures persistent values are only initialized once
    """

    PERSISTENT_SETTINGS_PREFIX = "/persistent"

    @staticmethod
    def to_snake_case(text: str) -> str:
        """
        Converts a given string into snake_case.

        Parameters:
        - text (str): The input string to convert.

        Returns:
        - str: The converted snake_case string.
        """
        # Replace spaces, hyphens, and underscores with a single space
        text = re.sub(r"[\s\-_]+", " ", text)
        # Convert camelCase and PascalCase to snake_case
        text = re.sub(r"([a-z])([A-Z])", r"\1_\2", text)
        # Convert all characters to lowercase and replace spaces with underscores
        return text.lower().replace(" ", "_")

    @staticmethod
    def fetch_class_module_name(setting_class: Any) -> str:
        """Fetch the class's parent module name, usually matching the extension name."""
        file_module_name = setting_class.__module__
        return file_module_name.rsplit(".", 1)[0] if "." in file_module_name else file_module_name

    def __init__(self, default_value: Any, is_persistent: bool = False):
        self.default_value = default_value
        self.is_persistent = is_persistent
        self.setting_key = None  # Set later in __set_name__

    @staticmethod
    def is_valid_owner(owner: type):
        valid_parent = isinstance(owner, CarbSettingMeta)
        return valid_parent

    def __set_name__(self, owner: type, variable_name: str):
        """Generate the settings key when assigned in a class."""
        extension_name = self.fetch_class_module_name(owner)
        class_name = owner.__name__
        self.setting_key = (
            f"/exts/{extension_name}/{self.to_snake_case(class_name)}/{self.to_snake_case(variable_name)}"
        )
        if self.is_persistent:
            self.setting_key = f"{self.PERSISTENT_SETTINGS_PREFIX}{self.setting_key}"

        # registry current carb setting metadata, match with current property
        valid_owner = self.is_valid_owner(owner=owner)
        if valid_owner:
            if not hasattr(owner, "_carb_setting_paths"):
                owner._carb_setting_paths = {}  # Ensures it's set for every subclass
            owner._carb_setting_paths[variable_name] = self.setting_key
            # since we are using the snake case converter to reformat the path, let user know their converted carb path
            carb.log_verbose(f"Registry the setting path pair in {str(owner)} {variable_name} : {self.setting_key}")
        value_exist = CarbSettingUtil.has_key(self.setting_key)
        carb.log_verbose(f"Is {self.setting_key} exist ? : {value_exist}")

        if value_exist:
            pre_exist_value = carb.settings.get_settings().get(self.setting_key)
            carb.log_verbose(f"Value already exist  in path {self.setting_key} : value  is {pre_exist_value}")

        # Ensure persistent values are initialized only once
        if (not self.is_persistent) or (not value_exist):
            carb.log_verbose(f"Set the default value of path {self.setting_key} to {self.default_value}")
            CarbSettingUtil.set_value_by_key(self.setting_key, self.default_value)

    def __get__(self, instance: Any, owner: type):
        """Fetch the value from Carb settings, returning the default if not found."""
        carb.log_verbose(f"Get value at path {self.setting_key} value: {self.default_value}")
        return CarbSettingUtil.get_value_by_key(self.setting_key, self.default_value)

    def __set__(self, instance: Any, value: Optional[Any] = None):
        """Set the value in Carb settings."""
        if value is None:
            # # If persistent, do not overwrite an existing value
            # if self.is_persistent and CarbSettingUtil.has_key(self.setting_key):
            #     return
            value = self.default_value

        CarbSettingUtil.set_value_by_key(self.setting_key, value)
        carb.log_verbose(f"Set value at path {self.setting_key} value: {value}")
