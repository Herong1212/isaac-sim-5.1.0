__all__ = ["SettingsDefaultHandler", "RenderSettingsDefaults"]

import carb.dictionary
import carb.settings


class SettingsDefaultHandler:
    def __init__(self):
        self._settings = carb.settings.get_settings()
        self._dictionary = carb.dictionary.get_dictionary()

    def _get_sanitized_path(self, path):
        if path is not None and len(path) > 0 and path[0] == "/":
            return path[1:]
        return ""

    def get_type(self, path):
        settings_dict = self._settings.get_settings_dictionary("")
        path = self._get_sanitized_path(path)
        item = self._dictionary.get_item(settings_dict, path)
        item_type = self._dictionary.get_item_type(item)
        return item_type

    def does_exist(self, path):
        return self.get_type(path) != carb.dictionary.ItemType.COUNT

    def set_default(self, path):
        item_type = self.get_type(path)
        if item_type == carb.dictionary.ItemType.FLOAT:
            self._settings.set(path, 0.0)
        elif item_type == carb.dictionary.ItemType.INT:
            self._settings.set(path, 0)
        elif item_type == carb.dictionary.ItemType.BOOL:
            self._settings.set(path, False)
        else:
            print("SettingsDefaultHandler unrecognised type", item_type)


class RenderSettingsDefaults:
    """
    This is a partial python implementation of Kit/rendering/include/rtx/utils/Settings.h
    which only provides sufficient functionality for getting/resetting default values
    by
    """

    try:
        _settings = carb.settings.get_settings()
    except Exception:
        _settings = None

    @classmethod
    def _get_associated_defaults_path(cls, settings_path: str):
        bits = settings_path.split("/")
        if len(bits) == 2:
            return "/" + bits[1] + "-defaults"
        else:
            return "/" + bits[1] + "-defaults/" + "/".join(bits[2:])

    def reset_setting_to_default(self, settings_path: str):
        defaultsPathStorage = self._get_associated_defaults_path(settings_path)
        srcItem = self._settings.get_settings_dictionary(defaultsPathStorage)

        # If we can't find a dictionary item, it's likely to be leaf node/scalar value
        if (
            srcItem is None
            or carb.dictionary.get_dictionary().get_item_type(srcItem) != carb.dictionary.ItemType.DICTIONARY
        ):
            defaultValue = self._settings.get(defaultsPathStorage)
            self._settings.set(settings_path, defaultValue)
        # It's a dictionary Item.. just update the whole section
        elif isinstance(srcItem, carb.dictionary._dictionary.Item):
            self._settings.update(settings_path, srcItem, "", carb.dictionary.UpdateAction.OVERWRITE)
        else:
            print("reset_setting_to_default: unknown type")
