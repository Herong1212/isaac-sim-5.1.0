# Changelog

The Omniverse UI Framework.

`omni.ui` provides the basic types necessary to create rich extensions with a
fluid and dynamic user interface in the Omniverse applications.

## [2.27.1] - 2025-08-05
### Fixed
- Special case for checking "Status Bar" 's visibility since it is not an omni.ui.Window

## [2.27.0] - 2025-07-02
### Fixed
- When call ui.Workspace.show_window true to destroyed window, it will properly show the window.
- When check destroy window's visibility, it returns None instead of wong visibility
- Change Windowhandle's visible to always return None in python.
- Add deprecating warning message for WindowHandle's setVisible and Windowhandle's isVisible in c++.

## [2.26.18] - 2025-06-02
### Fixed
- OMPE-48505: for IntSlider, when min and max are not defined, calculate the ratio for negatives from 0.5 instead of from 0

## [2.26.17] - 2025-04-24
### Fixed
- OMPE-45159: fix the IntSlider has color leak with default min and max int

## [2.26.16] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [2.26.15] - 2025-04-21
### Fixed
- OMPE-40877 and OMPE-39249: Force dirty for all children in Grid when row or column is resized.

## [2.26.14] - 2025-04-11
### Added
- Add missing binding for get_show_window_titles

## [2.26.13] - 2025-04-08
### Added
- OMPE-43022: Handle the runtime exception when acquiring windowing interface on OVC2.

## [2.26.12] - 2025-04-01
### Added
- Add get_show_window_titles

### Fixed
- OMPE-28324: simplified the null function case in the binding for `set_show_window_fn()`.

## [2.26.11] - 2025-04-02
### Added
- set_active APIs to turn off internal draw-subscription callbacks.

## [2.26.10] - 2025-03-12
### Changed
- OMPE-17421: Implement rendering data window with overscan and cropping support

## [2.26.9] - 2025-02-28
### Changed
- OMPE-38818: Enabled syncTextureLoad in OmniUiTest.

## [2.26.8] - 2025-02-06
### Changed
OMPE-32734: Updated relaunching kit on linux

## [2.26.7] - 2025-01-28
### Fixed
- Fixed ui.Plot: accessing empty vectors causing crash.

## [2.26.6] - 2024-12-09
### Fixed
- Fixed AddressSanitizer: alloc-dealloc-mismatch in RasterHelper.
- Fixed AddressSanitizer: heap-use-after-free in Window.

## [2.26.5] - 2024-11-21
### Changed
- Added `zero_mouse=False` to `finalize_test()` function as mouse position can cause golden image to change due to mouse hover

## [2.26.4] - 2024-11-14
### Changed
- Cleanup public API: remove omni.gpu_foundation_factory transitive import.

## [2.26.3] - 2024-11-13
### Added
- Allow setting window shadow color.

## [2.26.2] - 2024-10-11
### Added
- Expose Image.progress as public.

## [2.26.1] - 2024-10-03
### Added
-Remove `remove expanding` of OMNI_PROPERTY NOTIFY callbacks which is not API compatible

## [2.26.0] - 2024-09-25
### Added
-Added remove and destroy OMNI_PROPERTY NOTIFY callbacks.
-Exposed remove_visibility_changed_fn and destroy_visibility_changed_fn for ui.Window

## [2.25.26] - 2024-09-23
### Fixed
-TreeView resizer should not move when mouse and resizer are detached.

## [2.25.25] - 2024-08-29
### Changed
-Revert the `show_title` proeprty to Menu change since that's not needed.

## [2.25.24] - 2024-08-14
### Added
-add `show_title` proeprty to Menu so that in the delegate we can choose to show the menu title.

## [2.25.23] - 2024-08-06
### Fixed
- OM-10975, OM-107306, OM-93481: add `resizeable_on_columns_resized` property for TreeView so that TreeView can be resized when resizing the columns.

## [2.25.22] - 2024-08-01
### Fixed
- OM-123534: Silence carb::settings::ISettings warnings.

## [2.25.21] - 2024-07-22
### Fixed
- OM-123534: Change ImageProviderCache logs from warning to verbose.

## [2.25.20] - 2024-06-25
### Changed
- OMPE-5467: Ensuring that changes to the plot data invalidates the raster cache

## [2.25.19] - 2025-06-13
### Fixed
- OMPE-5802: Force AbstractFied to be rasterized when it get keyboard focus.

## [2.25.18] - 2025-05-29
### Fixed
- Removed usage of omni.kit.ui

## [2.25.17] - 2024-05-22
### Changed
- OMPE-7960: Added tooltip delay setting "/exts/omni.ui/tooltip_delay" with default of 0.5 seconds

## [2.25.16] - 2024-05-07
### Fixed
- OM-124694: The column_count keyword arg used by AbstractMultiField was not working.

## [2.25.15] - 2024-05-07
### Fixed
- OM-87257: Fix for detached window being extremely jittery.

## [2.25.14] - 2024-05-06
### Added
- OMPE-3160: Update to `capture_and_compare()` as screenshot may not happen in  single frame.

## [2.25.13] - 2024-05-01
### Added
- OM-124520: Fixed `create_test_window()` to set `_need_finalize` flag so `tearDown()` can verify finalize was called.

## [2.25.12] - 2024-04-25
### Added
- test for OM-110998

## [2.25.11] - 2024-04-25
### Fixed
- OM-123940: Unlock GIL for preparedraw to fix deadlock when running DS2 scenarios.

## [2.25.10] - 2024-04-03
### Fixed
- OM-123043: release python GIL during omni.ui object construction

## [2.25.9] - 2024-03-20
### Fixed
- OMPRW-690: use PreUpdateEvent to refresh image in main thread

## [2.25.8] - 2024-03-14
### Fixed
-  OM-104436 - Changed setting "/exts/omni.ui/Image/generateMips" to "/persistent/exts/omni.ui/Image/generateMips"
-  OM-104436 - Added preferences page to enable "/persistent/exts/omni.ui/Image/generateMips" setting

## [2.25.7] - 2024-03-15
### Fixed
- Better scoping to prevent live objects from being de-allocated in callbacks.
- Order of texture aquisition and release to help mitigate present-thread-issues.

## [2.25.6] - 2024-03-08
### Fixed
- OM-52829 - Compute TreeView height accurately with header visible

## [2.25.5] - 2024-02-26
### Updated
- OM-120601 - Added enterprise_support tag

## [2.25.4] - 2024-02-23
### Fixed
- OM-120971 - Fixed BezierCurve's set_mouse_released_fn doesn't work.

## [2.25.3] - 2024-02-16
### Fixed
-  OM-117243 - Added `tearAt(float x, float y)` function and tear_at python binding.

## [2.25.2] - 2024-02-05
### Fixed
- OMPRW-709 - Added 2 dependencies to avoid warnings.

## [2.25.1] - 2024-02-05
### Changed
- Make identifier property fallback to the name property when not set.

## [2.25.0] - 2024-02-05
### Fixed
- OMFP-3693: Fix for not keeping the resize cursor when dragging on the Placer widget.
### Added
- OMFP-3693: Added test to ensure the resize cursor is shown when dragging on Placer widget and TreeView columns.

## [2.24.0] - 2024-01-26
### Fixed
- OMPRW-514: Check against null and expired shared_ptr in ColorWidget.

## [2.23.1] - 2024-01-25
### Fixed
- OM-98841 - Check for node in WindowHandle::focus to avoid crashes.

## [2.23.0] - 2024-01-23
### Fixed
- OMPRW-514 - Fixed ColorWidget popup when rasterizing is on.

## [2.22.4] - 2024-01-15
### Fixed
- OM-118335 - Fix omni.ui Performance warning.

## [2.22.3] - 2024-01-11
### Fixed
- OMFP-3693: Fix for no resizing cursor shown when resizing sub-windows.

## [2.22.2] - 2023-12-08
### Fixed
- OM-114680: fixed setting default style crashes kit

## [2.22.1] - 2023-11-29
### Fixed
- OM-115311: fix CanvasFrame pan regression in compatibility=False situation
- OM-76013: solve the zoom in/out carries in graph panel
- solves the pan carries in graph panel

## [2.22.0] - 2023-11-27
### Added
- Added BezierCurve and Line anchor functionality

## [2.21.11] - 2023-11-17
### Fixed
- OMFP-1669: fix mouse events on freeshapes with placer offsets

## [2.21.10] - 2023-11-21
### Fixed
- OM-114997: fix the tooltip not working for graph output and connection

## [2.21.9] - 2023-11-14
### Fixed
- OM-89039: add test for window docked status

## [2.21.8] - 2023-11-09
### Fixed
- OM-89039: proper fix for the docked property not correct for window which is docked but inactive

## [2.21.7] - 2023-11-06
### Fixed
- Handle possibility ImGui is not valid when using ui.Workspace.

## [2.21.6] - 2023-11-01
### Changed
- add tabBar_tooltip property for Window, so that user can add customized tooltip when hovering over window tabbar.

## [2.21.5] - 2023-10-31
### Changed
- Remove unnecessary tooltips from window tab bars

## [2.21.4] - 2023-08-10
### Fixed
- Clipping rectangle issue in CanvasFrame preventing visual artifacts on Linux with Vulkan.

## [2.21.3] - 2023-08-14
### Fixed
- Clipping of tooltips in CanvasFrame.

## [2.21.2] - 2023-10-05
### Added
- Two new settings have been added to the UI Workspace settings allowing control
  over draw freeze functionality:
- The `draw_freeze_enabled` setting at
  `/exts/omni.ui/workpace/draw_freeze/enabled` allows to enable or disable
  the draw freezing functionality. This provides a smoother user experience
  by reducing visual "blinking" during rapid layout changes.
- The `draw_freeze_frames` setting at
  `/exts/omni.ui/workpace/draw_freeze/frames` lets specify the number of
  frames the UI will wait after a layout change before it resumes normal
  drawing operations. This allows more control over the amount of time the
  layout change will take effect visually.

## [2.21.1] - 2023-10-24
### Fixed
- OM-89039: fix the docked state not correct for window which is docked but inactive

## [2.21.0] - 2023-10-10
### Fixed
- Fix mouse events not triggering for FreeShapes

## [2.20.5] - 2023-10-09
### Fixed
- OMFP-1891: Cease use of pip install in test

## [2.20.3] - 2023-09-26
### Fixed
- Invalidation of parent raster-draw list on when Widget is destroyed.
- Properly suspend rasterization during editing.
### Added
- More nullptr checking in RasterHelper.

## [2.20.2] - 2023-09-21
### Fixed
- Checking if m_prv is null in RasterHelper::invalidateRaster to avoid crashes.

## [2.20.1] - 2023-09-13
### Fixed
- Added support for `padding` style parameter to `ui.Plot`.

## [2.20.0] - 2023-08-29
### Fixed
- Undefined behavior in asynchronous ui.Image texture loading.

## [2.16.9] - 2023-08-25
### Fixed
- Zoom and Pan in Viewport were carrying over to graph editor.  Changed from using m_isPressed to m_isClicked.

## [2.16.8] - 2023-08-17
### Added
- Add check box border style options

## [2.16.7] - 2023-08-09
### Changed
- ui.Menu submenu cannot be moved off left side of window, this could happen if menu is widger than main window

## [2.16.6] - 2023-07-28
### Changed
- update ui.Image and ui.VectorImageProvider to support omni paths

## [2.16.5] - 2023-07-21
### Changed
- ui.Label multiline fix to align each line individually

## [2.16.4] - 2023-07-13
### Added
- Fixed moveToNewOSWindow issue with zero width/height windows

## [2.16.3] - 2023-07-18
### Changed
- Fix issue with `ui.TreeView` column width not updated correctly when column widths changed after node draw

## [2.16.2] - 2023-07-11
### Changed
- update ui.Menu submenu overlapping current menu in non-legacy mode as it sometimes
  didn't prevent overlapping menus.

## [2.16.1] - 2023-07-13
### Changed
- Returning self from containers for proper context manager protocol support.

## [2.16.0] - 2023-07-13
### Added
- Ability to get exact content width and height from labels

## [2.15.9] - 2023-07-12
### Removed
- ImageProvider python binding to set the image data from an texture handle pointer

## [2.15.8] - 2023-07-10
### Changed
- Fix column resize issue when lengthForFraction is below 0.

## [2.15.7] - 2023-06-28
### Changed
- fix ui.Menu submenu overlapping current menu in non-legacy mode

## [2.15.5] - 2023-05-30
### Fixed
- Crash related to ui.ImageProvider when toggling the present thread

## [2.15.4] - 2023-05-25
### Fixed
- ui.Label memory usage - all ui.Label widgets using the same font now share a
single font resource.
### Changed
- Implemented a workaround in CanvasFrame to keep font resources intact when
nodes are deleted.

## [2.15.4] - 2023-06-06
### Fixed
- Stack iteration invalidation no longer causes crashes with subsequent add/remove during drawing.

## [2.15.3] - 2023-06-01
### Added
- Ability to specify ImageProvider texture creation options more explicitly.
- Source URL argument to constructors of Vector and Raster image providers.

## [2.15.2] - 2023-06-01
### Changed
- Improve treeview to support configuration of minimum column width.
- Improve treeview to match the column resize behavior as Windows File Explorer.

## [2.15.1] - 2023-05-19
### Changed
- Cleanup IGpuFoundation interface acquisition and headers.

## [2.15.0] - 2023-05-16
### Fixed
- Const correctness of ImageProvider bytes argument
- Update version to refelct divergence from 105.0

## [2.14.26] - 2023-05-17
### Fixed
- Ensure unique window names are created in the ui test harness

## [2.14.25] - 2023-05-08
### Fixed
- Resize of detached window

## [2.14.24] - 2023-05-04
### Fixed
- Dirty flag of CanvasFrame LODs

## [2.14.23] - 2023-05-02
### Fixed
- Bug when raster didn't update when ui.Label is changed.

## [2.14.22] - 2023-04-27
### Changed
- Do not open sub-menus when parent menu is disabled.

## [2.14.21] - 2023-04-26
### Fixed
- Clipping in CanvasFrame

## [2.14.20] - 2023-04-25
### Fixed
- Rasterization when hovering ComboBox list outsize of the window

## [2.14.19] - 2023-04-21
### Fixed
- When using the raster pipeline `Frame.build_fn` wasn't called in some cases. Fixed.

## [2.14.18] - 2023-04-12
### Added
- restore_workspace handle windows undocking

## [2.14.17] - 2023-04-04
### Fixed
- Fix mouse_released_fn called on widgets that weren't pressed

## [2.14.16] - 2023-04-11
### Fixed
- The bug when the window that is created from the context menu is always
  created in the first appwindow.

## [2.14.15] - 2023-03-27
### Added
- Multiple draw lists is raster. It helps to zoom-in in on the graph editors
  without regenerating draw lists.

## [2.14.14] - 2023-03-10
### Fixed
- Updates to handle WindowHandle windows in dump_window & compare_workspace better

## [2.14.13] - 2022-03-16
### Fixed
- Blurry text in ui.CanvasFrame
- `visible_min` and `visible_max` properties in `CanvasFrame` raster pipeline
- Fix crash with mipmapped single channel image

## [2.14.12] - 2023-03-10
### Added
- OmniUiTest.capture_and_compare method for multiple image compares in one test.

## [2.14.11] - 2022-02-24
### Added
- Fixed leak in finalize_test_no_image function

## [2.14.10] - 2023-03-01
### Fixed
- Fixed crash with invalid font path

## [2.14.9] - 2022-01-16
### Added
- ui.Plot: ability to draw xy graphs

## [2.14.8] - 2023-02-16
### Fixed
- Fixed more tests that weren't working in random order.

## [2.14.7] - 2023-01-30
### Fixed
- Layout compare improvments

## [2.14.6] - 2023-02-13
### Fixed
- ui.Label goes into an inifinite loop when visible set to false

## [2.14.5] - 2023-02-09
### Changed
- Cleaned up ImageProvider headers and expose fewer internals.

## [2.14.4] - 2023-02-06
### Changed
- Fixed more tests that weren't working in random order.

## [2.14.3] - 2023-02-06
### Fixed
- ui.Menu: Fix for incorrect behavior of shown_changed_fn in torn off menu
- ui.Menu: Fix calling shown and torn callbacks when shown_changed_fn used with torn-off menu.

## [2.14.2] - 2023-02-01
### Changed
- Fixed multiple tests that weren't working in random order.
- Fixed golden img comparison diff image to have good alpha values.

## [2.14.1] - 2023-01-29
### Fixed
- Grid crash due to memory leaks

## [2.14.0] - 2023-01-19
### Changed
- Changed `moveToNewOSWindow()` and `moveToMainOSWindow()` to public methods with python bindings.

## [2.13.4] - 2022-01-11
### Fixed
- Remove early exit from ui.Placer when child size is less than or equal ot zero.

## [2.13.3] - 2023-01-10
### Fixed
- Tooltip position for omni.ui cache on mode near the boundary of the current canvasFrame

## [2.13.2] - 2023-01-04
### Changed
- Upload SVG data to texture without going to an on-disk image when possible.

## [2.13.1] - 2022-11-28
### Added
- The ability to rasterize ui.Frame and ui.Window to speed up the run loop.
  `ui.Frame(raster_policy=ui.RasterPolicy.AUTO)`. `ui.Placer` also supports it.
- A new method for rendering the ui.CanvasFrame that does not alter the
  position of the child widgets. This method involves rasterizing the entire
  canvas area and skipping the iteration of the child widgets during zoom, which
  can improve performance.

## [2.13.0] - 2022-12-12
### Fixed
- Removed warning in `ui.VectorImageProvider`. Instead, it waits whaen the
  widget resolution is more than 0.
### Changed
- Added additional validity checks and move some internal asserts to carb-errors.
- Fix a few possible lifetime issues by keeping local shared_ptr alive.
- Avoid some unnecessary copies into containers.

## [2.12.20] - 2022-12-06
### Fixed
- Grid crash due to trying to access an array element greater than its size

## [2.12.19] - 2022-12-05
### Added
- Add DynamicTextureProvider
- Add set_bytes_data_from_gpu to ByteImageProvider for cuda/warp integration

## [2.12.18] - 2022-10-20
### Changed
- TreeView behaviour in CanvasFrame

## [2.12.17] - 2022-11-30
### Fixed
- Frame using separate_window flag was growing constantly during drag & drop

## [2.12.16] - 2022-11-30
### Fixed
- Layout change crashes due to _restore_workspace_asyncs is called simultaneously

## [2.12.15] - 2022-11-23
### Fixed
- Add callback to ui.Treeview on item hover state changed

## [2.12.14] - 2022-11-11
### Fixed
- Removed experimental code from ui.Frame

## [2.12.13] - 2022-11-07
### Fixed
- Invalid assert on displaying large doubles

## [2.12.12] - 2022-10-25
### Added
- Overview page for omni.ui docs

## [2.12.11] - 2022-10-20
### Fixed
- Removed warning in `ui.VectorImageProvider`. Instead, it waits whaen the
  widget resolution is more than 0.

## [2.12.10] - 2022-10-11
### Fixed
- Memory leak in `ui.ImageWithProvider`

## [2.12.9] - 2022-10-03
### Fixed
- Fixed unexpected call of `mouse_released_fn`

## [2.12.8] - 2022-10-07
### Added
- Changed overflow warning to only report once

## [2.12.7] - 2022-10-06
### Fixed
- Size caching of MultiFloatField

## [2.12.6] - 2022-10-04
### Fixed
- Size caching of menu bar of MainWindow

## [2.12.5] - 2022-04-21
### Fixed
- `ui.Window.deferred_dock_in` prevented normal work of the layout

## [2.12.4] - 2022-09-30
### Fixed
- Reset size caching of Grid

## [2.12.3] - 2022-08-31
### Fixed
- mouse_wheel_fn is not called in a container widget like Frame
### Added
- Property elidedTextStr for Label, so that user can customize the elided_text_str instead of "..."

## [2.12.2] - 2022-09-30
### Fixed
- Reset size caching when visibility changes

## [2.12.1] - 2022-09-29
### Fixed
- Placer size caching

### Changed
## [2.12.0] - 2022-09-22
### Changed
- Aggressive caching of sizes of all the widgets
- Stack.send_mouse_events_to_back is true by default to make the behavior like
  in ImGui

## [2.11.5] - 2022-09-19
### Added
- `ui.Window.app_window` accessor.

## [2.1
### Added
- `ui.MainWindow` is able to hide all the windows with the property
  `ui.MainWindow.show_foreground`

## [2.11.3] - 2022-09-06
### Fixed
- Fix the workspace remove_window_visibility_changed_callback remove all the callback function at once.

## [2.11.2] - 2022-08-29
### Fixed
- Skip Placer draw if the child is 0-size

## [2.11.1] - 2022-08-02
### Fixed
- ui.MenuItem was disabled when changing visibility with delay

## [2.11.0] - 2022-08-23
### Added
- 'sendMouseEventsToBack' property to Stack widget
### Changed
- In Z-based stacks mouse events will go the front-most widget, unless 'sendMouseEventsToBack' is true.

## [2.10.9] - 2022-08-15
### Changed
- mouse_wheel_fn is not called if another window covers the widget
### Added
- Property to be able to scroll unfocused window.

## [2.10.8] - 2022-08-10
### Fixed
- Fixed TreeView's computed content height when root node is hidden.

## [2.10.7] - 2022-08-01
### Fixed
- Regenerate Menu when it's enabled.
- Make sure the menu is always on top.
- Middle click outside of the menu closes the menu
- Drag of menu bar doesn't produce detached menu

## [2.10.6] - 2022-07-28
### Added
- Add a interface to remove window's visibility changed callback function in omni.ui.Workspace.

## [2.10.5] - 2022-07-25
### Fixed
- Menu 2.0 in full screen mode
- User needs to drag the menu for 5 pixels for tearing off

## [2.10.4] - 2022-07-21
### Added
- Menu 2.0 title bar line

## [2.10.3] - 2022-07-19
### Fixed
- Drop down menu disappears when mousing between the gap

## [2.10.2] - 2022-07-18
### Added
- Add callback function in omni.ui.Workspace to notify the listener when any window's visibility changed.

## [2.10.1] - 2022-07-13
### Fixed
- Menu 2.0: SubMenu position

## [2.10.0] - 2022-07-07
### Added
- Precision property for FloatSlider, FloatDrag and FloatField.

## [2.9.12] - 2022-07-06
### Fixed
- ui.ImageWithProvider carsh when the style or image_url is not defined (OM-45414)

## [2.9.11] - 2022-06-21
### Added
- Ability to use clickable buttons in Menu 2.0

## [2.9.10] - 2022-06-15
### Fixed
- Padding of Slider and Field
### Added
- Support of border_color in ComboBox
- Support of fonts in TextEditor
### Changed
- No necessary to keep ImageProvider in python var anymore

## [2.9.9] - 2022-06-01
### Added
- Supports for fonts through the style "font"

## [2.9.8] - 2022-05-25
### Fixed
- Rounding of ui.FloatSlider

## [2.9.7] - 2022-05-12
### Fixed
- Crash when creating and destroying ui.Image

## [2.9.6] - 2022-05-02
### Removed
- Dependency on pip

## [2.9.5] - 2022-05-06
### Added
- Add style to change modal window dim background color

## [2.9.4] - 2022-05-02
### Added
- ui.Workspace API to inspect parent docking node id and docking node size:
  - get_parent_dock_id
  - get_dock_id_width
  - get_dock_id_height
  - set_dock_id_width
  - set_dock_id_height

## [2.9.3] - 2022-04-22
### Fixed
- Image blurring when it's placed to fractional position (like x=0.5, y=0.5)

## [2.9.2] - 2022-04-08
### Fixed
- Change the CanvasFrame zoom max from constant 10 to float max
- Make the CanvasFrame zoom near the zoom min and zoom max smooth

## [2.9.1] - 2022-04-06
### Fixed
- The workspace should hide the explicitly invisible windows even if the flag
keep_windows_open is set.

## [2.9.0] - 2022-04-06
### Fixed
- Message "Failed to acquire interface while unloading all plugins" related to
  Button, Image and ImageWithProvider

## [2.8.2] - 2022-04-05
### Added
- setZoomKeyShortcut api for ui.CanvasFrame to allow user to set alternative shortcut for graph zoom in adition to middle
  mouse scroll

## [2.8.1] - 2022-04-01
### Fixed
- Used `getAmendedProjection` to transform to/from NDC space.

## [2.8.0] - 2022-03-21
### Changed
- ui.CollapsableFrame marks both its header and body for rebuilding on a rebuild call

## [2.7.9] - 2022-02-22
### Changed
- Updated `capture_and_compare` with use_log parameter
- Updated `docked_test_window` for omni.kit.window compatibility

## [2.7.8] - 2022-03-25
### Fixed
- Compensate dpiScale for the menu bar

## [2.7.7] - 2022-03-24
### Fixed
- Fixed the "Hide Tab" window title menu item
- Polishing `ui.Menu`

## [2.7.5] - 2022-03-17
### Fixed
- Fixed `/app/window/hideUi` mode when only viewport is visible

## [2.7.4] - 2022-03-14
### Fixed
- Checking ImGui visibility when creating new window

## [2.7.3] - 2022-03-10
### Fixed
- Fixed the size of `ui.ToolBar`. Before it was always 600x400 and it's the
  reason why the saves workspace proportions were wrong. So the workspace
  proportions are fixed.
- Fixed the visibility of windows in `ui.Workspace.restore_workspace`.

## [2.7.2] - 2022-03-08
### Fixed
- Treeview column reorder issue of wrong column width

## [2.7.1] - 2022-02-18
### Fixed
- OM-36695: Drag and drop of multiple items
- OM-43762: Freezing of ui.FreeBezierCurve when end_tangent_height is extreamly big
- "Move to External Window" menu should only appear when clicking the title

## [2.7.0] - 2022-02-18
### Added
- ui.CanvasFrame.set_pan_x_changed_fn for tracking how user navigates
- ui.MenuItemCollection that behaves like a radio box
- Property ui.Widget.tooltip so it's possible to query it
- Ability to create right-aligned horizontal menu

## Fixed
- The menu automatically updates when changing the `checked` property
- Horizontal ui.Menu doesn't open windows on hover
- ui.MenuHelper checks if the user clicked in another window

## [2.6.1] - 2022-02-14
### Fixed
- OM-44806: `ui.Widget.checked_changed_fn`

## [2.6.0] - 2022-02-02
### Changed
- Full refactor of ui.Menu. Fully compatible with the old menu.

## [2.5.19] - 2022-01-28
### Changed
- set TreeView header's height and width to 0 instead of computedHeight and computedWidth

## [2.5.18] - 2022-01-26
### Added
- Arg in `Workspace.restore_workspace` to keep the windows open

## [2.5.17] - 2022-01-19
### Changed
- Fix issue for OM-40734: once TreeView is scrolled, the header is not clickable

## [2.5.16] - 2022-01-19
### Changed
- Delay tooltip when hovering is larger than 0.5 second

## [2.5.15] - 2022-01-18
### Added
- Add scroll_x_max and scroll_y_max for ScrollingFrame

## [2.5.14] - 2022-01-11
### Changed
- The way to add a shade to named color:
  `cl.test_named_shade_append = cl.shade(cl("#000000"), red=cl("#FF0000"))`
  `cl.test_named_shade_append.add_shade(blue=cl("#0000FF"))`

## [2.5.12] - 2022-01-07
### Changed
- Override previously submitted tooltip (only one tooltip is allowed)

## [2.5.11] - 2022-01-06
### Changed
- `cl.shade` appends palette to existing shade

## [2.5.10] - 2021-12-16
### Fixed
- Crash when specifying `columns_resizable=True` on a treeview but forgetting to set `column_widths`

## [2.5.9] - 2021-12-13
### Added
- ImageWithProvider.prepare_draw to force the image loading

## [2.5.8] - 2021-12-09
### Added
- The ability to move ui.Window to the virtual OS window. See
  `ui.Window.move_to_app_window`

## [2.5.7] - 2021-12-08
### Added
- Warning message when restoring the layout of tab bar of the window that
doesn't exist

## [2.5.6] - 2021-12-02
### Fixed
- Crash when ui.Image attempts loading a broken svg the second time

## [2.5.5] - 2021-11-17
### Added
- ui.Separator supports title parameter for fancy menu headers

## [2.5.4] - 2021-11-06
### Fixed
- Crash ui.TreeView when getting children right after constructor

## [2.5.3] - 2021-11-02
### Added
- ui.Menu.shown is a property that is True if the menu is shown on the screen
- Static ui.Menu.get_current() that returns currently shown menu
- ui.Inspector can get children of ui.TreeView, ui.Grid and ui.Frame
- The ability to use FontHelper with non-widgets

## [2.5.2] - 2021-09-20
### Added
- Added missing `text` binding to omni.ui.Menu

## [2.5.1] - 2021-09-07
### Added
- The ability to add third-party modules to namespace omni.ui

## [2.5.0] - 2021-08-17
### Fixed
- TreeView crash when AbstractItem is removed in Python

## [2.4.0] - 2021-07-22
### Added
- OffsetLine draws the line stuck to the bounds of other widgets

## [2.3.2] - 2021-06-21
### Fixed
- [OM-29853] Fixed crash in WindowHandle::isSelectedInDock

## [2.3.1] - 2021-06-15
### Changed
- When `dock_tab_bar_visible` is false, tab bar has a triangle and doesn't
  have tabs
### Added
- Added a menu that sets `dock_tab_bar_visible` for a tab if it's a single
  tab in tab bar
- Added `dock_tab_bar_enabled` to disable tab bar completely
- Serialization of `dock_tab_bar_visible` and `dock_tab_bar_enabled` in quick
  layout

## [2.3.0] - 2021-06-04
### Added
- The ability to use style shades for floats and URLs in style properties

## [2.2.0] - 2021-05-31
### Added
- `ui.Widget.set_computed_content_size_changed_fn` will be called when the
  computed size of the widget is changed.

## [2.1.8] - 2021-05-14
### Fixed
- Tooltip on ui.Line
- ui.StringField size in ui.CanvasFrame

## [2.1.7] - 2021-05-11
### Added
- Added WINDOW_FLAGS_NO_SCROLL_WITH_MOUSE that locks scroll
### Fixed
- Fixed pan over a backdrop in Material Editor

## [2.1.6] - 2021-05-07
### Fixed
- Don't block hovering state when popup window is on the screen

## [2.1.5] - 2021-04-08
### Fixed
- position_x/position_y of undocked window
### Changed
- Those methods are not abstract anymore:
  a. AbstractItemDelegate::buildBranch
  b. AbstractItemDelegate::buildHeader
  c. AbstractItemModel::appendChildItem
  d. AbstractItemModel::removeItem

## [2.1.4] - 2021-04-06
### Added
- ui.Widget.FLAG_WANT_CAPTURE_KEYBOARD: The flag passed to `key_pressed`
  callback that indicated omni.ui is using the keyboard input exclusively

## [2.1.3] - 2021-03-18
## Added
- Default style can be applied to `omni.ui.style.default`
- CSS color names
- Named colors
- Shades

## [2.1.2] - 2021-02-17
### Added
- Added docked_test_window function to OmniUiTest

## [2.1.1] - 2021-02-08
### Added
- ui.Workspace.set_show_window_fn
- ui.Workspace.show_window

## [2.1.0] - 2021-01-12
### Changed
- Documentation
- Shapes API to have free and non-free widgets. `Shape` is abstract class, all
  the derived classes should implement `_drawShape`.

### Added
- Widget.style property
- FreeLine, FreeRectangle, FreeCircle, FreeTriangle

## [2.0.1] - 2020-11-16
### Added
- Started changelog
- Keyboard callback for `ui.Window`
- Ability to grab the keyboard for the exclusive use of `ui.Window`
