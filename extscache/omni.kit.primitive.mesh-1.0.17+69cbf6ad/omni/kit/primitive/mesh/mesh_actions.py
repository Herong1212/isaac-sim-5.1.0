"""This module provides functionalities to register and deregister actions for creating mesh primitives and managing settings within the Omniverse Kit."""

import omni.usd
import omni.kit.commands
import omni.kit.actions.core
from .evaluators import get_geometry_mesh_prim_list


def register_actions(extension_id, cls, get_self_fn):
    """Registers actions for creating mesh primitives and showing the settings window.

    Args:
        extension_id (str): The identifier of the extension registering the actions.
        cls (type): The class type that provides the actions.
        get_self_fn (Callable): Function to get the instance of the class 'cls'."""

    def create_mesh_prim(prim_type):
        usd_context = omni.usd.get_context()
        with omni.kit.usd.layers.active_authoring_layer_context(usd_context):
            omni.kit.commands.execute("CreateMeshPrimWithDefaultXform", prim_type=prim_type, above_ground=True)

    # actions
    for prim in get_geometry_mesh_prim_list():
        omni.kit.actions.core.get_action_registry().register_action(
            extension_id,
            f"create_mesh_prim_{prim.lower()}",
            lambda p=prim: create_mesh_prim(p),
            display_name=f"Create Mesh Prim {prim}",
            description=f"Create Mesh Prim {prim}",
            tag="Create Mesh Prim",
        )

    if get_self_fn() is not None:
        omni.kit.actions.core.get_action_registry().register_action(
            extension_id,
            "show_setting_window",
            get_self_fn().show_setting_window,
            display_name="Show Settings Window",
            description="Show Settings Window",
            tag="Show Settings Window",
        )


def deregister_actions(extension_id):
    """Unregisters all actions associated with the given extension ID.

    Args:
        extension_id (str): Identifier of the extension whose actions are to be deregistered."""
    action_registry = omni.kit.actions.core.get_action_registry()
    action_registry.deregister_all_actions_for_extension(extension_id)
