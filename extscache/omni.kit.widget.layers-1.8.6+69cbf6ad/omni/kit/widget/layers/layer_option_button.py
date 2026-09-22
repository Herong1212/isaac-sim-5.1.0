import carb
from omni.kit.widget.options_button import OptionsButton
from omni.kit.widget.options_menu import OptionItem, OptionSeparator, OptionCustom, OptionLabelMenuItemDelegate
from omni import ui

from .layer_settings import LayerSettings


class LayerOptionItem(OptionItem):
    def __init__(self, name: str, property_name: str):
        if hasattr(LayerSettings(), property_name):
            self.__property_name = property_name
        else:
            carb.log_warn(f"No {self.__property_name} in LayerSettings")
            self.__property_name = None
        super().__init__(
            name,
            default = eval(f"LayerSettings().{self.__property_name}") if self.__property_name else False,
            # on_value_changed_fn=self.__on_value_changed
        )

    def update_value(self):
        if self.__property_name is not None:
            exec(f"LayerSettings().{self.__property_name} = {self.value}")

    def __on_value_changed(self, value: bool) -> None:
        if self.__property_name is not None:
            exec(f"LayerSettings().{self.__property_name} = {value}")


class LayerOptionsButton(OptionsButton):
    def __init__(self, on_reload_layers_fn: callable):
        self.__on_reload_layers = on_reload_layers_fn
        option_items = [
            LayerOptionItem("Auto Reload Layers", "auto_reload_sublayers"),
            OptionCustom(build_fn=lambda: ui.MenuItem("Reload Outdated Layers", delegate=OptionLabelMenuItemDelegate(), triggered_fn=self.__on_reload_layers)),
            OptionSeparator(),
            LayerOptionItem("Show Layer Contents", "show_layer_contents"),
            LayerOptionItem("Show Session Layer", "show_session_layer"),
            LayerOptionItem("Show MetricsAssembler Layer", "show_metricsassembler_layer"),
            LayerOptionItem("Choose Root Layer As Default Location", "file_dialog_show_root_layer_location"),
            LayerOptionItem("Show Info Notification", "show_info_notification"),
            LayerOptionItem("Show Warning Notification", "show_warning_notification"),
            LayerOptionItem("Show Missing Reference", "show_missing_reference"),
            LayerOptionItem("Show Warning for Layer Merge or Flatten Operations", "show_merge_or_flatten_warning"),
            LayerOptionItem("Ignore Notifications for Outdated Layers", "ignore_outdate_notification"),
            OptionSeparator(),
            LayerOptionItem("Auto Authoring Layers (Experimental)", "enable_auto_authoring_mode"),
            LayerOptionItem("Continuous Updates in Auto-Authoring Mode", "continuous_update_in_auto_authoring"),
            LayerOptionItem("Spec Linking Mode (Experimental)", "enable_spec_linking_mode"),
        ]
        super().__init__(option_items, width=20, height=20)

    def set_item_value(self, name: str, value: bool) -> None:
        items = self.model.get_item_children(None)
        for item in items:
            if item.name == name:
                item.value = value
