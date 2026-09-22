```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
This extension provides a utility for managing connections to Nucleus servers, including handling authentication flows and connection management tasks. It offers a convenient interface for initiating and terminating server connections, as well as managing authentication processes.

## Important API List
The module consists of the following main components:
- [connect](omni.kit.widget.nucleus_connector/omni.kit.widget.nucleus_connector.connect): Connects to a specified Nucleus server by name and URL.
- [connect_with_dialog](omni.kit.widget.nucleus_connector/omni.kit.widget.nucleus_connector.connect_with_dialog): Prompts for server name and URL, then proceeds to connect to it.
- [reconnect](omni.kit.widget.nucleus_connector/omni.kit.widget.nucleus_connector.reconnect): Reconnects to a specified Nucleus server by URL.
- [disconnect](omni.kit.widget.nucleus_connector/omni.kit.widget.nucleus_connector.disconnect): Disconnects from a specified Nucleus server by URL.

## General Use Case
Users can utilize this extension to manage connections to Nucleus servers. This includes initiating connections via specified server details or interactive dialogs, reconnecting to servers, and handling disconnections. The extension also supports event-based notifications for successful connections, allowing users to adapt their workflows based on connection status. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)
- [](SETTINGS)
