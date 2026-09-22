from typing import Optional
import carb
import omni.kit.app
from omni.kit.actions.core import get_action_registry


_HOTKEYS_EXT = "omni.kit.hotkeys.core"
_DEFAULT_HOTKEY_MAP = {
    "perspective_camera": "ALT+P",
    "top_camera": "ALT+T",
    "front_camera": "ALT+F",
    "right_camera": "ALT+R",
    "toggle_grid_visibility": "G",
    "toggle_camera_visibility": "SHIFT+C",
    "toggle_light_visibility": "SHIFT+L",
    "toggle_global_visibility": "SHIFT+H",
    "toggle_wireframe": "SHIFT+W",
}


def register_hotkeys(extension_id: str, window_name: Optional[str] = None):

    ext_manager = omni.kit.app.get_app_interface().get_extension_manager()
    if not ext_manager.is_extension_enabled(_HOTKEYS_EXT):
        carb.log_info(f"{_HOTKEYS_EXT} is not enabled. Cannot register hotkeys.")
        return
    import omni.kit.hotkeys.core as hotkeys

    hotkey_registry = hotkeys.get_hotkey_registry()
    action_registry = get_action_registry()
    ext_actions = action_registry.get_all_actions_for_extension(extension_id)
    hotkey_filter = hotkeys.HotkeyFilter(windows=[window_name]) if window_name else None
    hotkey_map = _DEFAULT_HOTKEY_MAP.copy()

    for action in ext_actions:
        key = hotkey_map.get(action.id, None)
        # Not all Actions will have default hotkeys
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
    ext_manager = omni.kit.app.get_app_interface().get_extension_manager()
    if not ext_manager.is_extension_enabled(_HOTKEYS_EXT):
        carb.log_info(f"{_HOTKEYS_EXT} is not enabled. No hotkeys to deregister.")
        return
    import omni.kit.hotkeys.core as hotkeys

    hotkey_registry = hotkeys.get_hotkey_registry()
    hotkey_registry.deregister_all_hotkeys_for_extension(extension_id)
