# Python Usage Examples

## work with activity profiler
```python
import omni.activity.profiler

# acquire profiler interface
activity_profiler = omni.activity.profiler.acquire_activity_profiler(plugin_name="omni.activity.profiler.plugin")

# Enable an activity profiler capture mask through the activity profiler API.
uid1 = activity_profiler.enable_capture_mask(omni.activity.profiler.CAPTURE_MASK_LATENCY)

# Disable the first activity profiler capture mask that was set through the activity profiler API.
activity_profiler.disable_capture_mask(uid1)

# release profiler
omni.activity.profiler.release_activity_profiler(activity_profiler)
```
