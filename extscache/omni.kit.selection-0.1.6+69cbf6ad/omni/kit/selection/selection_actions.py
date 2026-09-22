import omni.kit.actions.core


def register_actions(extension_id):
    import omni.kit.commands

    action_registry = omni.kit.actions.core.get_action_registry()
    actions_tag = "Selection Actions"

    action_registry.register_action(
        extension_id,
        "all",
        lambda: omni.kit.commands.execute("SelectAll"),
        display_name="Select->All",
        description="Select all prims.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "none",
        lambda: omni.kit.commands.execute("SelectNone"),
        display_name="Select->None",
        description="Deselect all prims.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "invert",
        lambda: omni.kit.commands.execute("SelectInvert"),
        display_name="Select->Invert",
        description="Deselect all currently unselected prims, and select all currently unselected prims.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "parent",
        lambda: omni.kit.commands.execute("SelectParentCommand"),
        display_name="Select->Parent",
        description="Select the parents of all currently selected prims.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "leaf",
        lambda: omni.kit.commands.execute("SelectLeafCommand"),
        display_name="Select->Leaf",
        description="Select the leafs of all currently selected prims.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "hierarchy",
        lambda: omni.kit.commands.execute("SelectHierarchyCommand"),
        display_name="Select->Hierarchy",
        description="Select the hierachies of all currently selected prims.",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "similar",
        lambda: omni.kit.commands.execute("SelectSimilarCommand"),
        display_name="Select->Similar",
        description="Select prims of the same type as any currently selected prim.",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "HideUnselected",
        lambda: omni.kit.commands.execute("HideUnselected"),
        display_name="Select->Hide Unselected",
        description="Hide Unselected Prims",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "UnhideAllPrims",
        lambda: omni.kit.commands.execute("UnhideAllPrims"),
        display_name="Select->Unhide All Prims",
        description="Unhide All Prims",
        tag=actions_tag,
    )


def deregister_actions(extension_id):
    action_registry = omni.kit.actions.core.get_action_registry()
    action_registry.deregister_all_actions_for_extension(extension_id)
