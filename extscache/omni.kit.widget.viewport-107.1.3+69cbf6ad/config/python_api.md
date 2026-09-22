# Public API for module omni.kit.widget.viewport:

## Classes

- class ViewportWidget
  - static def get_instances()
  - [property] def viewport_api(self)
  - [property] def name(self)
  - [property] def visible(self)
  - [visible.setter] def visible(self, value) -> bool
  - def __init__(self, usd_context_name: str = '', camera_path: Optional[str] = None, resolution: Optional[tuple] = None, hd_engine: Optional[str] = None, viewport_api: Union[ViewportAPI, str, None] = None, hydra_engine_options: Optional[dict] = None, **ui_kwargs)
  - def destroy(self)
  - [property] def usd_context_name(self) -> str
  - [property] def display_delegate(self)
  - [display_delegate.setter] def display_delegate(self, display_delegate: ViewportDisplayDelegate)
  - [property] def resolution_uses_dpi(self) -> bool
  - [property] def fill_frame(self) -> bool
  - [property] def expand_viewport(self) -> bool
  - [resolution_uses_dpi.setter] def resolution_uses_dpi(self, value: bool)
  - [fill_frame.setter] def fill_frame(self, value: bool)
  - [expand_viewport.setter] def expand_viewport(self, value: bool)
  - def set_resolution(self, resolution: Tuple[float, float])
  - [property] def resolution(self) -> Tuple[float, float]
  - [resolution.setter] def resolution(self, resolution: Tuple[float, float])
  - [property] def full_resolution(self)
