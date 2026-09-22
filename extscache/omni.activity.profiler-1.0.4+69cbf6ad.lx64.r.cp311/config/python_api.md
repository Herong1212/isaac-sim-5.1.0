# Public API for module omni.activity.profiler:

## Classes

- class IActivityProfiler
  - def disable_capture_mask(self, unique_identifier: int)
  - def enable_capture_mask(self, capture_mask: int) -> int

## Functions

- def acquire_activity_profiler(plugin_name: str = None, library_path: str = None) -> IActivityProfiler
- def release_activity_profiler(arg0: IActivityProfiler)

## Variables

- CAPTURE_MASK_SCENE_LOADING: int
- CAPTURE_MASK_LATENCY: int
- CAPTURE_MASK_STARTUP: int
