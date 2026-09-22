```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Usage Examples

## Create a Fabric Primitive

```python
import omni.kit.commands

# Create a Fabric primitive of type 'Sphere'
omni.kit.commands.execute("CreateFabricPrim", prim_type="Sphere")
```

## Copy a Fabric Primitive

```python
import omni.kit.commands

# Copy a Fabric primitive from one path to another
omni.kit.commands.execute("CopyFabricPrim", path_from="/World/Sphere", path_to="/World/Sphere_Copy")
```

## Delete Fabric Primitives

```python
import omni.kit.commands

# Delete a list of Fabric primitives by their paths
omni.kit.commands.execute("DeleteFabricPrims", paths=["/World/Sphere", "/World/Cube"])
```

## Move a Fabric Primitive

```python
import omni.kit.commands

# Move a Fabric primitive from one path to another
omni.kit.commands.execute("MoveFabricPrim", path_from="/World/Sphere", path_to="/World/NewLocation/Sphere")
```

## Toggle Visibility of Selected Fabric Primitives

```python
import omni.kit.commands
import omni.usd

# Assuming '/World/Sphere' is selected, toggle its visibility
selected_paths = ["/World/Sphere"]
omni.kit.commands.execute("ToggleVisibilitySelectedFabricPrims", selected_paths=selected_paths)
```

## Group Fabric Primitives

```python
import omni.kit.commands

# Group multiple Fabric primitives under a new Xform primitive
prim_paths = ["/World/Sphere", "/World/Cube"]
omni.kit.commands.execute("GroupFabricPrims", prim_paths=prim_paths)
```

## Ungroup Fabric Primitives

```python
import omni.kit.commands

# Ungroup Fabric primitives from their common parent group
prim_paths = ["/World/Group"]
omni.kit.commands.execute("UngroupFabricPrims", prim_paths=prim_paths)
```

## Transform a Fabric Primitive

```python
import omni.kit.commands
import usdrt.Gf

# Apply a transformation matrix to a Fabric primitive
new_transform_matrix = usdrt.Gf.Matrix4d().SetTranslate(usdrt.Gf.Vec3d(1, 2, 3))
omni.kit.commands.execute(
    "TransformFabricPrim", path="/World/Sphere", new_transform_matrix=new_transform_matrix
)
```

## Change a Fabric Property

```python
import omni.kit.commands

# Change the 'radius' property of a Fabric Sphere primitive
prop_path = "/World/Sphere.radius"
omni.kit.commands.execute(
    "ChangeFabricProperty", prop_path=prop_path, value=2.0, prev=1.0
)
```

## Create Default Transform on a Fabric Primitive

```python
import omni.kit.commands

# Create and apply a default transform to a Fabric primitive at a specified path
omni.kit.commands.execute(
    "CreateDefaultXformOnFabricPrim", prim_path="/World/Sphere"
)
```