import omni.kit.actions.core


def register_actions(extension_id, cls):
    action_registry = omni.kit.actions.core.get_action_registry()
    actions_tag = "Activity Actions"

    action_registry.register_action(
        extension_id,
        "show_activity_window",
        lambda: cls.show_progress_bar(None, not cls._is_progress_visible()),
        display_name="Activity show/hide window",
        description="Activity show/hide window",
        tag=actions_tag,
    )


def deregister_actions(extension_id):
    action_registry = omni.kit.actions.core.get_action_registry()
    action_registry.deregister_all_actions_for_extension(extension_id)
