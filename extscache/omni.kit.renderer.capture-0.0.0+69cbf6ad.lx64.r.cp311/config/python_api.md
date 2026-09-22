# Public API for module omni.kit.renderer.capture:

## Classes

- class IRendererCapture
  - def capture_next_frame_rp_resource(self, filepath: str, resource: omni.gpu_foundation_factory._gpu_foundation_factory.RpResource, app_window: omni.appwindow._appwindow.IAppWindow = None, metadata: Metadata = None)
  - def capture_next_frame_rp_resource_callback(self, callback: typing.Callable[[capsule, int, int, int, omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat], None], resource: omni.gpu_foundation_factory._gpu_foundation_factory.RpResource, app_window: omni.appwindow._appwindow.IAppWindow = None, metadata: Metadata = None)
  - def capture_next_frame_rp_resource_list_callback(self, callback: typing.Callable[[typing.List[int], int, int, int, omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat], None], resource: omni.gpu_foundation_factory._gpu_foundation_factory.RpResource, app_window: omni.appwindow._appwindow.IAppWindow = None, metadata: Metadata = None)
  - def capture_next_frame_rp_resource_to_file(self, filepath: str, resource: omni.gpu_foundation_factory._gpu_foundation_factory.RpResource, app_window: omni.appwindow._appwindow.IAppWindow = None, format_desc: object = None, metadata: Metadata = None)
  - def capture_next_frame_swapchain(self, filepath: str, app_window: omni.appwindow._appwindow.IAppWindow = None, metadata: Metadata = None)
  - def capture_next_frame_swapchain_callback(self, callback: typing.Callable[[capsule, int, int, int, omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat], None], app_window: omni.appwindow._appwindow.IAppWindow = None, metadata: Metadata = None)
  - def capture_next_frame_swapchain_to_file(self, filepath: str, app_window: omni.appwindow._appwindow.IAppWindow = None, format_desc: object = None, metadata: Metadata = None)
  - def capture_next_frame_texture(self, filepath: str, texture: omni.gpu_foundation_factory._gpu_foundation_factory.Texture = None, app_window: omni.appwindow._appwindow.IAppWindow = None, metadata: Metadata = None)
  - def capture_next_frame_texture_callback(self, callback: typing.Callable[[capsule, int, int, int, omni.gpu_foundation_factory._gpu_foundation_factory.TextureFormat], None], texture: omni.gpu_foundation_factory._gpu_foundation_factory.Texture = None, app_window: omni.appwindow._appwindow.IAppWindow = None, metadata: Metadata = None)
  - def capture_next_frame_texture_to_file(self, filepath: str, texture: omni.gpu_foundation_factory._gpu_foundation_factory.Texture = None, app_window: omni.appwindow._appwindow.IAppWindow = None, format_desc: object = None, metadata: Metadata = None)
  - def capture_next_frame_using_render_product(self, viewport_handle: int, filepath: str, render_product: str)
  - def request_callback_memory_ownership(self) -> bool
  - def set_capture_sync(self, sync: bool, app_window: omni.appwindow._appwindow.IAppWindow = None) -> bool
  - def shutdown(self) -> bool
  - def start_frame_updates(self, app_window: omni.appwindow._appwindow.IAppWindow = None) -> bool
  - def startup(self) -> bool
  - def wait_async_capture(self, app_window: omni.appwindow._appwindow.IAppWindow = None)

## Functions

- def acquire_renderer_capture_interface(*args, **kwargs) -> typing.Any
