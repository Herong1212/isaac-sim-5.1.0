import carb
import omni.ext
import omni.kit.app
from omni.kit.actions.core import get_action_registry

from .actions import OmniGraphActions

_HOTKEYS_EXT = "omni.kit.hotkeys.core"
_DEFAULT_HOTKEY_MAP = {
    OmniGraphActions.LAYOUT_NODES: "CTRL+L",
    OmniGraphActions.FRAME_NODES: "F",
    OmniGraphActions.DUPLICATE_SELECTION: "CTRL+D",
    OmniGraphActions.COPY_NODES: "CTRL+C",
    OmniGraphActions.PASTE_NODES: "CTRL+V",
}


class OmniGraphHotkeys:
    """
    Binds hotkeys to the default OmniGraph editor actions. The hotkeys are applied based on window name.

    Extensions must register the actions first (e.g. by creating an instance of OmniGraphActions)
    before creating an instance of this class. Only those actions which have been registered against
    the extension will be given hotkeys. When the hotkeys are no longer needed, call destroy().

    Monitoring the state of the omni.kit.hotkeys.core extension is handled internally.
    """

    def __init__(self, extension_id: str, window_name: str):
        self._extension_id = extension_id
        self._window_name = window_name

        # Watch for hotkey extension enable/disable
        ext_manager = omni.kit.app.get_app_interface().get_extension_manager()
        hooks: omni.ext.IExtensionManagerHooks = ext_manager.get_hooks()

        self._hotkey_extension_enabled_hook = hooks.create_extension_state_change_hook(
            self._on_hotkey_ext_changed,
            omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_ENABLE,
            ext_name="omni.kit.hotkeys.core",
        )
        self._hotkey_extension_disabled_hook = hooks.create_extension_state_change_hook(
            self._on_hotkey_ext_changed,
            omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_DISABLE,
            ext_name="omni.kit.hotkeys.core",
        )

        self._register()

    def destroy(self):
        self._deregister()

    def _register(self):
        ext_manager = omni.kit.app.get_app_interface().get_extension_manager()
        if not ext_manager.is_extension_enabled(_HOTKEYS_EXT):
            carb.log_info(f"{_HOTKEYS_EXT} is not enabled. Cannot register hotkeys.")
            return
        import omni.kit.hotkeys.core as hotkeys

        hotkey_registry = hotkeys.get_hotkey_registry()
        ext_actions = get_action_registry().get_all_actions_for_extension(self._extension_id)
        hotkey_filter = hotkeys.HotkeyFilter(windows=[self._window_name])

        for action in ext_actions:
            key = _DEFAULT_HOTKEY_MAP.get(action.id, None)
            if not key:
                continue

            hotkey_registry.register_hotkey(
                hotkey_ext_id=self._extension_id,
                key=key,
                action_ext_id=action.extension_id,
                action_id=action.id,
                filter=hotkey_filter,
            )

    def _deregister(self):
        ext_manager = omni.kit.app.get_app_interface().get_extension_manager()
        if not ext_manager.is_extension_enabled(_HOTKEYS_EXT):
            carb.log_info(f"{_HOTKEYS_EXT} is not enabled. No hotkeys to deregister.")
            return
        import omni.kit.hotkeys.core as hotkeys

        hotkey_registry = hotkeys.get_hotkey_registry()
        hotkey_registry.deregister_all_hotkeys_for_extension(self._extension_id)

    def _on_hotkey_ext_changed(self, hotkey_ext_id: str, ext_change_type: omni.ext.ExtensionStateChangeType):
        if ext_change_type == omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_ENABLE:
            self._register()

        if ext_change_type == omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_DISABLE:
            self._deregister()
