```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

**omni.kit.widget.nucleus_info** reports and queries the services available from a Nucleus server. The extension provides a lightweight interface to verify if certain services are active and retrieve information about all available services—both synchronously and asynchronously—making it useful for extensions that need to adapt based on server capabilities.

```{image} ../../../../source/extensions/omni.kit.widget.nucleus_info/data/preview.png
---
align: center
---
```


## Functionality

- **[is_service_available](omni.kit.widget.nucleus_info/omni.kit.widget.nucleus_info.is_service_available)**  
  Quickly checks whether a specific service exists on a Nucleus server.

- **[get_nucleus_services](omni.kit.widget.nucleus_info/omni.kit.widget.nucleus_info.get_nucleus_services)**  
  Retrieves a list of available services in a synchronous manner, providing a snapshot of the current server state.

- **[get_nucleus_services_async](omni.kit.widget.nucleus_info/omni.kit.widget.nucleus_info.get_nucleus_services_async)**  
  Performs the same retrieval asynchronously, enabling non-blocking updates when accessing service information.

## Dependencies

- Relies on **omni.client** for communicating with a Nucleus server.
- Integrates with **omni.ui** and **omni.kit.window.popup_dialog**, ensuring that any UI-based reporting leverages consistent window and dialog constructs within Omniverse Kit SDK.

## Considerations

- The extension is focused on reporting service availability and does not provide any mechanisms for modifying or configuring the Nucleus server.
- It is designed as a reporting utility; therefore, any timeout or connectivity issues should be managed by the consumer of these APIs rather than within this extension.

By using the provided APIs, developers can efficiently determine the readiness of Nucleus services and dynamically adjust their application's behavior accordingly.