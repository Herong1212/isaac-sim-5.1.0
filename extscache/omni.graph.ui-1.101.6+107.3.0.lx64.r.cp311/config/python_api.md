# Public API for module omni.graph.ui:

## Classes

- class ComputeNodeWidget(UsdPropertiesWidget)
  - BUNDLE_INDEX: int
  - ATTRIB_LIST_INDEX: int
  - def __init__(self, title = 'OmniGraph Node', collapsed = False)
  - static def get_instance()
  - [property] def payload(self) -> list[Sdf.Path]
  - def on_shutdown(self)
  - def reset(self)
  - def on_new_payload(self, payload: list[Sdf.Path]) -> bool
  - def get_additional_kwargs(self, ui_attr: UsdAttributeUiEntry)
  - def get_widget_prim(self)
  - def add_template_path(self, file_path)
  - def get_template_path(self, template_name: str) -> pathlib.Path | None
  - def load_template(self, props: list[UsdPropertyUiEntry]) -> list[UsdPropertyUiEntry] | None
  - def rebuild_window(self)
  - def apply_default_layout(self, props: list[UsdPropertyUiEntry]) -> list[UsdPropertyUiEntry]
  - def width_changed_subscribe(self)
  - def list_diff(self, list_a, list_b)
  - def move_elements_to_beginning(self, elements_list, target_list)
  - def build_property_item(self, stage, ui_prop: UsdPropertyUiEntry, prim_paths: list[Sdf.Path])
  - def get_bundles(self)
  - def bundle_elements_layout_fn(self, **kwargs)
  - def display_bundles_content(self)
  - def set_bundle_models_values(self)
  - def on_bundles_update(self, event)
  - def on_stage_update(self, event)

- class ComputeNodeWidgetUtils
  - static def build_property_item(stage: Usd.Stage, ui_prop: UsdPropertyUiEntry, prim_path: Sdf.Path, label_kwd_args: dict[str, Any] = None, value_kwd_args: dict[str, Any] = None) -> tuple[ui.Container, list[ui.AbstractValueModel]]
  - static def customize_prop_metadata(node: og.Node, ui_prop: UsdPropertyUiEntry) -> og.Attribute
  - static def get_additional_kwargs(ui_prop: UsdPropertyUiEntry) -> tuple[dict[str, Any], dict[str, Any]]
  - static def update_prop_for_extended_type(node: og.Node, ui_prop: UsdPropertyUiEntry)

- class GraphVariableCustomLayout
  - def __init__(self, compute_node_widget)
  - def apply(self, props)

- class OmniGraphAttributeModel(ui.AbstractValueModel, OmniGraphBase)
  - def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], self_refresh: bool, metadata: dict, change_on_edit_end = False, **kwargs)
  - def clean(self)
  - def begin_edit(self)
  - def end_edit(self)
  - def get_value_as_string(self, elide_big_array = True) -> str
  - def get_value_as_float(self) -> float
  - def get_value_as_bool(self) -> bool
  - def get_value_as_int(self) -> int
  - def set_value(self, value)

- class OmniGraphBase
  - def __init__(self, stage: Usd.Stage, object_paths: list[Sdf.Path], self_refresh: bool, metadata: dict = None, change_on_edit_end = False, **kwargs)
  - def is_editing(self) -> bool
  - [property] def control_state(self)
  - [property] def stage(self)
  - [property] def metadata(self)
  - def update_control_state(self)
  - def set_on_control_state_changed_fn(self, fn)
  - def set_on_set_default_fn(self, fn)
  - def clean(self)
  - def is_different_from_default(self)
  - def might_be_time_varying(self)
  - def is_ambiguous(self)
  - def is_comp_ambiguous(self, index: int)
  - def get_value_by_comp(self, comp: int)
  - def get_attribute_paths(self) -> list[Sdf.Path]
  - def get_property_paths(self) -> list[Sdf.Path]
  - def get_connections(self)
  - def set_default(self, comp = -1)
  - def set_value(self, value, comp = -1) -> bool
  - def begin_edit(self)
  - def end_edit(self)
  - def get_value(self)
  - def get_current_time_code(self)
  - def set_locked(self, locked)
  - def is_locked(self)
  - def has_connections(self)

- class OmniGraphPropertiesWidgetBuilder(UsdPropertiesWidgetBuilder)
  - OVERRIDE_TYPENAME_KEY: str
  - UNRESOLVED_TYPENAME: str
  - tf_gf_matrix4d: Unknown
  - tf_gf_frame4d: Unknown
  - tf_gf_quatd: Unknown
  - tf_gf_quatf: Unknown
  - tf_gf_quath: Unknown
  - tf_tf_tokenarray: Unknown
  - class def init_builder_table(cls)
  - class def startup(cls)
  - class def build(cls, stage, attr_name, metadata, property_type, prim_paths: List[Sdf.Path], additional_label_kwargs = None, additional_widget_kwargs = None)

- class OmniGraphTfTokenAttributeModel(ui.AbstractItemModel, OmniGraphBase)
  - def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], self_refresh: bool, metadata: dict)
  - def clean(self)
  - def get_item_children(self, item)
  - def get_item_value_model(self, item, column_id)
  - def begin_edit(self, item)
  - def end_edit(self, item)
  - def get_value_as_token(self)
  - def is_allowed_token(self, token)

- class PrimAttributeCustomLayoutBase
  - def __init__(self, compute_node_widget)
  - def apply(self, props)

- class PrimPathCustomLayoutBase
  - def __init__(self, compute_node_widget)

- class RandomNodeCustomLayoutBase(DeclarativeCustomLayoutBase)
  - def __init__(self, compute_node_widget, widget_descriptors: dict)
  - def on_use_seed_changed(self, _)

- class ReadPrimsCustomLayoutBase
  - def __init__(self, compute_node_widget)

- class ConversionNodeCustomLayoutBase
  - def __init__(self, compute_node_widget)
  - def apply(self, props)

- class StandaloneAttributeBuilder
  - static def build_ui(attribute: og.Attribute, label_kwd_args: dict[str, Any] = None, value_kwd_args: dict[str, Any] = None) -> tuple[ui.Container, ui.AbstractValueModel]
  - static def get_value_as_string(value_model: ui.AbstractValueModel, elide_big_array: bool = False) -> str
  - static def is_attribute_supported(attribute: og.Attribute) -> bool

## Functions

- def add_create_menu_type(menu_title: str, evaluator_type: str, prefix: str, glyph_file: str, open_editor_fn)
- def build_port_type_convert_menu(port: Sdf.Path) -> ui.Menu
- def find_prop(props: List[UsdPropertyUiEntry], name: str) -> Optional[UsdPropertyUiEntry]
- def remove_create_menu_type(menu_title: str)

## Variables

- SETTING_PAGE_NAME: str
