from __future__ import annotations

import re
import logging

from omni import ui

from .input import emulate_mouse_move, emulate_mouse_click
from .common import human_delay, wait_n_updates_internal
from .vec2 import Vec2

logger = logging.getLogger(__name__)


def _find_menu_item(query, menu_root):
    menu_items = ui.Inspector.get_children(menu_root)
    for menu_item in menu_items:
        if isinstance(menu_item, ui.MenuItem) or isinstance(menu_item, ui.Menu):
            name = re.sub(r"[^\x00-\x7F]+", " ", menu_item.text).lstrip()
            if query == name:
                return menu_item
    return None


def _find_context_menu_item(query, menu_root, find_fn=_find_menu_item):
    tokens = re.split(r'(?<!/)/(?!/)', query)
    child = menu_root
    for i in range(0, len(tokens)):
        token = tokens[i].replace("//", "/")
        child = find_fn(token, child)
        if not child:
            break
    return child


async def select_context_menu(
    menu_path: str, menu_root: ui.Widget = None, offset=Vec2(100, 10), human_delay_speed: int = 4, find_fn=_find_menu_item
):
    """Emulate selection of context menu item with mouse.
     
    Supports nested menus separated by `/`:

    .. code-block:: python

        await ui_test.select_context_menu("Option/Select/All")

    This function waits for current menu for some time first. Unless `menu_root` was passed explicitly.
    When there are nested menu mouse moves to each of them and makes human delay for it to open. Then is emulates mouse
    click on final menu item.
    """
    logger.info(f"select_context_menu: {menu_path} (offset: {offset})")

    MAX_WAIT = 100

    # Find active menu
    for _ in range(MAX_WAIT):
        menu_root = menu_root or ui.Menu.get_current()
        if menu_root:
            break
        await wait_n_updates_internal(1)

    if not menu_root:
        raise Exception("Can't find context menu, wait time exceeded.")

    for _ in range(MAX_WAIT):
        if menu_root.shown:
            break
        await wait_n_updates_internal(1)

    if not menu_root.shown:
        raise Exception("Context menu is not visible, wait time exceeded.")

    sub_items = re.split(r'(?<!/)/(?!/)', menu_path)
    sub_menu_item = ""
    for item in sub_items:
        sub_menu_item = f"{sub_menu_item}/{item}" if sub_menu_item else f"{item}"
        menu_item = _find_context_menu_item(sub_menu_item, menu_root, find_fn)
        if not menu_item:
            raise Exception(f"Can't find menu item with path: '{menu_path}'. sub_menu_item: '{sub_menu_item}'")
        await emulate_mouse_move(Vec2(menu_item.screen_position_x, menu_item.screen_position_y) + offset)
    await human_delay(human_delay_speed)
    await emulate_mouse_click()
    await human_delay(human_delay_speed)


async def get_context_menu(menu_root: ui.Widget = None, get_all: bool=False):
    logger.info(f"get_context_menu: {menu_root}")

    MAX_WAIT = 100

    # Find active menu
    for _ in range(MAX_WAIT):
        menu_root = menu_root or ui.Menu.get_current()
        if menu_root:
            break
        await wait_n_updates_internal(1)

    if not menu_root:
        raise Exception("Can't find context menu, wait time exceeded.")

    for _ in range(MAX_WAIT):
        if menu_root.shown:
            break
        await wait_n_updates_internal(1)

    if not menu_root.shown:
        raise Exception("Context menu is not visible, wait time exceeded.")

    menu_dict = {}
    def list_menu(menu_root, menu_dict):
        for menu_item in ui.Inspector.get_children(menu_root):
            if not get_all and (not menu_item.enabled or not menu_item.visible):
                continue
            if isinstance(menu_item, ui.MenuItem) or isinstance(menu_item, ui.Menu) or (isinstance(menu_item, ui.Separator) and get_all):
                name = re.sub(r"[^\x00-\x7F]+", " ", menu_item.text).lstrip()
                if isinstance(menu_item, ui.Menu):
                    if not name in menu_dict:
                        menu_dict[name] = {}
                    list_menu(menu_item, menu_dict[name])
                elif menu_item.has_triggered_fn():
                    if not "_" in menu_dict:
                        menu_dict["_"] = []
                    menu_dict["_"].append(name)
                elif get_all:
                    menu_dict["_"].append(name)

    list_menu(menu_root, menu_dict)

    return menu_dict
