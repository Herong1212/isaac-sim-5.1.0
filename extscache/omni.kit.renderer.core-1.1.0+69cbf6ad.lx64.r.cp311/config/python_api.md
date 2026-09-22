# Public API for module omni.kit.renderer.bind:

## Classes

- class IRenderer
  - def attach_app_window(self, arg0: omni.appwindow._appwindow.IAppWindow) -> bool
  - def detach_app_window(self, arg0: omni.appwindow._appwindow.IAppWindow)
  - def draw_freeze_app_window(self, arg0: omni.appwindow._appwindow.IAppWindow, arg1: bool)
  - def force_render_frame(self, arg0: float)
  - def freeze_app_window(self, arg0: omni.appwindow._appwindow.IAppWindow, arg1: bool)
  - def get_clear_color(self, arg0: omni.appwindow._appwindow.IAppWindow) -> carb._carb.Float4
  - def get_framebuffer_height(self, arg0: omni.appwindow._appwindow.IAppWindow) -> int
  - def get_framebuffer_texture(self, arg0: omni.appwindow._appwindow.IAppWindow) -> omni.gpu_foundation_factory._gpu_foundation_factory.Texture
  - def get_framebuffer_width(self, arg0: omni.appwindow._appwindow.IAppWindow) -> int
  - static def get_graphics_command_list(*args, **kwargs) -> typing.Any
  - static def get_graphics_command_queue(*args, **kwargs) -> typing.Any
  - def get_graphics_device(self, arg0: omni.appwindow._appwindow.IAppWindow) -> omni.gpu_foundation_factory._gpu_foundation_factory.Device
  - def get_post_end_render_frame_event_stream(self, app_window: omni.appwindow._appwindow.IAppWindow = None) -> carb.events._events.IEventStream
  - def get_post_end_render_pass_event_stream(self, app_window: omni.appwindow._appwindow.IAppWindow = None) -> carb.events._events.IEventStream
  - def get_post_present_frame_buffer_event_stream(self, app_window: omni.appwindow._appwindow.IAppWindow = None) -> carb.events._events.IEventStream
  - def get_pre_begin_frame_event_stream(self, app_window: omni.appwindow._appwindow.IAppWindow = None) -> carb.events._events.IEventStream
  - def get_pre_begin_render_pass_event_stream(self, app_window: omni.appwindow._appwindow.IAppWindow = None) -> carb.events._events.IEventStream
  - def get_present_render_frame_event_stream(self, app_window: omni.appwindow._appwindow.IAppWindow = None) -> carb.events._events.IEventStream
  - def get_render_frame_event_stream(self, app_window: omni.appwindow._appwindow.IAppWindow = None) -> carb.events._events.IEventStream
  - def is_app_window_attached(self, arg0: omni.appwindow._appwindow.IAppWindow) -> bool
  - def set_clear_color(self, arg0: omni.appwindow._appwindow.IAppWindow, arg1: carb._carb.Float4)
  - def shutdown(self)
  - def startup(self)
  - def wait_idle(self, arg0: omni.appwindow._appwindow.IAppWindow)
  - [property] def clear_color(self) -> carb._carb.Float4
  - [clear_color.setter] def clear_color(self, arg1: omni.appwindow._appwindow.IAppWindow, arg2: carb._carb.Float4)

- class RendererEventType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - POST_END_RENDER_FRAME: omni.kit.renderer.bind._renderer.RendererEventType
  - POST_END_RENDER_PASS: omni.kit.renderer.bind._renderer.RendererEventType
  - POST_PRESENT_FRAME_BUFFER: omni.kit.renderer.bind._renderer.RendererEventType
  - PRESENT_RENDER_FRAME: omni.kit.renderer.bind._renderer.RendererEventType
  - PRE_BEGIN_FRAME: omni.kit.renderer.bind._renderer.RendererEventType
  - PRE_BEGIN_RENDER_PASS: omni.kit.renderer.bind._renderer.RendererEventType
  - RENDER_FRAME: omni.kit.renderer.bind._renderer.RendererEventType

## Functions

- def acquire_renderer_interface(plugin_name: str = None, library_path: str = None) -> IRenderer
- def get_renderer_event_name(event: RendererEventType, app_window: omni.appwindow._appwindow.IAppWindow = None) -> str
- def get_renderer_event_type(name: str) -> tuple
- def release_renderer_interface(arg0: IRenderer)
- def get_renderer_interface() -> IRenderer

## Other

- carb: public module
