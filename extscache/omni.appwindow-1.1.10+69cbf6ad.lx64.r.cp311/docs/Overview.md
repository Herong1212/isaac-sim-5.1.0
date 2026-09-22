```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The `omni.appwindow` extension provides functionality of creating main/top-level application windows in Omniverse Kit.
Ihe extension has a `IAppWindowFactory` which is an application window creation factory, which is in charge of creating
application windows. Users can create OS window or virtual window from it. OS window provides user with a graphical user
interface to interact with while virtual window is more for headless applications. The extension includes methods to
config the application window's settings, e.g., width, height, resizable, movable etc. It also provides interfaces to
capture the window event streams for users to add callback on that, e.g., focus, resize, drop, move etc.

## Important API List
- **omni::kit::IAppWindowFactory**: Application window creation factory which is in charge of creating application windows
- **omni::kit::IAppWindow**: Application window APIs which manages the lifecycle (startup and shutdown) of the application windows, gets/sets window settings and handles event streams of the application windows.
- **omni::kit::WindowDesc**: Window description which lists the application atttributes which user can customize.
- **omni::kit::WindowType**: This defines the window types where the extension can created: OS or virtual

## General Use Case
The `omni.appwindow` extension is utilized to manage the application window within an Omniverse Kit application. It is primarily used to create the application window with specific settings. This extension is essential for applications that need a window during startup or runtime.

For examples of how to use the APIs, please consult the [C++](USAGE_CPP) and [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](USAGE_CPP)
- [](CHANGELOG)