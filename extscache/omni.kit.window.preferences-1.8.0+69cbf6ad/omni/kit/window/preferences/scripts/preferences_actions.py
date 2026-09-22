"""
Register/deregister actions.
"""
import omni.kit.actions.core

def register_actions(extension_id, cls, get_self_fn):
    """
    Register actions: show_preferences_window, hide_preferences_window, toggle_preferences_window.
    """

    action_registry = omni.kit.actions.core.get_action_registry()
    actions_tag = "Window Preferences Actions"

    # actions
    action_registry.register_action(
        extension_id,
        "show_preferences_window",
        get_self_fn().show_preferences_window,
        display_name="Show Preferences Window",
        description="Show Preferences Window",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "hide_preferences_window",
        get_self_fn().hide_preferences_window,
        display_name="Hide Preferences Window",
        description="Hide Preferences Window",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "toggle_preferences_window",
        get_self_fn()._toggle_preferences_window,
        display_name="Toggle Preferences Window",
        description="Toggle Preferences Window",
        tag=actions_tag,
    )


def deregister_actions(extension_id):
    """
    Deregister actions: show_preferences_window, hide_preferences_window, toggle_preferences_window.
    """
    action_registry = omni.kit.actions.core.get_action_registry()
    action_registry.deregister_all_actions_for_extension(extension_id)
