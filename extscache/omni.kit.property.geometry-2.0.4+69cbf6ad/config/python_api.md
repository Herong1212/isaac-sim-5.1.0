# Public API for module omni.kit.property.geometry:

## Classes

- class PrimVarCommand(omni.kit.commands.Command)
  - def __init__(self, prim_path: List[str], prim_name: str, prim_type: str, value: Any, usd_context_name: Optional[str] = '')
  - def do(self)
  - def undo(self)

- class TogglePrimVarCommand(omni.kit.commands.Command)
  - def __init__(self, prim_path: List[str], prim_name: str, usd_context_name: Optional[str] = '')
  - def do(self)
  - def undo(self)

- class ToggleInstanceableCommand(omni.kit.commands.Command)
  - def __init__(self, prim_path: List[str], usd_context_name: Optional[str] = '')
  - def do(self)
  - def undo(self)

- class GeometryPropertyExtension(omni.ext.IExt)
  - def __init__(self)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - def register_custom_visual_attribute(self, attribute_name: str, display_name: str, type_name: str, default_value: Any, predicate: Callable[[Any], bool] = None)
  - def deregister_custom_visual_attribute(self, attribute_name: str)

## Functions

- def get_instance()
