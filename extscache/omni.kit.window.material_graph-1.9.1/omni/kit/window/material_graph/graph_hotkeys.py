from typing import Optional

import carb
import omni.kit.app
from omni.kit.actions.core import get_action_registry

g_action_registry = get_action_registry()
g_ext_manager = omni.kit.app.get_app_interface().get_extension_manager()

_HOTKEYS_EXT = "omni.kit.hotkeys.core"
_DEFAULT_HOTKEY_MAP = {
    "layout_all_nodes": "CTRL+L",
    "focus_on_nodes": "F",
    "copy_nodes": "CTRL+C",
    "paste_nodes": "CTRL+V",
    "expand_all_nodes": "KEY_1",
    "minimize_all_nodes": "KEY_2",
    "close_all_nodes": "KEY_3",
}

app = omni.kit.app.acquire_app_interface()
if float(app.get_kit_version_short()) >= 105:
    _DEFAULT_HOTKEY_MAP.update({"material_unpause_and_pause": "CTRL+R"})


def register_hotkeys(extension_id: str, window_name: Optional[str] = None):
    if not g_ext_manager.is_extension_enabled(_HOTKEYS_EXT):
        carb.log_info(f"{_HOTKEYS_EXT} is not enabled. Cannot register hotkeys.")
        return
    import omni.kit.hotkeys.core as hotkeys

    hotkey_registry = hotkeys.get_hotkey_registry()
    ext_actions = g_action_registry.get_all_actions_for_extension(extension_id)
    hotkey_filter = hotkeys.HotkeyFilter(windows=[window_name]) if window_name else None

    for action in ext_actions:
        key = _DEFAULT_HOTKEY_MAP.get(action.id, None)
        if not key:
            continue

        hotkey_registry.register_hotkey(
            hotkey_ext_id=extension_id,
            key=key,
            action_ext_id=action.extension_id,
            action_id=action.id,
            filter=hotkey_filter,
        )


def deregister_hotkeys(extension_id: str):
    if not g_ext_manager.is_extension_enabled(_HOTKEYS_EXT):
        carb.log_info(f"{_HOTKEYS_EXT} is not enabled. No hotkeys to deregister.")
        return
    import omni.kit.hotkeys.core as hotkeys

    hotkey_registry = hotkeys.get_hotkey_registry()
    hotkey_registry.deregister_all_hotkeys_for_extension(extension_id)
