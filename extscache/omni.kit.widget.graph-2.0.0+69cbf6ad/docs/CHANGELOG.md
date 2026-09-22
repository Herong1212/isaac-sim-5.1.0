# Changelog

This document records all notable changes to the **omni.kit.widget.graph** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [2.0.0] - 2025-01-02
### Changed
- Remove deprecated API

## [1.12.17] - 2024-10-16
### Changed
- Review public API

## [1.12.16] - 2024-10-10
### Added
- Ability to prohibit creation of empty isolation ports.

## [1.12.15] - 2024-07-03
### Fixed
- Inputs connection set should not include the existing connections

## [1.12.14] - 2024-06-26
### Added
- Documentations

## [1.12.13] - 2024-05-15
### Fixed
- HEAP layouted node can't be moved

## [1.12.12] - 2024-03-07
### Fixed
- allow_same_side_connections test not having the correct delegate for connected ports

## [1.12.11] - 2024-03-05
### Fixed
- when allow_same_side_connections is false, fixed same side connection attempts result in wired connection states
- Fixed exception raised when same side connection attempts
- Fixed when draw_curve_top_layer is trye, during the rewiring, the previous connection is not cleared.
- Make sure allow_same_side_conntions flag works properly

## [1.12.10] - 2024-02-28
### Fixed
- Recover the test. Add more test to take the code coverage to over 80%

## [1.12.9] - 2024-02-26
### Fixed
- Fix snapping preview cannot be withdrawn or canceled, once the wire preview is snapped it is locked in.

## [1.12.8] - 2024-02-13
### Fixed
- Recursively grab enclosed children of backdrops, when multiple backdrops are being moved.

## [1.12.7] - 2024-02-05
### Changed
- Remove unnecessary dependency

## [1.12.6] - 2024-02-02
### Fixed
- Make snapping area half of the node width
- Fix the snapping only works while hovering from top down, but not from bottom to top

## [1.12.5] - 2024-02-01
### Added
- Add tests to increaset the code coverage to over 80%
- Run update for rebuild_node full

## [1.12.4] - 2024-01-26
### Fixed
- Proper fix for wild connection flickering before connection completes

## [1.12.3] - 2024-01-24
### Changed
- Modify the snapping effect so that even when port delegate doesnt return anything, we still have snapping effect working
- Add tests to increaset the code coverage

## [1.12.2] - 2024-01-13
### Fixed
- Fixed connections disappear when remove other connection

## [1.12.1] - 2024-01-10
### Fixed
- Fixes clipping of dragging connections, as well as bringing those dragging connections in front of backdrops,

## [1.12.0] - 2024-01-04
### Fixed
- Adds dependency on omni.kit.commands.
- Reverts some of the rewiring test changes and refactors some parts from delegates to graph_node, in order to not break delegates.

## [1.11.0] - 2023-12-07
### Changed
- Adds functionality for rewiring and reverse wiring.

## [1.10.2] - 2023-12-07
### Fixed
- Fixed flicker of wild connection wire before connection completes

## [1.10.1] - 2023-11-30
### Changed
- refine the snapping for connection so that it works even when delegate doesn't return input or output port

## [1.10.0] - 2023-11-27
### Changed
- Reorganized graph drawing to optimize backdrop creation and editing.
- Also to allow curve anchors to draw parts in front of nodes, and other parts behind nodes, on top of curves.

## [1.9.1] - 2023-11-21
### Fixed
- Fixes snapping widgets key error exception

## [1.9.0] - 2023-11-15
### Changed
- introduce enable_snapping_for_connection arg for graph view. With that enabled we use port as the snapping frame so that users can have larger snapping area instead of just the target port widget for connetion

## [1.8.4] - 2023-09-21
### Fixed
- Fixes crash - Always call invalidate_raster, but C++ code checks for m_prv in case it is nullptr.

## [1.8.3] - 2023-09-11
### Fixed
- Fixes crash - Only call placer.invalidate_raster when dragging nodes, not when creating a new node.

## [1.8.2] - 2023-09-08
### Fixed
- Fixes a bug after a node moving command is undone, the position y of the node doesn't revert back to previous value.

## [1.8.1] - 2023-06-30
### Fixed
- Adds check for position == None to fix ETM failure

## [1.8.0] - 2023-06-26
### Added
- Adds selection widget functionality for backdrops to only select on header bar
- Adds better logic for backdrops to only contain nodes that are completely inside the backdrop.
- Adds ALT-drag hotkey to allow user to slide backdrop out from under nodes.

## [1.7.2] - 2023-06-13
### Added
- Store the port center widgets for nodes so that any graph view context menus can access them

## [1.7.1] - 2023-06-02
### Removed
- Removed declaration of omni.kit.widget.graph.tests from extension.toml for faster startup

## [1.7.0] - 2023-05-15
### Added
- Adds force_regenerate = True to layout_all method

## [1.6.4] - 2023-05-08
### Added
- Fixed COLUMNS layout for long port names

## [1.6.3] - 2023-05-04
### Added
- Read-only property `raster_nodes`

## [1.6.2] - 2023-04-24
### Changed
- Don't assume node is in node_widgets

## [1.6.1] - 2023-04-12
### Fixed
- Problem with the selection in the raster pipeline

## [1.6.0] - 2023-04-10
### Changed
- Added functionality to force redraw a node

## [1.5.7] - 2023-01-16
### Changed
- revert change in 1.5.5 for the snapping effect due to redesign

## [1.5.6] - 2023-01-11
### Fixed
- Connection or Node is not updated when model changes

## [1.5.5] - 2023-01-05
### Changed
- use the snapping widget for snapping effect during the connection instead of the actual connection widget

## [1.5.4] - 2022-12-19
### Added
- Setting `/exts/omni.kit.widget.graph/raster_nodes` to rasterize the nodes

## [1.5.3] - 2022-10-28
### Fixed
- Crash when moving several nodes

## [1.5.2] - 2022-10-24
### Added
- Overview for extension

## [1.5.1] - 2022-08-31
### Changed
- make sure rebuild_node only rebuilds the node look, but not rebuilds the ports so that it will not affect connections

## [1.5.0] - 2022-08-30
### Added
- a hook of rebuild_node (rebuild node delegate) to GraphModel, so that user can call it from the model

## [1.4.7] - 2022-07-29
### Changed
- revert the previous change since it crashes the graph during the multiple selection

## [1.4.6] - 2022-07-28
### Fixed
- incorrect node moving in graph (OM-55727)

## [1.4.5] - 2022-05-26
### Added
- The change of node name, description and display_color will trigger the node delegate rebuild

## [1.4.4] - 2022-05-26
### Fixed
- multi selection quick drag resets the selection in graph view(OM-48395)

## [1.4.3] - 2022-04-20
### Changed
- A flag to automatically detect which node is added/removed and edit the widget
  hierarchy instead of rebuilding everything. `always_force_regenerate=False`

## [1.4.2] - 2022-04-22
### Fixed
- fix nodes go wild when the zoom level is beyond the zoom limits(OM-48407)

## [1.4.1] - 2022-04-19
### Fixed
- fix focus_on_nodes to consider zoom_min and zoom_max limits
- fix unreliable tests (OM-48945)

## [1.4.0] - 2022-03-31
### Added
- add _on_set_zoom_key_shortcut API for GraphView to allow user set key shortcut to zoom the graph view

## [1.3.8] - 2022-03-17
### Fixed
- avoid modifier except ctrl and shift to trigger the selection

## [1.3.7] - 2022-03-16
### Added
- Fix the source_node_id is None loop
- Add tests for graph supporting subport

## [1.3.6] - 2022-03-15
### Fixed
- Fix OM-46181 to consider edges from folded ports in the layout algorithm

## [1.3.5] - 2022-03-14
### Fixed
- The connection issue with RMB click. Clear the connection while mouse release.

## [1.3.4] - 2022-02-18
### Changed
- Fix OM-42502 about drag selection node so that as long as the selection rectangle touches the node, the node is selected

## [1.3.3] - 2022-02-18
### Changed
- Fix OM-45166 about the empty menu box in graph

## [1.3.2] - 2021-12-02
### Added
- The ability to use same side connections

## [1.3.1] - 2021-12-01
### Added
- Update graph when delegate is changed

## [1.3.0] - 2021-11-29
### Added
- GraphModelBatchPosition to simplify multiselection and backdrops

## [1.2.1] - 2021-11-12
### Fixed
- Graph model set size changed during iterating

## [1.2.0] - 2021-07-22
### Added
- GraphNodeLayout.HEAP node layout "put everything to ZStack"

## [1.1.3] - 2021-06-01
### Added
- New properties `preview_state` for the model

## [1.1.2] - 2021-05-12
### Fixed
- Port grouping in compound nodes

## [1.1.1] - 2021-05-05
### Added
- Multisilection (flag `rectangle_selection=True`)
- Ability to draw connections on top (flag `connections_on_top`)
- New properties `icon` and `preview` on the model
### Fixed
- Ability to set `display_color` on the model

## [1.1.0] - 2021-01-25
### Changed
- The signatures of the delegate API. There is no compatibility with the
  previous version.
### Added
- Port grouping
- Smooth scrolling

## [1.0.2] - 2020-10-30
### Added
- GraphView has the new property virtual_ports that disables virtual ports.
- New column node layout.
- Ability to make the ports colored depending on the type.
- Ability to check the port type before connection and stick the connection
  to the port if it can be accepted.
- Display color.
- IsolationGraphModel isolates any model to show the children of specific
  item only.

## [1.0.1] - 2020-10-14
- The ability to disable virtual ports
- Two-column node layout

## [1.0.0] - 2020-10-13
### Added
- CHANGELOG
- Node routing

### Changed
- The signature of `AbstractGraphNodeDelegate.connection`
