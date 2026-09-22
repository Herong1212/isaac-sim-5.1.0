# Public API for module omni.kit.window.file_importer:

## Classes

- class FileImporterExtension(omni.ext.IExt)
  - def __init__(self)
  - def on_startup(self, ext_id)
  - def show_window(self, title: str = None, width: int = 1080, height: int = 450, show_only_collections: List[str] = None, show_only_folders: bool = False, file_postfix_options: List[str] = None, file_extension_types: List[Tuple[str, str]] = None, file_filter_handler: Callable[[str, str, str], bool] = None, import_button_label: str = 'Import', import_handler: Callable[[str, str, List[str]], None] = None, filename_url: str = None, file_postfix: str = None, file_extension: str = None, hide_window_on_import: bool = True, should_validate: bool = False, focus_filename_input: bool = True, allow_multi_files_selection: bool = False)
  - [property] def is_ui_ready(self) -> bool
  - [property] def is_window_visible(self) -> bool
  - def hide_window(self)
  - def add_import_options_frame(self, name: str, delegate: ImportOptionsDelegate)
  - def click_apply(self, filename_url: str = None, postfix: str = None, extension: str = None)
  - def click_cancel(self, cancel_handler: Callable[[str, str], None] = None)
  - async def select_items_async(self, url: str, filenames: List[str] = []) -> List[FileBrowserItem]
  - def detach_from_main_window(self)
  - def destroy_dialog(self)
  - def get_dialog(self)
  - def on_shutdown(self)

- class ImportOptionsDelegate
  - def __init__(self, glyph: str = None, build_fn: Callable[[], None] = None, selection_changed_fn: Callable[[List[str]], None] = None, filename_changed_fn: Callable[[str], None] = None, destroy_fn: Callable[[], None] = None, **kwargs)
  - def build_header(self, collapsed: bool, title: str)
  - def build_ui(self, frame: ui.Frame)
  - def on_selection_changed(self, selected: List[str] = [])
  - def on_filename_changed(self, filename: str)
  - def destroy(self)

## Functions

- def get_file_importer() -> FileImporterExtension
