```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

USDA Editor is an Omniverse Kit extension that augments the UI by adding context menu items for editing USD layers as USDA files. Once enabled, it integrates into both the content browser and Layers 2.0 interfaces, allowing users to easily launch an external text editor for modifying USD layer files. The extension streamlines the editing process while ensuring that any changes are tracked and synchronized via file watchers.

```{image} ../../../../source/extensions/omni.kit.usda_edit/data/preview.png
---
align: center
---
```


## Functionality

- **Context Menus:** The extension extends the content browser and Layers 2.0 with additional menu entries that let users start and stop editing layers as USDA files. These menus dynamically appear based on the availability of related UI modules.
- **Editing Workflow:** When a user selects an edit action, the extension initiates file watchers that monitor temporary USDA files. This ensures that any modifications are automatically propagated back into the active USD layer.
- **Lifecycle Management:** The extension manages the setup and teardown of editors and watchers during startup and shutdown, keeping the interface responsive and ensuring that resources are properly released.

## Relationships

- **Dependency Integration:** This extension depends on core modules including **omni.ui**, **omni.usd**, and **omni.usd.libs**, as well as **omni.kit.pip_archive** for package management. It further integrates with modules like the content browser and Layers 2.0 to provide its editing context menus.
- **Inter-Extension Communication:** It checks for the presence of related extensions (e.g., **omni.kit.window.content_browser** and **omni.kit.widget.layers**) and adjusts its behavior accordingly. This ensures a seamless user experience even as the application environment evolves.

## Limitations & Considerations

- The extension is designed for immediate use once enabled and does not expose additional public APIs for further customization.
- All editing sessions are managed externally, and cleanup operations (such as stopping file watchers and removing temporary files) are automatically handled during shutdown.
- It is important to use the extension within an environment where the supporting modules and UI components are available for the full integrated experience.

