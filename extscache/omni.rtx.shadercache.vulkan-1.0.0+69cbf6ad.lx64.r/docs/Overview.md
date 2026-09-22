```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
Note: This extension is kept for backward compatibility and is no longer required to be used. 
Please refer to the documentation of individual shader cache extensions on how to create new shader cache extensions for your plugin. 

- omni.gpu_foundation.shadercache.vulkan: for UI renderer.
- omni.hydra.rtx.shadercache.vulkan: for RTX renderers.
- omni.hydra.iray.shadercache.vulkan: for Iray renderer.

This extension simply loads all the existing Vulkan shader cache extensions as dependencies and adds them to the search path of shaderDb. They contain Vulkan shader caches for all the official renderers shipped by Kit apps and plugins that use shaderDb.
It is deprecated in favor of shipping individual "omni.{Plugin}.shadercache.vulkan" extensions.

## General Use Case
Explicitly including this extension in an app file loads all the officially available Vulkan shader cache extensions in advance, rather than waiting for each renderer to load it at runtime.
Instead of using this extension, each renderer is now shipped with their own shader cache extension as an optional or required dependency.

On Windows, your app may include either D3D12 or Vulkan cache extension in the app file, and then it can exclude unwanted default caches using `--/app/extensions/excluded`  when a specific graphics API is only desired. Note that at least one of the D3D12 or Vulkan caches are mandatory for Windows. Currently, Linux requires Vulkan caches.

## User Guide
- [](CHANGELOG)

