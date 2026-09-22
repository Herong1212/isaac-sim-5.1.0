from __future__ import annotations
import carb
from dataclasses import dataclass
from typing import ClassVar
from omni.metropolis.utils.config_file.property import Property, RelativePathProperty, AutoDictProperty, OrPropertyGroup, SelectionPropertyGroup, ListPropertyGroup
from omni.metropolis.utils.config_file.section import Section
from omni.metropolis.utils.config_file.util import PropertyVerifyUtil, ConfigFileError
from omni.metropolis.utils.type_util import TypeUtil
from omni.metropolis.utils.triggers.config_file_defines import TriggersManager, property_with_trigger
from ..data_generation.writers import get_writers_params_values
from .default import ConfigFileDefault


@dataclass
class GlobalSection(Section):
    # Class description
    name: ClassVar[str] = "global"
    is_required: ClassVar[bool] = True
    # Data
    seed: Property[int] = None
    simulation_length: Property[int] = None

    def __post_init__(self):
        self.seed = Property(
            value_type=int,
            name="seed",
            default_value=ConfigFileDefault.get_default_value_by_name(self.name, "seed"),
            verify_funcs=[PropertyVerifyUtil.verify_int_non_negative],
        )
        self.simulation_length = Property(
            value_type=int,
            name="simulation_length",
            default_value=ConfigFileDefault.get_default_value_by_name(self.name, "simulation_length"),
            verify_funcs=[PropertyVerifyUtil.verify_int_non_negative],
        )


@dataclass
class SceneSection(Section):
    # Class description
    name: ClassVar[str] = "scene"
    is_required: ClassVar[bool] = True
    # Data
    asset_path: Property[str] = None

    def __post_init__(self):
        self.asset_path = Property(
            value_type=str,
            name="asset_path",
            default_value=ConfigFileDefault.get_default_value_by_name(self.name, "asset_path"),
            verify_funcs=[PropertyVerifyUtil.verify_usd_path, PropertyVerifyUtil.verify_path_exist],
        )


@dataclass
class SensorSection(Section):
    # Class description
    name: ClassVar[str] = "sensor"
    is_required: ClassVar[bool] = True
    # Data
    camera_lidar_group: OrPropertyGroup = None

    def __post_init__(self):
        self.camera_lidar_group = OrPropertyGroup(
            name="camera_group",
            group_a=[
                Property(value_type=int, name="camera_num", verify_funcs=[PropertyVerifyUtil.verify_int_minus_one]),
                # Property(value_type=int, name="lidar_num", verify_funcs=[PropertyVerifyUtil.verify_int_minus_one]),
            ],
            group_b=[Property(value_type=list, name="camera_list")],  # Property(value_type=list, name="lidar_list")],
            default_values={
                "camera_num": ConfigFileDefault.get_default_value_by_name(self.name, "camera_num"),
                # "lidar_num": ConfigFileDefault.get_default_value_by_name(self.name, "lidar_num"),
                "camera_list": [],
                # "lidar_list": [],
            },
        )


@dataclass
class CharacterSection(Section):
    # Class description
    name: ClassVar[str] = "character"
    is_required: ClassVar[bool] = False  # Character section is optional
    # Data
    asset_path: Property[str] = None
    num: Property[int] = None
    filters: Property[list] = None
    command_file: RelativePathProperty = None
    spawn_area: Property[list] = None
    navigation_area: Property[list] = None

    def __post_init__(self):
        self.asset_path = Property(
            value_type=str,
            name="asset_path",
            default_value=ConfigFileDefault.get_default_value_by_name(self.name, "asset_path"),
            verify_funcs=[PropertyVerifyUtil.verfiy_folder_path_exist],
        )
        self.num = Property(
            value_type=int,
            name="num",
            default_value=ConfigFileDefault.get_default_value_by_name(self.name, "num"),
            verify_funcs=[PropertyVerifyUtil.verify_int_non_negative],
        )
        self.filters = Property(
            value_type=list,
            name="filters",
            default_value=[],
            verify_funcs=[PropertyVerifyUtil.verify_list],
        )
        self.command_file = RelativePathProperty(
            name="command_file",
            default_value=ConfigFileDefault.get_default_value_by_name(self.name, "command_file"),
            verify_funcs=[PropertyVerifyUtil.verify_text_path],
            relative_to_path=self._config_file_path,
        )
        self.spawn_area = Property(
            value_type=list,
            name="spawn_area",
            default_value=[],
            verify_funcs=[PropertyVerifyUtil.verify_list],
        )
        self.navigation_area = Property(
            value_type=list,
            name="navigation_area",
            default_value=[],
            verify_funcs=[PropertyVerifyUtil.verify_list],
        )


@dataclass
class RobotSection(Section):
    # Class description
    name: ClassVar[str] = "robot"
    is_required: ClassVar[bool] = False  # Robot section is optional
    # Data
    nova_carter_num: Property[int] = None
    iw_hub_num: Property[int] = None
    write_data: Property[bool] = None
    command_file: RelativePathProperty = None
    spawn_area: Property[list] = None
    navigation_area: Property[list] = None

    def __post_init__(self):
        self.nova_carter_num = Property(
            value_type=int,
            name="nova_carter_num",
            default_value=ConfigFileDefault.get_default_value_by_name(self.name, "nova_carter_num"),
            verify_funcs=[PropertyVerifyUtil.verify_int_non_negative],
        )
        self.iw_hub_num = Property(
            value_type=int,
            name="iw_hub_num",
            default_value=ConfigFileDefault.get_default_value_by_name(self.name, "iw_hub_num"),
            verify_funcs=[PropertyVerifyUtil.verify_int_non_negative],
        )
        self.write_data = Property(
            value_type=bool,
            name="write_data",
            default_value=ConfigFileDefault.get_default_value_by_name(self.name, "write_data"),
        )
        self.command_file = RelativePathProperty(
            name="command_file",
            default_value=ConfigFileDefault.get_default_value_by_name(self.name, "command_file"),
            verify_funcs=[PropertyVerifyUtil.verify_text_path],
            relative_to_path=self._config_file_path,
        )
        self.spawn_area = Property(
            value_type=list,
            name="spawn_area",
            default_value=[],
            verify_funcs=[PropertyVerifyUtil.verify_list],
        )
        self.navigation_area = Property(
            value_type=list,
            name="navigation_area",
            default_value=[],
            verify_funcs=[PropertyVerifyUtil.verify_list],
        )


@dataclass
class ReplicatorSection(Section):
    # Class description
    name: ClassVar[str] = "replicator"
    is_required: ClassVar[bool] = True
    # Data
    writer_selection: SelectionPropertyGroup = None

    def __post_init__(self):
        writers_params = get_writers_params_values().copy()
        self.writer_selection = SelectionPropertyGroup(
            name="writer_selection",
            selection_prop=Property(value_type=str, name="writer"),
            content_prop=AutoDictProperty(name="parameters"),
            default_values=writers_params,
        )

        default_writer = ConfigFileDefault.get_default_value_by_name(self.name, "writer")
        if default_writer not in writers_params:
            raise ConfigFileError("Default writer in default config file is not a built-in writer.")

        index = list(writers_params.keys()).index(default_writer)
        self.writer_selection.set_selection(index)


@property_with_trigger
@dataclass
class ResponseProperty(Property):
    value_type = dict
    is_required: bool = False

    def __post_init__(self):
        # Default value is from CommandBase definition
        self.name = "ResponseBase"
        self.default_value = {
            "name": "default response",
            "priority": 1,
            "pick_agent": "first_available",
            "resume": True,
            "position": carb.Float3(0, 0, 0),
            "trigger": TriggersManager.get_instance().get_default_trigger_type().default_dict(),
        }

    def set_value(self, new_val: dict, set_dirty=True, set_error=True):
        if new_val is None:
            new_val = self.default_value.copy()
        if self.value == new_val:
            return
        # Update dirty state
        if set_dirty:
            self.is_dirty = True
        self.value = self.default_value.copy()

        # Set ResponseBase field value
        for name, value in self.default_value.items():
            if name == "trigger":
                continue
            if name in new_val:
                self.value[name] = new_val[name]
                if name == "position": # Parse float3 from string
                    self.value[name] = TypeUtil.str_to_carb_float3(str(new_val[name]))
        # Pass value to trigger handling
        self.handle_trigger_from_dict(new_val, set_error)
        # Update error state
        if set_error:
            self.is_error = False
            for func in self.verify_funcs:
                self.is_error |= not func(self.name, self.value)
        # Notify update
        self.notify_update(self)

    def to_yaml_data(self):
        value_dict = self.value.copy()
        value_dict["position"] = str(value_dict["position"])
        return {self.name: value_dict}

@dataclass
class CommandResponseProperty(ResponseProperty):
    def __post_init__(self):
        super().__post_init__()
        # Default value is from CommandResponse definition
        self.name = "CommandResponse"
        self.default_value.update({"commands": []})


@dataclass
class ResponseSection(Section):
    # Class description
    name: ClassVar[str] = "response"
    is_required: ClassVar[bool] = True
    # Data
    response_list: ListPropertyGroup = None

    def __post_init__(self):
        self.response_list = ListPropertyGroup(
            name="response_list", ref_group=[CommandResponseProperty()], is_required=True
        )
