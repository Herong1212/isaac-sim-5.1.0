# Public API for module omni.kit.widget.context_menu:

## Classes

- class ContextMenuWidgetExtension(omni.ext.IExt)
  - def __init__(self)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - [property] def name(self) -> str
  - def close_menu(self)
  - def separator(self, name: str = '') -> bool
  - def menu(self, name: str, delegate = None, glyph = '', submenu = False, tearable = False, **kwargs)
  - def menu_item(self, name: str, triggered_fn: Callable = None, enabled: bool = True, checkable: bool = False, checked: bool = False, is_async_func = False, delegate = None, additional_kwargs = None, glyph = '')
  - def show_context_menu(self, menu_name: str, objects: dict, menu_list: List[dict], min_menu_entries: int = 1, delegate = None)
  - def get_context_menu(self)

- class DefaultMenuDelegate(IconMenuBaseDelegate)
  - def __init__(self, **kwargs)

- class ContextMenuEventType
  - ADDED: int
  - REMOVED: int

## Functions

- def get_instance()
- def close_menu()
- def reorder_menu_dict(menu_dict: List[dict])
- def add_menu(menu_dict, index: str = 'MENU', extension_id: str = '')
- def get_menu_dict(index: str = 'MENU', extension_id: str = '') -> List[dict]
- def get_menu_event_stream()
- def merge_menus(menu_list: list) -> List[dict]
