# Public API for module omni.kit.stage.copypaste:

## Classes

- class ImportLayerCommand(omni.kit.commands.Command, UsdStageHelper)
  - def __init__(self, layer: Sdf.Layer, root: Sdf.Path = Sdf.Path.absoluteRootPath, stage: Optional[Usd.Stage] = None, filter_fn: Optional[Callable] = None)
  - def do(self)
  - def undo(self)

## Functions

- [deprecated] def update_property_paths(prim_spec, old_path, new_path)
- [deprecated] def get_prim_as_text(stage: Usd.Stage, prim_paths: List[Sdf.Path]) -> Optional[str]
- [deprecated] def text_to_stage(stage: Usd.Stage, text: str, root: Sdf.Path = Sdf.Path.absoluteRootPath, keep_inputs = True, position = None, filter_fn: Optional[Callable] = None) -> bool
