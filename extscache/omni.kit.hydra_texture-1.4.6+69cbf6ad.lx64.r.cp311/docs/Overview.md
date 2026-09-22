```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

## Introduction
A very low level extension for receiving renderer output as texture, which is usually then piped into the UI or captured directly.  {py:mod}omni.kit.widget.viewport uses this extension to start a render and begin receiving its output.

Generally it is better to use higher level extensions like {py:mod}`omni.kit.widget.viewport` or {py:mod}`omni.kit.viewport.window`.


### How to create a new HydraTexture

#### Python

1. Import the relevant module and function.
```python
from omni.kit.hydra_texture import acquire_hydra_texture_factory_interface
```

2. Get the HydraTexture factory interface to start creating HydraTextures
```python
texture_factory = acquire_hydra_texture_factory_interface()
# Make sure to run any initialization/startup that must occur
texture_factory.startup()
```

3. Make sure the engine-type is attached to the UsdContext
```python
engine_name = "rtx"
usd_context_name = ""
usd_context = omni.usd.get_context(usd_context_name)
if not usd_context:
    raise RuntimeError(f"UsdContext named '{usd_context_name}' does not exist")
if engine_name not in usd_context.get_attached_hydra_engine_names():
    omni.usd.add_hydra_engine(engine_name, usd_context)
```

4. Create a HydraTexture object rendering with RTX at 1280x720, for a UsdGeom.Camera named "/OmniverseKit_Persp" on the default omni.usd.UsdContext (named "")
```python
hydra_texture = texture_factory.create_hydra_texture(
    name="your_unique_name",
    width=1280,
    height=720,
    usd_context_name=usd_context_name,
    usd_camera_path="/OmniverseKit_Persp",
    hydra_engine_name=engine_name)
```

5. Subscribe to the event with a callback when a new frame is delivered
```python
# Import carb for logging and type-hinting support with the callback
import carb

def renderer_completed(event: carb.events.IEvent):
    if event.type != omni.kit.hydra_texture.EVENT_TYPE_DRAWABLE_CHANGED:
        carb.log_error("Wrong event captured for EVENT_TYPE_DRAWABLE_CHANGED!")
        return

    # Get a handle to the result
    result_handle = event.payload['result_handle']
    # And pass that to the HydraTexture instance to get the AOV's that are available
    aov_info = hydra_texture.get_aov_info(result_handle)
    print(f"Available AOVs: {aov_info}")

    # Get an object for a specific AOV and include the GPU texture in the info
    ldr_info_array = hydra_texture.get_aov_info(result_handle, 'LdrColor', include_texture=True)
    print(f"LdrColor AOVs are: {ldr_info_array}")

    ldr_texture = ldr_info_array[0].get("texture", None)
    assert ldr_texture is not None

    ldr_color_res = ldr_texture.get("rp_resource")
    ldr_color_gpu_tex = ldr_texture.get("rp_resource")
    print(f"LdrColor[0]: {ldr_color_res}, {ldr_color_gpu_tex}")

    # YOU CANNOT USE THE RESOURCE OUTSIDE OF THIS FUNCTION/SCOPE
    # ldr_color_gpu_tex must be consumed now or passed to another object
    # that will use / add-ref the underlying GPU-texture.

event_sub = hydra_texture.get_event_stream().create_subscription_to_push_by_type(
    omni.kit.hydra_texture.EVENT_TYPE_DRAWABLE_CHANGED,
    renderer_completed,
    name="Your unique event name for profiling/debug purposes",
)

# When event_sub object is destroyed (from going out of scope or being re-assigned)
# then the callback will stop being triggered.
# event_sub = None
```
