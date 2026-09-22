(changelog_omni_graph_ui_nodes)=

# Changelog

This document records all notable changes to the **omni.graph.ui_nodes** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [1.50.5] - 2025-04-25
### Changed
- Use omni.kit.property.usd.AllowedTokenItem instead of or as base of custom AllowedTokenItem classes.

## [1.50.4] - 2025-02-20
### Changed
- Replaced omni.kit.window.viewport with omni.kit.viewport window in test dependencies.

## [1.50.3] - 2025-02-06
### Changed
- linux toolchain compatibility upgrade

## [1.50.2] - 2024-12-16
### Changed
- Remove test dependencies which are already included.

## [1.50.1] - 2024-12-16
### Changed
- Wait for stage streaming to complete before simulating picking events.

## [1.50.0] - 2024-11-18
### Changed
- Jumping versions for 107 to leave room for changes to 106.*-based builds.

## [1.41.0] - 2024-11-15
### Changed
- Build with Kit 107.0 with USD 24.05 and python 3.11

## [1.40.1] - 2024-12-09
### Changed
- Remove unnecessary dependency on IOmniHydra.

## [1.40.0] - 2024-09-19
### Changed
- bumping version to make room for 106.2-based extensions

## [1.30.0] - 2024-08-09
### Changed
- bumping version to make room for 106-based extensions

## [1.26.0] - 2024-07-31
### Changed
- C++ includes for carb::dictionary.

## [1.25.2] - 2024-06-06
### Fixed
- Property Window build functions which were not returning their value models.

## [1.25.1] - 2024-05-30
### Changed
- Updated the formatting

## [1.25.0] - 2024-05-17
### Added
- Update the 'support_level' entry in the configuration files to match the release requirements

## [1.24.2] - 2024-05-10
### Changed
- Replace deprecated function usages

## [1.24.1] - 2024-04-17
### Added
- Add a 'support_level' entry to the configuration file of the extensions

## [1.24.0] - 2024-04-10
### Changed
- Bumped dependency on omni.graph to version 1.139.0
- Bumped dependency on omni.graph.core to version 2.177.1
- Bumped dependency on omni.graph.tools to version 1.77.0

## [1.23.0] - 2024-04-08
### Removed
- DrawDebugCurve node.

## [1.22.1] - 2024-04-08
### Changed
- Replaced omni.ui_query calls with equivalent code in UINodeCommon.py
### Removed
- Dependency on omni.ui_query.

## [1.22.0] - 2024-03-18
### Changed
- Bumped dependency on omni.graph.core to version 2.176.3
- Bumped dependency on omni.graph to version 1.138.1

## [1.21.0] - 2024-02-15
### Changed
- Bumped dependency on omni.graph.core to version 2.174.2
- Bumped dependency on omni.graph.tools to version 1.76.1

## [1.20.1] - 2024-02-07
### Changed
- Fix for CameraTarget nodes

## [1.20.0] - 2024-02-05
### Changed
- Bumped dependency on omni.graph to version 1.138.0
- Bumped dependency on omni.graph.core to version 2.174.0
- Bumped dependency on omni.graph.tools to version 1.76.0

## [1.19.1] - 2024-02-03
### Changed
- Bumped minimum omni.graph.core extension version dependency to be compatible with changes to the INodeType interface and lazy graph executor.

## [1.19.0] - 2024-01-31
### Changed
- Bumped dependency on omni.graph to version 1.137.0
- Bumped dependency on omni.graph.core to version 2.171.1
- Bumped dependency on omni.graph.tools to version 1.76.0

## [1.18.0] - 2024-01-30
### Changed
- Bumped dependency on omni.graph to version 1.136.1
- Bumped dependency on omni.graph.core to version 2.170.1
- Bumped dependency on omni.graph.tools to version 1.74.0

## [1.17.0] - 2024-01-23
### Changed
- Bumped dependency on omni.graph to version 1.136.0

## [1.16.1] - 2024-01-22
### Fixed
- Made execution attribute descriptions consistent and informative

## [1.16.0] - 2024-01-18
### Changed
- Bumped dependency on omni.graph.core to version 2.169.1
- Bumped dependency on omni.graph to version 1.135.1
- Bumped dependency on omni.graph.tools to version 1.73.0

## [1.15.1] - 2024-01-13
### Fixed
- Repository URL in config file.

## [1.15.0] - 2024-01-12
### Changed
- Bumped dependency on omni.graph to version 1.134.7
- Bumped dependency on omni.graph.core to version 2.169.0
- Bumped dependency on omni.graph.tools to version 1.70.0

## [1.14.1] - 2024-01-04
### Added
- More tests of Python code.

## [1.14.0] - 2023-12-28
### Changed
- Bumped dependency on omni.graph.tools to version 1.69.0

## [1.13.0] - 2023-12-28
### Changed
- Bumped dependency on omni.graph.core to version 2.167.0
- Bumped dependency on omni.graph to version 1.134.2
- Bumped dependency on omni.graph.tools to version 1.68.0

## [1.12.0] - 2023-12-21
### Removed
- ComboBox, Placer, ReadWidgetProperty, ReadWindowSize, Spacer, VStack (aka Stack), WriteWidgetProperty and WriteWidgetStyle nodes.
### Changed
- Set the Button, Slider, OnWidgetClicked and OnWidgetValueChanged to be hidden in the UI.

## [1.11.0] - 2023-12-18
### Changed
- Bumped dependency on omni.graph.core to version 2.166.0
- Bumped dependency on omni.graph to version 1.134.0
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.10.1] - 2023-12-14
### Changed
- disable test_on_picked when FSD is enabled

## [1.10.0] - 2023-12-12
### Changed
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph to version 1.133.2
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.9.0] - 2023-12-11
### Changed
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph to version 1.133.2
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.8.0] - 2023-12-07
### Changed
- OM-77263 OM-105672 Use rtx viewport as picking doesn't work with pxr one and re-enable viewport tests

## [1.7.2] - 2023-11-30
### Changed
- Set the minimal omni.graph.core version required in order to properly load that extension

## [1.7.1] - 2023-11-28
### Changed
- Changed deprecated internal state functions to their new version

## [1.7.0] - 2023-10-26
### Changed
- Moved tests to omni.graph.ui

## [1.6.7] - 2023-10-19
### Changed
- Added tests for token array widget

## [1.6.6] - 2023-10-17
### Changed
- Added tests for node widgets

## [1.6.5] - 2023-10-04
### Changed
- Fix test images

## [1.6.4] - 2023-09-12
### Changed
- Updating tests for new target nodes

## [1.6.3] - 2023-09-08
### Changed
- Updated tests

## [1.6.2] - 2023-08-18
### Changed
- fix spelling

## [1.6.1] - 2023-08-16
### Changed
- Re-enable ui_nodes tests

## [1.6.0] - 2023-08-14
### Changed
- Ported over tests from Kit that make extensions require unnecessary dependencies on omni.graph.nodes

## [1.5.15] - 2023-08-11
### Changed
- Fixes some tests and skips others, to be able to focus on drag and drop crash

## [1.5.14] - 2023-08-11
### Fixed
- Fixed some ui_nodes tests so they can run again
- Set some of the broken tests to skip for now

## [1.5.13] - 2023-08-11
### Fixed
- Version bump to force extension publication to fix Linux platform errors

## [1.5.12] - 2023-08-09
### Fixed
- Linux build errors

## [1.5.11] - 2023-08-04
### Changed
- Bumped up the test timeout to prevent Linux flaky failures

## [1.5.10] - 2023-08-03
### Changed
- Targeted a specific version of the Kit SDK

## [1.5.9] - 2023-07-31
### Changed
- Standardized the format of the CHANGELOG

## [1.5.8] - 2023-07-27
### Added
- UI Nodes test migrated from Kit

## [1.5.7] - 2023-07-26
### Changed
- Migrated the extension from Kit

## [1.5.6] - 2023-07-13
### Removed
- Unnecessary dependency on omni.graph.test

## [1.5.5] - 2023-06-27
### Fixed
- Refactored OmniGraph documentation to point to locally generated files
### Added
- Example pre and post documentation additions

## [1.5.4] - 2023-06-27
### Changed
- OgnSetViewportMode imports OgnVStack by absolute path
- Set up the extension to load python tests in parallel

## [1.5.3] - 2023-06-12
### Changed
- Hide the ComboBox and Slider nodes in the node catalog.
- Give a warning if ComboBox or Slider are used.

## [1.5.2] - 2023-06-02
### Changed
- Added 'passClicksThru' input to SetViewportMode node.

## [1.5.1] - 2023-05-31
### Fixed
- Adjusted the CRLF settings for the generated .md node table of content files

## [1.5.0] - 2023-05-29
### Added
- Regenerated node table of contents

## [1.4.0] - 2023-05-15
### Added
- Added `OgnLockViewportRender` for locking and unlocking viewport render
### Fixed
- Enabled output execution attributes of `OgnSetViewportFullscreen`, `OgnSetViewportRenderer` and `OgnSetViewportResolution` when triggered

## [1.3.3] - 2023-04-21
### Changed
- Updated OnPicked and ReadPickState nodes to properly use targets
- Moved templates so they would properly work

## [1.3.2] - 2023-04-12
### Fixed
- Re-enabled tests

## [1.3.1] - 2023-04-11
### Added
- Table of documentation links for nodes in the extension

## [1.3.0] - 2023-03-29
### Added
- Updated tests for target output type change to relationship

## [1.2.0] - 2023-03-29
### Added
- Property panel support for allowMultiInput tags on target types

## [1.1.0] - 2023-03-28
### Added
- Target ports added to GetActiveViewportCamera and OnPicked nodes

## [1.0.2] - 2023-03-27
### Fixed
- Error in ReadViewportDragState, ReadViewportHoverState

## [1.0.1] - 2023-03-12
### Fixed
- bug in ReadViewportPressState

## [1.0.0] - 2023-03-06
### Initial Version
- Moved nodes out of omni.graph.ui
