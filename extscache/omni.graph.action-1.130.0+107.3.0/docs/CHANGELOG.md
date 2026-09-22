(changelog_omni_graph_action)=

# Changelog

This document records all notable changes to the **omni.graph.action** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.130.0] - 2024-11-18
### Changed
- Jumping versions for 107 to leave room for changes to 106.*-based builds.

## [1.121.0] - 2024-11-15
### Changed
- Added public API doc

## [1.120.0] - 2024-09-19
### Changed
- bumping version to make room for 106.2-based extensions

## [1.110.0] - 2024-08-09
### Changed
- bumping version to make room for 106-based extensions

## [1.101.1] - 2024-05-30
### Changed
- Updated the formatting

## [1.101.0] - 2024-05-17
### Added
- Update the 'support_level' entry in the configuration files to match the release requirements

## [1.100.3] - 2024-04-17
### Added
- Add a 'support_level' entry to the configuration file of the extensions

## [1.100.2] - 2024-01-13
### Fixed
- Repository URL in config file.

## [1.100.1] - 2024-01-03
### Added
- Terms that should rightly come from Kit, temporarily

## [1.100.0] - 2023-12-15
### Changed
- Manually bumped the version number to be higher than the one in the 105.1 and 105.2 branch so that it takes priority

## [1.54.3] - 2023-12-15
### Changed
- Add python coverage to omni.graph.action

## [1.54.2] - 2023-08-25
### Changed
- Fixed write to target flag

## [1.54.1] - 2023-08-18
### Fixed
- Placement and delivery of icon and preview images

## [1.54.0] - 2023-08-18
### Changed
- migrate from kit repo

## [1.53.0] - 2023-08-17
### Changed
- Moved extension repo

## [1.52.0] - 2023-08-14
### Changed
- Move nodes out of extension into omni.graph.action_nodes, move ABI into omni.graph.action_core

## [1.51.0] - 2023-07-27
### Changed
- Added reset pin to MultiGate

## [1.50.2] - 2023-07-21
### Changed
- Renamed Node::createForDef references to Node::create.

## [1.50.1] - 2023-07-14
### Fixed
- bug with compute-on-request nodes in subgraphs

## [1.50.0] - 2023-07-12
### Changed
- Removed omni.kit.async_engine dependency

## [1.49.0] - 2023-07-07
### Changed
- Latent chains of nodes will now be interrupted when their event node triggers.
- Can be disabled with /ext/omni.graph.action/disableInterrupts

## [1.48.5] - 2023-06-30
### Fixed
- Crash when script node triggers a stage resync

## [1.48.4] - 2023-06-28
### Fixed
- Bug in how pre/post execute is called for AG container graph

## [1.48.3] - 2023-06-28
### Changed
- Use ISchedulingHints2 interface when checking for node purity status.

## [1.48.2] - 2023-06-27
### Fixed
- Refactored OmniGraph documentation to point to locally generated files

## [1.48.1] - 2023-06-27
### Changed
- Set up the extension to load python nodes and tests in parallel

## [1.48.0] - 2023-06-27
### Changed
- Islands of nodes are moved into independent graphs so they can be executed in parallel. Can be disabled with /ext/omni.graph.action/disableArchipelago

## [1.47.3] - 2023-06-22
### Changed
- Ignore constant nodes when construct Action Graph backend execution graph topology.
- Modified unit test to account for fact that constant nodes will not be computed in Action Graphs.

## [1.47.2] - 2023-06-12
### Fixed
- Fix for instanced action graphs

## [1.47.1] - 2023-06-08
### Fixed
- test instability

## [1.47.0] - 2023-06-06
### Changed
- Subgraphs are now flattened for IR

## [1.46.0] - 2023-06-02
### Changed
- Converted nodes to use IActionGraph API

## [1.45.2] - 2023-05-31
### Fixed
- Support for partitioning of AG IR
- Added DependencyFoldPass test partitioner

## [1.45.1] - 2023-05-31
### Fixed
- Adjusted the CRLF settings for the generated .md node table of content files

## [1.45.0] - 2023-05-29
### Added
- Regenerated node table of contents

## [1.44.2] - 2023-05-15
### Removed
- Removed old subgraph unit test.

## [1.44.1] - 2023-05-08
### Fixed
- Bug with Python code generator for BundleContents

## [1.44.0] - 2023-04-21
### Fixed
- OnObjectChanged with graph instancing
### Added
- name input to OnObjectChanged

## [1.43.3] - 2023-04-20
### Changed
- Improved IActionGraph error handling

## [1.43.2] - 2023-04-12
### Changed
- Updated SetPrimActive ui

## [1.43.1] - 2023-04-11
### Added
- Links to C++ and Python ABI documentation
- Table of documentation links for nodes in the extension

## [1.43.0] - 2023-04-05
### Added
- IActionGraph::getExecutionEnabled

## [1.42.0] - 2023-03-28
### Fixed
- Add target input to nodes that have a prim path input and prefer this to the path if both are provided

## [1.41.0] - 2023-03-26
### Added
- IActionGraph to replace legacy execution attribute workflow

## [1.40.0] - 2023-03-24
### Changed
- Updated OnObjectChanged to use new target type for prim input

## [1.39.0] - 2023-03-10
### Fixed
- Fix tests to handle target attributes

## [1.38.1] - 2023-03-16
### Added
- "threadsafe" scheduling hints to OgnOnObjectChange, OgnOnVariableChange, and OgnRationalTimeSyncGate nodes.
### Changed
- OgnOnObjectChange and OgnOnVariableChange unit tests to utilize thread-safety test constructs since they are now marked threadsafe.

## [1.38.0] - 2023-03-10
### Changed
- OnStageEvent now ignores timeline pause and resume
- Added omni.timeline dependency

## [1.37.6] - 2023-03-10
### Changed
- OGN tick uses fabric vectorized states instead of an internal state (x10 perf improvment)

## [1.37.5] - 2023-03-01
### Fixed
- Corner case related to fan-out of exec connections to a single node

## [1.37.4] - 2023-02-25
### Changed
- Modifed format of Overview to be consistent with the rest of Kit

## [1.37.3] - 2023-02-23
### Fixed
- A few Action Graph node unit tests that were failing/flaky.

## [1.37.2] - 2023-02-22
### Added
- Links to JIRA tickets regarding filling in the missing documentation

## [1.37.1] - 2023-02-22
### Changed
- Renamed omni.kit.exec references to omni.kit.exec.core

## [1.37.0] - 2023-02-22
### Added
- `OnStageEvent` handles new event - "Hierarchy Changed"

## [1.36.3] - 2023-02-21
### Added
- Unit tests for all Action Graph nodes that were missing them.
- Threadsafety tests for threadsafe AG nodes using the ThreadsafetyTestUtils decorator.
### Changed
- Moved some of the Action Graph integration tests out of omni.graph.test and into
  omni.graph.action because they fit in the latter extension better (i.e. some of the
  AG "integration" tests were really just testing specific AG node behavior and/or
  specific AG evaluation mechanics, and not broader integration with other nodes/
  systems).

## [1.36.2] - 2023-02-19
### Changed
- Added label to the main doc page so that higher level docs can reference the extension
- Tagged for adding links to node documentation

## [1.36.1] - 2023-02-17
### Added
- "threadsafe" scheduling hints to OgnBranch, OgnCounter, OgnDelay, OgnFlipFlop, OgnForEach,
  OgnForLoop, OgnGate, OgnMultigate, OgnMultisequence, OgnOnClosing, OgnOnGamepadInput,
  OgnOnImpulseEvent, OgnOnLoaded, OgnOnMouseInput, OgnOnPlaybackTick, OgnOnce, OgnSequence,
  OgnSwitchToken, and OgnSyncGate nodes.
### Changed
- Changed a CARB_LOG_ERROR_ONCE call to CARB_LOG_WARN_ONCE in OnGamepadInput.cpp.
### Removed
- Unnecessary headers in OnVariableChange.cpp.
- Excluded .ogn tests for OgnCounter, OgnFlipFlop, and OgnForLoop due to failing
  false-positive autogenerated threadsafety tests.

## [1.36.0] - 2023-02-10
### Added
- New node GetGraphTargetId
### Fixed
- OnGamepadInput handling of button press
### Changed
- GraphTarget is now named "Get Graph Target"

## [1.35.3] - 2023-02-09
### Fixed
- Ordering of dependency node compute for AG fan-out with shared dependencies

## [1.35.2] - 2023-02-08
### Fixed
- Book-keeping in ActionNodeDef for add and remove of dynamic attributes

## [1.35.1] - 2023-02-07
### Fixed
- OnVariableChange node now correctly takes into account instancing in its "onValueChangeCallback"

## [1.35.0] - 2023-02-02
### Changed
- Adopted safe dispatch to stabilize execution of nodes computed for the first time.

## [1.34.2] - 2023-01-30
### Changed
- Removed the kit-sdk landing page
- Moved all of the documentation into the new omni.graph.docs extension

## [1.34.1] - 2023-01-26
### Fixed
- OnKeyboardInput to work with instancing
- bug in event node input dirtying logic

## [1.34.0] - 2023-01-24
### Added
- Execution framework implementation of action graph evaluator

## [1.33.0] - 2023-01-11
### Changed
- ABI calls to take into account instancing
- Few nodes implement vectorized computes

## [1.32.2] - 2022-12-21
### Changed
- Refactored CUDA build to consolidate build functions and remove unnecessary rebuilds

## [1.32.1] - 2022-08-30
### Fixed
- Linting errors

## [1.32.0] - 2022-08-17
### Added
- Added OnVariableChange node

## [1.31.0] - 2022-08-16
### Added
- SwitchToken

## [1.30.1] - 2022-08-09
### Fixed
- Applied formatting to all of the Python files

## [1.30.0] - 2022-07-29
### Changed
- Add prim input to OnObjectChanged node

## [1.29.0] - 2022-07-29
### Added
- Support for relative image urls in UI widget nodes

## [1.28.1] - 2022-07-28
### Fixed
- Spurious error messages about 'Node compute request is ignored because XXX is not request-driven'

## [1.28.0] - 2022-07-26
### Added
- Placer node.
- Added ReadWidgetProperty node

## [1.27.0] - 2022-07-26
### Changed
- Removed internal Placers from the widget nodes.

## [1.26.1] - 2022-07-25
### Fixed
- Various UI nodes were rejecting valid exec inputs like ENABLED_AND_PUSH

## [1.26.0] - 2022-07-22
### Added
- 'style' input attributes for Button, Spacer and Stack nodes.
### Fixed
- WriteWidgetStyle was failing on styles containing hex values (e.g. for colors)

## [1.25.0] - 2022-07-20
### Added
- WriteWidgetStyle node

## [1.24.1] - 2022-07-21
### Changed
- Undo revert

## [1.24.0] - 2022-07-18
### Added
- Spacer node
### Changed
- VStack node:
  - Removed all execution inputs except for create.
  - Added support for OgnWriteWidgetProperty.
  - inputs:parentWidgetPath is no longer optional.

## [1.23.0] - 2022-07-18
### Changed
- Reverted changes in 1.21.1

## [1.22.0] - 2022-07-15
### Added
- WriteWidgetProperty node
### Changed
- Removed all of Button node's execution inputs except for Create
- Removed Button node's 'iconSize' input.
- Modified Button node to work with WriteWidgetProperty

## [1.21.1] - 2022-07-15
### Changed
- Added test node TickN, modified tests

## [1.21.0] - 2022-07-14
### Changed
- Added +/- icons to Multigate and Sequence

## [1.20.0] - 2022-07-07
### Added
- Test for public API consistency

## [1.19.0] - 2022-07-04
### Changed
- OgnButton requires a parentWidgetPath. It no longer defaults to the current viewport.
- Each OgnButton instance can create multiples buttons. They no longer destroy the previous ones.
- widgetIdentifiers are now unique within GraphContext

## [1.18.1] - 2022-06-20
### Changed
- Optimized MultiSequence

## [1.18.0] - 2022-05-30
### Added
- OnClosing

## [1.17.1] - 2022-05-23
### Changed
- Changed VStack ui name to Stack

## [1.17.0] - 2022-05-24
### Changed
- Converted ForEach node from Python to C++
- Removed OnWidgetDoubleClicked

## [1.16.1] - 2022-05-23
### Changed
- Converted Counter node from Python to C++

## [1.16.0] - 2022-05-21
### Added
- Removed OnGraphInitialize, added Once to replace

## [1.15.1] - 2022-05-20
### Changed
- Added direction input to VStack node to allow objects to stack in width, height & depth directions.
- Button node uses styles to select icons rather than mouse functions.

## [1.15.0] - 2022-05-19
### Added
- OnGraphInitialize - triggers when the graph is created
### Changed
- OnStageEvent - removed non-functional events

## [1.14.1] - 2022-05-19
### Fixed
- Fixed OgnOnWidgetValueChanged output type resolution

## [1.14.0] - 2022-05-17
### Changed
- Added '(BETA)' to the ui_names of the new UI nodes.

## [1.13.0] - 2022-05-16
### Added
- Added Sequence node with dynamic outputs named OgnMultisequence

## [1.12.0] - 2022-05-11
### Added
- Node definitions for UI creation and manipulation
- Documentation on how to use the new UI nodes
- Dependencies on extensions omni.ui_query and omni.kit.window.filepicker(optional)

## [1.11.3] - 2022-04-12
### Fixed
- OnCustomEvent when onlyPlayback=true
- Remove state attrib from PrintText

## [1.11.2] - 2022-04-08
### Added
- Added absoluteSimTime output attribute to the OnTick node

## [1.11.1] - 2022-03-16
### Fixed
- OnStageEvent Animation Stop event when only-on-playback is true

## [1.11.0] - 2022-03-10
### Added
- Removed _outputs::shiftOut_, _outputs::ctrlOut_, _outputs::altOut_ from _OnKeyboardInput_ node.
- Added _inputs::shiftIn_, _inputs::ctrlIn_, _inputs::altIn_ from _OnKeyboardInput_ node.
- Added support for key modifiers to _OnKeyboardInput_ node.
## [1.10.1] - 2022-03-09
### Changed
- Made all input attributes of all event source nodes literalOnly
## [1.10.0] - 2022-02-24
### Added
- added SyncGate node
## [1.9.1] - 2022-02-14
### Fixed
- add additional extension enabled check for omni.graph.ui not enabled error
## [1.9.0] - 2022-02-04
### Added
- added SetPrimRelationship node
## [1.8.0] - 2022-02-04
### Modified
- Several event nodes now have _inputs:onlyPlayback_ attributes to control when they are active. The default is enabled, which means these nodes will only operate what playback is active.
### Fixed
- Category for Counter
## [1.7.0] - 2022-01-27
### Added
- Added SetPrimActive node
## [1.6.0] - 2022-01-27
### Added
- Added OnMouseInput node
### Modified
- Changed OnGamepadInput to use SubscriptionToInputEvents instead
- Changed OnKeyboardInput to use SubscriptionToInputEvents instead
## [1.5.0] - 2022-01-25
### Added
- Added OnGamepadInput node
## [1.4.5] - 2022-01-24
### Fixed
- categories for several nodes
## [1.4.4] - 2022-01-14
### Added
- Added car customizer tutorial
## [1.4.2] - 2022-01-05
### Modified
- Categories added to all nodes
## [1.4.1] - 2021-12-20
### Modified
- _GetLookAtRotation_ moved to _omni.graph.nodes_
## [1.4.0] - 2021-12-10
### Modified
- _OnStageEvent_ handles new stage events
## [1.3.0] - 2021-11-22
### Modified
- _OnKeyboardInput_ to use allowedTokens for input key
- _OnStageEvent_ bugfix to avoid spurious error messages on shutdown
## [1.2.0] - 2021-11-10
### Modified
- _OnKeyboardInput_, _OnCustomEvent_ to use _INode::requestCompute()_
## [1.1.0] - 2021-11-04
### Modified
- _OnImpulseEvent_ to use _INode::requestCompute()_

## [1.0.0] - 2021-05-10
### Initial Version
