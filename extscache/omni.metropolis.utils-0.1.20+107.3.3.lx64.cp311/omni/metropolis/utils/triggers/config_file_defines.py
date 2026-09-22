from typing import Type

import carb

from ..config_file.property import Property
from .core import TriggersManager


def property_with_trigger(prop_cls: Type[Property]):
    """
    Add trigger dict handling functionality for Property.
    It will handle the trigger part in dict.
    Example usage:
        prop.handle_trigger_from_dict(self, new_val["trigger"], set_error)
    """

    def handle_trigger_from_dict(self, data_dict, set_error):
        if "trigger" not in data_dict:
            return
        trigger_dict = data_dict["trigger"]
        if "type" not in trigger_dict:
            carb.log_error(f"Cannot find trigger type for proprety {self.name}.")
            if set_error:
                self.is_error = True
        else:
            trigger_type = trigger_dict["type"]
            trigger_cls = TriggersManager.get_instance().get_registered_trigger_type(trigger_type)
            if not trigger_cls:
                carb.log_error(f"Invalid trigger type '{trigger_type}' for property {self.name}.")
                if set_error:
                    self.is_error = True
            else:
                default_dict = trigger_cls.default_dict().copy()
                for k, v in default_dict.items():
                    if k in trigger_dict:
                        default_dict[k] = trigger_dict[k]
                self.value["trigger"] = default_dict

    setattr(prop_cls, "handle_trigger_from_dict", handle_trigger_from_dict)
    return prop_cls
