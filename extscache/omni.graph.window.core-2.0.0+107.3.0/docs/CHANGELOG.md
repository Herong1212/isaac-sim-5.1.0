(changelog_omni_graph_window_core)=

# Changelog

This document records all notable changes to the **omni.graph.window.core** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [2.0.0] - 2025-01-09
### Changed
- set omni.kit.widget.graph dependency to accept major change

## [1.140.1] - 2024-12-16
### Changed
- Remove test dependencies which are already included.

## [1.140.0] - 2024-11-18
### Changed
- Jumping versions for 107 to leave room for changes to 106.*-based builds.

## [1.131.0] - 2024-11-15
### Changed
- Added public API doc

## [1.130.1] - 2024-10-24
### Fixed
- Pasting nodes gave an exception due to a missing filter function.

## [1.130.0] - 2024-09-19
### Changed
- bumping version to make room for 106.2-based extensions

## [1.120.3] - 2024-09-06
### Fixed
- Renaming compound nodes no longer breaks connections

## [1.120.2] - 2024-08-30
### Changed
- Fix flaky test test_variable_instances_window

## [1.120.1] - 2024-08-27
### Changed
- Fix deprecated module imports

## [1.120.0] - 2024-08-09
### Changed
- bumping version to make room for 106-based extensions

## [1.112.0] - 2024-07-18
### Fixed
- Use exact uiName if it is provided, do not title case or remove namespace separators

## [1.111.0] - 2024-05-30
### Changed
- Updated the formatting
- Made omni.inspect optional

## [1.110.0] - 2024-05-17
### Added
- Update the 'support_level' entry in the configuration files to match the release requirements

## [1.109.1] - 2024-04-17
### Added
- Add a 'support_level' entry to the configuration file of the extensions

## [1.109.0] - 2024-04-10
### Changed
- Bumped dependency on omni.graph to version 1.139.0
- Bumped dependency on omni.graph.core to version 2.177.1
- Bumped dependency on omni.graph.tools to version 1.77.0

## [1.108.1] - 2024-04-04
### Changed
- Change the behavior category to character

## [1.108.0] - 2024-03-18
### Changed
- Bumped dependency on omni.graph.core to version 2.176.3
- Bumped dependency on omni.graph to version 1.138.1

## [1.107.0] - 2024-03-01
### Fixed
- If right mouse + Alt is held for zooming, it shouldn't trigger context menu even when the click is on the nodes

## [1.106.0] - 2024-02-29
### Changed
- Removed workaround from OM-99274.

## [1.105.2] - 2024-02-29
### Changed
- Fixed graph selector to work in raster mode and external AG window to refocus when Opening Graph from stage.

## [1.105.1] - 2024-02-23
### Changed
- Fixing graph crash during switching graph through selector

## [1.105.0] - 2024-02-15
### Changed
- Bumped dependency on omni.graph.core to version 2.174.2
- Bumped dependency on omni.graph.tools to version 1.76.1

## [1.104.0] - 2024-02-05
### Changed
- Bumped dependency on omni.graph to version 1.138.0
- Bumped dependency on omni.graph.core to version 2.174.0
- Bumped dependency on omni.graph.tools to version 1.76.0

## [1.103.0] - 2024-01-31
### Changed
- Bumped dependency on omni.graph to version 1.137.0
- Bumped dependency on omni.graph.core to version 2.171.1
- Bumped dependency on omni.graph.tools to version 1.76.0

## [1.102.1] - 2024-01-30
### Fixed
- increase test_create_connection refresh frames

## [1.102.0] - 2024-01-30
### Changed
- Bumped dependency on omni.graph to version 1.136.1
- Bumped dependency on omni.graph.core to version 2.170.1
- Bumped dependency on omni.graph.tools to version 1.74.0

## [1.101.1] - 2024-01-29
### Changed
- Add unit tests for variable rename

## [1.101.0] - 2024-01-26
### Added
- Support for connecting subgraph inputs to subgraph outputs

## [1.100.1] - 2024-01-25
### Fixed
- Updated tests image containing constant nodes

## [1.100.0] - 2024-01-23
### Changed
- reverted change to call node_background_v2
- Bumped dependency on omni.graph to version 1.136.0

## [1.99.1] - 2024-01-22
### Changed
- add node_background_v2 to allow disable drawing icon

## [1.99.0] - 2024-01-18
### Changed
- Bumped dependency on omni.graph.core to version 2.169.1
- Bumped dependency on omni.graph to version 1.135.1
- Bumped dependency on omni.graph.tools to version 1.73.0

## [1.98.3] - 2024-01-16
### Changed
- Re-enable tests

## [1.98.2] - 2024-01-13
### Fixed
- Repository URL in config file.

## [1.98.1] - 2024-01-12
### Changed
- Update variable instances window

## [1.98.0] - 2024-01-12
### Changed
- Bumped dependency on omni.graph to version 1.134.7
- Bumped dependency on omni.graph.core to version 2.169.0
- Bumped dependency on omni.graph.tools to version 1.70.0

## [1.97.3] - 2024-01-04
### Changed
- Made a test less time dependent (and thus less flaky).

## [1.97.2] - 2024-01-04
### Removed
- Kit 104-specific image tests.

## [1.97.1] - 2024-01-03
### Changed
- Adds right-click menu options for copy/paste.

## [1.97.0] - 2023-12-28
### Changed
- Bumped dependency on omni.graph.tools to version 1.69.0

## [1.96.0] - 2023-12-28
### Changed
- Bumped dependency on omni.graph.core to version 2.167.0
- Bumped dependency on omni.graph to version 1.134.2
- Bumped dependency on omni.graph.tools to version 1.68.0

## [1.95.0] - 2023-12-18
### Changed
- Bumped dependency on omni.graph.core to version 2.166.0
- Bumped dependency on omni.graph to version 1.134.0
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.94.0] - 2023-12-15
### Added
- Event streams for OmniGraphWidget and OmniGraphModel.

## [1.93.0] - 2023-12-12
### Changed
- Enable port snapping connection for omni.graph.window.core, make sure the return widget is correct for port_input and port_output

## [1.92.0] - 2023-12-12
### Changed
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph to version 1.133.2
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.91.0] - 2023-12-11
### Changed
- Increase test wait time between frames
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph to version 1.133.2
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.90.5] - 2023-12-08
### Fixed
- Call to private method was failing. Switched to public method.

## [1.90.4] - 2023-12-01
### Changed
- Added comment to catalog_model.py about a dependency on pseudo-node types in omni.kit.telemetry

## [1.90.3] - 2023-11-30
### Fixed
- Spelling errors

## [1.90.2] - 2023-11-30
### Changed
- Fix spelling issues

## [1.90.1] - 2023-11-29
### Changed
- add get variable instances fn in variable model

## [1.90.0] - 2023-11-16
### Fixed
- If right mouse + Alt is held for zooming, it shouldn't trigger context menu

## [1.89.3] - 2023-11-09
### Changed
- Ran the formatter

## [1.89.2] - 2023-11-06
### Changed
- IsolationModel EmptyPorts should not be renamable

## [1.89.1] - 2023-10-19
### Changed
- Fix compatibility with older versions of kit

## [1.89.0] - 2023-10-18
### Added
- Hidden menu items for mapping an target attributes

## [1.88.2] - 2023-09-27
### Changed
- Fix broken tests due to recent variable widget changes

## [1.88.1] - 2023-09-21
### Changed
- Fixed bundle connection test

## [1.88.0] - 2023-09-18
### Changed
- Restricting multi connections to bundle attributes without allowMultiInputs metadata

## [1.87.1] - 2023-09-12
### Changed
- Updating tests for new target nodes

## [1.87.0] - 2023-09-11
### Changed
- Renamed built-in characterSystem category to behavior and removed unused animationGraph category.

## [1.86.4] - 2023-09-08
### Changed
- Promote to Constant now works with target typed attributes

## [1.86.3] - 2023-09-07
### Changed
- replace VariableNameModel as VariableNameListModel

## [1.86.2] - 2023-09-07
### Changed
- Suppress multiple expected warnings/errors from incompatible type tests

## [1.86.1] - 2023-09-05
### Changed
- Allow QuickSearch extra time to initialize before rebuilding its node list.

## [1.86.0] - 2023-08-22
### Removed
- Disabled test that no longer works with PostRenderGraph

## [1.85.9] - 2023-08-21
### Changed
- Promote to Constant now supports all availible types

## [1.85.8] - 2023-08-11
### Changed
- Promote to Constant now supports all availible types

## [1.85.7] - 2023-08-10
### Changed
- Changes OmniNote to Note in node catalog

## [1.85.6] - 2023-08-09
### Changed
- Changed "OmniNote" to just "Note" in node catalog

## [1.85.5] - 2023-08-09
### Fixed
- Renaming and connecting output bundles to compound node outputs no longer throw errors

## [1.85.4] - 2023-08-09
### Fixed
- Renaming a compound node correctly refreshes connections
- Fixed exception during connection when renaming or creating compounds
### Changed
- Promotion menu items no longer visible when nothing selected

## [1.85.3] - 2023-08-02
### Fixed
- Add rename port to context menu for connected ports

## [1.85.2] - 2023-08-02
### Changed
- Add context menu to promote unconnected inputs/outputs on a node

## [1.85.1] - 2023-08-02
### Fixed
- Editing a compound subgraph prim now opens the subgraph instead of printing an error

## [1.85.0] - 2023-08-01
### Added
- Context menus to create new ports from the virtual node

## [1.84.2] - 2023-07-31
### Changed
- Standardized the format of the CHANGELOG

## [1.84.1] - 2023-07-29
### Fixed
- Dragging prims from the Stage window into a graph view was failing with errors.

## [1.84.0] - 2023-07-22
### Added
- Main documentation page

## [1.83.1] - 2023-07-20
### Changed
- Bumping the version so that debug versions of extensions will publish

## [1.83.0] - 2023-07-19
### Removed
- Obsolete test dependency on omni.graph.test

## [1.82.1] - 2023-07-18
### Fixed
- Lint errors caused by formatter
- Spelling errors

## [1.82.0] - 2023-07-18
### Added
- Enabled renaming ports on input and output nodes
### Changed
- Reusing port names during rename automatically finds a new name

## [1.81.0] - 2023-07-17
### Added
- Ability to create an empty compound subgraph from the context menu

## [1.80.0] - 2023-07-10
### Changed
- Migrated this extension from kit-graphs to the kit-omnigraph repo. The kit-graphs repo will continue to be
  used for Kit 105.0-based releases.

## [1.69.1] - 2023-06-29
### Fixed
- Compound node ports were incorrectly refreshing on disconnection

## [1.69.0] - 2023-06-29
### Added
- Context menu now appears when right-clicking empty space
### Changed
- Context menu on input and output nodes allows for removing of ports
- Input and Output nodes hide unsupported operations in node context menu
- Compound Nodes hide the help documentation overlay

## [1.68.0] - 2023-06-26
### Changed
- Support for only selecting backdrops only by header bar.
- Moved backdropGetter so we can pass in the GraphWidget, to be able to get node sizes.

## [1.67.0] - 2023-06-23
### Changed
- The node catalog and QuickSearch now search the UI name of the node type rather than its internal name.
- The node catalog and QuickSearch no longer search the node description.
- The matching of search terms can now be spread between the node type and its category.
- If a category matches the search terms it will be expanded even if none of its nodes match.
### Fixed
- Clicking on a node type in the QuickSearch window will reliably create the node.

## [1.66.0] - 2023-06-23
### Added
- Enabled compound subgraphs for all builds

## [1.65.1] - 2023-06-22
### Fixed
- Variables nodes are now correctly created in compound graphs

## [1.65.0] - 2023-06-13
### Added
- Added input and output virtual nodes when using a compound subgraph

## [1.64.0] - 2023-06-12
### Added
- Added OmniNote functionality.

## [1.63.3] - 2023-06-09
### Changed
- Only enable new graph delegate behavior if compounds are enabled and compound subgraphs are supported

## [1.63.2] - 2023-06-07
### Added
- Context menus for add/remove/rename ports for compounds
- Double click to edit compound names and port names
- Use compound name rather than type, regardless of the type as name setting

## [1.63.1] - 2023-06-05
### Changed
- Replaced deprecrated omni.graph.core.MetadataKeys references with omni.graph.tools.ogn.MetadataKeys
- Replaced deprecrated omni.graph.core.get_global_container_graphs references with get_global_orchestration_graphs
- Replaced deprecrated omni.graph.tools.supported_attribute_type_names refs with omni.graph.tools.ogn.supported_attribute_type_names

## [1.63.0] - 2023-05-31
### Changed
- bump kit-sdk version
- Breadcrumbs should use the compound name rather than the subgraph name
- Select compound node after creation
- Change tests to use lower case default compound name

## [1.62.0] - 2023-05-18
### Changed
- bumped kit-sdk version

## [1.61.0] - 2023-05-18
### Changed
- Moved `force_regenerate = True` to omni.kit.widget.graph

## [1.60.3] - 2023-05-17
### Added
- Added RMB menu option to edit a compound

## [1.60.2] - 2023-05-16
### Fixed
- Changed test to use different nodes that hadn't been changed from 105 to 105.1

## [1.60.1] - 2023-05-15
### Fixed
- Modified test to handle 105.0 and 105.1+ differently

## [1.60.0] - 2023-05-15
### Changed
- Re-enable double-click to enter compounds, but disable test caused by virtual input/output nodes appearing

## [1.59.3] - 2023-05-12
### Fixed
- Prim drop menu was always dropping ReadPrims.

## [1.59.2] - 2023-05-11
### Updated
- Updated another golden image

## [1.59.1] - 2023-05-10
### Updated
- Updated golden images

## [1.59.0] - 2023-05-04
### Added
- OmniGraphView.screen_to_view(), .mouse_to_view() and .mouse_to_screen()
### Fixed
- Dialog windows in the graph editor not appearing at mouse pointer.
- Invisible zombie dialog boxes never being destroyed.

## [1.58.0] - 2023-05-01
### Added
- Collapse nodes to a subgraph compound node

## [1.57.1] - 2023-04-24
### Added
- Added deprecation warning for bundle attributes without 'allowMultiInputs' metadata
- Reenabled bundle connection test

## [1.57.0] - 2023-04-24
### Removed
- Deprecated commands: OGSetUsdUINodeGraphNodeAttrCommand, OGRemoveUsdUIPositionAttrCommand

## [1.56.1] - 2023-04-24
### Fixed
- too many refreshes when attribute values change

## [1.56.0] - 2023-04-24
### Changed
- Reverted compound MR that enables subgraphs

## [1.55.0] - 2023-04-20
### Added
- Ability to double-click and open up compound nodes
- Added subgraphs to the list of graphs that can be switched to in the drop-down

## [1.54.2] - 2023-04-18
### Fixed
- Fixed issue where connections were always removed when making multiple connections.
- Updated test images for change in node help functionality

## [1.54.1] - 2023-04-18
### Fixed
- The node help icon only appears when hovering over the header now and only after a half-second delay.
- Only clicking with the left mouse button will bring up node help now.
- Dragging on the help icon won't bring up help.

## [1.54.0] - 2023-04-14
### Added
- Type conversion context menu to nodes

## [1.53.2] - 2023-04-14
### Changed
- Added more general way to handle relationship connections
- Removed implicit multi-connection support for target types.  Now relys on allowMultiInputs metadata.
### Added
- Added test_delete_target_connection

## [1.53.1] - 2023-04-11
### Fixed
- Call rebuild node when attributes are resolved

## [1.53.0] - 2023-04-11
### Fixed
- ActionGraph Subgraphs created in code or in older versions can be opened without exceptions in the editor.

## [1.52.6] - 2023-04-11
### Fixed
- Updated the test golden images to match kit 105.1

## [1.52.5] - 2023-04-05
### Changed
- Dragging a prim into the editor and reading bundles now brings in a ReadPrims node in 105 and greater.

## [1.52.4] - 2023-04-05
### Fixed
- Fixed failing test_delete_connection test.

## [1.52.3] - 2023-04-05
### Fixed
- Fixed some invalid type hinting.

## [1.52.2] - 2023-04-03
### Fixed
- The node context menu now appears even when there is no selected node

## [1.52.1] - 2023-04-03
### Fixed
- Added better check for newest mouse position functions

## [1.52.0] - 2023-03-29
### Added
- Added Actions and Hotkeys for Copy & Paste in OmniGraphs.

## [1.51.1] - 2023-03-23
### Fixed
- Variable type changes handle authoring layer mismatches
- Variable appearance refreshes on type change

## [1.51.0] - 2023-03-22
### Added
- graph_operations.show_help_for_node_type()
### Changed
- Have the node menu and the help icon use the new method.

## [1.50.0] - 2023-03-21
### Added
- Restore support for a help page to open up when the user clicks on the node type icon

## [1.49.1] - 2023-03-15
### Added
- Added support for target attributes in editor

## [1.49.0] - 2023-03-15
### Added
- double-clicking on the empty canvas will now select the Graph

## [1.48.0] - 2023-03-08
### Added
- omni.graph.bundle.action test dependency

## [1.47.1] - 2023-03-08
### Fixed
- Disable tests which use the ReadPrims node for Kit versions < 105 since they don't have that node.

## [1.47.0] - 2023-03-07
### Added
- Action and hotkey support.

## [1.46.0] - 2023-03-07
### Added
- Added a context menu for nodes.

## [1.45.4] - 2023-03-06
### Fixed
- New connections to bundle ports will remove existing connections.

## [1.45.3] - 2023-03-01
### Fixed
- Only utilize the new run_coroutine() method if it exists in omni.kit.async_engine, otherwise revert to asyncio.ensure_future(). This is done for backwards compatibility with Kit 104.2, which doesn't have the method.

## [1.45.2] - 2023-02-28
### Changed
- Replaced asyncio.ensure_future() call with the new omni.kit.async_engine.run_coroutine() method.

## [1.45.1] - 2023-02-22
### Fixed
- Attempts to create connections between incompatible attributes no longer remove the existing connections.

## [1.45.0] - 2023-02-21
### Changed
- Node types now sorted by name in catalog

## [1.44.4] - 2023-02-20
### Added
- Adds new category and icons for animationGraph and characterSystem.

## [1.44.3] - 2023-02-09
### Changed
- Use fastShutdown on tests to avoid problems in Kit 104.2 which have been fixed in 105.

## [1.44.2] - 2023-02-03
### Removed
- Removed support for the node help icon until some issues can be resolved.

## [1.44.1] - 2023-02-02
### Fixed
- Add dependency to omni.kit.ui_test for tests
- OmniGraphNodeTypeCatalogModel init: removing passing of 'args' to super init.
- Remove hardcoded subclass and self arguments in super() init call in the following classes:
      OmniGraphSelectorItemDelegate, OmniGraphSelectorItem and OmniGraphSelectorModel
- OmniGraphWindow: added property to store a function that will be called in on_build_window,
   This is done to fix a Pybind11 issue OM-79384, that was happening in the omni.graph.window.generic tests
   Note: this change should be reverted when that issue is solved.

## [1.44.0] - 2023-02-01
### Added
- Support for a help page to open up when the user clicks on the node type icon

## [1.43.3] - 2023-01-26
### Changed
- Disabled (in Linux ETM only) all tests which fail with 'invalid self' error.

## [1.43.2] - 2023-01-20
### Fixed
- View -> Layout Nodes works again. Or at least as well as it used to.
### Added
- test_layout_nodes

## [1.43.1] - 2023-01-12
### Fixed
- Fixed issue where hidden ports would be shown when node is first created.

## [1.43.0] - 2023-01-09
### Changed
- Merged all of the _get_kit_version() functions in og.window.* into one.

## [1.42.4] - 2023-01-07
### Fixed
- Don't let OmniGraphNodeTypeCatalogModel build the node list until after its __init__() has returned.

## [1.42.3] - 2022-12-30
### Fixed
- Don't cache a new connection until both of the connected nodes have been cached.

## [1.42.2] - 2022-12-14
### Fixed
- Increased image comparison threshold for test_set_from_variable to avoid failures due to minor differences in
  how text is aliased.

## [1.42.1] - 2022-12-13
### Changed
- Update test golden image.
### Fixed
- Filter prop changes from removed prims instead of changed prims.

## [1.42.0] - 2022-12-12
### Added
- Context menu on ports
- Promote to Constant, Promote to Variable and Set to/from Variable options

## [1.41.0] - 2022-12-01
### Fixed
- Handle the deprecation of the useSchemaPrims preference.

## [1.40.1] - 2022-11-02
### Added
- Create regression tests that mimic manual omnigraph changes

## [1.40.0] - 2022-10-28
### Added
- Context menu for compound creation

## [1.39.0] - 2022-10-26
### Added
- Support for compound node styles

## [1.38.0] - 2022-10-24
### Changed
- Stopped OM-66897 changes from affecting pre-kit-105 builds.

## [1.37.0] - 2022-10-24
### Changed
- OM-64076: Update drag and drop and add targets to the Read Prim.

## [1.36.0] - 2022-10-20
### Changed
- literalOnly input ports are no longer shown as ports because they are not connectable

## [1.35.0] - 2022-10-17
### Added
- Initial support for graphs containing compound nodes

## [1.34.0] - 2022-09-14
### Added
- Added draw_header_label_left(), draw_header_label_center() and draw_header_label_right() (for OM-61502)

## [1.33.1] - 2022-09-14
### Fixed
- Fixed variable read and write widgets not override drag of variable

## [1.33.0] - 2022-09-08
### Fixed
- Revert to old way of disabling undo if omni.kit.undo.disabled() is not available.

## [1.32.0] - 2022-09-02
### Fixed
- Nodes once again update their colors and tooltips when their error status changes.

## [1.31.0] - 2022-08-31
### Removed
- The fixed version in the omni.kit.commands dependency.

## [1.30.3] - 2022-08-25
### Changed
- Fixing issue where bundle connections show up as fan-in even when they are not

## [1.30.2] - 2022-08-25
### Changed
- Added ability to open graphs when right-clicking on a node in the stage

## [1.30.1] - 2022-08-28
- Added omni.graph.tutorials as test dependency

## [1.30.0] - 2022-08-24
### Changed
- Uses event stream on graph registry instead of the extension manager to refresh node catalog

## [1.29.1] - 2022-08-22
### Changed
- Renamed test golden image to be unique among all extensions.

## [1.29.0] - 2022-08-08
### Changed
- OGSetUsdUINodeGraphNodeAttrCommand and OGRemoveUsdUIPositionAttrCommand have been deprecated in favor of
  UsdUINodeGraphNodeSetCommand and UsdUIRemovePositionCommand from omni.kit.graph.usd.commands.

## [1.28.1] - 2022-08-02
### Fixed
- OM-57134 Fix for renaming tuple variables cause them to be deleted

## [1.28.0] - 2022-07-29
### Added
- OM-56665 handling fan-in to any attribute type, not represented in UI (moving implementation to base class)

## [1.27.2] - 2022-07-28
### Added
- OM-56668 Drag and drop multiple prims from stage onto node editor (fix for only dropping "readprimintobundle")

## [1.27.1] - 2022-07-28
### Fixed
- Variable type name is now in Sdf format when its model is initialized
- Fixed error when reading tooltip for a non-existing variable

## [1.27.0] - 2022-07-21
### Added
- OM-56668 Drag and drop multiple prims from stage onto node editor

## [1.26.2] - 2022-07-19
### Changed
- VariableNameModel now notifies subscribed widgets only after editing is finished

## [1.26.1] - 2022-07-15
### Fixed
- Leak of model on window shutdown

## [1.26.0] - 2022-07-14
### Changed
- Removed the icon tooltip from node catalog items and extended the description tooltip over the icon

## [1.25.1] - 2022-07-05
### Changed
- Added function that can be shared with particle system graph when processing property changes

## [1.25.0] - 2022-07-05
### Changed
- Changed definition of get_item_value_model in catalog_model for new catalog item design

## [1.24.0] - 2022-07-05
### Changed
- Reverted change

## [1.23.5] - 2022-07-04
### Changed
- Added description to WriteVariable node's tooltip.

## [1.23.4] - 2022-05-27
### Changed
- Removed view regeneration behavior from the literalOnly metadata key, and hardcoded it for Read/Write Variable nodes.

## [1.23.3] - 2022-05-27
### Fixed
- Renaming a variable to an existing name no longer creates a duplicate entry

## [1.23.2] - 2022-05-27
### Fixed
- Turned on always_force_regenerate optimization in OmniGraphView

## [1.23.1] - 2022-05-26
### Fixed
- dbl-click to rename backdrop

## [1.23.0] - 2022-05-23
### Added
- Backdrop support
- 'description', 'size', 'display_color' and 'stacking_order' properties to OmniGraphModel
- is_pseudo_node() and create_backdrop() methods to OmniGraphModel
- Added dependency on omni.kit.graph.usd.commands

## [1.22.1] - 2022-05-18
### Fixed
- Value changes to ui:graphnode:pos & ui:graphnode:expansionState now checked when the graph is dirtied.

## [1.22.0] - 2022-05-17
### Changed
- The 'ui' node category is displayed as 'Ui (BETA)'.

## [1.21.1] - 2022-05-17
### Fixed
- Improved node description formatting by using newlines to indicate paragraph breaks

## [1.21.0] - 2022-05-17
### Changed
- When creating default node name from type name, strip out "(BETA)".

## [1.20.0] - 2022-05-10
### Changed
- Replace all uses of OmniGraphWidget's '_graph_model' member with base class's 'model'.
- References to '_graph_model' by derived classes will be redirected to 'model' and a deprecation warning displayed.
- Clear the model when the stage is closed rather than when it is opened.

## [1.19.0] - 2022-05-06
### Added
- Added support for truncated words in node catalog search window

## [1.18.2] - 2022-05-03
### Fixed
- Fixed errors being displayed when creating and modifying variables
- Variable colors in side-panel now match variable node colors

## [1.18.1] - 2022-05-02
### Fixed
- Disable dragging for categories
### Added
- Add icon borders for create node drop menu

## [1.18.0] - 2022-04-08
### Added
- ALT+RMB+Drag for graph zoom

## [1.17.0] - 2022-04-06
### Fixed
- Added missing 'node' param to header label __draw_header_label()
### Changed
- Renamed _draw_header_label(), _draw_header_icon, and _draw_expansion_button() to make them private.

## [1.16.7] - 2022-04-06
### Fixed
- Fixed a bug where constant node names are broken
- Refactored naming utils - moved make_nice_name() from graph_model.py to graph_config.py so that it can be called from everywhere
- Determine node path from UI name rather than type name, for those nodes that don't have the UI_NAME metadata

## [1.16.6] - 2022-04-05
### Fixed
- Fixed undo/redo for variable description

## [1.16.5] - 2022-04-04
### Changed
- Added support for multiple variable node types

## [1.16.4] - 2022-03-30
### Fixed
- Setup default min/max canvas zoom levels.

## [1.16.3] - 2022-03-30
### Changed
- Hide WriteVariable output port
- Regenerate layout when a LITERAL_ONLY tagged attribute changes

## [1.16.2] - 2022-03-30
### Fixed
- Fixed incorrect node type name

## [1.16.1] - 2022-03-30
### Changed
update repo_build and repo-licensing

## [1.16.0] - 2022-03-28
### Changed
- Increment minor version so that derived windows can set a dependency which they know includes the test framework.

## [1.15.1] - 2022-03-28
### Added
- UI unit test framework.

## [1.15.0] - 2022-03-29
### Added
 - Variable nodes have custom nodes colored based on variable type
### Fixed
 - Expansion state shows correct state with updated color

## [1.14.3] - 2022-03-28
### Changed
- Made it default that open graph will not pop up an inqury window in home

## [1.14.2] - 2022-03-18
### Fixed
- Issue of deleting graph's parent making the graph crash

## [1.14.1] - 2022-03-18
### Fixed
- Fix the port colors
- Fix the node type name formatting

## [1.14.0] - 2022-03-16
### Changed
- Updated variable UI to match the latest design

## [1.13.0] - 2022-03-16
### Fixed
- Node types marked as hidden only hide in the catalogue, not on the canvas

## [1.12.0] - 2022-03-14
### Fixed
- When multiple nodes are selected dragging one now drags them all.

## [1.11.0] - 2022-03-11
### Changed
- Added the ability to change the type of variables after creation
- Removed the popup to create variables

## [1.10.2] - 2022-03-09
### Fixed
- Undoing node layout won't give an error.
- Undoing node layout only requires a single undo, not one per node.

## [1.10.1] - 2022-03-08
### Changed
- Duplicated nodes will appear offset from their originals
- Nodes which are duplicated together will have the same connections between them as their originals

## [1.10.0] - 2022-03-02
### Added
- Mechanism for registering graph editor extensions to open graphs from the stage widget
- Optional dependency on __omni.kit.window.quicksearch__ 2.1

## [1.9.6] = 2022-02-25
### Added
- Added right mouse button menu for connection curve to disconnect selected connection
- Added some comments about inputs property of _graph\_model_

## [1.9.5] - 2022-02-23
### Changed
- Skip the popup question if user clicks on the Create Graph button on toolbar
- Move the ? button to the right of the toolbar

## [1.9.4] - 2022-02-23
### Fixed
- Variables model refreshes properly when the graph is changed

## [1.9.3] - 2022-02-23
### Changed
- Moved the variable editing commands into kit

## [1.9.2] - 2022-02-22
### Changed
- Moved the quicksearch model to individual extensions
- Default node position with on_drop

## [1.9.1] - 2022-02-22
### Added
- Added a shortcut from graph editor to preference

## [1.9.0] - 2022-02-22
### Added
- OmniGraphNodeQuickSearchModel for quick search

## [1.8.10] - 2022-02-22
### Changed
- tool tips for ports
- added dependency on omni.graph.tools

## [1.8.9] - 2022-02-18
### Changed
- toolbar icon for graph selector

## [1.8.8] - 2022-02-18
### Added
- OG editors will now recognize the schema prims (OmniGraph, OmniGraphNode) when they are enabled.
### Changed
- OG editors will not recognize ComputeGraph, GlobalComputeGraph or ComputeGraphSettings nodes if schema prims are enabled

## [1.8.7] - 2022-02-18
### Fixed
- If a prim has a bogus/non-existent UsdUI expansion state, fall back to a sensible default.

## [1.8.6] - 2022-02-18
### Fixed
- Nodes will refresh when dynamic attributes are added or removed
### Added
- Script category icon

## [1.8.5] - 2022-02-17
### Fixed
- OmniGraphModel.expansion_state() wasn't handling prims without UsdUI NodeGraphNodeAPI properly.
- OmniGraphModel.expansion_state() was using the 'node_type_name' property incorrectly.

## [1.8.4] - 2022-02-16
### Added
- Added variables panel and supporting code

## [1.8.3] - 2022-02-16
### Added
- Added a Create Graph button to the toolbar
- Added an Edit Graph button to the toolbar
- Added a Help button to the toolbar

## [1.8.2] - 2022-02-16
### Added
- icons for tutorial and constant and animation categories

## [1.8.1] - 2022-02-15
### Fixed
- Fix "'_OmniGraphModel__usd_expansion_state_to_og' is not defined" error

## [1.8.0] - 2022-02-15
### Added
- OmniGraphModel.og_expansion_state_to_usd()
- OmniGraphModel.usd_expansion_state_to_og()
### Changed
- Removed 'usd' parameter from OmniGraphModel.get_default_node_expansion_state()
### Fixed
- OmniGraphModel.import_node() was passing tuples instead of strings to get_default_node_expansion_state()

## [1.7.1] - 2022-02-14
### Fixed
- An error when Prims are dragged on to stage, and legacy prims are enabled

## [1.7.0] - 2022-02-14
### Added
- OmniGraphModel.get_default_node_expansion_state()
### Changed
- Removed the first underscore from OmniGraphModel's __connections, __reversed_connections, and
  __node_connected_ports members, making them available for use by derived classes.
- Legacy Prim nodes now always display their node names, even when show_name_as_type is True.
### Fixed
- Workaround for OM-44798: exclude zombie legacy Prim nodes from OmniGraphModel's node caches.

## [1.6.6] - 2022-02-11
### Added
- Add icons to the getter and setter node dialogue

## [1.6.5] - 2022-02-11
### Fixed
- A regression where expansion state and View toolbar did not function

## [1.6.4] - 2022-02-10
### Fixed
- When delete graph prim from stage panel, the graph editor doesn't go back to startup screen
- Fix execution pin icon is 3 pixels too far to the right

## [1.6.3] - 2022-02-09
### Fixed
- Clear cached port and connection data when a node is deleted.

## [1.6.2] - 2022-02-08
### Added
- Setter method for OmniGraphModel.name
### Fixed
- Editing the node's name by double-clicking on it in the graph now works.
### Changed
- Double-clicking the node header won't put you into edit mode if the header
  is displaying the node's type instead of its name.
- Node tooltip now always shows the node's name and type, regardless of whether
  the header itself is showing name or type.

## [1.6.1] - 2022-02-04
### Added
- OmniGraphModel.get_node_from_prim()
### Changed
- Nodes change visual appearance when they have evaluation warnings or errors.
- Node header tooltip includes the current warning/error message.

## [1.5.1] - 2022-02-04
### Fixed
- Fallback category icon
### Changed
- Removed Subgraph category

## [1.5.0] - 2022-02-01
### Fixed
- undo of connections from legacy Prims
### Changed
- bump dependency on omni.graph to 1.9

## [1.4.0] - 2022-01-31
### Changed
- Added the catalog delegate

## [1.3.0] - 2022-01-31
### Fixed
- Fixed prim node culling override logic
- Temporarily relax dependency of omni.graph-1.9 to 1.8 to fix older builds of Create

## [1.2.2] - 2022-01-28
### Fixed
- Fixed delegate routing issue

## [1.2.1] - 2022-01-27
### Fixed
- Fixed dependency on omni.graph-1.9
- Changed default setting of showNameAsType

## [1.2.0] - 2022-01-26
### Changed
- Added OmniGraphWidget.is_graph_editable to allow filtering of graph selection

## [1.1.1] - 2022-01-25
### Fixed
- Bundle connections were not being drawn or connected

## [1.1.0] - 2022-01-24
### Changed
- Minor refactoring
- Only show nodes in their primary catalog category

## [1.0.2] - 2022-01-20
### Changed
- Changed main widget button layout
- Minor refactor
## [1.0.1] - 2022-01-20
### Changed
- Changed graph to not use catalog icons
- Updated fallback icon
- Factored out some settings and paths to graph_config module

## [1.0.0] - 2022-01-19
### Added
- Initial commit is migrating code from omni.graph.window.action
