__all__ = ["HotkeyDescription", "HotkeyStorage"]
import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Tuple
import carb.settings
from .hotkey import Hotkey
from .filter import HotkeyFilter
from .key_combination import KeyCombination


# Hotkey ext id for all hotkeys created from here
USER_HOTKEY_EXT_ID = "omni.kit.hotkeys.window"
SETTING_USER_HOTKEYS = "/persistent/omni.kit.hotkeys.core/userHotkeys"


@dataclass
class HotkeyDescription:
    hotkey_ext_id: str = ""
    action_ext_id: str = ""
    action_id: str = ""
    key: str = ""
    trigger_press: bool = True
    context: str = None
    windows: str = None

    @staticmethod
    def from_hotkey(hotkey: Hotkey):
        (context, windows) = HotkeyDescription.get_filter_string(hotkey)
        return HotkeyDescription(
            hotkey_ext_id=hotkey.hotkey_ext_id,
            action_ext_id=hotkey.action_ext_id,
            action_id=hotkey.action_id,
            key=hotkey.key_combination.as_string,
            trigger_press=hotkey.key_combination.trigger_press,
            context=context,
            windows=windows,
        )

    @property
    def id(self) -> str:  # noqa: A003
        return self.to_hotkey().id

    def to_hotkey(self) -> Hotkey:
        if self.context or self.windows:
            hotkey_filter = HotkeyFilter(context=self.context if self.context else None, windows=self.windows.split(",") if self.windows else None)
        else:
            hotkey_filter = None

        key = KeyCombination(self.key, trigger_press=self.trigger_press)

        return Hotkey(self.hotkey_ext_id, key, self.action_ext_id, self.action_id, filter=hotkey_filter)

    def update(self, hotkey: Hotkey) -> None:
        self.key = hotkey.key_combination.as_string
        self.trigger_press = hotkey.key_combination.trigger_press
        (self.context, self.windows) = HotkeyDescription.get_filter_string(hotkey)

    @staticmethod
    def get_filter_string(hotkey: Hotkey) -> Tuple[str, str]:
        return (
            hotkey.filter.context if hotkey.filter and hotkey.filter else "",
            ",".join(hotkey.filter.windows) if hotkey.filter and hotkey.filter.windows else ""
        )


class HotkeyStorage:
    def __init__(self):
        self.__settings = carb.settings.get_settings()
        self.__hotkey_descs: List[HotkeyDescription] = [HotkeyDescription(**desc) for desc in self.__settings.get(SETTING_USER_HOTKEYS) or []]
        carb.log_info(f"[Hotkey] {len(self.__hotkey_descs)} user defined hotkeys")

    def get_hotkey(self, hotkey: Hotkey) -> Optional[Hotkey]:
        """
        Get hotkey definition in storage.
        """
        hotkey_desc = self.__find_hotkey_desc(hotkey)
        return hotkey_desc.to_hotkey() if hotkey_desc else None

    def get_user_hotkeys(self) -> List[Hotkey]:
        """
        Get all user-defined hotkeys.
        """
        user_hotkeys: List[Hotkey] = []
        for hotkey_desc in self.__hotkey_descs:
            hotkey = hotkey_desc.to_hotkey()
            if self.is_user_hotkey(hotkey):
                user_hotkeys.append(hotkey)

        return user_hotkeys

    def get_hotkeys(self) -> List[Hotkey]:
        """
        Discover all hotkey definitions in this storage.
        """
        return [desc.to_hotkey() for desc in self.__hotkey_descs]

    def register_user_hotkey(self, hotkey: Hotkey):
        """
        Register user hotkey.
        """
        if self.is_user_hotkey(hotkey):
            # This is user defined hotkey
            hotkey_desc = HotkeyDescription().from_hotkey(hotkey)
            self.__hotkey_descs.append(hotkey_desc)
            self.__settings.set(SETTING_USER_HOTKEYS, [asdict(desc) for desc in self.__hotkey_descs])

    def edit_hotkey(self, hotkey: Hotkey):
        """
        Edit hotkey.

        This could be a user-defined hotkey or system hotkey but changed by user.
        """
        # This is system hotkey but user changed key bindings, etc.
        hotkey_desc = self.__find_hotkey_desc(hotkey)
        if hotkey_desc:
            hotkey_desc.update(hotkey)
        else:
            hotkey_desc = HotkeyDescription().from_hotkey(hotkey)
            self.__hotkey_descs.append(hotkey_desc)
        self.__settings.set(SETTING_USER_HOTKEYS, [asdict(desc) for desc in self.__hotkey_descs])

    def deregister_hotkey(self, hotkey: Hotkey):
        """
        Deregister user hotkey from storage.

        For system hotkey, keep in storage to reload when register again
        """
        if self.is_user_hotkey(hotkey):
            hotkey_desc = HotkeyDescription().from_hotkey(hotkey)
            if hotkey_desc in self.__hotkey_descs:
                self.__hotkey_descs.remove(hotkey_desc)
                self.__settings.set(SETTING_USER_HOTKEYS, [asdict(desc) for desc in self.__hotkey_descs])

    def disable_hotkey(self, hotkey: Hotkey):
        """
        Disable system hotkey.
        Disable means set key to empty string in storage.
        """
        if not self.is_user_hotkey(hotkey):
            hotkey_desc = self.__find_hotkey_desc(hotkey)
            if not hotkey_desc:
                hotkey_desc = HotkeyDescription().from_hotkey(hotkey)
                self.__hotkey_descs.append(hotkey_desc)
            hotkey_desc.key = ""
            self.__settings.set(SETTING_USER_HOTKEYS, [asdict(desc) for desc in self.__hotkey_descs])

    def __find_hotkey_desc(self, hotkey: Hotkey) -> Optional[HotkeyDescription]:
        """
        Find if there is user-defined hotkey
        """
        for hotkey_desc in self.__hotkey_descs:
            if hotkey_desc.id == hotkey.id:
                return hotkey_desc

        return None

    def clear_hotkeys(self) -> None:
        """
        Clear all hotkeys in storage
        """
        self.__hotkey_descs = []
        self.__settings.set(SETTING_USER_HOTKEYS, [])

    def is_user_hotkey(self, hotkey: Hotkey) -> bool:
        """
        If a user-defined hotkey
        """
        return hotkey.hotkey_ext_id == USER_HOTKEY_EXT_ID

    def save_preset(self, url: str) -> bool:
        """
        Save storage to file.
        """
        output = {
            "Type": "Hotkey Preset",
            "Keys": [asdict(desc) for desc in self.__hotkey_descs]
        }
        try:
            with open(url, "w", encoding="utf8") as json_file:
                json.dump(output, json_file, indent=4)
                json_file.close()
                carb.log_info(f"Saved hotkeys preset to {url}!")
        except FileNotFoundError:
            carb.log_warn(f"Failed to open {url}!")
            return False
        except PermissionError:
            carb.log_warn(f"Cannot write to {url}: permission denied!")
            return False
        except Exception as e:  # pylint: disable=broad-except
            carb.log_warn(f"Unknown failure to write to {url}: {e}")
            return False
        finally:
            if json_file:
                json_file.close()
        return bool(json_file)

    def load_preset(self, preset: List[Dict]) -> None:
        """
        Load hotkey preset.
        """
        self.clear_hotkeys()
        self.__hotkey_descs = [HotkeyDescription(**desc) for desc in preset]
        self.__settings.set(SETTING_USER_HOTKEYS, [asdict(desc) for desc in self.__hotkey_descs])

    def preload_preset(self, url: str) -> Optional[Dict]:
        """
        Preload hotkey preset from file.
        """
        keys_json = None
        try:
            with open(url, "r", encoding="utf8") as json_file:
                keys_json = json.load(json_file)
        except FileNotFoundError:
            carb.log_error(f"Failed to open {url}!")
        except PermissionError:
            carb.log_error(f"Cannot read {url}: permission denied!")
        except Exception as exc:  # pylint: disable=broad-except
            carb.log_error(f"Unknown failure to read {url}: {exc}")

        if keys_json is None:
            return None

        if keys_json.get("Type", None) != "Hotkey Preset":
            carb.log_error(f"{url} is not a valid hotkey preset file!")
            return None

        if "Keys" not in keys_json:
            carb.log_error(f"{url} is not a valid hotkey preset: No key found!")
            return None

        return keys_json["Keys"]
