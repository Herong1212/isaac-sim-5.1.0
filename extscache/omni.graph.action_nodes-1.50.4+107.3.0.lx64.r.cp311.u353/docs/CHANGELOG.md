(changelog_omni_graph_action_nodes)=

# Changelog

This document records all notable changes to the **omni.graph.action_nodes** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.50.4] - 2025-04-25
### Changed
- Use omni.kit.property.usd.AllowedTokenItem instead of or as base of custom AllowedTokenItem classes.

## [1.50.3] - 2025-02-11
### Changed
- OgnOnVariableChange is now caching the variable accessor to improve perf

## [1.50.2] - 2025-02-06
### Changed
- linux toolchain compatibility upgrade

## [1.50.1] - 2024-12-16
### Changed
- Remove test dependencies which are already included.

## [1.50.0] - 2024-11-18
### Changed
- Jumping versions for 107 to leave room for changes to 106.*-based builds.

## [1.41.0] - 2024-11-15
### Changed
- Build with Kit 107.0 with USD 24.05 and python 3.11

## [1.40.1] - 2024-12-12
### Changed
- Support different keyboard layouts for graph node 'On Keyboard Input' with carb.windowing.translate_key

## [1.40.0] - 2024-09-19
### Changed
- bumping version to make room for 106.2-based extensions

## [1.30.0] - 2024-08-09
### Changed
- bumping version to make room for 106-based extensions

## [1.24.0] - 2024-07-31
### Changed
- C++ includes for carb::dictionary; pathing for USD headers and libs.

## [1.23.2] - 2024-06-06
### Fixed
- Property Window build functions which were not returning their value models.

## [1.23.1] - 2024-05-30
### Changed
- Updated the formatting

## [1.23.0] - 2024-05-17
### Added
- Update the 'support_level' entry in the configuration files to match the release requirements

## [1.22.3] - 2024-05-10
### Changed
- Replace deprecated function usages

## [1.22.2] - 2024-04-17
### Added
- Add a 'support_level' entry to the configuration file of the extensions

## [1.22.1] - 2024-04-10
### Changed
- Fix for onkeyboardinput test

## [1.22.0] - 2024-04-10
### Changed
- Bumped dependency on omni.graph to version 1.139.0
- Bumped dependency on omni.graph.core to version 2.177.1
- Bumped dependency on omni.graph.tools to version 1.77.0

## [1.21.1] - 2024-04-08
### Changed
- Removed dependency on stage_templates and pipapi.

## [1.21.0] - 2024-03-18
### Changed
- Bumped dependency on omni.graph.core to version 2.176.3
- Bumped dependency on omni.graph to version 1.138.1

## [1.20.1] - 2024-02-22
### Changed
- Turn off hotkeys in with_window test

## [1.20.0] - 2024-02-15
### Fixed
- Filtered out a known test failure
### Changed
- Bumped dependency on omni.graph.core to version 2.174.2
- Bumped dependency on omni.graph.tools to version 1.76.1

## [1.19.1] - 2024-02-13
### Changed
- Replace fabric::kInvalidTime with the newer name, fabric::kInvalidRationalTime.

## [1.19.0] - 2024-02-05
### Changed
- Bumped dependency on omni.graph to version 1.138.0
- Bumped dependency on omni.graph.core to version 2.174.0
- Bumped dependency on omni.graph.tools to version 1.76.0

## [1.18.1] - 2024-02-03
### Changed
- Bumped minimum omni.graph.core extension version dependency to be compatible with changes to the INodeType interface and lazy graph executor.

## [1.18.0] - 2024-01-31
### Changed
- Bumped dependency on omni.graph to version 1.137.0
- Bumped dependency on omni.graph.core to version 2.171.1
- Bumped dependency on omni.graph.tools to version 1.76.0

## [1.17.0] - 2024-01-30
### Changed
- Bumped dependency on omni.graph to version 1.136.1
- Bumped dependency on omni.graph.core to version 2.170.1
- Bumped dependency on omni.graph.tools to version 1.74.0

## [1.16.1] - 2024-01-26
### Changed
- Fixed bug in OnMessageBusEvent where it would unexpectedly trigger after graph reset

## [1.16.0] - 2024-01-23
### Changed
- Bumped dependency on omni.graph to version 1.136.0

## [1.15.1] - 2024-01-22
### Fixed
- Made node type and attribute descriptions consistent and informative

## [1.15.0] - 2024-01-18
### Changed
- Bumped dependency on omni.graph.core to version 2.169.1
- Bumped dependency on omni.graph to version 1.135.1
- Bumped dependency on omni.graph.tools to version 1.73.0

## [1.14.1] - 2024-01-13
### Fixed
- Repository URL in config file.

## [1.14.0] - 2024-01-12
### Changed
- Bumped dependency on omni.graph to version 1.134.7
- Bumped dependency on omni.graph.core to version 2.169.0
- Bumped dependency on omni.graph.tools to version 1.70.0

## [1.13.1] - 2024-01-02
### Changed
- Add --no-window arg to tests

## [1.13.0] - 2023-12-28
### Changed
- Bumped dependency on omni.graph.tools to version 1.69.0

## [1.12.0] - 2023-12-28
### Changed
- Bumped dependency on omni.graph.core to version 2.167.0
- Bumped dependency on omni.graph to version 1.134.2
- Bumped dependency on omni.graph.tools to version 1.68.0

## [1.11.0] - 2023-12-18
### Removed
- Display of OnImpulseEvent's 'enableImpulse' attribute in the 'State' section of the Property Window.
### Added
- A 'Send Impulse' button to OnImpulseEvent's 'Inputs' section of the Property Window.

## [1.10.0] - 2023-12-18
### Changed
- Bumped dependency on omni.graph.core to version 2.166.0
- Bumped dependency on omni.graph to version 1.134.0
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.9.2] - 2023-12-18
### Changed
- Improve ForEach node error handling

## [1.9.1] - 2023-12-15
### Changed
- Minor change to improve code safety

## [1.9.0] - 2023-12-12
### Changed
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph to version 1.133.2
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.8.0] - 2023-12-11
### Changed
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph to version 1.133.2
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.7.2] - 2023-12-07
### Changed
- Fixed a bug related to string payload in SendMessageBusEvent

## [1.7.1] - 2023-12-06
### Changed
- Improve message bus node docs

## [1.7.0] - 2023-12-01
### Changed
- Add a test for attribute removal handling

## [1.6.5] - 2023-11-30
### Changed
- Set the minimal omni.graph.core version required in order to properly load that extension

## [1.6.4] - 2023-11-28
### Changed
- Changed deprecated internal state functions to their new version

## [1.6.3] - 2023-11-20
### Changed
- Use newer, stable INodeTypeForwarding2 ONI.

## [1.6.2] - 2023-11-09
### Changed
- Ran the formatter

## [1.6.1] - 2023-11-01
### Changed
- Convert SendMessageBusEvent to C++

## [1.5.1] - 2023-10-31
### Changed
- Built against kit-sdk version 132791

## [1.5.0] - 2023-10-26
### Changed
- Added c++ implementation for OnMessageBusEvent
### Added
- SendMessageBusEvent node

## [1.4.0] - 2023-10-05
### Changed
- Restore action nodes to .action from .action_nodes for forward-compatibility

## [1.3.5] - 2023-09-22
### Changed
- Fix crash related to OnGamepadInput

## [1.3.4] - 2023-09-07
### Changed
- replace VariableNameModel as VariableNameListModel

## [1.3.3] - 2023-09-07
### Changed
- OnStageEvent will react with 1 frame less relative to source event

## [1.3.2] - 2023-08-25
### Changed
- Fixed write to target flag

## [1.3.1] - 2023-08-24
### Changed
- Rename ApplicationExit to ExitApplication

## [1.3.0] - 2023-08-23
### Changed
- Add Application Exit node

## [1.2.1] - 2023-08-18
### Fixed
- Placement and delivery of icon and preview images

## [1.2.0] - 2023-08-18
### Changed
- migrate from kit repo

## [1.1.0] - 2023-08-17
### Changed
- Moved extension repo

## [1.0.0] - 2023-07-14
### Added
- Moved nodes from omni.graph.action
