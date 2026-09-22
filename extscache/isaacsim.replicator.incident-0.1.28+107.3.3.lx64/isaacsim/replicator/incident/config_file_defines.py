from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass, field, fields
from typing import ClassVar
from omni.metropolis.utils.config_file.property import Property, ListPropertyGroup, RelativePathProperty
from omni.metropolis.utils.config_file.section import Section
from omni.metropolis.utils.triggers.core import TriggersManager
from omni.metropolis.utils.triggers.config_file_defines import property_with_trigger
from omni.metropolis.utils.config_file.util import PropertyVerifyUtil

from .settings import IncidentSettings


# TODO:: To have each incident proeprty defined from each event manager implementation


@property_with_trigger
@dataclass
class EventPropertyBase(Property):
    """
    Provide unified property handling for each incident event.
    Every incident event follows this structure:
        event_type_name(self.property_name):
            name: "default event name"
            item (self.default_items):
                item_value_dict
            trigger:
                trigger_value_dict
    """
    all_sub_event_cls: ClassVar[list] = []

    value_type = dict
    is_required: bool = False
    # Additional params, to be set in children classes
    default_event_name: str = "default event"
    default_items: dict = field(default_factory=lambda: {})


    @classmethod
    def __init_subclass__(cls, **kwargs):
        # Base class keep tracks of implemented event names
        if cls != EventPropertyBase and cls not in EventPropertyBase.all_sub_event_cls:
            EventPropertyBase.all_sub_event_cls.append(cls)

    @classmethod
    def get_all_implemented_event_cls(cls):
        return EventPropertyBase.all_sub_event_cls

    @classmethod
    def get_implemented_event_cls_by_name(cls, name):
        for event_cls in EventPropertyBase.all_sub_event_cls:
            for f in fields(event_cls):
                # Event type name is saved in the property default value for sub classes
                if f.name == "name" and f.default == name:
                    return event_cls
        return None


    @classmethod
    def get_all_implemented_event_type_names(cls):
        names = []
        for event_cls in EventPropertyBase.all_sub_event_cls:
            for f in fields(event_cls):
                # Event type name is saved in the property default value for sub classes
                if f.name == "name":
                    names.append(f.default)
        return names

    def __post_init__(self):
        # Set up default values using addtional params
        self.default_value = {}
        self.default_value["name"] = self.default_event_name
        self.default_value.update(self.default_items)
        self.default_value["trigger"] = TriggersManager.get_instance().get_default_trigger_type().default_dict()

    def set_value(self, new_val: dict, set_dirty=True, set_error=True):
        if new_val is None:
            self.value = None
            return
        if not isinstance(new_val, dict):
            raise TypeError(
                f"Input value '{type(new_val)}' is not a dict in property '{self.name}'. Setting property value fails."
            )
        if self.value == new_val:
            return
        if set_dirty:
            self.is_dirty = True
        # Custom rules for dict value
        self.value = self.default_value.copy()
        if "name" in new_val:
            self.value["name"] = new_val["name"]
        for default_item_name, default_item_value in self.default_items.items():
            if default_item_name in new_val:
                item = new_val[default_item_name]
                item_keys = list(item.keys())
                default_keys = list(default_item_value.keys())
                for key in item_keys:
                    if key in default_keys:
                        self.value[default_item_name][key] = item[key]
        # Pass value to trigger handling
        self.handle_trigger_from_dict(new_val, set_error)
        # Update error state
        if set_error:
            self.is_error = False
            for func in self.verify_funcs:
                self.is_error |= not func(self.name, self.value)
        # Notify update
        self.notify_update(self)


@dataclass
class ToppleEventProperty(EventPropertyBase):
    name: str = "ToppleEvent"
    default_event_name: str = "default topple event"
    default_items: dict = field(
        default_factory=lambda: {
            "topple_item": {"item": IncidentSettings.RANDOM_LOOSE_ITEM, "topple_nearby_radius": 1.5}
        }
    )


@dataclass
class PyroEventProperty(EventPropertyBase):
    name: str = "FireEvent"
    default_event_name: str = "default fire event"
    default_items: dict = field(
        default_factory=lambda: {
            "flammable_item": {"item": IncidentSettings.RANDOM_FLAMMABLE_ITEM}
        }
    )


@dataclass
class SpillEventProperty(EventPropertyBase):
    name: str = "SpillEvent"
    default_event_name: str = "default spill event"
    default_items: dict = field(
        default_factory=lambda: {
            "leakable_item": {
                "item": IncidentSettings.RANDOM_LEAKABLE_ITEM,
                "target_size": 1.0,
                "leak_duration": 5.0,
            }
        }
    )


@dataclass
class IncidentGlobalSection(Section):
    name: ClassVar[str] = "global"
    is_required: ClassVar[str] = True
    # Data
    seed: Property[int] = None
    report_dir: Property[str] = None

    def __post_init__(self):
        self.seed = Property(
            value_type=int,
            name="seed",
            default_value=123456,
            verify_funcs=[PropertyVerifyUtil.verify_int_non_negative]
        )
        self.report_dir = Property(
            value_type=str,
            name="report_dir",
            default_value=str(Path.home().joinpath("EventsResult")),
            verify_funcs=[],
        )


@dataclass
class IncidentEventSection(Section):
    name: ClassVar[str] = "event"
    is_required: ClassVar[bool] = True
    # Data
    incident_list: ListPropertyGroup = None

    def __post_init__(self):
        self.incident_list = ListPropertyGroup(
            name="event_list", ref_group=[ToppleEventProperty(), PyroEventProperty(), SpillEventProperty()]
        )
