```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The Content Browser extension provides a feature-rich file management interface within the Omniverse Kit SDK. It allows for browsing, managing, and interacting with files and directories on various file systems including local and Nucleus servers. It supports various operations such as opening, copying, moving, renaming, and deleting files and folders. The extension is also extendable, allowing users to add custom actions, menus, and handlers for different file types.

## Important API List
The module consists of the following main components:
- **ContentBrowserAPI** : Core API class for the Content Browser, providing methods to interact with the content browser's functionality.
- **ContentBrowserWindow** : Class responsible for managing the Content Browser window UI.
- **ContentBrowserWidget** : The main widget of the Content Browser, which encapsulates the UI and logic for file browsing.
- **ContentBrowserExtension** : The extension class that initializes and manages the lifecycle of the Content Browser within the Omniverse Kit SDK.

## General Use Case
The Content Browser can be used to navigate the file system, perform file operations, and extend the browser's capabilities with custom actions, context menus, and file type handlers. It is designed to support workflows that involve frequent interaction with the file system within the Omniverse Kit environment. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)