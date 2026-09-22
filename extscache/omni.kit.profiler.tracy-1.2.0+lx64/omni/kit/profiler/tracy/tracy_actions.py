import omni.kit.actions.core
import omni.kit.profiler.tracy


def register_actions(extension_id):
    action_registry = omni.kit.actions.core.get_action_registry()
    actions_tag = "Tracy Actions"

    action_registry.register_action(
        extension_id,
        "launch_tracy",
        lambda: omni.kit.profiler.tracy.launch_tracy(),
        display_name="Tracy Launch",
        description="Launch the Tracy profiler",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "launch_tracy_and_connect",
        lambda: omni.kit.profiler.tracy.launch_tracy(connect_to_local_host=True),
        display_name="Tracy Launch And Connect",
        description="Launch the Tracy profiler and connect it to this Kit process",
        tag=actions_tag,
    )


def deregister_actions(extension_id):
    action_registry = omni.kit.actions.core.get_action_registry()
    action_registry.deregister_all_actions_for_extension(extension_id)
