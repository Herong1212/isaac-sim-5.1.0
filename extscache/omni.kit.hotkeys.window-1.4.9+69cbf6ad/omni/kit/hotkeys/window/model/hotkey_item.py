__all__ = [
    "AbstractFilterItem",
    "GlobalFilterItem",
    "FilterWindowItem",
    "FilterContextItem",
    "EmptyFilterWindowItem",
    "AddWindowItem",
    "EmptyHotkey",
    "HotkeyDetailItem",
    "EmptyHotkeyItem"
]
from typing import Optional

from omni.kit.hotkeys.core import Hotkey, KeyCombination, get_hotkey_registry
from omni.kit.actions.core import get_action_registry
from omni.kit.actions.window import AbstractActionItem, ActionExtItem

# Hotkey ext id for all hotkeys created from here
USER_HOTKEY_EXT_ID = "omni.kit.hotkeys.window"


class AbstractFilterItem(ActionExtItem):
    def __init__(self, hotkey_filter: str, highlight: Optional[str] = None):
        super().__init__(hotkey_filter, highlight=highlight)


class GlobalFilterItem(AbstractFilterItem):
    def __init__(self, highlight: Optional[str] = None):
        super().__init__("Global", highlight=highlight)


class FilterWindowItem(AbstractFilterItem):
    def __init__(self, window_title, highlight: Optional[str] = None):
        super().__init__(window_title, highlight=highlight)


class FilterContextItem(AbstractFilterItem):
    def __init__(self, context, highlight: Optional[str] = None):
        super().__init__(context, highlight=highlight)


class EmptyFilterWindowItem(FilterWindowItem):
    def __init__(self):
        super().__init__("")


class AddWindowItem(FilterWindowItem):
    def __init__(self):
        super().__init__("Add Window")


class EmptyHotkey(Hotkey):
    def __init__(self, hotkey_ext_id: str):
        super().__init__(hotkey_ext_id, KeyCombination(""), "", "", filter=None)


class HotkeyDetailItem(AbstractActionItem):
    def __init__(self, hotkey: Hotkey, highlight: Optional[str] = None):
        super().__init__(hotkey.action_id, highlight=highlight)
        self.hotkey = hotkey
        self.action = get_action_registry().get_action(hotkey.action_ext_id, hotkey.action_id) if hotkey.action_ext_id and hotkey.action_id else None
        hotkey_registry = get_hotkey_registry()
        (self.default_key_id, self.default_filter) = hotkey_registry.get_hotkey_default(hotkey)
        self.user_defined = hotkey_registry.is_user_hotkey(hotkey)

    def is_modified(self) -> bool:
        return (not self.user_defined) and (self.hotkey.key_combination.id != self.default_key_id or self.hotkey.filter != self.default_filter)

    @property
    def action_display(self) -> str:
        return self.hotkey.action.display_name if self.action else self.hotkey.action_text


class EmptyHotkeyItem(AbstractActionItem):
    def __init__(self, hotkey_ext_id: str = USER_HOTKEY_EXT_ID):
        super().__init__("__EMPTY_HOTKEY__")
        self.hotkey = EmptyHotkey(hotkey_ext_id)
        self.user_defined = False

    @property
    def action_display(self) -> str:
        action = get_action_registry().get_action(self.hotkey.action_ext_id, self.hotkey.action_id) if self.hotkey.action_ext_id and self.hotkey.action_id else None
        return action.display_name if action else self.hotkey.action_text
