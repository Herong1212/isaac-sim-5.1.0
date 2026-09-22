# Public API for module omni.kit.window.extensions:

## Classes

- class ToggleExtension(omni.kit.commands.Command)
  - def __init__(self, ext_id: str, enable: bool)
  - def do(self)

- class ExtsWindowExtension(omni.ext.IExt, MenuHelperExtension)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - def show_window(self, value)
  - class def refresh_extension_info_widget(cls)
  - class def add_tab_to_info_widget(cls, tab: ext_info_widget.PageBase)
  - class def remove_tab_from_info_widget(cls, tab: ext_info_widget.PageBase)
  - class def refresh_menu_items(cls)
  - class def add_menu_to_info_widget(cls, tab: ext_info_widget.PageBase)
  - class def remove_menu_from_info_widget(cls, tab: ext_info_widget.PageBase)
  - class def refresh_search_items(cls)
  - class def add_searchable_keyword(cls, keyword: str, description: str, filter_on_keyword: Callable, clear_cache: Callable)
  - class def remove_searchable_keyword(cls, keyword_to_remove: str)

- class SimpleCheckBox
  - def __init__(self, checked: bool, on_checked_fn: Callable, text: str = None, model = None, enabled = True)

- class PageBase
  - def build_tab(self, ext_info: dict, ext_item: ExtensionCommonInfo)
  - def destroy(self)
  - static def get_tab_name() -> str
  - def sort_index(self)

- class ExtInfoWidget
  - pages: List
  - current_page: int
  - def __init__(self)
  - def update_tabs(self)
  - def set_visible(self, visible)
  - def select_ext(self, ext_summary)
  - def set_show_dependencies_fn(self, fn: Callable)
  - def destroy(self)

- class ExtSource(Enum)
  - NVIDIA: int
  - THIRD_PARTY: int
  - def get_ui_name(self)

- class ExtsListWidget
  - menus: List
  - menu_style: Dict
  - searches: Unknown
  - def __init__(self)
  - class def build_menu_header(cls, title, clicked_fn)
  - def build(self)
  - def set_show_dependencies_fn(self, fn: Callable)
  - def set_ext_selected_fn(self, fn: Callable)
  - def select_extension_by_name(self, name: str)
  - def set_show_properties_fn(self, fn: Callable)
  - def rebuild_filter_menu(self)
  - def close_filter_menu(self)
  - def destroy(self)
  - def get_model(self)

## Functions

- def get_instance() -> weakref.ReferenceType[ExtsWindowExtension]
- def ext_id_to_fullname(ext_id: str) -> str
- def open_in_vscode_if_enabled(path: str, prefer_vscode: bool = True)
- async def show_ok_popup(title, message, **dialog_kwargs)
- async def show_user_input_popup(title, label, default)
- def get_open_example_links()
- async def _ask_user_for_path(is_export: bool, apply_button_label = 'Choose', title = None)
- def toggle_autoload(ext_id: str, toggle: bool)
