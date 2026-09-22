```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.property.layer` extension provides functionality to modify USD stage and layer properties via a property window. It includes commands to edit metadata and up axis of the layer, a file picker for selecting files, and widgets to display and interact with layer properties.

## Important API List
The module consists of the following main components:
- **ModifyStageAxisCommand**: A command to change the stage's up-axis.
- **ModifyLayerMetadataCommand**: A command to modify the metadata of a USD layer.
- **LayerPropertyWidgets**: A widget extension that registers property UI for layers.

## General Use Case
Users can use this extension to modify the up-axis of a USD stage, change layer metadata such as comments, documentation, time codes, and units. The extension also provides a file picker dialog to select files, and models to represent various layer properties which can be used in custom UIs. Additionally, it includes widgets that can be used to build a property window UI, facilitating the interaction with USD layer properties.

## User Guide
- [](CHANGELOG)
- [](USAGE_PYTHON)