# Public API for module omni.kit.window.toolbar:

## Classes

- class Toolbar(omni.ext.IExt, MenuHelperExtension)
  - WINDOW_NAME: str
  - MENU_GROUP: str
  - def __init__(self)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - [property] def context_menu(self)
  - def create_main_toolbar(self)
  - def add_widget(self, widget_group: WidgetGroup, priority: int, context: str = '')
  - def remove_widget(self, widget_group: WidgetGroup)
  - def get_widget(self, name: str)
  - def acquire_toolbar_context(self, context: str)
  - def release_toolbar_context(self, token: int)
  - def get_context(self)
  - def add_custom_select_type(self, entry_name: str, selection_types: list)
  - def remove_custom_select(self, entry_name)

- class WidgetGroup
  - def __init__(self)
  - def clean(self)
  - def get_style(self) -> dict
  - def create(self, default_size) -> dict[str, ui.Widget]
  - def on_toolbar_context_changed(self, context: str)
  - def on_added(self, context)
  - def on_removed(self)

## Functions

- def get_instance()
