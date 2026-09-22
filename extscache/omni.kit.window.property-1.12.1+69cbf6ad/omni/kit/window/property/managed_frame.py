"""
omni.kit.window.property managed_frame functions. This provides persistent open/closed states for ui.CollapsableFrames
"""

import omni.ui as ui

__all__ = ["prep", "set_collapsed_state", "get_collapsed_state", "reset_collapsed_state"]

collapsed_settings = {}


def prep(frame: ui.CollapsableFrame, group_name: str):
    """Update ui.CollapsableFrame and insert hooks so collapsed state can be tracked.

    Args:
        frame (ui.CollapsableFrame): frame to be prepared.
        group_name (str): group name of the frame.
    """
    index_name = f"{group_name}/{frame.title}"
    state = collapsed_settings.get(index_name, None)
    if state is not None:
        frame.collapsed = state
    frame.set_collapsed_changed_fn(lambda c, i=index_name: set_collapsed_state(i, c))


def set_collapsed_state(index_name: str, state: bool):
    """Set new collapsed state.

    Args:
        index_name (str): group name of the frame.
        state (bool): new collapsed state of the frame.
    """
    if state is None:
        del collapsed_settings[index_name]
    else:
        collapsed_settings[index_name] = state


def get_collapsed_state(index_name: str = None):
    """Get current collapsed state for `index_name`.

    Args:
        index_name (str): group name of the frame.

    Returns:
        dict: collapsed settings dictionary.
    """
    if index_name:
        state = collapsed_settings.get(index_name, None)
        return state
    return collapsed_settings


def reset_collapsed_state():
    """Reset collapsed state data, so default will be used."""
    global collapsed_settings

    collapsed_settings = {}
