import omni.kit.actions.core
import omni.kit.app

LAYOUT_ALL = "layout_all_nodes"
FOCUS_ON_NODES = "focus_on_nodes"
EXPAND_ALL = "expand_all_nodes"
MINIMIZE_ALL = "minimize_all_nodes"
CLOSE_ALL = "close_all_nodes"
COPY_NODES = "copy_nodes"
PASTE_NODES = "paste_nodes"
TOGGLE_MATERIAL_COMPILATION = "toggle_material_compilation"
MATERIAL_UNPAUSE_AND_PAUSE = "material_unpause_and_pause"


def register_actions(extension_id: str, ext_instance):
    action_registry = omni.kit.actions.core.get_action_registry()
    actions_tag = "Material Graph Actions"

    action_registry.register_action(
        extension_id,
        FOCUS_ON_NODES,
        ext_instance.focus_on_nodes,
        display_name="Focus on Nodes",
        description="Fit Graph View to Selected Nodes or All Nodes",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        LAYOUT_ALL,
        ext_instance.layout_all,
        display_name="Layout All",
        description="Layout All Graph Nodes",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        EXPAND_ALL,
        lambda: ext_instance.set_expansion("open"),
        display_name="Expand All",
        description="Expand All Graph Nodes",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        MINIMIZE_ALL,
        lambda: ext_instance.set_expansion("minimize"),
        display_name="Minimize All",
        description="Minimize All Graph Nodes",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        CLOSE_ALL,
        lambda: ext_instance.set_expansion("close"),
        display_name="Close All",
        description="Close All Graph Nodes",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        COPY_NODES,
        ext_instance.graph_copy,
        display_name="Graph Copy",
        description="Copy nodes to the clipboard.",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        PASTE_NODES,
        ext_instance.graph_paste,
        display_name="Graph Paste",
        description="Paste nodes from the clipboard.",
        tag=actions_tag,
    )

    app = omni.kit.app.acquire_app_interface()
    if float(app.get_kit_version_short()) >= 105:
        action_registry.register_action(
            extension_id,
            MATERIAL_UNPAUSE_AND_PAUSE,
            ext_instance.material_unpause_and_pause,
            display_name="Material unpause and pause",
            description="Unpause material, allow it to compile and then pause.",
            tag=actions_tag,
        )

        action_registry.register_action(
            extension_id,
            TOGGLE_MATERIAL_COMPILATION,
            ext_instance.toggle_material_compilation,
            display_name="Toggle material compilation",
            description="Toggle the material compilation lock state.",
            tag=actions_tag,
        )


def deregister_actions(extension_id):
    action_registry = omni.kit.actions.core.get_action_registry()
    action_registry.deregister_all_actions_for_extension(extension_id)
