# Public API for module omni.kit.manipulator.selection:

## Classes

- class SelectionManipulator(sc.Manipulator)
  - def __init__(self, style: dict = None, *args, **kwargs)
  - def on_build(self)
  - def on_model_updated(self, item)

- class SelectionMode
  - REPLACE: int
  - APPEND: int
  - REMOVE: int

- class SelectionShapeModel(sc.AbstractManipulatorModel)
  - def __init__(self, *args, **kwargs)
  - def get_item(self, name: str) -> sc.AbstractManipulatorItem()
  - def set_ints(self, name: str, values: Sequence[int])
  - def set_floats(self, name: str, values: Sequence[int])
  - def get_as_ints(self, name: str) -> List[int]
  - def get_as_floats(self, name: str) -> List[float]
