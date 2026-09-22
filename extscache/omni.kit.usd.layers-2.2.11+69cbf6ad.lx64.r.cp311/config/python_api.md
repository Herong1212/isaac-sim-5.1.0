# Public API for module omni.kit.usd.layers:

## Classes

- class LayerEditMode
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - AUTO_AUTHORING: omni.kit.usd.layers._omni_kit_usd_layers.LayerEditMode
  - NORMAL: omni.kit.usd.layers._omni_kit_usd_layers.LayerEditMode
  - SPECS_LINKING: omni.kit.usd.layers._omni_kit_usd_layers.LayerEditMode

- class LayerErrorType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - ALREADY_EXISTS: omni.kit.usd.layers._omni_kit_usd_layers.LayerErrorType
  - INVALID_PARAM: omni.kit.usd.layers._omni_kit_usd_layers.LayerErrorType
  - INVALID_STAGE: omni.kit.usd.layers._omni_kit_usd_layers.LayerErrorType
  - LIVE_SESSION_BASE_LAYER_MISMATCH: omni.kit.usd.layers._omni_kit_usd_layers.LayerErrorType
  - LIVE_SESSION_JOINED_ALREADY: omni.kit.usd.layers._omni_kit_usd_layers.LayerErrorType
  - LIVE_SESSION_NOT_JOINED: omni.kit.usd.layers._omni_kit_usd_layers.LayerErrorType
  - LIVE_SESSION_NOT_SUPPORTED: omni.kit.usd.layers._omni_kit_usd_layers.LayerErrorType
  - LIVE_SESSION_NO_MERGE_PERMISSION: omni.kit.usd.layers._omni_kit_usd_layers.LayerErrorType
  - LIVE_SESSION_VERSION_MISMATCH: omni.kit.usd.layers._omni_kit_usd_layers.LayerErrorType
  - LIVE_SESSOIN_INVALID: omni.kit.usd.layers._omni_kit_usd_layers.LayerErrorType
  - NOT_FOUND: omni.kit.usd.layers._omni_kit_usd_layers.LayerErrorType
  - READ_ONLY: omni.kit.usd.layers._omni_kit_usd_layers.LayerErrorType
  - SUCCESS: omni.kit.usd.layers._omni_kit_usd_layers.LayerErrorType
  - UNKNOWN: omni.kit.usd.layers._omni_kit_usd_layers.LayerErrorType

- class Layers
  - def __init__(self, layers_instance, usd_context: omni.usd.UsdContext)
  - def get_layers_state(self) -> LayersState
  - def get_specs_locking(self) -> SpecsLocking
  - def get_auto_authoring(self) -> AutoAuthoring
  - def get_specs_linking(self) -> SpecsLinking
  - def get_live_syncing(self) -> LiveSyncing
  - def get_event_stream(self)
  - def get_edit_mode(self) -> LayerEditMode
  - def set_edit_mode(self, edit_mode: LayerEditMode)
  - def get_last_error_type(self) -> LayerErrorType
  - def get_last_error_string(self)
  - [property] def usd_context(self) -> omni.usd.UsdContext

- class LayerEventPayload
  - def __init__(self, event: carb.events.IEvent)
  - [property] def event_type(self) -> LayerEventType
  - [property] def layer_info_data(self) -> Dict[str, List[str]]
  - [property] def identifiers_or_spec_paths(self) -> List[str]
  - [property] def layer_spec_paths(self) -> Dict[str, List[str]]
  - [property] def user_name(self) -> str
  - [property] def user_id(self) -> str
  - [property] def success(self) -> bool
  - [property] def layer_identifier(self) -> str
  - def is_layer_influenced(self, layer_identifier_or_handle: Union[str, Sdf.Layer]) -> bool

- class LayersState
  - def __init__(self, layers_instance: ILayersInstance, usd_context)
  - [property] def usd_context(self)
  - def set_muteness_scope(self, global_scope: bool)
  - def is_muteness_global(self) -> bool
  - def is_layer_locally_muted(self, layer_identifier: str) -> bool
  - def is_layer_globally_muted(self, layer_identifier: str) -> bool
  - def is_layer_writable(self, layer_identifier: str) -> bool
  - def is_layer_readonly_on_disk(self, layer_identifier: str) -> bool
  - def is_layer_savable(self, layer_identifier: str) -> bool
  - def set_layer_lock_state(self, layer_identifier: str, locked: bool)
  - def is_layer_locked(self, layer_identifier: str) -> bool
  - def set_layer_name(self, layer_identifier: str, name: str)
  - def get_layer_name(self, layer_identifier: str) -> str
  - def get_layer_owner(self, layer_identifier: str) -> str
  - def is_layer_outdated(self, layer_identifier: str) -> bool
  - def get_local_layer_identifiers(self, include_session_layers = False, include_anonymous_layers = True, include_invalid_layers = False) -> List[str]
  - def get_dirty_layer_identifiers(self, not_in_session = False) -> List[str]
  - def get_all_outdated_layer_identifiers(self, not_in_session = False, not_auto = False) -> List[str]
  - def get_outdated_sublayer_identifiers(self, not_in_session = False, not_auto = False) -> List[str]
  - def get_outdated_non_sublayer_identifiers(self, not_in_session = False, not_auto = False) -> List[str]
  - def reload_all_outdated_layers(self, not_in_session = True, not_auto = False)
  - def reload_outdated_sublayers(self, not_in_session = True, not_auto = False)
  - def reload_outdated_non_sublayers(self, not_in_session = True, not_auto = False)
  - def has_local_layer(self, layer_identifier) -> bool
  - def has_used_layer(self, layer_identifier) -> bool
  - def is_auto_reload_layer(self, layer_identifier: str) -> bool
  - def add_auto_reload_layer(self, layer_identifier: str)
  - def remove_auto_reload_layer(self, layer_identifier: str)
  - def get_auto_reload_layers(self) -> List[str]

- class SpecsLocking
  - def __init__(self, layers_instance: ILayersInstance, usd_context)
  - [property] def usd_context(self)
  - def lock_spec(self, spec_path: Union[str, Sdf.Path], hierarchy: bool = False) -> List[str]
  - def unlock_spec(self, spec_path: Union[str, Sdf.Path], hierarchy: bool = False) -> List[str]
  - def unlock_all_specs(self)
  - def get_all_locked_specs(self) -> List[str]
  - def is_spec_locked(self, spec_path: Union[str, Sdf.Path]) -> bool

- class AutoAuthoring
  - def __init__(self, layers_instance: ILayersInstance, usd_context)
  - [property] def usd_context(self)
  - def is_enabled(self) -> bool
  - def set_default_layer(self, layer_identifier: str)
  - def get_default_layer(self) -> str
  - def is_auto_authoring_layer(self, layer_identifier: str) -> bool

- class SpecsLinking
  - def __init__(self, layers_instance: ILayersInstance, usd_context)
  - [property] def usd_context(self)
  - def is_enabled(self) -> bool
  - def link_spec(self, spec_path: Union[str, Sdf.Path], layer_identifier: str, hierarchy: bool = False) -> List[str]
  - def unlink_spec(self, spec_path: Union[str, Sdf.Path], layer_identifier: str, hierarchy: bool = False) -> List[str]
  - def unlink_spec_from_all_layers(self, spec_path: Union[str, Sdf.Path], hierarchy: bool = False) -> Dict[str, List[str]]
  - def unlink_specs_to_layer(self, layer_identifier: str) -> List[str]
  - def unlink_all_specs(self)
  - def get_spec_layer_links(self, spec_path: Union[str, Sdf.Path], hierarchy: bool = False)
  - def get_spec_links_for_layer(self, layer_identifier: str) -> List[str]
  - def get_all_spec_links(self)
  - def is_spec_linked(self, spec_path: str, layer_identifier: str = '')

- class LiveSession
  - def __init__(self, handle, session_channel, live_syncing)
  - [property] def joined(self) -> bool
  - [property] def valid(self) -> bool
  - [property] def channel_url(self) -> str
  - [property] def base_layer_identifier(self) -> str
  - [property] def name(self) -> str
  - [property] def url(self) -> str
  - [property] def shared_link(self) -> str
  - [property] def owner(self) -> str
  - [property] def merge_permission(self) -> bool
  - [property] def root(self) -> str
  - [property] def peer_users(self) -> List[LiveSessionUser]
  - [property] def logged_user_name(self) -> str
  - [property] def logged_user_id(self) -> str
  - [property] def logged_user(self) -> LiveSessionUser
  - def get_peer_user_info(self, user_id) -> LiveSessionUser
  - def get_last_modified_time(self) -> int

- class LiveSyncing
  - def __init__(self, layers_instance: ILayersInstance, usd_context, layers_state)
  - [property] def usd_context(self) -> omni.usd.UsdContext
  - [property] def layers_instance(self) -> ILayersInstance
  - def get_all_live_sessions(self, layer_identifier: str = None) -> List[LiveSession]
  - def create_live_session(self, name: str, layer_identifier: str = None) -> LiveSession
  - def join_live_session(self, live_session: LiveSession, prim_path: Union[Sdf.Path, str] = None) -> bool
  - def join_live_session_by_url(self, layer_identifier: str, live_session_url: str, create_if_not_existed: bool = False) -> bool
  - def try_cancelling_live_session_join(self, layer_identifier: str) -> Optional[LiveSession]
  - def stop_live_session(self, layer_identifier: str = None, prim_path: Sdf.Path = None)
  - def stop_all_live_sessions(self)
  - def is_stage_in_live_session(self) -> bool
  - def is_layer_in_live_session(self, layer_identifier: str = None, live_prim_only: bool = False) -> bool
  - def is_prim_in_live_session(self, prim_path: Sdf.Path, layer_identifier: str = None, from_reference_or_payload_only = False) -> bool
  - def is_in_live_session(self) -> bool
  - def is_live_session_layer(self, layer_identifier: str) -> bool
  - def get_current_live_session_layers(self, layer_identifier: str = None) -> List[str]
  - def get_current_live_session_peer_users(self, layer_identifier: str = None) -> List[LiveSessionUser]
  - def get_live_session_for_live_layer(self, live_layer_identifier: str) -> LiveSession
  - def get_current_live_session(self, layer_identifier: str = None) -> LiveSession
  - def get_all_current_live_sessions(self, prim_path: Sdf.Path = None) -> List[LiveSession]
  - def get_live_session_by_url(self, session_url) -> LiveSession
  - def find_live_session_by_name(self, layer_identifier: str, session_name: str) -> LiveSession
  - [property] def permission_to_merge_current_session(self, layer_identifier: str = None) -> bool
  - def merge_live_session_changes(self, layer_identifier: str, stop_session: bool) -> bool
  - def merge_live_session_changes_to_specific_layer(self, layer_identifier: str, target_layer_identifier: str, stop_session: bool, clear_target_layer: bool) -> bool
  - def merge_changes_to_base_layers(self, stop_session: bool) -> bool
  - def merge_changes_to_specific_layer(self, target_layer_identifier: str, stop_session: bool, clear_target_layer: bool) -> bool
  - async def broadcast_merge_started_message_async(self, layer_identifier: str = None)
  - async def broadcast_merge_done_message_async(self, destroy: bool = True, layer_identifier: str = None)
  - async def merge_and_stop_live_session_async(self, target_layer: str = None, comment = '', pre_merge: Callable[[LiveSession], Awaitable] = None, post_merge: Callable[[bool], Awaitable] = None, layer_identifier: str = None) -> bool
  - def mute_live_session_merge_notice(self, layer_identifier: str)
  - def unmute_live_session_merge_notice(self, layer_identifier: str)
  - def is_live_session_merge_notice_muted(self, layer_identifier: str) -> bool
  - async def open_stage_with_live_session_async(self, stage_url, session_name = None) -> Tuple[bool, str]
  - def register_open_stage_addon(self, callback)

- class LiveSessionUser
  - def __init__(self, user_name, user_id, from_app)
  - [property] def user_name(self) -> str
  - [property] def user_id(self) -> str
  - [property] def from_app(self) -> str
  - [property] def user_color(self) -> Tuple[int, int, int]

- class LayerUtils
  - LAYER_OMNI_CUSTOM_KEY: str
  - LAYER_MUTENESS_CUSTOM_KEY: str
  - LAYER_LOCK_STATUS_CUSTOM_KEY: str
  - LAYER_NAME_CUSTOM_KEY: str
  - LAYER_AUTHORING_LAYER_CUSTOM_KEY: str
  - static def create_sublayer(layer: Sdf.Layer, sublayer_position: int, layer_identifier: str)
  - static def insert_sublayer(layer: Sdf.Layer, sublayer_position: int, layer_identifier: str, check_empty_layer = True)
  - static def replace_sublayer(layer: Sdf.Layer, sublayer_position: int, layer_identifier: str)
  - static def get_custom_layer_name(layer: Sdf.Layer)
  - static def set_custom_layer_name(layer: Sdf.Layer, name: str)
  - static def transfer_layer_content(source_layer: Sdf.Layer, target_layer: Sdf.Layer, copy_custom_data = True, skip_sublayers = True)
  - static def resolve_paths(base_layer: Sdf.Layer, target_layer: Sdf.Layer, store_relative_path = True, relative_to_base_layer = False, copy_sublayer_offsets = False)
  - static def get_sublayer_position_in_parent(parent_layer_identifier: str, layer_identifier: str)
  - static def has_prim_spec(layer_identifier: str, prim_spec_path)
  - static def get_sublayer_identifier(layer_identifier: str, sublayer_position: int)
  - static def restore_authoring_layer_from_custom_data(stage)
  - static def save_authoring_layer_to_custom_data(stage)
  - static def get_layer_global_muteness(root_layer: Sdf.Layer, layer_identifier: str)
  - static def set_layer_global_muteness(root_layer: Sdf.Layer, layer_identifier: str, muted: bool)
  - static def remove_layer_global_muteness(root_layer: Sdf.Layer, layer_identifier: str)
  - static def get_layer_lock_status(root_layer: Sdf.Layer, layer_identifier: str)
  - static def set_layer_lock_status(root_layer: Sdf.Layer, layer_identifier: str, locked: bool)
  - static def remove_layer_lock_status(root_layer: Sdf.Layer, layer_identifier: str)
  - static def restore_muteness_from_custom_data(stage)
  - static def remove_sublayer(layer: Sdf.Layer, position)
  - static def remove_prim_spec(layer: Sdf.Layer, prim_spec_path: Union[str, Sdf.Path])
  - static def move_layer(from_parent_layer_identifier, from_sublayer_position, to_parent_layer_identifier, to_sublayer_position, remove_source = False)
  - static def get_edit_target(stage) -> str
  - static def set_edit_target(stage, layer_identifier)
  - static def get_all_sublayers(stage, include_session_layers = False, include_only_omni_layers = False, include_anonymous_layers = True) -> List[str]
  - static def is_layer_writable(layer_identifier) -> bool
  - static def get_dirty_layers(stage, include_root_layer = True, include_only_omni_layers = False) -> List[str]
  - static async def create_checkpoint_async(layer_identifier: Union[str, List[str]], comment: str, force = False)
  - static def create_checkpoint(layer_identifier: Union[str, List[str]], comment: str, force = False)
  - static async def create_checkpoint_for_stage_async(stage, comment: str, only_dirty_layers = False, force = False)
  - static def reload_all_layers(layer_identifiers: Union[str, List[str]])

- class AbstractLayerCommand(omni.kit.commands.Command)
  - def __init__(self, context_name_or_instance: Union[str, omni.usd.UsdContext] = '')
  - def get_layers(self)
  - def get_specs_linking(self)
  - def get_specs_locking(self)
  - def do(self)
  - def do_impl(self)
  - def undo_impl(self)
  - def undo(self)

- class SetEditTargetCommand(AbstractLayerCommand)
  - def __init__(self, layer_identifier: str, usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do_impl(self)
  - def undo_impl(self)

- class CreateSublayerCommand(AbstractLayerCommand)
  - def __init__(self, layer_identifier: str, sublayer_position: int, new_layer_path: str, transfer_root_content: bool, create_or_insert: bool, layer_name: str = '', usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do_impl(self)
  - def undo_impl(self)

- class RemoveSublayerCommand(AbstractLayerCommand)
  - def __init__(self, layer_identifier: str, sublayer_position: int, usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do_impl(self)
  - def undo_impl(self)

- class RemovePrimSpecCommand(omni.kit.commands.Command)
  - def __init__(self, layer_identifier: str, prim_spec_path: Union[Sdf.Path, List[Sdf.Path]], usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do(self)
  - def undo(self)

- class MergeLayersCommand(AbstractLayerCommand)
  - def __init__(self, dst_parent_layer_identifier: str, dst_layer_identifier, src_parent_layer_identifier: str, src_layer_identifier: str, dst_stronger_than_src: bool, usd_context: Union[str, omni.usd.UsdContext] = '', src_layer_offset: Sdf.LayerOffset = Sdf.LayerOffset(0.0, 1.0))
  - def do_impl(self)
  - def undo_impl(self)

- class FlattenLayersCommand(AbstractLayerCommand)
  - def __init__(self, usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do_impl(self)
  - def undo_impl(self)

- class CreateLayerReferenceCommand(AbstractLayerCommand)
  - def __init__(self, layer_identifier: str, path_to: Sdf.Path, asset_path: str = None, prim_path: Sdf.Path = None, usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do_impl(self)
  - def undo_impl(self)

- class StitchPrimSpecsToLayer(AbstractLayerCommand)
  - def __init__(self, prim_paths: List[str], target_layer_identifier: str, usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do_impl(self)
  - def undo_impl(self)

- class MovePrimSpecsToLayerCommand(AbstractLayerCommand)
  - def __init__(self, dst_layer_identifier: str, src_layer_identifier: str, prim_spec_path: str, dst_stronger_than_src: bool, usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do_impl(self)
  - def undo_impl(self)

- class MoveSublayerCommand(AbstractLayerCommand)
  - def __init__(self, from_parent_layer_identifier: str, from_sublayer_position: int, to_parent_layer_identifier: str, to_sublayer_position: int, remove_source: bool = False, usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do_impl(self)
  - def undo_impl(self)

- class ReplaceSublayerCommand(AbstractLayerCommand)
  - def __init__(self, layer_identifier: str, sublayer_position: int, new_layer_path: str, usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do_impl(self)
  - def undo_impl(self)

- class SetLayerMutenessCommand(AbstractLayerCommand)
  - def __init__(self, layer_identifier: str, muted: bool, usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do_impl(self)
  - def undo_impl(self)

- class LockLayerCommand(AbstractLayerCommand)
  - def __init__(self, layer_identifier: str, locked: bool, usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do_impl(self)
  - def undo_impl(self)

- class LinkSpecsCommand(AbstractLayerCommand)
  - def __init__(self, spec_paths: Union[str, List[str]], layer_identifiers: Union[str, List[str]], additive: bool = True, hierarchy: bool = False, usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do(self)
  - def undo(self)

- class UnlinkSpecsCommand(AbstractLayerCommand)
  - def __init__(self, spec_paths: Union[str, List[str]], layer_identifiers: Union[str, List[str]], hierarchy = False, usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do(self)
  - def undo(self)

- class LockSpecsCommand(AbstractLayerCommand)
  - def __init__(self, spec_paths: Union[str, List[str]], hierarchy = False, usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do(self)
  - def undo(self)

- class UnlockSpecsCommand(AbstractLayerCommand)
  - def __init__(self, spec_paths: Union[str, List[str]], hierarchy = False, usd_context: Union[str, omni.usd.UsdContext] = '')
  - def do(self)
  - def undo(self)

## Functions

- def get_layers(context_name_or_instance: Union[str, omni.usd.UsdContext] = '') -> Union[Layers, None]
- def get_auto_authoring(context_name_or_instance: Union[str, omni.usd.UsdContext] = '') -> Union[AutoAuthoring, None]
- def get_layers_state(context_name_or_instance: Union[str, omni.usd.UsdContext] = '') -> Union[LayersState, None]
- def get_live_syncing(context_name_or_instance: Union[str, omni.usd.UsdContext] = '') -> Union[LiveSyncing, None]
- def get_last_error_type(context_name_or_instance: Union[str, omni.usd.UsdContext] = '') -> LayerErrorType
- def get_last_error_string(context_name_or_instance: Union[str, omni.usd.UsdContext] = '') -> str
- def active_authoring_layer_context(usd_context) -> Usd.EditContext
- def get_layer_event_payload(event: carb.events.IEvent) -> LayerEventPayload
- def get_short_user_name(user_name: str) -> str
- def get_live_session_name_from_shared_link(shared_session_link: str) -> str
- def link_specs(usd_context, spec_paths: Union[Union[str, Sdf.Path], List[Union[str, Sdf.Path]]], layer_identifiers: Union[str, List[str]], hierarchy = False) -> Dict[str, List[str]]
- def unlink_specs(usd_context, spec_paths: Union[Union[str, Sdf.Path], List[Union[str, Sdf.Path]]], layer_identifiers: Union[str, List[str]], hierarchy = False) -> Dict[str, List[str]]
- def unlink_specs_to_layers(usd_context, layer_identifiers: Union[str, List[str]]) -> Dict[str, List[str]]
- def unlink_specs_from_all_layers(usd_context, spec_paths: Union[str, List[str]], hierarchy = False) -> Dict[str, List[str]]
- def unlink_all_specs(usd_context)
- def get_spec_layer_links(usd_context, spec_paths: Union[Union[str, Sdf.Path], List[Union[str, Sdf.Path]]], hierarchy = False) -> Dict[str, List[str]]
- def get_spec_links_for_layers(usd_context, layer_identifiers: Union[str, List[str]]) -> Dict[str, List[str]]
- def get_all_spec_links(usd_context) -> Dict[str, List[str]]
- def is_spec_linked(usd_context, spec_path: Union[str, Sdf.Path], layer_identifier: str = '') -> bool
- def lock_specs(usd_context, spec_paths: Union[Union[str, Sdf.Path], List[Union[str, Sdf.Path]]], hierarchy = False) -> List[str]
- def unlock_specs(usd_context, spec_paths: Union[str, List[str]], hierarchy = False) -> List[str]
- def unlock_all_specs(usd_context)
- def get_all_locked_specs(usd_context) -> List[str]
- def is_spec_locked(usd_context, spec_path: Union[str, Sdf.Path]) -> bool

## Variables

- LayerEventType: Unknown
- SETTINGS_AUTO_RELOAD_SUBLAYERS: str
- SETTINGS_AUTO_RELOAD_NON_SUBLAYERS: str
- SETTINGS_IGNORE_OUTDATE_NOTIFICATION: str
