# Usage Examples

## Custom Shape Evaluator Implementation

```python
from omni.kit.primitive.mesh import AbstractShapeEvaluator
from pxr import Gf

# Define a custom evaluator for a specific shape
class CustomShapeEvaluator(AbstractShapeEvaluator):
    def __init__(self, attributes):
        super().__init__(attributes)

    def eval(self, **kwargs):
        # Custom implementation to define points, normals, uvs,
        # face_indices, and face_vertex_counts
        points = [Gf.Vec3f(0.0, 0.0, 0.0), Gf.Vec3f(1.0, 0.0, 0.0), Gf.Vec3f(0.0, 1.0, 0.0)]
        normals = [Gf.Vec3f(0.0, 0.0, 1.0) for _ in range(3)]
        uvs = [Gf.Vec2f(0.0, 0.0), Gf.Vec2f(1.0, 0.0), Gf.Vec2f(0.0, 1.0)]
        face_indices = [0, 1, 2]
        face_vertex_counts = [3]
        return points, normals, uvs, face_indices, face_vertex_counts

# Create an instance of the custom evaluator with attributes
attributes = {}
custom_evaluator = CustomShapeEvaluator(attributes)

# Evaluate the custom shape
points, normals, uvs, face_indices, face_vertex_counts = custom_evaluator.eval()

# Output the evaluated data
print("Points:", points)
print("Normals:", normals)
print("UVs:", uvs)
print("Face Indices:", face_indices)
print("Face Vertex Counts:", face_vertex_counts)
```

## List Available Geometry Mesh Primitive Names

```python
from omni.kit.primitive.mesh import get_geometry_mesh_prim_list

# Get a list of all available geometry mesh primitive names
mesh_prim_list = get_geometry_mesh_prim_list()

# Print the list of primitives
print("Available mesh primitives:", mesh_prim_list)
```

## Create a Mesh Primitive with Default Transform

```python
from omni.kit.commands import execute
from pxr import Gf

# Create a Sphere mesh primitive with default transform and specified origin
result, prim_path = execute(
    "CreateMeshPrim",
    prim_type="Sphere",
    object_origin=Gf.Vec3f(0.0, 0.0, 0.0),
    half_scale=50.0
)

# Ensure the command was successful and a path was returned
if result:
    print(f"Sphere primitive created at path: {prim_path}")
```

## Create and Undo the Creation of a Mesh Primitive

```python
import omni.kit.commands
import omni.kit.undo

# Create a Cube mesh primitive
result, prim_path = omni.kit.commands.execute(
    "CreateMeshPrim",
    prim_type="Cube",
    above_ground=True,
    half_scale=100,
    u_verts_scale=2,
    v_verts_scale=2,
    w_verts_scale=2
)

# Undo the creation
if result:
    omni.kit.undo.undo()
    print(f"Creation of Cube at path {prim_path} has been undone.")
```

## Create a Mesh Primitive with Tessellation Parameters

```python
from omni.kit.commands import execute

# Create a Cylinder mesh primitive with custom tessellation parameters
result, prim_path = execute(
    "CreateMeshPrim",
    prim_type="Cylinder",
    above_ground=True,
    half_scale=100,
    u_verts_scale=1,
    v_verts_scale=1,
    w_verts_scale=1,
    u_patches=2,
    v_patches=2,
    w_patches=2
)

# Check if the Cylinder primitive was created successfully
if result:
    print(f"Cylinder primitive created at path: {prim_path}")
```

## Create Mesh Primitives and Check Their Existence

```python
from omni.kit.commands import execute
from omni.usd import get_context
from pxr import UsdGeom

# Create a Torus mesh primitive and check its existence
result, prim_path = execute("CreateMeshPrim", prim_type="Torus", above_ground=True)

if result:
    stage = get_context().get_stage()
    torus_prim = stage.GetPrimAtPath(prim_path)
    if torus_prim and torus_prim.IsA(UsdGeom.Mesh):
        print(f"Torus primitive exists at path: {prim_path}")
```

## Execute Action to Create Mesh Primitive

```python
import omni.kit.actions.core
from omni.kit.primitive.mesh import get_geometry_mesh_prim_list

# Execute action to create a Plane mesh primitive
prim_type = "Plane"
omni.kit.actions.core.execute_action(
    "omni.kit.primitive.mesh",
    f"create_mesh_prim_{prim_type.lower()}"
)

print(f"Action executed to create a {prim_type} mesh primitive.")
```
