# Public API for module omni.kit.widget.filebrowser:

## Classes

- class FileBrowserWidget
  - def __init__(self, title: str, **kwargs)
  - [property] def show_udim_sequence(self)
  - [show_udim_sequence.setter] def show_udim_sequence(self, value: bool)
  - def create_treeview_model(self, name: str, drop_fn: Callable, filter_fn: Callable) -> FileBrowserModel
  - def get_root(self, pane: int = None) -> FileBrowserItem
  - def toggle_grid_view(self, show_grid_view: bool)
  - def hide_notification(self)
  - def show_notification(self)
  - [property] def show_grid_view(self)
  - def scale_grid_view(self, scale: float)
  - def create_grouping_item(self, name: str, path: str, parent: FileBrowserItem = None) -> FileBrowserItem
  - def add_model_as_subtree(self, model: FileBrowserModel, parent: FileBrowserItem = None)
  - def delete_child_by_name(self, item_name: str, parent: FileBrowserItem = None)
  - def delete_child(self, item: FileBrowserItem, parent: FileBrowserItem = None)
  - def link_views(self, src_widget: object)
  - def set_item_alert(self, item: FileBrowserItem, alert_level: int, msg: str)
  - def set_item_info(self, item: FileBrowserItem, msg: str)
  - def set_item_warning(self, item: FileBrowserItem, msg: str)
  - def set_item_error(self, item: FileBrowserItem, msg: str)
  - def clear_item_alert(self, item: FileBrowserItem)
  - def refresh_ui(self, item: FileBrowserItem = None, listview_only: bool = False)
  - def set_selections(self, selections: List[FileBrowserItem], pane: int = TREEVIEW_PANE)
  - def get_selected_item(self, pane: int = TREEVIEW_PANE) -> FileBrowserItem
  - def get_selections(self, pane: int = TREEVIEW_PANE) -> List[FileBrowserItem]
  - def select_and_center(self, selection: FileBrowserItem, pane: int = TREEVIEW_PANE)
  - def set_expanded(self, item: FileBrowserItem, expanded: bool, recursive: bool = False)
  - def show_model(self, model: FileBrowserModel)
  - def destroy(self)

- class FileBrowserItemCard(ui.Widget)
  - def __init__(self, item: FileBrowserItem, **kwargs)
  - [property] def item(self) -> FileBrowserItem
  - [property] def selected(self) -> bool
  - [selected.setter] def selected(self, value: bool)
  - def apply_cut_style(self)
  - def remove_cut_style(self)
  - def on_drag(self, thumbnail: Optional[str] = None)
  - def draw_thumbnail(self, thumbnail: str)
  - def draw_badges(self)
  - async def refresh_thumbnail_async(self, thumbnail: str)
  - def destroy(self)

- class FileBrowserModel(ui.AbstractItemModel)
  - def __init__(self, name: str = None, root_path: str = '', **kwargs)
  - [property] def show_udim_sequence(self)
  - [show_udim_sequence.setter] def show_udim_sequence(self, value: bool)
  - [property] def name(self) -> str
  - [property] def path(self) -> str
  - [property] def root(self) -> FileBrowserItem
  - [root.setter] def root(self, item: FileBrowserItem)
  - [property] def sort_by_field(self) -> str
  - [sort_by_field.setter] def sort_by_field(self, field: str)
  - [property] def sort_ascending(self) -> bool
  - [sort_ascending.setter] def sort_ascending(self, value: bool)
  - def create_root_item(self, name: str, path: str) -> Optional[FileBrowserItem]
  - def set_filter_fn(self, filter_fn: Callable[[str], bool])
  - def copy_presets(self, model: FileBrowserModel)
  - def get_item_children(self, item: FileBrowserItem) -> List[FileBrowserItem]
  - def filter_items(self, items: List[FileBrowserItem]) -> List[FileBrowserItem]
  - def get_item_value_model_count(self, item: FileBrowserItem) -> int
  - def get_item_value_model(self, item: FileBrowserItem, index: int) -> object
  - def auto_refresh_item(self, item: FileBrowserItem, throttle_frames: int = 4)
  - def sync_up_item_changes(self, item: FileBrowserItem)
  - def on_list_change_event(self, item: FileBrowserItem, result: omni.client.Result, event: omni.client.ListEvent, entry: omni.client.ListEntry, throttle_frames: int = 4)
  - [property] def single_column(self)
  - [single_column.setter] def single_column(self, value: bool)
  - [property] def builtin_column_count(self)
  - [property] def drag_mime_data(self)
  - [drag_mime_data.setter] def drag_mime_data(self, data: Union[str, List[str]])
  - def get_drag_mime_data(self, item: FileBrowserItem)
  - def drop_accepted(self, dst_item: FileBrowserItem, src_item: FileBrowserItem) -> bool
  - def drop(self, dst_item: FileBrowserItem, source: Union[str, FileBrowserItem])
  - def destroy(self)

- class FileBrowserItem(ui.AbstractItem)
  - expandable: bool
  - hideable: bool
  - def __init__(self, path: str, fields: FileBrowserItemFields, is_folder: bool = False, is_deleted: bool = False)
  - [property] def name(self) -> str
  - [property] def path(self) -> str
  - [property] def fields(self) -> FileBrowserItemFields
  - [property] def models(self) -> Tuple
  - [property] def parent(self) -> object
  - [property] def children(self) -> Dict[str, FileBrowserItem]
  - [property] def is_folder(self) -> bool
  - [property] def item_changed(self) -> bool
  - [item_changed.setter] def item_changed(self, value: bool)
  - [property] def is_deleted(self) -> bool
  - [is_deleted.setter] def is_deleted(self, value: bool)
  - [property] def populated(self) -> bool
  - [populated.setter] def populated(self, value: bool)
  - [property] def is_udim_file(self) -> bool
  - [is_udim_file.setter] def is_udim_file(self, value: bool)
  - [property] def enable_sorting(self) -> bool
  - [property] def icon(self) -> str
  - [icon.setter] def icon(self, icon: str)
  - [property] def readable(self) -> bool
  - [property] def writeable(self) -> bool
  - [property] def alert(self) -> Tuple[int, str]
  - [alert.setter] def alert(self, alert: Tuple[int, str])
  - [property] def expandable(self) -> bool
  - [property] def context_menu(self) -> Optional[BaseContextMenu]
  - [property] def hideable(self) -> bool
  - async def on_populated_async(self, result = None, children: Optional[Dict[str, FileBrowserItem]] = None, callback: Optional[Callable[[Dict[str, FileBrowserItem]], None]] = None)
  - def get_subitem_model(self, index: int) -> object
  - def populate_with_callback(self, callback: Callable, timeout: float = 10.0)
  - async def populate_async(self, callback_async: Callable = None, timeout: float = 10.0) -> Any
  - async def populate_children_async(self)
  - def on_list_change_event(self, event: omni.client.ListEvent, entry: omni.client.ListEntry) -> bool
  - def add_child(self, item: object) -> Optional[FileBrowserItem]
  - def del_child(self, item_name: str) -> Optional[FileBrowserItem]
  - async def get_custom_thumbnails_for_folder_async(self) -> Dict
  - static def size_as_string(value: int) -> str
  - static def datetime_as_string(value: datetime) -> str
  - def has_mouse_pressed_fn(self)
  - def mouse_pressed_fn(self)
  - def update_permissions(self, new_permissions: omni.client.AccessFlags)

- class FileBrowserUdimItem(FileBrowserItem)
  - def __init__(self, path: str, fields: FileBrowserItemFields, range_start: int, range_end: int, repr_frame: int = None)
  - [property] def repr_path(self) -> str
  - static def populate_udim(parent: FileBrowserItem)
  - static def get_udim_sequence(full_path: str)

- class FileBrowserItemFactory
  - static def create_group_item(name: str, path: str) -> FileBrowserItem
  - static def create_dummy_item(name: str, path: str) -> FileBrowserItem
  - static def create_udim_item(name: str, path: str, range_start: int, range_end: int, repr_frame: int)

- class FileSystemModel(FileBrowserModel)
  - def __init__(self, name: str, root_path: str = 'C:', **kwargs)

- class FileSystemItem(FileBrowserItem)
  - def __init__(self, path: str, fields: FileBrowserItemFields, is_folder: bool = False)
  - async def populate_async(self, callback_async: Callable, timeout: float = 10.0) -> Any
  - def on_list_change_event(self, event: omni.client.ListEvent, entry: omni.client.ListEntry) -> bool
  - static def keep_entry(entry: os.DirEntry) -> bool
  - [property] def readable(self) -> bool
  - [property] def writeable(self) -> bool

- class NucleusModel(FileBrowserModel)
  - def __init__(self, name: str, root_path: str, **kwargs)
  - def create_root_item(self, name: str, path: str) -> FileBrowserItem

- class NucleusItem(FileBrowserItem)
  - def __init__(self, path: str, fields: FileBrowserItemFields, is_folder: bool = True, is_deleted: bool = False)
  - async def populate_async(self, callback_async: Callable = None, timeout: float = 10.0) -> Any
  - def on_list_change_event(self, event: omni.client.ListEvent, entry: omni.client.ListEntry) -> bool
  - [property] def readable(self) -> bool
  - [property] def writeable(self) -> bool

- class NucleusConnectionItem(NucleusItem)
  - def __init__(self, path: str, fields: FileBrowserItemFields, is_folder: bool = True)
  - [property] def signed_in(self)
  - [signed_in.setter] def signed_in(self, value)

- class ColumnDelegateRegistry
  - def __init__(self)
  - def register_column_delegate(self, name: str, delegate: AbstractColumnDelegate)
  - def get_column_delegate_names(self)
  - def get_column_delegate(self, name) -> Optional[AbstractColumnDelegate]
  - def subscribe_delegate_changed(self, fn: Callable)

- class ColumnItem
  - def __init__(self, path)
  - [property] def path(self)

- class AbstractColumnDelegate
  - [property] def initial_width(self)
  - def build_header(self)
  - async def build_widget(self, item: ColumnItem)

## Functions

- async def find_thumbnails_for_files_async(urls: List[str], generate_missing: bool = True) -> Dict
- async def list_thumbnails_for_folder_async(url: str, timeout: float = 30.0, generate_missing: bool = True) -> Dict
- def save_items_to_clipboard(items: List[FileBrowserItem], is_cut: bool = False)
- def get_clipboard_items() -> List[FileBrowserItem]
- def is_clipboard_cut() -> bool
- def is_path_cut(path: str) -> bool
- def clear_clipboard()

## Variables

- FileBrowserItemFields: Unknown
- CONNECTION_ERROR_EVENT: int
- CONNECTION_ERROR_GLOBAL_EVENT: str
- MISSING_IMAGE_THUMBNAILS_EVENT: int
- MISSING_IMAGE_THUMBNAILS_GLOBAL_EVENT: str
- THUMBNAILS_GENERATED_EVENT: int
- THUMBNAILS_GENERATED_GLOBAL_EVENT: str
- ALERT_INFO: int
- ALERT_WARNING: int
- ALERT_ERROR: int
- LAYOUT_SINGLE_PANE_SLIM: int
- LAYOUT_SINGLE_PANE_WIDE: int
- LAYOUT_SPLIT_PANES: int
- LAYOUT_SINGLE_PANE_LIST: int
- LAYOUT_DEFAULT: int
- TREEVIEW_PANE: int
- LISTVIEW_PANE: int
