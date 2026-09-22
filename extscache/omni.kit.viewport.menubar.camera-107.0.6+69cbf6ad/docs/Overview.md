```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
This extension adds a menu to the Omniverse Kit Viewport with a list of cameras and additional camera controls. It allows users to select, create, and modify cameras directly from the viewport's menu bar. It also provides an extendable interface for custom camera widgets and menu items.

## Important API List
- **get_instance**: Retrieves the singleton instance of the viewport camera menu bar extension.
- **ViewportCameraMenuBarExtension**: The main class that manages the camera settings integration into the viewport menu bar.
- **ViewportCameraMenuBarExtension.register_menu_item**: Allows registration of custom menu items to the camera menu.
- **ViewportCameraMenuBarExtension.deregister_menu_item**: Removes custom menu items from the camera menu.
- **ViewportCameraMenuBarExtension.set_menu_item_type**: Sets a custom menu item type for the default created camera.
- **SingleCameraMenuItemBase**: A base class for creating custom single camera menu items.
- **AbstractWidgetDelegate**: A base class for creating custom widgets in camera button and camera menu item.
- **AbstractCameraButtonDelegate**: Self-register delegate to manage additional widgets in camera button.
- **AbstractCameraMenuItemDelegate**: Self-register delegate to manage additional widgets in camera menu item.

## General Use Case
The extension is used to manage cameras directly from the viewport menu bar. Users can select, lock, and create cameras, as well as access camera-specific properties like lens, focal distance, and F-stop. It supports adding custom menu items and widgets to the camera list, allowing for extended functionality tailored to specific workflows. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)