# Changelog

Omniverse Kit MDL UsdShade Editor

## [1.9.1] - 2025-09-03
### Fix
- OMPE-57951: Fix _window not used correctly after changing to MenuHelperExtensionFull

## [1.9.0] - 2025-09-01
### Changed
- OMPE-57951: Remove deprecated usage of omni.kit.get_editor_menu, use omni.kit.menu.utils instead.

## [1.8.23] - 2025-04-24
### Changed
- OMPE-45143: fix issue with creating compound nodes in referenced layers.

## [1.8.22] - 2025-04-08
### Changed
- Update documentation URL

## [1.8.21] - 2024-02-20
### Changed
- Add API function to register and unregister custom MDL nodes.

## [1.8.20] - 2025-02-14
### Changed
- added OmniSurface, OmniPBR, OmniHair, OmniSurfaceLite into mdl graph allowed list, so they can be initialized with inputs from scripts.

## [1.8.19] - 2024-10-02
### Changed
- OMPE-23881: add digital human color_correct and random_value modules to internal allow list.

## [1.8.18] - 2024-07-03
### Changed
- Another attempt to fix a flaky etm test.

## [1.8.17] - 2024-06-26
### Changed
- Attempt to fix fix etm tests by reworking framing logic.

## [1.8.16] - 2024-06-26
### Changed
- OMPE-13380: allow token->material connections.

## [1.8.15] - 2024-03-25
### Changed
- Revert of changes in 1.8.14.

## [1.8.14] - 2024-02-09
### Changed
- Cleanup of the MDL module loading.
- Switched to explicit USD identifiers read from the materialConfig userAllowList and userBlockList.
- Removed the support for wildcards which improves robustness and performance.

## [1.8.13] - 2023-11-13
### Fixed
- Fix a case "Open in MDL Material Graph" context menu on the material thumbnail did not open the material.

## [1.8.12] - 2023-09-18
### Fixed
- Do not cache texture-id for subsequent usage during app lifetime.

## [1.8.11] - 2023-09-18
- OM-108849, MDL range annotation: flatten Numpy arrays before converting to list.

## [1.8.10] - 2023-06-26
- Right-click "Open in MDL Material Graph" on the material thumbnail now opens corresponding material.

## [1.8.9] - 2023-06-26
- Ensure backdrop name is valid (ie spaces, non-alphanumeric chars)

## [1.8.8] - 2023-06-01
- OM-78704, update allowed type connections for Kit versions greather than 105.

## [1.8.7] - 2023-05-15
- Got rid of `force_regenerate = True` line that was unnecessary.

## [1.8.5] - 2023-04-27
- OM-89802, Fix ETM test failure due to menu-item removal.

## [1.8.4] - 2023-04-26
- Fix typo resulting in UsdUVTexture not being included in list of UsdPreviewSurface shaders.

## [1.8.3] - 2023-04-25
- Clean up node connection logic
- Create golden image for Kit < 105

## [1.8.2] - 2023-04-17
- Only permit UsdPreviewSurface nodes to connect to other UsdPreviewSurface nodes
- `MaterialGraphView.__serialize_positions`: skip invalid nodes.

## [1.8.1] - 2023-04-14
- Replace pause/resume icons.
- Update tool-tips for pause, resume and refresh buttons
- Add custom MaterialGraphView
- Refactor framing operations
- Remove hotkey for pause, resume
- Only activate pause for Kit vesrions > 105

## [1.8.0] - 2023-04-13
- Update for Python 3.10

## [1.7.4] - 2023-04-12
- Additional cyclical graph connection changes.
- Include hotkeys in tooltips

## [1.7.3] - 2023-04-05
- Fix focus when creating new materials and importing selected.

## [1.7.2] - 2023-04-04
- Add toolbar + mechanism to pause/resume shader compilation.
- Don't allow cyclical graph connections.
- Refator importing logic.
- Include "color" in the 3-component connection types if both nodes are UsdPreviewSurface.

## [1.7.1] - 2023-04-03
### Fixed
- Added better check for newest mouse position functions

## [1.7.0] - 2023-03-29
### Added
- Added actions and hotkeys for copy & paste in the graph
- Moved `_get_graph_view_hovered_position` out of GraphWidget, to graph_editor_core_widget.py

## [1.6.24] - 2023-03-28
### Fixed
- Don't close material graph on file save

## [1.6.23] - 2023-03-24
### Fixed
- Fix population of Quicksearch model.

## [1.6.22] - 2023-03-20
### Fixed
- Add support for range annotaions of compound types.

## [1.6.21] - 2023-03-16
### Fixed
- Added support for UsdPreviewSurface

## [1.6.20] - 2023-03-15
### Fixed
- Fixed "custom" material search paths were not read

## [1.6.19] - 2023-03-09
### Fixed
- Added missing omni.kit.material.library dependency

## [1.6.18] - 2023-02-25
### Fixed
- Update extension test so it passes in Usd 22.22
- Add tooltips to catalog items

## [1.6.17] - 2023-02-08
### Fixed
- Fixed "Add Compounds Directory" picked up wrong path
- Refresh compound lists after "Clear Compounds Directories"

## [1.6.16] - 2023-02-03
### Fixed
- Update MdlRegistry to use omni.client library for file operations

## [1.6.15] - 2023-01-24
### Fixed
- Remove setting of shader property order by NewUsdShadeNodeCommand
- use helper function to get stage via UsdShadeGraphModel update_dirty() method

## [1.6.14] - 2023-01-05
### Fixed
- Fixed errors in test in 105.

## [1.6.13] - 2023-01-04
### Fixed
- Update code in MdlRegistry.load_mdl_function to use pymdlsdk.IFunction_definition.Semantics.DS_UNKNOWN for Kit version > 104

## [1.6.12] - 2022-12-07
### Fixed
- The window turns to black when it is closed when it's moved to become an external window

## [1.6.11] - 2022-11-19
### Changed
- Fixed error in UsdShadeGraphModel.type() due to undeclarted variable.

## [1.6.10] - 2022-11-17
### Changed
- Fixed error condition when extension version is dynamically changed via Create extension manager.

## [1.6.9] - 2022-11-04
### Changed
- Update caching mechanism in UsdShadeGraphModel class

## [1.6.8] - 2022-11-02
### Changed
- Refector path gathering code so that the search paths are regengerated upon reload.

## [1.6.7] - 2022-10-20
### Changed
- Fix CompoundRegistrySubscription del() method
- Don't process empty paths.

## [1.6.6] - 2022-10-15
### Changed
- use Neuray to gather search paths
- use rtx_scope database

## [1.6.5] - 2022-10-11
### Changed
- the material-graph, now considers user paths to be the paths stored in "/materialConfig/searchPaths/local" + whatever get_mdl_user_paths() returns
- remove user paths from built-in paths
- modules no longer need to be in mdl directory

## [1.6.4] - 2022-10-06
### Changed
- Wait until graph is visible before populating the MDLRegistry
- Use Neuray to get MDL user paths
- If the userAllowList has been set in the config, clear the default userBlockList

## [1.6.3] - 2022-10-04
### Changed
- Gather mdl module allow/block lists from carb.settings
- Don't display nodes that have been explictly hidden in the material-graph
- Hide material mdl ports for Material-X based materials.

## [1.6.2] - 2022-10-03
### Changed
- Changed warning to info when hotkeys can't be loaded.

## [1.6.1] - 2022-09-29
### Added
- Use mdl simplename if as subidentifier if mdl function is not overloaded.
- Cache UsdShadeGraphModel.type property lookups.

## [1.6.0] - 2022-09-23
### Added
- Added Actions for common functions, and hotkeys to many of those Actions

## [1.5.8] - 2022-09-01
### Changed
- Parse MDL directly vs using JSON

## [1.5.7] - 2022-08-18
### Changed
- The name of graph entry button from `Import` to `Open`

## [1.5.6] - 2022-07-27
### Fixed
- Can't get type for object of unknown type when query description

## [1.5.5] - 2022-07-25
### Changed
- Fix broken compounds import function.  OM-052380
- Ensure xformOpOrder property is removed when importing compounds

## [1.5.4] - 2022-07-21
### Changed
- Fix broken compounds import function.  OM-052380
- Add custom metadate to file_texture brightness and contrast parameters.

## [1.5.3] - 2022-07-19
### Changed
- Ensure material prim updates if any of the child prim info* properties change.  OM-38232

## [1.5.2] - 2022-07-19
### Changed
- When connecting a parameter to a Nodegraph input port, copy that parameters metadata to the input port as well. OM-38653

## [1.5.1] - 2022-07-18
### Changed
- Fix broken Nodegraph and Material export function.  OM-052380

## [1.5.0] - 2022-05-23
### Changed
- Moved CreateUsdUIBackdropCommand, UsdUINodeGraphNodeSetCommand and UsdUIRemovePositionCommand to omni.kit.graph.usd.commands

## [1.4.11] - 2022-05-06
### Fixed
- Error when removing grouped port

## [1.4.10] - 2022-04-01
### Added
- Ability to connect material to token

## [1.4.9] - 2022-03-30
### Changed
update repo_build and repo-licensing

## [1.4.8] - 2022-03-18
### Fixed
- Issue of deleting graph's parent making the graph crash

## [1.4.7] - 2023-02-21
### Changed
- Using new exclusive API for the quick search model
- Changes in the catalog delegate to fix artifacts in quick search

## [1.4.6] - 2021-11-04
- Added create menu item "Create MDL Graph"

## [1.4.5] - 2021-10-26
- Removed compounds

## [1.4.4] - 2021-10-26
- update extension.toml

## [1.4.3] - 2021-08-10
### Added
- Icons for OmniHairBase, OmniSurfaceBase, OmniSurfaceBlend, OmniSurfaceLiteBase

## [1.4.2] - 2021-07-30
### Fixed
- Ensure extension gets fully cleaned up when unloaded, no dangling references

## [1.4.1] - 2021-07-19
### Added
- OmniSurfaceBlendBase and OmniHairBase
### Fixed
- sub-identifiers should be short if possible

## [1.4.0] - 2021-07-09
### Changed
- Update the dependencies due to the separation of omni.kit.widget.material_preview from omni.kit.window.material_preview

## [1.3.0] - 2021-06-30
### Fixed
- Ability to connect shaders with material output type created outside of
  Material Graph
- Added `mdl` render context to created materials
- Fixed colorspace attribute on bitmap nodes
- Fixed OmniSurfaceLiteBase
- Fixed the type of the created `Looks` prim
- Fixed undo when creating connections
### Changed
- Disabled Live Preview

## [1.2.20] - 2021-06-16
### Changed
- Added "Export NodeGraph" and "Export Material" menu options
- Requires omni.kit.widget.stage version 2.5.0 or greater

## [1.2.19] - 2021-06-15
- Add feature flag

## [1.2.18] - 2021-06-04
### Changed
- Using omni.kit.graph.editor.core
- Renamed to "Material Graph"

## [1.2.17] - 2021-06-01
### Added
- Live preview for the material nodes

## [1.2.16] - 2021-05-26
### Changed
- Swapped icons
### Added
- OmniSurfaceBase
- OmniSurfaceBaseLite

## [1.2.15] - 2021-05-29
### Added
- API to show materials in Material Editor window

## [1.2.14] - 2021-05-26
### Changed
- The start screen has nice buttons
- The window name is "Material Editor"
- Added more implicit conversion types
- Show start screen when editable material is removed

## [1.2.13] - 2021-05-19
### Fixed
- QuickSearch exception
### Added
- The ability to drag and drop from outside of Kit

## [1.2.12] - 2021-05-19
### Fixed
- Clear All
- QuickSearch Enter key
### Removed
- OmniPBR materials
### Added
- Ability to drop files from content browser
- Missing icons and colors
- Clear button to the search pannel
- Tooltip background

## [1.2.11] - 2021-05-17
### Changed
- Icons and colors
- Removed sections from QuickSearch
### Added
- Panel with New and Import buttons

## [1.2.10] - 2021-05-12
### Added
- Rename in place

## [1.2.9] - 2021-05-12
### Fixed
- Compounds on Kit 101
### Added
- All texture_return nodes are replaced with compounds

## [1.2.8] - 2021-05-11
### Added
- More colors for ports
- Type to the left pannel
### Fixed
- Connections to the materials
- Color of ports when using display_color

## [1.2.7] - 2021-05-11
### Added
- QuickSearch priority 0 puts the shaders on the top
- Fixed moving inside the compound
- Fixed scrolling the full window (need omni.ui 2.1.7)
- Using MDL types for inputs and outputs (including can_connect)
- Clear All context menu
- Image Tooltip
### Changed
- Icons
- Left pannel is on by default
- Tooltip with MDL signature
- New formula for the node background-color

## [1.2.4] - 2021-05-06
### Changed
- Design improvements
### Added
- Multiselection
- Set of compounds
### Fixed
- Backdrop color

## [1.2.3] - 2021-04-27
### Changed
- Changed "info:sourceAsset:subIdentifier" to "info:mdl:sourceAsset:subIdentifier"

## [1.2.2] - 2021-04-01
### Changed
- Added drag & drop from stage window

## [1.2.1] - 2021-04-01
### Changed
- Left pannel searches in tags
- Fixed icons
- Using short name as MDL identifier (requested by Lutz)
- Fixed F key
- Copy metadata when creating input port in NodeGraph
- Added Material node to left pannel
- Connected ports are removed when the node is deleted
- Renaming port updates Property window

## [1.2.0] - 2021-03-19
### Added
- Ability to save compound to the external file
- Ability to import compounds to the left panel
- Create meterial when the model is empty

## [1.1.2] - 2021-03-15
### Added
- Added stage widget context menu for open in material editor

## [1.1.1] - 2021-02-10
### Added
- Model for Quick Search with all the available materials.

## [1.1.0] - 2021-01-25
### Changed
- The signatures of the delegate API. There is no compatibility with the
  previous version.
### Added
- Support for Display Group metadata of USD Property
### Fixed
- Creating the second widget of the same type

## [1.0.2] - 2020-10-30
### Added
- `omni.kit.window.graph` is renamed to `omni.kit.window.material_graph`
- Included MDL description of the main shaders
- Support for UsdUIBackdrop
- Support for UsdShadeNodeGraph

### Changed
- Using TfNotice to watch the stage

## [1.0.1] - 2020-10-14

## [1.0.0] - 2020-10-13
### Added
- Initial Material Editor that uses omni.kit.widget.graph
- The ability to create nodes with drag and drop
- Using json files as database of MDL functions
