```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

## Introduction
A high level implementation of a Window that contains a Viewport and variety of menus and manipulators for interacting
and controlling a {py:class}`pxr.usd.UsdStage` attached to a specific {py:class}`omni.usd.UsdContext`.

### How to create a new ViewportWindow

#### Python

1. Import the class from the package:
```python
from omni.kit.viewport.window import ViewportWindow
```

2. Create a ViewportWindow instance named "Demo", attached to the default UsdContext
```python
viewport_window = ViewportWindow("Demo", width=640, height=480)
```

3. Get the active ViewportAPI attached to the ViewportWindow and inspect some properties.
```python
viewport_api = viewport_window.viewport_api
usd_context = viewport_api.usd_context
usd_context_name = viewport_api.usd_context_name
usd_stage = viewport_api.stage
camera_path = viewport_api.camera_path
resolution = viewport_api.resolution
```

## Further reading
[Viewport Documentation](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.viewport.docs/latest)

[Tutorials](https://docs.omniverse.nvidia.com/extensions/latest/ext_core/ext_viewport.html)
