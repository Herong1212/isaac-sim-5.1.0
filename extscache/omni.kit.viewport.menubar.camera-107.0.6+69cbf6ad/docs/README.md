# omni.kit.viewport.menubar.camera
Camera setting of a Menu-Bar in the viewport

## How to Customize the Widgets for Camera List
By default, it will only show camera label in the camera list of viewport menubar. It also provides a way to 
append additional widgets to the right of camera label. You only need to derive the `omni.kit.viewport.menubar.camera.AbstractCameraButtonDelegate/AbstractCameraMenuItemDelegate` to provide widget delegate that works for building the widgets. The difference between `AbstractCameraButtonDelegate` and `AbstractCameraMenuItemDelegate` is that the prior one serves to provide widgets for the camera list button, and the latter serves to provide widgets for each camera menu item under the camera list. Those delegates are self-registered, so you only need to hold its unique instance to manage its lifecycle.

When menubar tries to build camera list, it will build camera label firstly, then following with traversing all instances of `AbstractCameraButtonDelegate/AbstractCameraMenuItemDelegate` to create corresponding widgets.
