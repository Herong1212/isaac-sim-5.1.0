# Public API for module omni.kit.window.material_graph:

## Classes

- class GraphExtension(omni.ext.IExt, MenuHelperExtensionFull)
  - def __init__(self)
  - def on_startup(self, ext_id: str)
  - def on_shutdown(self)
  - static def refresh_compounds()
  - static def show_materials(prim_list: List[Usd.Prim])
  - static def add_node(mime_data: str)
  - def show_window(self, menu, value, index)
  - def layout_all(self)
  - def focus_on_nodes(self, nodes: Optional[List[Any]] = None)
  - def set_expansion(self, mode: str)
  - def graph_copy(self)
  - def graph_paste(self)
  - static def filter_paste_nodes(prim_spec: Sdf.PrimSpec) -> bool
  - def toggle_material_compilation(self)
  - def material_unpause_and_pause(self)

- class ConnectUsdShadeToSourceCommand(omni.kit.commands.Command)
  - def __init__(self, target: UsdShade.Input, source: UsdShade.Output)
  - def do(self)
  - def undo(self)

- class CreateInputPortCommand(CreateAbstractPortCommand)
  - def __init__(self, prim_path: Sdf.Path, port_name: str, port_type: Sdf.ValueTypeName, stage = None)

- class CreateOutputPortCommand(CreateAbstractPortCommand)
  - def __init__(self, prim_path: Sdf.Path, port_name: str, port_type: Sdf.ValueTypeName, stage = None)

- class ImportCompoundCommand(omni.kit.commands.Command, UsdStageHelper)
  - def __init__(self, parent_path: Sdf.Path, source_asset: str, identifier: str, position: Optional[List[int]] = None, stage = None, path = None, attributes_to_set: Optional[Dict[Sdf.Path, Any]] = None)
  - def do(self)
  - def undo(self)

- class NewUsdShadeMaterialCommand(omni.kit.commands.Command, UsdStageHelper)
  - def __init__(self, parent_path: Sdf.Path, identifier: str, position: Optional[Tuple[int]] = None, select_new_prim: bool = False, stage: Optional[Usd.Stage] = None, context_name: Optional[str] = None)
  - def do(self)
  - def undo(self)

- class NewUsdShadeNodeCommand(omni.kit.commands.Command, UsdStageHelper)
  - def __init__(self, parent_path, source_asset, sub_identifier, position, node, stage = None)
  - def do(self)
  - def undo(self)

- class NewUsdShadeNodeGraphCommand(omni.kit.commands.Command, UsdStageHelper)
  - def __init__(self, parent_path, identifier, position, stage = None)
  - def do(self)
  - def undo(self)

- class UsdShadeDisconnectSourceCommand(omni.kit.commands.Command)
  - def __init__(self, target: UsdShade.Input)
  - def do(self)
  - def undo(self)

## Other



# Public API for module omni.kit.window.material_graph.compound_registry:

## Classes

- class CompoundShadingNode
  - def __init__(self, prim: Usd.Prim, path: str)
  - [property] def customData(self)
  - [property] def colorSpace(self)
  - [property] def sdrMetaData(self)
  - [property] def name(self)
  - [property] def parameters(self)
  - [property] def category(self)
  - [property] def description(self)
  - [property] def sourceAsset(self)
  - [property] def subIdentifier(self)
  - [property] def uiOrder(self)
  - [property] def tags(self)
  - [property] def outputs(self)
  - [property] def displayName(self)
  - [property] def thumbnail(self)

## Functions

- def register_compound(path: str)
- def nodes()


# Public API for module omni.kit.window.material_graph.shader_registry:

## Classes

- class ShaderRegistry
  - def __init__(self)
  - def Get(self, context)

## Functions

- def Singleton(class_)
