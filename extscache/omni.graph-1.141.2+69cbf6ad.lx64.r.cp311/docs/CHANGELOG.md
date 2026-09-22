(changelog_omni_graph)=

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.141.2] - 2025-05-01
### Changed
- Prepare for Python-3.12

## [1.141.1] - 2025-04-15
### Fixed
- OMPE-43816: ensured some extension enable/disable hook objects are cleaned up.

## [1.141.0] - 2024-12-04
### Changed
- Graphs are now created by default using their own private fabric backing

## [1.140.2] - 2024-11-08
### Fixed
- Python callbacks not registered to the node on reload

## [1.140.1] - 2024-09-10
### Fixed
- Fix security issues (OMPE-18747).

## [1.140.0] - 2024-04-22
### Added
- Added python bindings for the CUDA device ID used by OmniGraph.

## [1.139.1] - 2024-04-18
### Fixed
- Usage of Python objects without the GIL held.

## [1.139.0] - 2024-03-18
### Fixed
- Added bypass for errors that only affect the docs build

## [1.138.1] - 2024-02-26
### Changed
- OnConnectionTypeResolved tests now test for dynamic attribute removal

## [1.138.0] - 2024-01-31
### Added
- og.Graph.CURRENT_FILE_FORMAT_VERSION constant
- og.FileFormatVersion >= and <= operators

## [1.137.0] - 2024-01-26
### Fixed
- Handling of node types that were unloaded when gathering extension information

## [1.136.1] - 2024-01-22
### Changed
- OM-115843 Removed unnecessary clear during bundle copy.

## [1.136.0] - 2024-01-18
### Added
- og.ObjectLookup.compound_graph and og.ObjectLookup.compound_node

## [1.135.1] - 2024-01-15
### Added
- Extra terminology links for documentation

## [1.135.0] - 2024-01-15
### Fixed
- Restore timecode to be automatically converted to double.

## [1.134.8] - 2024-01-11
### Changed
- OM-115855 Improve code coverage for bundles, complete line coverage

## [1.134.7] - 2024-01-10
### Changed
- OM-115855 Improve code coverage for bundles, exclude unsupported code and add unit tests

## [1.134.6] - 2023-12-29
### Changed
- Added additional test coverage
### Fixed
- generate_ogn no longer accesses invalid constants

## [1.134.5] - 2023-12-28
### Changed
- Fix setup cases in test code from previous test

## [1.134.4] - 2023-12-27
### Changed
- Added argument to test utils to reset the stage only when necessary

## [1.134.3] - 2023-12-20
### Changed
- Added additional test coverage

## [1.134.2] - 2023-12-16
### Changed
- Avoid exception and string conversion in extract_attribute_type_information for performance.

## [1.134.1] - 2023-12-15
### Changed
- Controller: Skip evaluating the pre and post render graphs and raise error when invoked explicitly.
- Controller: Raise error when evaluating a graph that does not exist.

## [1.134.0] - 2023-12-11
### Added
- Binding for setting custom fabric backing on target mapped attribute

## [1.133.2] - 2023-12-08
### Fixed
- og.Attribute.resolve_partially_coupled_attribute allows 'None' list arguments

## [1.133.1] - 2023-12-07
### Fixed
- Fixed OmniGraph upgrade code not triggering when Fabric Scene Delegate is enabled

## [1.133.0] - 2023-11-29
### Changed
- Deprecated binding of deprecated core ABIs

## [1.132.0] - 2023-11-28
### Added
- Implementation of the INodeType function definedAtRuntime

## [1.131.0] - 2023-11-23
### Fixed
- init_instance in python was not called

## [1.130.1] - 2023-11-17
### Fixed
- Fixed exception when the extension is destroyed before the background node registration task completes.

## [1.130.0] - 2023-11-17
### Added
- Callbacks to the python node interface to init/release a graph instance

## [1.129.0] - 2023-11-09
### Changed
- Made documentation references to AutoNode consistent through use of a substitution
### Removed
- Warning about requiring a setting to use AutoNode

## [1.128.1] - 2023-11-03
### Added
- Added the flag `--/exts/omni.graph/syncNodeRegistration` to toggle the deferred node registration off globally.
- Added extension config `package.python.node_registration_mode` to toggle synchronous node registration per extension.

## [1.128.0] - 2023-10-27
### Added
- Support and tests for all array types and the remaining special types for AutoNode
- Support and tests for the AutoNode decorator arguments
- Documentation on some of the pieces missing from the first implementation of AutoNode

## [1.127.0] - 2023-10-25
### Added
- Support and tests for all tuple types and the remaining special types for AutoNode
- Documentation on some of the pieces missing from the first implementation of AutoNode

## [1.126.1] - 2023-10-24
### Changed
- Added workaround in ExpectedError to handle cases where the carb output is an expected error or warning

## [1.126.0] - 2023-10-23
### Added
- Runtime node type definition registration handling
### Changed
- Implementation of AutoNode to use the new runtime node type definition
### Fixed
- Miscellaneous features of runtime node type definition

## [1.125.2] - 2023-10-22
### Changed
- Rearrangement of docs for AutoNode

## [1.125.1] - 2023-10-20
### Changed
- Use latest compound node type schema

## [1.125.0] - 2023-10-18
### Added
- Bindings for views, attribute mapping and vectorized count

## [1.124.0] - 2023-10-17
### Added
- Implementation and testing for method override addition in runtime node type definitions

## [1.123.0] - 2023-10-13
### Added
- Implementation and testing for metadata addition in runtime node type definitions
- Implementation and testing for attribute addition in runtime node type definitions

## [1.122.0] - 2023-10-13
### Changed
- Moved attribute structure information into the unstable namespace
### Removed
- Duplicate registration of Python node types in test_raw_extension_creation
### Added
- Safety checks for nodes with unregistered node types
- Exception raised when attempting to register the same node type name twice
- Callback to the register to deregister a node type when the subnode type is deregistered
- Basic implementation of runtime node type definition helper function and support

## [1.121.1] - 2023-10-11
### Added
- Support for some basic types in a method compatible with Warp definitions and tests for them
- Test arguments that enable the AutoNode tests
- Support for categories as an argument type for create_node_type definitions
- Addition of input and output execution pins to the structure definition when specified
- Support for conversion between runtime type representations of attribute data types
- Import module omni.graph.core.types exclusively holding type information
### Fixed
- A few typos
### Changed
- Separated the runtime and build time autonode tests

## [1.121.0] - 2023-10-10
### Changed
- Reworked a test to make it easier to filter out expected errors
### Removed
- Filtering of unreliable tests that have been succeeding recently

## [1.120.0] - 2023-10-06
### Changed
- Moved commands down into their own submodule
- Moved typing to type_aliases, a more suitable location

## [1.119.0] - 2023-10-02
### Fixed
- Changed compound commands to use latest OmniGraph USD compound schema

## [1.118.0] - 2023-09-29
### Added
- Addition of runtime definitions to the FunctionRegistry
- Generation of node type populator from an AutoNode decorated function

## [1.117.0] - 2023-09-28
- Modify error checking in python bindings. Exceptions are raised instead of returning invalid objects in many functions.

## [1.116.0] - 2023-09-21
### Added
- Support for runtime configuration of AutoNode decorators
- Tests of AutoNode function registration and developer mode implementation of node type

## [1.115.0] - 2023-09-20
### Changed
- Forced all exceptions from the controller to be og.OmniGraphError

## [1.114.0] - 2023-09-18
### Added
- Handling for runtime set and get of the PtrToPtrKind value

## [1.113.0] - 2023-09-13
### Added
- Framework for AutoNode runtime type definition
- Setting to disable AutoNode functionality by default
### Changed
- AutoNode test definition to match new naming and import locations
### Fixed
- Added missing extension disable calls for tests
- Made extensions enable immediately for tests

## [1.112.1] - 2023-09-06
### Changed
- Call the OGN release() callback when an extension with a python node is unloaded

## [1.112.0] - 2023-08-31
### Added
- Bindings for supported version of the node type forwarding interface
- Inspection capabilities for the node type forwarding interface
- Test dependency on omni.inspect for access to the inspection
- Tests for cycle detection of node type forwarding and reverse numerical addition

## [1.111.4] - 2023-08-16
### Added
- Support for accessing the default inspection of node types in the Python subnode types

## [1.111.3] - 2023-08-08
### Removed
- References to migrated extensions

## [1.111.2] - 2023-08-07
### Fixed
- Promoting bundle outputs no longer generates prefix errors

## [1.111.1] - 2023-08-01
### Fixed
- Compounds no longer error when creating and connecting bundle outputs

## [1.111.0] - 2023-07-31
### Changed
- Migrated the type annotation definitions used by AutoNode up to a proper typing module that can be introspected

## [1.110.0] - 2023-07-28
### Added
- Build of node type documentation extension, including build links to all extensions in the index

## [1.109.1] - 2023-07-26
### Changed
- Modified test utility methods for processing external files in .ogn "tests" constructs.

## [1.109.0] - 2023-07-25
### Changed
- Revert output and state bundle name space separator to underscore

## [1.108.0] - 2023-07-21
### Removed
- References to removed omni.graph.examples.python

## [1.107.4] - 2023-07-19
### Changed
- Replaced Usd.Stage traversals with usdrt queries to speed up the stage attach phase.

## [1.107.3] - 2023-07-17
### Fixed
- Enabled bundle output on compounds

## [1.107.2] - 2023-07-14
### Removed
- References to migrated tutorials node types

## [1.107.0] - 2023-07-13
### Changed
- OM-97363: Resolve input-output bundle asymmetry

## [1.106.1] - 2023-07-13
### Removed
- Removed the "defaultEvaluator" and "useCachedConnectionsForFileLoad" OG settings.

## [1.106.0] - 2023-07-11
### Added
- RenameCompoundSubgraph command

## [1.105.0] - 2023-07-05
### Added
- command to promote unconnected inputs/outputs to compound subgraph

## [1.104.1] - 2023-07-03
### Fixed
- OgnOnVariableChange with array based variables

## [1.104.0] - 2023-06-28
### Added
- New bindings for functionality described by ISchedulingHints2.

## [1.103.3] - 2023-06-28
### Changed
- traverse_downstream_graph, traverse_upstream_graph accept compound graph prims as inputs
- og.ObjectLookup.prims and og.Controller.prim_path accept og.Graph objects
- og.ObjectLookup.graph accepts Usd.Prim and Usd.Typed

## [1.103.2] - 2023-06-27
### Fixed
- Fixed some documentation examples

## [1.103.1] - 2023-06-22
### Added
- Bindings for new "pure" scheduling hint.

## [1.103.0] - 2023-06-20
### Added
- Bindings Change Tracking for bundles

## [1.102.0] - 2023-06-12
### Added
- og.ObjectLookup.usd_relationship and og.ObjectLookup.usd_property
### Fixed
- og.ObjectLookup.attribute gives the same result with equivalent str and Sdf.Path inputs

## [1.101.3] - 2023-06-08
### Changed
- Compound nodes correctly manage fan-in, including execution ports

## [1.101.2] - 2023-06-08
### Added
- Unit test to check if bundle can carry target attribute type

## [1.101.1] - 2023-06-05
### Fixed
- Fixed crash in ReplaceWithCompoundSubgraph when called from compound graph

## [1.101.0] - 2023-06-01
### Added
- Graph.get_owning_compound_node() API

## [1.100.0] - 2023-05-29
### Changed
- Moved cache generation tests to be disabled in the .toml file instead of by decorator
- Moved some calls to actual deprecation even though they are not functioning since others are at least calling them
### Removed
- Dependencies not required for OmniGraph operation (omni.kit.async_engine:stage_templates:pip_archive)
- Hard deprecated functions

## [1.99.0] - 2023-05-26
### Added
- CREATE_ATTRIBUTES capabilities in the controller.edit() function

## [1.98.1] - 2023-05-26
### Added
- Added command to rename compound subgraph ports

## [1.98.0] - 2023-05-25
### Added
- Support for promoting bundle inputs
- Validation methods for subgraph compounds
### Changed
- Output bundles excluded from compound promotion.

## [1.97.3] - 2023-05-24
### Changed
- Modified some comments that were referring to now-deprecated OG settings.

## [1.97.2] - 2023-05-24
### Removed
- Removed references to "pull" and "execution_pull" evaluators.
- Removed test scene that was being explicitly used to test the "pull" evaluator.

## [1.97.1] - 2023-05-24
### Changed
- Default name for compounds is lower case, same as other omni graph nodes

## [1.97.0] - 2023-05-23
### Removed
- Removed OG settings that were referencing now-removed constructs (dynamic scheduler and realm static scheduler).
- Removed TestDynamicScheduling.usda because OG dynamic scheduler no longer exists.

## [1.96.1] - 2023-05-17
### Fixed
- Fixed mismatched allocations on default type data

## [1.96.0] - 2023-05-16
### Added
- og.Controller.keys.CREATE_NODES now also takes a dictionary of commands to define a compound subgraph
- og.Controller.keys.PROMOTE_ATTRIBUTES added to define exposed compound node attributes

## [1.95.2] - 2023-05-12
### Changed
- Refactored extension search to prevent syncing the registry if it was already there

## [1.95.1] - 2023-05-10
### Changed
- Handle compound nodes when validating node's owner graph

## [1.95.0] - 2023-05-09
### Changed
- Made MetadataKeys deprecation message more explicit

## [1.94.0] - 2023-05-08
### Added
- og.Controller.keys.CREATE_VARIABLE tuples take an optional 3rd entry representing the default value

## [1.93.0] - 2023-05-08
### Deprecated
- Removed deprecated locations of Python modules

## [1.92.0] - 2023-05-04
### Added
- Compounds subgraphs attribute commands added to _unstable module

## [1.91.0] - 2023-05-04
### Added
- Migration support for omniGraphSchema.CompoundNodeAPI

## [1.90.0] - 2023-05-03
### Changed
- CreateCompoundNodeType now takes evaluator_type
- Added Py_Node.get_compound_graph_instance

## [1.89.0] - 2023-05-02
### Added
- Bindings for the new INodeTypeForwarding interface
- Added a generic validator for Python interface bindings
- Refactored some binding definitions to live in their own files

## [1.88.1] - 2023-05-01
### Added
- Setting to control auto-instancing

## [1.88.0] - 2023-04-28
### Added
- CreateCompoundSubgraph and ReplaceWithCompoundSubgraph

## [1.87.1] - 2023-04-24
### Fixed
- Don't allow other text streams to interleave with an expected error.

## [1.87.0] - 2023-04-24
### Deprecated
- Replaced all documentation for GraphContext.get_attribute_as_XX and GraphContext.set_XX with deprecation notices
- Added runtime deprecation notices to GraphContext.get_attribute_as_XX and GraphContext.set_XX calls
### Added
- Duplicate of deprecation macros from omni.graph.core to use here

## [1.86.0] - 2023-04-19
### Changed
- Py_AttributeData: review access data permission

## [1.85.0] - 2023-04-19
### Deprecated
- Removed all references to the obsolete settings constants

## [1.84.0] - 2023-04-19
### Deprecated
- Removed context_helper parameter from og.Database.__init__
- Removed context_helper parameter from og.DynamicAttributeInterface.set/get
- Removed og.ContextHelper and og.OmniGraphHelper
- Removed types supporting og.OmniGraphHelper - BundledAttribute_t, ConnectData_t, ConnectDatas_t, CreateNodeData_t, CreateNodeDatas_t, CreatePrimData_t, CreatePrimDatas_t, DeleteNodeData_t, DeleteNodeDatas_t, DisconnectData_t, DisconnectDatas_t, OmniGraphHelper, SetValueData_t, SetValueDatas_t

## [1.83.0] - 2023-04-18
### Removed
- References to deprecated torch/tensor support

## [1.82.3] - 2023-04-16
### Removed
- Removed dynamic test generation for legacy backend

## [1.82.2] - 2023-04-13
### Fixed
- Typo in a Python reference from og.LOG to ogi.LOG

## [1.82.1] - 2023-04-12
### Changed
- Setting target type values now support scalar and string values

## [1.82.0] - 2023-04-05
### Changed
- attribute_value_as_usd supports relationships
- Relationships can be set through controller.edit
### Added
- og.GraphContext.get_graph_target now takes optional instance index

## [1.81.0] - 2023-04-03
### Added
- og.INSTANCING_GRAPH_TARGET_PATH
- Bindings for missing functions in IAttribute ABI
- Testing support for validating ABI definitions
### Changed
- Moved binding definitions for omni.graph.core.Attribute into its own file

## [1.80.0] - 2023-03-31
### Changed
- target attributes now use relationships with output and state ports

## [1.79.0] - 2023-03-29
### Deprecated
- omni.graph.core.Database.ROLE_XX constants, in favor of omni.graph.core.AttributeRole enum values

## [1.78.1] - 2023-03-27
### Changed
- target python wrapping changed from string to usdrt Sdf.Path

## [1.78.0] - 2023-03-24
### Added
- IVariable.set_type python method for changing a variable type
- ChangeVariableTypeCommand
- GraphEvent.VARIABLE_TYPE_CHANGE event when a variable type is changed

## [1.77.2] - 2023-03-24
### Fixed
- Fixed documentation errors

## [1.77.1] - 2023-03-22
### Fixed
- Made all docstrings to publicly visible documentation consistent

## [1.77.0] - 2023-03-17
### Added
- Implementing target attribute python wrapping

## [1.76.1] - 2023-03-17
### Fixed
- Lint errors

## [1.76.0] - 2023-03-07
### Added
- Added functions to traverse the graph and visit upstream and downstream nodes

## [1.75.0] - 2023-03-05
### Added
- AttributeTemplate.get_default_data accessor

## [1.74.2] - 2023-03-01
### Fixed
- OM-84762 IBundleFactory get_bundle conversion methods bugfix.

## [1.74.1] - 2023-03-01
### Fixed
- warning about deprecated function call

## [1.74.0] - 2023-02-28
### Added
- ComputeGraph::flushUsd call to apply pending usd changes.

## [1.73.1] - 2023-02-25
### Changed
- Modifed format of Overview to be consistent with the rest of Kit
- Fixed link to Python autodocs

## [1.73.0] - 2023-02-24
### Added
- ResolveAttrTypeCommand

## [1.72.4] - 2023-02-23
### Added
- Two new utility methods for evaluating code once at the start/end of threaded
  unit tests in ThreadsafetyTestUtils.

## [1.72.3] - 2023-02-22
### Changed
- Renamed omni.kit.exec references to omni.kit.exec.core

## [1.72.2] - 2023-02-21
### Added
- ThreadsafetyTestUtils class that helps simplify the writing of thread-safety
  tests for OG nodes.

## [1.72.1] - 2023-02-19
### Changed
- Added label to the main doc page so that higher level docs can reference the extension

## [1.72.0] - 2023-02-16
### Changed
- Unification of Py_Bundle and IConstBundle/IBundle

## [1.71.1] - 2023-02-15
### Fixed
- Made test file pattern account for node files not beginning with Ogn

## [1.71.0] - 2023-02-15
### Changed
- Switched the default execution backend for generated tests. Execution Framework in enabled by default

## [1.70.1] - 2023-02-09
### Fixed
- Reverted unintential change to test case creation

## [1.70.0] - 2023-02-08
### Added
- AttributeTemplate API calls

## [1.69.0] - 2023-02-07
### Added
- Split support for test configurations without forcing specific base class

## [1.68.0] - 2023-02-06
### Added
- omni.graph.core._unstable module
- AttributeTemplate CompoundNodeType python bindings
- CreateCompoundNodeType, CreateCompoundNodeTypeInput, CreateCompoundNodeTypeOutput, RemoveCompoundNodeTypeInput, RemoveCompoundNodeTypeOutput commands
### Removed
- CreateNodeType, CreateTypeInput, CreateNodeTypeOutput, RemoveNodeTypeInput, RemoveNodeTypeOutput

## [1.67.4] - 2023-02-02
### Fixed
- Lint error that appeared when pylint updated

## [1.67.3] - 2023-01-30
### Changed
- Removed the kit-sdk landing page
- Moved all of the documentation into the new omni.graph.docs extension

## [1.67.2] - 2023-01-30
### Changed
- Refactored OG test generation to not assume execution backend

## [1.67.1] - 2023-01-20
### Fixed
- GIL locking safety in bindings call out to python
- GIL is released before Graph eval via python

## [1.67.0] - 2023-01-11
### Changed
- Made dynamic attribute failures raise exceptions
- Made return values of dynamic attribute commands more consistent
- Made the node controller failures in dynamic attribute operations raise exceptions

## [1.66.0] - 2023-01-11
### Removed
- Gather prototype is gone
### Changed
- Bundle attributes are now all typed as eRelationship (no ePrim anymore)

## [1.65.3] - 2023-01-03
### Changed
- Added [native] to make package separate for each platform & build config

## [1.65.2] - 2022-12-21
### Changed
- Refactored CUDA build to consolidate build functions and remove unnecessary rebuilds

## [1.65.1] - 2022-12-16
### Fixed
- Updated inspection to handle Python node redirection

## [1.65.0] - 2022-12-14
### Added
- CreateNodeTypeInput and CreateNodeTypeOutput support empty references and specifying the supported ogn type(s)

## [1.64.0] - 2022-12-14
### Changed
- Filtered out test_data_access tests from EF generation. These tests have issue with per-node data when run twice,
  but they don't provide any value for compute correctness since they only read a file and use python data base.

## [1.63.0] - 2022-12-13
### Added
- og.AttributeType.get_unions() method to access the attribute union definitions.

## [1.62.1] - 2022-12-12
### Added
- Fixed occasional crash in grouped undos/redos.

## [1.62.0] - 2022-12-08
### Fixed
- Settings.tempoary context manager now removes any settings that it adds.
### Changed
- Settings.temporary context manager now accepts a list of settings.

## [1.61.0] - 2022-12-02
### Changed
- Modified Python node type registration process to handle multiple versions on-demand

## [1.60.0] - 2022-11-24
### Removed
- Setting useSchemaPrims
- Test variations that allow modifying the deleted setting
### Changed
- Turned use of the deleted setting into errors

## [1.59.0] - 2022-11-22
### Added
- ObjectLookup.variable now supports Sdf.Path and str objects
### Fixed
- Errors and crashes from OmniGraph commands when grouping or applying successive undo and redo calls

## [1.58.1] - 2022-11-21
### Added
- Documentation for running a minimal Kit with OmniGraph

## [1.58.0] - 2022-11-17
### Removed
- Settings updateToUSD, supportForceWriteback, useLegacySimulationPipeline, and enableUSDInPreRender
- Test variations that allow modifying the deleted setting
### Changed
- Turned use of the deleted settings into errors

## [1.57.0] - 2022-11-14
### Changed
- Default simple dynamic attribute values to the CPU

## [1.56.0] - 2022-11-12
### Removed
- Support for the deleted implicit global graph setting
- Test variations that allow modifying the implicit global graph setting
### Changed
- Turned use of the implicit global graph setting into errors

## [1.55.1] - 2022-11-10
### Changed
- removed dependency on omni.kit.test

## [1.55.0] - 2022-11-10
### Added
- Support for redirecting dynamic attributes to the GPU

## [1.54.0] - 2022-10-31
### Changed
- change bindings to reflect new Fabric naming conventions.
- change all types to reflect new namespace, should remain abi compatible

## [1.53.0] - 2022-10-23
### Added
- og.get_kit_version()

## [1.52.0] - 2022-10-20
### Added
- NodeType.is_compound_node_type()
- GraphRegistryEvent.NODE_TYPE_NAMESPACED_CHANGED, GraphRegistryEvent.NODE_TYPE_CATEGORY_CHANGED

## [1.51.2] - 2022-10-19
### Fixed
- Corrected the path to the default category files

## [1.51.1] - 2022-10-14
### Changed
- test generation for EF will filter tests that target deprecated implicit graph
## [1.51.0] - 2022-10-03
### Added
- instance_path argument added to IVariable.get, get_array and set methods to specify the instance of the variable

## [1.50.0] - 2022-09-30
### Added
- node_type.get_path(), which returns the path to the prim associated with a node type

## [1.49.0] - 2022-09-28
### Added
- Collection of registration and deregistration timing for Python node types

## [1.48.1] - 2022-09-27
### Fixed
- Py_AttributeData set value for attribute with ePath role

## [1.48.0] - 2022-09-21
### Added
- Og.Node.is_compound_node
- Og.Graph.is_compound_graph
- CreateNodeType, CreateNodeTypeInput, RemoveNodeTypeInput, CreateNodeTypeOutput, RemoveNodeTypeOutput, ReplaceWithCompound commands

## [1.47.0] - 2022-09-20
### Added
- Ability to control prim and node creation behavior with allow_exists

## [1.46.1] - 2022-09-19
### Fixed
- Lookup of output bundles by path

## [1.46.0] - 2022-09-14
### Changed
- Refactored controller classes to accept variable arguments in all methods and constructor
### Removed
- References to obsolete set of unsupported types
- Last remaining references to the obsolete ContextHelper
### Added
- Argument flattening utility

## [1.45.2] - 2022-09-07
### Added
- Python node type registration deallocates attribute defaults after registration.

## [1.45.1] - 2022-09-01
### Fixed
- Fixed the type name access in the node controller to handle bundles properly

## [1.45.0] - 2022-08-30
### Added
- Handling for allocation of memory and transfer of values for Python default values

## [1.44.0] - 2022-08-23
### Added
- GraphRegistry.get_event_stream to get an event stream that triggers when node types are added and removed.

## [1.43.0] - 2022-08-19
### Added
- Access to new setting that turns deprecations into errors

## [1.42.0] - 2022-08-12
### Changed
- og.AttributeData now raise exceptions for errors instead of printing

## [1.41.1] - 2022-08-09
### Fixed
- All of the lint errors reported on the Python files in this extension

## [1.41.0] - 2022-08-02
### Added
- Optimize attribute setting from python nodes - during runtime computation we skip commands (no need for undo)

## [1.40.0] - 2022-07-27
### Added
- IBundle2 remove_attributes_by_name, remove_child_bundles_by_name

## [1.39.0] - 2022-07-27
### Changed
- Added better __repr__ to Attribute and Node

## [1.38.1] - 2022-07-26
### Fixed
- Adjusted config to avoid obsolete commands module
- Added firewall protection to AutoFunc and AutoClass initialization so that they work in the script editor

## [1.38.0] - 2022-07-19
### Added
- IBundle2 interface API review

## [1.37.0] - 2022-07-12
### Added
- Python performance: database caching, prefetch and commit for batching of simple attribute reads/writes

## [1.36.0] - 2022-07-12
### Fixed
- Backward compatibility of the generated attribute descriptions.

## [1.35.0] - 2022-07-08
### Added
- omni.graph.core.Attribute.is_deprecated()
- omni.graph.core.Attribute.deprecation_message()
- omni.graph.core.Internal sub-module
- omni.graph.core.Internal._deprecateAttribute()

## [1.34.0] - 2022-07-07
### Changed
- Refactored imports from omni.graph.tools to get the new locations
- Moved node_generator/ into the _impl/ subdirectory
- Made dunder attribute names in AttributeDataValueHelper into single-underscore to avoid Python compatibility problem
### Added
- Test for public API consistency

## [1.33.0] - 2022-07-06
### Added
- Metadata support for IBundle2 interface

## [1.32.3] - 2022-07-04
### Fixed
- Py_GraphContext's __eq__ and __hash__ now use the underlying GraphContext object rather than the Python wrapper

## [1.32.2] - 2022-06-28
### Changed
- Made node type failure a more actionable error
- Bootstrap the nodeContextHandle to allow independent database creation
### Added
- Linked docs in the build area

## [1.32.1] - 2022-06-26
### Changed
- Made node type failure a more actionable error

## [1.32.0] - 2022-06-26
### Added
- Added test for clearing bundle contents

## [1.31.1] - 2022-06-21
### Changed
- Fixed error in graph_settings when loading non-schema prims

## [1.31.0] - 2022-06-17
### Added
- omni.graph.core.graph.get_evaluator_name()

## [1.30.1] - 2022-06-17
### Added
- Added ApplyOmniGraph and RemoveOmniGraph api commands

## [1.30.0] - 2022-06-13
### Added
- omni.graph.core.GraphEvaluationMode enum
- evaluation_mode argument added to omni.graph.core.Graph.create_graph_as_node
- evaluation_mode property added to omni.graph.core.Graph
- SetEvaluationModeCommand
- evaluation_mode parameter added to CreateGraphAsNodeCommand
- evaluation_mode option added to GraphController

## [1.29.0] - 2022-06-13
### Added
- Temporary binding function to prevent Python node initialization from overwriting values already set

## [1.28.0] - 2022-06-07
### Added
- Added CPU-GPU pointer support in data_view class and propagation of the state through python wrapper classes

## [1.27.0] - 2022-06-07
### Added
- Support for the generator settings to complement runtime settings

## [1.26.1] - 2022-06-04
### Fixed
- Nodes with invalid connections no longer break upgrades to OmniGraph schema

## [1.26.0] - 2022-05-06
### Fixed
- Handling of runtime attributes whose bundle uses CPU to GPU pointers
### Added
- Support for CPU to GPU data in the DataWrapper

## [1.25.0] - 2022-05-05
### Removed
- Python subscriptions to changes in settings, now handled in C++

## [1.24.1] - 2022-05-05
### Deprecated
- Deprecated OmniGraphHelper and ContextHelper for og.Controller

## [1.24.0] - 2022-04-29
### Fixed
- Fixed override method for IPythonNode type
### Removed
- Obsolete example files
### Added
- Explicit settings handler
### Changed
- Used explicit OmniGraph test handler base classes

## [1.24.0] - 2022-04-27
### Added
- *GraphController.set_variable_default_value*
- *GraphController.get_variable_default_value*
- *ObjectLookup.variable*
- *GraphContext.get_graph_target*

## [1.23.0] - 2022-04-25
### Added
- Added a test to confirm that all version references in omni.graph.* match

## [1.22.2] - 2022-04-20
### Fixed
- Undoing the deletion of a connection's src prim will now restore the connection on undo.

## [1.22.1] - 2022-04-18
### Changed
- og.Attribute will now raise an exception when methods are called when in an invalid state.

## [1.22.0] - 2022-04-11
### Fixed
- Moved Py_Node and Py_Graph callback lists to static storage where they won't
  be destroyed prematurely.
- Callback objects now get destroyed when the extension is unloaded.

## [1.21.1] - 2022-04-05
### Fixed
- Added hash check to avoid overwriting ogn/tests/__init__.py when it hasn't changed
- Fix deprecated generator of ogn/tests/__init__.py to generate a safer, non-changing version

## [1.21.0] - 2022-03-31
### Added
- `IConstBundle2`, `IBundle2` and `IBundleFactory` interface python bindings.
- Unit tests for bundle interfaces

## [1.20.1] - 2022-03-24
### Fixed
- Fixed location of live-generation of USD files from .ogn
- Fixed contents of the generated tests/__init__.py file

### [1.20.0] - 2022-03-23
### Added
- *GraphEvent.CREATE_VARIABLE* and *GraphEvent.REMOVE_VARIABLE* event types
- *Graph.get_event_stream()*

## [1.19.0] - 2022-03-18
### Added
- Added command to set variable tooltip

## [1.18.0] - 2022-03-16
### Added
- support for *enableLegacyPrimConnection* setting to test utils

## [1.17.1] - 2022-03-14
### Fixed
- Corrected creation of implicit graphs that were not at the root path
- Added tests for such graphs and a graph in a layer

## [1.17.0] - 2022-03-11
### Added
- *Node.get_backing_bucket_id()*
- *GraphContext.write_bucket_to_backing()*

## [1.16.0] - 2022-03-01
### Added
- *expected_error.ExpectedError* (moved from omni.graph.test)
### Changed
- Updated OmniGraphTestCase and derived classes to use *test_case_class*

## [1.15.0] - 2022-02-16
### Added
- Added commands to create and remove variables

## [1.14.0] - 2022-02-11
### Added
- *Attribute.register_value_changed_callback*
- *Database.get_variable*
- *Database.set_variable*
- *Controller.keys.CREATE_VARIABLES*
- *GraphController.create_variable*

## [1.13.0] - 2022-02-10
### Added
- Added support for migration of old graphs to use schema prims

## [1.12.2] - 2022-02-07
### Changed
- Moved carb logging out of database.py and into Node::logComputeMessage.
- Fall back to old localized logging for Python nodes which don't yet
  support the compute message logging ABI.

## [1.12.1] - 2022-02-04
### Fixed
- Compute counts weren't working for Python nodes
- Compute messages from Python nodes weren't visible in the graph editors

## [1.12.0] - 2022-01-28
### Added
- Support for WritePrim creation in *GraphController.expose_prims*

## [1.11.0] - 2022-01-29
### Changed
- Reflecting change of omni.graph.core from 2.11 -> 2.12

## [1.10.0] - 2022-01-27
### Added
- *ObjectLookup.usd_attribute*

## [1.9.0] - 2022-01-21
### Added
- *Node.log_compute_message*
- *Node.get_compute_messages*
- *Node.clear_old_compute_messages*
- *Graph.register_error_status_change_callback*
- *Graph.deregister_error_status_change_callback*
- *Severity* enum

## [1.8.0] - 2021-12-17
### Added
- Added *NodeType.get_all_categories_*
- Added *get_node_categories_interface*
- Created binding class *NodeCategories*

## [1.7.0] - 2021-12-15
### Added
- Added _NodeType::isValid_ and cast to bool
- Added _Controller_ class
- Added _GraphController_ class

## [1.6.0] - 2021-12-06
### Added
- og.NodeEvent.ATTRIBUTE_TYPE_RESOLVE
## [1.5.2] - 2021-12-03
### Added
- Node, Attribute, AttributeData, Graph, and Type objects are now hashable
  in Python, meaning that they can be used in sets, as keys in dicts, etc.
### Fixed
- Comparing Node and Graph objects for equality in Python now compare the
  actual objects referenced rather than the wrappers which hold the references
- Comparing Attribute and AttributeData objects to None in Python no longer
  generates an exception.

## [1.5.0] - 2021-12-01
- Added functions to get extension versions for core and tools
- Added cascading Python node registration process, that auto-generates when out of date
- Added user cache location for live regeneration of nodes

## [1.4.0] - 2021-11-26
### Added
- Python Api `Graph.get_parent_graph`
### Fixed
- Fix failure when disconnecting a connection from a subgraph node to the parent graph node

## [1.3.2] - 2021-11-24
### Changed
- Generated python nodes will emit info instead of warning when inputs are unresolved
## [1.3.1] - 2021-11-22
### Changed
- Improved error messages from wrapped functions
## [1.3.0] - 2021-11-19
### Added
- __bool__ operators added to all returned OG Objects. So `if node:` is equivalent to `if node.is_valid():`
### Changed
- Bug fix in Graph getter methods
## [1.2.0] - 2021-11-10
### Added
- `og.get_node_by_path`
- `get_graph_by_path`, `get_node_by_path` now return None on failure

## [1.1.0] - 2021-10-17
### Added
- og.get_graph_by_path

## [1.0.0] - 2021-10-17
### Initial Version
- Started changelog with current version of omni.graph
