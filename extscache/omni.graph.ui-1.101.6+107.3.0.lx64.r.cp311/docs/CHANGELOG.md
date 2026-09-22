(changelog_omni_graph_ui)=

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.101.6] - 2025-05-13
### Changed
- update golden images for omni.graph.ui due to omni.ui Intdrag fix

## [1.101.5] - 2025-04-25
### Fixed
- Input token fields not accepting changes.
### Changed
- Use omni.kit.property.usd.AllowedTokenItem instead of or as base of custom AllowedTokenItem classes.

## [1.101.4] - 2025-02-20
### Changed
- Replaced omni.kit.window.viewport with omni.kit.viewport window in test dependencies.

## [1.101.3] - 2025-01-15
### Changed
- Copied decompose_test_list() and supporting methods from omni.kit.test as it has been deprecated there and is being removed.

## [1.101.2] - 2024-12-17
### Fixed
- Visual Scripting menu not appearing in the viewport context menu.

## [1.101.1] - 2024-12-16
### Changed
- Remove test dependencies which are already included.

## [1.101.0] - 2024-12-16
### Changed
- Changed fabric graph backing default from 'shared' to 'private' (ie. 'stage-without-history')

## [1.100.0] - 2024-11-18
### Changed
- Build with Kit 107.0 with USD 24.05 and python 3.11
- Jumping versions for 107 to leave room for changes to 106.*-based builds.

## [1.91.0] - 2024-11-28
### Changed
- Updated tests for nodes with new layer identifier inputs.
- Added UI templates for nodes with layer identifier inputs.

## [1.90.3] - 2024-10-23
### Changed
- Removed dependency on omni.debugdraw

## [1.90.2] - 2024-10-21
### Changed
- Updated tests for RandomNumeric/Gaussian for type resolution + range.

## [1.90.1] - 2024-10-03
### Changed
- Adjust test to use omni.graph.nodes.BundleConstructor

## [1.90.0] - 2024-09-19
### Changed
- bumping version to make room for 106.2-based extensions

## [1.80.2] - 2024-08-27
### Changed
- Fix deprecated module imports

## [1.80.1] - 2024-08-21
### Added
- omni.kit.window.file_importer to test dependencies.

## [1.80.0] - 2024-08-09
### Changed
- bumping version to make room for 106-based extensions

## [1.69.1] - 2024-07-19
### Changed
- OMPE-14122: Removed featured flag

## [1.69.0] - 2024-06-18
### Changed
- Remove node-descripion-editor UI code and menu entries

## [1.68.2] - 2024-06-17
### Changed
- Fix reference to BundleConstructor

## [1.68.1] - 2024-06-06
### Fixed
- Property Window build functions which were not returning their value models.

## [1.68.0] - 2024-05-30
### Changed
- Updated the formatting
- Made omni.inspect optional

## [1.67.0] - 2024-05-17
### Added
- Update the 'support_level' entry in the configuration files to match the release requirements

## [1.66.1] - 2024-04-17
### Added
- Add a 'support_level' entry to the configuration file of the extensions

## [1.66.0] - 2024-04-10
### Changed
- Bumped dependency on omni.graph to version 1.139.0
- Bumped dependency on omni.graph.core to version 2.177.1

## [1.65.3] - 2024-04-08
### Changed
- Removed dependency on stage_templates.

## [1.65.2] - 2024-04-04
### Changed
- Add omni.kit.window.file_importer to fix test

## [1.65.1] - 2024-03-19
### Changed
- Updated omni.kit.context_menu to omni.kit.widget.context_menu

## [1.65.0] - 2024-03-18
### Changed
- Bumped dependency on omni.graph.core to version 2.176.3
- Bumped dependency on omni.graph to version 1.138.1

## [1.64.0] - 2024-02-15
### Changed
- Bumped dependency on omni.graph.core to version 2.174.2

## [1.63.0] - 2024-02-05
### Changed
- Bumped dependency on omni.graph to version 1.138.0
- Bumped dependency on omni.graph.core to version 2.174.0

## [1.62.0] - 2024-01-31
### Changed
- Bumped dependency on omni.graph to version 1.137.0
- Bumped dependency on omni.graph.core to version 2.171.1

## [1.61.0] - 2024-01-30
### Changed
- Bumped dependency on omni.graph to version 1.136.1
- Bumped dependency on omni.graph.core to version 2.170.1

## [1.60.1] - 2024-01-29
### Changed
- Add unit tests for context menu

## [1.60.0] - 2024-01-23
### Changed
- Bumped dependency on omni.graph to version 1.136.0

## [1.59.1] - 2024-01-19
### Fixed
- Template tests now fix the scroll position

## [1.59.0] - 2024-01-18
### Added
- Test images for graph.io nodes
### Changed
- Bumped dependency on omni.graph.core to version 2.169.1
- Bumped dependency on omni.graph to version 1.135.1

## [1.58.1] - 2024-01-13
### Fixed
- Repository URL in config file.

## [1.58.0] - 2024-01-12
### Fixed
- Made the OmniGraph extension pane work for new and old variations of nodes.json
### Changed
- Bumped dependency on omni.graph to version 1.134.7
- Bumped dependency on omni.graph.core to version 2.169.0

## [1.57.3] - 2024-01-12
### Changed
- Fix build warnings

## [1.57.2] - 2024-01-11
### Changed
- Fix for test_target_attribute_browse, test_target_attribute

## [1.57.1] - 2024-01-09
### Changed
- Fix failure of test_extended_attributes in some cases

## [1.57.0] - 2023-12-28
### Changed
- Bumped dependency on omni.graph.core to version 2.167.0
- Bumped dependency on omni.graph to version 1.134.2

## [1.56.2] - 2023-12-19
### Changed
- Remove node description editor from py coverage

## [1.56.1] - 2023-12-18
### Fixed
- Setting attr values through the Property Window sometimes don't fire attribute changed callbacks.

## [1.56.0] - 2023-12-18
### Changed
- Bumped dependency on omni.graph.core to version 2.166.0
- Bumped dependency on omni.graph to version 1.134.0

## [1.55.1] - 2023-12-14
### Changed
- Fix spelling error in documentation

## [1.55.0] - 2023-12-12
### Fixed
- Typo of representation
### Changed
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph to version 1.133.2

## [1.54.0] - 2023-12-11
### Changed
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph to version 1.133.2

## [1.53.1] - 2023-12-08
### Fixed
- lint error caused by auto-formatter.

## [1.53.0] - 2023-12-08
### Added
- StandaloneAttributeBuilder and ComputeNodeWidgetUtils classes, allowing OG Property Window widgets to be used outside the Property Window.
### Fixed
- Exception if Fabric Debug button clicked when omni.fabric.fabric_inspector extension not enabled.

## [1.52.3] - 2023-12-08
### Changed
- Updated golden images for Minimum and Maximum nodes.

## [1.52.2] - 2023-11-15
### Changed
- Adjust ConstructArray property panel for union attributes

## [1.52.1] - 2023-11-15
### Added
- Updated golden images for AppendArray.

## [1.52.0] - 2023-10-31
### Changed
- Update golden images for new nodes.

## [1.51.0] - 2023-10-26
### Changed
- Moved tests from omni.graph.ui_nodes

## [1.50.3] - 2023-10-25
### Changed
- Add support for older compound schemas

## [1.50.2] - 2023-10-19
### Changed
- Token array editing will properly work with extended attributes and allowed tokens

## [1.50.1] - 2023-10-19
### Changed
- Fix target mapping with the relationship builder

## [1.50.0] - 2023-10-18
### Added
- Display target mapped items in the property panel

## [1.49.3] - 2023-10-18
### Changed
- Fixup compound node type schema property handler to use latest schema

## [1.49.2] - 2023-10-17
### Changed
- Added property UI for Quatd|f|h and Matrix4d

## [1.49.1] - 2023-10-11
### Changed
- Don't require omni.kit.window.extensions. Only enable the bits which use it if it's already loaded.

## [1.49.0] - 2023-10-09
### Changed
- Adding UI template for conversion nodes that allow role specification

## [1.48.0] - 2023-10-06
### Changed
- re-enable tests

## [1.47.0] - 2023-10-05
### Added
- Support for input and output api on compound node type graphs

## [1.46.11] - 2023-09-19
### Changed
- fix context menu misalignment issue

## [1.46.10] - 2023-09-07
### Changed
- update all instances when a variable is renamed

## [1.46.9] - 2023-09-06
### Changed
- Replaced VariableNameModel as VariableNameListModel

## [1.46.8] - 2023-08-29
### Changed
- Replaced use of pyclip with the native kit clipboard

## [1.46.7] - 2023-08-25
### Changed
- Fixed write to target flag

## [1.46.6] - 2023-08-19
### Added
- Missing extension icon

## [1.46.5] - 2023-08-14
### Changed
- Moved omni.graph.ui from Kit to the OmniGraph repo

## [1.46.4] - 2023-07-27
### Removed
- Test that requires omni.graph.ui_nodes to work - moved to the downstream repo with that extension

## [1.46.3] - 2023-07-13
### Removed
- Removed the "defaultEvaluator" and "useCachedConnectionsForFileLoad" OG settings.

## [1.46.2] - 2023-06-27
### Fixed
- Fixed some documentation nits

## [1.46.1] - 2023-06-12
### Changed
- Fixed one deprecated ogt.OmniGraphExtension reference which was missed.

## [1.46.0] - 2023-06-08
### Changed
- Remove widget for input bundle

## [1.45.3] - 2023-06-08
### Changed
- Replaced load-time dependency on omni.kit.window.tests with a runtime dependency

## [1.45.2] - 2023-05-29
### Changed
- Replaced deprecated calls with supported versions

## [1.45.1] - 2023-05-26
### Added
- Added test for layer identifier property widget.

## [1.45.0] - 2023-05-23
### Removed
- Removed OG settings that were referencing now-removed constructs (dynamic scheduler and realm static scheduler).

## [1.44.2] - 2023-05-17
### Changed
- Updated tests to work with ReadPrimsV2 node.

## [1.44.1] - 2023-05-17
### Fixed
- read/write prim attribute name widget shows graph attributes when targeting instanced prim

## [1.44.0] - 2023-05-11
### Added
- OmniGraphTfTokenNoAllowedTokensModel to handle tokens as asset-paths
### Changed
- OG property panel widgets now commit changes on end-edit instead of every change for string/token

## [1.43.0] - 2023-05-08
### Deprecated
- Removed deprecated locations of Python modules

## [1.42.1] - 2023-05-05
### Changed
- Updated `ReadPrims` related tests during to node inputs changes.

## [1.42.0] - 2023-05-04
### Changed
- Filter out problematic event types in on_graph_event

## [1.41.0] - 2023-04-26
### Changed
- Fix wording of bundle/target tooltip
- Fix unresolved attribute label

## [1.40.3] - 2023-04-24
### Changed
- Read/WritePrimAttribute nodes will find attribute names when prim or primPath is connected

## [1.40.2] - 2023-04-24
### Fixed
- Replaced deprecated call to get_elem_count

## [1.40.1] - 2023-04-21
### Fixed
- target property widget without template

## [1.40.0] - 2023-04-20
### Added
- Reset menu item for type-conversion menu

## [1.39.0] - 2023-04-17
### Changed
- target attributes now show instancing target path as relative to symbol

## [1.38.5] - 2023-04-12
### Changed
- Created template class for nodes with prim/primPath structure
- Changed bundle buttons in UI to say "Bundle(s)"

## [1.38.4] - 2023-04-11
### Fixed
- Prim node template allows text editing when non-valid prim is selected

## [1.38.3] - 2023-04-11
### Removed
- Removed node documentation TODO which is no longer relevant

## [1.38.2] - 2023-04-03
### Fixed
- Fixed incorrect object in template
### Added
- Added test for property window output extended attributes

## [1.38.1] - 2023-04-03
### Changed
- Added timcode to read/write prim Inputs group
- Name consistency pass

## [1.38.0] - 2023-04-03
### Added
- Support for picking graph-instancing-target

## [1.37.4] - 2023-03-31
### Changed
- output and state target attributes show values not target inputs
- Relationship attributes now are sorted into thier respective port display group

## [1.37.3] - 2023-03-30
### Changed
- Target widget shows as readonly when port is connected

## [1.37.2] - 2023-03-24
### Fixed
- Fix no len() exception when showing Quat attributes

## [1.37.1] - 2023-03-24
### Changed
- Graph instance variable now show warning when there is a type mismatch

## [1.37.0] - 2023-03-24
### Changed
- Updated Camera, picking nodes to use new target type for prim input
### Fixed
- Fixed ReadPrimAttributes property panel throwing errors

## [1.36.0] - 2023-03-24
### Added
- New button to access the Fabric inspector
### Removed
- Obsolete flags for dumping Fabric data from the graph

## [1.35.2] - 2023-03-16
### Added
- "threadsafe" scheduling hints to OgnGetCameraPosition, OgnGetCameraTarget, OgnOnPicked, OgnOnViewportClicked, OgnOnViewportDragged, OgnOnViewportHovered, OgnOnViewportPressed, OgnOnViewportScrolled, OgnReadMouseState, OgnReadPickState, OgnReadViewportClickState, OgnReadPickState, OgnReadViewportClickState, OgnReadViewportDragState, OgnReadViewportHoverState, OgnReadViewportPressState, and OgnReadViewportScrollState nodes.
- "usd-write" scheduling hint to OgnSetViewportFullscreen node.

## [1.35.1] - 2023-03-09
### Fixed
- Check component index is valid when comparing values

## [1.35.0] - 2023-03-10
### Changed
- Moved all nodes out of this extension, into omni.graph.ui_nodes

## [1.34.3] - 2023-03-09
### Added
- Change default index for static version of internal state to be the authoring graph
- Add wrappers for shared and per-instance state query functions

## [1.34.2] - 2023-03-08
### Fixed
- Fix exception when bringing up the attribute context menu on a non-node attribute.

## [1.34.1] - 2023-03-06
### Fixed
- Fix exceptions from property widget when multi-selecting certain node types

## [1.34.0] - 2023-03-06
### Changed
- Removed the warning about nodes being incompatible with instancing

## [1.33.2] - 2023-02-28
### Fixed
- OmniUiTest-based tests close any stages they open to avoid dangling graph references which crash on exit.

## [1.33.1] - 2023-02-25
### Changed
- Modifed format of Overview to be consistent with the rest of Kit

## [1.33.0] - 2023-02-24
### Added
- build_port_type_convert_menu
- property panel context menu for converting extended types

## [1.32.1] - 2023-02-22
### Added
- Links to JIRA tickets regarding filling in the missing documentation

## [1.32.0] - 2023-02-21
### Changed
- Added usdWriteBack to WritePrimAttribute

## [1.31.4] - 2023-02-21
### Changed
- Change ComputeNodeWidget label to reflect node type

## [1.31.3] - 2023-02-20
### Changed
- Made the interfaces subproject unique to omni.graph.ui

## [1.31.2] - 2023-02-19
### Changed
- Added label to the main doc page so that higher level docs can reference the extension
- Tagged for adding links to node documentation

## [1.31.1] - 2023-02-05
### Added
- Add property filter support

## [1.31.0] - 2023-02-15
### Changed
- unconnected token input arrays can be edited with property panel
### Fixed
- Don't error on default value of NaN for float inputs

## [1.30.2] - 2023-02-13
### Changed
- Runtime initialization for the `inputs:renderer` attribute of `OgnSetViewportRenderer`

## [1.30.1] - 2023-02-10
### Changed
- Correct namespace of `OgnSetViewportFullscreen`

## [1.30.0] - 2023-02-09
### Added
- Added `OgnSetViewportFullscreen`
- Added `OgnSetViewportRenderer` and `OgnGetViewportRenderer`
- Added `OgnSetViewportResolution` and `OgnGetViewportResolution`

## [1.29.3] - 2023-02-06
### Fixed
- Bug in property panel when setting resolved attribute values

## [1.29.2] - 2023-02-02
### Fixed
- Lint error that appeared when pylint updated

## [1.29.1] - 2023-01-30
### Changed
- Removed the kit-sdk landing page
- Moved all of the documentation into the new omni.graph.docs extension

## [1.29.0] - 2023-01-11
### Changed
- ABI calls to take into account instancing
- Changes related to introduction of native vectorization in core

## [1.28.4] - 2022-12-28
### Changed
- Changed the way errors and warnings are surfaced to OgnReadWidgetProperty/OgnWriteWidgetProperty

## [1.28.3] - 2022-12-07
### Fixed
- Make sure variable colour widgets use AbstractItemModel

## [1.28.2] - 2022-12-05
### Fixed
- Fixed tab not working on variable vector fields

## [1.28.1] - 2022-12-05
### Fixed
- Fixed UI update issues with graph variable widgets

## [1.28.0] - 2022-11-24
### Removed
- Widget controlling the deleted setting useSchemaPrims

## [1.27.0] - 2022-11-17
### Removed
- Widget controlling the deleted settings updateToUSD, useLegacySimulationPipeline and enableUSDInPreRender

## [1.26.0] - 2022-11-12
### Removed
- Widget controlling the deleted implicit global graph setting

## [1.25.0] - 2022-11-02
### Added
- Display initial and runtime values of graph variables

## [1.24.1] - 2022-10-28
### Fixed
- Undo on node attributes

## [1.24.0] - 2022-10-20
### Added
- Custom Property Panel for OmniGraphCompoundNodeType schema Prims

## [1.23.0] - 2022-09-28
### Added
- Widget for reporting timing information related to extension processing by OmniGraph

## [1.22.2] - 2022-09-19
### Added
- Use id paramteter for Viewport picking request so a node will only generate request.

## [1.22.1] - 2022-09-09
### Added
- Instance variable properties remove underlying attribute when reset to default

## [1.22.0] - 2022-08-31
### Changed
- Added OmniGraphAttributeModel to public API

## [1.21.1] - 2022-08-19
### Changed
- Added OnVariableChange to the list of instancing-compatible ndoes

## [1.21.0] - 2022-08-19
### Added
- UI for controlling new setting that turns deprecations into errors

## [1.20.1] - 2022-08-17
### Changed
- Refactored scene frame to be widget-based instead of monolithic

## [1.20.0] - 2022-08-16
### Fixed
- Modified the import path acceptance pattern to adhere to PEP8 guidelines
- Fixed hot reload for the editors by correctly destroying menu items
- Added FIXME comments recommended in a prior review
### Added
- Button for Save-As to support being able to add multiple nodes in a single session

## [1.19.0] - 2022-08-11
### Added
- ReadWindowSize node
- 'widgetPath' inputs to ReadWidgetProperty, WriteWidgetProperty and WriteWidgetStyle nodes.
### Changed
- WriteWidgetStyle now reports the full details of style sytax errors.

## [1.18.1] - 2022-08-10
### Fixed
- Applied formatting to all of the Python files

## [1.18.0] - 2022-08-09
### Changed
- Removed unused graph editor modules
- Removed omni.kit.widget.graph and omni.kit.widget.fast_search dependencies

## [1.17.1] - 2022-08-06
### Changed
- OmniGraph(API) references changed to 'Visual Scripting'

## [1.17.0] - 2022-08-05
### Added
- Mouse press gestures to picking nodes

## [1.16.4] - 2022-08-05
### Changed
- Fixed bug related to parameter-tagged properties

## [1.16.3] - 2022-08-03
### Fixed
- All of the lint errors reported on the Python files in this extension

## [1.16.2] - 2022-07-28
### Fixed
- Spurious error messages about 'Node compute request is ignored because XXX is not request-driven'

## [1.16.1] - 2022-07-28
### Changed
- Fixes for OG property panel
- compute_node_widget no longer flushes prim to FC

## [1.16.0] - 2022-07-25
### Added
- Viewport mouse event nodes for click, press/release, hover, and scroll
### Changed
- Behavior of drag and picking nodes to be consistent

## [1.15.3] - 2022-07-22
### Changed
- Moving where custom metadata is set on the usd property so custom templates have access to it

## [1.15.2] - 2022-07-15
### Added
- test_omnigraph_ui_node_creation()
### Fixed
- Missing graph context in test_open_and_close_all_omnigraph_ui()
### Changed
- Set all of the old Action Graph Window code to be omitted from pyCoverage

## [1.15.1] - 2022-07-13
- OM-55771: File browser button

## [1.15.0] - 2022-07-12
### Added
- OnViewportDragged and ReadViewportDragState nodes
### Changed
- OnPicked and ReadPickState, most importantly how OnPicked handles an empty picking event

## [1.14.0] - 2022-07-08
### Fixed
- ReadMouseState not working with display scaling or multiple workspace windows
### Changed
- Added 'useRelativeCoordinates' input and 'window' output to ReadMouseState

## [1.13.0] - 2022-07-08
### Changed
- Refactored imports from omni.graph.tools to get the new locations
### Added
- Added test for public API consistency

## [1.12.0] - 2022-07-07
### Changed
- Overhaul of SetViewportMode
- Changed default viewport for OnPicked/ReadPickState to 'Viewport'
- Allow templates in omni.graph.ui to be loaded

## [1.11.0] - 2022-07-04
### Added
- OgnSetViewportMode.widgetPath attribute
### Changed
- OgnSetViewportMode does not enable execOut if there's an error

## [1.10.1] - 2022-06-28
### Changed
- Change default viewport for SetViewportMode/OnPicked/ReadPickState to 'Viewport Next'

## [1.10.0] - 2022-06-27
### Changed
- Move ReadMouseState into omni.graph.ui
- Make ReadMouseState coords output window-relative

## [1.9.0] - 2022-06-24
### Added
- Added PickingManipulator for prim picking nodes controlled from SetViewportMode
- Added OnPicked and ReadPickState nodes for prim picking

## [1.8.5] - 2022-06-17
### Added
- Added instancing ui elements

## [1.8.4] - 2022-06-07
### Changed
- Updated imports to remove explicit imports
- Added explicit generator settings

## [1.8.3] - 2022-05-24
### Added
- Remove dependency on Viewport for Camera Get/Set operations
- Run tests with omni.hydra.pxr/Storm instead of RTX

## [1.8.2] - 2022-05-23
### Added
- Use omni.kit.viewport.utility for Viewport nodes and testing.

## [1.8.1] - 2022-05-20
### Fixed
- Change cls.default_model_table to correctly set model_cls in _create_color_or_drag_per_channel
 for vec2d, vec2f, vec2h, and vec2i omnigraph attributes
- Infer default values from type for OG attributes when not provided in metadata

## [1.8.0] - 2022-05-05
### Added
- Support for enableLegacyPrimConnections setting, used by DS but deprecated
### Fixed
- Tooltips and descriptions for settings that are interdependent

## [1.7.1] - 2022-04-29
### Changed
- Made tests derive from OmniGraphTestCase

## [1.7.0] - 2022-04-26
### Added
- GraphVariableCustomLayout property panel widget moved from omni.graph.instancing

## [1.6.1] - 2022-04-21
### Fixed
- Some broken and out of date tests.

## [1.6.0] - 2022-04-18
### Changed
- Property Panel widget for OG nodes now reads attribute values from Fabric backing instead of USD.

## [1.5.0] - 2022-03-17
### Added
- Added _add\_create\_menu\_type_ and _remove\_create\_menu\_type_ functions to allow kit-graph extensions to add their corresponding create graph menu item
### Changed
- _Menu.create\_graph_ now return the wrapper node, and will no longer pops up windows
- _Menu_ no longer creates the three menu items _Create\Visual Sciprting\Action Graph_, _Create\Visual Sciprting\Push Graph_, _Create\Visual Sciprting\Lazy Graph_ at extension start up
- Creating a graph now will directly create a graph with default title and open it

## [1.4.4] - 2022-03-11
### Added
- Added glyph icons for menu items _Create/Visual Scripting/_ and items under this submenu
- Added Create Graph context menu for viewport and stage windows.

## [1.4.3] - 2022-03-11
### Fixed
- Node is written to backing store when the custom widget is reset to ensure that view is up to date with FC.

## [1.4.2] - 2022-03-07
### Changed
- Add spliter for items in submenu _Window/Visual Scripting_
- Renamed menu item _Create/Graph_ to _Create/Visual Scripting_
- Changed glyph icon for _Create/Visual Scripting_ and added glyph icons for all sub menu items under

## [1.4.1] - 2022-02-22
### Changed
- Change _Window/Utilities/Attribute Connection_, _Window/Visual Scripting/Node Description Editor_ and _Window/Visual Scripting/Toolkit_ into toggle buttons
- Added OmniGraph.svg glyph for _Create/Graph_

## [1.4.0] - 2022-02-16
### Changes
- Decompose the original OmniGraph menu in toolbar into several small menu items under correct categories

## [1.3.0] - 2022-02-10
### Added
- Toolkit access to the setting that uses schema prims in graphs, and a migration tool for same

## [1.2.2] - 2022-01-28
### Fixed
- Potential crash when handling menu or stage changes

## [1.2.1] - 2022-01-21
### Fixed
- ReadPrimAttribute/WritePrimAttribute property panel when usePath is true

## [1.2.0] - 2022-01-06
### Fixed
- Property window was generating exceptions when a property is added to an OG prim.

## [1.1.0] - 2021-12-02
### Changes
- Fixed compute node widget bug with duplicate graphs

## [1.0.2] - 2021-11-24
### Changes
- Fixed compute node widget to work with scoped graphs
## [1.0.1] - 2021-02-10
### Changes
- Updated StyleUI handling

## [1.0.0] - 2021-02-01
### Initial Version
- Started changelog with initial released version of the OmniGraph core
