```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
This extension provides a collection of commands for managing and manipulating primitives within a Fabric stage using USDRT API. It includes commands for creating, copying, moving, deleting, and transforming primitives, as well as grouping, ungrouping, and changing properties and attributes of these primitives. They are designed to work with Fabric, a framework within NVIDIA Omniverse for real-time graphics and simulation.

## Important API List
- [DeleteFabricPrimsCommand](omni.fabric.commands/omni.fabric.commands.DeleteFabricPrimsCommand): Deletes specified primitives from a Fabric stage.
- [MoveFabricPrimCommand](omni.fabric.commands/omni.fabric.commands.MoveFabricPrimCommand): Moves a single Fabric prim to a new path within the same stage.
- [MoveFabricPrimsCommand](omni.fabric.commands/omni.fabric.commands.MoveFabricPrimsCommand): Moves multiple Fabric prims to new locations within the stage.
- [ToggleVisibilitySelectedFabricPrimsCommand](omni.fabric.commands/omni.fabric.commands.ToggleVisibilitySelectedFabricPrimsCommand): Toggles the visibility of selected Fabric primitives.
- [CreateFabricPrimWithDefaultXformCommand](omni.fabric.commands/omni.fabric.commands.CreateFabricPrimWithDefaultXformCommand): Creates a Fabric primitive with a default transform.
- [CreateFabricPrimCommand](omni.fabric.commands/omni.fabric.commands.CreateFabricPrimCommand): Creates a Fabric primitive.
- [CreateFabricPrimsCommand](omni.fabric.commands/omni.fabric.commands.CopyFabricPrimsCommand): Creates multiple Fabric primitives.
- [CreateDefaultXformOnFabricPrimCommand](omni.fabric.commands/omni.fabric.commands.CreateDefaultXformOnFabricPrimCommand): Applies a default transform to a Fabric primitive.
- [CopyFabricPrimCommand](omni.fabric.commands/omni.fabric.commands.CopyFabricPrimCommand): Copies a Fabric primitive to a new location in the stage.
- [CopyFabricPrimsCommand](omni.fabric.commands/omni.fabric.commands.CopyFabricPrimsCommand): Copies multiple Fabric primitives to new locations in the stage.
- [GroupFabricPrimsCommand](omni.fabric.commands/omni.fabric.commands.GroupFabricPrimsCommand): Groups multiple Fabric primitives under a new Xform primitive.
- [UngroupFabricPrimsCommand](omni.fabric.commands/omni.fabric.commands.UngroupFabricPrimsCommand): Ungroups Fabric primitives from their common parent Xform primitive.
- [TransformFabricPrimCommand](omni.fabric.commands/omni.fabric.commands.TransformFabricPrimCommand): Transforms a Fabric primitive with a given transformation matrix.
- [ChangeFabricPropertyCommand](omni.fabric.commands/omni.fabric.commands.ChangeFabricPropertyCommand): Changes a specified property on a Fabric primitive.
- [ChangeFabricAttributeCommand](omni.fabric.commands/omni.fabric.commands.ChangeFabricAttributeCommand): Changes a specified attribute on a Fabric primitive.

## General Use Case
Users can use this extension to perform various operations on primitives within a Fabric stage, such as creating, deleting, moving, grouping, and transforming primitives, as well as managing their properties and visibility. These commands facilitate the manipulation of scene elements in a programmatic and undoable manner, allowing for efficient scene management in the Omniverse Kit. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)