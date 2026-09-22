```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Settings Provided by the Extension

### `exts."omni.kit.renderer.core".imgui.enableMips`
- **Default Value:** false
- **Description:** Whether to enable Mipmaps for imgui rendering

### `exts."omni.kit.renderer.core".threads.syncMainToPresent`
- **Default Value:** false
- **Description:** Whether to sync the main thread to the present thread

### `exts."omni.kit.renderer.core".present.enabled`
- **Default Value:** false
- **Description:** Whether to enable the present thread. When it is ecplicitly set, the value set to will be honored. If it is initially unset/undefined, the application will choose whether to auto-enable it or not.

### `exts."omni.kit.renderer.core".present.presentAfterRendering`
- **Default Value:** false
- **Description:** In the present thread, whether waiting for the rendering thread to submit everything and waiting for the result of the rendering.
