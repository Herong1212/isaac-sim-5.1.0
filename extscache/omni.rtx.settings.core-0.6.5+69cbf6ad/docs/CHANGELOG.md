# CHANGELOG

This document records all notable changes to ``omni.rtx.settings.core`` extension.
This project adheres to `Semantic Versioning <https://semver.org/>`.

## [0.6.5] - 2025-03-12
### Added
- Added new settings for data window.

## [0.6.4] - 2025-03-06
### Fixed
- Fixed SettingsSearchableCombo handling of missing items.

## [0.6.3] - 2024-06-07
### Added
- Added 'Opacity Scaling' option in 'NVIDIA IndeX Compositing'.

## [0.6.2] - 2024-03-01
### Added
- Added an option to enable RTPT (Experimental)

## [0.6.1] - 2024-01-17
### Added
- Added RTPT (Experimental) renderer settings
### Removed
- Removed GI denoiser settings from UI now that DLSS RR is non-optional

## [0.6.0] - 2023-11-06
### Changed
- Handle possibility of no GPUs better when building UI

## [0.5.11] - 2023-07-31
### Changed
- "Total Samples per Pixel" is now 0-100,000

## [0.5.10] - 2022-11-22
### Changed
- Renamed all Debug Views that are intended to be RT-specific with RT prefix.
- Moved RT and PT MGPU settings frames to the bottom to be consistent with one another.

## [0.5.9] - 2022-11-17
### Changed
- For photosentivity/seizure concerns, included [WARNING: Flashing Colors] to Debug View names known to flash.

## [0.5.8] - 2022-10-26
### Added
- Added tooltips for all render settings.
- Added BVH Splits settings to 'Common/Geometry/Curves Settings'.
- Added Heat Map views to 'Common/Debug View'.
- Added an 'Invisible Lights Roughness Threshold' setting to 'Common/Lighting'.
- Added 'Frame Generation' setting to 'Real-Time/NVIDIA DLSS'.
- Added 'New Denoiser (experimental)' setting to 'Real-Time/Direct Lighting'.
- Added 'Multi Matte' settings in 'Interactive (Path Tracing)'.
- Added 'Adaptive Sampling' settings in 'Interactive (Path Tracing)/Path-Tracing'.

### Changed
- Refactored 'Lighting Mode' settings for Dome Lights in 'Common/Lighting'; now provides 'Image-Based Lighting' (simply a rename of the previous default) and 'Limited Image-Based Lighting'.
- Improved UI for setting-dependency clarity; settings which depend on others now tend to be indented under them, and hidden when the parent setting is not enabled.
- Improved PT AOV names for clarity.

## [0.5.7] - 2022-06-04
### Changed
- Make sure a stage is loaded to trigger RTX loading in Viewport.

## [0.5.6] - 2022-05-23
### Changed
- Add omni.hydra.rtx as test depenency

## [0.5.5] - 2022-03-11

### Changed
- Rename 'Path Traced' to 'Interactive (Path Tracing)'

## [0.5.4] - 2020-11-27

### Changed
- Update to use new RenderSettingsFactory entry point in rtx.window.settings

## [0.5.3] - 2020-11-25

### Changed

- Registration/Unregistration process
- Added Reset RTX settings button
- Added texture compression setting in common settings
- Updated to match current Render Settings 1.0
- make Enable/Disable of settings consistent


## [0.5.2] - 2020-11-18

### Changed
- Updated to match current Render Settings 1.0

## [0.5.1] - 2020-11-16

### Changed
- Shortened any labels that went over the new width (220)
## [0.5.0] - 2020-11-04

### Changed

- initial release
