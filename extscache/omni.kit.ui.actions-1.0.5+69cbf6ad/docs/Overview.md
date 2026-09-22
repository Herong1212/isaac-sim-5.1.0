```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The **omni.kit.ui.actions** extension provides a set of actions and hotkey controls for managing viewport appearance and behavior. It enables users to easily toggle UI visibility, switch between fullscreen and windowed modes, and adjust interface scaling via DPI settings. This extension streamlines user workflows by integrating actions into hotkeys that are available as soon as the extension is enabled.

## Functionality

- The extension registers actions to control UI display (such as hiding or showing UI elements) and to toggle between different window modes (fullscreen versus windowed).  
- It includes mechanisms to adjust DPI scaling through hotkey-triggered actions, allowing users to increase, decrease, or reset the display scale settings.  
- Lifecycle functions manage the registration and deregistration of these actions and hotkeys, ensuring that UI behavior is consistently maintained during startup and shutdown.

## Configuration

- Specific settings allow control over whether UI hotkeys are registered (ui_hotkeys) and if the escape hotkey should remain active (ui_hotkey_escape).  
- The DPI scale adjustment settings include limits, defaults, and increment steps, giving users practical control over scaling without the need for direct code changes.

## Integration

- The extension integrates with core modules such as **omni.kit.hotkeys.core**, **omni.ui**, **omni.kit.context_menu**, and **omni.appwindow.**  
- It is designed to work harmoniously with other UI-related extensions; for instance, if **omni.kit.menu.common** is active, the internal UI hotkeys functionality is disabled to avoid conflicts.

## Considerations

- Users benefit from a ready-to-use interface that handles common UI state toggling and scaling operations without requiring additional API calls.  
- Proper cleanup of hotkey registrations and UI actions during shutdown prevents conflicts and ensures a consistent user experience throughout the lifecycle of the application.