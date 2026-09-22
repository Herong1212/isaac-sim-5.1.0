```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The `omni.kit.mainwindow` extension is responsible for managing the main window of the Omniverse Kit application. It provides a class, `MainWindow`, that encapsulates functionality related to the initialization, display, and cleanup of the main window. It also includes methods to toggle the visibility of the main menu and status bar, and to dock various application windows upon startup. The extension ensures that the main window settings are in line with the application's settings and provides an interface for other components to interact with the main window.

## Important API List

- [MainWindow](omni.kit.mainwindow/omni.kit.mainwindow.MainWindow): Represents the main application window, managing its initialization, visibility, and window docking.
- [get_main_window](omni.kit.mainwindow/omni.kit.mainwindow.get_main_window): Retrieves the global instance of the `MainWindow` class, allowing for centralized management and access.

## General Use Case

The `omni.kit.mainwindow` extension is utilized to manage the main window's lifecycle within an Omniverse Kit application. It is primarily used to initialize the main window with specific settings, handle the visibility of interface elements like the main menu bar and status bar, and to organize the docking of various windows (such as Stage, Viewport, Property, Toolbar, and Console) within the main window. This extension is useful for extensions or applications that need to interact with or modify the main window or its elements during startup or runtime. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)