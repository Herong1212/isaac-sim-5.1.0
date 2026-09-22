```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.async_engine` module is designed to integrate Python's asyncio with the application's update cycle, enabling asynchronous coroutine execution within the application's main event loop. It provides a mechanism to submit coroutines for execution and ensures that the main event loop object is consistent and accessible across different modules.

## Important API List
- [run_coroutine](omni.kit.async_engine/omni.kit.async_engine.run_coroutine): Submit a coroutine to be executed on the main event loop and return a task or future object, depending on the calling thread.

## General Use Case
The main use case for the `omni.kit.async_engine` module is to enable asynchronous programming patterns within applications that have a main event loop. Developers can use `run_coroutine` to schedule coroutines to be run asynchronously, integrating smoothly with the application's event-driven architecture. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)