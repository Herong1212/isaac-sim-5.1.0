# Public API for module omni.kit.window.content_browser_registry:

## Functions

- def get_instance()
- def custom_menus() -> OrderedDict
- def selection_handlers() -> Set
- def search_delegate() -> SearchDelegate
- def register_context_menu(name: str, glyph: str, click_fn: Callable, show_fn: Callable, index: int = -1)
- def deregister_context_menu(name: str)
- def register_listview_menu(name: str, glyph: str, click_fn: Callable, show_fn: Callable, index: int = -1)
- def deregister_listview_menu(name: str)
- def register_import_menu(name: str, glyph: str, click_fn: Callable, show_fn: Callable)
- def deregister_import_menu(name: str)
- def register_file_open_handler(name: str, open_fn: Callable, file_type: Union[int, Callable])
- def deregister_file_open_handler(name: str)
- def register_selection_handler(handler: Callable)
- def deregister_selection_handler(handler: Callable)
- def register_search_delegate(search_delegate: SearchDelegate)
- def deregister_search_delegate(search_delegate: SearchDelegate)
- def register_checkpoint_menu(name: str, glyph: str, click_fn: Callable, show_fn: Callable, index = -1)
- def deregister_checkpoint_menu(name: str)
