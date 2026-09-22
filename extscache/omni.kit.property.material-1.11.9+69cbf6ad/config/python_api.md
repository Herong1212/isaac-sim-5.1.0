# Public API for module omni.kit.property.material:

## Classes

- class UsdShadeDisconnectCommand(omni.kit.commands.Command)
  - def __init__(self, target: UsdShade.Input)
  - def do(self)
  - def undo(self)

- class SetUsdShadeInfoAttributeCommand(ChangePropertyCommand)
  - def __init__(self, prop_path: str, value: Any, prev: Any, timecode = None, type_to_create_if_not_exist: Sdf.ValueTypeNames = None, target_layer: Sdf.Layer = None, usd_context_name: Union[str, omni.usd.UsdContext, Usd.Stage] = '', is_custom: bool = False, variability: Sdf.Variability = Sdf.VariabilityVarying)
  - def undo(self)
