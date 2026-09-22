```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.helper.file_utils` extension provides a system for managing and tracking file events, such as opening and saving files, within an application. It maintains a history of these events and offers an API for other extensions to access this information. Additionally, it includes utilities for recognizing and handling different asset types based on file extensions, which are used in determining the type of asset involved in a file event.

## Important API List
- **FileEventModel**: Data model representing a file event within the application.
- **get_latest_urls_from_event_queue**: Retrieves a list of the latest URLs from the event queue based on certain criteria.
- **get_last_url_visited**: Retrieves the last URL visited based on asset type and tag.
- **get_last_url_opened**: Retrieves the last URL opened based on asset type and tag.
- **get_last_url_saved**: Retrieves the last URL saved based on asset type and tag.
- **reset_file_event_queue**: Clears the file event queue.
- **asset_types**: Provide default asset types' defination and relative methods.

## General Use Case
This extension is used to track and manage file-related events, such as when a file is opened or saved. It allows for querying the most recent file events, which can be filtered by asset type, event type, or tag. This helps in maintaining a history of user interactions with files and can be used for features like recent files lists or undo/redo operations. The asset type recognition utilities can be used to associate file extensions with particular types of assets, providing icons and thumbnails for different file types and enhancing file management within the application. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)