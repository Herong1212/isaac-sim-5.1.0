# Public API for module omni.fabric.commands:

## Classes

- class DeleteFabricPrimsCommand(omni.kit.commands.Command, FabricStageHelper)
  - def __init__(self, paths: list[Union[str, usdrt.Sdf.Path]], delete_descendents: bool = True, stage: Optional[usdrt.Usd.Stage] = None, context_name: Optional[str] = None)
  - def do(self)
  - def undo(self)

- class MoveFabricPrimCommand(omni.kit.commands.Command)
  - def __init__(self, path_from: Union[str, usdrt.Sdf.Path], path_to: Union[str, usdrt.Sdf.Path], time_code: usdrt.Usd.TimeCode = usdrt.Usd.TimeCode.Default(), keep_world_transform: bool = True, on_move_fn: Callable = None, stage_or_context: Union[str, usdrt.Usd.Stage, omni.usd.UsdContext] = None)
  - def do(self)
  - def undo(self)

- class MoveFabricPrimsCommand(omni.kit.commands.Command)
  - def __init__(self, paths_to_move: Dict[str, str], time_code: usdrt.Usd.TimeCode = usdrt.Usd.TimeCode.Default(), keep_world_transform: bool = True, on_move_fn: Callable = None, stage_or_context: Union[str, usdrt.Usd.Stage, omni.usd.UsdContext] = None)
  - def do(self)
  - def undo(self)

- class ToggleVisibilitySelectedFabricPrimsCommand(omni.kit.commands.Command)
  - def __init__(self, selected_paths: List[str], stage: Optional[usdrt.Usd.Stage] = None)
  - def do(self)
  - def undo(self)

- class CreateFabricPrimWithDefaultXformCommand(omni.kit.commands.Command, FabricStageHelper)
  - attr_type_table: Dict
  - default_size_attr_table: Dict
  - def __init__(self, prim_type: str, prim_path: str = None, select_new_prim: bool = True, attributes: Dict[str, Any] = {}, create_default_xform = True, stage: Optional[usdrt.Usd.Stage] = None, context_name: Optional[str] = None)
  - def do(self)
  - def undo(self)

- class CreateDefaultXformOnFabricPrimCommand(omni.kit.commands.Command)
  - def __init__(self, prim_path: str, stage: usdrt.Usd.Stage)
  - def do(self)
  - def undo(self)

- class CreateFabricPrimCommand(CreateFabricPrimWithDefaultXformCommand)
  - def __init__(self, prim_type: str, prim_path: str = None, select_new_prim: bool = True, attributes: Dict[str, Any] = {}, create_default_xform = True, stage: Optional[usdrt.Usd.Stage] = None, context_name: Optional[str] = None)

- class GroupFabricPrimsCommand(omni.kit.commands.Command, FabricStageHelper)
  - def __init__(self, prim_paths: List[Union[str, Sdf.Path]], stage: Optional[usdrt.Usd.Stage] = None, context_name: Optional[str] = None)
  - def do(self)
  - def undo(self)

- class UngroupFabricPrimsCommand(omni.kit.commands.Command, FabricStageHelper)
  - def __init__(self, prim_paths: List[Union[str, usdrt.Sdf.Path]], stage: Optional[usdrt.Usd.Stage] = None, context_name: Optional[str] = None)
  - def do(self)
  - def undo(self)

- class TransformFabricPrimCommand(omni.kit.commands.Command)
  - def __init__(self, path: str, new_transform_matrix: usdrt.Gf.Matrix4d, old_transform_matrix: usdrt.Gf.Matrix4d = None, is_world_xform: bool = False, time_code: usdrt.Usd.TimeCode = usdrt.Usd.TimeCode.Default(), usd_context_name: str = '')
  - def do(self)
  - def undo(self)

- class CopyFabricPrimCommand(omni.kit.commands.Command)
  - def __init__(self, path_from: str, path_to: str = None, exclusive_select: bool = True, usd_context_name: str = '')
  - def do(self)
  - def undo(self)

- class CopyFabricPrimsCommand(omni.kit.commands.Command)
  - def __init__(self, paths_from: list[str], paths_to: list[str] = None)
  - def do(self)
  - def undo(self)

- class ChangeFabricPropertyCommand(omni.kit.commands.Command)
  - def __init__(self, prop_path: str, value: Any, prev: Any, timecode = usdrt.Usd.TimeCode.Default(), type_to_create_if_not_exist: usdrt.Sdf.ValueTypeNames = None, usd_context_name: Union[str, omni.usd.UsdContext, Usd.Stage, usdrt.Usd.Stage] = '', is_custom: bool = False)
  - def do(self)
  - def undo(self)

- class ChangeFabricAttributeCommand(omni.kit.commands.Command)
  - def __init__(self, attr_path: str, value: Any, prev: Any, timecode = usdrt.Usd.TimeCode.Default(), type_to_create_if_not_exist: usdrt.Sdf.ValueTypeNames = None, stage: usdrt.Usd.Stage = None, is_custom: bool = False)
  - def do(self)
  - def undo(self)

- class FabricCommandsExtension(omni.ext.IExt)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

## Other

- omni.ext: public module
- omni.usd: public module
