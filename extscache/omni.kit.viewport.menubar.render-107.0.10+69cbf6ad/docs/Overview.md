```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
This extension integrates render settings directly into the Omniverse Kit SDK's viewport menu bar, offering a convenient interface for selecting and configuring renderers. It supports dynamic registration of custom renderer menu items and manages renderer availability based on extension activity.

## Important API List
- **get_instance**: Retrieves the singleton instance of the viewport render menu bar extension.
- **ViewportRenderMenuBarExtension**: The main class that manages the render settings integration into the viewport menu bar.
- **SingleRenderMenuItemBase**: A base class for creating custom single renderer menu items.
- **SingleRenderMenuItem**: A default implementation for a single renderer menu item, with an option to open render settings.

## General Use Case
This extension is primarily used to provide users with a menu item for selecting different renderers directly from the viewport menu bar in the Omniverse Kit SDK. It facilitates the customization of the render settings menu by allowing the registration of custom renderer menu items. It ensures that the menu reflects the current state of renderer availability. Users can leverage this extension to quickly switch between different rendering modes, adjust lighting and material settings, and access renderer-specific options, enhancing rendering workflow within the Omniverse Kit SDK. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)