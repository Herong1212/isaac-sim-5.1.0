"""Register material actions class."""

__all__ = ["register_actions", "deregister_actions"]

import omni.kit.actions.core

def register_actions(extension_id, cls):
    """
    Register material actions.

    Arg:
        extension_id (str): extensions id.
        cls (class): callers class for function calls.
    """
    # actions
    created_actions = []
    omni.kit.actions.core.get_action_registry().register_action(
        extension_id,
        "create_material_and_assign",
        cls._create_material_and_assign,
        display_name="create_material_and_assign",
        description="create_material_and_assign",
        tag="Material Library Actions",
    )
    # add to material_actions list to prevent action from being created again
    created_actions.append("create_material_and_assign")

    omni.kit.actions.core.get_action_registry().register_action(
        extension_id,
        "create_usd_preview_surface_material_and_assign",
        cls._on_create_preview_surface,
        display_name="create_usd_preview_surface_material_and_assign",
        description="USD Preview Surface",
        tag="Material Library Actions",
    )
    created_actions.append("create_usd_preview_surface_material_and_assign")

    omni.kit.actions.core.get_action_registry().register_action(
        extension_id,
        "create_usd_preview_surface_texture_material_and_assign",
        cls._on_create_preview_surface_texture,
        display_name="create_usd_preview_surface_texture_material_and_assign",
        description="USD Preview USD Preview Surface Texture",
        tag="Material Library Actions",
    )
    created_actions.append("create_usd_preview_surface_texture_material_and_assign")

    omni.kit.actions.core.get_action_registry().register_action(
        extension_id,
        "create_add_mdl_file_material_and_assign",
        cls._on_create_custom_mdl_material,
        display_name="create_add_mdl_file_material_and_assign",
        description="Add MDL File",
        tag="Material Library Actions",
    )
    created_actions.append("create_add_mdl_file_material_and_assign")

    omni.kit.actions.core.get_action_registry().register_action(
        extension_id,
        "create_add_mtlx_file_material_and_assign",
        cls._on_create_custom_mtlx_material,
        display_name="create_add_mtlx_file_material_and_assign",
        description="Add MaterialX Reference",
        tag="Material Library Actions",
    )
    created_actions.append("create_add_mtlx_file_material_and_assign")

    return created_actions

def deregister_actions(extension_id): # pragma: no cover
    """
    Unregister material actions.

    Arg:
        extension_id (str): extensions id.
    """
    action_registry = omni.kit.actions.core.get_action_registry()
    if action_registry:
        action_registry.deregister_all_actions_for_extension(extension_id)
