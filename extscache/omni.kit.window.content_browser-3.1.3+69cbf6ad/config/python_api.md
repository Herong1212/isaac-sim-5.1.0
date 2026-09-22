# Public API for module omni.kit.window.content_browser:

## Classes

- class ContentBrowserExtension(omni.ext.IExt)
  - WINDOW_NAME: str
  - MENU_GROUP: str
  - def __init__(self)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

- class ContentBrowser(MenuHelperExtension)
  - def __init__(self, ext_id)
  - [property] def window(self) -> ui.Window
  - [window.setter] def window(self, window: ui.Window)
  - def show_window(self, menu, value)
  - [property] def api(self) -> ContentBrowserAPI
  - def add_connections(self, connections: dict)
  - def set_current_directory(self, path: str)
  - def get_current_directory(self) -> str
  - def get_current_selections(self, pane: int = 2) -> List[str]
  - def subscribe_selection_changed(self, fn: Callable)
  - def unsubscribe_selection_changed(self, fn: Callable)
  - def navigate_to(self, url: str)
  - async def navigate_to_async(self, url: str)
  - async def select_items_async(self, url: str, filenames: List[str] = []) -> List[FileBrowserItem]
  - def add_context_menu(self, name: str, glyph: str, click_fn: Callable, show_fn: Callable, index: int = 0, separator_name = '_add_on_end_separator_') -> str
  - def delete_context_menu(self, name: str)
  - def add_listview_menu(self, name: str, glyph: str, click_fn: Callable, show_fn: Callable, index: int = -1) -> str
  - def delete_listview_menu(self, name: str)
  - def add_import_menu(self, name: str, glyph: str, click_fn: Callable, show_fn: Callable) -> str
  - def delete_import_menu(self, name: str)
  - def add_file_open_handler(self, name: str, open_fn: Callable, file_type: Union[int, Callable]) -> str
  - def delete_file_open_handler(self, name: str)
  - def get_file_open_handler(self, url: str) -> Callable
  - def set_search_delegate(self, delegate: SearchDelegate)
  - def unset_search_delegate(self, delegate: SearchDelegate)
  - def decorate_from_registry(self, event: carb.events.IEvent | carb.eventdispatcher.Event)
  - def show_model(self, model: FileBrowserModel)
  - def toggle_grid_view(self, show_grid_view: bool)
  - def toggle_bookmark_from_path(self, name: str, path: str, is_bookmark: bool, is_folder: bool = True) -> bool
  - def refresh_current_directory(self)
  - def get_checkpoint_widget(self) -> CheckpointWidget
  - def get_timestamp_widget(self) -> TimestampWidget
  - def add_checkpoint_menu(self, name: str, glyph: str, click_fn: Callable, show_fn: Callable, index = -1) -> str
  - def delete_checkpoint_menu(self, name: str)
  - def add_collection_data(self, collection_data: CollectionData)
  - def remove_collection_data(self, collection_id: str)

- class ContentBrowserWidget(FilePickerWidget)
  - def __init__(self, **kwargs)
  - def destroy(self)

## Functions

- def get_content_window() -> ContentBrowser
