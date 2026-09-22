```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The `omni.kit.viewport.registry` extension is a part of the NVIDIA Omniverse Kit and is designed to manage and register viewport factories within the application. It maintains a list of items that want to be added to a default viewport. It provides a registry system that can be used to add and remove factories for scenes and viewport layers, as well as notify when changes occur.

## Important API List

- **_Factory**: An internal helper class that wraps a factory callable and its identifier.
- **_Registry**: An internal class that allows the registration and deregistration of viewport factories, and notifies subscribers of changes.
- **_make_registry**: Creates and returns the _Registry class. It provides mechanisms to invoke the provided callback function for each factory object that is not already recorded. Both [RegisterScene](omni.kit.viewport.registry/omni.kit.viewport.registry.RegisterScene) and [RegisterViewportLayer](omni.kit.viewport.registry/omni.kit.viewport.registry.RegisterViewportLayer) are an alias of `_make_registry`.

## General Use Case

The general use case for `omni.kit.viewport.registry` is to manage and keep track of different viewport-related factories within the Omniverse Kit applications. This can include registering new types of scenes or viewport layers, ordering them, and notifying when these items are loaded or unloaded. It is primarily used by developers who are extending the functionality of the application's viewport system.

For more detailed usage examples and information, developers should refer to the NVIDIA Omniverse Kit documentation and the source code of the `omni.kit.viewport.registry` extension.For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)