
```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

omni.kit.render.capture is an extension to capture different graphics resources to a file. It can be used to save specific swapchain buffer, GUI texture, or RpResource into a file with specified compression parameters.

Here is an example of using omni.renderer_capture to save RpResource into a file.

```python
import omni.ui as ui
import omni.kit.renderer_capture

def interecept_capture(*args, **kwargs):
    print("Capture callback called")

# create an example RpResource
data = [0, 0, 0, 255, 255, 0, 0, 255, 0, 255, 0, 255, 0, 0, 255, 255]
resolution = [2, 2]
textureprovider = ui.DynamicTextureProvider("textureX")
textureprovider.set_bytes_data(data, resolution)
# textureprovider.get_managed_resource() as the resource object needs to be passed to a consumer immediately and not held in Python variable/cached for later use

renderer = omni.renderer_capture.acquire_renderer_capture_interface()
# Request to capture RTX resource manager RpResource and trigger a callback when capture buffer is available.
renderer.capture_next_frame_rp_resource_callback(interecept_capture, resource=textureprovider.get_managed_resource())
# Capture RTX resource manager RpResource and save it to /your/file/path
renderer.capture_next_frame_rp_resource_to_file(filepath="/your/file/path.png", resource=textureprovider.get_managed_resource())
```

**Note**: this extension is under development, APIs could change largely in the future.