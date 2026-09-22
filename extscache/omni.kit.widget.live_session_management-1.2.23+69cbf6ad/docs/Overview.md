```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The Live Session Management Widgets extension provides a set of reusable UI components and utility functions to simplify live session workflows within Omniverse Kit SDK. It offers ready-made widgets for displaying live session user lists, managing session selection, and camera tracking of users. The extension is designed so that other extensions can quickly integrate live session capabilities without duplicating UI logic.

```{image} ../../../../source/extensions/omni.kit.widget.live_session_management/data/docs_images/display_live_session_users.png
---
align: center
---
```


## Concepts

- **Live Session User Interfaces:**  
  The extension includes widgets such as [LiveSessionUserList](omni.kit.widget.live_session_management/omni.kit.widget.live_session_management.LiveSessionUserList), [LiveSessionCameraFollowerList](omni.kit.widget.live_session_management/omni.kit.widget.live_session_management.LiveSessionCameraFollowerList), and [LiveSessionModel](omni.kit.widget.live_session_management/omni.kit.widget.live_session_management.LiveSessionModel) that allow developers to visually display active users in a live session or to manage session selection via a combobox. For example, [LiveSessionCameraFollowerList](omni.kit.widget.live_session_management/omni.kit.widget.live_session_management.LiveSessionCameraFollowerList) builds an icon list showing who is following a specific camera.

- **Utility Functions:**  
  In addition to UI widgets, the extension provides helper functions. Using [build_live_session_user_layout](omni.kit.widget.live_session_management/omni.kit.widget.live_session_management.build_live_session_user_layout), developers can generate standardized user icon widgets complete with optional click and double-click actions. The function [reload_outdated_layers](omni.kit.widget.live_session_management/omni.kit.widget.live_session_management.reload_outdated_layers) ensures that any outdated USD layers are refreshed, handling potential live session conflicts. The [is_viewer_only_mode](omni.kit.widget.live_session_management/omni.kit.widget.live_session_management.is_viewer_only_mode) utility checks if the session has been set to viewer-only mode, which changes how unsaved changes are handled during session transitions.

## Functionality

- **Session Management Widgets:**  
  The provided widgets standardize the appearance and behavior of live session user lists across the application. They allow for tracking changes based on a target layer or camera path and include options such as icon size, spacing, and filtering of local users.

- **Model and Layout Integration:**  
  [LiveSessionModel](omni.kit.widget.live_session_management/omni.kit.widget.live_session_management.LiveSessionModel) extends a combobox model to list and select live sessions based on a specified layer. By tapping into live updates of user data, it helps manage session state and supports creating new session names when needed.

- **Viewer-Only Mode Behavior:**  
  The [is_viewer_only_mode](omni.kit.widget.live_session_management/omni.kit.widget.live_session_management.is_viewer_only_mode) function leverages a settings flag (viewer_only_mode) to determine if the extension should bypass dialog prompts when unsaved changes are present. 

## Relationships

- **Integrated Dependencies:**  
  The extension builds on several core modules such as **omni.ui** for UI components and **omni.kit.usd.layers** for layer management. It also works alongside other session and collaboration extensions, ensuring a consistent live session UI throughout the application.

- **Configurable Behavior via Settings:**  
  The extension’s behavior can be influenced by specific settings defined in its extension.toml. For example, the viewer-only mode setting and quick join options directly affect how live session transitions are handled, allowing developers to customize the user experience based on their workflow needs.

In summary, the Live Session Management Widgets extension makes it easier to implement live session features by providing standard UI components and helper functions. Its focus on consistency and reusability helps maintain a unified live session experience across different parts of the application.