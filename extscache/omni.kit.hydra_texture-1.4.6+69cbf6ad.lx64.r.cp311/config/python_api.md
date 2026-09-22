# Public API for module omni.kit.hydra_texture:

## Classes

- class IHydraTexture
  - def cancel_all_picking(self)
  - def get_aov_info(self, result_handle: int = 0, aov_name: str = None, include_texture: bool = False) -> typing.List[dict]
  - def get_async(self) -> bool
  - def get_camera_path(self) -> str
  - def get_drawable_resource(self, result_handle: int = 0, aov_name: str = '') -> omni.gpu_foundation_factory._gpu_foundation_factory.RpResource
  - def get_event_stream(self) -> carb.events._events.IEventStream
  - def get_frame_info(self, result_handle: int = 0, include_aov_list: bool = False) -> dict
  - def get_height(self) -> int
  - def get_hydra_engine(self) -> str
  - def get_name(self) -> str
  - def get_render_product_path(self) -> str
  - def get_settings_path(self) -> str
  - def get_updates_enabled(self) -> bool
  - def get_usd_context_name(self) -> str
  - def get_width(self) -> int
  - def pick(self, x_left: int, y_top: int, x_right: int = 0, y_bottom: int = 0, mode: omni.usd._usd.PickingMode = PickingMode.TRACK, pick_name: str = '', y_down: bool = True)
  - def query(self, x: int, y: int, callback: typing.Callable[[str, carb._carb.Double3, carb._carb.Uint2], None] = None, add_outline: bool = False, query_name: str = '', y_down: bool = True)
  - def request_pick(self, p0: carb._carb.Uint2, p1: carb._carb.Uint2, mode: omni.usd._usd.PickingMode = PickingMode.TRACK, pick_name: str = '', y_down: bool = True) -> bool
  - def request_query(self, pixel: carb._carb.Uint2, callback: typing.Callable[[str, carb._carb.Double3, carb._carb.Uint2], None] = None, query_name: str = '', add_outline: bool = False, y_down: bool = True) -> bool
  - def request_query(self, pixel: carb._carb.Uint2, callback: typing.Callable[[str, carb._carb.Double3, carb._carb.Uint2], None] = None, query_name: str = '', view: handle = None, projection: handle = None, add_outline: bool = False, y_down: bool = True) -> bool
  - def set_async(self, is_async: bool)
  - def set_camera_path(self, usd_camera_path: str = '/OmniverseKit_Persp')
  - def set_height(self, height: int)
  - def set_hydra_engine(self, hydra_engine_name: str = 'rtx')
  - def set_render_product_path(self, prim_path: str, keep_camera: bool = False, keep_resolution: bool = False) -> bool
  - def set_updates_enabled(self, updates_enabled: bool = True)
  - def set_width(self, width: int)
  - [property] def camera_path(self) -> str
  - [camera_path.setter] def camera_path(self, arg1: str)
  - [property] def height(self) -> int
  - [height.setter] def height(self, arg1: int)
  - [property] def hydra_engine(self) -> str
  - [hydra_engine.setter] def hydra_engine(self, arg1: str)
  - [property] def is_async(self) -> bool
  - [is_async.setter] def is_async(self, arg1: bool)
  - [property] def updates_enabled(self) -> bool
  - [updates_enabled.setter] def updates_enabled(self, arg1: bool)
  - [property] def width(self) -> int
  - [width.setter] def width(self, arg1: int)

## Functions

- def create_hydra_texture(name: str, width: int, height: int, usd_context_name: str = '', usd_camera_path: str = '/OmniverseKit_Persp', hydra_engine_name: str = 'rtx', is_async: bool = True, is_async_low_latency: bool = False, hydra_tick_rate: int = 0, engine_creation_flags: int = 0, device_mask: int = 0, *args, **kwargs)

## Variables

- EVENT_TYPE_DRAWABLE_CHANGED: int
- EVENT_TYPE_HYDRA_ENGINE_CHANGED: int
- EVENT_TYPE_RENDER_SETTINGS_CHANGED: int
