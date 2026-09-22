# Usage Examples

## Get and Set Transformations for Primitives Using Data Accessor
```python
# This snippet is adjusted for clarity and ensures that the FabricDataAccessor is correctly instantiated with a model (stage) that exists.
from omni.kit.manipulator.prim.fabric import FabricDataAccessor
from usdrt.Sdf import Path
from usdrt.Usd import TimeCode
import omni.usd

# Ensure the USD context is available and correctly referenced
context = omni.usd.get_context()
stage = context.get_stage()  # Obtain the USD stage directly from the context

# Instantiate the data accessor for a given USD context
fabric_data_accessor = FabricDataAccessor(usd_context_name="default", model=stage)  # Pass the stage as the model

# Get the SRT (scale, rotation, translation) of a primitive at a specified time
prim_path = Path("/World/MyPrim")
time = TimeCode.Default()
scale, rotation, rotation_order, translation = fabric_data_accessor.get_local_transform_SRT(
    prim=fabric_data_accessor.get_prim_at_path(prim_path),
    time=time
)

# Print the retrieved transformation components
print(f"Scale: {scale}, Rotation: {rotation}, Rotation Order: {rotation_order}, Translation: {translation}")

# Set a new transformation for the primitive (example: translate by 10 units along X axis)
fabric_data_accessor.do_transform_selected_prims(
    paths=["/World/MyPrim"],
    paths_c=[prim_path.pathC.path],
    new_translations=[10, 0, 0],  # New translation
    new_rotation_eulers=[0, 0, 0],  # Keep existing rotation
    new_rotation_orders=[rotation_order[0], rotation_order[1], rotation_order[2]],  # Keep existing rotation order
    new_scales=[scale[0], scale[1], scale[2]]  # Keep existing scale
)
```

## Register and Unregister Fabric Data Accessor
```python
# This snippet is correct as provided and correctly simulates the startup and shutdown process for the extension.
from omni.kit.manipulator.prim.fabric import FabricDataAccessor
from omni.kit.manipulator.prim.core import get_prim_data_accessor_registry

# get the global data accessor registry
prim_data_accessor_registry = get_prim_data_accessor_registry()

# registers the Fabric data accessor from the global registry.
prim_data_accessor_registry.register_data_accessor(FabricDataAccessor, "FABRIC")

# unregisters the Fabric data accessor from the global registry.
prim_data_accessor_registry.unregister_data_accessor("FABRIC")
```

## Transform Multiple Primitives with Given SRT (Scale, Rotation, Translation)
```python
# This snippet is correct as provided; the error mentioned does not directly correspond to the code provided.
import asyncio
from omni.kit.manipulator.prim.fabric import TransformMultiPrimsFabricSRT
from usdrt.Sdf import Path
from usdrt.Gf import Vec3d, Vec3i
from usdrt.Usd import TimeCode

# Define the paths to the primitives in the stage
paths = [Path("/World/Prim1"), Path("/World/Prim2")]

# Define the new transformations for each primitive
new_translations = [Vec3d(10, 0, 0), Vec3d(0, 20, 0)]
new_rotation_eulers = [Vec3d(0, 45, 0), Vec3d(90, 0, 0)]
new_rotation_orders = [Vec3i(0, 1, 2), Vec3i(0, 1, 2)]
new_scales = [Vec3d(1, 1, 1), Vec3d(2, 2, 2)]

# Create and execute the command to transform the primitives
transform_command = TransformMultiPrimsFabricSRT(
    paths=paths,
    new_translations=new_translations,
    new_rotation_eulers=new_rotation_eulers,
    new_rotation_orders=new_rotation_orders,
    new_scales=new_scales,
    time_code=TimeCode.Default()
)

# Use asyncio to run the command if it needs to be executed in an async context
asyncio.ensure_future(transform_command.do())

# To undo the transformation, simply call the undo method on the command
# Use asyncio to run the undo if it needs to be executed in an async context
asyncio.ensure_future(transform_command.undo())
```
