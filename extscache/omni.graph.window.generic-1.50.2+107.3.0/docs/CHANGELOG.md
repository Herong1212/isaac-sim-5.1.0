(changelog_omni_graph_window_generic)=

# Changelog

This document records all notable changes to the **omni.graph.window.generic** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [1.50.2] - 2025-01-09
### Changed
- Update dependency versions

## [1.50.1] - 2024-12-16
### Changed
- Remove test dependencies which are already included.

## [1.50.0] - 2024-11-18
### Changed
- Jumping versions for 107 to leave room for changes to 106.*-based builds.

## [1.41.0] - 2024-11-15
### Changed
- Added public API doc

## [1.40.0] - 2024-09-19
### Changed
- bumping version to make room for 106.2-based extensions

## [1.30.0] - 2024-08-09
### Changed
- bumping version to make room for 106-based extensions

## [1.25.1] - 2024-07-19
### Changed
- OMPE-14122: Removed featured flag

## [1.25.0] - 2024-05-17
### Added
- Update the 'support_level' entry in the configuration files to match the release requirements

## [1.24.1] - 2024-04-17
### Added
- Add a 'support_level' entry to the configuration file of the extensions

## [1.24.0] - 2024-04-10
### Changed
- Bumped dependency on omni.graph to version 1.139.0
- Bumped dependency on omni.graph.core to version 2.177.1
- Bumped dependency on omni.graph.tools to version 1.77.0

## [1.23.1] - 2024-03-20
### Fixed
- Removed obsolete import

## [1.23.0] - 2024-03-18
### Changed
- Bumped dependency on omni.graph.core to version 2.176.3
- Bumped dependency on omni.graph to version 1.138.1

## [1.22.0] - 2024-02-15
### Changed
- Bumped dependency on omni.graph.core to version 2.174.2
- Bumped dependency on omni.graph.tools to version 1.76.1

## [1.21.0] - 2024-02-05
### Changed
- Bumped dependency on omni.graph to version 1.138.0
- Bumped dependency on omni.graph.core to version 2.174.0
- Bumped dependency on omni.graph.tools to version 1.76.0

## [1.20.0] - 2024-01-31
### Changed
- Bumped dependency on omni.graph to version 1.137.0
- Bumped dependency on omni.graph.core to version 2.171.1
- Bumped dependency on omni.graph.tools to version 1.76.0

## [1.19.0] - 2024-01-30
### Changed
- Bumped dependency on omni.graph to version 1.136.1
- Bumped dependency on omni.graph.core to version 2.170.1
- Bumped dependency on omni.graph.tools to version 1.74.0

## [1.18.0] - 2024-01-23
### Changed
- Bumped dependency on omni.graph to version 1.136.0

## [1.17.0] - 2024-01-18
### Changed
- Bumped dependency on omni.graph.core to version 2.169.1
- Bumped dependency on omni.graph to version 1.135.1
- Bumped dependency on omni.graph.tools to version 1.73.0

## [1.16.1] - 2024-01-13
### Fixed
- Repository URL in config file.

## [1.16.0] - 2024-01-12
### Changed
- Bumped dependency on omni.graph to version 1.134.7
- Bumped dependency on omni.graph.core to version 2.169.0
- Bumped dependency on omni.graph.tools to version 1.70.0

## [1.15.2] - 2024-01-04
### Changed
- Updated golden image tests to be less affected by changes to the node catalog.
### Removed
- Kit 104-specific image tests.

## [1.15.1] - 2024-01-03
### Changed
- Adds toast warning when pasting node with variables that does not exist in the current graph. And ignore nodes that are incompatible

## [1.15.0] - 2023-12-28
### Changed
- Bumped dependency on omni.graph.tools to version 1.69.0

## [1.14.0] - 2023-12-28
### Changed
- Bumped dependency on omni.graph.core to version 2.167.0
- Bumped dependency on omni.graph to version 1.134.2
- Bumped dependency on omni.graph.tools to version 1.68.0

## [1.13.0] - 2023-12-18
### Changed
- Bumped dependency on omni.graph.core to version 2.166.0
- Bumped dependency on omni.graph to version 1.134.0
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.12.0] - 2023-12-12
### Changed
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph to version 1.133.2
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.11.0] - 2023-12-11
### Changed
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph to version 1.133.2
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.10.1] - 2023-07-31
### Changed
- Standardized the format of the CHANGELOG

## [1.10.0] - 2023-07-22
### Added
- Main documentation page

## [1.9.1] - 2023-07-20
### Changed
- Bumping the version so that debug versions of extensions will publish

## [1.9.0] - 2023-07-19
### Removed
- Obsolete test dependency on omni.graph.test

## [1.8.2] - 2023-07-18
### Fixed
- Lint errors caused by formatter

## [1.8.1] - 2023-07-17
### Fixed
- Format and linting on tests

## [1.8.0] - 2023-07-10
### Changed
- Migrated this extension from kit-graphs to the kit-omnigraph repo. The kit-graphs repo will continue to be
  used for Kit 105.0-based releases.

## [1.7.0] - 2023-06-22
### Changed
- Nodes created from the QuickSearch window by clicking on an item or pressing ENTER will now be created at the
  position the mouse was at when QuickSearch was invoked.
### Fixed
- Clicking on a node type in the QuickSearch window will reliably create the node.

## [1.6.2] - 2023-06-14
### Changed
- Updated golden image

## [1.6.1] - 2023-06-05
### Changed
- Replaced deprecrated omni.graph.core.MetadataKeys references with omni.graph.tools.ogn.MetadataKeys

## [1.6.0] - 2023-05-09
### Added
- Ability to double-click and enter compounds

## [1.5.2] - 2023-05-04
### Changed
- Disabled node rasterization in tests.

## [1.5.1] - 2023-04-11
### Fixed
- Updated the test golden images to match kit 105.1

## [1.5.0] - 2023-03-31
### Added
- Added filter_fn to Generic Graph, to specify valid prims to paste into the graph.

## [1.4.0] - 2023-03-07
### Added
- Action and hotkey support.

## [1.3.17] - 2023-02-09
### Changed
- Use fastShutdown on tests to avoid problems in Kit 104.2 which have been fixed in 105.

## [1.3.16] - 2023-02-02
### Changed
- Add additional dependencies
- Add dependency to omni.kit.ui_test for tests
- Added hack to tests which passes a function to the OmniGraphWindow constructur to fix a Pybind11 issue OM-79384.
   Note: this change should be reverted when that issue is solved.

## [1.3.15] - 2023-01-26
### Changed
- Disabled (in Linux ETM only) all tests which fail with 'invalid self' error.

## [1.3.14] - 2023-01-19
### Fixed
- Generic Graph window once again opens as soon as it is created, or shown for the first time.

## [1.3.13] - 2023-01-11
### Fixed
- The Generic Graph window now toggles correctly in the Window -> Visual Scripting menu and selecting the
  menu item while it is checked will cause the window to close.

## [1.3.12] - 2023-01-09
### Changed
- Ensure outstanding futures are cancelled on object destruction.

## [1.3.11] - 2022-12-07
### Fixed
- The window turns to black when it is closed when it's moved to become an external window

## [1.3.10] - 2022-08-28
- Added omni.graph.tutorials as test dependency

## [1.3.9] - 2022-08-22
### Changed
- Renamed test golden image to be unique among all extensions.

## [1.3.8] - 2022-03-30
### Changed
update repo_build and repo-licensing

## [1.3.7] - 2022-03-29
### Added
- UI testing framework.

## [1.3.6] - 2022-03-17
### Added
- The lifetime of _Create\\Visual Sciprting\\Push Graph_, _Create\\Visual Sciprting\\Lazy Graph_ menu items is now controlled by this extension
- After opening a graph, the correspnding graph editor window will become focused

## [1.3.5] - 2022-03-02
### Added
- Stage widget can open non-action graphs in generic editor

## [1.3.4] - 2022-02-23
### Changed
- skip the popup question if user clicks on the Create Graph button on toolbar

## [1.3.3] - 2022-02-22
### Change
- create OmniGraphNodeQuickSearchModel in the extension instead from the core

## [1.3.2] - 2022-02-16
### Changed
- Window is now located at Window/Visual Scripting/Generic Graph
- Renamed window to Generic Graph

## [1.3.1] - 2022-02-21
### Added
- register quick search with Omni Graph Generic nodes

## [1.3.0] - 2022-02-01
- Bump dependency on omni.graph.core

## [1.2.0] - 2022-01-31

### Changed
- Added no-op model override and cleanup
- Temporarily tie Prim culling to the drag-drop setting
- Workaround for Create 2022.1.0-beta8

## [1.1.0] - 2022-01-28

### Changed
- Window is now located at Window/OmniGraph/OmniGraph Generic
### Fixed
- Destroy window when extension is unloaded

## [1.0.0] - 2022-01-26
### Added
- Initial commit - add new window type
