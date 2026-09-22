# pylint: disable=attribute-defined-outside-init

__all__ = ["get_hotkey_context", "get_hotkey_registry", "HotkeysExtension"]
import carb
import omni.ext
from .context import HotkeyContext
from .registry import HotkeyRegistry
from .trigger import HotkeyTrigger
from .keyboard_layout import USKeyboardLayout, GermanKeyboardLayout, FrenchKeyboardLayout

_hotkey_context = None
_hotkey_registry = None


# public API
def get_hotkey_context() -> HotkeyContext:
    """
    Get the hotkey context.

    Return:
        HotkeyContext object which implements the hotkey context interface.
    """
    return _hotkey_context


def get_hotkey_registry() -> HotkeyRegistry:
    """
    Get the hotkey registry.

    Return:
        HotkeyRegistry object which implements the hotkey registry interface.
    """
    return _hotkey_registry


class HotkeysExtension(omni.ext.IExt):
    """
    Hotkeys extension.
    """
    def on_startup(self, ext_id):
        """
        Extension startup entrypoint.
        """
        self._us_keyboard_layout = USKeyboardLayout()
        self._german_keyboard_layput = GermanKeyboardLayout()
        self._french_keyboard_layout = FrenchKeyboardLayout()

        global _hotkey_context, _hotkey_registry
        _hotkey_context = HotkeyContext()
        _hotkey_registry = HotkeyRegistry()

        self._hotkey_trigger = None
        _settings = carb.settings.get_settings()
        enabled = _settings.get("/exts/omni.kit.hotkeys.core/hotkeys_enabled")
        if enabled:
            self._hotkey_trigger = HotkeyTrigger(_hotkey_registry, _hotkey_context)
        else:
            carb.log_info("All Hotkeys disabled via carb setting /exts/omni.kit.hotkeys.core/hotkeys_enabled=false")

    def on_shutdown(self):
        if self._hotkey_trigger:
            self._hotkey_trigger.destroy()

        self._us_keyboard_layout = None
        self._german_keyboard_layput = None
        self._french_keyboard_layout = None

        global _hotkey_context, _hotkey_registry
        _hotkey_context = None
        _hotkey_registry = None
