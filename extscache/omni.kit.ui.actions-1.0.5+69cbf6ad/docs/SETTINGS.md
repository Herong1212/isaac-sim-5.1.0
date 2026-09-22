```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Settings Provided by the Extension
### exts."omni.kit.ui.actions".ui_hotkey_escape
- **Default Value**: True
- **Description**: Enables the registration of the ESCAPE key to cancel fullscreen or no-UI mode by triggering the "cancel_fullscreen_ui" action.

### exts."omni.kit.ui.actions".ui_hotkeys
- **Default Value**: False
- **Description**: Controls whether the default UI hotkeys (such as F7 for toggling UI and F11 for fullscreen) are enabled within the extension.

## Settings Used by the Extension but Provided by Another Extension
### /app/window/showDpiScaleMenu
- **Description**: Determines if the DPI scale menu should be shown, which in turn enables additional DPI scale hotkeys for increasing or decreasing the DPI scale.

### /app/window/dpiScaleOverride
- **Description**: Holds the current DPI scale override value that can be adjusted (increased, decreased, or reset) by the hotkey actions.

### /exts/omni.appwindow/listenF11
- **Description**: Checks whether the app window extension is already listening for the F11 hotkey to avoid conflict when registering the fullscreen toggle hotkey.

### /app/window/hideUi
- **Description**: Specifies whether the UI is currently hidden in the app window, affecting how actions toggle or restore the window’s UI state.

### /app/window/displayModeLock
- **Description**: Locks the display mode to force the application to remain in a specific mode (e.g., fullscreen), modifying the behavior of the UI hide/show logic.

### exts/omni.kit.viewport.actions/ui_hotkeys
- **Description**: Enables the registration of UI hotkeys for the viewport, which provides an alternative set of hotkey controls separate from those defined in this extension.