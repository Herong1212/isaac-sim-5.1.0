# Public API for module omni.kit.widget.live_session_management:

## Classes

- class LiveSessionUserList
  - def __init__(self, usd_context: omni.usd.UsdContext, base_layer_identifier: str, **kwargs)
  - [property] def layout(self) -> ui.HStack
  - def track_layer(self, layer_identifier)
  - def empty(self)
  - def destroy(self)

- class LiveSessionModel(LiveSessionComboBoxModel)
  - def __init__(self, layers_interface, layer_identifier, update_users = True)
  - def destroy(self)
  - def create_new_session_name(self) -> str

- class LiveSessionCameraFollowerList
  - def __init__(self, usd_context: omni.usd.UsdContext, camera_path: Sdf.Path, **kwargs)
  - [property] def layout(self) -> ui.HStack
  - def empty(self) -> bool
  - def track_camera(self, camera_path: Sdf.Path)
  - def destroy(self)

## Functions

- def stop_or_show_live_session_widget(usd_context: Union[str, omni.usd.UsdContext] = '', stop_session_only: bool = False, stop_session_forcely: bool = False, show_join_options: bool = True, layer_identifier: str = None, quick_join: str = False, prim_path: Union[str, Sdf.Path] = None)
- def build_live_session_user_layout(user_info: layers.LiveSessionUser, size = 16, tooltip = '', on_double_click_fn: Callable[[float, float, int, int, layers.LiveSessionUser], None] = None, on_mouse_click_fn: Callable[[float, float, int, int, layers.LiveSessionUser], None] = None) -> ui.ZStack
- def is_viewer_only_mode()
- def reload_outdated_layers(layer_identifiers: Union[str, List[str]], usd_context_name_or_instance: Union[str, omni.usd.UsdContext] = None)

## Variables

- VIEWER_ONLY_MODE_SETTING: str
