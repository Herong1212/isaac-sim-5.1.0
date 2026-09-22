```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Settings Provided by the Extension
### exts."omni.kit.menu.common".external_reference_guide_url
   - **Default Value**: https://docs.omniverse.nvidia.com/main/text/Omniverse_Kit_Overview.html
   - **Description**: URL for the external reference guide.

### exts."omni.kit.menu.common".reference_guide_name
   - **Default Value**: USD Reference Guide
   - **Description**: Name for the reference guide.
   - NOTE: If this is "" then the menu will not be added

### exts."omni.kit.menu.common".external_kit_manual_url
   - **Default Value**: https://docs.omniverse.nvidia.com/py/kit/index.html
   - **Description**: URL for the external kit manual.

### exts."omni.kit.menu.common".kit_manual_name
   - **Default Value**: Developers Manual
   - **Description**: Name for the developers manual.
   - NOTE: If this is "" then the menu will not be added

### exts."omni.kit.menu.common".external_kit_sdk_url
   - **Default Value**: https://docs.omniverse.nvidia.com/prod_kit/prod_kit/overview.html
   - **Description**: URL for the external kit SDK.

### exts."omni.kit.menu.common".kit_sdk_name
   - **Default Value**: Discover Kit SDK
   - **Description**: Name for the kit SDK.
   - NOTE: If this is "" then the menu will not be added

## Settings Used by the Extension but Provided by Another Extension
### /exts/omni.appwindow/listenF11
   - **Default Value**: False
   - **Description**: Determines whether the app window listens for the F11 key for toggling fullscreen mode.
   - NOTE: As this extension also bind F11 key, this must be False to prevent double binding. So always load via .kit file

### /app/window/showDpiScaleMenu
   - **Description**: Controls the visibility of the DPI scale menu in the window settings.
