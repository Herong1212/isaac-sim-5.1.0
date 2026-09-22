# Usage Examples

## Add Translation, Rotation, and Scale Operations

```python
import omni.usd
import omni.kit.commands
from omni.kit.property.transform import AddXformOpCommand

# Ensure the omni.usd extension is enabled
omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate("omni.usd", True)

# Get the current stage
stage = omni.usd.get_context().get_stage()

# Check if the stage is valid
if stage:
    prim_path = "/World/MyPrim"
    # Check if the primitive exists
    prim = stage.GetPrimAtPath(prim_path)
    if prim:
        # Create a command to add transform operations to the primitive
        add_xform_op_command = AddXformOpCommand(
            payload={'stage': stage, 'prim_paths': [prim_path]},
            precision=None,
            rotation_order="XYZ",
            add_translate_op=True,
            add_orient_op=True,
            add_scale_op=True,
            add_transform_op=False,
            add_pivot_op=False
        )
        
        # Execute the command to add the operations
        omni.kit.commands.execute(add_xform_op_command)
```

## Change Rotation Operation

```python
import omni.usd
from omni.kit.property.transform import ChangeRotationOpCommand
from pxr import UsdGeom

# Ensure the omni.usd extension is enabled
omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate("omni.usd", True)

# Get the current stage
stage = omni.usd.get_context().get_stage()

# Check if the stage is valid
if stage:
    prim_path = "/World/MyPrim"
    # Get the rotate operation attribute
    rotate_attr = UsdGeom.Xformable(stage.GetPrimAtPath(prim_path)).GetOrderedXformOps()[0]
    
    # Create a command to change the rotation operation from ZYX to XYZ
    change_rotation_op_command = ChangeRotationOpCommand(
        src_op_attr_path=rotate_attr.GetPath(),
        op_name="rotateXYZ",
        dst_op_attr_name="xformOp:rotateXYZ",
        is_inverse_op=False
    )
    
    # Execute the command to apply the change
    omni.kit.commands.execute(change_rotation_op_command)
```

## Remove Transformation Operation

```python
import omni.usd
from omni.kit.property.transform import RemoveXformOpCommand
from pxr import UsdGeom

# Ensure the omni.usd extension is enabled
omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate("omni.usd", True)

# Get the current stage
stage = omni.usd.get_context().get_stage()

# Check if the stage is valid
if stage:
    xformable = UsdGeom.Xformable(stage.GetPrimAtPath("/World/MyPrim"))
    
    # Get the xformOpOrder attribute
    xform_op_order_attr = xformable.GetXformOpOrderAttr()
    xform_ops = xformable.GetOrderedXformOps()
    xform_op_to_remove = xform_ops[0]  # Remove the first operation
    
    # Create a command to remove the first xform operation
    remove_xform_op_command = RemoveXformOpCommand(
        op_order_attr_path=xform_op_order_attr.GetPath(),
        op_name=xform_op_to_remove.GetOpName(),
        op_order_index=0  # Index of the operation in the xformOpOrder attribute
    )
    
    # Execute the command to remove the operation
    omni.kit.commands.execute(remove_xform_op_command)
```

## Remove Transformation Operation and Its Attribute

```python
import omni.usd
from omni.kit.property.transform import RemoveXformOpAndAttrbuteCommand
from pxr import UsdGeom

# Ensure the omni.usd extension is enabled
omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate("omni.usd", True)

# Get the current stage
stage = omni.usd.get_context().get_stage()

# Check if the stage is valid
if stage:
    xformable = UsdGeom.Xformable(stage.GetPrimAtPath("/World/MyPrim"))
    
    # Get the xformOpOrder attribute
    xform_op_order_attr = xformable.GetXformOpOrderAttr()
    xform_ops = xformable.GetOrderedXformOps()
    xform_op_to_remove = xform_ops[0]  # Remove the first operation
    
    # Create a command to remove the first xform operation and its attribute
    remove_xform_op_and_attribute_command = RemoveXformOpAndAttrbuteCommand(
        op_order_attr_path=xform_op_order_attr.GetPath(),
        op_name=xform_op_to_remove.GetOpName(),
        op_order_index=0  # Index of the operation in the xformOpOrder attribute
    )
    
    # Execute the command to remove the operation and its attribute
    omni.kit.commands.execute(remove_xform_op_and_attribute_command)
```

## Enable Transformation Operation

```python
import omni.usd
from omni.kit.property.transform import EnableXformOpCommand

# Ensure the omni.usd extension is enabled
omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate("omni.usd", True)

# Get the current stage
stage = omni.usd.get_context().get_stage()

# Check if the stage is valid
if stage:
    xform_op_attr_path = "/World/MyPrim.xformOp:translate"
    
    # Create a command to enable the translate xformOp
    enable_xform_op_command = EnableXformOpCommand(op_attr_path=xform_op_attr_path)
    
    # Execute the command to enable the translate operation
    omni.kit.commands.execute(enable_xform_op_command)
```

