```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The `omni.kit.usd_undo` extension provides utility classes for managing undo operations on USD layers and edit targets in Omniverse Kit applications. This extension is designed to work specifically with the USD API, allowing developers to encapsulate and manage changes made to USD assets, which can be critical for non-destructive editing workflows.

## Important API List

- [UsdLayerUndo](omni.kit.usd_undo/omni.kit.usd_undo.UsdLayerUndo): Manages undo operations on USD layers. It tracks changes, reserves them for undo, and resets the undo stack.
- [UsdEditTargetUndo](omni.kit.usd_undo/omni.kit.usd_undo.UsdEditTargetUndo): Adapts `UsdLayerUndo` to work with USD edit targets, providing methods to reserve and undo changes on a layer through an edit target.

## General Use Case

The primary use case for the `omni.kit.usd_undo` extension is to provide developers with the ability to add undo functionality to their applications that manipulate USD layers. Developers can instantiate either `UsdLayerUndo` or `UsdEditTargetUndo` depending on their needs, reserve changes they wish to be able to undo, and then call the `undo` method when they want to revert the USD layer to its previous state. This is particularly useful for applications that provide a user interface for editing USD scenes, as it allows users to safely make changes and revert them if necessary.

Here is a brief example of how to use `UsdLayerUndo`:
```python
   import omni.kit.usd_undo

   usd_undo = omni.kit.usd_undo.UsdLayerUndo(stage.GetEditTarget().GetLayer())

   usd_undo.reserve("/root/prim")

   '''Do anything to prim /root/prim here, including creating/deleting prim,
   modifying/creating/deleting meta data or fields, modifying/creating/deleting
   any attributes, modifying/creating/deleting any descendants, etc.'''

   usd_undo.reserve("root/prim2.prop")

   '''Do anything to property root/prim2.prop here, including creating, deleting,
   modifying, etc.'''

   usd_undo.reserve("root/prim2", Usd.Tokens.apiSchemas)

   '''Do anything to apiSchemas field of prim root/prim2 here.'''

   # Call UsdLayerUndo.undo() to revert all changes of those paths.
   usd_undo.undo()
```

For more examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)