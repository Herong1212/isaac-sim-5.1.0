# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""Register/Deregister actions of the extension."""
__all__ = ["register_actions", "deregister_actions"]
import omni.kit.actions.core
from .app_ui import DialogOptions


def register_actions(extension_id: str):
    """
    Register actions.
    Args:
        extension_id(str): Extension name with version part removed.
    """
    import omni.kit.window.file

    action_registry = omni.kit.actions.core.get_action_registry()
    actions_tag = "File Actions"

    action_registry.register_action(
        extension_id,
        "new",
        omni.kit.window.file.new,
        display_name="File->New",
        description="Create a new USD stage.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "open",
        omni.kit.window.file.open,
        display_name="File->Open",
        description="Open an existing USD stage.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "open_stage",
        omni.kit.window.file.open_stage,
        display_name="File->Open Stage",
        description="Open an named USD stage.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "reopen",
        omni.kit.window.file.reopen,
        display_name="File->Reopen",
        description="Reopen the currently opened USD stage.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "open_with_new_edit_layer",
        omni.kit.window.file.open_with_new_edit_layer,
        display_name="File->Open With New Edit Layer",
        description="Open an existing USD stage with a new edit layer.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "save",
        lambda: omni.kit.window.file.save(dialog_options=DialogOptions.HIDE),
        display_name="File->Save",
        description="Save the currently opened USD stage to file.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "save_with_options",
        lambda: omni.kit.window.file.save(dialog_options=DialogOptions.FORCE),
        display_name="File->Save With Options",
        description="Save the currently opened USD stage to file.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "save_as",
        lambda: omni.kit.window.file.save_as(False),
        display_name="File->Save As",
        description="Save the currently opened USD stage to a new file.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "save_as_flattened",
        lambda: omni.kit.window.file.save_as(True),
        display_name="File->Save As Flattened",
        description="Save the currently opened USD stage to a new flattened file.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "add_reference",
        lambda: omni.kit.window.file.add_reference(is_payload=False),
        display_name="File->Add Reference",
        description="Add a reference to a file.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "add_payload",
        lambda: omni.kit.window.file.add_reference(is_payload=True),
        display_name="File->Add Payload",
        description="Add a payload to a file.",
        tag=actions_tag,
    )


def deregister_actions(extension_id: str):
    """
    Deregister actions.
    Args:
        extension_id(str): Extension name with version part removed.
    """
    action_registry = omni.kit.actions.core.get_action_registry()
    action_registry.deregister_all_actions_for_extension(extension_id)
