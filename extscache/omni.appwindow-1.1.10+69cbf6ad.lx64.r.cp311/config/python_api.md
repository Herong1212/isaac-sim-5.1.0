# Public API for module omni.appwindow:

## Classes

- class IAppWindow
  - def broadcast_input_blocking_state(self, should_block: bool)
  - def focus(self)
  - def get_action_mapping_set_path(self) -> str
  - def get_clipboard(self) -> str
  - def get_cursor_blink(self) -> bool
  - def get_dpi_scale(self) -> float
  - def get_dpi_scale_override(self) -> float
  - static def get_gamepad(*args, **kwargs) -> typing.Any
  - def get_height(self) -> int
  - static def get_input_blocking_state(*args, **kwargs) -> typing.Any
  - static def get_keyboard(*args, **kwargs) -> typing.Any
  - static def get_mouse(*args, **kwargs) -> typing.Any
  - def get_position(self) -> carb._carb.Int2
  - def get_size(self) -> carb._carb.Uint2
  - def get_title(self) -> str
  - def get_ui_scale(self) -> float
  - def get_width(self) -> int
  - static def get_window(*args, **kwargs) -> typing.Any
  - def get_window_close_event_stream(self) -> carb.events._events.IEventStream
  - def get_window_content_scale_event_stream(self) -> carb.events._events.IEventStream
  - def get_window_drop_event_stream(self) -> carb.events._events.IEventStream
  - def get_window_focus_event_stream(self) -> carb.events._events.IEventStream
  - def get_window_minimize_event_stream(self) -> carb.events._events.IEventStream
  - def get_window_move_event_stream(self) -> carb.events._events.IEventStream
  - def get_window_resize_event_stream(self) -> carb.events._events.IEventStream
  - def is_focused(self) -> bool
  - def is_fullscreen(self) -> bool
  - def is_maximized(self) -> bool
  - def maximize_window(self)
  - def move(self, x: int, y: int)
  - def resize(self, width: int, height: int)
  - def restore_window(self)
  - def set_clipboard(self, text: str)
  - def set_dpi_scale_override(self, dpi_scale_override: float)
  - def set_fullscreen(self, fullscreen: bool)
  - static def set_input_blocking_state(*args, **kwargs) -> typing.Any
  - def shutdown(self) -> bool
  - def startup(self, name: str = '') -> bool
  - def startup_with_desc(self, title: str, width: int, height: int, x: int = 18446744073709551614, y: int = 18446744073709551614, decorations: bool = True, resize: bool = True, always_on_top: bool = False, scale_to_monitor: bool = True, dpi_scale_override: float = -1.0, cursor_blink: bool = True)
  - def update(self, dt: float)
  - [property] def ui_scale_multiplier(self) -> float
  - [ui_scale_multiplier.setter] def ui_scale_multiplier(self, arg1: float)

- class IAppWindowFactory
  - def create_window_by_type(self, window_type: WindowType) -> IAppWindow
  - def create_window_from_settings(self) -> IAppWindow
  - def create_window_ptr_by_type(self, window_type: WindowType) -> IAppWindow
  - def create_window_ptr_from_settings(self) -> IAppWindow
  - def destroy_window_ptr(self, app_window: IAppWindow)
  - def get_app_window(self) -> IAppWindow
  - def get_default_window(self) -> IAppWindow
  - def get_window_at(self, index: int) -> IAppWindow
  - def get_window_count(self) -> int
  - def get_windows(self) -> tuple
  - def set_default_window(self, Arg0: IAppWindow)

- class WindowType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - OS: omni.appwindow._appwindow.WindowType
  - VIRTUAL: omni.appwindow._appwindow.WindowType

## Functions

- def acquire_app_window_factory_interface(*args, **kwargs) -> typing.Any
- def get_default_app_window(*args, **kwargs) -> typing.Any

## Variables

- POSITION_CENTERED: int
- POSITION_UNSET: int
