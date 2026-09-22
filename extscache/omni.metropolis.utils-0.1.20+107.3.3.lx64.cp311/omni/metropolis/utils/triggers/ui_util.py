import carb
import omni.ui as ui
from ..ui_util import UIUtil, MinimalStringListModel
from .core import TriggersManager

class UITriggerHelper:
    """Helper class to create UI and pass along update events for trigger values"""
    def __init__(self, trigger_value_dict):
        self.value_dict = trigger_value_dict
        self.model_dict = {}
        self.ui_dict = {}
        self.trigger_type_changed_fn_list= [] # f(new_trigger_value_dict)
        self.trigger_value_changed_fn_list = [] # f(new_trigger_value_dict)

    def create_ui_models(self):
        """Create a dict of UI Models from trigger value dict."""
        all_trigger_cls = TriggersManager.get_instance().get_all_registered_triggers()
        all_trigger_names = [c.type_name for c in all_trigger_cls]
        self.model_dict = {}
        self.model_dict["type"] = MinimalStringListModel(all_trigger_names, all_trigger_names.index(self.value_dict["type"]))
        self.model_dict["type"].add_item_changed_fn(lambda m, i : self._on_trigger_type_changed(m.get_selection()))
        for key, value in self.value_dict.items():
            if key == "type":
                continue
            self.model_dict[key] = UIUtil.create_model_for_value(value)
            self.model_dict[key].add_value_changed_fn(lambda m, k=key:
                                                      self._on_trigger_value_changed(k, UIUtil.get_value_from_model(m)))
        return self.model_dict

    def create_ui(self):
        """Create UI fields for trigger model dict."""
        if not self.model_dict:
            carb.log_warn("Please ensure UI models are craeted before creating UI.")
            return
        self.ui_dict = {}
        with ui.HStack(spacing=5):
            ui.Label("\tTrigger Type", width=120)
            self.ui_dict["type"] = ui.ComboBox(self.model_dict["type"], width=120)
        for key, model in self.model_dict.items():
            if key == "type":
                continue
            with ui.HStack(spacing=5):
                ui.Label(f"\t{key}", width=120)
                self.ui_dict[key] = UIUtil.create_field_for_model(model)
        return self.ui_dict

    def add_trigger_type_changed_fn(self, fn: callable):
        self.trigger_type_changed_fn_list.append(fn)

    def add_trigger_value_changed_fn(self, fn: callable):
        self.trigger_value_changed_fn_list.append(fn)

    def _on_trigger_type_changed(self, new_trigger_type):
        if new_trigger_type == self.value_dict["type"]:
            return
        new_trigger_cls = TriggersManager.get_instance().get_registered_trigger_type(new_trigger_type)
        self.value_dict = new_trigger_cls.default_dict()
        self.create_ui_models()
        # Notify
        for fn in self.trigger_type_changed_fn_list:
            fn(self.value_dict)

    def _on_trigger_value_changed(self, key, value):
        self.value_dict[key] = value
        # Notify
        for fn in self.trigger_value_changed_fn_list:
            fn(self.value_dict)