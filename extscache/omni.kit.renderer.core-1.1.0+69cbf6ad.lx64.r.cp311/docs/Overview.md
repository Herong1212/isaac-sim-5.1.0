
```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

omni.kit.renderer.core is a low level abstract GUI rendering extension, i.e. it manages (through carb::graphics) swapchains, basic resources like textures/buffers, and implements an event structure for higher level systems (e.g. ImGui renderer, which is just one of the possible GUI renderers in theory). It supports multi-window too, including virtual windows.

There are no public Python or C++ interfaces available to access this low-level functionality directly.