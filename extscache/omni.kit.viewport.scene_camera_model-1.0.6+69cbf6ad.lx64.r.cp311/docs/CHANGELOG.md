# Changelog

## [1.0.6] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [1.0.5] - 2024-08-20
- Warn if external settings aren't enabled
- Avoid rebuilding subscriptions unless necessary

## [1.0.4] - 2024-05-15
- Setting name for single-camera-model to conform to proper /exts/ namespace and enable with extension

## [1.0.3] - 2023-10-16
- Support for DLSS-G subframes. SceneCameraModel now manages and tracks
  subframes throughout the rendering process for more accurate and visually
  consistent results.

## [1.0.2] - 2023-10-13
- Internal changes to shape API back to one that can handle projection.

## [1.0.1] - 2023-10-10
- Introduced `eHydraEngineFramesAdded` event for early notification of frames entering the rendering pipeline.
- Added `m_frameViewMatrixQueue` to better track and handle in-flight frames.
- Updated the `_onRenderFrameComplete` and `_onRenderFrameAdded` methods handling based on `m_frameViewMatrixQueue`.

## [1.0.0] - 2023-09-28
- Initial release
