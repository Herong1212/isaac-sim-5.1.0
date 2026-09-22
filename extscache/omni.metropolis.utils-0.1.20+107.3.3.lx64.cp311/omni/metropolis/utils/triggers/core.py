from __future__ import annotations
from dataclasses import dataclass, field, fields, _MISSING_TYPE
from abc import ABC
from typing import Callable, Type, List, ClassVar

import carb

@dataclass
class TriggerBase(ABC):
    # Trigger type name
    type_name: ClassVar[str] = ""
    # Callbacks to be triggered.
    # (Not required during init nor included in the dict representation)
    callbacks: List[Callable[[TriggerBase]]] = field(default_factory=lambda: [], init=False)

    @classmethod
    def from_dict(cls, data_dict: dict) -> TriggerBase:
        """
        Create a Trigger instance from dict. Use its default value for missing fields.
        """
        if "trigger" not in data_dict:
            return None
        if "type" not in data_dict["trigger"]:
            return None
        if data_dict["trigger"]["type"] != cls.type_name:
            return None
        trigger_data_dict = data_dict["trigger"]
        default_dict = cls.default_dict()
        field_names = list(default_dict.keys())
        d = {k: v for k, v in trigger_data_dict.items() if k in field_names}
        d.update({k: v for k, v in default_dict.items() if k not in d})
        del d["type"]  # Do not input type since it is fixed for each class
        return cls(**d)

    @classmethod
    def default_dict(cls) -> dict:
        """
        Return the trigger's default dict representation.
        Each item is the field(init=True) and its default value.
        """
        default_dict = {"type": cls.type_name}
        # Gather all default values
        for field in fields(cls):
            if not field.init:
                continue
            if isinstance(field.default, _MISSING_TYPE):
                default_dict[field.name] = field.default_factory()
            else:
                default_dict[field.name] = field.default
        return default_dict

    def to_dict(self) -> dict:
        data_dict = {"type": self.type_name}
        # Gather fields from children
        for field in fields(self):
            if field.name == "type_name":
                continue
            if not field.init:
                continue
            data_dict[field.name] = getattr(self, field.name)
        return {"trigger": data_dict}

    def add_callback(self, callback_fn: Callable[[TriggerBase]]):
        self.callbacks.append(callback_fn)

    def trigger(self):
        for callback in self.callbacks:
            if callback:
                callback(self)

    def destroy(self):
        self.callbacks = []


class TriggersManager:

    __instance: TriggersManager = None

    @classmethod
    def get_instance(cls) -> TriggersManager:
        if cls.__instance is None:
            TriggersManager()
        return cls.__instance

    def __init__(self):
        if TriggersManager.__instance is not None:
            raise RuntimeError("TriggersManager cannot have more than 1 instance.")
        TriggersManager.__instance = self
        self.registered_trigger_types: List[Type[TriggerBase]] = []

    def register_trigger_type(self, trigger_type_list: List[Type[TriggerBase]]) -> bool:
        for trigger_type in trigger_type_list:
            if trigger_type in self.registered_trigger_types:
                carb.log_warn(f"Trigger type '{trigger_type.type_name}' was registered already. Skip Registering.")
                continue
            self.registered_trigger_types.append(trigger_type)
            carb.log_info(f"Register trigger type ''{trigger_type.type_name}'.")
        return True

    def deregister_trigger_type(self, trigger_type_list: List[Type[TriggerBase]]) -> bool:
        to_remove = []
        for trigger_type in trigger_type_list:
            if trigger_type not in self.registered_trigger_types:
                carb.log_warn(f"Trigger type '{trigger_type}' is not registered. Deregister fails.")
                continue
            to_remove.append(trigger_type)
        for t in to_remove:
            self.registered_trigger_types.remove(t)
            carb.log_info(f"Deregister trigger type ''{trigger_type.type_name}'.")
        return True

    def get_registered_trigger_type(self, name: str) -> TriggerBase:
        for trigger_type in self.registered_trigger_types:
            if trigger_type.type_name == name:
                return trigger_type
        return None

    def get_default_trigger_type(self) -> TriggerBase:
        if not self.registered_trigger_types:
            return None
        return self.registered_trigger_types[0]

    def create_trigger_by_dict(self, dict_data: dict) -> TriggerBase:
        for trigger_type in self.registered_trigger_types:
            instance = trigger_type.from_dict(dict_data)
            if instance:
                return instance
        return None

    def get_all_registered_triggers(self) -> List[Type[TriggerBase]]:
        return self.registered_trigger_types
