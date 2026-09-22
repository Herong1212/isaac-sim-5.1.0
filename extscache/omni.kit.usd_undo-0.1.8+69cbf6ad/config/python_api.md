# Public API for module omni.kit.usd_undo:

## Classes

- class UsdLayerUndo
  - class Key
    - def __init__(self, path, info)
  - def __init__(self, layer: Sdf.Layer)
  - def reserve(self, path: Sdf.Path, info = None)
  - def undo(self)
  - def reset(self)

- class UsdEditTargetUndo(UsdLayerUndo)
  - def __init__(self, edit_target: Usd.EditTarget)
  - def reserve(self, path: Sdf.Path, info = None)
