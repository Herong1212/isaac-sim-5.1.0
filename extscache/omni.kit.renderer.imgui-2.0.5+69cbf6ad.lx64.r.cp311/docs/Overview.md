
```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

omni.kit.renderer.imgui is a low level GUI rendering extension. This extension subscribes to rendering events emitted from the omni.kit.renderer.core and implements an ImGUI rendering backend, i.e. it does actual windows, buttons, fonts rendering. It is essential for omni.ui which is the UI toolkit for creating graphical user interfaces in the Kit extensions.

There are no public Python or C++ interfaces available to access this low-level functionality directly.