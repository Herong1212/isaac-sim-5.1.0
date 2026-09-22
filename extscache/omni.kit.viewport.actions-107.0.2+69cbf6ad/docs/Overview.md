```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The extension omni.kit.viewport.actions provides a suite of actions for switching cameras, toggle the visibility of elements such as lights, cameras, skeletons, meshes, and HUD components, as well as adjusting renderer settings and viewport resolutions.

## Important Action List
### Viewport Camera Menu Actions
- **perspective_camera**: Switch to Perspective Camera.
- **top_camera**: Switch to Top Camera.
- **front_camera**: Switch to Front Camera.
- **right_camera**: Switch to Right Camera.
### Viewport Display Menu Actions
- **toggle_show_by_purpose_all**: Toggle Show By Purpose - All.
- **toggle_show_by_purpose_guide**: Toggle Show By Purpose - Guide.
- **toggle_show_by_purpose_proxy**: Toggle Show By Purpose - Proxy.
- **toggle_show_by_purpose_render**: Toggle Show By Purpose - Render.
- **toggle_camera_visibility**: Toggles the visibility of cameras in the viewport.
- **toggle_light_visibility**: Toggles the visibility of lights in the viewport.
- **toggle_skeleton_visibility**: Toggles the visibility of skeletons in the viewport.
- **toggle_audio_visibility**: Toggles the visibility of audio elements.
- **toggle_mesh_visibility**: Toggles the visibility of meshes in the viewport.
- **toggle_show_by_type_visibility**: Toggles the visibility of cameras, lights, skeletons and audio in the viewport.
- **toggle_grid_visibility**: Toggles the visibility of the grid in the viewport.
- **toggle_axis_visibility**: Toggles the visibility of the axis in the viewport.
- **toggle_selection_hilight_visibility**: Toggles the visibility of selection highlights.
- **toggle_bounding_box_visibility**: Toggles the visibility of bounding boxes.
- **toggle_global_visibility**: Toggles visibility of grid, HUD, audio, light, camera, and skeleton gizmos.
- **toggle_viewport_visibility**: Toggles the visibility of viewport items by key.
### Viewport Settings Menu Actions
- **toggle_camera_inertia_enabled**: Toggle Camera Inertia Mode Enabled.
- **toggle_fill_viewport**: Toggle Fill Viewport Setting.
- **toggle_lock_navigation_height**: Toggle whether fly-mode forward/backward and up/down uses ore ignores the camera orientation.
- **set_viewport_resolution**: Sets the resolution of the viewport.
### Viewport Render Menu Actions
- **set_renderer_rtx_realtime**: Set Renderer Engine to RTX Realtime.
- **set_renderer_rtx_pathtracing**: Set Renderer Engine to RTX Pathtracing.
- **toggle_rtx_rendermode**: Toggle RTX render-mode between Realtime and Pathtracing.
- **set_renderer_iray**: Set Renderer Engine to RTX Accurate (Iray).
- **set_renderer_pxr_storm**: Set Renderer Engine to Pixar Storm.
- **toggle_wireframe**: Toggles the wireframe rendering mode.
### Viewport HUD Visibility Actions
- **toggle_hud_fps_visibility**: Toggle the visibility of render fps in HUD.
- **toggle_hud_resolution_visibility**:  Toggle the visibility of render resolution in HUD.
- **toggle_hud_progress_visibility**: Toggle the visibility of render progress in HUD.
- **toggle_hud_camera_speed_visibility**: Toggle the visibility of camera speed in HUD.
- **toggle_hud_memory_visibility**: Toggles the visibility of memory in the HUD.
- **toggle_hud_visibility**: Toggles the visibility of all HUD elements.

## General Use Case
The extension allows users to easily manage the visibility of different elements within the Omniverse Kit Viewport, change the active camera, adjust rendering settings, and customize the viewport's appearance to their needs. This can be particularly useful for scene setup, visualization, and ensuring optimal performance during the development process by selectively toggling element visibility. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)