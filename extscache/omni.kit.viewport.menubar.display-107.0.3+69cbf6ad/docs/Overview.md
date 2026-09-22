```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
This extension enriches the Omniverse Kit SDK by providing a menu item to control display settings. It enables users to customize the visibility of various scene elements such as bounding boxes, grids, cameras, lights, skeletons, audio sources, meshes, and selection outlines. Additionally, it provides options for displaying elements based on their purpose (render, proxy, guide) and includes a heads-up display (HUD) category with settings for FPS, memory usage, resolution, progress, and camera speed. The extension also supports adding custom display settings and categories, allowing for further customization of the viewport display menu.

## Important API List
- **ViewportDisplayMenuBarExtension**: Main class to manage the display settings in the viewport menu bar.
- **get_instance**: Function to retrieve the current instance of the `ViewportDisplayMenuBarExtension`.

## General Use Case
This extension is used to manage the visibility of different elements within the viewport to aid in scene composition and visualization. Users can easily toggle the visibility of essential components like bounding boxes, grids, and more directly from the viewport's menu bar. It also allows developers to add custom settings and categories to the display menu, enabling the creation of a more personalized and efficient workspace tailored to the needs of specific projects or workflows. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)