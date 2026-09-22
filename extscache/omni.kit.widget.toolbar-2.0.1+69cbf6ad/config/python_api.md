# Public API for module omni.kit.widget.toolbar:

## Classes

- class Toolbar
  - WINDOW_NAME: str
  - DEFAULT_CONTEXT: str
  - DEFAULT_CONTEXT_TOKEN: int
  - DEFAULT_SIZE: int
  - def __init__(self)
  - [property] def context_menu(self)
  - def destroy(self)
  - def add_widget(self, widget_group: WidgetGroup, priority: int, context: str = '')
  - def remove_widget(self, widget_group: WidgetGroup)
  - def get_widget(self, name: str) -> ui.Widget
  - def acquire_toolbar_context(self, context: str)
  - def release_toolbar_context(self, token: int)
  - def get_context(self)
  - def set_axis(self, axis: ui.ToolBarAxis)
  - def rebuild_toolbar(self, root_frame = None)
  - def subscribe_grab_mouse_pressed(self, function: Callable[[int, 'weakref.ref'], None])
  - def add_custom_select_type(self, entry_name: str, selection_types: list)
  - def remove_custom_select(self, entry_name)
  - def add_custom_move_type(self, entry_name: str, move_type: str)
  - def remove_custom_move(self, entry_name: str)

- class SimpleToolButton(WidgetGroup)
  - def __init__(self, name, tooltip, icon_path, icon_checked_path, hotkey = None, toggled_fn = None, model = None, additional_style = None)
  - def clean(self)
  - def get_style(self)
  - def create(self, default_size)
  - def get_tool_button(self)

- class WidgetGroup
  - def __init__(self)
  - def clean(self)
  - def get_style(self) -> dict
  - def create(self, default_size) -> dict[str, ui.Widget]
  - def on_toolbar_context_changed(self, context: str)
  - def on_added(self, context)
  - def on_removed(self)

- class Hotkey
  - def __init__(self, action_name: str, hotkey: carb.input.KeyboardInput, on_action_fn: Callable[[], None], hotkey_enabled_fn: Callable[[], bool], modifiers: int = 0, on_hotkey_changed_fn: Callable[[str], None] = None)
  - def clean(self)
  - def get_as_string(self, default: str) -> str

- class ToolbarPlayButtonClickedCommand(omni.kit.commands.Command)
  - def do(self)

- class ToolbarPauseButtonClickedCommand(omni.kit.commands.Command)
  - def do(self)

- class ToolbarStopButtonClickedCommand(omni.kit.commands.Command)
  - def do(self)

- class ToolbarPlayFilterCheckedCommand(omni.kit.commands.Command)
  - def __init__(self, setting_path, enabled)
  - def do(self)
  - def undo(self)

- class ToolbarPlayFilterSelectAllCommand(omni.kit.commands.Command)
  - def __init__(self, settings)
  - def do(self)
  - def undo(self)

## Functions

- def get_instance() -> Toolbar
