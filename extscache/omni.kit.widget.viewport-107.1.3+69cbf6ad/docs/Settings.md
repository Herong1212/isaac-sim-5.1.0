
```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Settings used by the extension

### `persistent.app.primCreation.typedDefaults.camera.focalLength`
- Default Value: `18.147562`
- Description: Default focal-length for perspective cameras.

### `persistent.app.primCreation.typedDefaults.camera.clippingRange`
- Default Value: `[1.0, 10000000.0]`
- Description: Set default clipping range for perspective cameras.

### `persistent.app.primCreation.typedDefaults.orthoCamera.clippingRange`
- Default Value: `[1.0, 10000000.0]`
- Description: Set default clipping range for orthographic cameras.


## Settings provided by the extension

### `exts."omni.kit.widget.viewport".resize.textureFrameDelay`
- Default Value: `3`
- Description: Minimum amount of frames to wait before pushing ui size changes to render texture.

### `exts."omni.kit.widget.viewport".resize.waitForMousePaused`
- Default Value: `10`
- Description: Push ui size changes to render texture after mouse has stopped moving for this many frames.

### `exts."omni.kit.widget.viewport".resize.waitForMouseUp`
- Default Value: `false`
- Description: Whether to wait for a mouse up before triggering a render texture resize.

### `exts."omni.kit.widget.viewport".resize.updateProjection`
- Default Value: `false`
- Description: Whether to update the camera projection while waiting for resize to complete.

### `exts."omni.kit.widget.viewport".autoAttach.mode`
- Default Value: `0`
- Description: Whether to auto-attach a renderer to a Viewport (0=off, 1=on-stage-open, 2=on-viewport-creation).

### `exts."omni.kit.widget.viewport".autoAttach.renderer`
- Default Value: `""`
- Description: Setting to force a specific renderer for auto-attach (fallback is usual active renderer).

### `exts."omni.kit.widget.viewport".picking.rtx.accelerate`
- Default Value: `true`
- Description: Setting to accelerate prim-query requests if possible.

### `exts."omni.kit.widget.viewport".picking.rtx.timeout.resolve`
- Default Value: `0.06`
- Description: Max amount of time (in seconds) to wait for an accelerated picking query to complete.
