__all__ = ["HotkeyFilter"]
from typing import List, Optional


class HotkeyFilter:
    """
    Hotkey filter class.
    """
    def __init__(self, context: Optional[str] = None, windows: Optional[List[str]] = None):
        """
        Define a hotkey filter object.

        Keyword Args:
            context (Optional[str]): Name of context to filter. Default None.
            windows (Optional[List[str]]): List of window names to filter. Default None

        Returns:
            The hotkey filter object that was created.
        """
        self.context = context
        self.windows = windows

    @property
    def windows_text(self):
        """
        String of windows defined in this filter.
        """
        return ",".join(self.windows) if self.windows else ""

    def __eq__(self, other):
        return isinstance(other, HotkeyFilter) and self.context == other.context and self.windows == other.windows

    def __str__(self):
        info = ""
        if self.context:
            info += f"[Context] {self.context}"
        if self.windows:
            info += "[Windows] " + (",".join(self.windows))

        return info
