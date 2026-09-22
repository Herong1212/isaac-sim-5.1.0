# Public API for module omni.kit.window.preferences:

## Classes

- class PreferenceBuilder
  - WINDOW_NAME: str
  - def __init__(self, title)
  - def show_page(self) -> bool
  - def label(self, name: str, tooltip: str = None)
  - def create_setting_widget_combo(self, name: str, setting_path: str, list: List[str], setting_is_index: bool | None = None, **kwargs) -> ui.Widget
  - def create_setting_widget(self, label_name: str, setting_path: str, setting_type: SettingType, **kwargs) -> ui.Widget
  - def add_frame(self, name: str) -> ui.CollapsableFrame
  - def spacer(self) -> ui.Spacer
  - def get_title(self) -> str
  - def cleanup_slashes(self, path: str, is_directory: bool = False) -> str

- class PreferenceBuilderUI
  - def __init__(self, visibility_changed_fn: Callable)
  - def destroy(self)
  - def update_page_list(self, page_list: List)
  - def create_window(self)
  - def rebuild_pages(self)
  - def set_active_page(self, page_index: Union[int, str])
  - def select_page(self, page: PreferenceBuilder) -> bool
  - def show_window(self)
  - def hide_window(self)

- class PreferencesExtension(omni.ext.IExt)
  - class PreferencesState(IntFlag)
    - Invalid: int
    - Created: int
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - def rebuild_pages(self)
  - def select_page(self, page)
  - def show_preferences_window(self)
  - def hide_preferences_window(self)

- class SettingType(Enum)
  - FLOAT: int
  - INT: int
  - COLOR3: int
  - BOOL: int
  - STRING: int
  - DOUBLE3: int
  - INT2: int
  - DOUBLE2: int
  - ASSET: int

## Functions

- def register_actions(extension_id, cls, get_self_fn)
- def deregister_actions(extension_id)
- def get_instance()
- def show_preferences_window()
- def hide_preferences_window()
- def get_page_list()
- def get_shown_page_list()
- def register_page(page)
- def select_page(page)
- def rebuild_pages()
- def unregister_page(page, rebuild: bool = True)
- def show_file_importer(title: str, file_exts: list = [('All Files(*)', '')], filename_url: str = None, click_apply_fn: Callable = None, show_only_folders: bool = False)
- def restart_kit(args)

## Variables

- PERSISTENT_SETTINGS_PREFIX: str
- DEVELOPER_PREFERENCE_PATH: str
- GLOBAL_PREFERENCES_PATH: str
- RENDERING_PREFERENCES_PATH: str
