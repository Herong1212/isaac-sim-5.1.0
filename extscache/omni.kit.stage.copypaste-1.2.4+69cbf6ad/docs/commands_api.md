# Commands
Public command API for module **omni.kit.stage.copypaste**:

- [ImportLayerCommand](#importlayercommand)


## ImportLayerCommand
Import given layer to the given stage under the specific root.

###

### Arguments
- layer: Sdf.Layer`
- root: Sdf.Path`
- stage: Optional[int]`
- filter_fn

### Usage

```python
import omni.usd
import omni.kit.commands
from pxr import Sdf, Usd

# Get the current stage from the USD context.
stage = omni.usd.get_context().get_stage()

# Create an anonymous layer to simulate the source layer.
# In a real use case, this layer might be loaded from an existing file.
layer = Sdf.Layer.CreateAnonymous("import_layer")

# Define the root path where the imported prims will be placed.
root_path = Sdf.Path("/World/Imported")

# Optionally, define a filter function to control which prims to import.
# In this example, the filter accepts all prims.
filter_fn = lambda prim: True

# Execute the ImportLayerCommand to import prims from the layer into the stage.
omni.kit.commands.execute("ImportLayerCommand", layer=layer, root=root_path, stage=stage, filter_fn=filter_fn)
```

