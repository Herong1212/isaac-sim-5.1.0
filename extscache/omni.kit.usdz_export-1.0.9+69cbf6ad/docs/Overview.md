```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

USDZ Exporter packages assets into a USDZ archive, making it easy to [export](omni.kit.usdz_export/omni.kit.usdz_export.usdz_export) scene layers for sharing or further processing. The extension adds a context menu to layer window for easy access. It offers a straightforward API to trigger exports asynchronously.

```{image} ../../../../source/extensions/omni.kit.usdz_export/data/preview.png
---
align: center
---
```


## Functionality

- **[usdz_export](omni.kit.usdz_export/omni.kit.usdz_export.usdz_export)(identifier, export_path):** Asynchronously exports a specified layer to the provided file path. It gathers required files in a temporary directory before packaging them into a USDZ archive.

## Relationships

- Depends on modules like **omni.kit.window.file_exporter** to provide a consistent file export experience.
- Utilizes **omni.usd** and **omni.usd.libs** for handling USD data structures during the export process.
- Integrates with **omni.kit.usd.collect** to aggregate assets for packaging.
- Works alongside **omni.ui** and **omni.kit.pip_archive** to manage user interface components and dependency delivery.

## Considerations

- The [usdz_export](omni.kit.usdz_export/omni.kit.usdz_export.usdz_export) actions are only active when layer functionality is available, ensuring that the LayersMenu is only added when the "**omni.kit.widget.layers**" extension is loaded.
- The extension adapts dynamically to workspace changes, creating or cleaning up its UI components on startup and shutdown.
- Its simplicity and clear API design facilitate integration into script-based workflows within the Omniverse Kit SDK.