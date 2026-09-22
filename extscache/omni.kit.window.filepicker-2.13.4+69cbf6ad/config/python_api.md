# Public API for module omni.kit.window.filepicker:

## Classes

- class CollectionData
  - identifier: str
  - title: str
  - path_to_icon: str
  - model: FileBrowserModel
  - populate_fn: Callable[[], None]

- class FilePickerDialog
  - def __init__(self, title: str, **kwargs)
  - def set_visibility_changed_listener(self, listener: Callable[[bool], None])
  - def add_connections(self, connections: dict)
  - def set_current_directory(self, path: str)
  - def get_current_directory(self) -> str
  - def get_current_selections(self, pane: int = 2) -> List[str]
  - def set_filename(self, filename: str)
  - def get_filename(self) -> str
  - def get_file_postfix(self) -> str
  - def set_file_postfix(self, postfix: str)
  - def get_file_postfix_options(self) -> List[str]
  - def get_file_extension(self) -> str
  - def set_file_extension(self, extension: str)
  - def get_file_extension_options(self) -> List[Tuple[str, str]]
  - def set_filebar_label_name(self, name: str)
  - def get_filebar_label_name(self) -> str
  - def set_item_filter_fn(self, item_filter_fn: Callable[[str], bool])
  - def set_click_apply_handler(self, click_apply_handler: Callable[[str, str], None])
  - def navigate_to(self, path: str)
  - def toggle_bookmark_from_path(self, name: str, path: str, is_bookmark: bool, is_folder: bool = True)
  - def refresh_current_directory(self)
  - [property] def current_filter_option(self)
  - def add_detail_frame_from_controller(self, name: str, controller: DetailFrameController)
  - def delete_detail_frame(self, name: str)
  - def set_search_delegate(self, delegate)
  - def show_model(self, model: FileBrowserModel)
  - def show(self, path: str = None)
  - def hide(self)
  - def destroy(self)

- class FilePickerWidget
  - def __init__(self, title: str, **kwargs)
  - [property] def api(self) -> FilePickerAPI
  - [property] def model(self)
  - [property] def file_bar(self) -> FileBar
  - [property] def current_filter_option(self) -> int
  - def set_item_filter_fn(self, item_filter_fn: Callable[[str], bool])
  - def set_click_apply_handler(self, click_apply_handler: Callable[[str, str], None])
  - def get_selected_filename_and_directory(self) -> Tuple[str, str]
  - def destroy(self)

- class FilePickerView
  - def __init__(self, title: str, **kwargs)
  - [property] def filebrowser(self)
  - [property] def navigation_model(self) -> Optional[NavigationModel]
  - [property] def show_only_collections(self)
  - [show_only_collections.setter] def show_only_collections(self, value: List[str])
  - def destroy(self)
  - [property] def show_udim_sequence(self)
  - [show_udim_sequence.setter] def show_udim_sequence(self, value: bool)
  - [property] def notification_frame(self)
  - def register_collection_item(self, collection_item: CollectionItem) -> bool
  - def deregister_collection_item(self, collection_item: CollectionItem) -> bool
  - def add_collection(self, collection_data: CollectionData) -> FileBrowserItem
  - def add_custom_collection(self, collection_data: CollectionData) -> Optional[CollectionItem]
  - def remove_collection(self, collection_id: str)
  - [property] def collections(self)
  - def get_root(self, pane: int = None) -> FileBrowserItem
  - def all_collection_items(self, collection: str = None) -> List[FileBrowserItem]
  - def is_collection_root(self, url: str = None) -> bool
  - def has_connection_with_name(self, name: str, collection: str = None) -> bool
  - def get_connection_with_url(self, url: str) -> Optional[NucleusConnectionItem]
  - def set_item_filter_fn(self, item_filter_fn: Callable[[str], bool])
  - def set_selections(self, selections: List[FileBrowserItem], pane: int = TREEVIEW_PANE)
  - def get_selections(self, pane: int = LISTVIEW_PANE) -> List[FileBrowserItem]
  - def refresh_ui(self, item: FileBrowserItem = None)
  - def is_connection_point(self, item: FileBrowserItem) -> bool
  - def is_local_point(self, item: FileBrowserItem) -> bool
  - def is_bookmark(self, item: FileBrowserItem, path: Optional[str] = None) -> bool
  - def is_collection_node(self, item: FileBrowserItem) -> bool
  - def select_and_center(self, item: FileBrowserItem)
  - def show_model(self, model: FileBrowserModel)
  - def show_connect_dialog(self, item: Optional[AddNewItem])
  - def add_server(self, name: str, path: str, publish_event: bool = True, auto_select: bool = True) -> FileBrowserModel
  - def delete_server(self, item: FileBrowserItem, publish_event: bool = True)
  - def rename_server(self, item: FileBrowserItem, new_name: str, publish_event: bool = True)
  - def reconnect_server(self, item: FileBrowserItem)
  - def log_out_server(self, item: NucleusConnectionItem)
  - def add_bookmark(self, name: str, path: str, is_folder: bool = True, publish_event: bool = True) -> BookmarkItem
  - def delete_bookmark(self, item: BookmarkItem, publish_event: bool = True) -> bool
  - def rename_bookmark(self, item: BookmarkItem, new_name: str, new_url: str, publish_event: bool = True)
  - def mount_user_folders(self, folders: dict)
  - def toggle_grid_view(self, show_grid_view: bool)
  - [property] def show_grid_view(self)
  - def scale_grid_view(self, scale: float)
  - def show_notification(self)
  - def hide_notification(self)
  - static def is_connected(url: str) -> bool

- class FilePickerModel
  - def __init__(self, **kwargs)
  - [property] def collections(self) -> dict
  - [collections.setter] def collections(self, collections: dict)
  - def get_icon(self, item: FileBrowserItem, expanded: bool) -> str
  - def get_thumbnail(self, item: FileBrowserItem) -> str
  - def get_badges(self, item: FileBrowserItem) -> List[Tuple[str, str]]
  - def find_item_with_callback(self, url: str, callback: Callable = None)
  - async def find_item_async(self, url: str, callback: Callable = None) -> FileBrowserItem
  - async def find_item_in_subtree_async(self, root: FileBrowserItem, path: str) -> FileBrowserItem
  - static def is_local_path(path: str) -> bool
  - def sanitize_path(self, path: str) -> str
  - def destroy(self)

- class FilePickerAPI
  - def __init__(self, model: FilePickerModel = None, view: FilePickerView = None)
  - def add_connections(self, connections: dict)
  - def set_current_directory(self, path: str)
  - def get_current_directory(self) -> str
  - def get_current_selections(self, pane: int = LISTVIEW_PANE) -> List[str]
  - def set_filename(self, filename: str)
  - def get_filename(self) -> str
  - def navigate_to(self, url: str, callback: Callable = None)
  - async def navigate_to_async(self, url: str, callback: Callable = None)
  - def connect_server(self, url: str, callback: Callable = None)
  - def find_subdirs_with_callback(self, url: str, callback: Callable)
  - async def find_subdirs_async(self, url: str, callback: Callable) -> List[str]
  - async def select_items_async(self, url: str, filenames: List[str] = []) -> List[FileBrowserItem]
  - def add_context_menu(self, name: str, glyph: str, click_fn: Callable, show_fn: Callable, index: int = -1, separator_name = '_add_on_end_separator_') -> str
  - def delete_context_menu(self, name: str)
  - def add_listview_menu(self, name: str, glyph: str, click_fn: Callable, show_fn: Callable, index: int = -1) -> str
  - def delete_listview_menu(self, name: str)
  - def add_detail_frame(self, name: str, glyph: str, build_fn: Callable[[], None], selection_changed_fn: Callable[[List[str]], None] = None, filename_changed_fn: Callable[[str], None] = None, destroy_fn: Callable[[], None] = None)
  - def add_detail_frame_from_controller(self, name: str, controller: DetailFrameController)
  - def delete_detail_frame(self, name: str)
  - def set_search_delegate(self, delegate)
  - def show_model(self, model: FileBrowserModel)
  - def refresh_current_directory(self)
  - def toggle_bookmark_from_path(self, name: str, path: str, is_bookmark: bool, is_folder: bool = True)
  - def subscribe_client_bookmarks_changed(self)
  - def hide_loading_pane(self)
  - def register_collection_item(self, collection_item: CollectionItem) -> bool
  - def deregister_collection_item(self, collection_item: CollectionItem) -> bool
  - def add_collection(self, collection_data: CollectionData) -> Optional[CollectionItem]
  - def remove_collection(self, collection_id: str)
  - def add_show_only_collection(self, collection_id: str)
  - def remove_show_only_collection(self, collection_id: str)
  - def destroy(self)

- class BaseContextMenu
  - def __init__(self, title: str = None, **kwargs)
  - [property] def menu(self) -> ui.Menu
  - [property] def context(self) -> dict
  - def show(self, item: FileBrowserItem, selected: List[FileBrowserItem] = [])
  - def hide(self)
  - def add_menu_item(self, name: str, glyph: str, onclick_fn: Callable, show_fn: Callable, index: int = -1, separator_name: Optional[str] = None) -> str
  - def delete_menu_item(self, name: str)
  - def destroy(self)

- class ContextMenu(BaseContextMenu)
  - def __init__(self, **kwargs)

- class CollectionContextMenu(BaseContextMenu)
  - def __init__(self, **kwargs)

- class ConnectionContextMenu(BaseContextMenu)
  - def __init__(self, **kwargs)

- class BookmarkContextMenu(BaseContextMenu)
  - def __init__(self, **kwargs)

- class UdimContextMenu(BaseContextMenu)
  - def __init__(self, **kwargs)

- class LocalContextMenu(BaseContextMenu)
  - def __init__(self, **kwargs)

- class DetailView
  - def __init__(self, **kwargs)
  - def get_detail_frame(self, name: str) -> DetailFrameController
  - def add_detail_frame(self, name: str, glyph: str, build_fn: Callable[[], ui.Widget], selection_changed_fn: Callable[[List[str]], None] = None, filename_changed_fn: Callable[[str], None] = None, destroy_fn: Callable[[ui.Widget], None] = None)
  - def add_detail_frame_from_controller(self, name: str, detail_frame: DetailFrameController = None)
  - def delete_detail_frame(self, name: str)
  - def on_selection_changed(self, selected: List[FileBrowserItem] = [])
  - def on_filename_changed(self, filename: str = '')
  - def destroy(self)

- class DetailFrameController
  - def __init__(self, glyph: str = None, build_fn: Callable[[], None] = None, selection_changed_fn: Callable[[List[str]], None] = None, filename_changed_fn: Callable[[str], None] = None, destroy_fn: Callable[[], None] = None, **kwargs)
  - def build_header(self, collapsed: bool, title: str)
  - def build_ui(self, frame: ui.Frame)
  - def on_selection_changed(self, selected: List[str] = [])
  - def on_filename_changed(self, filename: str)
  - def destroy(self)

- class ToolBar
  - SAVED_SETTINGS_OPTIONS_MENU: str
  - def __init__(self, **kwargs)
  - [property] def config_values(self)
  - def set_config_value(self, name: str, value: bool)
  - [property] def path(self) -> str
  - def set_path(self, path: str)
  - [property] def bookmarked(self) -> bool
  - def set_bookmarked(self, true_false: bool)
  - def set_search_delegate(self, delegate)
  - def destroy(self)

- class TimestampWidget
  - def __init__(self, **kwargs)
  - def destroy(self)
  - def rebuild(self, selected: List[str])
  - static def create_timestamp_widget() -> TimestampWidget
  - static def delete_timestamp_widget(widget: TimestampWidget)
  - static def on_selection_changed(widget: TimestampWidget, selected: List[str])
  - def set_checkpoint_widget(self, widget)
  - def on_list_checkpoint(self, select)
  - def set_url(self, url: str)
  - def get_timestamp_url(self, url: str) -> str
  - def add_on_check_changed_fn(self, fn)
  - [property] def check(self) -> bool
  - [check.setter] def check(self, value: bool)

- class ConfirmItemDeletionDialog(PopupDialog)
  - def __init__(self, items: List[FileBrowserItem], title: str = 'Confirm File Deletion', message: str = 'You are about to delete', message_fn: Callable[[None], None] = None, parent: ui.Widget = None, width: int = 500, ok_handler: Callable[[PopupDialog], None] = None, cancel_handler: Callable[[PopupDialog], None] = None)
  - def destroy(self)
  - def rebuild_ui(self, message_fn: Callable[[None], None])

- class CollectionItem(FileBrowserItem)
  - def __init__(self, identifier: str, title: str, icon: str, access: int = omni.client.AccessFlags.READ | omni.client.AccessFlags.WRITE, populated: bool = True, order = 10000)
  - [property] def children(self) -> Dict[str, FileBrowserItem]
  - [property] def children_list(self) -> List[FileBrowserItem]
  - [property] def connections(self) -> List[FileBrowserItem]
  - [property] def add_new_item(self) -> Optional[AddNewItem]
  - def accept_url(self, url: str) -> bool
  - def create_add_new_item(self) -> Optional[AddNewItem]
  - def create_child_item(self, name: str, path: str, is_folder: bool = True) -> Optional[FileBrowserItem]
  - def add_path(self, name: str, path: str, is_folder: bool = True) -> Optional[FileBrowserItem]
  - def add_child(self, item: FileBrowserItem) -> Optional[FileBrowserItem]

- class AddNewItem(FileBrowserItem)
  - def __init__(self, name: str, icon: str = f'{ICON_PATH}/hdd_plus.svg')
  - def add_new(self, on_success_fn: Callable[[str, str, bool, bool], None])

## Functions

- def delete_items(items: List[FileBrowserItem], view: Optional[FilePickerView] = None)
- def move_items(dst_item: FileBrowserItem, src_paths: List[str], dst_name: Optional[str] = None, callback: Callable = None)
- def rename_item(item: FileBrowserItem, view: FilePickerView)
- def get_user_folders_dict() -> Dict[str, str]

## Variables

- UI_READY_EVENT: int
- UI_READY_GLOBAL_EVENT: str
- SETTING_PERSISTENT_SHOW_GRID_VIEW: Unknown
- SETTING_PERSISTENT_GRID_VIEW_SCALE: Unknown
