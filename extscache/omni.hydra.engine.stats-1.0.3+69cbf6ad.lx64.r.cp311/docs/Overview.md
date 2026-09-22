```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.hydra.engine.stats` module provides functionalities to query memory statistics, device information and gpu profiler results related to the Hydra rendering engine used in Omniverse Kit SDK.

## Important API List
The module consists of the following main components:
- [HydraEngineStats](omni.hydra.engine.stats/omni.hydra.engine.stats.HydraEngineStats): A class to query and save gpu profiler result for usd context and hydra engine.
- [get_device_info](omni.hydra.engine.stats/omni.hydra.engine.stats.get_device_info): Retrieves information about the rendering device.
- [get_mem_stats](omni.hydra.engine.stats/omni.hydra.engine.stats.get_mem_stats): Retrieves memory statistics.

These components are essential for understanding and optimizing the rendering process.

## General Use Case
This extension is utilized for monitoring and optimizing the rendering performance within the Omniverse Kit SDK. Developers can use it to access detailed information about the hardware being used for rendering and to gather memory usage statistics, aiding in the identification of bottlenecks or inefficiencies in the rendering pipeline. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)