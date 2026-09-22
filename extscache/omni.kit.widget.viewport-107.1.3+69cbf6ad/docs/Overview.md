```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

## Introduction
A low level implementation of an {py:class}`omni.ui.Widget` that displays rendered output.
The {py:class}`omni.kit.widget.viewport.ViewportWidget` does not include any additional features (such as menu-items or
manipulators).  It is used by {py:class}`omni.kit.viewport.window.ViewportWindow` to provide a higher level, default Viewport
experience in Kit based apps.

### How to create a new ViewportWidget

#### Python

1. Import {py:mod}`omni.ui` so the {py:class}`ViewportWidget` can be created inside an {py:class}`omni.ui.Window`
```python
import omni.ui as ui
```

2. Import the class from the package:
```python
from omni.kit.widget.viewport import ViewportWidget
```

3. Choose the resolution and camera this instance will start rendering with.
```python
resolution=(512, 512)
camera_path="/OmniverseKit_Persp"
```

3. Create an empty {py:class}`omni.ui.Window` and instantiate a new {py:class}`ViewportWidget` in its {py:class}`omni.ui.Frame`
```python
window = ui.Window("Demo ViewportWidget", width=resolution[0], height=resolution[1])
with window.frame:
  vp_widget = ViewportWidget(camera_path=camera_path, resolution=resolution)
```

3. Get the active ViewportAPI attached to the {py:class}`ViewportWidget` and inspect some properties.
```python
viewport_api = vp_widget.viewport_api
usd_context = viewport_api.usd_context
usd_context_name = viewport_api.usd_context_name
usd_stage = viewport_api.stage
camera_path = viewport_api.camera_path
resolution = viewport_api.resolution
```

## Further reading
[Viewport Documentation](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.viewport.docs/latest)

[Tutorials](https://docs.omniverse.nvidia.com/extensions/latest/ext_core/ext_viewport.html)
