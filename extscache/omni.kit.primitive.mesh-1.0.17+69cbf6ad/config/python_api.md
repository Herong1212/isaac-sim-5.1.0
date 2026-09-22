# Public API for module omni.kit.primitive.mesh:

## Classes

- class AbstractShapeEvaluator
  - def __init__(self, attributes: dict)
  - def eval(self, **kwargs) -> Tuple[List[Gf.Vec3f], List[Gf.Vec3f], List[Gf.Vec2f], List[int], List[int]]
  - static def build_setting_ui()
  - static def reset_setting()
  - static def get_default_half_scale()

- class CreateMeshPrimCommand(CreateMeshPrimWithDefaultXformCommand)
  - def __init__(self, prim_type: str, **kwargs)

- class CreateMeshPrimWithDefaultXformCommand(omni.kit.commands.Command)
  - def __init__(self, prim_type: str, **kwargs)
  - def do(self)
  - def undo(self)

## Functions

- def get_geometry_mesh_prim_list()
