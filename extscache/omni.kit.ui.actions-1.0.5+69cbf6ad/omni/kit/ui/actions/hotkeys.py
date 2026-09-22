from typing import Optional
import carb
import omni.kit.app
from omni.kit.actions.core import get_action_registry


_HOTKEYS_EXT = "omni.kit.hotkeys.core"

def register_hotkeys(extension_id: str, window_name: Optional[str] = None):
    ext_manager = omni.kit.app.get_app_interface().get_extension_manager()
    if not ext_manager.is_extension_enabled(_HOTKEYS_EXT):
        carb.log_info(f"{_HOTKEYS_EXT} is not enabled. Cannot register hotkeys.")
        return
    import omni.kit.hotkeys.core as hotkeys
    from dataclasses import dataclass

    @dataclass
    class KeyItem:
        key: str
        filter: list

    hotkey_registry = hotkeys.get_hotkey_registry()
    action_registry = get_action_registry()
    ext_actions = action_registry.get_all_actions_for_extension(extension_id)
    hotkey_filter = hotkeys.HotkeyFilter(windows=[window_name]) if window_name else None
    hotkey_map = {}

    # add UI hotkeys
    # NOTE: There is no "exts/omni.kit.viewport.actions/ui_hotkeys" defined as default
    if carb.settings.get_settings().get("exts/omni.kit.viewport.actions/ui_hotkeys"):
        hotkey_map["toggle_ui"] = KeyItem("F7", hotkey_filter)
        # check if IAppWindowImplOs has already registered F11
        if not carb.settings.get_settings().get("/exts/omni.appwindow/listenF11"):
            hotkey_map["toggle_fullscreen"] = KeyItem("F11", hotkey_filter)

        if carb.settings.get_settings().get_as_bool( "/app/window/showDpiScaleMenu"):
            hotkey_map["dpi_scale_increase"] = KeyItem("EQUAL", hotkey_filter)
            hotkey_map["dpi_scale_decrease"] = KeyItem("MINUS", hotkey_filter)

    for action in ext_actions:
        hk_item = hotkey_map.get(action.id, None)
        # Not all Actions will have default hotkeys
        if hk_item and hk_item.key:
            hotkey_registry.register_hotkey(
                hotkey_ext_id=extension_id,
                key=hk_item.key,
                action_ext_id=action.extension_id,
                action_id=action.id,
                filter=hk_item.filter,
            )


def deregister_hotkeys(extension_id: str):
    ext_manager = omni.kit.app.get_app_interface().get_extension_manager()
    if not ext_manager.is_extension_enabled(_HOTKEYS_EXT):
        carb.log_info(f"{_HOTKEYS_EXT} is not enabled. No hotkeys to deregister.")
        return
    import omni.kit.hotkeys.core as hotkeys

    hotkey_registry = hotkeys.get_hotkey_registry()
    hotkey_registry.deregister_all_hotkeys_for_extension(extension_id)
