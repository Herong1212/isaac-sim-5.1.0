```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Usage Examples

## Reserve Changes for Undo on USD Layer

This example demonstrates creating a mesh prim, modifying an attribute, reserving the changes for undo, and then
reverting those changes using the undo functionality provided by the `UsdEditTargetUndo` class.

```python
from pxr import Usd, UsdGeom, Sdf
from omni.kit.usd_undo import UsdEditTargetUndo

# Open an existing stage or create a new one
stage = Usd.Stage.CreateNew("myStage.usda")
edit_target = stage.GetEditTarget()

# Create an instance of UsdEditTargetUndo for managing undo operations
usd_undo = UsdEditTargetUndo(edit_target)

# Make changes to the stage
mesh = UsdGeom.Mesh.Define(stage, "/Root/Mesh")
mesh.CreateNormalsAttr().Set([(1.0, 0.0, 0.0)])

# Reserve the changes for undo
usd_undo.reserve("/Root/Mesh.normals")

# Perform undo to revert the changes
usd_undo.undo()

# After undo, the layer should be reverted back to its state
# before the changes were made.
```

## Reset Undo Stack for USD Layer

```python
from pxr import Sdf, Usd
from omni.kit.usd_undo.layer_undo import UsdLayerUndo

# Open an existing USD stage
layer_path = "/path/to/existing/stage.usda"
stage = Usd.Stage.Open(layer_path)

# Create UsdLayerUndo for the root layer
usd_layer_undo = UsdLayerUndo(stage.GetRootLayer())

# Reset the undo stack for the layer
usd_layer_undo.reset()

# After reset, there will be no changes to undo.
```