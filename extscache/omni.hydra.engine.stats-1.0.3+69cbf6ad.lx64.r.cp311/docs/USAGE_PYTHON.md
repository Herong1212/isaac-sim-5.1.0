# Usage Examples

## Retrieve Memory Statistics

```python
import omni.hydra.engine.stats as engine_stats

# Get general memory statistics
mem_stats = engine_stats.get_mem_stats()
for stat in mem_stats:
    print(f"{stat['category']}: {stat['size']}")

# Get detail memory statistics (more categories)
detail_mem_stats = engine_stats.get_mem_stats(detailed=True)
for detail_stat in detail_mem_stats:
    print(f"{detail_stat['category']}: {detail_stat['size']}")
```

## Get Device Information

```python
import omni.hydra.engine.stats as engine_stats

# Get all device information
all_devices = engine_stats.get_device_info()
for device in all_devices:
    for name, value in device.items():
        print(f"{name}: {value}")

# Get first device information
first_device = engine_stats.get_device_info(device_index=0)
for device in first_device:
    for name, value in device.items():
        print(f"{name}: {value}")
```

## Access Hydra Engine Statistics

```python
import omni.hydra.engine.stats as engine_stats
import carb.settings

# Create a HydraEngineStats instance
hd_stats = engine_stats.HydraEngineStats()

# Get nested GPU profiler results, which should be indexable
nested_gpu_profiler_results = hd_stats.get_nested_gpu_profiler_result()
print("Nested GPU Profiler Results are indexable.")

# Get flat GPU profiler results
gpu_profiler_results = hd_stats.get_gpu_profiler_result()
print("GPU Profiler Results are indexable.")

save_file = "test.json"
succ = hd_stats.save_gpu_profiler_result_to_json(save_file)
if succ:
    settings = carb.settings.get_settings()
    save_path = settings.get("/profiler/filePath")
    print(f"Saved to {save_path}/{save_file}")

# Reset GPU profiler containers
reset_success = hd_stats.reset_gpu_profiler_containers()
print(f"GPU Profiler Containers Reset: {reset_success}")
```

## Hydra Engine Statistics with Specific Context

```python
import omni.hydra.engine.stats as engine_stats

# Create a HydraEngineStats instance with a named UsdContext
hd_stats_specific = engine_stats.HydraEngineStats(usd_context_name='')

# Similar operations as the general HydraEngineStats instance
nested_gpu_profiler_results_specific = hd_stats_specific.get_nested_gpu_profiler_result()
print("Nested GPU Profiler Results for specific context are indexable.")

gpu_profiler_results_specific = hd_stats_specific.get_gpu_profiler_result()
print("GPU Profiler Results for specific context are indexable.")

# Reset operation
reset_success_specific = hd_stats_specific.reset_gpu_profiler_containers()
print(f"GPU Profiler Containers Reset for specific context: {reset_success_specific}")
```

