# Public API for module omni.graph.window.core:

## Classes

- class OmniGraphCatalogTreeDelegate(GraphEditorCoreTreeDelegate)
  - def __init__(self, flat = False)
  - def destroy(self)
  - def build_section_icon(self, model, item, column_id, level, expanded)
  - def build_icon_with_tooltip(self, model, item, column_id, level, expanded)
  - def build_item_widget(self, model, item, column_id, level, expanded)

- class OmniGraphNodeQuickSearchModel(OmniGraphNodeTypeCatalogModel)
  - def execute(self, item)

- class OmniGraphNodeTypeCatalogModel(ui.AbstractItemModel)
  - def __init__(self)
  - def allow_node_type(self, node_type_name: str)
  - def destroy(self)
  - def get_item_children(self, item) -> List[ActionNodeItem]
  - def get_item_value_model_count(self, item)
  - def get_item_value_model(self, item, column_id) -> ui.SimpleStringModel
  - def get_drag_mime_data(self, item)
  - def filter_by_text(self, filter_name_text: str)

- class OmniGraphWindowCoreExtension(omni.ext.IExt)
  - def __init__(self)
  - def on_startup(self, ext_id: str)
  - def on_shutdown(self)

- class ConnectAttrWithSubgraphCommand(omni.kit.commands.Command, UsdStageHelper)
  - def __init__(self, src_path: Sdf.Path, dest_path: Sdf.Path, allow_remove: bool = True, stage = None)
  - def do(self)
  - def undo(self)

- class CreatePortCommand(omni.kit.commands.Command, UsdStageHelper)
  - def __init__(self, prim_path: Sdf.Path, port_name: str, port_type: Sdf.ValueTypeName, stage = None)
  - def do(self)
  - def undo(self)

- class DisconnectAttrWithSubgraphCommand(omni.kit.commands.Command, UsdStageHelper)
  - def __init__(self, src_path: Sdf.Path, dest_path: Sdf.Path, stage = None)
  - def do(self)
  - def undo(self)

- class SubdivideConnectionCommand(omni.kit.commands.Command, UsdStageHelper)
  - def __init__(self, src_to_actual_src: List[Sdf.Path], dest_to_actual_dest: List[Sdf.Path], stage = None)
  - def do(self)
  - def undo(self)

- class OmniGraphNodeDelegate(GraphNodeDelegateBase)
  - def __init__(self, graph_widget: GraphEditorCoreWidget)
  - def destroy(self)
  - def get_node_layout(self, model, node_desc: GraphNodeDescription)
  - def port_input(self, model: OmniGraphModel, node_desc: GraphNodeDescription, port_desc: GraphPortDescription)
  - def port_output(self, model: OmniGraphModel, node_desc: GraphNodeDescription, port_desc: GraphPortDescription)
  - def port(self, model: OmniGraphModel, node_desc: GraphNodeDescription, port_desc: GraphPortDescription)
  - def connection(self, model: OmniGraphModel, source: GraphConnectionDescription, target: GraphConnectionDescription, foreground: bool = False) -> Tuple[ui.ZStack, ui.FreeLine, ui.FreeBezierCurve]
  - def draw_header_label_center(self, model: OmniGraphModel, node: Union[og.Node, Usd.Prim], node_name: str, node_category: str, bg_style_override: str, label_style_override: str)
  - def draw_header_label_left(self, model: OmniGraphModel, node: Union[og.Node, Usd.Prim], node_name: str, node_category: str, bg_style_override: str, label_style_override: str)
  - def draw_header_label_right(self, model: OmniGraphModel, node: Union[og.Node, Usd.Prim], node_name: str, node_category: str, bg_style_override: str, label_style_override: str)
  - def build_header(self, node_name: str, model: OmniGraphModel, node_desc: GraphNodeDescription, error_state: og.Severity)
  - def get_error_state(self, model: OmniGraphModel, node_desc: GraphNodeDescription) -> Tuple[og.Severity, str, Optional[str], Optional[str]]
  - def node_header(self, model: OmniGraphModel, node_desc: GraphNodeDescription)
  - def node_background(self, model: OmniGraphModel, node_desc: GraphNodeDescription)
  - static def specialized_expansion_style(name: str, color_on: int, color_off: int) -> Dict

- class OmniGraphModel(GraphModel, GraphModelBatchPositionHelper)
  - def __init__(self, prim: Usd.Prim)
  - def destroy(self)
  - [property] def name(self, item: Union[og.Node, Usd.Prim, Sdf.Path] = None)
  - [name.setter] def name(self, value, item: Union[og.Node, Usd.Prim, Sdf.Path])
  - [property] def nice_name(self, item = None) -> Optional[str]
  - [property] def type(self, item = None) -> Optional[str]
  - [property] def node_type_name(self, item) -> Optional[str]
  - [property] def description(self, item)
  - [description.setter] def description(self, value, item = None)
  - def is_output(self, item = None) -> bool
  - def is_execution(self, item = None) -> bool
  - [property] def is_execution_pin(self, item = None)
  - def port_tooltip_text(self, item: Sdf.Path) -> str
  - def cull_legacy_prims(self)
  - def cache_graph(self)
  - def cache_nodes(self, graph)
  - [property] def nodes(self, item: Optional[Usd.Prim] = None)
  - def allow_multiple_inputs(self, item: Optional[Union[og.Attribute, Sdf.Path, Usd.Prim]] = None) -> bool
  - def cache_connections(self, node_string: str)
  - [property] def connected_ports(self, item = None)
  - [property] def ports(self, item = None)
  - [property] def inputs(self, item)
  - def remove_port_ui(self, port_path: Sdf.Path)
  - def connect_attribute_ui(self, src_attr_path: Sdf.Path, dest_attr_path: Sdf.Path, connectable_check = False, compatibility_check = False) -> bool
  - def disconnect_attribute_ui(self, dest_attr_path: Sdf.Path)
  - [inputs.setter] def inputs(self, values, item = None)
  - def create_connections(self, dest_attr_path: Sdf.Path, src_attr_path: Sdf.Path)
  - def remove_connections(self, dest_attr_path: Sdf.Path, disconnected_values: List[Sdf.Path])
  - def create_new_subgraph_port(self, src_attr: og.Attribute, dest_prim: Usd.Prim, is_output: bool, force_new_port: bool) -> Sdf.Path
  - [property] def outputs(self, item)
  - [outputs.setter] def outputs(self, value, item = None)
  - def get_output_connections(self, item) -> Optional[List[Sdf.Path]]
  - [property] def display_color(self, item)
  - [display_color.setter] def display_color(self, value, item = None)
  - [property] def position(self, item = None)
  - [position.setter] def position(self, new_position, item = None)
  - def position_begin_edit(self, item)
  - def position_end_edit(self, item)
  - [property] def size(self, item)
  - [size.setter] def size(self, value, item = None)
  - def size_begin_edit(self, item)
  - def size_end_edit(self, item)
  - def og_expansion_state_to_usd(self, og_state: GraphModel.ExpansionState) -> str
  - def usd_expansion_state_to_og(self, usd_state: str) -> GraphModel.ExpansionState
  - def get_default_node_expansion_state(self, node_type_name: str) -> GraphModel.ExpansionState
  - [property] def expansion_state(self, item: Union[Usd.Prim, Sdf.Path] = None) -> GraphModel.ExpansionState
  - [expansion_state.setter] def expansion_state(self, new_value: GraphModel.ExpansionState, item: Union[Usd.Prim, Sdf.Path] = None)
  - [property] def selection(self) -> List[Usd.Prim]
  - [selection.setter] def selection(self, value: List[Usd.Prim])
  - [property] def stacking_order(self, item)
  - def register_graph_event_callback(self, callback: Callable[[og.GraphEvent], None])
  - def create_node_ui(self, node_path: Sdf.Path, graph_path: Sdf.Path)
  - def import_node(self, prim_path: Sdf.Path, graph_path_str: str, node_type: PrimNodeType, window, position: Tuple[float])
  - def create_read_prim_node(self, prim_paths: List[Sdf.Path], graph_path_str: str, window, position: Tuple[float])
  - def create_backdrop(self, graph_path: Sdf.Path, position: Tuple[float])
  - def create_note(self, graph_path: Sdf.Path, position: Tuple[float])
  - def create_node(self, node_type_name: str, graph_path: str, position: Tuple[float], node_name: str = None)
  - def create_subgraph_node(self, graph_path: str, position: Tuple[float])
  - def create_compound(self, compound_name: str, compound_namespace: str, selected_nodes: List[Usd.Prim])
  - def create_subgraph_compound(self, selected_nodes: List[Usd.Prim])
  - def get_graph(self, graph_path: str)
  - def is_graph(self, item: Sdf.Path)
  - def get_attribute_from_path(self, attr_path: Sdf.Path) -> Optional[og.Attribute]
  - def get_path_from_attribute(self, attr: og.Attribute) -> Sdf.Path
  - def traverse_actual_dests(self, ports: List[Sdf.Path], results: List[List[Sdf.Path]])
  - def get_actual_dests(self, port: Sdf.Path) -> List[List[Sdf.Path]]
  - def get_actual_source(self, port_path: Sdf.Path) -> List[Sdf.Path]
  - def get_event_stream(self) -> carb.events.IEventStream
  - def get_port_type(self, path: Sdf.Path) -> Optional[str]
  - def get_usd_port_type(self, attr_path: Sdf.Path) -> Sdf.ValueTypeName
  - def get_next_free_name(self, base_name, node_path: Sdf.Path)
  - def get_node_from_prim(self, prim: Union[Usd.Prim, Sdf.Path]) -> Optional[og.Node]
  - def is_pseudo_node(self, prim_or_path: Union[Usd.Prim, Sdf.Path])
  - def find_next_position_descending(self, pos: Tuple[float]) -> Tuple[float]
  - def special_select_widget(self, node, node_widget)
  - static def make_nice_name(ugly_name: str, preserve_final_part: bool = False)
  - [deprecated] def create_compound_from_selection(self, compound_name: str, compound_namespace: str)
  - [deprecated] [property] def selected_nodes(self) -> List[Usd.Prim]

- class OmniGraphWidget(GraphEditorCoreWidget)
  - def __init__(self, graph_model_class: Optional[Type[OmniGraphModel]] = None, graph_delegate: Optional[OmniGraphNodeDelegate] = None, catalog_model: Optional[OmniGraphNodeTypeCatalogModel] = None, variables_model: Optional[OmniGraphVariablesModel] = None, context_menu_class: Optional[Type[OmniGraphNodeContextMenu]] = None, filter_fn: Optional[Callable[[Sdf.Path, Sdf.PrimSpec], bool]] = None)
  - def destroy(self)
  - [property] def model(self)
  - [model.setter] def model(self, model)
  - def on_build_graph(self)
  - def on_add_variable(self)
  - def on_build_variable_value_widget(self, item: ui.AbstractItem) -> bool
  - def on_drag_variable_readwrite(self, item: ui.AbstractItem, operation: str) -> str
  - def is_graph_editable(self, graph: og.Graph) -> bool
  - def on_build_startup(self)
  - def on_build_catalog(self)
  - def on_build_breadcrumbs(self)
  - def choose_prim_node_dialog(self, prim_paths: Union[str, Sdf.Path, List[str], List[Sdf.Path]], graph_path: str, position: Tuple[float], window_position: Optional[Tuple[float]] = None)
  - def create_variable_node_dialog(self, variable_name, position: Tuple[float], window_position: Optional[Tuple[float]] = None)
  - def create_graph(self, evaluator_type: str, name_prefix: str, menu_arg = None, value = None, use_dialog = False)
  - [property] def current_compound(self) -> Usd.Prim | None
  - def enter_compound(self, item: Usd.Prim, focus = True)
  - def on_accept_drop(self, drop_data: str)
  - def get_prim_drop_menu_items(self) -> List[Tuple[str, str, Callable[[OmniGraphModel, Sdf.Path, str, ui.Window, Tuple[float]], None], Callable[[str, Sdf.Path], bool]]]
  - def get_prim_drop_menu_items2(self) -> List[Tuple[str, str, Callable[[OmniGraphModel, Sdf.Path, str, ui.Window, Tuple[float]], None], Callable[[str, Sdf.Path], bool], bool]]
  - def on_drop(self, event: ui.WidgetMouseDropEvent)
  - def on_left_mouse_button_double_clicked(self, items: List[Usd.Prim])
  - def get_specialized_style(self)
  - def on_toolbar_create_graph_clicked(self)
  - def on_toolbar_edit_graph_clicked(self)
  - def on_toolbar_expansion_state_clicked(self, state)
  - def on_toolbar_onframe_clicked(self)
  - def on_toolbar_addnote_clicked(self)
  - def on_toolbar_view_clicked(self)
  - def on_toolbar_edit_clicked(self)
  - def on_toolbar_help_clicked(self)
  - def on_use_prim_name_clicked(self, Value)
  - def on_frame_selected_clicked(self)
  - def on_layout_clicked(self)
  - def show_context_menu(self, context_item, pos: Tuple[float, float] | None = None)
  - def get_event_stream(self) -> carb.events.IEventStream

- class OmniGraphWindow(ui.Window)
  - def __init__(self, title, **kwargs)
  - def destroy(self)
  - def on_build_window(self)

## Functions

- def register_stage_graph_opener(can_open_fn: Callable[[bool], list[Usd.Prim]], open_fn: Callable[[None], list[Usd.Prim]], priority: int = 0) -> Any

## Other

- omni.graph.core: public module
