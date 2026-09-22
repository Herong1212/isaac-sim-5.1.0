
```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Settings Provided by the Extension

### `exts."omni.kit.viewport.window".startup.windowName`
- Default Value: `"Viewport"`
- Description: Default name of the ViewportWindow

### `exts."omni.kit.viewport.window".startup.disableWindowOnLoad`
- Default Value: `false`
- Description: Setting to disable opening a Window instance when loaded

### `exts."omni.kit.viewport.window".startup.dockTabInvisible`
- Default Value: `true`
- Description: Whether to hide the Viewport's docking tab when created

### `exts."omni.kit.viewport.window".startup.singleTabGroup`
- Default Value: `false`
- Description: Whether multiple Viewports startup with tabs overlapped (exclusive viewing) or quad-like layout.

### `exts."omni.kit.viewport.window".windowMenu.entryCount`
- Default Value: `2`
- Description: The number of "Viewport" menu-item entries available for use

### `exts."omni.kit.viewport.window".windowMenu.entryLabels`
- Default Value: `[]`
- Description: A list of string to label the "Viewport" menu-item as. An empty list (or empty slot in the list) will use default labeling

### `exts."omni.kit.viewport.window".windowMenu.label`
- Default Value: `"Viewport"`
- Description: Name of top-level "Viewport" menu entry that holds all of the entries

### `exts."omni.kit.viewport.window".startup.windowNames`
- Default Value: `[]`
- Description: Similar per-Viewport control of startup options.

### `exts."omni.kit.viewport.window".startup.showOnLaunch`
- Default Value: `[]`
- Description: Similar per-Viewport control of startup options.

### `exts."omni.kit.viewport.window".dragDrop.maxPlaneDistance`
- Default Value: `0`
- Description: Max allowed distance for drag-drop plane intersection test

### `exts."omni.kit.viewport.window".dragDrop.intersectMode`
- Default Value: `"ground"`
- Description: Valid modes 'x', 'y', 'z', 'ground', 'object', ''

### `app.renderer.skipWhileInvisible`
- Default Value: `true`
- Description: Whether to automatically disable updates to the Viewport when it is made invisible

### `exts."omni.kit.viewport.window".coiDoubleClick`
- Default Value: `false`
- Description: Whether a double click in the Viewport will change the camera's center-of-interest

### `persistent.exts."omni.kit.viewport.window".cameraSpeedMessage.collapsed`
- Default Value: `false`
- Description: Whether to start the camera-speed-hud collapsed or not.

### `exts."omni.kit.viewport.window".cameraSpeedMessage.seconds`
- Default Value: `5.0`
- Description: Amount of time camera-speed-hud stays visible (in seconds).

### `exts."omni.kit.viewport.window".cameraSpeedMessage.fadeIn`
- Default Value: `0.5`
- Description: Amount of time camera-speed-hud takes to fade-in (in seconds).

### `exts."omni.kit.viewport.window".cameraSpeedMessage.fadeOut`
- Default Value: `0.5`
- Description: Amount of time camera-speed-hud takes to fade-out (in seconds).

### `exts."omni.kit.viewport.window".hud.memoryTypes`
- Default Value: `["device", "process"]`
- Description: Types of memory info to show in the HUD stats ("device", "process", "host")

### `app.viewport.defaults.noTitleBar`
- Default Value: `false`
- Description: Whether to hide the ViewportWindow title-bar
