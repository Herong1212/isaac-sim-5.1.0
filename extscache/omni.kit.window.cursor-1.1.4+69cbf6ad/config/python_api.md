# Public API for module omni.kit.window.cursor:

## Classes

- class WindowCursor(omni.ext.IExt)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - def register_cursor_shape_extend(self, shape_name: str, path: str) -> bool
  - def unregister_cursor_shape_extend(self, shape_name: str) -> bool
  - def override_cursor_shape_extend(self, shape_name: str) -> bool
  - def override_cursor_shape(self, shape: windowing.CursorStandardShape) -> bool
  - def clear_overridden_cursor_shape(self) -> bool
  - def get_cursor_shape_override_extend(self) -> Optional[str]
  - def get_cursor_shape_override(self) -> Optional[windowing.CursorStandardShape]

## Functions

- def get_main_window_cursor() -> weakref.CallableProxyType
