```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```


# Overview


The `omni.activity.profiler` extension provides python bindings for acquiring and releasing profilers for activity events which converts carb profiler events to omniverse activity events. It is a telemetry extension which allows users to profile omniverse activity events.


It provides APIs of `enable_capture_mask` and `disable_capture_mask` which filters specific activity event out defined with a capture mask, e.g. `omni.activity.profiler.CAPTURE_MASK_LATENCY`.


There are three capture masks defined in this extension:
- omni.activity.profiler.CAPTURE_MASK_SCENE_LOADING: profiles USD scene loading activity
- omni.activity.profiler.CAPTURE_MASK_LATENCY: profiles latency
- omni.activity.profiler.CAPTURE_MASK_STARTUP: profiles startup activity


The capture mask could be combined with bitwise or operator, e.g. `omni.activity.profiler.CAPTURE_MASK_STARTUP | omni.activity.profiler.CAPTURE_MASK_LATENCY` captures both startup and latency.


## Important API List
- **acquire_activity_profiler**: Acquire activity profiler interface.
- **release_activity_profiler**: Release activity profiler interface
- **enable_capture_mask**: Enable a capture mask for the activity profiler, and enable the activity core if needed.
- **disable_capture_mask**: Disable a capture mask that was previously set, and disable the activity core if needed.


## General Use Case
The capture masks are used to send profiler events that should be processed by the carb.profiler-activity backend. When we start capturing activity spans, the capture mask of the carb.profiler-activity implementation should be set to the value corresponding to events we want to capture (for example scene loading or input latency). Then when we
stop capturing activity spans the capture mask should be reset to kCaptureMaskNone to avoid unnecessary processing.


For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.


## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)
