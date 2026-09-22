```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Settings Provided by the Extension
### exts."omni.kit.window.title".version
- **Default Value**: ${app_version}
- **Description**: Specifies the version string to include in the application window title, which is resolved through the tokens interface.

### exts."omni.kit.window.title".pollIntervalMS
- **Default Value**: 500.0
- **Description**: Sets the polling interval (in milliseconds) used to periodically update the window title based on application state changes.

## Settings Used by the Extension but Provided by Another Extension
### /app/window/title
- **Description**: Retrieves the application’s window title from the global settings, which is then resolved as part of composing the complete window title.