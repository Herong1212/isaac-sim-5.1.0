```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Settings Provided by the Extension
### exts."omni.kit.viewport.actions".resetVisibilityOnOpen
   - **Default Value**: []
   - **Description**: Defines the visibility options that should be reset when a new stage is opened.

### exts."omni.kit.viewport.actions".visibilityToggle.ignoreStageWindowHidden
   - **Default Value**: false
   - **Description**: Controls whether visibility toggling should ignore objects that are hidden in the stage-view UI.

### exts."omni.kit.viewport.actions".visibilityToggle.globalTypes
   - **Default Value**: ["guide/grid", "scene/cameras", "scene/lights", "scene/skeletons"]
   - **Description**: Specifies the global types of objects that the visibility toggle actions can show or hide.

### exts."omni.kit.viewport.actions".visibilityToggle.removeCameraMeshes
   - **Default Value**: true
   - **Description**: Determines whether camera visibility should remove the child-camera mesh or toggle the parent camera's visibility.

### exts."omni.kit.viewport.actions".visibilityToggle.hudTypes
   - **Default Value**: ["hud/renderFPS", "hud/deviceMemory", "hud/hostMemory", "hud/renderProgress", "hud/renderResolution"]
   - **Description**: Defines HUD items that can be hidden or shown by the visibility toggle actions.
