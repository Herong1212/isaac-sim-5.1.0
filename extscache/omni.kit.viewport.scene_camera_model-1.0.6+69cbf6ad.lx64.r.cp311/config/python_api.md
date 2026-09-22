# Public API for module omni.kit.viewport.scene_camera_model:

## Classes

- class SceneCameraModel(omni.ui_scene._scene.CameraModel, omni.ui_scene._scene.AbstractManipulatorModel)
  - def __init__(self, usdContextName: str, viewportHandle: int)
  - def get_usdcontext_name(self) -> str
  - def get_viewport_handle(self) -> int
  - def set_usdcontext_name(self, usdContextName: str)
  - def set_viewport_handle(self, viewportHandle: int)
