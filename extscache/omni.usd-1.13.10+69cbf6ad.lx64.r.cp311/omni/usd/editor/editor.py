# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pxr import Usd

## C++ counterpart at include/omni/kit/EditorUsd.h

## Metadata should match whatever defined in source/plugins/omni.kit/usd/omniKit/resources
"""If the metadata exists and is True, the prim is hidden in the prim list of stage window."""
HIDE_IN_STAGE_WINDOW = "hide_in_stage_window"

"""If the metadata exists and is True, the prim should not be removed from stage."""
NO_DELETE = "no_delete"

"""If the metadata exists and is True, picking a prim will always pick the enclosing prim with kind:model."""
ALWAYS_PICK_MODEL = "always_pick_model"

"""If the metadata is set, UI can use it to display user readable name instead of prim name."""
DISPLAY_NAME = "displayName"

# New meta that obeys naming convention
# UI can use this meta to decide if it should be displayed.
"""This metadata is more general than HIDE_IN_STAGE_WINDOW."""
HIDE_IN_UI = "omni:kit:hideInUI"


def set_hide_in_stage_window(prim: Usd.Prim, hide: bool):
    """Sets metadata for prim to instruct stage window to display/hide the prim."""

    if hide is None:
        prim.ClearMetadata(HIDE_IN_STAGE_WINDOW)
    else:
        prim.SetMetadata(HIDE_IN_STAGE_WINDOW, hide)


def is_hide_in_stage_window(prim: Usd.Prim) -> bool:
    """Whether the prim should be hidden in the stage window or not."""

    return prim.GetMetadata(HIDE_IN_STAGE_WINDOW)


def set_no_delete(prim: Usd.Prim, no_delete: bool):
    """Sets metadata for prim to instruct UI whether the prim can be removed or not."""

    if no_delete is None:
        prim.ClearMetadata(NO_DELETE)
    else:
        prim.SetMetadata(NO_DELETE, no_delete)


def is_no_delete(prim: Usd.Prim) -> bool:
    """Whether the prim should be removed or not."""

    return prim.GetMetadata(NO_DELETE)


def set_always_pick_model(prim: Usd.Prim, pick_model: bool):
    """Sets metadata for prim to instruct selection whether it should always pick the enclosing prim with kind:model or not."""

    if pick_model is None:
        prim.ClearMetadata(ALWAYS_PICK_MODEL)
    else:
        prim.SetMetadata(ALWAYS_PICK_MODEL, pick_model)


def is_always_pick_model(prim: Usd.Prim) -> bool:
    """Whether selecting this prim should always pick the enclosing prim with kind:model or not."""

    return prim.GetMetadata(ALWAYS_PICK_MODEL)


def set_hide_in_ui(prim: Usd.Prim, value: bool):
    """Sets metadata for the prim to instruct UI whether it should be hidden in the UI or not."""

    if value is None:
        prim.ClearMetadata(HIDE_IN_UI)
    else:
        prim.SetMetadata(HIDE_IN_UI, value)


def is_hide_in_ui(prim: Usd.Prim) -> bool:
    """Whether the prim should be hidden or not."""

    return prim.GetMetadata(HIDE_IN_UI)


def set_display_name(prim: Usd.Prim, name: str):
    """Sets an user readable name for the prim to instruct UI to display it."""

    if name is None:
        prim.ClearMetadata(DISPLAY_NAME)
    else:
        prim.SetMetadata(DISPLAY_NAME, str(name))


def get_display_name(prim) -> str:
    """Gets display name from the metadata of the prim."""

    return prim.GetMetadata(DISPLAY_NAME)
