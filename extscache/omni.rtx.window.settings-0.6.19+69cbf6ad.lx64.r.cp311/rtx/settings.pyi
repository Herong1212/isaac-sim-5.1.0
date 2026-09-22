"""pybind11 rtx.settings bindings"""
from __future__ import annotations
import rtx.settings
import typing

__all__ = [
    "SETTING_FLAGS_NONE",
    "SETTING_FLAGS_RESET_DISABLED",
    "SETTING_FLAGS_TRANSIENT",
    "get_associated_setting_flags_path",
    "get_internal_setting_string"
]


def get_associated_setting_flags_path(arg0: str) -> str:
    """
    Gets the associated internal setting path to modify the behavior flags that are assigned to each rtx setting.
            It must be set before the app starts or before RTX plugins are loaded to avoid rtx-defaults from being set mistakenly.
            This path is simply produced by replacing 'rtx' parent in the setting path with 'rtx-flags'.
            It allows the behavior of RTX settings to be overridden via SETTING_FLAGS_X flags/attributes.
            Note that using SETTING_FLAGS_TRANSIENT will cause such settings to not be saved to or loaded from USD.

            Args:
                settingPath: RTX setting path to get the associated rtx-flags.

            Returns:
                 The equivalent rtx setting flag path as string.
            
    """
def get_internal_setting_string(arg0: str) -> str:
    pass
SETTING_FLAGS_NONE = 0
SETTING_FLAGS_RESET_DISABLED = 2
SETTING_FLAGS_TRANSIENT = 1
