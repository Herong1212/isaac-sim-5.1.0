# Overview

This is the extension providing prim manipulator selector in Kit.

Manipulator selector acts like the central manager for all _prim_ manipulators. Instead of subscribing to UsdStageEvent for selection change, prim manipulator should inherit `ManipulatorBase` class in this extension and implements all abstractmethods to support choosing between multiple types of prim manipulators based on their order and enable criterions.

The order of the manipulator is specified at carb.settings path `/persistent/exts/omni.kit.manipulator.selector/orders/<name>"`

## Class List
- **ManipulatorBase**:  An abstract base class that provides a foundation for implementing prim manipulators that work with the ManipulatorSelector. Instead of directly subscribing to USD stage events for selection changes, manipulators should inherit from ManipulatorBase and implement the required abstract methods. This allows the ManipulatorSelector to manage the selection and ordering of multiple manipulator types based on their order and enable criteria.

- **ManipulatorOrderManager**:  A class manages the order of manipulators and provides a way to subscribe to changes in the order. It uses the carb.settings module to retrieve and update the manipulator order settings. Subscribers can register functions to be called when the manipulator order changes.

- **ManipulatorSelector**:  A class manages the selection and ordering of manipulators in a USD context. It handles stage selection events and calls the appropriate manipulator's on_selection_changed method based on the manipulator order and enable criteria. Manipulators can register and unregister themselves with the ManipulatorSelector.

## Example Usage
```python
from omni.kit.manipulator.transform.manipulator import TransformManipulator

# Define a custom manipulator that inherits from ManipulatorBase
class PrimMeshManipulator(ManipulatorBase):
    def __init__(self, name, usd_context_name):
        super().__init__(name, usd_context_name)
        # could init TransformManipulator with custom model and gesture here
        self._manipulator = TransformManipulator()

    # This manipulator will only enabled when select mesh prim
    def on_selection_changed(self, stage: Usd.Stage, selection: Union[List[Sdf.Path], None], *args, **kwargs) -> bool:
        if selection is None:
            self._manipulator.model.on_selection_changed([])
            return False

        self._manipulator.model.on_selection_changed(selection)
        for path in selection:
            prim = stage.GetPrimAtPath(path)
            if prim.IsA(UsdGeom.Mesh):
                return True

        return False

    @property
    def enabled(self):
        self._manipulator.enabled

    @enabled.setter
    def enabled(self, value):
        self._manipulator.enabled = value

# Create an instance of your custom manipulator
mesh_manipulator = PrimMeshManipulator("my_manipulator_name", "my_usd_context_name")
```
