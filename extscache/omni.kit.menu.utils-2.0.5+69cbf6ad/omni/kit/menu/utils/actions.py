"""Actions Omniverse Kit API (deprecated)

Module to work with **Actions** in the Kit. It is built on top of ``carb.input`` system that features action mapping logic.

this is deprecated as its old get_editor_menu().add_action_to_menu(..) and nothing todo with omni.kit.actions
"""

from typing import Callable, Tuple


class ActionMenuSubscription:  # pragma: no cover
    """
    Action menu subscription wrapper to make it scoped (auto unsubscribe on del) (deprecated)
    """

    def __init__(self, _on_del: Callable):
        self._on_del = _on_del
        self._mapped = True

    def unsubscribe(self):
        if self._mapped:
            self._mapped = False
            self._on_del()

    def __del__(self):
        self.unsubscribe()


def add_action_to_menu(
    menu_path: str,
    on_action: Callable,
    action_name: str = None,
    default_hotkey: Tuple[int, int] = None,
    on_rmb_click: Callable = None,
) -> ActionMenuSubscription:  # pragma: no cover
    """
    Add action to menu path. (deprecated)

    This function binds passed callable `on_action` function with :mod:`carb.input` action and a menu path together. If
    `default_hotkey` is provided it is set into settings and appears on the menu.

    Args:
        menu_path: menu path. E.g. "File/Open".
        on_action: function to be called as an action.
        on_rmb_click: function to be called when right mouse button clicked.
        action_name: action name. If not provided menu path is used as action, where all '/' are replaced with '-'.
        default_hotkey(tuple(int, :class:`carb.input.KeyboardInput`)): modifier and key tuple to associate with given action.

    Returns:
        Subscription holder object. Action is removed when this object is destroyed.
    """
    import carb
    import omni.kit.ui

    carb.log_warn("add_action_to_menu: add_action_to_menu & omni.kit.ui.get_editor_menu are deprecated")

    return omni.kit.ui.get_editor_menu().add_action_to_menu(
        menu_path, on_action, action_name, default_hotkey, on_rmb_click
    )

    # this code is broken and not used.
    def unsubsribe():  # pylint: disable=unreachable
        # input.unsubscribe_to_action_events(sub_id)
        menu = omni.kit.ui.get_editor_menu()
        if menu:
            action_mapping_set_path = omni.appwindow.get_default_app_window().get_action_mapping_set_path()
            menu.set_action(menu_path, action_mapping_set_path, "")

    return ActionMenuSubscription(unsubsribe)
