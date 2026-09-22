# omni.kit.viewport.scene_camera_model

# SceneCameraModel

SceneCameraModel is an enhanced camera model class in the Kit viewport that is designed specifically to improve navigation lag in omni.ui.scene. The core feature of SceneCameraModel is that it provides real-time synchronization between viewport status and the rendered content, leading to smoother scene navigation.

## Features
* Extends the basic `CameraModel`.
* Fetches the view matrix directly from `UsdFrameCompletionMonitor` ensuring the SceneView is always up-to-date and minimizing navigation lag.
* Protects view matrix from simultaneous read/write in multiple threads instilling thread safety.

## Usage
SceneCameraModel is automatically initiated and utilized in the viewport in Kit and does not need to be manually operated by users. `omni.kit.viewport` automatically adjusts viewport settings according to the frame updates to ensure smooth navigation.
