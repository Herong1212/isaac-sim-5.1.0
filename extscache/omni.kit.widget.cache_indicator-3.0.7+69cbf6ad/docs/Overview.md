```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

Cache Status Indicator is an Omniverse Kit extension designed to manage the installation and update processes for the Hub. It provides an interactive user interface that informs you about the current state of the Hub cache, including whether it is running, installing, or requires an update.

## Concepts

- **Cache and Hub State** – The extension uses a set of predefined states (such as HUB_RUNNING, HUB_NOT_DETECTED, HUB_INSTALLING, HUB_UPDATE_DETECTED, and HUB_INSTALLED) to represent the current condition of the Hub.  
- **Version Management** – It compares the local Hub cache version against the remote version using semantic versioning. This ensures that any required updates are detected accurately, even when multiple versions might exist from legacy setups.
- **NGC Integration** – The system interfaces with NVIDIA’s NGC API. This enables the extension to retrieve authentication tokens, query for the latest versions, and download updated files while handling errors gracefully.

## Functionality

- **User Interface Indicators** – A dedicated menu is registered to display cache and Hub status. The UI delegate updates dynamically, reflecting changes such as when the hub is starting, installing, or when a newer version is available.
- **Update Checking and Downloading** – As part of its workflow, the extension automatically checks if a new version of the Hub cache is available. When an update is detected, it provides options to download and install the latest version.
- **Version Comparison** – Utilizing a semver-compatible class, it ensures that version comparisons are accurate, offering clear insights into whether the local installation is outdated.
- **Error Notifications** – It includes mechanisms to log HTTP errors and post warnings or notifications, helping users quickly identify and resolve issues during the installation process.

## Configuration

- **NGC Settings** – The extension settings require a valid NGC API key and specify key identifiers, including organization (defaulted to “nvidia”), team (“omniverse”), and resource (“hub_workstation_cache”).  
- **API Endpoint and Package Path** – The NGC API endpoint and the default package installation path can be configured, ensuring that the extension operates within your specific system environment.
- **Update Checks** – An option is available to enable or disable automatic update checks ensuring that the extension’s behavior can be fine-tuned according to operational needs.
- **Custom Install Path** – Cache Status Indicator will install Hub into a custom location if one is configured in the environment. This is same path used by the Hub client to search for Hub installations, and is currently indicated by the 'OMNICLIENT_HUB_EXE' environment variable. If set, this should be the directory below which new Hub installations will be located. Please note that this is an experimental feature and subject to change.

## Relationships

- **UI and Notification Integration** – It depends on Omniverse Kit’s UI and menu utilities to display component statuses, positioning the cache indicator adjacent to other live status indicators when applicable.
- **Optional Dependencies** – The extension integrates with additional modules, such as live indicator support and notification management, to enhance user feedback and ensure a consistent experience across the application.

## Considerations

- **Version Ambiguity** – In rare cases, multiple versions of the Hub cache might be present due to legacy installations. The extension attempts to identify the most recently installed version but users should be aware of this possibility.  
- **NGC Credentials** – Successful operation hinges on proper NGC account credentials and API key configuration; missing or incorrect settings may prevent the extension from resolving update information accurately.

This extension simplifies the management of your Hub cache by providing clear visual indicators and an automated approach to checking and applying updates, all integrated directly within the Omniverse Kit environment.