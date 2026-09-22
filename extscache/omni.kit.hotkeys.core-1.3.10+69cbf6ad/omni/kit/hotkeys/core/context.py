__all__ = ["HotkeyContext"]
from typing import List, Optional
import carb.settings

SETTING_HOTKEY_CURRENT_CONTEXT = "/exts/omni.kit.hotkeys.core/context"


class HotkeyContext:
    def __init__(self):
        """Represent hotkey context."""
        self._queue: List[str] = []
        self._settings = carb.settings.get_settings()

    def push(self, name: str) -> None:
        """
        Push a context.

        Args:
            name (str): name of context
        """
        self._queue.append(name)
        self._update_settings()

    def pop(self) -> Optional[str]:
        """Remove and return last context."""
        poped = self._queue.pop() if self._queue else None
        self._update_settings()
        return poped

    def get(self) -> Optional[str]:
        """Get last context."""
        return self._queue[-1] if self._queue else None

    def clean(self) -> None:
        """Clean all contexts"""
        self._queue.clear()
        self._update_settings()

    def _update_settings(self):
        current = self.get()
        self._settings.set(SETTING_HOTKEY_CURRENT_CONTEXT, current if current else "")
