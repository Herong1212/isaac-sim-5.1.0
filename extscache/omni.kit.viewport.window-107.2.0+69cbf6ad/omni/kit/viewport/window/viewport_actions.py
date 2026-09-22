from typing import Callable, Optional

import omni.kit.actions.core


def register_actions(extension_id: str, index: int, show_fn: Callable, visible_fn: Callable) -> Optional[str]:
    action_registry = omni.kit.actions.core.get_action_registry()
    if not action_registry:
        return None

    action_name = f"show_viewport_window_{index + 1}"
    action_registry.register_action(
        extension_id,
        action_name,
        lambda: show_fn(None, not visible_fn()),
        display_name="Viewport show/hide window",
        description="Viewport show/hide window",
        tag="Viewport Actions",
    )
    return action_name


def deregister_actions(extension_id: str, action_name: str) -> None:
    action_registry = omni.kit.actions.core.get_action_registry()
    if action_registry:
        action_registry.deregister_action(extension_id, action_name)
