# Public API for module omni.kit.property.transform:

## Classes

- class TransformPropertyExtension(omni.ext.IExt)
  - def __init__(self)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

- class EnableXformOpCommand(omni.kit.commands.Command)
  - def __init__(self, op_attr_path: str)
  - def do(self)
  - def undo(self)

- class ChangeRotationOpCommand(omni.kit.commands.Command)
  - def __init__(self, src_op_attr_path: str, op_name: str, dst_op_attr_name: str, is_inverse_op: bool, auto_target_layer: bool = True)
  - def do(self)
  - def undo(self)

- class RemoveXformOpCommand(omni.kit.commands.Command)
  - def __init__(self, op_order_attr_path: str, op_name: str, op_order_index: int)
  - def do(self)
  - def undo(self)

- class RemoveXformOpAndAttrbuteCommand(omni.kit.commands.Command)
  - def __init__(self, op_order_attr_path: str, op_name: str, op_order_index: int)
  - def do(self)
  - def undo(self)

- class AddXformOpCommand(omni.kit.commands.Command)
  - def __init__(self, payload, precision, rotation_order, add_translate_op, add_orient_op, add_scale_op, add_transform_op, add_pivot_op, add_rotateXYZ_op = None, add_rotate_xyz_op = None)
  - def do(self)
  - def undo(self)
