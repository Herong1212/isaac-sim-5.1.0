```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
This extension facilitates the registration and management of customizations within the Content Browser of NVIDIA's Omniverse Kit. It enables the creation of custom menus, selection handlers, search delegates, and file open handlers, allowing for a tailored user experience. Through a singleton instance, it provides a centralized point to manage these customizations, ensuring they can be reapplied or modified as necessary.

## Important API List
- **register_context_menu**: Adds a new context menu option.
- **deregister_context_menu**: Removes a previously registered context menu.
- **register_listview_menu**: Registers a menu item for the listview context menu.
- **deregister_listview_menu**: Removes a previously registered listview menu.
- **register_import_menu**: Registers a custom menu item for the import context.
- **deregister_import_menu**: Removes a custom menu item from the import menu.
- **register_file_open_handler**: Registers a handler for opening files.
- **deregister_file_open_handler**: Removes a previously registered file open handler.
- **register_selection_handler**: Registers a selection handler.
- **deregister_selection_handler**: Removes a selection handler from the registry.
- **register_search_delegate**: Registers a search delegate.
- **deregister_search_delegate**: Removes a previously registered search delegate.
- **register_checkpoint_menu**: Registers a custom menu item under the 'checkpoint' category.
- **deregister_checkpoint_menu**: Deregisters a previously registered checkpoint menu.

## General Use Case
This extension is primarily used by developers and integrators working with NVIDIA's Omniverse Kit to enhance the Content Browser's functionality. By utilizing the public APIs, users can add custom context menus, listview menus, import menus, and file open handlers tailored to specific workflows. Additionally, it supports the registration of selection handlers and search delegates, providing further customization and control over the user interaction with the Content Browser. This extension ensures that these customizations are centrally managed and persist across sessions or Content Browser restarts. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)