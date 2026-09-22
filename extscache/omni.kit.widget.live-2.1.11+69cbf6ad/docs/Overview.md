```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

Live Mode Control Widget provides an interactive interface to monitor and control live session states directly within the Omniverse Kit environment. This extension is designed to offer users a clear and intuitive way to visualize and manage the live state of their sessions without needing additional coding. Users can view the number of users in the current live session, see the current live session state and interact with the widget dropdown menu to start, join or leave a live session.

## Concepts

- Live Mode Control Widget is built for users who want direct control over live session states.  
- The widget visually indicates the current live state and users in the current live session.

## Functionality

- The extension displays live session information via a dynamic menu, allowing users to quickly assess if a session is active.  
- It automatically registers UI elements such as menu items related to live state, ensuring that state changes are visible and controllable from the main interface.  
- Icons and styles are managed internally to maintain a consistent look-and-feel that aligns with the overall Omniverse Kit UI design.


## Relationships

- The extension integrates with several key components of the system, including the USD stage, live session management, and other UI elements provided by Omniverse Kit.  
- It depends on extensions such as **omni.usd**, **omni.client**, **omni.ui**, **omni.kit.usd.layers**, **omni.kit.menu.utils**, and **omni.kit.widget.live_session_management** to function properly, ensuring it works within a broader ecosystem managing live sessions.

## Considerations

- The user experience is streamlined for direct interaction through the UI, meaning no additional public API calls are required for regular use.  
- Live Mode Control Widget is tightly coupled with live session workflows; it is intended to function as a self-contained tool that enhances visibility and control over live states without the need for extensive reconfiguration.