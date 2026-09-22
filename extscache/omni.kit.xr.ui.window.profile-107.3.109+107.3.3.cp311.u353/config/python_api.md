# Public API for module omni.kit.xr.ui.window.profile:

## Classes

- class XRSettingsFrame
  - def __init__(self, profile: XRProfile, config: dict = {})
  - def is_advanced(self)
  - def is_info(self)
  - def is_collapsed(self)
  - def is_collapsable(self)
  - def get_config(self)
  - def get_profile_name(self) -> str
  - def get_profile_path(self) -> str
  - def get_persistent_path(self) -> str
  - def get_non_persistent_path(self) -> str
  - def get_scene_persistent_path(self) -> str
  - def get_non_profile_persistent_path(self) -> str
  - def get_non_profile_path(self) -> str
  - def get_profile(self)
  - def get_frame_name(self) -> str
  - def destroy(self)
  - def build_header(self, collapsed, title)
  - def add_info(self, name: str, path: str)
  - def add_info_bool(self, name: str, path: str, trueText: str, falseText: str)
  - def add_setting(self, setting_type, name: str, path: str, range_from = 0, range_to = 0, step = 0.01, has_reset = True, tooltip = '', callback = None, **kwargs)
  - def add_setting_combo(self, name: str, path: str, items: Union[list, dict], callback = None, has_reset = True, tooltip = '')
  - def build_ui(self)
  - def add_rebuild_subscription(self, path: str)
  - def add_rebuild_on_messagebus(self, message_name: str)
  - def get_available_systems(self) -> List[XRSystem]
  - def get_current_system(self) -> Union[None, XRSystem]
  - def is_quadview_active(self) -> bool

- class XRSettingsStack
  - def __init__(self, components)
  - def build_ui(self, profile: XRProfile)

- class XRMenuAdvancedFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)
  - def is_advanced(self)

- class XRMenuAnchorFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class SettingType(Enum)
  - FLOAT: int
  - INT: int
  - COLOR3: int
  - BOOL: int
  - STRING: int
  - DOUBLE3: int
  - INT2: int
  - DOUBLE2: int
  - ASSET: int

- class XRMenuClippingPlanesFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuDesktopDisplayFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuEyeTrackingFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuFoveationSettingsFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuGeneralFrame(XRSettingsFrame)
  - def build_ui(self)

- class XRMenuGeneralARFrame(XRMenuGeneralFrame)
  - def get_frame_name(self)
  - def is_collapsable(self)

- class XRMenuGeneralTabletARFrame(XRMenuGeneralFrame)
  - def get_frame_name(self)
  - def is_collapsable(self)

- class XRMenuGeneralVRFrame(XRMenuGeneralFrame)
  - def get_frame_name(self)
  - def is_collapsable(self)

- class XRMenuMatteObjectFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuNavigationFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuOpenXRInfo(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuOpenXRSetupInstructions(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuOutputFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

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

- class XRMenuScalingFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuSimulatedXRInfo(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuSimulationFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuSimulationStereoFrame(XRMenuSimulationFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuSimulationTabletFrame(XRMenuSimulationFrame)
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuSimulationControllerFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)
  - def make_button(self, input_device, input)
  - def layout_buttons(self, label_name: str, device_name: str)

- class XRMenuXCRFrame(XRSettingsFrame)
  - capture_layer_path_setting: str
  - replay_enabled_path_setting: str
  - replay_file_path_setting: str
  - def get_frame_name(self)
  - def build_ui(self)

- class XRMenuSystemInfo(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)
  - def is_info(self)

- class XRMenuViewportSettingsFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)

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

- class XRMenuXRDepthFrame(XRSettingsFrame)
  - def get_frame_name(self)
  - def build_ui(self)
  - def on_xr_update(self, event)
  - def on_xr_disable(self, event)

- class XRSettingsDefaults
  - def reset_setting_to_default(self, settings_path: str)

- class RestoreDefaultXRSettingCommand(omni.kit.commands.Command)
  - def __init__(self, path: str)
  - def do(self)
  - def undo(self)

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

- class XRShutdown
  - class def add_shutdown_function(cls, fn: Callable[[], Any], module: str, description: str)
  - class def assert_object_deletion_upon_shutdown(cls, obj: Any)
  - class def run_shutdown_functions(cls, module: str)

- class XRSystem
  - def __init__(self, internal: XRSystem_Internal)
  - def get_name(self) -> str
  - def get_modes(self) -> list[str]
  - def has_mode(self, modeName: str) -> bool
  - def get_meta_data(self, key: str, default: Any) -> Any

- class SettingsWidgetBuilder
  - checkbox_alignment: NoneType
  - checkbox_alignment_set: bool
  - class def get_checkbox_alignment(cls)
  - label_alignment: NoneType
  - label_alignment_set: bool
  - class def get_label_alignment(cls)
  - class def createColorWidget(cls, model, comp_count = 3, additional_widget_kwargs = None) -> omni.ui.HStack
  - class def createVecWidget(cls, model, range_min, range_max, comp_count = 3, additional_widget_kwargs = None)
  - class def createIVecWidget(cls, model, range_min, range_max, comp_count = 3, additional_widget_kwargs = None)
  - class def createLabelMultiline(cls, text: str, **label_kwargs)
  - class def createBoolWidget(cls, model, additional_widget_kwargs = None)
  - class def createFloatFieldWidget(cls, model, kwargs = None)
  - class def createFloatWidget(cls, model, range_min, range_max, step, kwargs = None)
  - class def createIntFieldWidget(cls, model, kwargs = None)
  - class def createIntWidget(cls, model, range_min, range_max, step, kwargs = None)
  - class def createAssetWidget(cls, model, additional_widget_kwargs = None)
  - class def createPathWidget(cls, model, additional_widget_kwargs = None)
  - class def createPathOrAssetWidget(cls, model, additional_widget_kwargs = None)

- class AssetPathSettingsModel(SettingModel)
  - def get_resolved_path(self)

- class SettingModel(ui.AbstractValueModel)
  - def __init__(self, setting_path: str, draggable: bool = False)
  - def begin_edit(self)
  - def end_edit(self)
  - def get_value_as_string(self) -> str
  - def get_value_as_float(self) -> float
  - def get_value_as_bool(self) -> bool
  - def get_value_as_int(self) -> int
  - def set_value(self, value: Any)
  - def set_reset_button(self, button: ui.Rectangle)
  - def destroy(self)

- class SettingsComboItemModel(ui.AbstractItemModel)
  - def __init__(self, setting_path, key_value_pairs: Dict[str, Any])
  - def set_reset_button(self, button)
  - def get_item_children(self, item)
  - def get_item_value_model(self, item, column_id: int)
  - def destroy(self)

- class VectorSettingsModel(ui.AbstractItemModel)
  - def __init__(self, setting_path: str, component_count: int)
  - def get_item_children(self, item)
  - def get_item_value_model(self, item, column_id)
  - def begin_edit(self, item)
  - def set_reset_button(self, button)
  - def end_edit(self, item)
  - def destroy(self)

- class FilePickerDialog
  - def __init__(self, title: str, **kwargs)
  - def set_visibility_changed_listener(self, listener: Callable[[bool], None])
  - def add_connections(self, connections: dict)
  - def set_current_directory(self, path: str)
  - def get_current_directory(self) -> str
  - def get_current_selections(self, pane: int = 2) -> List[str]
  - def set_filename(self, filename: str)
  - def get_filename(self) -> str
  - def get_file_postfix(self) -> str
  - def set_file_postfix(self, postfix: str)
  - def get_file_postfix_options(self) -> List[str]
  - def get_file_extension(self) -> str
  - def set_file_extension(self, extension: str)
  - def get_file_extension_options(self) -> List[Tuple[str, str]]
  - def set_filebar_label_name(self, name: str)
  - def get_filebar_label_name(self) -> str
  - def set_item_filter_fn(self, item_filter_fn: Callable[[str], bool])
  - def set_click_apply_handler(self, click_apply_handler: Callable[[str, str], None])
  - def navigate_to(self, path: str)
  - def toggle_bookmark_from_path(self, name: str, path: str, is_bookmark: bool, is_folder: bool = True)
  - def refresh_current_directory(self)
  - [property] def current_filter_option(self)
  - def add_detail_frame_from_controller(self, name: str, controller: DetailFrameController)
  - def delete_detail_frame(self, name: str)
  - def set_search_delegate(self, delegate)
  - def show_model(self, model: FileBrowserModel)
  - def show(self, path: str = None)
  - def hide(self)
  - def destroy(self)

- class PathPicker
  - def __init__(self, model)
  - def build_ui(self, additional_widget_kwargs = None)

- class AssetPicker
  - def __init__(self, model)
  - def get_icon_path(self) -> Path
  - def on_show_dialog(self, model, item_filter_options)
  - def build_ui(self, additional_widget_kwargs = None)

- class PathOrAssetPicker
  - def get_icon_path(self) -> Path
  - def __init__(self, model)
  - def on_show_dialog(self, model, item_filter_options)
  - def build_ui(self, additional_widget_kwargs = None)

- class XRUIProfileWindowExtension(omni.ext.IExt)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

- class XRProfileSettingsWindow
  - def __init__(self, name: str, ext_name: str, component_list: List[Callable], icons: Union[None, List[str]] = None, show_greeting_dialog: bool = False)
  - def destroy(self)
  - def get_profile(self) -> XRProfile
  - def get_display_name(self) -> str
  - [property] def component_list(self)
  - [property] def icons(self)

## Functions

- def XRWeakMethod(fn: Union[Callable[Ellipsis, Any], Callable[Ellipsis, None]], def_return: Any = None) -> Union[Callable[Ellipsis, Any], Callable[Ellipsis, None]]
- def get_openxr_runtime()
- def get_xcr_capture_filepath()
- def on_capture_button_clicked(is_capture_started: bool, frame: ui.Frame)
- def is_xcr_capture_layer_requested()
- def create_setting_widget(setting_path: str, setting_type: SettingType, range_from = 0, range_to = 0, step = 0.01, **kwargs) -> omni.ui.Widget
- def create_setting_widget_combo(setting_path: str, items: Union[list, dict], **kwargs) -> Tuple[SettingsComboItemModel, omni.ui.ComboBox]
- def get_colors() -> dict
- def get_style()

## Variables

- color: Unknown
- OPENXR_SYSTEM: str
- SIMULATEDXR_SYSTEM: str
- LABEL_HEIGHT: int
- HORIZONTAL_SPACING: int
- LABEL_WIDTH: int

## Other

- omni.kit.app: public module
- carb: public module
- carb.settings: public module
- omni.ui: public module
- pathlib: builtin module
- platform: builtin module
- math: builtin module
- partial: unknown
- carb.dictionary: public module
- omni.kit.commands: public module
- List: unknown
- Union: unknown
- Tuple: unknown
- Path: unknown
- omni.kit.ui: internal module
- omni.usd: public module
- omni.ext: public module
