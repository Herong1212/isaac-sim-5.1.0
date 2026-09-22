```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.debug.python` module is designed to facilitate debugging in Python scripts within the Omniverse Kit environment. It provides a set of functions to control the debugging process, including initiating breakpoints, enabling logging, checking if a debugger is attached, configuring the debug server, and waiting for a debug client to connect.

## Important API List
The module consists of the following main components:
- [enable_logging](omni.kit.debug.python/omni.kit.debug.python.enable_logging): Enable logging for the debugging process.
- [get_listen_address](omni.kit.debug.python/omni.kit.debug.python.get_listen_address): Retrieve the address on which the debug server is listening.
- [is_attached](omni.kit.debug.python/omni.kit.debug.python.is_attached): Check whether a debug client is currently attached.

## General Use Case
Developers can use this module to debug Python code within Omniverse Kit by setting breakpoints, enabling extensive logging to track the debugging process, and controlling the interaction with the debugger client. Users can check if a debugger is attached to their session and manage the server's listening address. The module also allows for pausing execution until a debugger client is connected, ensuring that no code is missed during the debugging session. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)
- [](SETTINGS)