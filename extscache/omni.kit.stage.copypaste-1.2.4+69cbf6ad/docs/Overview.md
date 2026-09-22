```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The USD Prim Copy Paste extension provides a way to copy USD prims by converting them into a text representation and pasting them back into a USD stage. Its practical purpose is to offer users the ability to replicate parts of a USD scene efficiently and reliably. The extension streamlines the process by encapsulating import operations into an undoable command.

```{image} ../../../../source/extensions/omni.kit.stage.copypaste/data/preview.png
---
align: center
---
```


## Concepts

- **USD Prim Copy-Paste:** The extension focuses on extracting prim data as text and reintroducing it into a USD stage, which facilitates operations like cloning or transferring scene elements.
- **Layer Importing:** At its core, the [ImportLayerCommand](omni.kit.stage.copypaste/omni.kit.stage.copypaste.ImportLayerCommand) takes an entire USD layer and integrates its prims under a specified root in the target stage. A filtering function can be used to narrow down which prims should be imported.

## Functionality

- **[ImportLayerCommand](omni.kit.stage.copypaste/omni.kit.stage.copypaste.ImportLayerCommand):** This command encapsulates the import process by handling the copying of prim specs from a given USD layer into the stage. It saves the current selection, applies an optional filter to decide which prims are imported, updates property paths so USD relationships and connections are maintained, and then refreshes the selection to include the newly created prims. The design ensures that the command is undoable, allowing users to revert the changes if needed.


## Relationships

- The extension depends on several core and clipboard-related modules (e.g., **omni.kit.clipboard**, **omni.kit.commands**, **omni.usd**) to handle stage manipulation, command execution, and text-based data management.
- Optional dependencies such as **omni.kit.hotkeys.core** add further integration in cases where hotkey support is desirable.

## Considerations

- The [ImportLayerCommand](omni.kit.stage.copypaste/omni.kit.stage.copypaste.ImportLayerCommand) design requires careful use of the optional filter function to control which prims are considered for import.  
- Since the extension operates on layer and prim data, any changes made via the text conversion utilities are subject to the underlying USD schema and may require validation when integrating complex scenes.

This extension is ideal for scenarios involving scene editing where replicating or moving specific USD prims is necessary, while still offering full undo/redo support through the command system.