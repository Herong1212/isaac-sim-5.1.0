# ui_test like routines specifically for omni.graph
import re

import omni.ui as ui
from omni.kit import ui_test

MENU_MAX_WAIT = 100


# ----------------------------------------------------------------------------------------------
async def get_current_context_menu() -> ui.Menu | None:
    """Returns the currently displayed context menu or None if one is not visible."""
    menu_root = None
    for _ in range(MENU_MAX_WAIT):
        menu_root = ui.Menu.get_current()
        if menu_root:
            break
        await ui_test.wait_n_updates(1)
    if not menu_root:
        raise Exception("Can't find context menu, wait time exceeded.")
    for _ in range(MENU_MAX_WAIT):
        if menu_root.shown:
            break
        await ui_test.wait_n_updates(1)
    if not menu_root.shown:
        raise Exception("Context menu is not visible, wait time exceeded.")
    return menu_root


# ----------------------------------------------------------------------------------------------
def _find_context_menu_item(query, menu_root):
    def find_menu_item(query, menu_root):
        menu_items = ui.Inspector.get_children(menu_root)
        for menu_item in menu_items:
            if isinstance(menu_item, (ui.MenuItem, ui.Menu)):
                name = re.sub(r"[^\x00-\x7F]+", " ", menu_item.text).lstrip()
                if query == name:
                    return menu_item
        return None

    tokens = query.split("/")
    child = menu_root
    for token in tokens:
        child = find_menu_item(token, child)
        if not child:
            break
    return child


# ----------------------------------------------------------------------------------------------
async def run_menu_item(menu_root: ui.Menu, menu_item_name: str):
    """Runs the menu item with the given name from the given menu."""
    menu_item = _find_context_menu_item(menu_item_name, menu_root)
    if not menu_item:
        raise Exception(f"Can't find menu item '{menu_item_name}'")
    if not menu_item.enabled:
        raise Exception(f"Menu item '{menu_item_name}' is disabled")
    menu_item.call_triggered_fn()
    menu_root.hide()
