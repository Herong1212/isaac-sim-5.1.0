# Changelog

This document records all notable changes to the **omni.kit.viewport.menubar.display** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [107.0.3] - 2024-07-09
### Changed
- Remove "Skeletons" from Show By Type" by default
- Refresh "Show By Type" when exclude list changed at runtime

## [107.0.2] - 2024-06-04
### Changed
- Updated documentation with AI agent.

## [107.0.1] - 2024-05-27
### Changed
OM-55821: Linting

## [107.0.0] - 2024-03-18
### Changed
- Move version to 107.0.0

## [106.0.0] - 2023-11-14
### Added
- OM-84741: Add new menu item for bounding box visibility

## [106.0.0] - 2023-11-14
### Added
- OMFP-3721: Ability to change memory-item labeling.

## [105.0.6] - 2023-10-24
### Added
- OMFP-2649: Adding settings flag that can be used to hide the audio item from the viewport display.

## [105.0.5] - 2023-09-26
### Added
- Add hotkey support to more menu items

## [105.0.4] - 2023-09-18
### Added
- Show hotkey text

## [105.0.3] - 2023-08-07
### Changed
- Use viewport actions for HUD menu item visibility toggling.

## [105.0.2] - 2023-02-03
### Changed
- Move grid, axis, and selection-hilight items to use actions for toggling.
### Fixed
- Show by type mixed-mode icon click wasn't triggering action.

## [105.0.1] - 2022-11-05
### Added
- Cherry-picked changes from v104.1.10 & 11 and merged with latest v105

## [105.0.0] - 2022-10-17
### Added
- Sart unwinding functionality based on displayOptions in favor of a simpler view on per-viewport settings.
- Pass triggered_fn to scene-level items to invoke omni.viewport.action.
### Removed
- Stage open handler which is managed by action now.

## [104.1.11] - 2022-10-26
### Added
- Can now set the root CategoryCollectionItem of SimpleModelCategory, needed for top level categories.
- Updated example in README.md

## [104.1.10] - 2022-10-22
### Added
- Optional new section separator for categories.
### Fixed
- Removed unnecessary separator for custom items if there are not state or collection items in a category menu.
- Checked state for category collection now correctly shows empty if there are only custom items.

## [104.1.9] - 2022-10-12
### Added
- Allow creation of new display menu root categories.

## [104.1.8] - 2022-09-26
### Added
- Display option for new fly-mode speed indicator.

## [104.1.7] - 2022-08-26
### Fixed
- Issue with some entries models begin synchrnoized to state after MenuItem created from it.

## [104.1.6] - 2022-08-10
### Changed
- Toggling show by type should not effect meshes

## [104.1.5] - 2022-08-05
### Changed
- Make Viewport visibility flags sticky on UsdPrims on subsequent opens.

## [104.1.4] - 2022-07-25
### Changed
- Make Viewport visibility flags sticky on UsdPrims on subsequent opens.

## [104.1.3] - 2022-07-16
### Changed
- OM-55152: Re-adjust viewport dashboard and icons for VP2

## [104.1.2] - 2022-07-08
### Fixed
- Do not hide SkelRoot from Skeleton display toggle.

## [104.1.1] - 2022-07-01
### Changed
- Make sub-menus not tearable by default.

## [104.1.0] - 2022-06-16
### Added
- Ability to add/remove custom display setting
- Multi-level for display categories

## [104.0.5] - 2022-06-05
### Changed
- Simplify test to use default Viewport and window size.
- Make failure of one test not cause failure of others.
- Don't create a new Viewport for every menu-item test.

## [104.0.4] - 2022-05-31
### Changed
- Visibilty of Skeleton and Mesh to work with instances if possible.
- Split visibility logic into separate test-able module.
- Make any usage of legacy displayOptions bitmask private and do not expose an API for it.
### Fixed
- Startup visibility for grid and selection.
- Make "Selection" item toggle "Selection Outline", not "Selection Box".
- Restoration of various show/hide items that should be persistent.
- Reset Show/Hide values/types that are scene/stage dependent to keep UI and render in Sync.

## [104.0.3] - 2022-05-04
### Changed
- Imported to kit repro and bump version to match Kit SDK

## [1.0.3] - 2022-03-28
### Added
- Setting for visible and Order

## [1.0.2] - 2022-03-16
### Fixed
- OM-46224: Fix camera manipulation lock out and legacy Camera frustum drawing.

## [1.0.1] - 2022-03-16
### Changed
- Move print to carb.log_info

## [1.0.0] - 2022-03-11
### Added
- Split from omni.kit.viewport.menubar
