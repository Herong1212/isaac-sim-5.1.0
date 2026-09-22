```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Settings Provided by the Extension
### exts."omni.kit.window.console".startup.show_window
   - **Default Value**: True
   - **Description**: Determines if the console window should be shown on startup.

### exts."omni.kit.window.console".enableInput
   - **Default Value**: True
   - **Description**: Enables or disables input functionality in the console window.

### exts."omni.kit.window.console".showOpenLogButtons
   - **Default Value**: True
   - **Description**: Controls the visibility of buttons to open logs in the console window.

### exts."omni.kit.window.console".logFilter.fatal
   - **Default Value**: True
   - **Description**: Filters fatal log messages in the console window.

### exts."omni.kit.window.console".logFilter.error
   - **Default Value**: True
   - **Description**: Filters error log messages in the console window.

### exts."omni.kit.window.console".logFilter.warning
   - **Default Value**: True
   - **Description**: Filters warning log messages in the console window.

### exts."omni.kit.window.console".logFilter.info
   - **Default Value**: False
   - **Description**: Filters informational log messages in the console window.

### exts."omni.kit.window.console".logFilter.verbose
   - **Default Value**: False
   - **Description**: Filters verbose log messages in the console window.

### exts."omni.kit.window.console".startupCommands
   - **Default Value**: []
   - **Description**: List of commands to be executed when the console window starts up.

## Settings Used by the Extension but Provided by Another Extension
### /exts/omni.kit.window.console/startup/show_window
   - **Description**: Determines if the console window should be shown on startup based on the application's settings.

### /app/python/scriptFolders
   - **Description**: Script in these folders could be executed as commands.