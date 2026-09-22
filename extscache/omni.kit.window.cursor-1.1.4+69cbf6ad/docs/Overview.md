```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
This extension is designed to enhance cursor management within the main application window by allowing the customization of cursor shapes. It provides functionality to register, unregister, override, and retrieve both custom and standard cursor shapes.

## Important API List
The module consists of the following main components:
- [WindowCursor](omni.kit.window.cursor/omni.kit.window.cursor.WindowCursor): Manages custom cursor shapes within the application, providing methods to register, override, and retrieve cursor shapes.
- [get_main_window_cursor](omni.kit.window.cursor/omni.kit.window.cursor.get_main_window_cursor): Retrieves the extension instance `WindowCursor`.

## General Use Case
This extension can be utilized to customize the appearance of the cursor within the main application window, supporting both custom images and standard cursor shapes. It is particularly useful for developers looking to enhance user interaction feedback through the cursor's appearance. By managing cursor shapes dynamically, applications can provide context-sensitive cursor feedback to users, improving the overall user experience. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)
- [](SETTINGS)
