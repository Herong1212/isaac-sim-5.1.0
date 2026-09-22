"""
Layout implementation class. See "Layouts and & Hooks" section
"""

import copy
from typing import List

import carb
import carb.settings

from .builder_utils import (
    LayoutSourceSearch,
    MenuItemDescription,
    PrebuiltItemOrder,
    create_prebuild_entry,
    get_action_path,
)


class MenuLayout:
    """
    Layout implementation class. See "Layouts and & Hooks" section
    """

    _order_index = {}

    class MenuLayoutItem:
        def __init__(self, name=None, source=None, source_search=LayoutSourceSearch.EVERYWHERE):
            self.name = name
            self.source = source
            self.source_search = source_search

        def __repr__(self):
            if self.source:
                return f"<{self.__class__} name:{self.name} source:{self.source}>"
            return f"<{self.__class__} name:{self.name}>"

        def json_enc(self):
            sub_items = {}
            values = {f"MenuLayout.{self.__class__.__name__}": sub_items}
            for index in dir(self):
                if not index.startswith("_"):
                    item = getattr(self, index)
                    if item is not None and not callable(item):
                        sub_items[index] = item
            return values

    class Menu(MenuLayoutItem):
        def __init__(self, name, items=None, source=None, source_search=LayoutSourceSearch.EVERYWHERE, remove=False):
            super().__init__(name, source, source_search)
            self.items = items if items else []
            self.remove = remove

    class SubMenu(MenuLayoutItem):
        def __init__(
            self, name, items=None, source=None, source_search=LayoutSourceSearch.EVERYWHERE, remove=False, glyph=None
        ):
            super().__init__(name, source, source_search)
            self.items = items if items else []
            self.remove = remove
            self.glyph = glyph

    class Item(MenuLayoutItem):
        def __init__(
            self,
            name,
            source=None,
            source_search=LayoutSourceSearch.EVERYWHERE,
            remove=False,
            duplicate=False,
            glyph=None,
        ):
            super().__init__(name, source, source_search)
            self.remove = remove
            self.duplicate = duplicate
            self.glyph = glyph

        def __repr__(self):
            if self.source:
                return f"<{self.__class__} name:{self.name} source:{self.source} duplicate:{self.duplicate}>"
            return f"<{self.__class__} name:{self.name} duplicate:{self.duplicate}>"

    class Seperator(MenuLayoutItem):
        def __init__(self, name=None, source=None, source_search=LayoutSourceSearch.EVERYWHERE):
            super().__init__(name, source, source_search)

    class Group(MenuLayoutItem):
        def __init__(self, name, items=None, source=None, source_search=LayoutSourceSearch.EVERYWHERE):
            super().__init__(name, source, source_search)
            self.items = items if items else []

    class Sort(MenuLayoutItem):
        def __init__(
            self,
            name=None,
            source=None,
            source_search=LayoutSourceSearch.EVERYWHERE,
            exclude_items=None,
            sort_submenus=False,
        ):
            super().__init__(name, source)
            self.items = exclude_items if exclude_items else []
            self.sort_submenus = sort_submenus

        def __repr__(self):
            return f"<{self.__class__} items:{self.items} sort_submenus:{self.sort_submenus}>"

    def __init__(self, debuglog=False):
        self._layout_template = []
        self._menus_created = False
        self._debuglog = debuglog

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._layout_template = None

    def menus_created(self):
        self._menus_created = True

    def add_layout(self, layout: List[MenuLayoutItem]):
        self._layout_template.append(layout.copy())

    def remove_layout(self, layout: List[MenuLayoutItem]):
        self._layout_template.remove(layout)

    def get_layout(self):
        return self._layout_template

    def apply_layout(self, prebuilt_menus: dict):
        if not self._menus_created:
            return

        menu_layout_lists = self.get_layout()
        MenuLayout._order_index = {}

        for menu_layout in menu_layout_lists:
            MenuLayout.process_layout(
                prebuilt_menus,
                menu_layout,
                menu_name=None,
                submenu_name=None,
                parent_layout_offset=0,
                parent_layout_index=0,
                debuglog=self._debuglog,
            )

    # static functions to prevent self leaks
    @staticmethod
    def find_menu_item(
        menu_items: List,
        menu_items_root: List,
        layout_item: MenuLayoutItem,
        sub_menu=False,
        use_original_location=False,
    ):
        if layout_item.source:
            if "/" in layout_item.source:
                temp_src = layout_item.source
                split = temp_src.rfind("/")
                sub_prefix = temp_src[split + 1 :]
                sub_name = get_action_path(temp_src[:split], "")

                if sub_name in menu_items_root:
                    menu_subitems = menu_items_root[sub_name]["items"]
                    for item in menu_subitems:
                        # looking for submenu so ignore any items without submenu
                        if sub_menu and not item.sub_menu:
                            continue
                        if item.name == sub_prefix:
                            return item, menu_subitems, sub_name

                    if use_original_location:
                        # cannot find item at path, must of already been moved
                        for sub_name in menu_items_root.keys():
                            menu_subitems = menu_items_root[sub_name]["items"]
                            for item in menu_subitems:
                                if "original_location" in item.user:
                                    for oloc in item.user["original_location"]:
                                        if oloc == layout_item.source:
                                            duplicate_item = copy.copy(item)
                                            if duplicate_item.sub_menu:
                                                dup_index = f".{len(item.user['original_location'])}"
                                                duplicate_key = duplicate_item.sub_menu + dup_index
                                                duplicate_item.sub_menu = duplicate_key
                                                menu_items_root[duplicate_key] = copy.copy(
                                                    menu_items_root[item.sub_menu]
                                                )
                                                menu_items_root[duplicate_key]["action_prefix"] = (
                                                    menu_items_root[item.sub_menu]["action_prefix"] + dup_index
                                                )
                                                menu_items_root[duplicate_key]["items"] = []
                                                for di in menu_items_root[item.sub_menu]["items"]:
                                                    menu_items_root[duplicate_key]["items"].append(copy.copy(di))

                                            return duplicate_item, menu_subitems, sub_name

                return None, None, None

            for item in menu_items:
                if item.name == layout_item.source:
                    return item, None, None
        else:
            for item in menu_items:
                if item.name == layout_item.name:
                    return item, None, None
            if layout_item.source_search == LayoutSourceSearch.EVERYWHERE:
                # not in current menu, search them all....
                for sub_name in menu_items_root.keys():
                    menu_subitems = menu_items_root[sub_name]["items"]
                    for item in menu_subitems:
                        if item.name == layout_item.name:
                            layout_item.source = f"{sub_name}/{layout_item.name}"
                            return item, menu_subitems, sub_name
        return None, None, None

    @staticmethod
    def _get_order_index(key: str) -> int:
        if key in MenuLayout._order_index:
            MenuLayout._order_index[key] += 1
        else:
            MenuLayout._order_index[key] = 0

        return PrebuiltItemOrder.LAYOUT_ORDERED + MenuLayout._order_index[key]

    @staticmethod
    def _set_prebuilt_order(item, value):
        item.user["prebuilt_order"] = value

    @staticmethod
    def process_layout(
        prebuilt_menus: dict,
        menu_layout: List,
        menu_name: str,
        submenu_name: str,
        parent_layout_offset: int,  # legacy: not used
        parent_layout_index: int,  # legacy: not used
        debuglog: bool,
    ):
        def item_in_menu(menus, menu_name):
            return any(sub_item.name == menu_name for sub_item in menus)

        def create_menu_entry(menu_name, submenu_name):
            item = None
            action_prefix = get_action_path(menu_name, submenu_name)
            if action_prefix not in prebuilt_menus:
                if menu_name in prebuilt_menus:
                    menu_subitems = prebuilt_menus[menu_name]["items"]
                    # if item not already in submenu, add it
                    if not item_in_menu(menu_subitems, submenu_name):
                        item = MenuItemDescription(submenu_name, sub_menu=action_prefix)
                        MenuLayout._set_prebuilt_order(item, PrebuiltItemOrder.UNORDERED)
                        menu_subitems.append(item)

                create_prebuild_entry(prebuilt_menus, submenu_name, action_prefix)
                prebuilt_menus[action_prefix]["sub_menu"] = True
            return item

        def create_submenu_from_item(item, layout_item, glyph):
            layout_list = []
            new_layout = MenuLayout.SubMenu(layout_item.name, glyph=glyph)
            layout_list.append(new_layout)
            items = prebuilt_menus[item.sub_menu]["items"]
            if layout_item.duplicate and prebuilt_menus[item.sub_menu]["remapped"]:
                for remap in prebuilt_menus[item.sub_menu]["remapped"]:
                    if prebuilt_menus[remap]["items"]:
                        items = prebuilt_menus[remap]["items"]
                        break

            for sub_item in items:
                new_source = f"{layout_item.source}/{sub_item.name}"
                if not sub_item.name:
                    item = MenuLayout.Seperator(name=sub_item.header)
                else:
                    item = MenuLayout.Item(
                        name=sub_item.name, source=new_source, duplicate=layout_item.duplicate, glyph=layout_item.glyph
                    )

                new_layout.items.append(item)

            return layout_list

        for layout_item in menu_layout:
            # MenuLayout.Menu
            if isinstance(layout_item, MenuLayout.Menu):
                action_prefix = get_action_path(layout_item.name, None)
                if layout_item.remove:
                    if action_prefix in prebuilt_menus:
                        del prebuilt_menus[action_prefix]
                    elif debuglog:
                        carb.log_warn(f"Warning: Layout item {layout_item} not found in prebuilt_menus")
                else:
                    # menu doesn't exist, create one
                    if action_prefix not in prebuilt_menus:
                        carb.log_warn(
                            f'Menu {layout_item.name} not found. Create with; ("menu_index" controls menu order)'
                        )
                        carb.log_warn(
                            f'  self._menu_placeholder = omni.kit.menu.utils.add_menu_items([MenuItemDescription(name="placeholder", show_fn=lambda: False)], name="{layout_item.name}", menu_index=90)'
                        )
                        continue

                    MenuLayout.process_layout(
                        prebuilt_menus, layout_item.items, layout_item.name, submenu_name, 0, 0, debuglog
                    )

            # MenuLayout.SubMenu
            elif isinstance(layout_item, MenuLayout.SubMenu):
                if not menu_name:
                    carb.log_warn(f"Warning: Bad Layout item {layout_item}. Cannot have SubMenu without Menu as parent")

                if layout_item.remove:
                    action_prefix = get_action_path(menu_name, layout_item.name)
                    if action_prefix in prebuilt_menus:
                        del prebuilt_menus[action_prefix]
                        menu_subitems = prebuilt_menus[menu_name]["items"]
                        for item in menu_subitems:
                            if item.sub_menu == layout_item.name:
                                menu_subitems.remove(item)
                                break
                    elif debuglog:
                        carb.log_warn(f"Warning: Layout item {layout_item} not found in prebuilt_menus")
                else:
                    action_prefix = get_action_path(menu_name, None)
                    if action_prefix in prebuilt_menus:
                        menu_subitems = prebuilt_menus[action_prefix]["items"]
                        menu_subitem, source_menu, _ = MenuLayout.find_menu_item(
                            menu_subitems, prebuilt_menus, layout_item, sub_menu=True
                        )
                        if menu_subitem:
                            MenuLayout._set_prebuilt_order(menu_subitem, MenuLayout._get_order_index(menu_name))
                        else:
                            # submenu item not found, create one
                            menu_subitem = MenuItemDescription(
                                name=layout_item.name,
                                sub_menu=get_action_path(menu_name, layout_item.name),
                                glyph=layout_item.glyph,
                            )
                            menu_subitems.append(menu_subitem)
                            MenuLayout._set_prebuilt_order(menu_subitem, MenuLayout._get_order_index(menu_name))

                    if submenu_name:
                        action_prefix = get_action_path(menu_name, submenu_name)
                        MenuLayout.process_layout(
                            prebuilt_menus,
                            layout_item.items,
                            action_prefix,
                            layout_item.name,
                            0,
                            0,
                            debuglog,
                        )
                    else:
                        MenuLayout.process_layout(
                            prebuilt_menus,
                            layout_item.items,
                            menu_name,
                            layout_item.name,
                            0,
                            0,
                            debuglog,
                        )

            # MenuLayout.Item
            elif isinstance(layout_item, MenuLayout.Item):
                action_prefix = get_action_path(menu_name, submenu_name)
                new_item = create_menu_entry(menu_name, submenu_name)
                menu_subitems = prebuilt_menus[action_prefix]["items"]
                menu_subitem, source_menu, orig_root_menu = MenuLayout.find_menu_item(
                    menu_subitems, prebuilt_menus, layout_item, use_original_location=layout_item.duplicate
                )

                if orig_root_menu and action_prefix not in prebuilt_menus[orig_root_menu]["remapped"]:
                    prebuilt_menus[orig_root_menu]["remapped"].append(action_prefix)

                # new item was created, copy glyph from source item
                if new_item and orig_root_menu in prebuilt_menus and "parent" in prebuilt_menus[orig_root_menu]:
                    parent_item = prebuilt_menus[orig_root_menu]["parent"]
                    if parent_item:
                        new_item.glyph = parent_item.glyph
                        MenuLayout._set_prebuilt_order(new_item, MenuLayout._get_order_index(menu_name))

                # item is submenu, it needs to be MenuLayout.SubMenu not Item as it breaks menu refreshing
                if menu_subitem and menu_subitem.sub_menu:
                    MenuLayout.process_layout(
                        prebuilt_menus,
                        create_submenu_from_item(menu_subitem, layout_item, menu_subitem.glyph),
                        menu_name,
                        submenu_name,
                        0,
                        0,
                        debuglog,
                    )
                    MenuLayout._set_prebuilt_order(menu_subitem, MenuLayout._get_order_index(menu_name))
                elif menu_subitem:
                    # item is being moved, remove the header (ui.Separator) as can cause random extra separators
                    menu_subitem.header = None
                    # change the icon
                    if layout_item.glyph is not None:
                        menu_subitem.glyph = layout_item.glyph

                    MenuLayout._set_prebuilt_order(menu_subitem, MenuLayout._get_order_index(menu_name))

                    if "original_location" not in menu_subitem.user:
                        menu_subitem.user["original_location"] = []
                    menu_subitem.user["original_location"].append(layout_item.source)

                    if source_menu and source_menu != menu_subitems or layout_item.duplicate:
                        if layout_item.duplicate:
                            menu_subitems.append(menu_subitem)
                        else:
                            menu_subitems.append(menu_subitem)
                            source_menu.remove(menu_subitem)
                        if layout_item.source:
                            menu_subitem.name = layout_item.name
                    else:
                        if layout_item.remove:
                            menu_subitems.remove(menu_subitem)
                        elif layout_item.source:
                            menu_subitem.name = layout_item.name
                elif debuglog:
                    carb.log_warn(f"Warning: Layout not found {layout_item}")

            # MenuLayout.Seperator
            elif isinstance(layout_item, MenuLayout.Seperator):
                action_prefix = get_action_path(menu_name, submenu_name)
                if action_prefix in prebuilt_menus:
                    menu_subitems = prebuilt_menus[action_prefix]["items"]
                    item = MenuItemDescription()
                    if layout_item.name:
                        item.header = layout_item.name

                    MenuLayout._set_prebuilt_order(item, MenuLayout._get_order_index(menu_name))
                    menu_subitems.append(item)

            # MenuLayout.Group
            elif isinstance(layout_item, MenuLayout.Group):
                action_prefix = get_action_path(menu_name, submenu_name)
                create_menu_entry(menu_name, submenu_name)

                menu_subitems = prebuilt_menus[action_prefix]["items"]
                item = MenuItemDescription(header=layout_item.name)
                MenuLayout._set_prebuilt_order(item, MenuLayout._get_order_index(menu_name))

                menu_subitems.append(item)
                MenuLayout.process_layout(
                    prebuilt_menus,
                    layout_item.items,
                    menu_name,
                    submenu_name,
                    0,
                    0,
                    debuglog,
                )

                if layout_item.source:
                    menu_subitem, source_menu, _ = MenuLayout.find_menu_item(menu_subitems, prebuilt_menus, layout_item)
                    if source_menu and source_menu != menu_subitems:
                        if menu_subitem.sub_menu:
                            for item in prebuilt_menus[menu_subitem.sub_menu]["items"]:
                                MenuLayout._set_prebuilt_order(item, MenuLayout._get_order_index(menu_name))
                                menu_subitems.append(item)
                        else:
                            menu_subitems.append(menu_subitem)
                        source_menu.remove(menu_subitem)

            # MenuLayout.Sort
            elif isinstance(layout_item, MenuLayout.Sort):
                action_prefix = get_action_path(menu_name, submenu_name)
                create_menu_entry(menu_name, submenu_name)
                menu_subitems = prebuilt_menus[action_prefix]["items"]
                sort_submenus = []
                items = [i for i in menu_subitems if i.name != "" and i.name not in layout_item.items]
                for item in sorted(items, key=lambda a: a.name):
                    item_offset = (
                        PrebuiltItemOrder.LAYOUT_SUBMENU_SORTED
                        if item.sub_menu
                        else PrebuiltItemOrder.LAYOUT_ITEM_SORTED
                    )
                    MenuLayout._set_prebuilt_order(item, MenuLayout._get_order_index(menu_name))

                    if (
                        layout_item.sort_submenus
                        and item.sub_menu
                        and item.sub_menu not in layout_item.items
                        and item.sub_menu in prebuilt_menus
                    ):
                        sort_submenus.append(item.sub_menu)

                for sub_menu in sort_submenus.copy():
                    item_list = prebuilt_menus[sub_menu]["items"]
                    # separators must not move, just sort items in-between
                    groups = []
                    last_seperator = 0
                    for index, item in enumerate(item_list):
                        if item.name == "":
                            if last_seperator != index:
                                groups.append((last_seperator, index))
                            last_seperator = index
                    if last_seperator:
                        groups.append((last_seperator, len(item_list)))
                        for gstart, gend in groups:
                            items = [i for i in item_list[gstart:gend] if i.name not in layout_item.items]
                            item_offset = items[0].user["prebuilt_order"]
                            items = items[1:]
                            for index, item in enumerate(sorted(items, key=lambda a: a.name)):
                                item.user["prebuilt_order"] = item_offset + index
                                if item.sub_menu and item.sub_menu not in layout_item.items:
                                    sort_submenus.append(item.sub_menu)
                    else:
                        items = [i for i in item_list if i.name not in layout_item.items]
                        for item in sorted(items, key=lambda a: a.name):
                            item_offset = (
                                PrebuiltItemOrder.LAYOUT_SUBMENU_SORTED
                                if item.sub_menu
                                else PrebuiltItemOrder.LAYOUT_ITEM_SORTED
                            )
                            MenuLayout._set_prebuilt_order(item, MenuLayout._get_order_index(menu_name))
                            if item.sub_menu and item.sub_menu not in layout_item.items:
                                sort_submenus.append(item.sub_menu)
            elif debuglog:
                carb.log_warn(f"Warning: Unknown layout type {layout_item}")
