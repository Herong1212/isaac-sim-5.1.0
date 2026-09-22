import carb.events
from omni.kit.app import register_event_alias

HOTKEY_REGISTER_GLOBAL_EVENT: str = "omni.kit.hotkeys.core.HOTKEY_REGISTER"
HOTKEY_REGISTER_EVENT: int = carb.events.type_from_string(HOTKEY_REGISTER_GLOBAL_EVENT)
register_event_alias(HOTKEY_REGISTER_EVENT, HOTKEY_REGISTER_GLOBAL_EVENT)

HOTKEY_DEREGISTER_GLOBAL_EVENT: str = "omni.kit.hotkeys.core.HOTKEY_DEREGISTER"
HOTKEY_DEREGISTER_EVENT: int = carb.events.type_from_string(HOTKEY_DEREGISTER_GLOBAL_EVENT)
register_event_alias(HOTKEY_DEREGISTER_EVENT, HOTKEY_DEREGISTER_GLOBAL_EVENT)

HOTKEY_CHANGED_GLOBAL_EVENT: str = "omni.kit.hotkeys.core.HOTKEY_CHANGED"
HOTKEY_CHANGED_EVENT: int = carb.events.type_from_string(HOTKEY_CHANGED_GLOBAL_EVENT)
register_event_alias(HOTKEY_CHANGED_EVENT, HOTKEY_CHANGED_GLOBAL_EVENT)
