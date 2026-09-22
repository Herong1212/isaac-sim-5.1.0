(changelog_omni_graph_window_action)=

# Changelog

This document records all notable changes to the **omni.graph.window.action** extension.

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

## [1.27.0] - 2024-05-17
### Added
- Update the 'support_level' entry in the configuration files to match the release requirements

## [1.26.2] - 2024-04-30
### Changed
- Calling new app_window.focus to bring external windows to the front

## [1.26.1] - 2024-04-17
### Added
- Add a 'support_level' entry to the configuration file of the extensions

## [1.26.0] - 2024-04-10
### Changed
- Bumped dependency on omni.graph to version 1.139.0
- Bumped dependency on omni.graph.core to version 2.177.1
- Bumped dependency on omni.graph.tools to version 1.77.0

## [1.25.1] - 2024-03-20
### Fixed
- Removed obsolete import

## [1.25.0] - 2024-03-18
### Changed
- Bumped dependency on omni.graph.core to version 2.176.3
- Bumped dependency on omni.graph to version 1.138.1

## [1.24.0] - 2024-02-15
### Changed
- Bumped dependency on omni.graph.core to version 2.174.2
- Bumped dependency on omni.graph.tools to version 1.76.1

## [1.23.0] - 2024-02-05
### Changed
- Bumped dependency on omni.graph to version 1.138.0
- Bumped dependency on omni.graph.core to version 2.174.0
- Bumped dependency on omni.graph.tools to version 1.76.0

## [1.22.0] - 2024-01-31
### Changed
- Bumped dependency on omni.graph to version 1.137.0
- Bumped dependency on omni.graph.core to version 2.171.1
- Bumped dependency on omni.graph.tools to version 1.76.0

## [1.21.0] - 2024-01-30
### Changed
- Bumped dependency on omni.graph to version 1.136.1
- Bumped dependency on omni.graph.core to version 2.170.1
- Bumped dependency on omni.graph.tools to version 1.74.0

## [1.20.0] - 2024-01-23
### Changed
- Bumped dependency on omni.graph to version 1.136.0

## [1.19.0] - 2024-01-18
### Changed
- Bumped dependency on omni.graph.core to version 2.169.1
- Bumped dependency on omni.graph to version 1.135.1
- Bumped dependency on omni.graph.tools to version 1.73.0

## [1.18.1] - 2024-01-13
### Fixed
- Repository URL in config file.

## [1.18.0] - 2024-01-12
### Changed
- Bumped dependency on omni.graph to version 1.134.7
- Bumped dependency on omni.graph.core to version 2.169.0
- Bumped dependency on omni.graph.tools to version 1.70.0

## [1.17.2] - 2024-01-04
### Changed
- Updated golden image tests to be less affected by changes to the node catalog.
### Removed
- Kit 104-specific image tests.

## [1.17.1] - 2024-01-03
### Changed
- Adds toast warning when pasting node with variables that does not exist in the current graph. And ignore nodes that are incompatible

## [1.17.0] - 2023-12-28
### Changed
- Bumped dependency on omni.graph.tools to version 1.69.0

## [1.16.0] - 2023-12-28
### Changed
- Bumped dependency on omni.graph.core to version 2.167.0
- Bumped dependency on omni.graph to version 1.134.2
- Bumped dependency on omni.graph.tools to version 1.68.0

## [1.15.0] - 2023-12-18
### Changed
- Bumped dependency on omni.graph.core to version 2.166.0
- Bumped dependency on omni.graph to version 1.134.0
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.14.0] - 2023-12-12
### Changed
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph to version 1.133.2
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.13.0] - 2023-12-11
### Changed
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph to version 1.133.2
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.12.2] - 2023-08-14
### Changed
- Fix test for renamed action nodes

## [1.12.1] - 2023-07-31
### Changed
- Standardized the format of the CHANGELOG

## [1.12.0] - 2023-07-22
### Added
- Main documentation page

## [1.11.2] - 2023-07-21
### Removed
- Another omni.graph.test dependency.

## [1.11.1] - 2023-07-20
### Changed
- Bumping the version so that debug versions of extensions will publish

## [1.11.0] - 2023-07-19
### Removed
- Obsolete test dependency on omni.graph.test

## [1.10.1] - 2023-07-18
### Fixed
- Spelling errors

## [1.10.0] - 2023-07-10
### Changed
- Migrated this extension from kit-graphs to the kit-omnigraph repo. The kit-graphs repo will continue to be
  used for Kit 105.0-based releases.

## [1.9.0] - 2023-06-22
### Changed
- Nodes created from the QuickSearch window by clicking on an item or pressing ENTER will now be created at the
  position the mouse was at when QuickSearch was invoked.
### Fixed
- Clicking on a node type in the QuickSearch window will reliably create the node.

## [1.8.1] - 2023-06-05
### Changed
- Replaced deprecated omni.graph.core.MetadataKeys references with omni.graph.tools.ogn.MetadataKeys

## [1.8.0] - 2023-05-12
### Added
- Enable double-click to enter compound nodes

## [1.7.7] - 2023-05-10
### Updated
- Updated golden image

## [1.7.6] - 2023-05-04
### Changed
- Disabled node rasterization in tests.

## [1.7.5] - 2023-03-31
### Changed
- Removed omni.graph.ui_nodes tests

## [1.7.4] - 2023-03-28
### Fixed
- Disable crashing test

## [1.7.3] - 2023-03-21
### Fixed
- A couple of golden image tests were overwriting each other's output files.

## [1.7.2] - 2023-03-15
### Fixed
- another test fix

## [1.7.1] - 2023-03-10
### Fixed
- test fix

## [1.7.0] - 2023-03-08
### Added
- omni.graph.bundle.action test dependency

## [1.6.0] - 2023-03-07
### Added
- Action and hotkey support

## [1.5.6] - 2023-02-22
### Fixed
- An expected SyntaxError check in test_button_negative_invalid_style() now works with Python 3.10 as well.

## [1.5.5] - 2023-02-09
### Changed
- Use fastShutdown on tests to avoid problems in Kit 104.2 which have been fixed in 105.

## [1.5.4] - 2023-02-06
### Changed
- Disabled test_write_widget_style_with_widget_path on Linux

## [1.5.3] - 2023-02-02
### Fixed
- Add dependency to omni.kit.ui_test for tests

## [1.5.2] - 2023-01-19
### Fixed
- Action Graph window once again opens as soon as it is created, or shown for the first time.

## [1.5.1] - 2023-01-11
### Fixed
- The Action Graph window now toggles correctly in the Window -> Visual Scripting menu and selecting the
  menu item while it is checked will cause the window to close.

## [1.5.0] - 2023-01-09
### Changed
- Switched how versioned golden images are suffixed. The most recent version is unsuffixed and older
  versions are suffixed with last kit version they worked for.
- Added new golden image for og.window.core.test_dynamic_attributes.
- Merged all of the _get_kit_version() functions in og.window.* into one.

## [1.4.7] - 2023-01-07
### Changed
- Moved OgActionTestCatalogModel into action_catalog_model.py.
- OgActionTestCatalogModel's constructor now takes an iterable of the node types to allow.
- Removed all the debugging prints that I added earlier.

## [1.4.6] - 2022-12-29
### Fixed
- Don't cache a new connection until both of the connected nodes have been cached.

## [1.4.5] - 2022-12-29
### Added
- Some prints to investigate linux ETM test failure.

## [1.4.4] - 2022-12-22
### Changed
- Disable display of the viewport HUD, grid, and axis gnomon.
### Fixed
- test_vstack_and_spacer now ensures that the stack's children are added in a consistent order.

## [1.4.3] - 2022-12-19
### Changed
- Moved tests requiring a viewport into test_ui_nodes.py
- Removed viewport dependencies from the other tests.
- Removed graph editor setup and display from the tests in test_ui_nodes.py

## [1.4.2] - 2022-12-08
### Added
- Added tests for Action Graph UI-creation nodes.
- Added modern viewport as dependency

## [1.4.1] - 2022-12-07
### Fixed
- The window turns to black when it is closed when it's moved to become an external window

## [1.4.0] - 2022-08-22
### Changed
- Created separate pre- and post-kit-105 golden images.

## [1.3.9] - 2022-08-22
### Changed
- Changed test golden image name to be unique among all extensions.

## [1.3.8] - 2022-03-30
### Changed
update repo_build and repo-licensing

## [1.3.7] - 2022-03-29
### Added
- UI unit test framework.

## [1.3.6] - 2022-03-17
### Added
- The lifetime of _Create\\Visual Sciprting\\Action Graph_ menu item is now controlled by this extension
- After opening a graph, the correspnding graph editor window will become focused

## [1.3.5] - 2022-03-02
### Changed
- Mechanism for opening graph from stage widget

## [1.3.4] - 2022-02-23
### Changed
- skip the popup question if user clicks on the Create Graph button on toolbar

## [1.3.3] - 2022-02-22
### Change
- create OmniGraphNodeQuickSearchModel in the extension instead from the core

## [1.3.2] - 2022-02-16
### Changed
- Window is now located at Window/Visual Scripting/Action Graph

## [1.3.1] - 2022-02-21
### Added
- register quick search with Omni Graph Action nodes

## [1.3.0] - 2022-02-01
### Fixed
- Bump dependency on omni.graph.window.core

## [1.2.0] - 2022-01-31
### Fixed
- Workaround for Create 2022.1.0-beta8

## [1.1.0] - 2022-01-28
### Changed
- Window is now located at Window/OmniGraph/Action Graph

## [1.0.36] - 2022-01-26
### Changed
- Filter non-action graphs out of graph selectors

## [1.0.35] - 2022-01-24
### Changed
- Specialize the catalog
- Filter out node types from other types of graphs
- Bump dependency on omni.graph.window.core to 1.1.0

## [1.0.34] - 2022-01-20
### Changed
- Modified main widget button layout

## [1.0.33] - 2022-01-19
### Changed
- Implementation is now based on omni.graph.window.core

## [1.0.32] - 2022-01-14
### Changed
- Fix connection artifact for halfway connections

## [1.0.31] - 2022-01-14
### Fixed
- Display custom icons on node instances

## [1.0.30] - 2022-01-14
### Fixed
- Fixed an error thrown when creating a new graph

## [1.0.29] - 2022-01-12
### Changed
- Simplify port delegate override

## [1.0.28] - 2022-01-11
### Fixed
- Fixed a bug in USD notice handling

## [1.0.27] - 2022-01-07
### Changed
- Return the node type to override the node tooltip in modern delegate

## [1.0.26] - 2022-01-07
### Changed
- Save node positions and expansion state to USD.

## [1.0.25] - 2022-01-07
### Fixed
- Fixed an error that could occur when subgraph nodes are created.

## [1.0.24] - 2022-01-06
### Changed
- Node types with the metadata tag 'hidden' no longer appear.

## [1.0.23] - 2022-01-05
### Changed
- The node type catalog is now organized using OG _categories_ metadata

## [1.0.22] - 2021-12-21
### Changed
- Added a 'nice_name' property to the model.

## [1.0.21] - 2021-12-20
### Fixed
- The automatically added output bundle attribute is now hidden by default for non-Prim OmniGraph nodes.

## [1.0.20] - 2021-12-20
### Fixed
- Position of dragged and dropped nodes
### Changed
- Deprecated Prim nodes are no longer shown in the graph by default

## [1.0.19] - 2021-12-20
### Changed
- Changed connection and connected port color to constant gray by default

## [1.0.18] - 2021-12-17
### Added
- Toolbar added to OmniGraph window

## [1.0.17] - 2021-12-17
### Fixed
- Bug with is_output check causing errors and breaking subgraphs

## [1.0.16] - 2021-12-15
### Changed
- Input attributes with metadata "outputOnly" set to "1" will be given an output port and no input port.

## [1.0.15] - 2021-12-15
### Fixed
- Fix dynamic attributes in UI

## [1.0.14] - 2021-12-10
### Fixed
- Fix tooltips for extended types.

## [1.0.13] - 2021-12-09
### Fixed
- Fix for bug in stage RMB menu for ComputeGraph

## [1.0.12] - 2021-12-08
### Fixed
- Update window to be compatible with latest Kit.

## [1.0.11] - 2021-12-06
### Fixed
- Fix for bug in drop handler for legacy prim node setting

## [1.0.10] - 2021-12-06
### Changed
- Changed the delegate function name to align with other types of delegates

## [1.0.9] - 2021-12-06
### Added
- Tools for supporting working with multiple graphs
  - Switch graph button on the graph editor next to the breadcrumbs
  - Open graph button to main page with list of options

## [1.0.8] - 2021-12-03
### Changed
- Prim drop menu now offers Read/WritePrimAttribute instead of Read/WritePrim

## [1.0.7] - 2021-11-26
### Fixed
- Allow multiple inputs to execution attributes for nodes & subgraphs

## [1.0.6] - 2021-11-23
### Fixed
- Fixed the subgraph connection issue
- Moved the execution pin delegate here from omni.kit.graph.delegate.modern

## [1.0.5] - 2021-11-23
### Fixed
- Moved hard coded color and icons from omni.kit.graph.delegate.modern here
- changed the catalog filter also check node type and node info

## [1.0.4] - 2021-11-19
### Fixed
- fix the bundle attribute connection

## [1.0.3] - 2021-11-19
### Fixed
- remove omni.graph.bundle.action extension. Otherwise, there is a circular dependency

## [1.0.2] - 2021-11-19
### Fixed
- fixed issued caused by empty description of nodes
- fixed drop handler in new editor (read/write/read bundle)

## [1.0.1] - 2021-11-17
### Fixed
- fixed error of `[Error] [omni.graph] Invalid NodeObj object in Py_Node` triggered by graph model

## [1.0.0] - 2021-11-12
### Added
- Initial commit for omni graph
