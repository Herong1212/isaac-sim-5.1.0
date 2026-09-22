```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The `omni.kit.viewport.utility` module provides a collection of utilities for interacting with and manipulating Viewport instances in NVIDIA Omniverse Kit applications. It allows users to access information about the active viewport, frame specific primitives, capture viewport images, and more.

## Important API List

- [frame_viewport_prims](omni.kit.viewport.utility/omni.kit.viewport.utility.frame_viewport_prims): Frames the viewport to include the specified prims.
- [frame_viewport_selection](omni.kit.viewport.utility/omni.kit.viewport.utility.frame_viewport_selection): Frames the camera in the viewport to include the current selection.
- [get_viewport_from_window_name](omni.kit.viewport.utility/omni.kit.viewport.utility.get_viewport_from_window_name): Retrieves the viewport API instance from a specified window name.
- [get_active_viewport](omni.kit.viewport.utility/omni.kit.viewport.utility.get_active_viewport): Retrieves the active viewport API instance.
- [get_active_viewport_and_window](omni.kit.viewport.utility/omni.kit.viewport.utility.get_active_viewport_and_window): Retrieves the active viewport API instance and the corresponding window instance.
- [get_viewport_window_camera_path](omni.kit.viewport.utility/omni.kit.viewport.utility.get_viewport_window_camera_path): Retrieves the camera path for the viewport in the specified window.
- [get_viewport_window_camera_string](omni.kit.viewport.utility/omni.kit.viewport.utility.get_viewport_window_camera_string): Retrieves the camera path string for the viewport in the specified window.
- [get_active_viewport_camera_path](omni.kit.viewport.utility/omni.kit.viewport.utility.get_active_viewport_camera_path): Retrieves the camera path for the active viewport.
- [get_active_viewport_camera_string](omni.kit.viewport.utility/omni.kit.viewport.utility.get_active_viewport_camera_string): Retrieves the camera path string for the active viewport.
- [get_num_viewports](omni.kit.viewport.utility/omni.kit.viewport.utility.get_num_viewports): Returns the number of active viewports.
- [capture_viewport_to_file](omni.kit.viewport.utility/omni.kit.viewport.utility.capture_viewport_to_file): Captures the provided viewport to a file.
- [capture_viewport_to_buffer](omni.kit.viewport.utility/omni.kit.viewport.utility.capture_viewport_to_buffer): Captures the current viewport and sends the image to a callback function.
- [post_viewport_message](omni.kit.viewport.utility/omni.kit.viewport.utility.post_viewport_message): Posts a message as a toast notification to the viewport or viewport window.
- [toggle_global_visibility](omni.kit.viewport.utility/omni.kit.viewport.utility.toggle_global_visibility): Toggles the global visibility of all viewport layers.
- [create_drop_helper](omni.kit.viewport.utility/omni.kit.viewport.utility.create_drop_helper): Creates a helper object to handle drag-and-drop operations in a viewport.
- [disable_selection](omni.kit.viewport.utility/omni.kit.viewport.utility.disable_selection): Disables selection for a given viewport.
- [get_ground_plane_info](omni.kit.viewport.utility/omni.kit.viewport.utility.get_ground_plane_info): Retrieves the ground plane information including its normal and the planes it occupies.

## General Use Case

The utilities provided by the module are geared towards enhancing the viewport experience within Omniverse Kit applications. It can be used for framing objects within the viewport, capturing images of the viewport for both file output and use within the application, toggling visibility settings, and adding interactivity through drag-and-drop helpers. It also provides functionality for posting notifications to the viewport and disabling certain interactive elements like selection and context menus for specific use cases.For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)