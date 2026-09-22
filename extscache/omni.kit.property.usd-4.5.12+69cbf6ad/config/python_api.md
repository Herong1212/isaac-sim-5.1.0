# Public API for module omni.kit.property.usd:

## Classes

- class AllowedTokenItem(ui.AbstractItem)
  - def __init__(self, item)

- class ControlStateManager
  - class def get_instance(cls)
  - def __init__(self, icon_path)
  - def destory(self)
  - def register_control_state(self, on_refresh_state: Callable, on_build_state: Callable, icon_path: str, priority: float = 0.0) -> int
  - def unregister_control_state(self, flag)
  - def update_control_state(self, usd_model_base)
  - def build_control_state(self, control_state, **kwargs)

- class FloatModel(ui.SimpleFloatModel)
  - def __init__(self, parent)
  - def begin_edit(self)
  - def end_edit(self)

- class GfMatrixAttributeModel(MatrixBaseAttributeModel)
  - def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], comp_count: int, tf_type: Tf.Type, self_refresh: bool, metadata: dict)

- class GfQuatAttributeModel(ui.AbstractItemModel, UsdBase)
  - def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], tf_type: Tf.Type, self_refresh: bool, metadata: dict)
  - def clean(self)
  - def get_item_children(self, item)
  - def get_item_value_model(self, item, column_id)
  - def begin_edit(self, item = None)
  - def end_edit(self, item = None)

- class GfQuatEulerAttributeModel(ui.AbstractItemModel, UsdBase)
  - axes: List
  - def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], tf_type: Tf.Type, self_refresh: bool, metadata: dict)
  - def clean(self)
  - def update_to_submodels(self)
  - def get_item_children(self, item)
  - def get_item_value_model(self, item, column_id)
  - def begin_edit(self, item = None)
  - def end_edit(self, item = None)

- class GfVecAttributeModel(ui.AbstractItemModel, UsdBase)
  - def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], comp_count: int, tf_type: Tf.Type, self_refresh: bool, metadata: dict, **kwargs)
  - def clean(self)
  - def construct_vector_from_item(self)
  - def get_item_children(self, item)
  - def get_item_value_model(self, item, column_id)
  - def begin_edit(self, item = None)
  - def end_edit(self, item = None)
  - def set_value(self, value, comp: int = -1) -> bool

- class GfVecAttributeSingleChannelModel(UsdAttributeModel)
  - def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], channel_index: int, self_refresh: bool, metadata: dict, change_on_edit_end = True, **kwargs)
  - def is_value_array(self)
  - def get_value_as_string(self, elide_big_array = True) -> str
  - def get_value_as_float(self) -> float
  - def get_value_as_bool(self) -> bool
  - def get_value_as_int(self) -> int
  - def set_value(self, value, comp: int = -1)
  - def is_different_from_default(self)

- class IntModel(ui.SimpleIntModel)
  - def __init__(self, parent)
  - def begin_edit(self)
  - def end_edit(self)

- class MdlEnumAttributeModel(ui.AbstractItemModel, UsdBase)
  - def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], self_refresh: bool, metadata: dict, **kwargs)
  - def clean(self)
  - def get_item_children(self, item)
  - def get_item_value_model(self, item, column_id)
  - def begin_edit(self, item = None)
  - def end_edit(self, item = None)
  - def get_value_as_string(self)
  - def is_allowed_enum_string(self, enum_str)
  - def set_from_enum_string(self, enum_str)

- class OptionItem(ui.AbstractItem)
  - def __init__(self, display_name: str, value: int)

- class PlaceholderAttribute
  - def __init__(self, name, prim = None, metadata = None)
  - def Get(self, time_code = 0)
  - def GetPath(self)
  - def ValueMightBeTimeVarying(self)
  - def GetMetadata(self, token)
  - def GetAllMetadata(self)
  - def GetPrim(self)
  - def GetName(self)
  - def GetDisplayGroup(self)
  - def CreateAttribute(self)
  - def HasAuthoredConnections(self)
  - def IsHidden(self)
  - def GetPropertyStack(self, *args, **kwargs)

- class PrimPathWidget(SimplePropertyWidget)
  - def __init__(self)
  - def clean(self)
  - def reset(self)
  - def on_new_payload(self, payload)
  - static def payload_wrapper(objects, onclick_fn_weak)
  - def build_items(self)
  - static def add_button_menu_entry(path: str, glyph: str = None, name_fn = None, show_fn: Callable = None, enabled_fn: Callable = None, onclick_fn: Callable = None, add_to_context_menu: bool = True)
  - static def remove_button_menu_entry(item: ButtonMenuEntry)
  - static def get_button_menu_entries()
  - static def add_path_item(draw_fn: Callable)
  - static def remove_path_item(draw_fn: Callable)
  - static def get_path_items()
  - static def rebuild()
  - static def set_path_item_padding(padding: float)
  - static def get_path_item_padding(padding = None)

- class PrimSelectionPayload
  - def __init__(self, stage: weakref.ref[Usd.Stage], paths: List[Sdf.Path])
  - def get_stage(self)
  - def get_paths(self) -> List[Sdf.Path]
  - def set_large_selection_override(self, state: bool)
  - def get_large_selection_count(self)
  - def is_large_selection(self) -> bool
  - def cleanup_payload(self)

- class SdfAssetPathArrayAttributeItemModel(ui.AbstractItemModel)
  - def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], self_refresh: bool, metadata: dict, delegate)
  - def clean(self)
  - [property] def value_model(self) -> UsdAttributeModel
  - def get_item_children(self, item)
  - def get_item_value_model_count(self, item)
  - def get_item_value_model(self, item, column_id)
  - def get_drag_mime_data(self, item)
  - def drop_accepted(self, target_item, source, drop_location = -1)
  - def drop(self, target_item, source, drop_location = -1)
  - def get_value(self, *args, **kwargs)
  - def set_value(self, *args, **kwargs)

- class SdfAssetPathArrayAttributeSingleEntryModel(SdfAssetPathAttributeModel)
  - def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], index: int, self_refresh: bool, metadata: dict)
  - [property] def index(self)
  - def get_value_as_string(self, elide_big_array = True) -> str
  - def get_value(self)
  - def is_valid_path(self) -> bool
  - def get_resolved_path(self)
  - def set_value(self, value, comp: int = -1, resolved_path: str = '')

- class SdfAssetPathAttributeModel(UsdAttributeModel)
  - def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], self_refresh: bool, metadata: dict, **kwargs)
  - def get_value_as_string(self, elide_big_array = True) -> str
  - def is_valid_path(self) -> bool
  - def get_resolved_path(self)
  - def set_value(self, value, comp: int = -1, resolved_path: str = '')

- class SdfAssetPathItem(ui.AbstractItem)
  - def __init__(self, asset_path_single_entry_model)
  - def destroy(self)

- class SdfTimeCodeModel(UsdAttributeModel)

- class SelectionNotifier
  - def __init__(self, usd_context_id = '', property_window_context_id = '')
  - def start(self)
  - def stop(self)
  - def notify_property_window(self, save_scroll_pos: bool = False)

- class TfTokenAttributeModel(ui.AbstractItemModel, UsdBase)
  - DUPLICATE_TAG: str
  - def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], self_refresh: bool, metadata: dict, **kwargs)
  - def clean(self)
  - def get_item_children(self, item)
  - def get_item_value_model(self, item, column_id)
  - def begin_edit(self, item = None)
  - def end_edit(self, item = None)
  - def get_value_as_token(self)
  - def is_allowed_token(self, token)
  - def set_value(self, value, comp: int = -1) -> bool

- class UsdAttributeInvertedModel(UsdAttributeModel)
  - def get_value_as_bool(self) -> bool
  - def get_value_as_string(self, elide_big_array = True) -> str
  - def set_value(self, value, comp: int = -1)
  - def get_value(self)

- class UsdAttributeModel(ui.AbstractValueModel, UsdBase)
  - def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], self_refresh: bool, metadata: dict, change_on_edit_end = True, **kwargs)
  - def clean(self)
  - def begin_edit(self)
  - def end_edit(self)
  - def get_value_as_string(self, elide_big_array = True) -> str
  - def get_value_as_float(self) -> float
  - def get_value_as_bool(self) -> bool
  - def get_value_as_int(self) -> int
  - def set_value(self, value, comp: int = -1)

- class UsdBase
  - def __init__(self, stage: Usd.Stage, object_paths: List[Sdf.Path], self_refresh: bool, metadata: dict = None, change_on_edit_end: bool = True, treat_array_entry_as_comp: bool = False, **kwargs)
  - [property] def control_state(self)
  - [property] def stage(self)
  - def get_valid_stage_adapter_read(self, path)
  - def get_valid_stage_adapter_write(self, path)
  - [property] def metadata(self)
  - def update_control_state(self)
  - def set_on_control_state_changed_fn(self, fn)
  - def create_placeholder_attribute(self, name, prim = None, metadata = None)
  - def set_on_set_default_fn(self, fn)
  - def clean(self)
  - def is_different_from_default(self) -> bool
  - def might_be_time_varying(self) -> bool
  - def is_ambiguous(self) -> bool
  - def is_readonly(self) -> bool
  - def is_comp_ambiguous(self, index: int) -> bool
  - def is_array_type(self) -> bool
  - def get_all_comp_ambiguous(self) -> List[bool]
  - def get_attribute_paths(self) -> List[Sdf.Path]
  - def get_property_paths(self) -> List[Sdf.Path]
  - def get_prim_paths(self, stage) -> List[Sdf.Path]
  - def get_connections(self)
  - def get_bad_connection(self) -> tuple[bool, str]
  - def set_default(self, comp = -1)
  - def set_value(self, value, comp: int = -1) -> bool
  - def begin_edit(self)
  - def end_edit(self)
  - def is_editing(self) -> bool
  - def get_value_by_comp(self, comp: int)
  - static def update_value_by_comp(from_value, to_value, comp: int)
  - def is_value_array(self)
  - def set_locked(self, locked)
  - def is_instance_proxy(self)
  - def is_locked(self)
  - def has_connections(self)
  - def get_value(self)
  - def get_stage(self)
  - def get_current_time_code(self)
  - def set_soft_range_userdata(self, soft_range_min, soft_range_max)
  - def get_layers_with_strongest_value_opinions(self) -> list[Sdf.Layer]
  - get_attributes: _get_attributes
  - get_objects: _get_objects

- class UsdFloatItem(ui.AbstractItem)
  - def __init__(self, model)

- class UsdMatrixItem(ui.AbstractItem)
  - def __init__(self, model)

- class UsdPropertyWidgets(omni.ext.IExt)
  - def __init__(self)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

- class UsdQuatItem(ui.AbstractItem)
  - def __init__(self, model)

- class UsdVectorItem(ui.AbstractItem)
  - def __init__(self, model)

- class RelationshipTargetPicker
  - def __init__(self, stage, filter_type_list, filter_lambda, additional_widget_kwargs)
  - def clean(self)
  - def show(self, targets_limit, on_targets_selected: Optional[Callable] = None)

- class SelectionWatch
  - def __init__(self, stage, on_selection_changed_fn, filter_type_list, filter_lambda, tree_view = None)
  - def reset(self, targets_limit)
  - def set_tree_view(self, tree_view)
  - def clear_selection(self)
  - def enable_filtering_checking(self, enable: bool)
  - def set_filtering(self, filter_string: Optional[str])

- class MetadataObjectModel(ui.AbstractItemModel, UsdBase)
  - def __init__(self, stage: Usd.Stage, object_paths: List[Sdf.Path], self_refresh: bool, metadata: dict, key: str, default, options: list)
  - def clean(self)
  - def get_item_children(self, item)
  - def get_item_value_model(self, item, column_id)
  - def begin_edit(self)
  - def end_edit(self)
  - def is_different_from_default(self) -> bool
  - def set_default(self, comp = -1)
  - def set_value(self, value, comp = -1)

- class PayloadReferenceWidget(UsdPropertiesWidget)
  - def __init__(self, use_payloads = False)
  - def clean(self)
  - def reset(self)
  - def on_new_payload(self, payload)
  - def build_impl(self)
  - def on_collapsed_changed(self, collapsed)
  - def build_items(self)

- class CustomLayoutFrame(Container)
  - def __init__(self, hide_extra = False)
  - def apply(self, props)

- class CustomLayoutGroup(Container)
  - def __init__(self, container_name, collapsed = False, hide_if_true = None, show_if_true = None)

- class CustomLayoutProperty
  - def __init__(self, prop_name, display_name = None, build_fn = None, hide_if_true = None, show_if_true = None)
  - def get_property_name(self)
  - def get_display_name(self)
  - def get_build_fn(self)
  - def is_visible(self)

- class RegisteredSchemaCodes(IntEnum)
  - NOT_FOUND: int
  - FOUND: int
  - PRIVATE: int
  - PUBLIC: int
  - NO_CREATE: int
  - NO_REMOVE: int

## Functions

- def get_large_selection_count()
- def register_schema(widget_name: str, schemas: list, options: RegisteredSchemaCodes = RegisteredSchemaCodes.PRIVATE)
- def get_registered_schemas()
- def is_registered_schema(widget_names: list[str], schema_name: str) -> tuple[str, RegisteredSchemaCodes]

## Variables

- ADDITIONAL_CHANGED_PATH_EVENT_TYPE: int
- ADDITIONAL_CHANGED_PATH_GLOBAL_EVENT: str

## Other

- UsdPropertiesWidget: unknown
- UsdPropertiesWidgetBuilder: unknown
- UsdPropertyUiEntry: unknown
- SchemaPropertiesWidget: unknown
