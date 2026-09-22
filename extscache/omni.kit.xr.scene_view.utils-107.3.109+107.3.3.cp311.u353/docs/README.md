# SceneView Utils [omni.kit.xr.sceneview_utils]

This is a collection of helper functions and classes to make creating and manipulating `omni.ui.scene.SceneView`-based UIs smoother by handling the boilerplate for you.

Here are the main classes:
- `WidgetComponent`: This wrapper handles taking a "normal" `omni.ui` setup and giving it a transform and size in 3D.
- `UiContainer`: this is the "top-level" container class for when you want a UI. Your UI's lifecycle is tied to this object, so if you drop the object, your UI will be removed, and any references to UI items may cause errors if you try to use them.
- `SceneViewUtils`: a helper class for setting up and destroying `omni.ui.scene.SceneView` instances. For the most part, you shouldn't need to interface with this, as other classes handle managing one of these already.

The major components to use are `SceneWidgetManipulator` for placing `omni.ui` interfaces into the scene, as well as `ManipulatorComponent` and its child classes for more easily attaching logic to your scene elements.

This utility library is a work in progress, and so there may be breaking changes in the future.
