"""
Menu implementation class.
"""

__all__ = [
    "ActionMenuSubscription",
    "add_action_to_menu",
    "IconMenuDelegate",
    "MenuActionControl",
    "MenuItemOrder",
    "MenuState",
    "LayoutSourceSearch",
    "MenuAlignment",
    "MenuItemDescription",
    "PrebuiltItemOrder",
    "get_action_path",
    "MenuHelperExtension",
    "MenuHelperExtensionFull",
    "MenuHelperWindow",
    "MenuLayout",
    "MenuUtilsExtension",
    "get_instance",
    "add_menu_items",
    "replace_menu_items",
    "remove_menu_items",
    "refresh_menu_items",
    "add_hook",
    "remove_hook",
    "rebuild_menus",
    "set_default_menu_priority",
    "add_layout",
    "remove_layout",
    "get_menu_layout",
    "get_merged_menus",
    "get_debug_stats",
    "build_submenu_dict",
]

# pylint: disable=unused-private-member
from typing import Callable, List, Union

import carb
import carb.settings
import omni.ext
import omni.kit.app

from .actions import ActionMenuSubscription, add_action_to_menu  # noqa # pylint: disable=unused-import
from .app_menu import (  # noqa # pylint: disable=unused-import
    IconMenuDelegate,
    MenuActionControl,
    MenuItemOrder,
    MenuState,
)
from .builder_utils import (  # noqa # pylint: disable=unused-import
    LayoutSourceSearch,
    MenuAlignment,
    MenuItemDescription,
    PrebuiltItemOrder,
    get_action_path,
)
from .extension_window_helper import MenuHelperExtension  # noqa # pylint: disable=unused-import
from .extension_window_helper_full import (  # noqa # pylint: disable=unused-import
    MenuHelperExtensionFull,
    MenuHelperWindow,
)
from .layout import MenuLayout  # noqa # pylint: disable=unused-import

_extension_instance = None


class MenuUtilsExtension(omni.ext.IExt):
    """
    Menu implementation class.
    """

    def __init__(self):
        super().__init__()
        self._menu_creator = None

        # debug stats
        self._stats = {}
        self._stats["add_menu_items"] = 0
        self._stats["remove_menu_items"] = 0
        self._stats["replace_menu_items"] = 0
        self._stats["add_hook"] = 0
        self._stats["remove_hook"] = 0
        self._stats["add_layout"] = 0
        self._stats["remove_layout"] = 0
        self._stats["refresh_menu_items"] = 0
        self._stats["refresh_menu_items_skipped"] = 0
        self._stats["rebuild_menus"] = 0
        self._stats["rebuild_menus_skipped"] = 0

    def on_startup(self, ext_id):
        global _extension_instance
        _extension_instance = self

        loaded_extension_count_path = "/exts/omni.kit.menu.utils/loaded_extension_count"
        settings = carb.settings.get_settings()
        settings.set_default_int(loaded_extension_count_path, 0)
        loaded_extension_count = settings.get(loaded_extension_count_path) + 1
        settings.set(loaded_extension_count_path, loaded_extension_count)

        self._menu_creator = None
        self._stats["extension_loaded_count"] = loaded_extension_count

        from .app_menu import AppMenu

        self._menu_creator = AppMenu()

        settings = carb.settings.get_settings()
        if settings.get("/exts/omni.kit.menu.utils/forceEditorMenu") is not None:
            carb.log_error("omni.kit.menu.utils forceEditorMenu is no longer supported")

    def on_shutdown(self):
        global _extension_instance
        _extension_instance = None

        if self._menu_creator:
            self._menu_creator.destroy()
            del self._menu_creator
            self._menu_creator = None

    def add_menu_items(
        self,
        menu: list,
        name: str,
        menu_index: int,
        can_rebuild_menus: bool,
        delegate=None,
    ) -> list:
        return self._menu_creator.add_menu_items(menu, name, menu_index, can_rebuild_menus, delegate=delegate)

    def replace_menu_items(self, new_menu: list, old_menu: list, name: str) -> list:
        return self._menu_creator.replace_menu_items(new_menu, old_menu, name)

    def set_default_menu_priority(self, name: str, menu_index: int):
        self._menu_creator.set_default_menu_priority(name, menu_index)

    def remove_menu_items(self, menu: list, name: str, can_rebuild_menus: bool):
        self._menu_creator.remove_menu_items(menu, name, can_rebuild_menus)

    def add_hook(self, callback: Callable):
        self._stats["add_hook"] += 1
        if self._menu_creator:
            self._menu_creator.add_hook(callback)

    def remove_hook(self, callback: Callable):
        self._stats["remove_hook"] += 1
        try:
            if self._menu_creator:
                self._menu_creator.remove_hook(callback)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            carb.log_warn(f"omni.kit.menu.utils remove_hook failed {exc}")

    def add_layout(
        self,
        layout: List[
            Union[MenuLayout.Menu, MenuLayout.SubMenu, MenuLayout.Item, MenuLayout.Seperator, MenuLayout.Group]
        ],
    ):
        self._menu_creator.add_layout(layout)

    def remove_layout(
        self,
        layout: List[
            Union[MenuLayout.Menu, MenuLayout.SubMenu, MenuLayout.Item, MenuLayout.Seperator, MenuLayout.Group]
        ],
    ):
        self._menu_creator.remove_layout(layout)

    def get_merged_menus(self):
        return self._menu_creator.get_merged_menus()

    def refresh_menu_items(self, name: str, immediately: bool = False):
        if not self._menu_creator.ready_state & MenuState.Created:
            self._stats["refresh_menu_items_skipped"] += 1
            return

        action_path = ""
        if "/" in name:
            action_path = get_action_path(name, None)
            name = name.split("/")[0]

        self._stats["refresh_menu_items"] += 1

        self._menu_creator.refresh_menu_items(name, action_path)

    def rebuild_menus(self):
        if not self._menu_creator.ready_state & MenuState.Created:
            self._stats["rebuild_menus_skipped"] += 1
            return

        self._menu_creator.rebuild_menus()

    def get_menu_layout(self):
        return self._menu_creator.get_menu_layout()

    def get_menu_data(self):
        return self._menu_creator.get_menu_data()

    def clear_menu_data(self):
        self._menu_creator.clear_menu_data()

    def get_debug_stats(self) -> dict:
        """
        gets debug stats as dictionary, info on what functions called and how many times.
        """
        return self._stats


def get_instance():
    """
    get MenuUtilsExtension class ptr
    """
    return _extension_instance


def add_menu_items(menu: list, name: str, menu_index: int = 0, can_rebuild_menus: bool = True, delegate=None):
    """
    add a list of menus items to menu.
    menu is list of MenuItemDescription()
    name is name to appear when menu is collapsed
    menu_index is horizontal positioning
    can_rebuild_menus is flag to call rebuild_menus when True
    delegate ui.MenuDelegate delegate
    """
    instance = get_instance()
    if instance:
        return get_instance().add_menu_items(menu, name, menu_index, can_rebuild_menus, delegate)
    return None


def replace_menu_items(new_menu: list, old_menu: list, name: str):
    """
    replace a existing list of menus items to menu.
    menu is list of MenuItemDescription()
    name is name to appear when menu is collapsed
    """
    instance = get_instance()
    if instance:
        return get_instance().replace_menu_items(new_menu, old_menu, name)
    return None


def remove_menu_items(menu: list, name: str, can_rebuild_menus: bool = True):
    """
    remove  a list of menus items to menu.
    menu is list of MenuItemDescription()
    name is name to appear when menu is collapsed
    can_rebuild_menus is flag to call rebuild_menus when True
    """
    instance = get_instance()
    if instance:
        instance.remove_menu_items(menu, name, can_rebuild_menus)


def refresh_menu_items(name: str, immediately=None):
    """
    update menus enabled state
    menu is list of MenuItemDescription()
    name is name to appear when menu is collapsed
    immediately is deprecated and not used
    """
    instance = get_instance()
    if instance:
        carb.log_info(f"omni.kit.menu.utils.refresh_menu_items {name}")
        if immediately is not None:
            carb.log_warn("refresh_menu_items immediately parameter is deprecated and not used")

        instance.refresh_menu_items(name)


def add_hook(callback: Callable):
    """
    add a menu modification callback hook
    callback is function to be called when menus are re-generated
    """
    instance = get_instance()
    if instance:
        instance.add_hook(callback)


def remove_hook(callback: Callable):
    """
    remove a menu modification callback hook
    callback is function to be called when menus are re-generated
    """
    instance = get_instance()
    if instance:
        instance.remove_hook(callback)


def rebuild_menus():
    """
    force menus to rebuild, triggering hooks
    """
    instance = get_instance()
    if instance:
        carb.log_info("omni.kit.menu.utils.rebuild_menus")
        instance.rebuild_menus()


def set_default_menu_priority(name, menu_index):
    """
    set default menu priority
    """
    instance = get_instance()
    if instance:
        instance.set_default_menu_priority(name, menu_index)


def add_layout(
    layout: List[Union[MenuLayout.Menu, MenuLayout.SubMenu, MenuLayout.Item, MenuLayout.Seperator, MenuLayout.Group]],
):
    """
    add a menu layout.
    """
    instance = get_instance()
    if instance:
        instance.add_layout(layout)


def remove_layout(
    layout: List[Union[MenuLayout.Menu, MenuLayout.SubMenu, MenuLayout.Item, MenuLayout.Seperator, MenuLayout.Group]],
):
    """
    remove a menu layout.
    """
    instance = get_instance()
    if instance:
        instance.remove_layout(layout)


def get_menu_layout():
    """
    get menu layouts.
    """
    instance = get_instance()
    if instance:
        return instance.get_menu_layout().get_layout()
    return None


def get_merged_menus() -> dict:
    """
    get combined menus as dictionary
    """
    instance = get_instance()
    if instance:
        return instance.get_merged_menus()

    return None


def get_debug_stats() -> dict:
    """
    gets debug stats as dictionary, info on what functions called and how many times.
    """
    instance = get_instance()
    if instance:
        return instance.get_debug_stats()

    return None


def build_submenu_dict(menu_list: list, glyph: str = None):
    """
    builds a dictionary of List[MenuItemDescription] with sub_menus from List[MenuItemDescription] with full paths. EG: "/Window/Viewport/Viewport 1"
    """
    import copy

    def get_menu_list_from_dict(menu_dict: dict, glyph: str):
        menu_list = []
        for key in menu_dict.keys() - ["_"]:
            if menu_dict[key]["_"]:
                menu_list.append(MenuItemDescription(name=key, glyph=glyph, sub_menu=menu_dict[key]["_"]))
            menu_list.append(
                MenuItemDescription(name=key, glyph=glyph, sub_menu=get_menu_list_from_dict(menu_dict[key], None))
            )
        return menu_list

    # build dict form menu_list items
    menu_dict = {}
    for item in menu_list:
        parts = item.name.split("/")
        # remove items without groups
        if len(parts) == 1:
            carb.log_error(f'Menu item "{item}" has no group. Item removed from list.')
            continue
        group = parts[0]
        parts = parts[1:]
        if group not in menu_dict:
            menu_dict[group] = {"_": []}
        menu_leaf = menu_dict[group]

        for part in parts[:-1]:
            if part not in menu_leaf:
                menu_leaf[part] = {"_": []}
            menu_leaf = menu_leaf[part]

        new_item = copy.copy(item)
        new_item.name = parts[-1]
        menu_leaf["_"].append(new_item)

    # recursively build new list from dict & add root items
    complex_dict = {}
    for group, item in menu_dict.items():
        complex_dict[group] = get_menu_list_from_dict(item, glyph) + item["_"]
    return complex_dict
