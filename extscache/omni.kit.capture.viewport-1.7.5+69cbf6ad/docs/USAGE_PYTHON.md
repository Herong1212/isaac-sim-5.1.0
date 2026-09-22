# Usage Examples

## Capture A Single Frame as Image

```python
import omni.kit.app
from omni.kit.capture.viewport import CaptureExtension, CaptureOptions
import omni.kit.viewport.utility as vp_utils
import asyncio

async def get_outputs_async(capture_instance):
    while not capture_instance.done:
        await omni.kit.app.get_app().next_update_async()

    output_files = capture_instance.get_outputs()
    print(f"Captured files: {output_files}")

# Get the capture instance
capture = CaptureExtension.get_instance()

# Create capture options
viewport = vp_utils.get_active_viewport()
options = CaptureOptions()
options.camera = viewport.camera_path.pathString
options.output_folder = "/path/to/output"
options.file_name = "SingleFrameImage"
capture.options = options

# Start the capture
if capture.start():
    asyncio.ensure_future(get_outputs_async(capture))
```
---

## Capture Sequence of Frames as Images

```python
import omni.kit.app
from omni.kit.capture.viewport import CaptureExtension, CaptureOptions, CaptureRangeType
import omni.kit.viewport.utility as vp_utils
import asyncio

async def get_outputs_async(capture_instance):
    while not capture_instance.done:
        await omni.kit.app.get_app().next_update_async()

    output_files = capture_instance.get_outputs()
    print(f"Captured files: {output_files}")

# Get the capture instance
capture = CaptureExtension.get_instance()

# Create capture options
viewport = vp_utils.get_active_viewport()
options = CaptureOptions()
options.camera = viewport.camera_path.pathString
options.output_folder = "/path/to/output"
options.file_name = "SequenceCapture"
options.range_type = CaptureRangeType.FRAMES
options.start_frame = 1
options.end_frame = 10
options.capture_every_Nth_frames = 1
options.fps = 30
options.overwrite_existing_frames = True
capture.options = options

# Start the capture
if capture.start():
    asyncio.ensure_future(get_outputs_async(capture))
```
---

## Capture Sequence of Frames to Video

```python
#############################################################
# NOTE: omni.videoencoding must be enabled to capture video
#############################################################
import omni.kit.app
from omni.kit.capture.viewport import CaptureExtension, CaptureOptions, CaptureRangeType
import omni.kit.viewport.utility as vp_utils
import asyncio

async def get_outputs_async(capture_instance):
    while not capture_instance.done:
        await omni.kit.app.get_app().next_update_async()

    output_files = capture_instance.get_outputs()
    print(f"Captured files: {output_files}")

# Get the capture instance
capture = CaptureExtension.get_instance()

# Create capture options
viewport = vp_utils.get_active_viewport()
options = CaptureOptions()
options.camera = viewport.camera_path.pathString
options.output_folder = "/path/to/output"
options.file_name = "VideoCapture"
options.file_type = ".mp4"
options.range_type = CaptureRangeType.FRAMES
options.start_frame = 1
options.end_frame = 10
options.capture_every_Nth_frames = 1
options.fps = 30
options.overwrite_existing_frames = True
capture.options = options

# Start the capture
if capture.start():
    asyncio.ensure_future(get_outputs_async(capture))
```
---

## Capture With Render Product

```python
#############################################################################
# NOTE: following extensions must be enabled to capture with render product
#       omni.graph
#       omni.graph.nodes
#       omni.graph.examples.cpp
#############################################################################
import omni.kit.app
from omni.kit.capture.viewport import CaptureExtension, CaptureOptions, CaptureRenderPreset
import omni.kit.viewport.utility as vp_utils
import asyncio

async def get_outputs_async(capture_instance):
    while not capture_instance.done:
        await omni.kit.app.get_app().next_update_async()

    output_files = capture_instance.get_outputs()
    print(f"Captured files: {output_files}")

# Get the capture instance
capture = CaptureExtension.get_instance()

# Create capture options
viewport = vp_utils.get_active_viewport()
options = CaptureOptions()
options.camera = viewport.camera_path.pathString
options.output_folder = "/path/to/output"
options.file_name = "RenderProductCapture"
options.file_type = ".exr"
options.render_preset = CaptureRenderPreset.PATH_TRACE
options.render_product = "/Render/RenderView"
capture.options = options

# Start the capture
if capture.start():
    asyncio.ensure_future(get_outputs_async(capture))

```
