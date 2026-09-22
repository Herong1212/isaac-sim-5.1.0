# Public API for module omni.kit.widget.versioning:

## Classes

- class CheckpointWidget
  - def __init__(self, url: str = '', show_none_entry = False, **kwargs)
  - def destroy(self)
  - def set_mouse_pressed_fn(self, mouse_pressed_fn: Callable)
  - def set_mouse_double_clicked_fn(self, mouse_double_clicked_fn: Callable)
  - def set_multi_select(self, state: bool)
  - def set_url(self, url: str)
  - def set_search(self, keywords)
  - def add_on_selection_changed_fn(self, fn)
  - def set_on_list_checkpoint_fn(self, fn)
  - def empty(self)
  - static def create_checkpoint_widget() -> CheckpointWidget
  - static def on_model_url_changed(widget: CheckpointWidget, urls: List[str])
  - static def delete_checkpoint_widget(widget: CheckpointWidget)
  - def add_context_menu(self, name: str, glyph: str, click_fn: Callable, enable_fn: Callable, index: int = -1) -> str
  - def delete_context_menu(self, name: str)

- class CheckpointModel(ui.AbstractItemModel)
  - def __init__(self, show_none_entry)
  - def reset(self)
  - def destroy(self)
  - [property] def single_column(self)
  - [single_column.setter] def single_column(self, value: bool)
  - def empty(self)
  - def set_multi_select(self, state: bool)
  - def set_url(self, url)
  - def get_url(self)
  - def set_search(self, keywords)
  - def set_on_list_checkpoint_fn(self, fn)
  - def on_list_checkpoints(self, file_entry, checkpoints_entries)
  - def get_item_children(self, item)
  - def get_item_value_model_count(self, item)
  - def list_checkpoint(self)
  - def restore_checkpoint(self, file_path, checkpoint_path)
  - def get_drag_mime_data(self, item)

- class CheckpointItem(ui.AbstractItem)
  - def __init__(self, entry, url)
  - [property] def comment(self)
  - def get_full_url(self)
  - def get_relative_path(self)
  - static def size_to_string(size: int)
  - static def datetime_to_string(dt: datetime)

- class CheckpointCombobox
  - def __init__(self, absolute_asset_path, on_selection_changed_fn, width: ui.Length = ui.Pixel(100), has_pre_spacer: bool = True, popup_width: int = 450, visible: bool = True, modal: bool = False)
  - def destroy(self)
  - [property] def visible(self) -> bool
  - [visible.setter] def visible(self, value: bool)
  - [property] def url(self) -> str
  - [url.setter] def url(self, value: str)

- class CheckpointHelper
  - server_cache: Dict
  - static def extract_server_from_url(url: str) -> str
  - static async def is_checkpoint_enabled_async(url: str) -> bool
  - static def is_checkpoint_enabled_with_callback(url: str, callback: Callable)

## Variables

- LAYOUT_SLIM_VIEW: int
- LAYOUT_TABLE_VIEW: int
- LAYOUT_DEFAULT: int
