# Public API for module omni.usd:

## Classes

- class HydraEngineCreationConfig
  - def __init__(self)
  - [property] def creation_index(self) -> int
  - [creation_index.setter] def creation_index(self, arg0: int)
  - [property] def device_mask(self) -> int
  - [device_mask.setter] def device_mask(self, arg0: int)
  - [property] def flags(self) -> EngineCreationFlags
  - [flags.setter] def flags(self, arg0: EngineCreationFlags)
  - [property] def tickrate_in_hz(self) -> int
  - [tickrate_in_hz.setter] def tickrate_in_hz(self, arg0: int)

- class EngineCreationFlags
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - MOTION_RAYTRACING_ENABLED: omni.usd._usd.EngineCreationFlags
  - NONE: omni.usd._usd.EngineCreationFlags
  - SKIP_ON_WORKER_PROCESS: omni.usd._usd.EngineCreationFlags

- class OpaqueSharedHydraEngineContext

- class AudioManager

- class PickingMode
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - INVERT_SELECTION: omni.usd._usd.PickingMode
  - MERGE_SELECTION: omni.usd._usd.PickingMode
  - NONE: omni.usd._usd.PickingMode
  - RESET_AND_SELECT: omni.usd._usd.PickingMode
  - TRACK: omni.usd._usd.PickingMode

- class PrimCaching
  - def __init__(self, usd_type: Any, stage: [Usd.Stage | None] = None, on_changed: Callable[[], None] = None, usd_context_name: [str | None] = None)
  - def destroy(self)
  - def get_cache_state(self) -> bool
  - def set_cache_state(self, state: bool)
  - def get_stage(self) -> Optional[Usd.Stage]

- class Selection
  - class SourceType
    - def __init__(self, value: int)
    - [property] def name(self) -> str
    - [property] def value(self) -> int
    - ALL: omni.usd._usd.Selection.SourceType
    - FABRIC: omni.usd._usd.Selection.SourceType
    - USD: omni.usd._usd.Selection.SourceType
  - def clear_selected_prim_paths(self, source: Selection.SourceType = SourceType.USD) -> bool
  - def get_selected_prim_paths(self, source: Selection.SourceType = SourceType.USD) -> typing.List[str]
  - def is_prim_path_selected(self, path: str, source: Selection.SourceType = SourceType.USD) -> bool
  - def select_all_prims(self, type_names: object = None, type_kind_filtering: bool = False)
  - def select_inverted_prims(self, type_kind_filtering: bool = False)
  - def set_prim_path_selected(self, path: str, selected: bool = True, forcePrim: bool = True, clearSelected: bool = False, expandInStage: bool = True, source: Selection.SourceType = SourceType.USD) -> bool
  - def set_selected_prim_paths(self, paths: typing.List[str], expandInStage: bool = True, source: Selection.SourceType = SourceType.USD, type_kind_filtering: bool = False) -> bool

- class StageEventType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - ACTIVE_LIGHT_COUNTS_CHANGED: omni.usd._usd.StageEventType
  - ANIMATION_START_PLAY: omni.usd._usd.StageEventType
  - ANIMATION_STOP_PLAY: omni.usd._usd.StageEventType
  - ASSETS_LOADED: omni.usd._usd.StageEventType
  - ASSETS_LOADING: omni.usd._usd.StageEventType
  - ASSETS_LOAD_ABORTED: omni.usd._usd.StageEventType
  - CLOSED: omni.usd._usd.StageEventType
  - CLOSING: omni.usd._usd.StageEventType
  - COUNT: omni.usd._usd.StageEventType
  - DIRTY_STATE_CHANGED: omni.usd._usd.StageEventType
  - GIZMO_TRACKING_CHANGED: omni.usd._usd.StageEventType
  - HIERARCHY_CHANGED: omni.usd._usd.StageEventType
  - HYDRA_GEOSTREAMING_STARTED: omni.usd._usd.StageEventType
  - HYDRA_GEOSTREAMING_STOPPED: omni.usd._usd.StageEventType
  - HYDRA_GEOSTREAMING_STOPPED_AT_LIMIT: omni.usd._usd.StageEventType
  - HYDRA_GEOSTREAMING_STOPPED_NOT_ENOUGH_MEM: omni.usd._usd.StageEventType
  - MDL_PARAM_LOADED: omni.usd._usd.StageEventType
  - OMNIGRAPH_START_PLAY: omni.usd._usd.StageEventType
  - OMNIGRAPH_STOP_PLAY: omni.usd._usd.StageEventType
  - OPENED: omni.usd._usd.StageEventType
  - OPENING: omni.usd._usd.StageEventType
  - OPEN_FAILED: omni.usd._usd.StageEventType
  - SAVED: omni.usd._usd.StageEventType
  - SAVE_FAILED: omni.usd._usd.StageEventType
  - SAVING: omni.usd._usd.StageEventType
  - SELECTION_CHANGED: omni.usd._usd.StageEventType
  - SETTINGS_LOADED: omni.usd._usd.StageEventType
  - SETTINGS_SAVING: omni.usd._usd.StageEventType
  - SIMULATION_START_PLAY: omni.usd._usd.StageEventType
  - SIMULATION_STOP_PLAY: omni.usd._usd.StageEventType

- class StageRenderingEventType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - COUNT: omni.usd._usd.StageRenderingEventType
  - HYDRA_ENGINE_FRAMES_ADDED: omni.usd._usd.StageRenderingEventType
  - HYDRA_ENGINE_FRAMES_COMPLETE: omni.usd._usd.StageRenderingEventType
  - NEW_FRAME: omni.usd._usd.StageRenderingEventType
  - RENDERER_RECORDING_COMPLETE: omni.usd._usd.StageRenderingEventType

- class StageState
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - CLOSED: omni.usd._usd.StageState
  - CLOSING: omni.usd._usd.StageState
  - OPENED: omni.usd._usd.StageState
  - OPENING: omni.usd._usd.StageState

- class TransformHelper
  - def __init__(self)
  - def is_transform(self, source_path: str) -> bool
  - def get_transform_attr(self, attrs: List[Usd.Attribute]) -> Tuple[Usd.Attribute, List[Usd.Attribute], Usd.Attribute, Usd.Attribute]
  - def order_attrs(self, attrs, order)
  - def add_to_attr_order(self, attr_order, path, use_placeholder = False)
  - def is_common_attr(self, source_attr)

- class UsdContext
  - def attach_stage_with_callback(self, stage_id: int, on_finish_fn: typing.Callable[[bool, str], None] = None) -> bool
  - def can_close_stage(self) -> bool
  - def can_open_stage(self) -> bool
  - def can_save_stage(self) -> bool
  - def close_stage(self, on_finish_fn: typing.Callable[[bool, str], None] = None) -> bool
  - def close_stage_with_callback(self, on_finish_fn: typing.Callable[[bool, str], None]) -> bool
  - def compute_path_world_bounding_box(self, arg0: str) -> typing.Tuple[carb._carb.Double3, carb._carb.Double3]
  - def compute_path_world_transform(self, arg0: str) -> typing.Annotated[typing.List[float], pybind11_stubgen.typing_ext.FixedSize(16)]
  - def disable_save_to_recent_files(self)
  - def enable_save_to_recent_files(self)
  - def export_as_stage(self, url: str, on_finish_fn: typing.Callable[[bool, str], None] = None) -> bool
  - def export_as_stage_with_callback(self, url: str, on_finish_fn: typing.Callable[[bool, str], None]) -> bool
  - def get_attached_hydra_engine_description(self, arg0: int) -> HydraEngineDesc
  - def get_attached_hydra_engine_names(self) -> typing.List[str]
  - def get_attached_hydra_engine_uids(self) -> typing.List[int]
  - def get_geometry_instance_path(self, arg0: int) -> str
  - def get_name(self) -> str
  - def get_rendering_event_stream(self) -> carb.events._events.IEventStream
  - static def get_selection(*args, **kwargs) -> typing.Any
  - def get_stage_audio_manager(self) -> AudioManager
  - def get_stage_event_stream(self) -> carb.events._events.IEventStream
  - def get_stage_id(self) -> int
  - def get_stage_loading_status(self) -> typing.Tuple[str, int, int]
  - def get_stage_state(self) -> StageState
  - def get_stage_streaming_status(self) -> bool
  - def get_stage_url(self) -> str
  - def get_timeline(self) -> omni.timeline._timeline.Timeline
  - def get_timeline_name(self) -> str
  - def has_pending_edit(self) -> bool
  - def is_new_stage(self) -> bool
  - def is_omni_stage(self) -> bool
  - def is_writable(self) -> bool
  - def load_render_settings_from_stage(self, arg0: int)
  - def manual_update(self, dt: float) -> bool
  - def open_stage(self, url: str, on_finish_fn: typing.Callable[[bool, str], None] = None, load_set: UsdContextInitialLoadSet = UsdContextInitialLoadSet.LOAD_ALL) -> bool
  - def open_stage_with_callback(self, url: str, on_finish_fn: typing.Callable[[bool, str], None], load_set: UsdContextInitialLoadSet = UsdContextInitialLoadSet.LOAD_ALL) -> bool
  - def open_stage_with_session_layer(self, url: str, session_layer_url: str, on_finish_fn: typing.Callable[[bool, str], None], load_set: UsdContextInitialLoadSet = UsdContextInitialLoadSet.LOAD_ALL) -> bool
  - def register_selection_group(self) -> int
  - def remove_all_hydra_engines(self)
  - def reopen_stage(self, on_finish_fn: typing.Callable[[bool, str], None] = None, load_set: UsdContextInitialLoadSet = UsdContextInitialLoadSet.LOAD_ALL) -> bool
  - def reopen_stage_with_callback(self, on_finish_fn: typing.Callable[[bool, str], None], load_set: UsdContextInitialLoadSet = UsdContextInitialLoadSet.LOAD_ALL) -> bool
  - def reset_renderer_accumulation(self)
  - def save_as_stage(self, url: str, on_finish_fn: typing.Callable[[bool, str, typing.List[str]], None] = None) -> bool
  - def save_as_stage_with_callback(self, url: str, on_finish_fn: typing.Callable[[bool, str, typing.List[str]], None]) -> bool
  - def save_layers(self, new_root_layer_path: str, layer_identifiers: typing.List[str], on_finish_fn: typing.Callable[[bool, str, typing.List[str]], None] = None) -> bool
  - def save_layers_with_callback(self, new_root_layer_path: str, layer_identifiers: typing.List[str], on_finish_fn: typing.Callable[[bool, str, typing.List[str]], None]) -> bool
  - def save_render_settings_to_current_stage(self)
  - def save_stage(self, on_finish_fn: typing.Callable[[bool, str, typing.List[str]], None] = None) -> bool
  - def save_stage_with_callback(self, on_finish_fn: typing.Callable[[bool, str, typing.List[str]], None]) -> bool
  - def set_pending_edit(self, arg0: bool)
  - def set_pickable(self, arg0: str, arg1: bool)
  - def set_selection_group(self, groupId: int, path: str)
  - def set_selection_group_outline_color(self, groupId: int, color: carb._carb.Float4)
  - def set_selection_group_shade_color(self, groupId: int, color: carb._carb.Float4)
  - def set_timeline(self, name: str = '')
  - def stage_event_name(self, event: StageEventType) -> str
  - def stage_event_type(self, event: str) -> StageEventType
  - def stage_rendering_event_name(self, event: StageRenderingEventType, immediate: bool = False) -> str
  - def stage_rendering_event_type(self, event: str) -> StageRenderingEventType
  - def try_cancel_save(self)
  - def updated_hydra_engine_device_mask(self, arg0: int, arg1: int) -> bool

- class UsdContextInitialLoadSet
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - LOAD_ALL: omni.usd._usd.UsdContextInitialLoadSet
  - LOAD_NONE: omni.usd._usd.UsdContextInitialLoadSet

- class UsdWatcher
  - def __init__(self)
  - def destroy(self)
  - def subscribe_to_resync_path(self, path: Sdf.Path, on_change: typing.Callable) -> carb.Subscription
  - def subscribe_to_change_info_path(self, path: Sdf.Path, on_change: typing.Callable) -> carb.Subscription

- class Value_On_Layer(Enum)
  - No_Value: int
  - ON_CURRENT_LAYER: int
  - ON_STRONGER_LAYER: int
  - ON_WEAKER_LAYER: int

## Functions

- def create_hydra_engine(name: str, context: UsdContext) -> int
- def destroy_hydra_engine(uid: int) -> bool
- def attach_all_hydra_engines(context: UsdContext)
- def attr_has_timesample_on_key(attr: Usd.Attribute, time_code: Usd.TimeCode)
- def can_be_copied(prim)
- def can_prim_have_children(stage: Usd.Stage, new_path: Sdf.Path, prim: Usd.Prim)
- def check_ancestral(prim: Usd.Prim) -> bool
- def clear_attr_val_at_time(attr: Usd.Attribute, time_code = Usd.TimeCode.Default(), auto_target_layer: bool = True)
- def copy_timesamples_from_weaker_layer(stage, attr: Usd.Attribute)
- def create_context(name: str = '') -> UsdContext
- def create_material_input(prim: Usd.Prim, name: str, value: Any, vtype: str, def_value: Any = None, min_value: Any = None, max_value: Any = None, display_name: str = None, display_group: str = None, color_space: str = None) -> Usd.Attribute
- def destroy_context(name: str = '') -> bool
- def duplicate_prim(stage: Usd.Stage, prim_path: Union[str, Sdf.Path], path_to: Union[str, Sdf.Path], duplicate_layers: bool = True)
- def find_path_in_nodes(node, set_fn)
- def find_spec_on_session_or_its_sublayers(stage: Usd.Stage, path: Sdf.Path, predicate: Callable[[Sdf.Spec], bool] = None)
- def get_all_sublayers(stage, include_session_layers = False, include_only_omni_layers = False, include_anonymous_layers = True) -> List[str]
- def get_attribute_effective_defaultvalue_layer_info(stage, attr: Usd.Attribute)
- def get_attribute_effective_timesample_layer_info(stage, attr: Usd.Attribute)
- def get_attribute_effective_value_layer_info(stage, attr: Usd.Attribute)
- def get_authored_prim(prim)
- def get_composed_payloads_from_prim(prim: Usd.Prim, fix_slashes: bool = True) -> List[Tuple[Sdf.Payload, Sdf.Layer]]
- def get_composed_references_from_prim(prim: Usd.Prim, fix_slashes: bool = True) -> List[Tuple[Sdf.Reference, Sdf.Layer]]
- def get_context(name: str = '') -> UsdContext
- def get_dirty_layers(stage: Usd.Stage, include_root_layer = True)
- def get_edit_target_identifier(stage: Usd.Stage) -> str
- def get_frame_time(time_code, fps)
- def get_frame_time_code(time, fps)
- def get_introducing_layer(prim: Usd.Prim) -> Tuple[Sdf.Layer, Sdf.Path]
- def get_local_transform_SRT(prim, time = Usd.TimeCode.Default()) -> Tuple[Gf.Vec3d | Gf.Vec3f | Gf.Vec3h, Gf.Vec3d | Gf.Vec3f | Gf.Vec3h, Gf.Vec3i, Gf.Vec3d | Gf.Vec3f | Gf.Vec3h]
- def get_local_transform_matrix(prim: Usd.Prim, time_code: Usd.TimeCode = Usd.TimeCode.Default()) -> Gf.Matrix4d
- def get_prim_at_path(path: Sdf.Path, usd_context_name: Union[str, Usd.Stage] = '') -> Usd.Prim
- def get_prim_descendents(root_prim: Usd.Prim) -> List[Usd.Prim]
- def get_prop_at_path(path: Sdf.Path, usd_context_name: Union[str, Usd.Stage] = '') -> Usd.Property
- def get_sdf_layer(prim)
- def get_shader_from_material(prim, get_prim = False)
- def get_stage_next_free_path(stage: Usd.Stage, path: Union[str, Sdf.Path], prepend_default_prim: bool, source_prim: Optional[Usd.Prim] = None)
- async def get_subidentifier_from_material(prim: Usd.Prim, on_complete_fn: typing.Callable = None)
- async def get_subidentifier_from_mdl(mdl_file: str, on_complete_fn: typing.Callable = None)
- def get_timesamples_count_in_authoring_layer(stage, attr_path: Sdf.Path)
- def get_url_from_prim(prim)
- def get_watcher()
- def get_world_transform_matrix(prim: Usd.Prim, time_code: Usd.TimeCode = Usd.TimeCode.Default()) -> Gf.Matrix4d
- def handle_exception(func)
- def is_ancestor_prim_type(stage: Usd.Stage, prim_path: Sdf.Path, prim_type: Usd.SchemaBase)
- def is_child_type(prim, type)
- def is_hidden_type(prim: Usd.Prim)
- def is_layer_locked(usd_context, layer_identifier: str) -> bool
- def is_layer_writable(layer_identifier: str) -> bool
- def is_path_valid(path: Union[str, Sdf.Path])
- def is_prim_material_supported(prim)
- def is_usd_readable_filetype(filepath: str) -> bool
- def is_usd_writable_filetype(filepath: str) -> bool
- def make_path_relative_to_current_edit_target(url_path: str, stage: Usd.Stage = None) -> str
- def merge_layers(dst_layer_identifier: str, src_layer_identifier: str, dst_is_stronger_than_src: bool = True, src_layer_offset: float = 0.0, src_layer_scale: float = 1.0) -> bool
- def merge_prim_spec(dst_layer_identifier: str, src_layer_identifier: str, prim_spec_path: str, dst_is_stronger_than_src: bool = True, target_prim_path: str = '')
- def on_layers_saved_result(result: bool, err_msg: str, saved_layers: List[str], future: asyncio.Future)
- def on_stage_result(result: bool, err_msg: str, future: asyncio.Future)
- def readable_usd_dotted_file_exts() -> List[str]
- def readable_usd_file_exts() -> List[str]
- def readable_usd_file_exts_str() -> str
- def readable_usd_files_desc() -> str
- def readable_usd_re() -> re.Pattern
- def release_all_hydra_engines(context: UsdContext = None)
- def remove_property(prim_path: Union[str, Sdf.Path], property_name: str, usd_context_or_stage: Union[str, Usd.Stage] = '')
- def resolve_paths(src_layer_identifier: str, dst_layer_identifier: str, store_relative_path: bool = True, relative_to_src_layer: bool = False, copy_sublayer_offsets: bool = False)
- def resolve_prim_path_references(layer: str, old_prim_path: str, new_prim_path: str)
- def resolve_prim_paths_references(layer: str, old_prim_paths: typing.List[str], new_prim_paths: typing.List[str])
- def set_attr_val(attr: Usd.Attribute, val: typing.Any, time_code = Usd.TimeCode.Default(), auto_target_layer: bool = True)
- def set_edit_target_by_identifier(stage: Usd.Stage, layer_identifier: str)
- def set_prop_val(prop: Usd.Property, val: typing.Any, time_code = Usd.TimeCode.Default(), auto_target_layer: bool = True)
- def shutdown_usd()
- def stitch_prim_specs(stage: Usd.Stage, prim_path: Union[str, Sdf.Path], target_layer: Sdf.Layer, target_prim_path: str = None, include_references_or_payloads = False)
- def writable_usd_dotted_file_exts() -> List[str]
- def writable_usd_file_exts() -> List[str]
- def writable_usd_file_exts_str() -> str
- def writable_usd_files_desc() -> str
- def writable_usd_re() -> re.Pattern
- def get_context_from_stage(stage)
- def get_context_from_stage_id(stage_id: int) -> UsdContext
- def correct_filename_case(file: str) -> str
- def gather_default_attributes(prim_type)
- def get_prop_auto_target_session_layer(stage: Usd.Stage, prop_path: Sdf.Path)
- def get_geometry_standard_prim_list(usd_context = None)
- def get_light_prim_list(usd_context = None)
- def make_valid_identifier(*args, **kwargs) -> typing.Any
- def create_hydra_engine_with_config(name: str, context: UsdContext, configuration: HydraEngineCreationConfig) -> int
- def add_hydra_engine(name: str, context: UsdContext) -> int
- def is_usd_crate_file(filepath: str) -> bool
- def is_usd_crate_file_version_supported(filepath: str, stage = None, usd_context_name: str = '') -> bool
- def stage_event_type(event: str) -> StageEventType
- def stage_rendering_event_type(event: str) -> StageRenderingEventType

## Variables

- HydraEngineInvalidUniqueId: int

# Public API for module omni.usd.audio:

## Classes

- class AssetLoadStatus
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - DONE: omni.usd.audio._audio.AssetLoadStatus
  - FAILED: omni.usd.audio._audio.AssetLoadStatus
  - IN_PROGRESS: omni.usd.audio._audio.AssetLoadStatus
  - NOT_REGISTERED: omni.usd.audio._audio.AssetLoadStatus

- class EventType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - ACTIVE_LISTENER_CHANGE: omni.usd.audio._audio.EventType
  - LISTENER_LIST_CHANGE: omni.usd.audio._audio.EventType
  - METADATA_CHANGE: omni.usd.audio._audio.EventType

- class FeatureDefault
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - FORCE_OFF: omni.usd.audio._audio.FeatureDefault
  - FORCE_ON: omni.usd.audio._audio.FeatureDefault
  - OFF: omni.usd.audio._audio.FeatureDefault
  - ON: omni.usd.audio._audio.FeatureDefault

- class SoundLengthType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - ASSET_LENGTH: omni.usd.audio._audio.SoundLengthType
  - PLAY_LENGTH: omni.usd.audio._audio.SoundLengthType
  - SOUND_LENGTH: omni.usd.audio._audio.SoundLengthType

- class StreamListener
  - def __init__(self, p: carb.events._events.IEventStream, open: typing.Callable[[carb.audio.audio.SoundFormat], None], writeData: typing.Callable[[list], None], close: typing.Callable[[], None])

- class IStageAudio
  - mgr: NoneType
  - INVALID_STREAMER_ID: Unknown
  - def __init__(self)
  - def has_audio(self)
  - def get_sound_count(self)
  - def play_sound(self, prim)
  - def is_sound_playing(self, prim)
  - def stop_sound(self, prim)
  - def get_sound_length(self, prim, length_type = SoundLengthType.PLAY_LENGTH)
  - def stop_all_sounds(self)
  - def spawn_voice(self, prim)
  - def get_sound_asset_status(self, prim)
  - def subscribe_to_asset_load(self, prim, callback)
  - def set_active_listener(self, prim)
  - def get_active_listener(self)
  - def get_listener_count(self)
  - def get_listener_by_index(self, index)
  - def set_doppler_default(self, value = FeatureDefault.OFF)
  - def get_doppler_default(self)
  - def set_distance_delay_default(self, value = FeatureDefault.OFF)
  - def get_distance_delay_default(self)
  - def set_interaural_delay_default(self, value = FeatureDefault.OFF)
  - def get_interaural_delay_default(self)
  - def set_concurrent_voices(self, value = 64)
  - def get_concurrent_voices(self)
  - def set_speed_of_sound(self, value = carb.audio.DEFAULT_SPEED_OF_SOUND)
  - def get_speed_of_sound(self)
  - def set_doppler_scale(self, value = 1.0)
  - def get_doppler_scale(self)
  - def set_doppler_limit(self, value = 2.0)
  - def get_doppler_limit(self)
  - def set_spatial_time_scale(self, value = 1.0)
  - def get_spatial_time_scale(self)
  - def set_nonspatial_time_scale(self, value = 1.0)
  - def get_nonspatial_time_scale(self)
  - def set_device(self, deviceName)
  - def create_capture_streamer(self)
  - def destroy_capture_streamer(self, id)
  - def set_capture_filename(self, id, filename)
  - def create_event_stream_for_capture(self, id)
  - def start_capture(self, id, filename = None)
  - def start_captures(self, ids)
  - def stop_capture(self, id)
  - def stop_captures(self, ids)
  - def wait_for_capture(self, id, timeout_milliseconds)
  - def get_metadata_change_stream(self)
  - def draw_waveform(self, prim, width, height, flags = carb.audio.AUDIO_IMAGE_FLAG_USE_LINES | carb.audio.AUDIO_IMAGE_FLAG_SPLIT_CHANNELS, channel = 0, background = [0, 0, 0, 1.0], colors = [])

## Functions

- def test_hydra_plugin() -> bool
- def get_stage_audio_interface() -> IStageAudio

## Variables

- INVALID_STREAMER_ID: int

# Public API for module omni.usd.commands:

## Classes

- class GroupPrimsCommand(omni.kit.commands.Command, UsdStageHelper)
  - def __init__(self, prim_paths: List[Union[str, Sdf.Path]], stage: Optional[Usd.Stage] = None, context_name: Optional[str] = None, destructive = True)
  - def do(self)
  - def undo(self)

- class UngroupPrimsCommand(omni.kit.commands.Command, UsdStageHelper)
  - class ExitCode(Enum)
    - Success: Unknown
    - NoParent: Unknown
  - def __init__(self, prim_paths: List[Union[str, Sdf.Path]], stage: Optional[Usd.Stage] = None, context_name: Optional[str] = None, destructive = True)
  - def do(self)
  - def undo(self)

- class CreatePrimWithDefaultXformCommand(omni.kit.commands.Command, UsdStageHelper)
  - def __init__(self, prim_type: str, prim_path: str = None, select_new_prim: bool = True, attributes: Dict[str, Any] = {}, create_default_xform = True, stage: Optional[Usd.Stage] = None, context_name: Optional[str] = None)
  - def do(self)
  - def undo(self)

- class CreatePrimCommand(CreatePrimWithDefaultXformCommand)
  - def __init__(self, prim_type: str, prim_path: str = None, select_new_prim: bool = True, attributes: Dict[str, Any] = {}, create_default_xform = True, stage: Optional[Usd.Stage] = None, context_name: Optional[str] = None)

- class CopyPrimCommand(omni.kit.commands.Command)
  - def __init__(self, path_from: str, path_to: str = None, duplicate_layers: bool = False, combine_layers: bool = False, exclusive_select: bool = True, usd_context_name: str = '', flatten_references: bool = False, copy_to_introducing_layer: bool = False)
  - def do(self)
  - def undo(self)
  - def modify_callback_info(self, cb_type: str, cmd_args: Dict[str, Any]) -> Dict[str, Any]

- class CopyPrimsCommand(omni.kit.commands.Command)
  - def __init__(self, paths_from: List[str], paths_to: List[str] = None, duplicate_layers: bool = False, combine_layers: bool = False, flatten_references: bool = False, copy_to_introducing_layer: bool = False)
  - def do(self)
  - def undo(self)

- class CreateInstanceCommand(omni.kit.commands.Command)
  - def __init__(self, path_from: str)
  - def do(self)
  - def undo(self)

- class CreateInstancesCommand(omni.kit.commands.Command)
  - def __init__(self, paths_from: List[str])
  - def do(self)
  - def undo(self)

- class DeletePrimsCommand(omni.kit.commands.Command, UsdStageHelper)
  - def __init__(self, paths: List[Union[str, Sdf.Path]], destructive = True, stage: Optional[Usd.Stage] = None, context_name: Optional[str] = None)
  - def do(self)
  - def undo(self)

- class CreatePrimsCommand(omni.kit.commands.Command)
  - def __init__(self, prim_types: List[str], usd_context_name: Optional[str] = None)
  - def do(self)
  - def undo(self)

- class CreateDefaultXformOnPrimCommand(omni.kit.commands.Command)
  - def __init__(self, prim_path: str, stage: Usd.Stage)
  - def do(self)
  - def undo(self)

- class BindMaterialCommand(omni.kit.commands.Command, UsdStageHelper)
  - def __init__(self, prim_path: Union[str, list], material_path: str, strength = None, stage: Optional[Usd.Stage] = None, context_name: Optional[str] = None, material_purpose: Optional[str] = UsdShade.Tokens.allPurpose)
  - class PathType(Enum)
    - Prim: Unknown
    - Collection: Unknown
    - Neither: Unknown
  - def do(self)
  - def undo(self)

- class SetMaterialStrengthCommand(omni.kit.commands.Command)
  - def __init__(self, rel, strength)
  - def do(self)
  - def undo(self)

- class TransformPrimCommand(omni.kit.commands.Command)
  - def __init__(self, path: str, new_transform_matrix: Gf.Matrix4d, old_transform_matrix: Gf.Matrix4d = None, time_code: Usd.TimeCode = Usd.TimeCode.Default(), had_transform_at_key: bool = False, usd_context_name: str = '')
  - def do(self)
  - def undo(self)

- class TransformPrimSRTCommand(omni.kit.commands.Command)
  - def __init__(self, path: str, new_translation: Gf.Vec3d = None, new_rotation_euler: Gf.Vec3d = None, new_scale: Gf.Vec3d = None, new_rotation_order: Gf.Vec3i = None, old_translation: Gf.Vec3d = None, old_rotation_euler: Gf.Vec3d = None, old_rotation_order: Gf.Vec3i = None, old_scale: Gf.Vec3d = None, time_code: Usd.TimeCode = Usd.TimeCode.Default(), had_transform_at_key: bool = False, usd_context_name: str = '')
  - def do(self)
  - def undo(self)

- class TransformPrimsCommand(omni.kit.commands.Command)
  - def __init__(self, prims_to_transform: List[Tuple[str, Gf.Matrix4d, Gf.Matrix4d, Usd.TimeCode]])
  - def do(self)
  - def undo(self)

- class TransformPrimsSRTCommand(omni.kit.commands.Command)
  - def __init__(self, prims_to_transform: List[Tuple[str, Gf.Vec3d, Gf.Vec3d, Gf.Vec3i, Gf.Vec3d, Gf.Vec3d, Gf.Vec3d, Gf.Vec3i, Gf.Vec3d, Usd.TimeCode, bool]])
  - def do(self)
  - def undo(self)

- class FramePrimsCommand(omni.kit.commands.Command)
  - def __init__(self, prim_to_move: Union[str, Sdf.Path], prims_to_frame: Optional[Sequence[Union[str, Sdf.Path]]] = None, time_code: Usd.TimeCode = Usd.TimeCode.Default(), usd_context_name: str = '', aspect_ratio: float = 1, use_horizontal_fov: bool = None, zoom: float = 0.45, horizontal_fov: float = 0.20656116130367255)
  - def do(self)
  - def undo(self)

- class SelectPrimsCommand(omni.kit.commands.Command)
  - def __init__(self, old_selected_paths: List[str], new_selected_paths: List[str], expand_in_stage: bool = True, source: omni.usd.Selection.SourceType = omni.usd.Selection.SourceType.USD)
  - def do(self)
  - def undo(self)

- class ToggleVisibilitySelectedPrimsCommand(omni.kit.commands.Command)
  - def __init__(self, selected_paths: List[str], stage: Optional[Usd.Stage] = None, visible: Optional[bool] = None)
  - def do(self)
  - def undo(self)

- class UnhideAllPrimsCommand(omni.kit.commands.Command)
  - def do(self)
  - def undo(self)

- class MovePrimCommand(omni.kit.commands.Command)
  - def __init__(self, path_from: Union[str, Sdf.Path], path_to: Union[str, Sdf.Path], time_code: Usd.TimeCode = Usd.TimeCode.Default(), keep_world_transform: bool = True, on_move_fn: Callable[[Sdf.Path, Sdf.Path], None] = None, destructive = True, stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None, resolve_reference: bool = True)
  - def modify_callback_info(self, cb_type: str, cmd_args: Dict[str, Any]) -> Dict[str, Any]
  - class RenameHandler
    - def __init__(self, old_path: Sdf.Path)
    - def apply_change(self, old_path: Sdf.Path, new_path: Sdf.Path)
  - def do(self)
  - def undo(self)

- class MovePrimsCommand(omni.kit.commands.Command)
  - def __init__(self, paths_to_move: Dict[str, str], time_code: Usd.TimeCode = Usd.TimeCode.Default(), keep_world_transform: bool = True, on_move_fn: Callable = None, destructive = True, stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None)
  - def do(self)
  - def undo(self)

- class RenamePrimCommand(omni.kit.commands.Command)
  - def __init__(self, prim_path: str, new_name: str)
  - def do(self)
  - def undo(self)

- class ReplaceReferencesCommand(omni.kit.commands.Command)
  - def __init__(self, path: str, old_url: str, new_url: str)
  - def do(self)
  - def undo(self)

- class CreateUsdAttributeOnPathCommand(omni.kit.commands.Command)
  - def __init__(self, attr_path: Union[Sdf.Path, str], attr_type: Sdf.ValueTypeName, custom: bool = True, variability: Sdf.Variability = Sdf.VariabilityVarying, attr_value: Any = None, usd_context_name: str = '')
  - def do(self)
  - def undo(self)

- class CreateUsdAttributeCommand(omni.kit.commands.Command)
  - def __init__(self, prim: Usd.Prim, attr_name: str, attr_type: Sdf.ValueTypeName, custom: bool = True, variability: Sdf.Variability = Sdf.VariabilityVarying, attr_value: Any = None)
  - def do(self)
  - def undo(self)

- class ChangePropertyCommand(omni.kit.commands.Command)
  - overriden_notification: NoneType
  - def __init__(self, prop_path: str, value: Any, prev: Any, timecode = Usd.TimeCode.Default(), type_to_create_if_not_exist: Sdf.ValueTypeNames = None, target_layer: Sdf.Layer = None, usd_context_name: Union[str, omni.usd.UsdContext, Usd.Stage] = '', is_custom: bool = False, variability: Sdf.Variability = Sdf.VariabilityVarying)
  - def do(self)
  - def undo(self)

- class RemovePropertyCommand(omni.kit.commands.Command)
  - def __init__(self, prop_path: Union[Sdf.Path, str], usd_context_name: Union[str, Usd.Stage] = '', remove_from_layers: Optional[Union[List[Union[str, Sdf.Layer]], str, Sdf.Layer]] = None)
  - def do(self)
  - def undo(self)

- class ChangeMetadataInPrimsCommand(omni.kit.commands.Command)
  - def __init__(self, prim_paths: List[str], key: Any, value: Any, usd_context_name: str = '')
  - def do(self)
  - def undo(self)

- class ChangeMetadataCommand(omni.kit.commands.Command)
  - def __init__(self, object_paths: List[str], key: Any, value: Any, usd_context_name: str = '')
  - def do(self)
  - def undo(self)

- class ChangeAttributesColorSpaceCommand(omni.kit.commands.Command)
  - def __init__(self, attributes: List[Usd.Attribute], color_space: Any)
  - def do(self)
  - def undo(self)

- class CreateMdlMaterialPrimCommand(omni.kit.commands.Command, UsdStageHelper)
  - def __init__(self, mtl_url: str, mtl_name: str, mtl_path: str, select_new_prim: bool = False, stage: Optional[Usd.Stage] = None, context_name: Optional[str] = None)
  - def do(self)
  - def undo(self)

- class CreateMtlxMaterialPrimCommand(omni.kit.commands.Command, UsdStageHelper)
  - def __init__(self, mtlx_url: str, base_path: str, select_new_prim: bool = False, stage: Optional[Usd.Stage] = None, context_name: Optional[str] = None)
  - def do(self)
  - def undo(self)

- class CreateShaderPrimFromSdrCommand(omni.kit.commands.Command)
  - def __init__(self, parent_path: str, identifier: str, name: str = None, select_new_prim: bool = False, stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None, node_type = 'mdl')
  - def do(self)
  - def undo(self)

- class CreatePreviewSurfaceMaterialPrimCommand(omni.kit.commands.Command)
  - def __init__(self, mtl_path: str, shader_prim_name = 'Shader', select_new_prim: bool = False)
  - def do(self)
  - def undo(self)

- class CreatePreviewSurfaceTextureMaterialPrimCommand(omni.kit.commands.Command)
  - def __init__(self, mtl_path: Union[str, Sdf.Path], select_new_prim: bool = False)
  - def do(self)
  - def undo(self)

- class ClearCurvesSplitsOverridesCommand(omni.kit.commands.Command)
  - def do(self)

- class ClearRefinementOverridesCommand(omni.kit.commands.Command)
  - def __init__(self)
  - def do(self)
  - def undo(self)

- class RelationshipTargetBase(omni.kit.commands.Command)
  - def __init__(self, relationship: Usd.Relationship, target: Sdf.Path)
  - def undo(self)

- class AddRelationshipTargetCommand(RelationshipTargetBase)
  - def __init__(self, relationship: Usd.Relationship, target: Sdf.Path, position: Usd.ListPosition = Usd.ListPositionBackOfPrependList)
  - def do(self)

- class RemoveRelationshipTargetCommand(RelationshipTargetBase)
  - def __init__(self, relationship: Usd.Relationship, target: Sdf.Path)
  - def do(self)

- class SetRelationshipTargetsCommand(RelationshipTargetBase)
  - def __init__(self, relationship: Usd.Relationship, targets: List[Sdf.Path])
  - def do(self)

- class ReferenceCommandBase(omni.kit.commands.Command)
  - def __init__(self, stage, prim_path: Sdf.Path, reference: Sdf.Reference)
  - def undo(self)

- class AddReferenceCommand(ReferenceCommandBase)
  - def __init__(self, stage: Usd.Stage, prim_path: Sdf.Path, reference: Sdf.Reference, position: Usd.ListPosition = Usd.ListPositionBackOfPrependList)
  - def do(self)

- class RemoveReferenceCommand(ReferenceCommandBase)
  - def __init__(self, stage: Usd.Stage, prim_path: Sdf.Path, reference: Sdf.Reference)
  - def do(self)

- class ReplaceReferenceCommand(ReferenceCommandBase)
  - def __init__(self, stage: Usd.Stage, prim_path: Sdf.Path, old_reference: Sdf.Reference, new_reference: Sdf.Reference)
  - def do(self)

- class PayloadCommandBase(omni.kit.commands.Command)
  - def __init__(self, stage, prim_path: Sdf.Path, payload: Sdf.Payload)
  - def undo(self)

- class AddPayloadCommand(PayloadCommandBase)
  - def __init__(self, stage: Usd.Stage, prim_path: Sdf.Path, payload: Sdf.Payload, position = Usd.ListPositionBackOfPrependList)
  - def do(self)

- class RemovePayloadCommand(PayloadCommandBase)
  - def __init__(self, stage, prim_path: Sdf.Path, payload: Sdf.Payload)
  - def do(self)

- class ReplacePayloadCommand(PayloadCommandBase)
  - def __init__(self, stage, prim_path: Sdf.Path, old_payload: Sdf.Payload, new_payload: Sdf.Payload)
  - def do(self)

- class CreatePrimCommandBase(omni.kit.commands.Command)
  - def __init__(self, usd_context: omni.usd.UsdContext, path_to: Sdf.Path, asset_path: str, select_prim: bool = True)
  - def do(self)
  - def undo(self)

- class CreateReferenceCommand(CreatePrimCommandBase)
  - def __init__(self, usd_context: omni.usd.UsdContext, path_to: Sdf.Path, asset_path: str = None, prim_path: Sdf.Path = None, instanceable: bool = True, select_prim: bool = True)
  - def do(self)
  - def undo(self)

- class CreatePayloadCommand(CreatePrimCommandBase)
  - def __init__(self, usd_context: omni.usd.UsdContext, path_to: Sdf.Path, asset_path: str = None, prim_path: Sdf.Path = None, instanceable: bool = True, select_prim: bool = True)
  - def do(self)
  - def undo(self)

- class CreateAudioPrimFromAssetPathCommand(CreatePrimCommandBase)
  - def __init__(self, usd_context: omni.usd.UsdContext, path_to: Sdf.Path, asset_path: str, select_prim: bool = True)
  - def do(self)

- class ToggleActivePrimsCommand(omni.kit.commands.Command)
  - def __init__(self, prim_paths: List[Sdf.Path], stage_or_context: Union[Usd.Stage, str, omni.usd.UsdContext] = None, active: Union[bool, None] = None)
  - def do(self)
  - def undo(self)

- class UsdStageHelper
  - def __init__(self, stage: Optional[Usd.Stage] = None, context_name: Optional[str] = None)

- class TogglePayLoadLoadSelectedPrimsCommand(omni.kit.commands.Command)
  - def __init__(self, selected_paths: List[str], stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None)
  - def do(self)
  - def undo(self)

- class SetPayLoadLoadSelectedPrimsCommand(omni.kit.commands.Command)
  - def __init__(self, selected_paths: List[str], value: bool, stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None)
  - def do(self)
  - def undo(self)

- class ParentPrimsCommand(omni.kit.commands.Command)
  - def __init__(self, parent_path: str, child_paths: List[str], on_move_fn: callable = None, keep_world_transform: bool = True, stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None)
  - def do(self)
  - def undo(self)

- class UnparentPrimsCommand(omni.kit.commands.Command)
  - def __init__(self, paths: List[str], on_move_fn: callable = None, keep_world_transform: bool = True, stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None)
  - def do(self)
  - def undo(self)

- class AppendAPIToPrimsCommand(omni.kit.commands.Command)
  - def __init__(self, paths: List[str], api_schema: str, api_instance: str = '', stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None)
  - def do(self)
  - def undo(self)

- class RemoveAPIFromPrimsCommand(omni.kit.commands.Command)
  - def __init__(self, paths: List[str], api_schema: str, api_instance: str = '', stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None)
  - def do(self)
  - def undo(self)

## Functions

- def post_notification(message: str, info: bool = False, duration: int = 3)
- def active_edit_context(usd_context_or_stage)
- def remove_prim_spec(layer: Sdf.Layer, prim_spec_path: str)
- def prim_can_be_removed_without_destruction(usd_context_or_stage, prim_path)
- def write_refinement_override_enabled_hint(stage)
- def get_default_rotation_order_str()
- def get_default_camera_rotation_order_str()
- def get_default_rotation_order_type(is_camera: bool = False)
- def ensure_parents_are_active(stage, path)

# Public API for module omni.usd.editor:

## Functions

- def set_hide_in_stage_window(prim: Usd.Prim, hide: bool)
- def is_hide_in_stage_window(prim: Usd.Prim) -> bool
- def set_no_delete(prim: Usd.Prim, no_delete: bool)
- def is_no_delete(prim: Usd.Prim) -> bool
- def set_always_pick_model(prim: Usd.Prim, pick_model: bool)
- def is_always_pick_model(prim: Usd.Prim) -> bool
- def set_hide_in_ui(prim: Usd.Prim, value: bool)
- def is_hide_in_ui(prim: Usd.Prim) -> bool
- def set_display_name(prim: Usd.Prim, name: str)
- def get_display_name(prim) -> str

## Variables

- HIDE_IN_STAGE_WINDOW: str
- NO_DELETE: str
- ALWAYS_PICK_MODEL: str
- DISPLAY_NAME: str

# Public API for module omni.stageupdate:

## Classes

- class IStageUpdate
  - def destroy_stage_update(self, name: str) -> bool
  - def get_stage_update(self, name: str = '') -> StageUpdate

- class StageUpdate
  - def create_stage_update_node(self, display_name: str, on_attach_fn: typing.Callable[[int, float], None] = None, on_detach_fn: typing.Callable[[], None] = None, on_update_fn: typing.Callable[[float, float], None] = None, on_prim_add_fn: typing.Callable[[str], None] = None, on_prim_or_property_change_fn: typing.Callable[[str], None] = None, on_prim_remove_fn: typing.Callable[[str], None] = None, on_raycast_fn: typing.Callable[[carb._carb.Float3, carb._carb.Float3, bool], None] = None) -> StageUpdateNode
  - def get_stage_update_nodes(self) -> tuple
  - def set_stage_update_node_enabled(self, index: int, enabled: bool)
  - def set_stage_update_node_order(self, index: int, order: int)
  - def subscribe_to_stage_update_node_change_events(self, fn: typing.Callable[[], None]) -> carb._carb.Subscription

- class StageUpdateNode

## Functions

- def acquire_stage_update_interface(plugin_name: str = None, library_path: str = None) -> IStageUpdate
- def get_stage_update_interface(name: str = '') -> StageUpdate

# Public API for module usd.schema.kit:

No public API
