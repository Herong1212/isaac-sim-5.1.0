__all__ = ["SAVED_SETTINGS_OPTIONS_MENU", "ConfigItem", "ConfigButton"]
from typing import Callable, Dict
import carb.settings
from omni.kit.widget.options_button import OptionsButton
from omni.kit.widget.options_menu import OptionsModel, OptionItem

SAVED_SETTINGS_OPTIONS_MENU = "/persistent/app/omniverse/filepicker/options_menu/"

class ConfigItem(OptionItem):
    def __init__(self, name: str, text: str, default: bool):
        self.__settings_path = SAVED_SETTINGS_OPTIONS_MENU + name
        self.__settings = carb.settings.get_settings()
        super().__init__(name, text=text, default = self.__get_default(default), on_value_changed_fn=self.__on_value_changed)

    def __get_default(self, default: bool) -> bool:
        value = self.__settings.get(self.__settings_path)
        return default if value is None else value
    
    def __on_value_changed(self, value: bool) -> None:
        self.__settings.set(self.__settings_path, value)


class ConfigButton(OptionsButton):
    def __init__(self, enable_soft_delete: bool, on_value_changed_fn: Callable[[Dict[str, bool]], None] = None):
        config_items = [
            ConfigItem("hide_unknown", "Hide Unknown File Types", False),
            ConfigItem("hide_thumbnails", "Hide Thumbnails Folders", True),
            ConfigItem("show_details", "Show Details", False),
            ConfigItem("show_udim_sequence", "Display UDIM Sequence", False),
        ]
        if enable_soft_delete:
            config_items.append(ConfigItem("show_deleted", "Show Deleted", False))
        super().__init__(config_items)

        self.__on_value_changed_fn = on_value_changed_fn
        self.__sub = self.model.subscribe_item_changed_fn(self.__on_value_changed)

    @property
    def values(self) -> Dict[str, bool]:
        """
        Option values in dict.
        """
        values = {}
        for item in self.model.get_item_children(None):
            values[item.name] = item.value

        return values
    
    @values.setter
    def values(self, v: Dict[str, bool]) -> bool:
        for item in self.model.get_item_children(None):
            if item.name in v:
                item.value = v[item.name]

    def destroy(self):
        self.__sub = None
        super().destroy()

    def __on_value_changed(self, model: OptionsModel, item: ConfigItem) -> None:
        values = {}
        for item in model.get_item_children(None):
            values[item.name] = item.value

        if self.__on_value_changed_fn:
            self.__on_value_changed_fn(values)