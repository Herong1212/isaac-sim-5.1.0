```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
This extension provides support for handling OS drag and drop events in specified application windows, from Windows Explorer or Ubuntu's Nautilus. It offers functionality to detect these events, check mouse coordinates, and expand directories in payloads to include all files within. The core of this functionality is encapsulated in the `ExternalDragDrop` class, which manages drag and drop events on the application's main window and invokes callback functions when an drop event is detected over a specified window area.

## Important API List
- **ExternalDragDrop**: Manages drag and drop events for a specified window, invoking a callback function upon detection of such events.
- **destroy**: Cleans up resources and subscriptions held by the ExternalDragDrop instance.
- **get_current_mouse_coords**: Retrieves the current mouse coordinates, scaled by the DPI scale.
- **is_window_hovered**: Checks if the mouse is hovering over the specified window.
- **expand_payload**: Expands a payload to include all files within any directories contained in the payload.

## General Use Case
This extension is primarily used to enhance user interaction within application windows by handling external drag and drop events. Developers can utilize the `ExternalDragDrop` class to monitor specific windows for these events, perform checks to see if the window is being hovered over, and handle payloads that include directories by expanding them to include all contained files. This functionality is especially useful in applications that benefit from drag and drop operations for file or data management. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](CHANGELOG)
