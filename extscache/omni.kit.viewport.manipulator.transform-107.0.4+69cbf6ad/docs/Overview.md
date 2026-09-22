```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.viewport.manipulator.transform` module provides a set of tools and classes for manipulating and transforming objects within a viewport. The module includes utilities for handling transformations, accessing transformation data, and managing viewport states.

## Important API List
The module consists of the following main components:
- [ManipulationMode](omni.kit.viewport.manipulator.transform/omni.kit.viewport.manipulator.transform.ManipulationMode): Defines different modes for manipulating objects in a 3D space.
- [Viewport1WindowState](omni.kit.viewport.manipulator.transform/omni.kit.viewport.manipulator.transform.Viewport1WindowState): Manages the state of Viewport-1 windows, including selection and picking functionalities.
- [DataAccessorRegistry](omni.kit.viewport.manipulator.transform/omni.kit.viewport.manipulator.transform.DataAccessorRegistry): Manages and provides access to DataAccessor instances.
- [DataAccessor](omni.kit.viewport.manipulator.transform/omni.kit.viewport.manipulator.transform.DataAccessor): Provides methods to retrieve and clear transformation data for objects.
- [ViewportTransformModel](omni.kit.viewport.manipulator.transform/omni.kit.viewport.manipulator.transform.ViewportTransformModel): Manages viewport transformations in a USD context.

## General Use Case
Users can leverage this module to handle various transformation and manipulation tasks within a 3D environment. It is particularly useful for managing object transformations, accessing transformation data efficiently, and handling viewport-specific states and interactions. This module is essential for developers working with interactive 3D applications that require precise control and manipulation of objects within a viewport. For examples of how to use the APIs, please look at [usage](USAGE_PYTHON) pages.

## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)
- [](SETTINGS)
