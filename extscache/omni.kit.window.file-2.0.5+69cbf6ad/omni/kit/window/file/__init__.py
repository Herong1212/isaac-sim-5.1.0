# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""
This extension provides util functions to new/open/save/close USD files. It handles file picking dialog and prompt for unsaved stage.
"""
__all__ = [
    "DialogOptions",
    "get_instance",
    "new",
    "open",
    "open_stage",
    "open_with_new_edit_layer",
    "reopen",
    "save",
    "save_as",
    "close",
    "save_layers",
    "prompt_if_unsaved_stage",
    "add_reference",
    "register_open_stage_addon",
    "register_open_stage_complete",
    "ReadOnlyOptionsWindow",
    "Prompt",
    "StageSaveDialog",
    "IGNORE_UNSAVED_STAGE",
]

from .file_window import *
from .app_ui import DialogOptions
from .read_only_options_window import ReadOnlyOptionsWindow
from .prompt_ui import Prompt
from .save_stage_ui import StageSaveDialog