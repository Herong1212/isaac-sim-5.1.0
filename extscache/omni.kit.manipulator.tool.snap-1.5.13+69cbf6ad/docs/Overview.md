```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The `omni.kit.manipulator.tool.snap` module provides snapping functionality as well as a registry for external snap tools. It allows objects to snap to various elements in the scene, such as other primitives, surface normals, or a grid.

The module is extensible, it allows developer to register their own `Snap Provider` to the registry to provide customized snapping behavior. The registered provider will be an option in the toolbar's context menu that user can choose as their manipulator's snap provider.

This extension also contains 3 built-in snap providers:
- Snap to Surface (framebuffer based).
- Snap to Prim transform.
- Snap to Grid (when grid is enabled).

It also contains `Explicit Transform` snapping, which is minimal increment for translate, scale and rotate.


## Important API List

- [RegistrationHelper](omni.kit.manipulator.tool.snap/omni.kit.manipulator.tool.snap.RegistrationHelper): A helper class for registering snap provider classes.
- [SnapProvider](omni.kit.manipulator.tool.snap/omni.kit.manipulator.tool.snap.SnapProvider): Abstract base class for snap providers.
- [SnapProviderManager](omni.kit.manipulator.tool.snap/omni.kit.manipulator.tool.snap.SnapProviderManager): Manages enabling, disabling, and updating snap providers. It also provides the interface to query the snap result.
- [SnapProviderRegistry](omni.kit.manipulator.tool.snap/omni.kit.manipulator.tool.snap.SnapProviderRegistry): Singleton registry for managing SnapProvider instances.
- [SnapToolButton](omni.kit.manipulator.tool.snap/omni.kit.manipulator.tool.snap.SnapToolButton): A button for toggling snap functionality in transform manipulators.
- [SnapToolExt](omni.kit.manipulator.tool.snap/omni.kit.manipulator.tool.snap.SnapToolExt): An extension for enabling and managing snap tools in the application.

## General Use Case

The snapping tool is generally used in the context of moving objects within the NVIDIA Omniverse Kit. It provides a way to align objects precisely with scene elements or a grid. For more detailed usage, please refer to the extension's usage page.

For more details on usage, please refer to the [usage page](https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_snap-tool.html).For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)