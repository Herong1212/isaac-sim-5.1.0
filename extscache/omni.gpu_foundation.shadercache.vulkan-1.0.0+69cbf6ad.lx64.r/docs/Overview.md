```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

This extension contains precompiled Vulkan shader caches for GPU Foundation and UI renderer, and upon loading it will add them to the search path of shaderDb.
Without shader caches, Kit apps are not able to continue.

## General Use Case

The GPU Foundation plugin requires this extension as dependency for some shader-based operations, such as render graphs. It will be automatically loaded by GPU Foundation, unless it is excluded explicitly and replaced with another alternative cache extension.

On Windows, your app may include either D3D12 or Vulkan cache extension in the app file, and then it can exclude unwanted default caches using `--/app/extensions/excluded`  when a specific graphics API is only desired. Note that at least one of the D3D12 or Vulkan caches are mandatory for Windows. Currently, Linux requires Vulkan caches.

## User Guide
- [](CHANGELOG)
- [](USAGE_PYTHON)

