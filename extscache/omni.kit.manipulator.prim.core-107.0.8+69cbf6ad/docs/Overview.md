```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
This extension provides a comprehensive set of utilities for manipulating primitives in 3D space, offering capabilities such as translation, rotation, and scaling. It includes support for both global and local transformations and integrates snapping features for precise positioning. The extension also includes tools for setting the pivot point based on various criteria, such as the center of selection or bounding box. In addition to manipulating individual primitives, it can handle multiple selections with options to maintain or ignore spacing between objects during transformations. The extension accommodates both viewport and legacy modes, and it features a toolbar for easy access to manipulator settings and functions.

## Important API List
The module consists of the following main components:
- **PrimDataAccessorRegistry** : Manages the registration of data accessor functions for primitives.
- **TransformManipulatorRegistry** : Handles the lifecycle of transform manipulator instances in a scene.
- **PrimTransformManipulator** : Provides a manipulator for interactive transformation of USD prims.
- **PrimTransformModel** : Represents a model for transforming USD prims in a viewport.
- **get_toolbar_registry** : Retrieves the singleton instance of the toolbar registry for manipulator tools.

## General Use Case
The extension is used for transforming USD primitives within a 3D application, allowing users to translate, rotate, and scale objects with precision. It also provides tools for setting and manipulating the pivot point for transformations. Users can access these functionalities through a dedicated toolbar, enhancing the efficiency of 3D scene editing and manipulation workflows. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](CHANGELOG)