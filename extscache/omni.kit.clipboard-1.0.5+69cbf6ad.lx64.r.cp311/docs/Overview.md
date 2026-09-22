```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
This extension provides functionality for interacting with the system clipboard, enabling applications to copy to and paste from it. It offers a straightforward API for clipboard operations, making it easy to integrate clipboard functionality into any application.

## Important API List
- **copy**: Copies a given string into the system clipboard.
- **paste**: Retrieves a string from the system clipboard, offering a platform-independent mechanism suitable for various environments, including headless ones.

## General Use Case
This extension can be utilized by applications that need to interact with the system clipboard, allowing for the copying of text into the clipboard and pasting text from it. This is particularly useful for applications that need to handle text input and output without direct user interaction with the clipboard through a GUI. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)