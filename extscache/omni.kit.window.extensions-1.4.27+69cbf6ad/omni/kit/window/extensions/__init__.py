# flake8: noqa
"""This module provides a user interface for managing and interacting with extensions in the application, including features for controlling extension activation, viewing detailed information, and managing settings."""

__all__ = [
    "ToggleExtension",
    "get_instance",
    "ExtsWindowExtension",
    "SimpleCheckBox",
    "ext_id_to_fullname",
    "open_in_vscode_if_enabled",
    "show_ok_popup",
    "show_user_input_popup",
    "PageBase",
    "ExtInfoWidget",
    "get_open_example_links",
    "ExtSource",
    "ExtsListWidget",
    "_ask_user_for_path",
    "toggle_autoload",
]


from .common import ExtSource, get_open_example_links
from .ext_commands import ToggleExtension
from .ext_components import SimpleCheckBox
from .ext_controller import toggle_autoload
from .ext_export_import import _ask_user_for_path
from .ext_info_widget import ExtInfoWidget, PageBase
from .extension import ExtsWindowExtension, get_instance
from .exts_list_widget import ExtsListWidget
from .utils import *
