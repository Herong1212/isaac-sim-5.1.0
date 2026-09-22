```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.primitive.mesh` module provides functionality to create and manipulate mesh primitives within the Omniverse application. It includes commands for generating various types of mesh primitives with default transformations and evaluators for geometric shapes.

## Important API List
The module consists of the following main components:
- [AbstractShapeEvaluator](omni.kit.primitive.mesh/omni.kit.primitive.mesh.AbstractShapeEvaluator): A base class for creating shape evaluators that calculate geometric data for different shapes.
- [CreateMeshPrimCommand](omni.kit.primitive.mesh/omni.kit.primitive.mesh.CreateMeshPrimCommand): A command for creating mesh primitives with default transformations in a USD stage.
- [CreateMeshPrimWithDefaultXformCommand](omni.kit.primitive.mesh/omni.kit.primitive.mesh.CreateMeshPrimWithDefaultXformCommand): Similar to CreateMeshPrimCommand, but specialized in creating mesh primitives with default transformations.
- [get_geometry_mesh_prim_list](omni.kit.primitive.mesh/omni.kit.primitive.mesh.get_geometry_mesh_prim_list): Function that returns a sorted list of all available geometry mesh primitive names.

## General Use Case
Users can use this module to create various mesh primitives like planes, spheres, cones, etc., with default transformations, and manipulate them within the Omniverse application. The module also provides base classes for evaluating geometric shapes, allowing for further customization and extension for specific shape calculations. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)
- [](SETTINGS)
