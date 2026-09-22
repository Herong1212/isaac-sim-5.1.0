"""This module defines functions to register and deregister create actions for USD prims, cameras, shapes, lights, and audio prims in Omniverse Kit."""

__all__ = []

import omni.kit.actions.core

# pylint: disable=redefined-outer-name, protected-access
import omni.kit.app
import omni.usd


def _get_action_name(name):
    """Converts a given name to a format suitable for action identifiers.

    Args:
        name (str): The original name string to be converted.

    Returns:
        str: The converted string with spaces and hyphens replaced by underscores and in lowercase."""
    return name.lower().replace("-", "_").replace(" ", "_")


def register_actions(extension_id, cls, get_self_fn):
    """Registers multiple create actions to the Omniverse Kit action registry.

    Args:
        extension_id (str): The ID of the extension registering these actions.
        cls: The class that contains callback methods for the actions being registered.
        get_self_fn (Callable): Function that returns an instance of the class containing the action callbacks.

    This function registers several actions related to creating USD prims, including general prims, camera, scope, xform, various shapes, lights, and audio prims. It also includes a toggle for high-quality options. Each action is associated with a display name, description, and belongs to a specified tag group for organization.
    """
    import omni.kit.actions.core

    actions_tag = "Create Menu Actions"

    # actions
    omni.kit.actions.core.get_action_registry().register_action(
        extension_id,
        "create_prim",
        cls.on_create_prim,
        display_name="Create->Create Prim",
        description="Create Prim",
        tag=actions_tag,
    )

    omni.kit.actions.core.get_action_registry().register_action(
        extension_id,
        "create_prim_camera",
        lambda: cls.on_create_prim("Camera", {}),
        display_name="Create->Create Camera Prim",
        description="Create Camera Prim",
        tag=actions_tag,
    )

    omni.kit.actions.core.get_action_registry().register_action(
        extension_id,
        "create_prim_scope",
        lambda: cls.on_create_prim("Scope", {}),
        display_name="Create->Create Scope",
        description="Create Scope",
        tag=actions_tag,
    )

    omni.kit.actions.core.get_action_registry().register_action(
        extension_id,
        "create_prim_xform",
        lambda: cls.on_create_prim("Xform", {}),
        display_name="Create->Create Xform",
        description="Create Xform",
        tag=actions_tag,
    )

    def on_create_shape(shape_name):
        shape_attrs = omni.usd.get_geometry_standard_prim_list()
        cls.on_create_prim(shape_name, shape_attrs[shape_name])

    for prim in omni.usd.get_geometry_standard_prim_list().keys():
        omni.kit.actions.core.get_action_registry().register_action(
            extension_id,
            f"create_prim_{prim.lower()}",
            lambda p=prim: on_create_shape(p),
            display_name=f"Create->Create Prim {prim}",
            description=f"Create Prim {prim}",
            tag=actions_tag,
        )

    for name, prim, attrs in omni.usd.get_light_prim_list():
        omni.kit.actions.core.get_action_registry().register_action(
            extension_id,
            f"create_prim_{_get_action_name(name)}",
            lambda p=prim, a=attrs: cls.on_create_light(p, a),
            display_name=f"Create->Create Prim {name}",
            description=f"Create Prim {name}",
            tag=actions_tag,
        )

    try:
        import usd.schema.audio

        for name, prim, attrs in usd.schema.audio.get_audio_prim_list():  # pylint: disable=c-extension-no-member
            omni.kit.actions.core.get_action_registry().register_action(
                extension_id,
                f"create_prim_{_get_action_name(name)}",
                lambda p=prim, a=attrs: cls.on_create_prim(p, a),
                display_name=f"Create->Create Prim {name}",
                description=f"Create Prim {name}",
                tag=actions_tag,
            )
    except ModuleNotFoundError:
        pass

    omni.kit.actions.core.get_action_registry().register_action(
        extension_id,
        "high_quality_option_toggle",
        get_self_fn()._high_quality_option_toggle,
        display_name="Create->High Quality Option Toggle",
        description="Create High Quality Option Toggle",
        tag=actions_tag,
    )


def deregister_actions(extension_id):
    """Deregisters all actions associated with a given extension ID.

    This function unregisters all actions that were previously registered for a specific extension.
    This is typically called when an extension is being unloaded to clean up any actions it
    contributed to the application's UI or action registry.

    Args:
        extension_id (str): The identifier for the extension whose actions are to be deregistered."""
    action_registry = omni.kit.actions.core.get_action_registry()
    action_registry.deregister_all_actions_for_extension(extension_id)
