# Usage Examples

## Import Layer to Stage

```python
import omni.usd
from pxr import Sdf, Usd
from omni.kit.stage.copypaste import ImportLayerCommand

# Get the current stage
usd_context = omni.usd.get_context()
stage = usd_context.get_stage()

# Create a new stage if none exists
if not stage:
    omni.usd.get_context().new_stage()
    stage = omni.usd.get_context().get_stage()

# Create a new anonymous layer
layer = Sdf.Layer.CreateAnonymous()

# Create a nested structure in the layer that matches what ImportLayerCommand expects
# First create a root prim that will be a container
root_container = Sdf.CreatePrimInLayer(layer, Sdf.Path("/Root"))
root_container.specifier = Sdf.SpecifierDef

# Then create an actual prim that will be imported
prim_path = Sdf.Path("/Root/MySphere")
prim_spec = Sdf.CreatePrimInLayer(layer, prim_path)
prim_spec.specifier = Sdf.SpecifierDef
prim_spec.typeName = "Sphere"

# Add a property to the prim
prop_spec = Sdf.AttributeSpec(prim_spec, "radius", Sdf.ValueTypeNames.Double, 
                             variability=Sdf.VariabilityVarying)
prop_spec.default = 10.0

# Define the root path where you want to import the layer
root_path = Sdf.Path("/World")

# Optional filter function to determine which prims to import
def filter_fn(prim_spec):
    # For example, only import prims that have a certain prefix
    return prim_spec.name.startswith("My")

# Create and execute the import command
import_cmd = ImportLayerCommand(layer, root_path, stage, filter_fn)
import_cmd.do()
print("Layer imported to stage")
```
