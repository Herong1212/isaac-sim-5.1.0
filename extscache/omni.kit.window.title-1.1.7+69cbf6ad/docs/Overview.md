```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The Title Bar extension manages the application window’s title by composing parts such as the app name, version, custom title text, and additional decorations. It ensures that the displayed title reflects the current state of the application by automatically responding to changes in the USD stage and context.

```{image} ../../../../source/extensions/omni.kit.window.title/data/preview.png
---
align: center
---
```


## Concepts

- The title is assembled from individual components—app name, version, title text, and decor—that update in real time.
- It reacts to changes from the USD context (like stage events) to append indicators such as a modified state or read-only flag.

## Functionality

- The extension provides the public API [get_main_window_title](omni.kit.window.title/omni.kit.window.title.get_main_window_title)() to retrieve the current WindowTitle object.
- The WindowTitle class is responsible for setting and updating each title component and ensuring that any change is immediately reflected in the window title.
- It leverages Carb settings and tokens to resolve dynamic values, keeping the title in sync with the application state.

## Settings

- A configurable poll interval (defaulting to 500.0 ms) controls how frequently the extension checks for changes.
- The version part of the title is set to the current application version, ensuring consistency between the displayed title and the app’s version.

## Relationships

- The extension depends on **omni.appwindow** for handling window interfaces and **omni.usd** for observing USD stage events.
- It is designed to work seamlessly within the Omniverse Kit SDK environment, relying on existing windowing and USD capabilities to update the title.

