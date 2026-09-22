__all__ = ["is_window_hovered", "get_hovered_window"]
from typing import Optional, List
import omni.ui as ui

EXCLUDE_WINDOWS = [
    "Debug##Default",
]


def is_window_hovered(pos_x: float, pos_y: float, window: ui.Window) -> bool:
    """
    Check if window under mouse position.
    Args:
        pos_x (float): X position.
        pos_y (float): Y position.
        window (ui.Window): Window to check.
    """
    # if window hasn't been drawn yet docked may not be valid, so check dock_id also
    # OM-65505: For ui.ToolBar, is_selected_in_dock always return False if docked.
    if not window or not window.visible or ((window.docked or window.dock_id != 0) and (not isinstance(window, ui.ToolBar) and not window.is_selected_in_dock())):
        return False

    if (window.position_x + window.width > pos_x > window.position_x
            and window.position_y + window.height > pos_y > window.position_y):
        return True
    return False


def get_hovered_window(pos_x: float, pos_y: float) -> Optional[str]:
    """
    Get first window under mouse.

    Args:
        pos_x (float): X position.
        pos_y (float): Y position.

    Return None if nothing found.
    If multiple window found, float window first. If multiple float window, just first result
    """
    hovered_float_windows: List[ui.Window] = []
    hovered_docked_windows: List[ui.Window] = []
    dpi = ui.Workspace.get_dpi_scale()
    pos_x /= dpi
    pos_y /= dpi
    windows = ui.Workspace.get_windows()
    for window in windows:
        if window.title in EXCLUDE_WINDOWS:
            continue
        # OMPRW-513: We want to make sure the window an instance of ui.Window, because
        # destroyed windows can still return a valid ui.WindowHandle instance
        if isinstance(window, ui.Window) and is_window_hovered(pos_x, pos_y, window):
            if window.docked:
                hovered_docked_windows.append(window)
            else:
                hovered_float_windows.append(window)

    if hovered_float_windows:
        return hovered_float_windows[0]
    if hovered_docked_windows:
        return hovered_docked_windows[0]
    return None
