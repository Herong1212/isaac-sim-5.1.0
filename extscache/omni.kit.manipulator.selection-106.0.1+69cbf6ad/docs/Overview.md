```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# omni.kit.manipulator.selection Module Overview

## Overview
The `omni.kit.manipulator.selection` module is part of the NVIDIA Omniverse Kit and provides functionality to create interactive selection manipulators within a 3D scene. These manipulators allow users to select objects using various gestures, such as clicking for single object selection or dragging to create a rectangle selection. The module includes classes to handle different selection modes, gesture recognition, and the visual representation of the selection region.

The module is designed to be extensible, supporting custom styles for the selection rectangle and integration into existing user interfaces. The selection process is managed by a model that handles the properties of the selection shape and updates the manipulator based on user interactions.

## Class List
- [SelectionMode](omni.kit.manipulator.selection/omni.kit.manipulator.selection.SelectionMode): An enumeration for different selection modes, including REPLACE, APPEND, and REMOVE.
- [SelectionShapeModel](omni.kit.manipulator.selection/omni.kit.manipulator.selection.SelectionShapeModel): A model to handle the selection region in a manipulator, managing selection shapes and their properties.
- [SelectionManipulator](omni.kit.manipulator.selection/omni.kit.manipulator.selection.SelectionManipulator): A manipulator class for selecting objects within a scene, providing functionality for various selection gestures and visual styling.

## General Use Case
The `omni.kit.manipulator.selection` module is typically used in applications that require interactive object selection within a 3D scene. It is useful for building tools that allow users to select, move, or otherwise interact with objects in a virtual environment. For instance, in a 3D modeling software, users can use the selection manipulator to select and transform models or parts of a scene.

For more details on how to use the selection manipulator, you can visit the [usage page](https://docs.omniverse.nvidia.com/py/kit/docs/package_omni.kit.manipulator.selection.html) which provides in-depth information and examples on integrating the module into your application.For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)