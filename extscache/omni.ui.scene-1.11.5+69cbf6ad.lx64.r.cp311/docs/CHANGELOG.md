# CHANGELOG

## [1.11.5] - 2025-08-25
### Fix
- Fixing potential use after free of cached gestures when Scene is destroyed mid draw.

## [1.11.4] - 2024-01-04
### Fix
- Fix leak of items on container clear().

## [1.11.3] - 2024-12-10
### Fixed
- Fixed Python GIL not releasing causing RasterImageProvider::_waitAsset to timeout and fail, which destroyed datasource connection before asset was loaded that led to AddressSanitizer: heap-use-after-free.

## [1.11.2] - 2024-11-14
### Changed
- Cleanup public API.

## [1.11.1] - 2024-10-03
### Added
-Revert adding `remove` OMNI_PROPERTY NOTIFY callbacks which is abi breaking change.

## [1.11.0] - 2024-09-25
### Added
-Added remove OMNI_PROPERTY NOTIFY callbacks.

## [1.10.4] - 2024-09-03
### Fixed
- OMPE-14095: Fix for drag gesture can be triggered when other widgets are resizing.
### Added
- OMPE-14095: Added test to check resizing on border doesn't trigger drag gesture.

## [1.10.3] - 2024-04-03
### Fixed
- OM-123043: release python GIL during omni.ui.scene object construction

## [1.10.2] - 2024-02-20
### Fixed
- Fix cache_draw_buffer's init cast missing

## [1.10.1] - 2024-01-11
### Added
- API to control devices that omni.ui.scene.Image are created on and omni.ui.scene.Widget is blited to.

## [1.10.0] - 2024-01-10
### Changed
- Decouple transform and content cache.

## [1.9.2] - 2023-12-08
### Changed
- Remove redundant upward traverse in gesture managers collecting.

## [1.9.1] - 2023-11-21
### Changed
- Filter gestures before GestureManager::prevent.

## [1.9.0] - 2023-11-16
### Added
- Caching draw buffer.

## [1.8.0] - 2023-11-08
### Fixed
- Optimized GestureManager::prevent

## [1.7.0] - 2023-11-08
### Added
- More granular carb profile-zones.

## [1.6.17] - 2023-11-06
### Added
- OMFP 3154: Improved gesture `__repr__` to avoid crash in generated binding code.

## [1.6.16] - 2023-10-03
### Fixed
- Keyboard in `sc.Widget`

## [1.6.15] - 2023-09-28
### Fixed
- Thread safety to SceneView via mutexes for CameraModel's itemChanged multi-threaded calls.

## [1.6.14] - 2023-07-19
### Fixed
- Setting `sc.Widget.resolution_width`/`sc.Widget.resolution_height` runtime.

## [1.6.13] - 2023-08-17
### Fixed
- Improved `sc.Arc` gesture culling accuracy by utilizing the camera direction over ray direction.
### Added
- Added test for `sc.Arc` to validate culling is operating accordingly.

## [1.6.12] - 2023-07-13
### Added
- Returning self from containers to implement proper context manager protocol support.

## [1.6.11] - 2023-07-10
### Changed
- Revert to 105.0 UV flipping brehavior and add optional argument to move to 106.0 USD Uv specification.

## [1.6.10] - 2023-07-05
### Fixed
- `sc.Curve` Cubic method no longer crashes the application when improper number of points are used.

## [1.6.9] - 2023-06-08
### Added
- Optional `TransformBasis` for `Transform` objects
- Python bindings to create `Transform` objects with a `TransformBasis` subclass

## [1.6.8] - 2023-05-24
### Added
- Ability to specifiy options to pass through to ImageProvider texture creation.
### Fixed
- Const correctness of exposed property getters.

## [1.6.7] - 2023-05-24
### Changed
- Handle V texture co-ordinate in drawsystem that needs to flip it, not in UV data specification.

## [1.6.6] - 2023-05-23
### Fixed
- `sc.Label` no longer crashes with empty string.

## [1.6.5] - 2023-04-26
### Fixed
- The functionality of DragGesture.check_mouse_moved

## [1.6.4] - 2023-04-04
### Changed
- Using RpResource to show app window in omni.ui.scene

## [1.6.3] - 2023-03-31
### Added
- Fixed a bug sending infinite amount of mouse drag deltas even if cursor is still (
OM-88669))

## [1.6.2] - 2023-03-16
### Added
- Access to the raw input data from gesture
- Math improvements (for example it wasn't possible to copy the matrix and thus
memorize the transformation on begin)

## [1.6.1] - 2023-03-10
### Changed
- Only create AbstractDrawSystem when scene has contents, and release it when scene is empty.
- Const correctness of buffers passed to AbstractDrawSystem::render.
- Release underlying AbstractDrawSystem when SceneView is made invisible.
### Fixed
- Lack of any signal to AbstractDrawSystem when SceneView contents are emptied.

## [1.6.0] - 2022-12-12
### Changed
- Caching canBePrevented and shouldPrevent to improve performance
- Added `image_width` and `image_height` to `sc.Image` that is useful to set the
  svg rasterization resolution
- Fix possible lifetime issue by keeping stack-top alive with a local shared_ptr.
### Fixed
- Indersection didn't work for small objects
- Issue with DoubleClickGesture not begin called when ClickGesture exists.

## [1.5.11] - 2022-12-12
### Fixed
- Memory leak in DrawList

## [1.5.10] - 2022-10-20
### Changed
- Added API for custom SceneView
- Added resolution to sc.Widget

## [1.5.9] - 2022-09-23
### Added
- Support middle and right mouse button in sc.Widget

## [1.5.8] - 2022-08-15
### Fixed
- SceneView should ignore scroll events if another window covers it

## [1.5.7] - 2022-08-09
### Fixed
- More precisely filter out mouse events in SceneView when the mouse hovers over
other windows.

## [1.5.6] - 2022-07-11
### Added
- The ability to copy sc.Scene and share between different sc.SceneViews

## [1.5.5] - 2022-07-12
### Fixed
- addPolygonMesh buffer issue which causes the color leak (OM-56044)
- add tests to check the fix

## [1.5.4] - 2022-06-27
### Fixed
- Crash when relasing a big number of sc.TexturedMesh

## [1.5.3] - 2022-06-15
### Fixed
- Crash when relasing a big number of sc.Images

## [1.5.2] - 2022-06-03
### Fixed
- The failure of `omni.kit.core.tests` tests. It failed because it imports
  `omni.ui.scene.tests` without initialization of `omni.ui.scene`
  (`omni.ext.IExt.on_startup`).

## [1.5.1] - 2022-05-18
### Added
- Vector3 cross and dot for python binding

## [1.5.0] - 2022-04-26
### Added
- TexturedMesh shape for free-form textured polygon mesh.
- Vector2 python binding type convertion
- Intersection for PolygonMesh
- Intersection for TexturedMesh with uv
- Created ImageHelper which contains the code shared by TexturedMesh and Image

## [1.4.6] - 2022-04-15
### Changed
- Fixed double world transform when `transform_space` between WORLD and NDC space.

## [1.4.5] - 2022-03-30
### Changed
- `sc.Widget` has transparent background

## [1.4.4] - 2022-03-23
### Fixed
- Used `getAmendedProjection` to transform to/from NDC space.

## [1.4.3] - 2022-03-14
### Added
- The property `intersection_thickness`

## [1.4.2] - 2022-03-11
### Fixed
- Intersection considers thickness
- sc.Arc should not flip angle when reaching +/- pi (OM-45724)

## [1.4.1] - 2022-03-10
### Added
- scene curve docs section

## [1.4.0] - 2022-03-08
### Added
- `sc.Widget` that allows to use omni.ui widgets in the scene

## [1.3.3] - 2022-02-24
### Fixed
- Gestures are uniform in horizontal/vertical directions

## [1.3.2] - 2022-02-01
### Added
- Property `culled` to `ArcGesturePayload`
### Changed
- GestureManager ignores invisible shapes

## [1.3.1] - 2022-01-31
### Added
- ScrollGesture

## [1.3.0] - 2022-01-27
### Added
- Double precision

## [1.2.0] - 2022-01-26
### Added
- Ability to inject own input to the gestures. Useful for tests.

## [1.1.4] - 2021-12-13
### Added
- More docs

## [1.1.3] - 2021-12-13
### Added
- Property to filter out mouse events from mouse events of widgets in
  `ui.VStack(content_clipping=1)`

## [1.1.2] - 2021-12-13
### Fixed
- Added sc.Line.thickness

## [1.1.1] - 2021-12-09
### Fixed
- Filter out the mouse events from the child windows

## [1.1.0] - 2021-11-25
### Changed
- Renamed Intersection to GesturePayload
### Added
- Python shortcuts to use the model with no item
- Python shortcuts to use sinle value instead of array in the model
- `transform_space(sc.Space.WORLD, sc.Space.NDC)`
- `transform_space(sc.Space.NDC, sc.Space.WORLD)`
### Fixed
- The mismatch of projection matrix in SceneView and Viewport

## [1.0.1] - 2021-11-01
### Added
- scene.Label to draw text
- scene.Manipulator

## [1.0.0] - 2021-10-19
### Added
- Initial implementation. There are Scene, Gestures and ImGui draw system
