# Public API for module omni.kit.viewport.window:

## Classes

- class ViewportWindow(ui.Window)
  - active_window: Optional[weakref.ProxyType]
  - def __init__(self, name: str | None = None, usd_context_name: str = '', width: int = None, height: int = None, flags: int = None, style: dict = None, usd_drop_support: bool = True, hydra_engine_options: Optional[dict] = None, **ui_kw_args)
  - [property] def name(self)
  - [property] def viewport_api(self)
  - [property] def viewport_widget(self)
  - def set_style(self, style)
  - def visible(self, visible: bool)
  - def add_external_drag_drop_support(self, callback_fn: Callable = None)
  - def remove_external_drag_drop_support(self)
  - def get_frame(self, name: str) -> ui.Frame
  - def destroy(self)
  - static def set_default_style(style, overwrite: bool = False, usd_context_name: str | None = '', apply: bool = True)
  - static def get_instances(usd_context_name: str | None = '')

## Functions

- def get_viewport_window_instances(usd_context_name: str | None = '')
- def set_viewport_window_default_style(style: dict, overwrite: bool = False, usd_context_name: str | None = '', apply: bool = True)
