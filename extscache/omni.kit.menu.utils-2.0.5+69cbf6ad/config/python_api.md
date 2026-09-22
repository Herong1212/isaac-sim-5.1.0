# Public API for module omni.kit.menu.utils:

## Classes

- class AppMenu
  - def __init__(self, get_instance: Optional[callable] = None, menu_bar: Optional[ui.MenuBar] = None)
  - static def sort_menu_hook(merged_menu)
  - def destroy(self)
  - def add_menu_items(self, menu: list, name: str, menu_index: int, can_rebuild_menus: bool, delegate = None) -> list
  - def replace_menu_items(self, new_menu: list, old_menu: list, name: str) -> list
  - def set_default_menu_priority(self, name: str, menu_index: int)
  - def remove_menu_items(self, menu: list, name: str, can_rebuild_menus: bool)
  - def add_layout(self, layout: List[Union[MenuLayout.Menu, MenuLayout.SubMenu, MenuLayout.Item, MenuLayout.Seperator, MenuLayout.Group]])
  - def remove_layout(self, layout: List[Union[MenuLayout.Menu, MenuLayout.SubMenu, MenuLayout.Item, MenuLayout.Seperator, MenuLayout.Group]])
  - def get_merged_menus(self)
  - def rebuild_menus(self)
  - def get_menu_layout(self)
  - def get_menu_data(self)
  - def clear_menu_data(self)
  - def build_menus_after_loading(self)
  - def add_hook(self, callback: Callable)
  - def remove_hook(self, callback: Callable)
  - def merge_menus(self, menu_keys: list, menu_defs: list, menu_order: list, delegates = None)
  - def prebuild_menu(self, menus, prefix_name, action_prefix, delegate)
  - def get_fn_result(self, menu_entry: MenuItemDescription, name: str, default: bool = True)
  - def set_right_padding(self, padding)
  - def create_menu(self)
  - def refresh_menu_items(self, name: str, action_path: str = '')

- class MenuUtilsDebugExtension(omni.ext.IExt)
  - def __init__(self)
  - def on_startup(self)
  - def on_shutdown(self)
  - def show_menu_debug_debug_window(self)

- class ActionMenuSubscription
  - def __init__(self, _on_del: Callable)
  - def unsubscribe(self)

- class IconMenuDelegate(IconMenuBaseDelegate)
  - def __init__(self, **kwargs)

- class MenuActionControl
  - NONE: str
  - NODELAY: str

- class MenuItemOrder
  - FIRST: str
  - LAST: str

- class MenuState(IntFlag)
  - Invalid: int
  - Created: int

- class LayoutSourceSearch
  - EVERYWHERE: int
  - LOCAL_ONLY: int

- class MenuAlignment
  - DEFAULT: int
  - RIGHT: int

- class MenuItemDescription
  - MAX_DEPTH: int
  - def __init__(self, name: str = '', glyph: str = '', header: Optional[str] = None, appear_after: Union[list, str] = '', enabled: bool = True, ticked: bool = False, ticked_value: Optional[bool] = None, radio_group: Optional[str] = '', sub_menu = None, hotkey: Tuple[int, int] = None, name_fn: Callable = None, show_fn: Callable = None, enable_fn: Callable = None, ticked_fn: Callable = None, onclick_action: Tuple = None, unclick_action: Tuple = None, onclick_fn: Callable = None, unclick_fn: Callable = None, onclick_right_fn: Callable = None, original_svg_color: bool = False, original_menu_item = None, user = None, hotkey_window: Optional[str] = None)
  - def add_on_delete_func(self, on_delete_fn: callable)
  - def remove_on_delete_func(self, on_delete_fn: callable)
  - def add_on_hotkey_update_func(self, hotkey_update_fn: callable)
  - def remove_on_hotkey_update_func(self, hotkey_update_fn: callable)
  - def set_hotkey(self, hotkey)
  - def get_action_mapping_desc(self)
  - def has_action(self)
  - def destroy(self, recurse: bool = True)
  - def json_enc(self)
  - def get(self, key, default_value = None)

- class PrebuiltItemOrder
  - UNORDERED: int
  - LAYOUT_ORDERED: int
  - LAYOUT_SUBMENU_SORTED: int
  - LAYOUT_ITEM_SORTED: int

- class MenuHelperExtension
  - def __init__(self)
  - def menu_startup(self, window_name, menu_desc, menu_group, appear_after = '', header = None, verbose = False) -> bool
  - def menu_shutdown(self) -> bool
  - def menu_refresh(self)

- class MenuHelperExtensionFull
  - class ArrayRedirect
    - def __init__(self, array_ptr, index)
  - def __init__(self)
  - def menu_startup(self, create_window_fn, window_name, menu_desc, menu_group, window_attr_name = None, verbose = False) -> Optional[int]
  - def menu_shutdown(self, index = -1) -> bool
  - def show_window(self, menu, value, index)

- class MenuHelperWindow(ui.Window)
  - def __init__(self, *args, **kwargs)
  - def destroy(self)
  - def set_visibility_changed_listener(self, listener)

- class MenuLayout
  - class MenuLayoutItem
    - def __init__(self, name = None, source = None, source_search = LayoutSourceSearch.EVERYWHERE)
    - def json_enc(self)
  - class Menu(MenuLayoutItem)
    - def __init__(self, name, items = None, source = None, source_search = LayoutSourceSearch.EVERYWHERE, remove = False)
  - class SubMenu(MenuLayoutItem)
    - def __init__(self, name, items = None, source = None, source_search = LayoutSourceSearch.EVERYWHERE, remove = False, glyph = None)
  - class Item(MenuLayoutItem)
    - def __init__(self, name, source = None, source_search = LayoutSourceSearch.EVERYWHERE, remove = False, duplicate = False, glyph = None)
  - class Seperator(MenuLayoutItem)
    - def __init__(self, name = None, source = None, source_search = LayoutSourceSearch.EVERYWHERE)
  - class Group(MenuLayoutItem)
    - def __init__(self, name, items = None, source = None, source_search = LayoutSourceSearch.EVERYWHERE)
  - class Sort(MenuLayoutItem)
    - def __init__(self, name = None, source = None, source_search = LayoutSourceSearch.EVERYWHERE, exclude_items = None, sort_submenus = False)
  - def __init__(self, debuglog = False)
  - def destroy(self)
  - def menus_created(self)
  - def add_layout(self, layout: List[MenuLayoutItem])
  - def remove_layout(self, layout: List[MenuLayoutItem])
  - def get_layout(self)
  - def apply_layout(self, prebuilt_menus: dict)
  - static def find_menu_item(menu_items: List, menu_items_root: List, layout_item: MenuLayoutItem, sub_menu = False, use_original_location = False)
  - static def process_layout(prebuilt_menus: dict, menu_layout: List, menu_name: str, submenu_name: str, parent_layout_offset: int, parent_layout_index: int, debuglog: bool)

- class MenuUtilsExtension(omni.ext.IExt)
  - def __init__(self)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - def add_menu_items(self, menu: list, name: str, menu_index: int, can_rebuild_menus: bool, delegate = None) -> list
  - def replace_menu_items(self, new_menu: list, old_menu: list, name: str) -> list
  - def set_default_menu_priority(self, name: str, menu_index: int)
  - def remove_menu_items(self, menu: list, name: str, can_rebuild_menus: bool)
  - def add_hook(self, callback: Callable)
  - def remove_hook(self, callback: Callable)
  - def add_layout(self, layout: List[Union[MenuLayout.Menu, MenuLayout.SubMenu, MenuLayout.Item, MenuLayout.Seperator, MenuLayout.Group]])
  - def remove_layout(self, layout: List[Union[MenuLayout.Menu, MenuLayout.SubMenu, MenuLayout.Item, MenuLayout.Seperator, MenuLayout.Group]])
  - def get_merged_menus(self)
  - def refresh_menu_items(self, name: str, immediately: bool = False)
  - def rebuild_menus(self)
  - def get_menu_layout(self)
  - def get_menu_data(self)
  - def clear_menu_data(self)
  - def get_debug_stats(self) -> dict

## Functions

- def add_action_to_menu(menu_path: str, on_action: Callable, action_name: str = None, default_hotkey: Tuple[int, int] = None, on_rmb_click: Callable = None) -> ActionMenuSubscription
- def get_action_path(action_prefix: str, menu_entry_name: str)
- def get_instance()
- def add_menu_items(menu: list, name: str, menu_index: int = 0, can_rebuild_menus: bool = True, delegate = None)
- def replace_menu_items(new_menu: list, old_menu: list, name: str)
- def remove_menu_items(menu: list, name: str, can_rebuild_menus: bool = True)
- def refresh_menu_items(name: str, immediately = None)
- def add_hook(callback: Callable)
- def remove_hook(callback: Callable)
- def rebuild_menus()
- def set_default_menu_priority(name, menu_index)
- def add_layout(layout: List[Union[MenuLayout.Menu, MenuLayout.SubMenu, MenuLayout.Item, MenuLayout.Seperator, MenuLayout.Group]])
- def remove_layout(layout: List[Union[MenuLayout.Menu, MenuLayout.SubMenu, MenuLayout.Item, MenuLayout.Seperator, MenuLayout.Group]])
- def get_menu_layout()
- def get_merged_menus() -> dict
- def get_debug_stats() -> dict
- def build_submenu_dict(menu_list: list, glyph: str = None)
