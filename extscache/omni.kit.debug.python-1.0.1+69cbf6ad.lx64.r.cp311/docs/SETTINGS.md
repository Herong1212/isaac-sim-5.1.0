```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Settings Provided by the Extension
### exts."omni.kit.debug.python".break
   - **Default Value**: False
   - **Description**: Determines if an immediate breakpoint should be triggered after the debugger server is ready.

### exts."omni.kit.debug.python".waitForClient
   - **Default Value**: False
   - **Description**: Controls whether the debugger should wait for a client to connect before executing further.

### exts."omni.kit.debug.python".debugpyLogging
   - **Default Value**: False
   - **Description**: Enables logging for the debug sessions to the path specified by the environment's token settings.

### exts."omni.kit.debug.python".mode
   - **Default Value**: listen
   - **Description**: Sets the mode of the debugger server to either listen for incoming connections or connect to a specified client.

### exts."omni.kit.debug.python".port
   - **Default Value**: 3000
   - **Description**: Specifies the port number on which the debugger server should listen or connect.

### exts."omni.kit.debug.python".host
   - **Default Value**: 127.0.0.1
   - **Description**: Defines the host address for the debugger server to listen for connections or to connect to a client.
