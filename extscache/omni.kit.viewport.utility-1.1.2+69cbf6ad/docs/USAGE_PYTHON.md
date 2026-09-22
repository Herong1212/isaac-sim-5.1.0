```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Usage Examples

## Retrieve Active Viewport and Camera

```python
from omni.kit.viewport.utility import get_active_viewport, get_active_viewport_camera_path

# Retrieve the active viewport
viewport = get_active_viewport()

# Get the Sdf.Path to the camera used by the active viewport
camera_path = get_active_viewport_camera_path()
```

## Get Number of Viewports

```python
from omni.kit.viewport.utility import get_num_viewports

# Get the number of viewports
num_viewports = get_num_viewports()
```

## Capture Viewport to Image File

```python
import asyncio
from omni.kit.viewport.utility import capture_viewport_to_file, get_active_viewport

# Define the path to save the captured image
output_file_path = "/path/to/output/image.png"

# Capture the active viewport to the file
viewport = get_active_viewport()
capture_helper = capture_viewport_to_file(viewport, file_path=output_file_path)

# Wait for the capture to complete
async def wait_for_capture():
    await capture_helper.wait_for_result()

asyncio.run(wait_for_capture())
```

## Frame Selected Primitives in Viewport

```python
from omni.kit.viewport.utility import frame_viewport_prims, get_active_viewport

# Frame specified primitives in the active viewport
primitives_to_frame = ["/World/MyPrim1", "/World/MyPrim2"]
viewport = get_active_viewport()
frame_viewport_prims(viewport, prims=primitives_to_frame)
```

## Post Message to Viewport

```python
from omni.kit.viewport.utility import post_viewport_message, get_active_viewport

# Post a message to the active viewport
viewport = get_active_viewport()
post_viewport_message(viewport, "This is a test message")
```

## Disable Selection in Viewport

```python
from omni.kit.viewport.utility import disable_selection, get_active_viewport

# Disable selection in the active viewport
viewport = get_active_viewport()
disable_handle = disable_selection(viewport)

# Selection is now disabled; to re-enable, delete the handle
del disable_handle
```