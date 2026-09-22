
# Usage Examples

## Get and Set Transformations for Primitives Using Data Accessor
```python
# This snippet is adjusted for clarity and ensures that the UsdDataAccessor is correctly instantiated with a model (stage) that exists.
from omni.kit.manipulator.prim.usd import UsdDataAccessor
from usdrt.Sdf import Path
from usdrt.Usd import TimeCode
import omni.usd

# Ensure the USD context is available and correctly referenced
context = omni.usd.get_context()
stage = context.get_stage()  # Obtain the USD stage directly from the context

# Instantiate the data accessor for a given USD context
usd_data_accessor = UsdDataAccessor(usd_context_name="default", model=stage)  # Pass the stage as the model

# Get the SRT (scale, rotation, translation) of a primitive at a specified time
prim_path = Path("/World/MyPrim")
time = TimeCode.Default()
scale, rotation, rotation_order, translation = usd_data_accessor.get_local_transform_SRT(
    prim=usd_data_accessor.get_prim_at_path(prim_path),
    time=time
)

# Print the retrieved transformation components
print(f"Scale: {scale}, Rotation: {rotation}, Rotation Order: {rotation_order}, Translation: {translation}")

# Set a new transformation for the primitive (example: translate by 10 units along X axis)
usd_data_accessor.do_transform_selected_prims(
    paths=["/World/MyPrim"],
    paths_c=[prim_path.pathC.path],
    new_translations=[10, 0, 0],  # New translation
    new_rotation_eulers=[0, 0, 0],  # Keep existing rotation
    new_rotation_orders=[rotation_order[0], rotation_order[1], rotation_order[2]],  # Keep existing rotation order
    new_scales=[scale[0], scale[1], scale[2]]  # Keep existing scale
)
```

## Register and Unregister Usd Data Accessor
```python
# This snippet is correct as provided and correctly simulates the startup and shutdown process for the extension.
from omni.kit.manipulator.prim.usd import UsdDataAccessor
from omni.kit.manipulator.prim.core import get_prim_data_accessor_registry

# get the global data accessor registry
prim_data_accessor_registry = get_prim_data_accessor_registry()

# registers the Usd data accessor from the global registry.
prim_data_accessor_registry.register_data_accessor(UsdDataAccessor, "USD")

# unregisters the Usd data accessor from the global registry.
prim_data_accessor_registry.unregister_data_accessor("USD")
```