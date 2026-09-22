```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The **omni.kit.widget.versioning** extension offers a set of UI components and helpers for displaying and managing branch and checkpoint information in Omniverse Kit SDK. It provides a cohesive way to list, filter, and restore checkpoints for files while supporting different visual layouts and interactive controls.

```{image} ../../../../source/extensions/omni.kit.widget.versioning/data/preview.png
---
align: center
---
```


## Concepts

- The extension introduces a model-view approach where a [CheckpointModel](omni.kit.widget.versioning/omni.kit.widget.versioning.CheckpointModel) manages checkpoint data and a [CheckpointWidget](omni.kit.widget.versioning/omni.kit.widget.versioning.CheckpointWidget) provides a visual interface to display that data.  
- Individual checkpoint entries are represented by [CheckpointItem](omni.kit.widget.versioning/omni.kit.widget.versioning.CheckpointItem) objects, which include utility methods such as converting file sizes and formatting dates.  
- [CheckpointCombobox](omni.kit.widget.versioning/omni.kit.widget.versioning.CheckpointCombobox) offers a compact dropdown interface for selecting checkpoints, while [CheckpointHelper](omni.kit.widget.versioning/omni.kit.widget.versioning.CheckpointHelper) centralizes URL processing and checkpoint status verification.

## Functionality

- The [CheckpointModel](omni.kit.widget.versioning/omni.kit.widget.versioning.CheckpointModel) retrieves checkpoint data asynchronously, supports search filtering, and manages selection modes for single or multiple checkpoints.  
- The [CheckpointWidget](omni.kit.widget.versioning/omni.kit.widget.versioning.CheckpointWidget) integrates the model with various layout options and event callbacks (mouse pressed, double-click, and context menus) to drive user interaction.  
- Helper functions in [CheckpointHelper](omni.kit.widget.versioning/omni.kit.widget.versioning.CheckpointHelper) simplify server URL extraction and enable efficient caching for checkpoint status queries.  

## Dependencies

- This extension relies on **omni.ui** and **omni.client** for UI elements and client-side operations, as well as **omni.kit.widget.context_menu** for context menu support.  

## Considerations

- The extension is designed specifically for versioning tasks and checkpoint management; its functionality is tailored to handling file checkpoints, so integration with your asset management workflow is key.  
- As checkpoint listings and restoration involve asynchronous operations, ensure that your application handles these updates appropriately to maintain a responsive UI.