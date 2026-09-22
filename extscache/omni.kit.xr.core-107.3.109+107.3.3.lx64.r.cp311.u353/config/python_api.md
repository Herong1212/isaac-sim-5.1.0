# Public API for module omni.kit.xr.core:

## Classes

- class XRAnchorMode
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - active_camera: omni.kit.xr.core._xrcore.XRAnchorMode
  - custom_anchor: omni.kit.xr.core._xrcore.XRAnchorMode
  - scene_origin: omni.kit.xr.core._xrcore.XRAnchorMode

- class XRCoordinateSystem
  - def __init__(self, meters_per_unit: float = 0.009999999776482582, up_axis: str = 'y')
  - def get_backward_vector(self) -> object
  - def get_forward_vector(self) -> object
  - def get_left_vector(self) -> object
  - def get_right_vector(self) -> object
  - def get_up_vector(self) -> object
  - [property] def meters_per_unit(self) -> float
  - [property] def up_axis(self) -> str
  - [property] def up_axis_index(self) -> int

- class XRCoreEventType
  - static def profile_disable(arg0: object) -> int
  - static def profile_enable(arg0: object) -> int
  - static def system_disable(arg0: object) -> int
  - static def system_enable(arg0: object) -> int
  - first_launch_greeting: int
  - post_device_events_update: int
  - post_layer_update: int
  - post_sync_update: int
  - pre_sync_update: int
  - profile_changed: int
  - profile_list_updated: int
  - system_changed: int
  - system_list_updated: int
  - xr_disabled: int
  - xr_display_disabled: int
  - xr_display_enabled: int
  - xr_enabled: int
  - xr_viewport_disabled: int
  - xr_viewport_enabled: int

- class XROrientationAlignment
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - anchor: omni.kit.xr.core._xrcore.XROrientationAlignment
  - anchor_no_roll: omni.kit.xr.core._xrcore.XROrientationAlignment
  - anchor_up_right: omni.kit.xr.core._xrcore.XROrientationAlignment
  - device: omni.kit.xr.core._xrcore.XROrientationAlignment
  - device_no_roll: omni.kit.xr.core._xrcore.XROrientationAlignment
  - device_up_right: omni.kit.xr.core._xrcore.XROrientationAlignment
  - world: omni.kit.xr.core._xrcore.XROrientationAlignment

- class XRRay
  - def __init__(self, origin: object, direction: object, min_t: float = 0.0, max_t: float = inf)
  - [property] def forward(self) -> object
  - [forward.setter] def forward(self, arg1: object)
  - [property] def max_t(self) -> float
  - [max_t.setter] def max_t(self, arg1: float)
  - [property] def min_t(self) -> float
  - [min_t.setter] def min_t(self, arg1: float)
  - [property] def origin(self) -> object
  - [origin.setter] def origin(self, arg1: object)

- class XRSystem
  - def __init__(self, internal: XRSystem_Internal)
  - def get_name(self) -> str
  - def get_modes(self) -> list[str]
  - def has_mode(self, modeName: str) -> bool
  - def get_meta_data(self, key: str, default: Any) -> Any

- class XRRayQueryResult
  - def __init__(self)
  - def get_target_enclosing_model_usd_path(self) -> str
  - def get_target_usd_path(self) -> str
  - [property] def hit_position(self) -> object
  - [property] def hit_t(self) -> float
  - [property] def instance_id(self) -> int
  - [property] def normal(self) -> object
  - [property] def valid(self) -> bool

- class XRTargetInfo
  - def __init__(self, internal: XRTargetInfo_Internal)
  - [property] def valid(self) -> bool
  - [property] def position(self) -> Gf.Vec3f
  - [property] def normal(self) -> Gf.Vec3f
  - [property] def instance_id(self) -> int
  - def get_target_usd_path(self) -> Optional[str]
  - def get_target_enclosing_model_usd_path(self) -> Optional[str]

- class XRTransformType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - local: omni.kit.xr.core._xrcore.XRTransformType
  - scope: omni.kit.xr.core._xrcore.XRTransformType
  - stage: omni.kit.xr.core._xrcore.XRTransformType

- class XRToken
  - def __init__(self, name: str = '')

- class XRAssetManager
  - def __init__(self)
  - static def get_singleton() -> Optional[XRAssetManager]
  - def get_asset_package_list(self) -> Tuple[XRAssetPackageInfo]
  - def resolve_asset_path(self, asset_name: Union[str, XRToken]) -> str

- class XRAssetPackageInfo
  - def __init__(self, name: object, path: object, version: int)
  - [property] def name(self) -> XRToken
  - [property] def path(self) -> XRToken
  - [property] def version(self) -> int

- class XRCore
  - def __init__(self)
  - static def get_singleton() -> XRCore
  - def get_message_bus(self) -> carb.events.IEventStream
  - def dispatch_message_bus_and_check_consume(self, event_type, event_dict) -> bool
  - def get_profile(self, name: str) -> XRProfile
  - def ensure_profile(self, name: str) -> XRProfile
  - def get_coordinate_system(self) -> XRCoordinateSystem
  - def get_stage_coordinate_system(self) -> XRCoordinateSystem
  - def get_profile_list(self) -> list[XRProfile]
  - def get_profile_name_list(self) -> list[str]
  - def get_system(self, name: str) -> Optional[XRSystem]
  - def get_systems(self, modes: Union[list[str], str, None] = None) -> list[XRSystem]
  - def get_system_names(self, modes: Union[list[str], str, None] = None) -> list[str]
  - def is_xr_enabled(self) -> bool
  - def is_xr_display_enabled(self) -> bool
  - def is_xr_viewport_enabled(self) -> bool
  - def get_current_profile(self) -> XRProfile
  - def get_current_xr_profile(self) -> XRProfile
  - def get_current_profile_name(self) -> str
  - def get_current_xr_profile_name(self) -> str
  - def create_xr_usd_layer(self, usd_path: str, meters_per_unit: float = 0.01, up_axis: str = 'y', ui_layer_name: str = '', component_layer_name: str = '') -> XRUsdLayer
  - static def request_enable_profile(name: str)
  - def request_disable_profile(self)
  - def schedule_capture_viewport_frame(self, file_name: str, viewport_id: int = 0)
  - def schedule_capture_display_frame(self, file_name: str, display_name: Optional[str] = None, capture_source: Optional[str] = None, capture_output: Optional[str] = 'color', capture_depth_range: Tuple[float, float] = (0.1, 10.0))
  - static def show_ovxr_app_docs(page: Optional[str] = None)
  - def test_system(self, system_name: str, test_name: str)
  - def submit_raycast_query(self, ray: XRRay, callback: Callable[[XRRay, XRRayQueryResult], None])
  - def submit_multi_raycast_query(self, rays: list[XRRay], callback: Callable[[list[XRRay], list[XRRayQueryResult]], None])
  - def get_stage_anchor_prim_path(self) -> Optional[str]
  - def detach_stage_anchor(self)
  - def schedule_apply_viewport_navigation(self, dx: float, dy: float, dz: float, yaw: float, pitch: float)
  - def schedule_set_stage_anchor(self, stage_anchor: str)
  - def schedule_teleport_to_view(self, stage_anchor: str, view_pose: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]])
  - def schedule_set_space_origin(self, space_origin_pose: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]])
  - def schedule_set_camera(self, view_pose: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]])
  - def schedule_move_space_origin_relative_to_camera(self, dx: float, dy: float, dz: float)
  - def schedule_rotate_space_origin_relative_to_camera(self, yaw: float, pitch: float)
  - def get_input_device(self, handle: Union[str, XRToken]) -> Optional[XRInputDevice]
  - def has_input_device(self, handle: Union[str, XRToken]) -> bool
  - def get_input_devices(self, handle: Union[str, XRToken]) -> list[XRInputDevice]
  - def get_all_input_devices(self) -> list[XRInputDevice]
  - def get_action_map(self) -> Optional[XRActionMap]
  - def is_gui_enabled(self) -> bool
  - def is_tool_enabled(self, tool: Union[str, XRToken]) -> bool
  - def is_gui_layer_enabled(self, gui_layer: Union[str, XRToken]) -> bool
  - def bind_input_event_generator(self, event_name: str, event_list: Iterable[str], tooltips: Union[dict[str, str], str] = {}) -> Optional[XREventGenerator]
  - def unbind_input_event_generator(self, event_name: str)
  - static def check_current_renderer_supported(profile_display_name: str, notify: bool = True) -> bool
  - def set_pickable_path(self, usd_path: str, pickable: bool)
  - def unset_pickable_path(self, usd_path: str)
  - def is_fsd_enabled(self) -> bool
  - def suggest_edit_layer_for_prim(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> str
  - def check_if_prim_transform_is_usdrt_only(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> bool
  - def check_if_prim_is_on_layer(self, prim: Union[Usd.Prim, Sdf.Path, str], layer: Union[str, None, Sdf.Layer]) -> bool
  - def remove_prim_from_layer(self, prim: Union[Usd.Prim, Sdf.Path, str], layer: Union[str, None, Sdf.Layer])
  - def set_local_transform_matrix(self, prim: Union[Usd.Prim, Sdf.Path, str], matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]], layer_identifier: Union[str, None] = None)
  - def set_world_transform_matrix(self, prim: Union[Usd.Prim, Sdf.Path, str], matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]], layer_identifier: Union[str, None] = None)
  - def get_local_transform_matrix(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> Gf.Matrix4d
  - def get_world_transform_matrix(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> Gf.Matrix4d
  - def get_enclosing_model(self, usd_path: str) -> str
  - def reorient_transform_matrix_up_right(self, matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]], y_up: bool = True) -> Gf.Matrix4d
  - def reorient_transform_matrix_no_roll(self, matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]], y_up: bool = True) -> Gf.Matrix4d
  - static def on_raycast_query_result(_ray: XRRay, result: XRRayQueryResult, future: asyncio.Future)
  - async def execute_raycast_query_async(self, ray: XRRay) -> XRRayQueryResult
  - static def on_multi_raycast_query_result(_rays: List[XRRay], results: List[XRRayQueryResult], future: asyncio.Future)
  - async def execute_multi_raycast_query_async(self, rays: List[XRRay]) -> List[XRRayQueryResult]

- class XRProfile
  - def __init__(self, internal: XRProfile_Internal = None)
  - def get_name(self) -> str
  - def request_enable_profile(self)
  - def is_enabled(self) -> bool
  - def get_persistent_path(self) -> str
  - def get_non_persistent_path(self) -> str
  - def get_scene_persistent_path(self) -> str
  - def get_temp_path(self) -> str
  - def get_ar_mode(self) -> bool
  - def set_ar_mode(self, ar_mode)
  - def set_config(self, config: Any)
  - def get_config(self) -> Any
  - def teleport(self, transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]])

- class XRUsdLayer
  - def __init__(self, internal: XRUsdLayer_Internal = None)
  - def get_id(self) -> int
  - def invalidate(self)
  - def is_valid(self) -> bool
  - def get_top_level_prim_path(self) -> str
  - def get_top_level_prim(self) -> Usd.Prim
  - def get_layer_name(self) -> str
  - def get_ui_layer_name(self) -> str
  - def get_component_layer_name(self) -> str
  - def get_layer(self) -> Sdf.Layer
  - def get_ui_layer(self) -> Sdf.Layer
  - def get_component_layer(self) -> Sdf.Layer
  - def get_edit_context(self) -> Usd.EditContext
  - def get_coordinate_system(self, path: Union[Usd.Prim, Sdf.Path, str, XRToken] = '') -> XRCoordinateSystem
  - def show(self, path: Union[Usd.Prim, Sdf.Path, str, XRToken] = '')
  - def hide(self, path: Union[Usd.Prim, Sdf.Path, str, XRToken] = '')
  - def is_visible(self, path: Union[Usd.Prim, Sdf.Path, str, XRToken] = '') -> bool
  - def add_asset(self, path: Union[Sdf.Path, str, XRToken], group: str, file_path: str, layer_identifier: str = '', transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]], None] = None, transform_type: XRTransformType = XRTransformType.local, pickable: bool = False, visible: bool = True) -> str
  - def add_beam(self, path: Union[Sdf.Path, str, XRToken], group: str, material_reference: Union[Sdf.Path, str, XRToken], transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]], None] = None, transform_type: XRTransformType | int = XRTransformType.local, max_length: float = 20.0, length: float = -1.0, tube_radius: float = 0.005, visible: bool = True) -> str
  - def add_teleport_arc(self, path: Union[Sdf.Path, str, XRToken], group: str, material_reference: Union[Sdf.Path, str, XRToken], transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]], None] = None, transform_type: XRTransformType | int = XRTransformType.local, max_height: float = 3.0, tube_radius: float = 0.02, num_segments: int = 120, visible: bool = True) -> str
  - def add_transform(self, path: Union[Sdf.Path, str, XRToken], group: str, transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]], None] = None, transform_type: XRTransformType = XRTransformType.local, visible: bool = True) -> str
  - def add_reorient(self, path: Union[Sdf.Path, str, XRToken], group: str, alignment: XROrientationAlignment = XROrientationAlignment.world, input_device: Union[str, None, XRToken] = None, pose_name: Union[str, None, XRToken] = None, visible: bool = True) -> str
  - def add_link(self, path: Union[Sdf.Path, str, XRToken], group: str, link_path: Union[Sdf.Path, str, Usd.Prim, XRToken], transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]], None] = None, transform_type: XRTransformType | int = XRTransformType.local, visible: bool = True) -> str
  - def add_link_to_input_device(self, path: Union[Sdf.Path, str, XRToken], group: str, input_device_name: Union[str, XRToken], pose_name: Union[str, XRToken], transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]], None] = None, transform_type: XRTransformType | int = XRTransformType.local, visible: bool = True) -> str
  - def add_reference(self, path: Union[Sdf.Path, str, XRToken], group: str, reference_path: Union[Sdf.Path, Usd.Prim, str, XRToken], transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]], None] = None, transform_type: XRTransformType | int = XRTransformType.local, pickable: bool = False, visible: bool = True) -> str
  - def remove(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken])
  - def remove_group(self, group: str)
  - def is_managed_prim(self, path: Union[Usd.Prim, Sdf.Path, str, XRToken]) -> bool
  - def clear(self)
  - def set_transform(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]], transform_type: XRTransformType | int = XRTransformType.local, use_usd: bool = False)
  - def set_position(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], position: Union[Gf.Vec3d, Iterable[float]], transform_type: XRTransformType | int = XRTransformType.local, use_usd: bool = False)
  - def get_transform(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], transform_type: XRTransformType | int = XRTransformType.local, use_usd: bool = False) -> Gf.Matrix4d
  - def get_position(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], transform_type: XRTransformType | int = XRTransformType.local) -> Gf.Vec3d
  - def set_file_path(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], file_path: str)
  - def get_file_path(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> str
  - def get_wrapped_prim_path(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> str
  - def set_pickable(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], pickable: bool)
  - def get_pickable(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> bool
  - def get_target_info(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> XRTargetInfo
  - def set_length(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], length: float)
  - def get_length(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> float
  - def set_radius(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], radius: float)
  - def get_radius(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> float
  - def set_max_length(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], max_length: float)
  - def get_max_length(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> float
  - def get_end_prim_path(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> str
  - def get_end_prim(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> Usd.Prim
  - def get_begin_prim_path(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> str
  - def get_begin_prim(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken]) -> Usd.Prim
  - def commit_link_transform(self, path: Union[Sdf.Path, Usd.Prim, str, XRToken], layer: str = '')
  - def ensure_device_prim_path(self, input_device: Union[str, XRToken]) -> str
  - def convert_vector_from_stage_to_session(self, vec: Gf.Vec3d) -> Gf.Vec3d
  - def convert_vector_from_session_to_stage(self, vec: Gf.Vec3d) -> Gf.Vec3d
  - def convert_normal_vector_from_stage_to_session(self, vec: Gf.Vec3d) -> Gf.Vec3d
  - def convert_normal_vector_from_session_to_stage(self, vec: Gf.Vec3d) -> Gf.Vec3d
  - def load_asset(self, asset_name: Union[str, XRToken]) -> str
  - def set_meta_data(self, key: str, value: str)
  - def get_meta_data(self, key: str) -> Optional[str]
  - def clear_meta_data(self, key_prefix: str)
  - def get_prim_at_path(self, prim_path: Union[XRToken, str, Sdf.Path])
  - def is_grabbable(self, prim: Union[Sdf.Path, Usd.Prim, str]) -> bool
  - def set_grabbable(self, prim: Union[Sdf.Path, Usd.Prim, str], grabbable: bool = True)

- class XRInputDevice
  - def __init__(self, internal: XRInputDevice_Internal)
  - def get_name(self) -> XRToken
  - def get_type(self) -> XRToken
  - def ensure_pose(self, pose_name: Union[XRToken, str])
  - def remove_pose(self, pose_name: Union[XRToken, str])
  - def has_pose(self, pose_name: Union[XRToken, str]) -> bool
  - def get_raw_pose(self, pose_name: Union[XRToken, str] = '') -> Gf.Matrix4d
  - def get_raw_pose_desc(self, pose_name: Union[XRToken, str] = '') -> XRPoseDesc
  - def get_pose(self, pose_name: Union[XRToken, str] = '') -> Gf.Matrix4d
  - def get_pose_desc(self, pose_name: Union[XRToken, str] = '') -> XRPoseDesc
  - def set_pose_desc(self, pose_name: Union[XRToken, str], pose: XRPoseDesc)
  - def set_pose(self, pose_name: Union[XRToken, str], pose: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]])
  - def get_virtual_world_pose(self, pose_name: Union[XRToken, str] = '') -> Gf.Matrix4d
  - def get_virtual_world_pose_desc(self, pose_name: Union[XRToken, str] = '') -> XRPoseDesc
  - def get_pose_names(self) -> list[XRToken]
  - def get_all_poses(self) -> dict[str, XRPoseDesc]
  - def get_all_raw_poses(self) -> dict[str, XRPoseDesc]
  - def get_all_virtual_world_poses(self) -> dict[str, XRPoseDesc]
  - def ensure_input_gesture(self, input_name: Union[XRToken, str], gesture_name: Union[XRToken, str], source_name: Union[XRToken, str] = '')
  - def remove_input_gesture(self, input_name: Union[XRToken, str], gesture_name: Union[XRToken, str])
  - def remove_input_gestures_by_source(self, source_name: Union[XRToken, str])
  - def get_input_gesture_source(self, input_name: Union[XRToken, str], gesture_name: Union[XRToken, str]) -> XRToken
  - def has_input(self, input_name: Union[XRToken, str]) -> bool
  - def has_input_gesture(self, input_name: Union[XRToken, str], gesture_name: Union[XRToken, str]) -> bool
  - def set_input_base(self, input_name: Union[XRToken, str], base_input_name: Union[XRToken, str])
  - def get_input_base(self, input_name: Union[XRToken, str]) -> XRToken
  - def has_input_base(self, input_name: Union[XRToken, str]) -> bool
  - def get_overlapping_inputs(self, input_name: Union[XRToken, str]) -> list[XRToken]
  - def get_input_gesture_names(self, input_name: Union[XRToken, str]) -> list[XRToken]
  - def get_input_names(self) -> list[XRToken]
  - def set_input_gesture_value(self, input_name: Union[XRToken, str], gesture_name: Union[XRToken, str], value: float)
  - def get_input_gesture_value(self, input_name: Union[XRToken, str], gesture_name: Union[XRToken, str]) -> float
  - def get_hand_tracking_data_source(self) -> XRToken
  - def get_model(self) -> Optional[XRInputDeviceModel]
  - def ensure_output(self, output_name: Union[XRToken, str])
  - def remove_output(self, output_name: Union[XRToken, str])
  - def has_output(self, output_name: Union[XRToken, str]) -> bool
  - def set_output_value(self, output_name: Union[XRToken, str], value: float)
  - def get_output_value(self, output_name: Union[XRToken, str]) -> float
  - def get_output_names(self) -> list[XRToken]
  - def bind_event_generator(self, input_name: Union[XRToken, str], event_name: Union[XRToken, str], event_list: Iterable[Union[XRToken, str]], tooltips: Union[dict[str, str], str] = {}) -> Optional[XREventGenerator]
  - def unbind_event_generator(self, event_name: Union[XRToken, str])
  - def has_event_generator(self, input_name: Union[XRToken, str]) -> bool
  - def get_input_tooltips(self, input_name: Union[XRToken, str]) -> dict[str, str]

- class XREventGenerator
  - def __init__(self, internal: XREventGenerator_Internal)
  - def get_event_name(self) -> XRToken
  - def get_input_device_name(self) -> XRToken
  - def get_component_name(self) -> XRToken
  - def get_event_list(self) -> list[XRToken]
  - def set_auto_unbind(self, auto_unbind: bool)

- class XRInputDeviceModel
  - def __init__(self, internal: XRInputDeviceModel_Internal)
  - def get_name(self) -> XRToken
  - def get_asset(self) -> XRToken
  - def get_input_device_tags(self) -> dict[str, int]
  - def get_input_device_names(self) -> tuple[XRToken]

- class XRActionMap
  - def __init__(self, internal: XRActionMap_Internal)
  - def get_name(self) -> XRToken
  - def get_input_device_tags(self) -> tuple[XRToken]
  - def get_tool_layout(self) -> XRToken
  - def get_dominant_hand(self) -> XRToken
  - def get_tool_list(self) -> tuple[XRToken]
  - def get_action_map(self) -> tuple[XRActionMapRecord]

- class XRPoseDesc
  - pose_matrix: Gf.Matrix4d
  - validity_flags: XRPoseValidityFlags
  - def __init__(self, internal: XRPoseDesc_Internal)

- class XRPoseValidityFlags(enum.IntFlag)
  - ORIENTATION_VALID: int
  - POSITION_VALID: int
  - ORIENTATION_TRACKED: int
  - POSITION_TRACKED: int

- class XRShutdown
  - class def add_shutdown_function(cls, fn: Callable[[], Any], module: str, description: str)
  - class def assert_object_deletion_upon_shutdown(cls, obj: Any)
  - class def run_shutdown_functions(cls, module: str)

- class XRSingletonType(Protocol)
  - class def get_singleton(cls) -> Any

- class XREditorMenuToggleItem
  - def __init__(self, extension_id: str, menu_location: str, weak_fn: Callable, value: bool)
  - def refresh_menu(self)
  - [property] def ticked_value(self)
  - [ticked_value.setter] def ticked_value(self, value: bool)

- class XRCoreExtension(omni.ext.IExt)
  - def __init__(self)
  - def on_startup(self, _ext_id)
  - def on_shutdown(self)

- class XRUsdLayerManager(XRComponentBase, XRSingletonType)
  - def __init__(self)
  - def on_enable(self)
  - def on_disable(self)
  - def get_usd_layer(self, layer_name: str) -> Optional[XRUsdLayer]
  - def has_usd_layer(self, layer_name: str) -> bool

- class XRComponentBase
  - def __init__(self, name: str)
  - def start(self, event_name: str, enabled: bool = True)
  - def get_name(self) -> str
  - def get_event_name(self) -> str
  - def on_enable_callback(self)
  - def on_disable_callback(self)
  - def on_profile_update_callback(self)
  - def is_enabled(self) -> bool
  - def on_destroy(self)
  - def on_start(self)
  - def on_enable(self)
  - def on_disable(self)
  - def on_update(self)
  - def on_profile_update(self, profile_name: str)
  - def get_xr_core(self) -> XRCore
  - def get_settings(self) -> carb.settings.ISettings
  - def get_persistent_profile_setting_path(self, setting_name: str) -> str
  - def get_non_persistent_profile_setting_path(self, setting_name: str) -> str
  - def get_scene_persistent_profile_setting_path(self, setting_name: str) -> str
  - def register_setting_event_handler(self, setting_name: str, callback: Union[Callable[Ellipsis, None], Callable[Ellipsis, Any]]) -> carb.settings.SubscriptionId
  - def register_message_bus_event_handler(self, event_name: str, callback: Union[Callable[Ellipsis, None], Callable[Ellipsis, Any]], order = 0) -> carb.events.ISubscription
  - def dispatch_message_bus_event(self, message_name: Union[str, XRToken], payload: Any = {})
  - def translate_usd_name_to_event_name(self, usd_name: str) -> str

- class XRGuiLayerComponentBase(XRUsdComponentBase)
  - def __init__(self, name: str)
  - def run_enable_if_enabled(self)

- class XRToolComponentBase(XRUsdComponentBase)
  - def __init__(self, name: str)
  - def is_enabled(self) -> bool
  - def run_enable_if_enabled(self)
  - def bind_input_event_generator(self, event_name: str, event_list: Iterable[str], tooltips: Union[str, dict[str, str]]) -> Optional[XREventGenerator]
  - def bind_selection_event_generator(self, event_name: str, event_list: Iterable[str], usd_path: str, priority: int) -> XRSelectionEventGeneratorSubscription

- class XRGuiLayerEvent
  - def __init__(self, event: carb.events.IEvent)
  - [property] def gui_layer(self) -> str
  - [property] def carb_event(self) -> carb.events.IEvent

- class XRInputDeviceEvent
  - def __init__(self, event: carb.events.IEvent)
  - [property] def input_device(self) -> str
  - [property] def carb_event(self) -> carb.events.IEvent

- class XRToolEvent
  - def __init__(self, event: carb.events.IEvent)
  - [property] def tool(self) -> str
  - [property] def carb_event(self) -> carb.events.IEvent

- class XRActionMapEvent
  - def __init__(self, event: carb.events.IEvent)
  - [property] def action_map(self) -> str
  - [property] def carb_event(self) -> carb.events.IEvent

- class XRProfileEvent
  - def __init__(self, event: carb.events.IEvent)
  - [property] def profile(self) -> str
  - [property] def carb_event(self) -> carb.events.IEvent

- class XRProfileListEvent
  - def __init__(self, event: carb.events.IEvent)
  - [property] def profile(self) -> str
  - [property] def carb_event(self) -> carb.events.IEvent

- class XRSystemEvent
  - def __init__(self, event: carb.events.IEvent)
  - [property] def system(self) -> str
  - [property] def carb_event(self) -> carb.events.IEvent

- class XRSystemListEvent
  - def __init__(self, event: carb.events.IEvent)
  - [property] def systems(self) -> str
  - [property] def carb_event(self) -> carb.events.IEvent

- class XRTooltipEvent
  - def __init__(self, event: carb.events.IEvent)
  - [property] def input_device(self) -> str
  - [property] def input(self) -> str
  - [property] def tooltip_button(self) -> Optional[str]
  - [property] def tooltip_left(self) -> Optional[str]
  - [property] def tooltip_right(self) -> Optional[str]
  - [property] def tooltip_left_right(self) -> Optional[str]
  - [property] def tooltip_up(self) -> Optional[str]
  - [property] def tooltip_down(self) -> Optional[str]
  - [property] def tooltip_up_down(self) -> Optional[str]
  - [property] def carb_event(self) -> carb.events.IEvent

- class XRInputDeviceGeneratorEvent
  - def __init__(self, event: carb.events.IEvent)
  - [property] def event_name(self) -> str
  - [property] def event_type(self) -> str
  - [property] def input(self) -> str
  - [property] def input_device(self) -> str
  - [property] def input_device_type(self) -> str
  - [property] def dt(self) -> str
  - [property] def touch(self) -> Optional[str]
  - [property] def click(self) -> Optional[str]
  - [property] def value(self) -> Optional[str]
  - [property] def x(self) -> Optional[str]
  - [property] def y(self) -> Optional[str]
  - [property] def carb_event(self) -> carb.events.IEvent

- class XRSelectionManager(XRSingletonType)
  - def __init__(self)
  - def set_selection(self, selection: Union[str, Iterable[str], None])
  - def toggle_selection(self, selection: Union[str, None])
  - def clear_selection(self)
  - def bind_event_generator(self, path: Union[str, None], priority: int, event_name: str, event_types: Union[str, Iterable[str]]) -> XRSelectionEventGeneratorSubscription
  - def create_beam(self, usd_layer: XRUsdLayer, hand: Union[XRToken, str], attachment_point: str, material: str, max_length: float = 10000, tube_radius: float = 0.5) -> XRSelectionBeam
  - def destroy_beam(self, hand: Union[XRToken, str])
  - def get_beam(self, hand: Union[XRToken, str]) -> Optional[XRSelectionBeam]
  - def dispatch_release(self, hand: Union[XRToken, str], button_changed: str)
  - def dispatch_press(self, hand: Union[XRToken, str], button_changed: str)
  - def dispatch_update(self, hand: Union[XRToken, str])
  - def process_hover(self, hand: Union[XRToken, str])

- class XRSelectionBeam
  - def __init__(self, usd_layer: XRUsdLayer, hand: Union[XRToken, str], attachment_point: str, material: str, max_length: float = 10000, tube_radius: float = 0.5)
  - def get_turn_table_path(self) -> Optional[str]
  - def get_link_path(self) -> Optional[str]
  - def create_turn_table_and_link(self, target_usd_path: str)
  - def remove_turn_table_and_link(self, commit: bool = True)
  - def get_length(self) -> float
  - def set_length(self, length: float)
  - def get_hand(self) -> str
  - def get_target_info(self) -> Optional[XRTargetInfo]
  - def get_button_target_info(self) -> Optional[XRTargetInfo]
  - def update_target_info(self)
  - def add_pressed_button(self, button: str)
  - def remove_pressed_button(self, button: str)
  - def check_button_is_pressed(self, button: str) -> bool
  - def get_pressed_buttons(self) -> Set[str]
  - def check_if_buttons_are_pressed(self) -> bool
  - def update_visibility(self)
  - def set_active(self, active: bool)
  - def set_pointing_at_ui(self, pointing_at_ui: bool)
  - def is_active(self) -> bool
  - def is_pointing_at_ui(self) -> bool
  - def is_visible(self) -> bool
  - def get_beam_pose(self) -> Gf.Matrix4d
  - def get_beam_end_pose(self) -> Gf.Matrix4d

- class XRSelectionEvent
  - def __init__(self, event: carb.events.IEvent)
  - [property] def hand(self) -> str
  - [property] def selected_path(self) -> str
  - [property] def enclosing_model(self) -> str
  - [property] def hit_valid(self) -> bool
  - [property] def hit_point(self) -> Gf.Vec3d
  - [property] def hit_normal(self) -> Gf.Vec3d
  - [property] def button_changed(self) -> str
  - [property] def carb_event(self) -> carb.events.IEvent
  - def consume(self)

- class XRSelectionEventGeneratorSubscription
  - def __init__(self, disconnect_fcn)

- class XRTooltip
  - def __init__(self, icon = None, text = None)
  - [property] def icon(self) -> Optional[str]
  - [icon.setter] def icon(self, value: Optional[str])
  - [property] def text(self) -> Union[str, list[str], None]
  - [text.setter] def text(self, value: Union[str, list[str], None])

- class XRTooltipManager(XRSingletonType)
  - def __init__(self)
  - def define_tooltip(self, tooltip_name: str, tooltip: XRTooltip)
  - def get_tooltip(self, tooltip_name: str) -> XRTooltip

## Functions

- def XRSingleton()
- def XRWeakMethod(fn: Union[Callable[Ellipsis, Any], Callable[Ellipsis, None]], def_return: Any = None) -> Union[Callable[Ellipsis, Any], Callable[Ellipsis, None]]
- def printXRException(exp, exc_info)

## Variables

- XRUtils: XRCore
- XR_INPUT_DEVICE_HAND_TRACKING_POSE_NAMES: Tuple
- INTERACT_FREEZE_DELAY_SETTING_KEY: str

# Public API for module omni.kit.xr.core.imagecomparison:

## Classes

- class XRComparisonResults
  - def __init__(self)
  - [property] def images_equal(self) -> bool
  - [images_equal.setter] def images_equal(self, arg0: bool)
  - [property] def message(self) -> str
  - [message.setter] def message(self, arg0: str)
  - [property] def result_value(self) -> float
  - [result_value.setter] def result_value(self, arg0: float)
  - [property] def threshold(self) -> float
  - [threshold.setter] def threshold(self, arg0: float)

- class XRImageComparisonDesc
  - def __init__(self, arg0: str, arg1: str, arg2: str)
  - [property] def diff_filename(self) -> str
  - [diff_filename.setter] def diff_filename(self, arg0: str)
  - [property] def golden_filename(self) -> str
  - [golden_filename.setter] def golden_filename(self, arg0: str)
  - [property] def output_filename(self) -> str
  - [output_filename.setter] def output_filename(self, arg0: str)

## Functions

- def xr_compare_output_image_to_golden_image(arg0: XRImageComparisonDesc, arg1: float) -> XRComparisonResults

# Public API for module omni.kit.xr.core.recorder:

## Classes

- class XRCore
  - def __init__(self)
  - static def get_singleton() -> XRCore
  - def get_message_bus(self) -> carb.events.IEventStream
  - def dispatch_message_bus_and_check_consume(self, event_type, event_dict) -> bool
  - def get_profile(self, name: str) -> XRProfile
  - def ensure_profile(self, name: str) -> XRProfile
  - def get_coordinate_system(self) -> XRCoordinateSystem
  - def get_stage_coordinate_system(self) -> XRCoordinateSystem
  - def get_profile_list(self) -> list[XRProfile]
  - def get_profile_name_list(self) -> list[str]
  - def get_system(self, name: str) -> Optional[XRSystem]
  - def get_systems(self, modes: Union[list[str], str, None] = None) -> list[XRSystem]
  - def get_system_names(self, modes: Union[list[str], str, None] = None) -> list[str]
  - def is_xr_enabled(self) -> bool
  - def is_xr_display_enabled(self) -> bool
  - def is_xr_viewport_enabled(self) -> bool
  - def get_current_profile(self) -> XRProfile
  - def get_current_xr_profile(self) -> XRProfile
  - def get_current_profile_name(self) -> str
  - def get_current_xr_profile_name(self) -> str
  - def create_xr_usd_layer(self, usd_path: str, meters_per_unit: float = 0.01, up_axis: str = 'y', ui_layer_name: str = '', component_layer_name: str = '') -> XRUsdLayer
  - static def request_enable_profile(name: str)
  - def request_disable_profile(self)
  - def schedule_capture_viewport_frame(self, file_name: str, viewport_id: int = 0)
  - def schedule_capture_display_frame(self, file_name: str, display_name: Optional[str] = None, capture_source: Optional[str] = None, capture_output: Optional[str] = 'color', capture_depth_range: Tuple[float, float] = (0.1, 10.0))
  - static def show_ovxr_app_docs(page: Optional[str] = None)
  - def test_system(self, system_name: str, test_name: str)
  - def submit_raycast_query(self, ray: XRRay, callback: Callable[[XRRay, XRRayQueryResult], None])
  - def submit_multi_raycast_query(self, rays: list[XRRay], callback: Callable[[list[XRRay], list[XRRayQueryResult]], None])
  - def get_stage_anchor_prim_path(self) -> Optional[str]
  - def detach_stage_anchor(self)
  - def schedule_apply_viewport_navigation(self, dx: float, dy: float, dz: float, yaw: float, pitch: float)
  - def schedule_set_stage_anchor(self, stage_anchor: str)
  - def schedule_teleport_to_view(self, stage_anchor: str, view_pose: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]])
  - def schedule_set_space_origin(self, space_origin_pose: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]])
  - def schedule_set_camera(self, view_pose: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]])
  - def schedule_move_space_origin_relative_to_camera(self, dx: float, dy: float, dz: float)
  - def schedule_rotate_space_origin_relative_to_camera(self, yaw: float, pitch: float)
  - def get_input_device(self, handle: Union[str, XRToken]) -> Optional[XRInputDevice]
  - def has_input_device(self, handle: Union[str, XRToken]) -> bool
  - def get_input_devices(self, handle: Union[str, XRToken]) -> list[XRInputDevice]
  - def get_all_input_devices(self) -> list[XRInputDevice]
  - def get_action_map(self) -> Optional[XRActionMap]
  - def is_gui_enabled(self) -> bool
  - def is_tool_enabled(self, tool: Union[str, XRToken]) -> bool
  - def is_gui_layer_enabled(self, gui_layer: Union[str, XRToken]) -> bool
  - def bind_input_event_generator(self, event_name: str, event_list: Iterable[str], tooltips: Union[dict[str, str], str] = {}) -> Optional[XREventGenerator]
  - def unbind_input_event_generator(self, event_name: str)
  - static def check_current_renderer_supported(profile_display_name: str, notify: bool = True) -> bool
  - def set_pickable_path(self, usd_path: str, pickable: bool)
  - def unset_pickable_path(self, usd_path: str)
  - def is_fsd_enabled(self) -> bool
  - def suggest_edit_layer_for_prim(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> str
  - def check_if_prim_transform_is_usdrt_only(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> bool
  - def check_if_prim_is_on_layer(self, prim: Union[Usd.Prim, Sdf.Path, str], layer: Union[str, None, Sdf.Layer]) -> bool
  - def remove_prim_from_layer(self, prim: Union[Usd.Prim, Sdf.Path, str], layer: Union[str, None, Sdf.Layer])
  - def set_local_transform_matrix(self, prim: Union[Usd.Prim, Sdf.Path, str], matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]], layer_identifier: Union[str, None] = None)
  - def set_world_transform_matrix(self, prim: Union[Usd.Prim, Sdf.Path, str], matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]], layer_identifier: Union[str, None] = None)
  - def get_local_transform_matrix(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> Gf.Matrix4d
  - def get_world_transform_matrix(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> Gf.Matrix4d
  - def get_enclosing_model(self, usd_path: str) -> str
  - def reorient_transform_matrix_up_right(self, matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]], y_up: bool = True) -> Gf.Matrix4d
  - def reorient_transform_matrix_no_roll(self, matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]], y_up: bool = True) -> Gf.Matrix4d
  - static def on_raycast_query_result(_ray: XRRay, result: XRRayQueryResult, future: asyncio.Future)
  - async def execute_raycast_query_async(self, ray: XRRay) -> XRRayQueryResult
  - static def on_multi_raycast_query_result(_rays: List[XRRay], results: List[XRRayQueryResult], future: asyncio.Future)
  - async def execute_multi_raycast_query_async(self, rays: List[XRRay]) -> List[XRRayQueryResult]

- class XRCoreEventType
  - static def profile_disable(arg0: object) -> int
  - static def profile_enable(arg0: object) -> int
  - static def system_disable(arg0: object) -> int
  - static def system_enable(arg0: object) -> int
  - first_launch_greeting: int
  - post_device_events_update: int
  - post_layer_update: int
  - post_sync_update: int
  - pre_sync_update: int
  - profile_changed: int
  - profile_list_updated: int
  - system_changed: int
  - system_list_updated: int
  - xr_disabled: int
  - xr_display_disabled: int
  - xr_display_enabled: int
  - xr_enabled: int
  - xr_viewport_disabled: int
  - xr_viewport_enabled: int

- class XCRReplayAPI
  - def __init__(self)
  - def get_replay_frame_count(self) -> int
  - def get_replay_frame_timestamp(self, frame_index: int) -> float
  - def get_replay_interaction_profile(self) -> str
  - def play_replay(self)
  - def set_replay_file(self, filepath: str)
  - def set_replay_frame(self, frame_index: int)
  - def set_replay_playback_complete_callback(self, playback_complete_callback: function)
  - def set_replay_timestamp(self, timestamp_in_seconds: float)
  - def start_replay_service(self, captured_replay_filepath: str)
  - def start_replay_service_with_config(self, captured_replay_filepath: str, replay_service_config: XCRReplayServiceMainConfig)
  - def stop_replay(self)
  - def stop_replay_service_after_replay_playback(self)
  - def stop_replay_service_immediately(self)

- class XCRReplayServiceMainConfig
  - def __init__(self)
  - def __init__(self, profile: typing.Optional[str], width: typing.Optional[int], height: typing.Optional[int])
  - [property] def overridden_interaction_profile(self) -> str
  - [overridden_interaction_profile.setter] def overridden_interaction_profile(self, arg0: str)
  - [property] def resolution_height(self) -> int
  - [resolution_height.setter] def resolution_height(self, arg0: int)
  - [property] def resolution_width(self) -> int
  - [resolution_width.setter] def resolution_width(self, arg0: int)

- class XCRReplayService
  - def __init__(self, replay_filepath: str, xr_test: test_utils.XRTest, service_config: Optional[XCRReplayServiceMainConfig] = None)
  - def set_registry_value_for_windows(self)
  - def clear_registry_value_for_windows(self)
  - async def ensure_xcr_is_active_openxr_runtime(self)
  - def get_xcr_api(self) -> XCRReplayAPI
  - def is_running_on_ci(self) -> bool
  - def set_simulated_elapsed_time(self, elapsed_time: float)
  - async def replay_frames_and_perform_golden_image_viewport_tests(self, capture_frequency: int, output_file_name: str, threshold: float, source_name: Optional[str], fixed_elapsed_time: Optional[float] = None, max_frame: Optional[int] = None)

## Functions

- def get_xcr_capture_filepath()
- def on_capture_button_clicked(is_capture_started: bool, frame: ui.Frame)
- def start_replay_if_enabled(xr_profile: XRProfile)
- def stop_replay_service(xr_profile: XRProfile)

## Variables

- NINETY_FPS_FIXED_ELAPSED_TIME: Final

## Other

- asyncio: builtin module
- os: builtin module
- pathlib: builtin module
- platform: builtin module
- tempfile: builtin module
- Final: unknown
- Optional: unknown
- carb: public module


# Public API for module omni.kit.xr.core.test_utils:

## Classes

- class XRCore
  - def __init__(self)
  - static def get_singleton() -> XRCore
  - def get_message_bus(self) -> carb.events.IEventStream
  - def dispatch_message_bus_and_check_consume(self, event_type, event_dict) -> bool
  - def get_profile(self, name: str) -> XRProfile
  - def ensure_profile(self, name: str) -> XRProfile
  - def get_coordinate_system(self) -> XRCoordinateSystem
  - def get_stage_coordinate_system(self) -> XRCoordinateSystem
  - def get_profile_list(self) -> list[XRProfile]
  - def get_profile_name_list(self) -> list[str]
  - def get_system(self, name: str) -> Optional[XRSystem]
  - def get_systems(self, modes: Union[list[str], str, None] = None) -> list[XRSystem]
  - def get_system_names(self, modes: Union[list[str], str, None] = None) -> list[str]
  - def is_xr_enabled(self) -> bool
  - def is_xr_display_enabled(self) -> bool
  - def is_xr_viewport_enabled(self) -> bool
  - def get_current_profile(self) -> XRProfile
  - def get_current_xr_profile(self) -> XRProfile
  - def get_current_profile_name(self) -> str
  - def get_current_xr_profile_name(self) -> str
  - def create_xr_usd_layer(self, usd_path: str, meters_per_unit: float = 0.01, up_axis: str = 'y', ui_layer_name: str = '', component_layer_name: str = '') -> XRUsdLayer
  - static def request_enable_profile(name: str)
  - def request_disable_profile(self)
  - def schedule_capture_viewport_frame(self, file_name: str, viewport_id: int = 0)
  - def schedule_capture_display_frame(self, file_name: str, display_name: Optional[str] = None, capture_source: Optional[str] = None, capture_output: Optional[str] = 'color', capture_depth_range: Tuple[float, float] = (0.1, 10.0))
  - static def show_ovxr_app_docs(page: Optional[str] = None)
  - def test_system(self, system_name: str, test_name: str)
  - def submit_raycast_query(self, ray: XRRay, callback: Callable[[XRRay, XRRayQueryResult], None])
  - def submit_multi_raycast_query(self, rays: list[XRRay], callback: Callable[[list[XRRay], list[XRRayQueryResult]], None])
  - def get_stage_anchor_prim_path(self) -> Optional[str]
  - def detach_stage_anchor(self)
  - def schedule_apply_viewport_navigation(self, dx: float, dy: float, dz: float, yaw: float, pitch: float)
  - def schedule_set_stage_anchor(self, stage_anchor: str)
  - def schedule_teleport_to_view(self, stage_anchor: str, view_pose: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]])
  - def schedule_set_space_origin(self, space_origin_pose: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]])
  - def schedule_set_camera(self, view_pose: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]])
  - def schedule_move_space_origin_relative_to_camera(self, dx: float, dy: float, dz: float)
  - def schedule_rotate_space_origin_relative_to_camera(self, yaw: float, pitch: float)
  - def get_input_device(self, handle: Union[str, XRToken]) -> Optional[XRInputDevice]
  - def has_input_device(self, handle: Union[str, XRToken]) -> bool
  - def get_input_devices(self, handle: Union[str, XRToken]) -> list[XRInputDevice]
  - def get_all_input_devices(self) -> list[XRInputDevice]
  - def get_action_map(self) -> Optional[XRActionMap]
  - def is_gui_enabled(self) -> bool
  - def is_tool_enabled(self, tool: Union[str, XRToken]) -> bool
  - def is_gui_layer_enabled(self, gui_layer: Union[str, XRToken]) -> bool
  - def bind_input_event_generator(self, event_name: str, event_list: Iterable[str], tooltips: Union[dict[str, str], str] = {}) -> Optional[XREventGenerator]
  - def unbind_input_event_generator(self, event_name: str)
  - static def check_current_renderer_supported(profile_display_name: str, notify: bool = True) -> bool
  - def set_pickable_path(self, usd_path: str, pickable: bool)
  - def unset_pickable_path(self, usd_path: str)
  - def is_fsd_enabled(self) -> bool
  - def suggest_edit_layer_for_prim(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> str
  - def check_if_prim_transform_is_usdrt_only(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> bool
  - def check_if_prim_is_on_layer(self, prim: Union[Usd.Prim, Sdf.Path, str], layer: Union[str, None, Sdf.Layer]) -> bool
  - def remove_prim_from_layer(self, prim: Union[Usd.Prim, Sdf.Path, str], layer: Union[str, None, Sdf.Layer])
  - def set_local_transform_matrix(self, prim: Union[Usd.Prim, Sdf.Path, str], matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]], layer_identifier: Union[str, None] = None)
  - def set_world_transform_matrix(self, prim: Union[Usd.Prim, Sdf.Path, str], matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]], layer_identifier: Union[str, None] = None)
  - def get_local_transform_matrix(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> Gf.Matrix4d
  - def get_world_transform_matrix(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> Gf.Matrix4d
  - def get_enclosing_model(self, usd_path: str) -> str
  - def reorient_transform_matrix_up_right(self, matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]], y_up: bool = True) -> Gf.Matrix4d
  - def reorient_transform_matrix_no_roll(self, matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]], y_up: bool = True) -> Gf.Matrix4d
  - static def on_raycast_query_result(_ray: XRRay, result: XRRayQueryResult, future: asyncio.Future)
  - async def execute_raycast_query_async(self, ray: XRRay) -> XRRayQueryResult
  - static def on_multi_raycast_query_result(_rays: List[XRRay], results: List[XRRayQueryResult], future: asyncio.Future)
  - async def execute_multi_raycast_query_async(self, rays: List[XRRay]) -> List[XRRayQueryResult]

- class XRCoreEventType
  - static def profile_disable(arg0: object) -> int
  - static def profile_enable(arg0: object) -> int
  - static def system_disable(arg0: object) -> int
  - static def system_enable(arg0: object) -> int
  - first_launch_greeting: int
  - post_device_events_update: int
  - post_layer_update: int
  - post_sync_update: int
  - pre_sync_update: int
  - profile_changed: int
  - profile_list_updated: int
  - system_changed: int
  - system_list_updated: int
  - xr_disabled: int
  - xr_display_disabled: int
  - xr_display_enabled: int
  - xr_enabled: int
  - xr_viewport_disabled: int
  - xr_viewport_enabled: int

- class XRProfile
  - def __init__(self, internal: XRProfile_Internal = None)
  - def get_name(self) -> str
  - def request_enable_profile(self)
  - def is_enabled(self) -> bool
  - def get_persistent_path(self) -> str
  - def get_non_persistent_path(self) -> str
  - def get_scene_persistent_path(self) -> str
  - def get_temp_path(self) -> str
  - def get_ar_mode(self) -> bool
  - def set_ar_mode(self, ar_mode)
  - def set_config(self, config: Any)
  - def get_config(self) -> Any
  - def teleport(self, transform: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]])

- class EnabledXRProfile
  - def __init__(self, profile_name: str, frames_to_wait: int = 3)

- class TestTabletProfile
  - WAIT_ASYNC_TIME: int
  - def __init__(self, test_class_instance: XRTestTablet)

- class XRTestTablet(XRTest)
  - def __init__(self, *args, **kwargs)
  - async def setUp(self)
  - async def tearDown(self)
  - def create_tablet_profile(self, name: str) -> XRProfile
  - def update_viewport_gizmos(self)
  - def create_test_tablet_profile(self, name: str) -> XRProfile
  - def create_perf_tablet_profile(self, name: str) -> XRProfile
  - async def start_tablet_test_profile(self) -> XRProfile

- class ViewportCameraState
  - def __init__(self, camera_path: str = None, viewport = None, time: Usd.TimeCode = None, **kwargs)
  - def get_world_camera_up(self, stage) -> Gf.Vec3d
  - [property] def usd_camera(self) -> Usd.Prim
  - [property] def position_world(self)
  - [property] def target_world(self)
  - def set_position_world(self, world_position: Gf.Vec3d, rotate: bool)
  - def set_target_world(self, world_target: Gf.Vec3d, rotate: bool)

- class GoldenImageTest
  - def __init__(self, disable_comparison)
  - def get_frames_to_wait(self) -> int
  - def prepare_paths(self, golden_image_name: str, module_name: Optional[str]) -> Tuple[List[str], List[str]]
  - def capture_images(self, golden_image_name: str, file_paths: List[str])
  - async def capture_and_compare_output_async(self, golden_image_name: str, threshold: float, module_name: Optional[str]) -> bool
  - def compare_all_test_images(self, file_names: List[str], threshold: float, module_name: Optional[str]) -> bool
  - async def wait_for_images_async(self, paths: Sequence[str]) -> bool
  - async def wait_pre_sync_async(self, count: int = 1)

- class QuadviewImageTest(GoldenImageTest)
  - def __init__(self, disable_comparison, **kwargs)

- class StereoGoldenImageTest(GoldenImageTest)
  - def __init__(self, disable_comparison, **kwargs)

- class TabletGoldenImageTest(GoldenImageTest)
  - def __init__(self, disable_comparison, **kwargs)

- class ViewportGoldenImageTest(GoldenImageTest)
  - def __init__(self, disable_comparison)

- class WarpedGoldenImageTest(GoldenImageTest)
  - def __init__(self, disable_comparison, **kwargs)

- class XRTest(omni.kit.test.AsyncTestCase)
  - async def setUp(self)
  - async def tearDown(self)
  - def set_module(self, module: str)
  - def is_linux(self) -> bool
  - def disable_comparison(self)
  - def is_comparison_disabled(self)
  - def compare_result(self, new_result: bool)
  - def get_recording_directory(self, module: Union[str, None] = None) -> pathlib.Path
  - async def wait_post_sync_async(self, count: int = 1)
  - async def wait_materials_loaded_async(self)
  - async def wait_pre_sync_async(self, count: int = 1)
  - async def capture_and_compare_stereo_output_async(self, golden_image_name: str, threshold: float, module_name: str, capture_source: Optional[str] = None, capture_output: str = 'color', capture_depth_range: tuple[float, float] = (0.1, 10.0))
  - async def capture_and_compare_tablet_output_async(self, golden_image_name: str, threshold: float, module_name: str, capture_source: Optional[str] = None, capture_output: str = 'color', capture_depth_range: tuple[float, float] = (0.1, 10.0))
  - async def capture_and_compare_quadview_output_async(self, golden_image_name: str, threshold: float, module_name: str, capture_source: Optional[str] = None, capture_output: str = 'color', capture_depth_range: tuple[float, float] = (0.1, 10.0))
  - async def capture_and_compare_warped_output_async(self, golden_image_name: str, threshold: float, module_name: str, capture_output: str = 'color', capture_depth_range: tuple[float, float] = (0.1, 10.0))
  - async def capture_and_compare_viewport_output_async(self, golden_image_name: str, threshold: float, module_name: str)
  - async def new_stage_async(self)
  - async def load_stage_async(self, file_path: str)
  - def request_enable_profile(self, name: str)
  - def request_disable_profile(self)
  - def set_xr_camera(self, position: Gf.Vec3d, target: Gf.Vec3d)
  - def set_viewport_camera(self, position: Gf.Vec3d, target: Gf.Vec3d)
  - async def set_physical_world_matrix(self, pymatrix)
  - async def wait_until_event_set(self, event: asyncio.Event)
  - def set_param(self, profile: str, path: str, value: Any)
  - def set_setting(self, path: str, value: Any)

- class XRUsdStage
  - def __init__(self, usd_file_path: Optional[str] = None, keep_stage: Optional[bool] = False)
  - static def get_layer_names() -> Set[str]
  - static def get_prim_names() -> Set[str]
  - static def has_xr_gui_prims() -> bool

- class TestVRProfile
  - WAIT_ASYNC_TIME: int
  - def __init__(self, test_class_instance: XRTestVR)

- class TestVRUIProfile
  - WAIT_ASYNC_TIME: int
  - def __init__(self, test_class_instance: XRTestVR)

- class XRTestVR(XRTest)
  - def __init__(self, *args, **kwargs)
  - async def setUp(self)
  - async def tearDown(self)
  - def set_vr_profile_defaults(self, name: str)
  - def set_vr_ui_profile_defaults(self, name: str)
  - def create_test_vr_profile(self, name: str) -> XRProfile
  - def create_test_vr_ui_profile(self, name: str) -> XRProfile
  - def set_vr_profile_settings(self, name: str)
  - async def start_vr_test_profile(self) -> XRProfile
  - async def start_vr_ui_test_profile(self) -> XRProfile

## Functions

- def assert_setting(test_instance, path: str, value: Any)
- async def run_system_test(test_case: omni.kit.test.AsyncTestCase, system_name: str, test_name: str)
- def get_xcr_recording_directory(module: Union[str, None] = None) -> pathlib.Path
- def get_golden_image_source_directory(module: Union[str, None] = None) -> pathlib.Path
- def get_xcr_runtime_json() -> str
- def get_xcr_directory() -> pathlib.Path
- def get_data_directory(module: Union[str, None] = None) -> pathlib.Path
- def get_usd_directory(module: Union[str, None] = None) -> pathlib.Path
- def get_test_output_directory() -> pathlib.Path
- def ensure_directory_exist(directory: str)
- def get_test_ext_output_directory() -> pathlib.Path
- def get_test_name_and_file_name(test_image_name: str, test_file_name: Optional[str], type_name: str) -> str
- def get_ext_id_by_file_name(file_name: Optional[str]) -> str
- def get_current_profile() -> XRProfile
- def get_current_xr_profile_name() -> str
- def get_active_viewport(usd_context_name: str = '')
- def opened_usd_stage(usd_file_path = None, keep_stage = False)

## Other

- Any: unknown
- carb: public module
- omni.kit.app: public module
- os: builtin module
- pathlib: builtin module
- lru_cache: unknown
- Optional: unknown
- Union: unknown
- asyncio: builtin module
- Sequence: unknown
- Set: unknown
- omni.kit.test: public module
- omni.usd: public module
- Gf: unknown
- functools: builtin module


