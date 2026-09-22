# Public API for module omni.kit.widget.graph:

## Classes

- class AbstractBatchPositionGetter(abc.ABC)
  - def __init__(self, model: GraphModel)
  - [property] def model(self)
  - [model.setter] def model(self, value)

- class AbstractGraphNodeDelegate
  - def destroy(self)
  - def get_node_layout(self, model, node_desc: GraphNodeDescription)
  - def node_background(self, model, node_desc: GraphNodeDescription)
  - def node_header_input(self, model, node_desc: GraphNodeDescription)
  - def node_header_output(self, model, node_desc: GraphNodeDescription)
  - def node_header(self, model, node_desc: GraphNodeDescription)
  - def node_footer(self, model, node_desc: GraphNodeDescription)
  - def port_input(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription)
  - def port_output(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription)
  - def port(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription)
  - def connection(self, model, source_desc: GraphConnectionDescription, target_desc: GraphConnectionDescription, foreground: bool = False)

- class GraphConnectionDescription
  - def __init__(self, node, port, widget, level, is_tangent_reversed = False)

- class GraphNodeDescription
  - def __init__(self, node, connected_source = None, connected_target = None)

- class GraphNodeLayout(Enum)
  - LIST: Unknown
  - COLUMNS: Unknown
  - HEAP: Unknown

- class GraphPortDescription
  - def __init__(self, port, level, relative_position, parent_child_count, connected_source = None, connected_target = None)

- class BackdropDelegate(GraphNodeDelegateFull)
  - def node_header(self, model, node_desc: GraphNodeDescription)
  - def node_background(self, model, node_desc: GraphNodeDescription)
  - def node_footer(self, model, node_desc: GraphNodeDescription)

- class BackdropGetter(AbstractBatchPositionGetter)
  - def __init__(self, model: GraphModel, is_backdrop_fn: Callable[[Any], bool], graph_widget = None)

- class CompoundInputOutputNodeDelegate(GraphNodeDelegateFull)
  - def __init__(self)
  - def destroy(self)
  - def port_input(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription)
  - def port_output(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription)
  - def port(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription)

- class CompoundNodeDelegate(GraphNodeDelegateFull)

- class GraphModel
  - class ExpansionState(Enum)
    - OPEN: int
    - MINIMIZED: int
    - CLOSED: int
  - class PreviewState(IntFlag)
    - NONE: int
    - OPEN: Unknown
    - CACHED: Unknown
    - LARGE: Unknown
  - DISPLAY_NAME: NoneType
  - def __init__(self)
  - def subscribe_item_changed(self, fn)
  - def subscribe_selection_changed(self, fn)
  - def subscribe_node_changed(self, fn)
  - static def has_nodes(obj)
  - [property] def name(self, item) -> str
  - [name.setter] def name(self, value: str, item = None)
  - [property] def type(self, item)
  - [property] def inputs(self, item)
  - [inputs.setter] def inputs(self, value, item = None)
  - [property] def outputs(self, item)
  - [outputs.setter] def outputs(self, value, item = None)
  - [property] def nodes(self, item = None)
  - [property] def ports(self, item = None)
  - [ports.setter] def ports(self, value, item = None)
  - [property] def expansion_state(self, item = None) -> ExpansionState
  - [expansion_state.setter] def expansion_state(self, value: ExpansionState, item = None)
  - def can_connect(self, source, target)
  - [property] def position(self, item = None)
  - [position.setter] def position(self, value, item = None)
  - def position_begin_edit(self, item)
  - def position_end_edit(self, item)
  - [property] def size(self, item)
  - [size.setter] def size(self, value, item = None)
  - def size_begin_edit(self, item)
  - def size_end_edit(self, item)
  - [property] def description(self, item)
  - [description.setter] def description(self, value, item = None)
  - [property] def display_color(self, item)
  - [display_color.setter] def display_color(self, value, item = None)
  - [property] def stacking_order(self, item)
  - [property] def selection(self)
  - [selection.setter] def selection(self, value: list)
  - def special_select_widget(self, node, node_widget)
  - def destroy(self)
  - [property] def icon(self, item) -> Optional[Union[str, Any]]
  - [icon.setter] def icon(self, value: Optional[Union[str, Any]], item = None)
  - [property] def preview(self, item) -> Optional[Union[str, Any]]
  - [preview.setter] def preview(self, value: Optional[Union[str, Any]], item = None)
  - [property] def preview_state(self, item) -> PreviewState
  - [preview_state.setter] def preview_state(self, value: PreviewState, item = None)
  - [property] def add_empty_input_port(self, item) -> bool
  - [property] def add_empty_output_port(self, item) -> bool

- class GraphModelBatchPositionHelper
  - def __init__(self)
  - [property] def batch_proxy(self)
  - [batch_proxy.setter] def batch_proxy(self, value)
  - def add_get_moving_items_fn(self, fn: Callable[[Any], List[Any]])
  - def batch_set_position(self, position: List[float], item: Any = None)
  - def batch_position_begin_edit(self, item: Any)
  - def batch_position_end_edit(self, item: Any)

- class GraphNodeDelegate(GraphNodeDelegateRouter)
  - def __init__(self)
  - static def get_style()
  - static def specialized_color_style(name, color, icon, icon_tint_color = None)
  - static def specialized_port_style(name, color)

- class GraphNodeDelegateRouter(AbstractGraphNodeDelegate)
  - def __init__(self)
  - def add_route(self, delegate: AbstractGraphNodeDelegate, type = None, expression = None)
  - def get_node_layout(self, model, node_desc: GraphNodeDescription)
  - def node_background(self, model, node_desc: GraphNodeDescription)
  - def node_header_input(self, model, node_desc: GraphNodeDescription)
  - def node_header_output(self, model, node_desc: GraphNodeDescription)
  - def node_header(self, model, node_desc: GraphNodeDescription)
  - def node_footer(self, model, node_desc: GraphNodeDescription)
  - def port_input(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription)
  - def port_output(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription)
  - def port(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription)
  - def connection(self, model, source: GraphConnectionDescription, target: GraphConnectionDescription, foreground: bool = False)
  - def destroy(self)

- class GraphView
  - DEFAULT_DISTANCE_BETWEEN_NODES: float
  - def __init__(self, **kwargs)
  - def subscribe_post_delayed_build_layout(self, fn)
  - def subscribe_pre_delayed_build_layout(self, fn)
  - def subscribe_empty_connection_drop(self, fn)
  - def layout_all(self)
  - def set_expansion(self, state: GraphModel.ExpansionState)
  - [property] def raster_nodes(self)
  - [property] def model(self)
  - [model.setter] def model(self, model)
  - [property] def virtual_ports(self)
  - [virtual_ports.setter] def virtual_ports(self, value)
  - def set_model(self, model: GraphModel)
  - def set_delegate(self, delegate: AbstractGraphNodeDelegate)
  - def filter_upstream(self, nodes: list)
  - def get_bbox_of_nodes(self, nodes: list)
  - def focus_on_nodes(self, nodes: Optional[List[Any]] = None)
  - [property] def selection(self)
  - [selection.setter] def selection(self, value)
  - def destroy(self)
  - [property] def zoom(self)
  - [zoom.setter] def zoom(self, value)
  - [property] def zoom_min(self)
  - [zoom_min.setter] def zoom_min(self, value)
  - [property] def zoom_max(self)
  - [zoom_max.setter] def zoom_max(self, value)
  - [property] def pan_x(self)
  - [pan_x.setter] def pan_x(self, value)
  - [property] def pan_y(self)
  - [pan_y.setter] def pan_y(self, value)

- class IsolationGraphModel
  - class MagicWrapperMeta(type)
    - def __init__(cls, name, bases, dct)
  - class EmptyPort
    - def __init__(self, parent: Union[IsolationGraphModel.InputNode, IsolationGraphModel.OutputNode])
    - static def get_type_name() -> str
  - class InputNode
    - def __init__(self, model: GraphModel, source)
    - static def get_type_name() -> str
    - [property] def ports(self) -> Optional[List[Any]]
  - class OutputNode
    - def __init__(self, model: GraphModel, source)
    - static def get_type_name() -> str
    - [property] def ports(self) -> Optional[List[Any]]
  - def __init__(self, model: GraphModel, root)
  - def destroy(self)
  - def clear_caches(self)
  - def add_input_or_output(self, position: Tuple[float], is_input: bool = True)
  - def subscribe_item_changed(self, fn)
  - def subscribe_selection_changed(self, fn)
  - def subscribe_node_changed(self, fn)
  - [property] def nodes(self, item: Any = None)
  - def can_connect(self, source: Any, target: Any)
  - def position_begin_edit(self, item: Any)
  - def position_end_edit(self, item: Any)
  - [property] def selection(self) -> Optional[List[Any]]
  - [selection.setter] def selection(self, value: Optional[List[Any]])

- class SelectionGetter(AbstractBatchPositionGetter)
  - def __init__(self, model: GraphModel)
