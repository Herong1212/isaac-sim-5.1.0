```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The Transform Manipulator Extension provides interactive manipulation tools for objects within a 3D scene. It includes a set of gestures and a manipulator (TransformManipulator) for translating, rotating, and scaling objects. The manipulator is customizable with different axes, models, styles, and gestures. It can be extended with tools that add functionality to the toolbar, such as snapping and precision control.

## Important API List

- [AbstractTransformManipulatorModel](omni.kit.manipulator.transform/omni.kit.manipulator.transform.AbstractTransformManipulatorModel): An abstract base class for creating models that define how manipulator gestures affect objects.
- [TransformChangedGesture](omni.kit.manipulator.transform/omni.kit.manipulator.transform.TransformChangedGesture): A gesture representing a change in a transformation, such as translation, rotation, or scaling.
- [TranslateChangedGesture](omni.kit.manipulator.transform/omni.kit.manipulator.transform.TranslateChangedGesture): A gesture representing a change in a translation during an interaction with a manipulator.
- [RotateChangedGesture](omni.kit.manipulator.transform/omni.kit.manipulator.transform.RotateChangedGesture): A gesture representing a change in rotation during an interaction with a manipulator.
- [ScaleChangedGesture](omni.kit.manipulator.transform/omni.kit.manipulator.transform.ScaleChangedGesture): A gesture representing a change in scaling during an interaction with a manipulator.
- [Operation](omni.kit.manipulator.transform/omni.kit.manipulator.transform.Operation): An enumeration representing different types of manipulator operations, like translation, rotation, and scaling.

## General Use Case

The Transform Manipulator Extension is used for interactive object manipulation in 3D scenes. This manipulator is made from and for omni.ui.scene. It provides a visual and interactive manipulator that users can interact with to move, rotate, or scale objects. The extension comes with a set of pre-defined gestures that handle different manipulation operations. Developers can create custom models derived from the AbstractTransformManipulatorModel to define custom behaviors for manipulation gestures.

Toolbar tools can be developed and registered to the ToolbarRegistry to extend the functionality of the manipulator's toolbar, providing users with additional controls and options while manipulating objects. The extension is highly extensible, allowing for the creation of custom manipulator tools that integrate seamlessly with the existing toolbar and manipulator framework. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)