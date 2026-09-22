# Public API for module omni.kit.viewport.manipulator.transform:

## Classes

- class ManipulationMode(IntEnum)
  - PIVOT: int
  - UNIFORM: int
  - INDIVIDUAL: int

- class Viewport1WindowState
  - def __init__(self)
  - def get_picked_world_pos(self)
  - def destroy(self)
  - def get_usd_context_name(self)

- class DataAccessorRegistry
  - def __init__(self)
  - def getDataAccessor(self)

- class DataAccessor
  - def __init__(self)
  - def get_local_to_world_transform(self, obj)
  - def get_parent_to_world_transform(self, obj)
  - def clear_xform_cache(self)

- class ViewportTransformModel(AbstractTransformManipulatorModel)
  - def __init__(self, usd_context_name: str = '', viewport_api = None)

- class ViewportTransformChangedGestureBase
  - def __init__(self, usd_context_name: str = '', viewport_api = None)
  - def on_began(self, payload_type = TransformDragGesturePayload)
  - def on_changed(self, payload_type = TransformDragGesturePayload)
  - def on_ended(self, payload_type = TransformDragGesturePayload)
  - def on_canceled(self, payload_type = TransformDragGesturePayload)

- class ViewportTranslateChangedGesture(TranslateChangedGesture, ViewportTransformChangedGestureBase)
  - def __init__(self, snap_manager: SnapProviderManager, **kwargs)
  - def on_began(self)
  - def on_ended(self)
  - def on_canceled(self)
  - def on_changed(self)

- class ViewportRotateChangedGesture(RotateChangedGesture, ViewportTransformChangedGestureBase)
  - def __init__(self, **kwargs)
  - def on_began(self)
  - def on_ended(self)
  - def on_canceled(self)
  - def on_changed(self)

- class ViewportScaleChangedGesture(ScaleChangedGesture, ViewportTransformChangedGestureBase)
  - def __init__(self, **kwargs)
  - def on_began(self)
  - def on_ended(self)
  - def on_canceled(self)
  - def on_changed(self)
