(changelog_omni_graph_core)=

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.184.5] - 2025-08-14
### Changed
- Removed a now useless and costly call to USDRT population affecting badly performance

## [2.184.4] - 2025-06-13
### Fixed
- Fixed not accessing proper "globals" for a graph that is being auto instanced
- Fixed default value not properly applied on array node attributes of an auto-instanced graph

## [2.184.3] - 2025-06-12
### Fixed
- Only graph using the shared fabric backing type were actually being executed when importing into an existing stage

## [2.184.2] - 2025-04-23
### Fixed
- Don't try to resolve unresolved inputs which have incoming connections.

## [2.184.1] - 2025-02-11
### Changed
- Fabric accesses for write ar now using a shared lock instead of an exclusive one (as change tracking bug is fixed)

## [2.184.0] - 2025-01-07
### Changed
- Prevent the possibility of returning a reference from a rvalue

## [2.183.0] - 2024-12-18
### Changed
- Graphs are now created by default using their own private fabric backing

## [2.182.1] - 2024-12-17
### Fixed
- Graph::destroyNode() was accessing wrapped graph after it had been freed.

## [2.182.0] - 2024-12-05
### Changed
- Added new ABI ICompoundNodeType::getDefaultFolderPath and deprecated ICompoundNodeType::getDefaultFolder.
### Fixed
- Replaced some usages of omni::fabric::PathC with omni::fabric::Path.

## [2.181.9] - 2024-12-05
### Fixed
- Suppress invalid node type handle errors when unloading extensions.

## [2.181.8] - 2024-12-03
### Fixed
- Disable pointer caching by default
- Create a unique, private, and shared fabric for graph backed by StageWithoutHistory
- Added abitlity to copy bundles between different fabric
- Makes sure that prim operations happens on the main fabric (target mapping/reading/manipulation, prim views binding, USD writebacks, etc...)
- Fixed a bug in CoW when copying between fabrics

## [2.181.7] - 2024-10-15
### Fixed
- Node, Attribute and Graph handles are now path-based. They will remain valid when the underlying OmniGraph object has been regenerated.

## [2.181.6] - 2024-10-15
### Fixed
- Show a warnings about missing GPU device only once.

## [2.181.5] - 2024-10-09
### Fixed
- Dead lock caused by multithreaded USD write access when loading several graphs from USD at the same time

## [2.181.4] - 2024-10-02
### Fixed
- Reload OmniGraphs when the parent prim was resynced.

## [2.181.3] - 2024-09-27
### Fixed
- Fix security issues (OMPE-18747).

## [2.181.2] - 2024-09-27
### Fixed
- Node type resolution does not trigger errors for compound nodes which may not have loaded yet.

## [2.181.1] - 2024-09-24
### Fixed
- Do not attempt to write back to USD from fabric an attribute when role is changed to ePath

## [2.181.0] - 2024-09-24
### Added
- Moves loading code from GraphContext to its own file
- Transposed loading code (Instead of going graph per graph, now going step by step, with all available graphs
- Threading on steps where possible
- Makes all fabric access by bucket id so we have a single point of protection required for safe threaded type resolution
- Batches node instance initialization (big win for python nodes)
### Fixed
- Bugs related to auto-instancing (moving og instances from auto instance master back and forth)

## [2.180.3] - 2024-09-20
### Fixed
- Fix security issues (OMPE-18747).

## [2.180.2] - 2024-09-19
### Fixed
- Fixed the reload of instances following a root layer resync USD notice.

## [2.180.1] - 2024-09-17
### Fixed
- Fixed a memory overwrite with compound nodes that could occur when unloading the stage.

## [2.180.0] - 2024-08-29
### Added
- Added support for non-usd backed variables.

## [2.179.2] - 2024-06-18
### Changed
- Pass lvalue reference to `omni::fabric::toSdfPath/toTfToken` to avoid potential issues with temporary objects.

## [2.179.1] - 2024-06-07
### Fixed
- Removed the SimulationOrchestrationGraph mutex lock in `updateSimStepUsd_abi`, which was causing deadlocks
  in DriveSim.

## [2.179.0] - 2024-05-23
### Fixed
- Auto-instanced graph did not always have proper default values
- Crash when executing a lot of graphs concurrently because of unprotected snapshot detection code

## [2.178.0] - 2024-04-22
### Fixed
- Threadsafe nodes have the correct CUDA device set on the host thread when executing concurrently.
### Added
- Exposed the CUDA device ID used by OmniGraph in the ComputeGraph interface.

## [2.177.2] - 2024-04-09
### Changed
- Undo change that forces `flushFsd` to be invoked each time `ComputeGraphImpl::updateChangeProcessing` is
  called since this results in CoreAPI crashing.

## [2.177.1] - 2024-04-02
### Changed
- `flushFsd` always gets invoked when `ComputeGraphImpl::updateChangeProcessing` is called, even if there
  are no deferred tasks that need evaluation.

## [2.177.0] - 2024-03-22
### Changed
- OmniGraph queries the Renderer for the active CUDA device.

## [2.176.3] - 2024-03-07
### Fixed
- Fixed crash when calling Attribute::getDataOwningAttribute_abi on attribute with unknown type.

## [2.176.2] - 2024-02-29
### Fixed
- considerKitUpdateLoop interface was not being filled with the corresponding ABI implementation;
  this has been fixed.

## [2.176.1] - 2024-02-27
### Fixed
- OnConnectionTypeResolved now invoked when a dynamic attribute is removed.

## [2.176.0] - 2024-02-26
### Added
- Added the setting `--/app/omnigraph/disableUsdBacking` disable the loading of OmniGraph from USD.

## [2.175.2] - 2024-02-16
### Changed
- Skip OG pre-process tasks when OG itself is disabled from ticking in StageUpdate.
- Force updateSimStepUsd (which is used by DriveSim to on-demand execute OG) to explicitly
  run the required pre-process tasks in the sim thread before actual evaluation.

## [2.175.1] - 2024-02-15
### Fixed
- Added back the accidentally-deleted implementation for considerKitUpdateLoop (which was
  replaced at the time with a no-op for local testing purposes, but wasn't reverted prior
  to merging).

## [2.175.0] - 2024-02-14
### Added
- Added new node ABI computeCuda, supported in the pre and post render graph nodes.

## [2.174.2] - 2024-02-13
### Changed
- Removed GraphPipelineGuard in favor of explicitly grabbing mutex locks when accessing orchestration graphs.
- Acquire all orchestration graph mutexes with std::scoped_lock prior to invoking any methods that iterate
  over all orchestration graphs; helps to prevent deadlocks in multithreaded simulation environments (e.g.,
  DriveSim2).

## [2.174.1] - 2024-02-08
### Fixed
- OM-119859 Remove RuntimeAttributes from database by name instead of by handle

## [2.174.0] - 2024-02-01
### Fixed
- Modified type created by BundlePrim::addRelationship to be a relationship rather than a token[].

## [2.173.0] - 2024-01-31
### Added
- Ability for OG nodes to register custom ONI implementations and to query said interfaces via INodeType.
- New IDirtyable interface to allow OG nodes to communicate with the lazy graph executor in a customized fashion.
### Changed
- Cleaned up the lazy graph executor to utilize the new IDirtyable interface rather than having hard-coded logic
  for handling specific node types.

## [2.172.0] - 2024-01-31
### Added
- >= and <= operators to FileFormatVersion

## [2.171.1] - 2024-01-29
### Removed
- Workaround that prevented a crash caused by thread safety issue in the Fabric change tracking system, which is now fixed

## [2.171.0] - 2024-01-25
### Fixed
- Bundle asymmetry issue, outputs:bundle and state:bundle renamed to outputs_bundle and state_bundle

## [2.170.1] - 2024-01-22
### Changed
- Modified all pre-process task scheduling calls to use the new "persist" argument rather than
  recursively rescheduling themselves after evaluation (which is no longer allowed).

## [2.170.0] - 2024-01-18
### Changed
- Renamed PullGraphDef to LazyGraphDef.
- Miscellaneous refactorings surrounding the legacy OG scheduling/evaluation system clean-up.
### Removed
- Legacy OG scheduling/evaluation systems.

## [2.169.2] - 2024-01-17
### Changed
- Move ComputeGraphImpl::updateChangeProcessing into its own pre-process task, rather than calling it
  during execution graph compilation/pre-execution.

## [2.169.1] - 2024-01-16
### Removed
- Duplicated implementation of bundle interface

## [2.169.0] - 2024-01-11
### Fixed
- Evaluating explicitly an auto-instancved graph now works as expected
### Added
- AllowAutoInstancing graph option from the schema is now correctly managed

## [2.168.2] - 2024-01-10
### Changed
- OM-115855 Improve code coverage for bundles, exclude unsupported code and add unit tests

## [2.168.1] - 2024-01-09
### Changed
- OM-117492 Bundle implementation replace handles with reference counted fabric::Path

## [2.168.0] - 2023-12-20
### Fixed
- Added the ability for the OGN layer to not cache any pointers. OmniGraph now works with StageWithHistory with prim filtering disabled

## [2.167.1] - 2023-12-20
### Deprecated
- OM-116989 Soft-deprecate access to child bundles by index

## [2.167.0] - 2023-12-18
### Changed
- Reduced non-fatal problem from an error to a warning in order to fix tests

## [2.166.3] - 2023-12-14
### Removed
- Removes useless setting monitoring callback

## [2.166.2] - 2023-12-13
### Fixed
- Missing include + fixes some compile warning

## [2.166.1] - 2023-12-12
### Fixed
- Prevent crashing when using an invalid RuntimeAttribute

## [2.166.0] - 2023-12-11
### Added
- Allows to set custom fabric backing on target mapped attribute

## [2.165.3] - 2023-12-09
### Added
- OM-116247 Provide getBundle and getBundles overloaded functions for IBundleFactory

## [2.165.2] - 2023-12-08
### Fixed
- Fixed double6 incorrectly identified as an OGN type

## [2.165.1] - 2023-12-08
### Changed
- onConnectionTypeResolved callback now triggers when an dynamic extended attribute is created

## [2.165.0] - 2023-12-08
### Fixed
- objectId supported in extended types
- bundle, target and execution explicitly excluded from 'any' or union types
- timecode type works with resolvePartiallyCoupledAttributes
- Attribute:setResolvedType allows for re-resolution of extended attributes
- Attribute:setResolvedType(og.Type()) no longer unresolves other input attributes with extended types

## [2.164.4] - 2023-12-07
### Fixed
- Fixed target mapping and instancing out of order updates with Fabric Scene Delegate enabled

## [2.164.3] - 2023-12-06
### Fixed
- Crash when deleting a graph containing nodes of an extension that has been unloaded

## [2.164.2] - 2023-12-05
### Changed
- Post-process (formerly known as post-execute) tasks are now scheduled via the default ExecutionController.

## [2.164.1] - 2023-12-05
### Fixed
- OM-98247 Remove bundle portion from dirty ids implementation

## [2.164.0] - 2023-11-29
### Changed
- Log an error when registering a node built with a more recent framework than the one used in the running app

## [2.163.0] - 2023-11-29
### Removed
- Removed old and now unused code, and deprecated assotiated ABIs

## [2.162.1] - 2023-11-29
### Fixed
- Added validity checks to ensure node type is still active when scheduling

## [2.162.0] - 2023-11-28
### Added
- INodeType function definedAtRuntime to check if a node type was created at runtime
### Changed
- Separated out INodeType into its own file

## [2.161.0] - 2023-11-24
### Changed
- Invalid connections now prevent nodes from evaluating and log errors during the compute phase

## [2.160.0] - 2023-11-23
### Fixed
- Do not call releaseInstance on the authoring graph

## [2.159.0] - 2023-11-22
### Added
- Added ABIs for Attribute::isPassthrough and Attribute::getDataOwningAttribute

## [2.158.0] - 2023-11-21
### Fixed
- Keep a reference to target paths as token, so it remains the same

## [2.157.4] - 2023-11-21
### Changed
- Cleaned up unused code paths

## [2.157.3] - 2023-11-20
### Changed
- Updated getINodeTypeForwarding to use the most up-to-date interface (V2).

## [2.157.2] - 2023-11-17
### Added
- Added templated version of GenericNodeDefT execution node

## [2.157.1] - 2023-11-17
### Changed
- Improved code coverage for compound nodes.
### Fixed
- Fixed compound node types not responding to API additions & removes from USD

## [2.157.0] - 2023-11-17
### Added
- Callbacks to the node interface to init/release a graph instance
- Plugged that feature into the OGN framework
- Ability to access internal state through instance index as well as instance ID

## [2.156.0] - 2023-11-13
### Removed
- Retires deprecated ABI related to schedule node and assotiated features
- Removes dead code
### Fixed
- Fixed small bugs revealed by improved code coverage
### Changed
- Exclude some safety error path code from code coverage

## [2.155.1] - 2023-11-09
### Added
- Support for testing of the graph registry
### Fixed
- A few miscellaneous pointer check issues

## [2.155.0] - 2023-11-08
### Fixed
- Authoring graph and default instance now have a different unique ID (allows shared internal state and per instance one to be distinct for example)

## [2.154.4] - 2023-11-08
### Fixed
- Small fix when trying to access a graph target with an invalid index

## [2.154.3] - 2023-11-06
### Fixed
- Small fixes for bugs revealed by increased test code coverage

## [2.154.2] - 2023-11-05
### Added
- Tests for coverage of AttributeType.cpp file and tuple.h
### Fixed
- Handling of tuple type comparisons for half-precision floating point values

## [2.154.1] - 2023-11-02
### Changed
- Added error checks for invalid node prims

## [2.154.0] - 2023-11-02
### Added
- Ability to run C++ unit tests through Kit unit test framework
### Fixed
- Casts for pxr::GfHalf types that did not work
### Changed
- Moved disabled unit tests to the new framework and enabled them

## [2.153.4] - 2023-11-01
### Fixed
- Infinite loop when using path attribute with an inexisting relative path

## [2.153.3] - 2023-10-30
### Fixed
- Potential crash with math operations on arrays

## [2.153.2] - 2023-10-24
### Fixed
- Invalid access errors occurring in omni.graph.tests in debug mode

## [2.153.1] - 2023-10-24
### Fixed
- Unmapping of attribute that are in a deferded mapping state

## [2.153.0] - 2023-10-20
### Changed
- Upgraded to latest OmniGraphSchema. Changed references to use latest Compound Node Type schema

## [2.152.3] - 2023-10-20
### Changed
- Runtime attribute do not prefetch pointers when using the 'any' type of memory
- Bundle attribute insertion does not remove target attribute if it is compatible (instead of perfect type equality)

## [2.152.2] - 2023-10-19
### Fixed
- Fix crash when accessing invalid variables

## [2.152.1] - 2023-10-18
### Fixed
- Made UniqueQueue thread safe.

## [2.152.0] - 2023-10-18
### Added
- Ability to map a node attribute directly to a target attribute
- Ability to bind a 'prim view' to a graph, an object that is responsible to return a collection of prims that are used to populate the instances
- Execution of push graphs can now take into account various vectorized segment size per node, and multithread them
- Ability to retrieve the vectorized target list as path as well as token

## [2.151.3] - 2023-10-17
### Fixed
- Fixed crash on exit on scenes that use Path attributes types

## [2.151.2] - 2023-10-17
### Changed
- Batched node instantiation to speed up the stage attach.

## [2.151.1] - 2023-10-16
### Fixed
- Update issue with type resolution of dynamic attrs. OM-108200

## [2.151.0] - 2023-10-13
### Added
- Safety checks for nodes with unregistered node types
- Execution graph topology change notification when node types that are in use are deregistered

## [2.150.3] - 2023-10-11
### Changed
- Fixed nodes in a compound graph not having InternalState data properly removed

## [2.150.2] - 2023-10-10
### Changed
- Added extra information to the node type forwarding error message to make them easier to correlate

## [2.150.1] - 2023-10-04
### Fixed
- Graph USD changes are processed on main thread to fix hangs that can occur when extensions with USD notice handlers are loaded.

## [2.150.0] - 2023-10-02
### Changed
- Upgraded Compound Node Types to use latest OmniGraph USD compound schema

## [2.149.3] - 2023-09-27
### Changed
- Skip parsing compound node graphs during stage attach.

## [2.149.2] - 2023-09-22
### Changed
- Replaced Usd.Stage traversals with usdrt queries to speed up the stage attach phase.

## [2.149.1] - 2023-09-21
### Fixed
- Prevent useless allocatin and copy on the stack when setting an attribute value from python

## [2.149.0] - 2023-09-21
### Changed
- OM-110007 Fix graph instances removal

## [2.148.2] - 2023-09-18
### Changed
- OM-108141 Fix bump bundle dirty id for write flag for getArraySizes for CPU and GPU

## [2.148.1] - 2023-09-13
### Fixed
- OmniGraph global time update logic for DriveSim-specific animation.

## [2.148.0] - 2023-09-11
### Added
- New BundleWriteBlock API to minimize the number of bundles that are made dirty during the lifetime of the block

## [2.147.4] - 2023-09-08
### Fixed
- Creating attribute with a defualt value not properly setting the default in all situation
- Setting a default value was not working for all types
- Memory corruption when seting a value with the wrong type from USD

## [2.147.3] - 2023-09-08
### Changed
- Make sure that OGN overrides are called before removing them when an extension with a python node is unloaded.

## [2.147.2] - 2023-09-07
### Changed
- Fix crash that can occur setting default data from a USD attribute

## [2.147.1] - 2023-09-06
### Fixed
- Execution types always write out their type to custom metadata

## [2.147.0] - 2023-09-06
### Removed
- Serialization data: OG prims are not synched to fabric anymore
- __resolved__ tag on extended attributes
### Changed
- The way default data is stored, and can be modified using
### Added
- setDefaultValue ABI

## [2.146.0] - 2023-08-31
### Added
- Officially supported interface for node type forwarding
### Fixed
- Faulty cycle detection and access of null pointer strings

## [2.145.3] - 2023-08-25
### Changed
- Nodes inside a compound now ignore cross-graphs connections to a non-compound nodes.

## [2.145.2] - 2023-08-24
### Added
- An extra execution graph compilation step for DriveSim2's updateSimStepUsd_abi method.

## [2.145.1] - 2023-08-23
### Fixed
- Uninitialized dirty ids would cause bundles and attributes to be put into the change tracking cache, thus produce per-frame cleanup overhead.

## [2.145.0] - 2023-08-17
### Added
- Added an execution node in OmniGraph for the rendering execution graph.

## [2.144.3] - 2023-08-15
### Fixed
- Auto instancing managment on reload_from_stage

## [2.144.2] - 2023-08-10
### Fixed
- Resolution errors when renaming ports on subgraphs

## [2.144.1] - 2023-08-04
### Fixed
- OM-100540 Bug fix - nodes during graph removal could traverse through deleted instances

## [2.144.0] - 2023-07-31
### Fixed
- Added missing null pointer checks to avoid crash on exit

## [2.143.0] - 2023-07-30
### Added
- Node type forwarding for the core GPU interop nodes

## [2.142.0] - 2023-07-25
### Changed
- Revert output and state bundle name space separator to underscore

## [2.141.0] - 2023-07-21
### Removed
- References to obsolete node types

## [2.140.7] - 2023-07-21
### Changed
- Renamed Node::createForDef references to Node::create.

## [2.140.6] - 2023-07-19
### Changed
- Added more profiler tags for the stage attach phase.

## [2.140.5] - 2023-07-18
### Changed
- OM-101615 Suppress Fabric warnings when bundles are removed

## [2.140.4] - 2023-07-18
### Changed
- OM-97363 Bundle asymmetry - file format update use UsdRt to traverse primitives

## [2.140.3] - 2023-07-17
### Changed
- OM-97363 Bundle asymmetry - update connect and disconnect prim

## [2.140.2] - 2023-07-17
### Removed
- References to migrated tutorials node types

## [2.140.1] - 2023-07-14
### Fixed
- Graph::ReloadFromStage preserves instance references

## [2.140.0] - 2023-07-13
### Changed
- OM-97363: Resolve input-output bundle asymmetry

## [2.139.6] - 2023-07-13
### Removed
- Removed the "defaultEvaluator" and "useCachedConnectionsForFileLoad" OG settings.

## [2.139.5] - 2023-07-12
### Fixed
- Resolved types now serialize correct values in compound graphs

## [2.139.4] - 2023-07-11
### Changed
- Compound Subgraphs are created with no_delete metadata

## [2.139.3] - 2023-07-06
### Changed
- Improved performance for `IBundle2::createAttribute*` by skipping the existing attribute(s)

## [2.139.2] - 2023-07-06
### Changed
- DM_ASSERT is using CARB_ASSERT when DataModel debug is off

## [2.139.1] - 2023-06-30
### Changed
- Refactor all code regarding graph runtime data in its own class

## [2.139.0] - 2023-06-28
### Added
- New ISchedulingHints2 ABI that extends ISchedulingHints by including functionality
for the new "pure" scheduling hint.

## [2.138.1] - 2023-06-28
### Fixed
- Added the generated code support files to the C API documentation

## [2.138.0] - 2023-06-27
### Changed
- OM-99661 Materialize attribute before resizing

## [2.137.1] - 2023-06-27
### Changed
- Replaced C17 std::same_v<> with C14 std::same<>::value

## [2.137.0] - 2023-06-26
### Changed
- OM-98519: Do not allow bundle to target connection

## [2.136.0] - 2023-06-23
### Added
- New "pure" scheduling hint for OG nodes.
### Changed
- Ignore constant nodes in Push Graphs when constructing their backend execution graph topology.

## [2.135.5] - 2023-06-23
### Changed
- OM-99356 Remove C++17 features from IDirtyID2 header file.

## [2.135.4] - 2023-06-22
### Fixed
- OM-99127 bundle change tracking do not bump dirty ids for attributes that already exist

## [2.135.3] - 2023-06-22
### Fixed
- Fixed crash when renaming a compound graph

## [2.135.2] - 2023-06-22
### Changed
- Prevent creating USD scene-graph-instanced graph (which are not correctly supported), and log a warning

## [2.135.1] - 2023-06-21
### Changed
- Prevent creating USD scene-graph-instanced graph (which are not correctly supported), and log a warning

## [2.135.0] - 2023-06-21
### Fixed
- Compute messages are now thread safe
### Changed
- Compute messages are now tagged with the instance emitting them
- Compute messages are now managed at the graph level, not at the node level anymore

## [2.134.0] - 2023-06-20
### Added
- Change Tracking for bundles

## [2.133.2] - 2023-06-20
### Changed
- Global flag set on the Graph to warn that evaluation is in progress, instead of relying on the task TLS
### Removed
- Old leftover of the "is in evaluation" tracking

## [2.133.1] - 2023-06-19
### Fixed
- Crash when preparing a graph that has no fabric cache attached

## [2.133.0] - 2023-06-14
### Fixed
- Attributes that don't have a USD value don't get properly initialized
### Changed
- OGN defaults are not set to USD anymore

## [2.132.2] - 2023-06-09
### Fixed
- OM-97928: enable docs generation for bundles.

## [2.132.1] - 2023-06-08
### Changed
- temporarily disable auto-instancing for action graph

## [2.132.0] - 2023-06-06
### Changed
- Use __bundle__private__ prefix to make attributes private in a bundle

## [2.131.3] - 2023-06-05
### Fixed
- Log error when graph.reloadFromStage is called from a subgraph

## [2.131.2] - 2023-06-02
### Changed
- `WritePrimsV2` node now supports exporting relationship.

## [2.131.1] - 2023-06-01
### Fixed
- removing an attributes from a node was not cleaning the associated runtime and serialization data
- Node removed then re-added to an empty graph was keeping its old values

## [2.131.0] - 2023-06-01
### Added
- IGraph::getOwningCompoundNode ABI

## [2.130.0] - 2023-05-31
### Added
- Double underscored attributes in a bundle are private

## [2.129.7] - 2023-05-30
### Fixed
- Fixed PrivateNodeDef and PrivateNodeGraphDef to correctly handle EF partition passes in instanced OG graphs.

## [2.129.6] - 2023-05-29
### Removed
- Obsolete node registration since there are no nodes in this extension
### Changed
- Used Fabric token and path text converters rather than the direct USD ones

## [2.129.5] - 2023-05-29
### Fixed
- Invoking the changelog script without a console attached

## [2.129.4] - 2023-05-26
### Added
- Added `registerForUSDWriteBacksToLayer` function to support USD writeback to a local layer.

## [2.129.3] - 2023-05-26
### Added
- Support for attribute in OGN that have `any` or `union` as type, and `any` as memory type
### Fixed
- Runtime attribute with `any` memory type

## [2.129.2] - 2023-05-25
### Fixed
- Fixed errors when promoting bundle attributes to compounds

## [2.129.1] - 2023-05-24
### Changed
- Moved s_settingsDefaultEvaluator and s_settingsUseCachedConnectionsForFileLoad to the list of hard-deprecated OG settings.

## [2.129.0] - 2023-05-24
### Removed
- Removed the FallbackGraphDef, FallbackInstancedGraphDef, and StaticScheduler.
- Removed the "pull" and "execution_pull" modes from the PullEvaluator.

## [2.128.2] - 2023-05-24
### Fixed
- Reset as early as possible broken array attribute reference

## [2.128.1] - 2023-05-23
### Removed
- Removed some OG settings that were referencing now-deleted legacy systems (using the dynamic/realm static schedulers).

## [2.128.0] - 2023-05-19
### Added
- Copy child bundle python bindings and unit tests.

## [2.127.0] - 2023-05-19
### Added
- Fix copy attribute's metadata when copying attributes by name.

## [2.126.0] - 2023-05-18
### Removed
- Removed some of the legacy evaluators/schedulers, more specifically the DynamicScheduler, RealmStaticScheduler,
ExecutionScheduler, and ExecutionEvaluator.

## [2.125.0] - 2023-05-18
### Changed
- OM-94464 IBundle use Bundle Data Model.

## [2.124.0] - 2023-05-18
### Fixed
- Auto instancing now provides the actual node and graph that the instance refers to
- Auto instancing now properly keep the data (including bundles) when an auto instance get (un)merged
- OG natvis
### Changed
- Perf for adding/removing/merging instances
- Bundle python functions takes the instance index

## [2.123.2] - 2023-05-16
### Changed
- Fixed issue where compounds attributes are incorrectly identified

## [2.123.1] - 2023-05-15
### Fixed
- Ghost data when disconnecting an attribute

## [2.123.0] - 2023-05-12
### Added
- EF support for non-instanced/standalone graphs running with the OnDemand pipeline.

## [2.122.6] - 2023-05-11
### Fixed
- Allow bundles to re-create attributes with 0 size

## [2.122.5] - 2023-05-10
### Fixed
- Crash when adding a node to an instantiated graph

## [2.122.4] - 2023-05-10
### Fixed
- Manually resolved attribute type is now persisted to customData without a value change

## [2.122.3] - 2023-05-10
### Changed
- OM-94111: Improve copying bundles through BundleDataModel

## [2.122.2] - 2023-05-09
### Fixed
- OM-94114: BundleDataModel recursive children removal

## [2.122.1] - 2023-05-09
### Fixed
- type resolution bug where downstream connections where not being type checked

## [2.122.0] - 2023-05-08
### Changed
- CompoundSubgraphs share variables with their parent graph

## [2.121.0] - 2023-05-04
### Changed
- Compatibility with usd-ext-omnigraph 5.0.130, which adds OmniGraphSchema.CompoundNodeAPI schema
- Upgraded USD file format to 1.7

## [2.120.0] - 2023-05-03
### Added
- INode::getCompoundGraphInstance
- Support for subgraph evaluator types which don't match the parent graph

## [2.119.0] - 2023-05-02
### Added
- New interface class INodeTypeForwarding
- Node type registry information to remember node type forwarding
### Changed
- Moved all of the current renaming to their respective .ogn files

## [2.118.1] - 2023-05-02
### Added
- Added function constructInputFromOutput to construct an input RuntimeAttribute from an output.

## [2.118.0] - 2023-05-01
### Added
- Auto-instancing: similar graphs gets merged together as auto instances, and can be computed vectorized

## [2.117.3] - 2023-04-28
### Fixed
- CreateAttribute API adds proper metadata for target and objectID types

## [2.117.2] - 2023-04-27
### Added
- Cache lookups of the compound node type definitions

## [2.117.1] - 2023-04-26
### Changed
- All OG handles are now unique per object, and not recycled (not the pointer anymore)

## [2.117.0] - 2023-04-24
### Added
- Add special node type to represent compound subgraphs

## [2.116.3] - 2023-04-24
### Fixed
- Crash when deleting a graph with instances through the UI

## [2.116.2] - 2023-04-24
### Fixed
- Do not assert when trying to materialize a deleted array

## [2.116.1] - 2023-04-24
### Added
- Variation of the deprecation macro that outputs then name of the function it's in

## [2.116.0] - 2023-04-21
### Added
- ArrayWrapper::empty

## [2.115.2] - 2023-04-20
### Fixed
- Crash related to creating child bundles

## [2.115.1] - 2023-04-20
### Fixed
- Fixed crash that can occur when a data copy fails

## [2.115.0] - 2023-04-19
### Changed
- Move children management to Bundle Data Model

## [2.114.0] - 2023-04-19
### Deprecated
- Removed all references to the obsolete settings constants

## [2.113.2] - 2023-04-17
### Changed
- Move old IDirtyID interface as refactoring process before new IDirtyID arrives.

## [2.113.1] - 2023-04-14
### Changed
- Call `release` on node before removing them from their owning graph list of nodes

## [2.113.0] - 2023-04-13
### Added
- Unit tests to clear content of the bundle.

## [2.112.0] - 2023-04-12
### Changed
- Changed graph target path to be a relative path

## [2.111.0] - 2023-04-12
### Changed
- Introduce Bundle Data Model for IBundle2.

## [2.110.2] - 2023-04-11
### Fixed
- Take into account the graph disabled state in EF

## [2.110.1] - 2023-04-11
### Changed
- Refactored some duplicated EF-related code to use existing methods.

## [2.110.0] - 2023-04-06
### Added
- OmniGraphDatabase cache dynamic inputs, outputs and states.

## [2.109.2] - 2023-04-06
### Changed
- Using the new Fabric's addAttributesToBucket which allows to add several atributes to a bucket at once

## [2.109.1] - 2023-04-05
### Changed
- IBundle2 clears metadata by default

## [2.109.0] - 2023-04-05
### Added
- Target types support the use of placeholder graph target prim

## [2.108.1] - 2023-04-04
### Changed
- IBundle and IBundle2 code cleanup

## [2.108.0] - 2023-04-03
### Added
- kInstancingGraphTargetPath
### Removed
- Deprecated code from 2021

## [2.107.0] - 2023-03-31
### Changed
- target attributes now use relationships with output and state ports

## [2.106.2] - 2023-03-30
### Fixed
- Loading input target attributes as outputOnly now maintain their connections when loaded

## [2.106.1] - 2023-03-29
### Added
- Added Fabric Type class to C++ docs

## [2.106.0] - 2023-03-29
### Fixed
- Disable the node type definitions when the extension implementing them is unloaded
- Enable the node type definitions when the extension implementing them is loaded

## [2.105.3] - 2023-03-28
### Fixed
- Deleting a node or a graph was leaking its bundle attributes
- Deleting a bundle was leaking its children
- Serialization data was leaking empty bundle attribute
- Deleting child bundles was deleting upstream bundles when passed by reference

## [2.105.2] - 2023-03-28
### Fixed
- Copy the default value from the indirect pointer for array attribute

## [2.105.1] - 2023-03-27
### Changed
- Added ability for target attributes to target bundle attributes
### Fixed
- target attributes use correct port name in fabric

## [2.105.0] - 2023-03-24
### Added
- IVariable2 class with method for changing a variable type
- IGraphEvent.eVariableTypeChanged event

## [2.104.0] - 2023-03-24
### Added
- added firstOrDefault accessor to ArrayAttribute helper

## [2.103.1] - 2023-03-24
### Fixed
- Crash in topology depth computation when having several cycles in the graph

## [2.103.0] - 2023-03-24
### Removed
- Deprecated code accessing the old Fabric interfaces

## [2.102.7] - 2023-03-23
### Changed
- Comments on PushGraphDef and PullGraphDef EF graph builders as to why single-node cycles are still (silently) not constructed in the corresponding IR.

## [2.102.6] - 2023-03-23
### Added
- Fixed node state being unnecessarily reset by changes to unrelated USD objects

## [2.102.5] - 2023-03-23
### Fixed
- Fix crash copying array attributes when restoring saved data from stage

## [2.102.4] - 2023-03-22
### Changed
- Improved children creation for bundles

## [2.102.3] - 2023-03-22
### Fixed
- Fabric restored from an older snapshot was making OG crash

## [2.102.2] - 2023-03-22
### Fixed
- Made all docstrings to publicly visible documentation consistent

## [2.102.1] - 2023-03-17
### Changed
- PushGraph and PullGraph executor visitation strategies to ignore cycles.
- Silently disallow the creation of loops when the IR of PushGraphs and PullGraphs is being built in EF to prevent Kit app crash (temporary fix).

## [2.102.0] - 2023-03-17
### Added
- Implemented new target typed backed by relationships

## [2.101.5] - 2023-03-15
### Added
- Compute and maintain a topological depth integer on nodes
### Changed
- Use the topoplogical depth to order type resolution

## [2.101.4] - 2023-03-13
### Changed
- Do not serialize default OGN value to USD

## [2.101.3] - 2023-03-10
### Changed
- Allows to change the type resolution of an attribute if the new one keeps auto-converison compatibility with upstream node

## [2.101.2] - 2023-03-10
### Added
- ABI to register several USD-write-backs at once
### Fixed
- Graph::reset was missing some important cleanup

## [2.101.1] - 2023-03-09
### Fixed
- Prevent deepCopy of a variable value if it is badly typed in source data

## [2.101.0] - 2023-03-07
### Added
- Revert New BundleDataModel built on top of DataModel.

## [2.100.1] - 2023-03-07
### Fixed
- Variables now copy initial values instead of using connections to Fabric prims
- Connections are updated when copying arrays in Fabric

## [2.100.0] - 2023-03-07
### Added
- New BundleDataModel built on top of DataModel.

## [2.99.1] - 2023-03-06
### Added
- Support for compute incomplete in pull graph def

## [2.99.0] - 2023-03-05
### Added
- CompoundNodeType reads default data from USD custom object data
- IAttributeTemplate.getDefaultData()

## [2.98.1] - 2023-03-01
### Added
- updateChangeProcessing call to updateSimStepUsd_abi
### Fixed
- Fixes DRIVESim 2 OG nodes to correctly be created and run with the hard deprecation of global implicit graphs.

## [2.98.0] - 2023-02-28
### Added
- og._flush_usd call to apply pending usd changes.
### Fixed
- Improved compatibility when Fabric Scene Delegate is enabled.

## [2.97.9] - 2023-02-27
### Fixed
- Compute helper was not working correctly on a set of vectorized arrays
### Added
- Allow access to data of a specific instance in python

## [2.97.8] - 2023-02-27
### Fixed
- Properly invalidates OGN databases when a new upstream connection is made to an existing upstream node

## [2.97.7] - 2023-02-25
### Changed
- Modifed format of Overview to be consistent with the rest of Kit

## [2.97.6] - 2023-02-23
### Changed
- BundleContents delays attribute cache creation until needed

## [2.97.5] - 2023-02-23
### Fixed
- ABI violation with OGN DBs
### Changed
- OGN databases are not deleted on graph bucket reconfiguration
- On topological changes, OGN databases are lazily deleted, threaded, at compute time
### Added
- Protection of graph bucket reconstruction for concurrent accesses

## [2.97.4] - 2023-02-22
### Added
- Fixed instances not updated after stage frame rate changed

## [2.97.3] - 2023-02-22
### Changed
- Renamed omni.kit.exec references to omni.kit.exec.core

## [2.97.2] - 2023-02-21
### Fixed
- Python node in instantiated graph are now working
### Changed
- Python node internal states are now per graph instance

## [2.97.1] - 2023-02-19
### Changed
- Added label to the main doc page so that higher level docs can reference the extension

## [2.97.0] - 2023-02-17
### Changed
- Soft deprecate INode::(de)registerPathChangedCallback

## [2.96.1] - 2023-02-15
### Fixed
- Type resolution propagation to not enter compound graphs

## [2.96.0] - 2023-02-15
### Changed
- Execution Framework backend is enabled by default

## [2.95.2] - 2023-02-14
### Fixed
- Don't access invalid bucket in DataModel::copyAndWrite

## [2.95.1] - 2023-02-14
### Changed
- Graph reset function will make sure NodeGraphDef is invalidated by the end of the call

## [2.95.0] - 2023-02-13
### Added
- Support for stage update loop skipping in OmniGraphDef

## [2.94.0] - 2023-02-13
### Added
- Resetting of cuda device in OmniGraphDef to device:0

## [2.93.0] - 2023-02-10
### Changed
- Soft deprecated `PrimHandle`

## [2.92.2] - 2023-02-010
### Fixed
- Ordering of dependency node compute for AG fan-out with shared dependencies

## [2.92.1] - 2023-02-09
### Added
- Gives access to underlying ABI handle in OGN SimpleAttribute

## [2.92.0] - 2023-02-09
### Changed
- Removed onAttributeChanged_abi, onNodeChanged_abi
- PullGraphDef now checks for attribute changes in PullExecutionVisit

## [2.91.0] - 2023-02-08
### Added
- IAttributeTemplate metadata ABI calls

## [2.90.0] - 2023-02-08
### Changed
- SafeDispatch now uses Isolate scheduling constraint for nodes that execute first time.

## [2.89.1] - 2023-02-07
### Changed
- Don't prepare a graph on target access unless absolutly necessary
- While propagating type resolution, postpone the prepare of graph to the end

## [2.89.0] - 2023-02-06
### Added
- IAttributeTemplate and ICompoundNodeType interfaces in unstable namespace.
- addExtendedInput, addExtendedOutput, addExtendedState can be overridden in custom INodeType

## [2.88.3] - 2023-02-06
### Fixed
- Set the proper instance index in the action graph executor before doing anything

## [2.88.2] - 2023-02-03
### Fixed
- Assert in debug build (was not detecting a critical situation though)

## [2.88.1] - 2023-02-02
### Fixed
- Storing of OGN databases was not thread safe when running several instances of the same graph concurrently
- Graph was not prepared when starting computation with EF

## [2.88.0] - 2023-02-02
### Added
- Introduced new safe dispatch to serialize granularily node on their first compute.

## [2.87.8] - 2023-01-31
### Changed
- Retrieving the nodes of a graph is now done by enumerating them instead of filling a provided container

## [2.87.7] - 2023-01-31
### Removed
- Workarounds added for initial EF implementation, not necesary anymore

## [2.87.6] - 2023-01-30
### Added
- Ability to schedule full vectorized batches through EF for instantiated pushgraph

## [2.87.5] - 2023-01-30
### Changed
- Removed the kit-sdk landing page
- Moved all of the documentation into the new omni.graph.docs extension
- Added support for doxygen generation of a subset of the ABI
- Created a minimal landing page for the core functionality

## [2.87.4] - 2023-01-30
### Fixed
- Different role in runtime attribute won't prevent vectorization anymore
### Added
- Ability to access proper variable in a vectorized loop

## [2.87.3] - 2023-01-27
### Fixed
- Prevent copy error by not triggering USD notice handler when setting initial value while creating an attribute

## [2.87.2] - 2023-01-27
### Fixed
- Fix crash when adding an instance to an empty graph

## [2.87.1] - 2023-01-26
### Fixed
- Fix regression - release was not called on node when destroyed through USD notice handler

## [2.87.0] - 2023-01-26
### Changed
- NodeDef's are created with type name returned by getTypeName instead of getNodeType

## [2.86.2] - 2023-01-25
### Fixed
- Fix regression - release was not called on node when destroyed through ABI

## [2.86.1] - 2023-01-20
### Fixed
- When disconnecting an attribute, modify the topology BEFORE modifying USD so notice handler can operate on an up-to-date authoring graph

## [2.86.0] - 2023-01-20
### Added
- INode::getAttributeChangeStamp
- IGraphEvent::eClosing, IGraphEvent::eComputeRequested
- IGenericNodeGraphDef_abi::inspect_abi
- IExecutor::continueExecute_abi
### Fixed
- Locking logic in ExecutionContext::applyOnEach
### Changed
- action evaluator logic for requestCompute, OnClosing and request-driven node dirty based on attribute changes

## [2.85.2] - 2023-01-18
### Changed
- Isolates AttributeData interface in its own file
- Restore RuntimeAttribute RO-array-accessor returning const_array<cont T> instead of const_array<T>

## [2.85.1] - 2023-01-17
### Fixed
- Push back to usd was called too often, for instantiated graphs and subgraph

## [2.85.0] - 2023-01-11
### Added
- Internal API calls to validate attribute name

## [2.84.1] - 2023-01-11
### Added
- Profiler instrumentation to OmniGraphDef

## [2.84.0] - 2023-01-11
### Added
- Native support for vectorization compute in nodes
- Ability to index a given instance in OGN database and wrappers
- All OGN attributes now also have a vectorized(count) accessor which returns a span<>, and allows an efficient loop/SIMD
### Fixed
- Default values for states were not taken into account
- Few places were not properly treating relationship attribute as array of paths
- Bundle attributes are now all typed as eRelationship (no ePrim anymore)
### Removed
- Gather prototype is gone
### Changed
- Runtime data is stored in a unique fabric bucket managed by the graph
- Variables are now stored in this bucket
- Each instance has its own set of data
- The GraphContext now has an index which references the current active instance
- Compute helpers now support vectorization, are more efficient, and are variadic (any number of parameters)
- OGN DB state are per instance
- OGN DB caching is now per context index
- All OGN attributes have a reference to the current DB target, but can also be accessed with an offset compared to the current DB target (which also has an offset compared to the current context target)
- DataModel don't try to create an attribute on copy
- Most data access ABI now take an instance index
- Internals of OGN wrappers are now private
- Extended attributes now uses a specialization of SimpleAttribute that stores the RuntimeAttrib, which allows the proper vectorized access
- Each Input and output bundle now have a dedicated relationship attribute, that can be vectorized
- There is no more special treatment regarding bundle attributes and connections to other attributes
- OGN Array attributes don't store the data pointer anymore. The responsability of the pointer managment has been given to the ogn array helper struct
- The ogn array helper struct (for string and array attributes) now has the context and the target handle. This allows to request the data from DataModel as lazily as possible, and apply CoW only on the ultimate data access

## [2.83.1] - 2023-01-10
### Fixed
- Enabled precompiled headers and cleaned up includes

## [2.83.0] - 2023-01-03
### Added
- Compound Node Types inputs and output definitions handle description and display name metadata

## [2.82.3] - 2022-12-21
### Changed
- Refactored CUDA build to consolidate build functions and remove unnecessary rebuilds

## [2.82.2] - 2022-12-16
### Fixed
- Updated output to properly handle subnode types

## [2.82.1] - 2022-12-15
### Fixed
- Performance for processing of large node fan-in (action graph)

## [2.82.0] - 2022-12-14
### Added
- Added areAnyTypesCompatible typeConversion helper

## [2.81.1] - 2022-12-14
### Added
- Implementation for new EF interface allowing push and lazy graph defs to be partition

## [2.81.0] - 2022-12-13
### Added
- IAttribute 1.3->1.4: ABI functions added to access the attribute union definitions.

## [2.80.2] - 2022-12-11
### Fixed
- OM-75582 Fix for write back to Usd

## [2.80.1] - 2022-12-09
### Fixed
- Condition for allowing evaluation of pull graph in the EF

## [2.80.0] - 2022-12-09
### Changed
- Updated DataModel's metadata implementation.
- Deprecated access to bundle metadata storage in IBundle2.
- IConstBundle2 and IBundle2 made public.
- Cleaned up implementation and removed code duplication.

## [2.79.4] - 2022-12-08
### Fixed
- Accessing the size of an inexistent array was returning 1

## [2.79.3] - 2022-12-07
### Fixed
- OM-75593 Fixed DataModel::copyAttributeInternal for array attribute that used to set array size to 0 when src and dst
  was the same.

## [2.79.2] - 2022-12-06
### Changed
- GraphContext::invalidateBucket() now also invalidates the databases of downstream nodes.
- Don't assign the node's database until *after* its bucket has been invalidated.

## [2.79.1] - 2022-12-03
### Fixed
- Fixed crash when loading resolved string attributes

## [2.79.0] - 2022-11-24
### Removed
- Setting useSchemaPrims
- Code implementing support for that setting

## [2.78.4] - 2022-11-23
### Fixed
- Bug in evaluation of fan-out nodes in some cases
### Changed
- Improved overhead of OG when stage contains no OmniGraph prims

## [2.78.3] - 2022-11-22
### Fixed
- EF invalidation for graph instance changes

## [2.78.2] - 2022-11-21
### Added
- Documentation link in how-tos for running a minimal Kit with OmniGraph
- Documentation for the various types of node implementations and what they are for

## [2.78.1] - 2022-11-19
### Fixed
- Issues detected with EF and test_compute_counts: hang on a lock in recursive pattern and incorrect Graph::isInEvaluation

## [2.78.0] - 2022-11-18
### Added
- Interfaces for EF: IGenericNodeGraphDef, IGenericNodeDef, IPrivateNodeGraphDef
- New internal method to IInternal: createPrivateGraphDef
- Refactored population of EF to support any graph type
- Introduced basic support for lazy / dirty_push graph

## [2.77.0] - 2022-11-17
### Removed
- Settings updateToUSD, supportForceWriteback, useLegacySimulationPipeline, and enableUSDInPreRender
- Code implementing support for those settings

## [2.76.3] - 2022-11-16
### Fixed
- Bug in Graph::reloadFromStage for EF

## [2.76.2] - 2022-11-16
### Fixed
- Fixed memory leak when compound nodes are deleted

## [2.76.1] - 2022-11-14
### Added
- Start of unstable ABI for Execution Framework (omni.graph.exec)

## [2.76.0] - 2022-11-12
### Removed
- Setting that controls the ability to work with implicit global graphs
- Code implementing support for implicit global graphs

## [2.75.3] - 2022-11-09
## Fixed
- BundlePrims attribute copying regression

## [2.75.2] - 2022-11-04
### Fixed
- potential crash on detach stage in same update that nodes are removed

## [2.75.1] - 2022-11-03
### Fixed
- Crash in omnigraph when loading usda files with start time offset

## [2.75.0] - 2022-10-31
### Changed
- tuple indexes are now uint8_t instead of int in the cpp headers

## [2.74.0] - 2022-10-28
### Added
- Interpretation of the deprecationsAreErrors setting that disables all non-schema support

## [2.73.3] - 2022-10-26
### Fixed
- Do not reinitialize node's bucket to empty bucket.

## [2.73.2] - 2022-10-25
### Added
- Fixed double parse of nested graphs on stage during load.

## [2.73.1] - 2022-10-21
### Fixed
- Bug related to action graph loops

## [2.73.0] - 2022-10-20
### Added
- INodeType 1.8->1.9: isCompoundNodeType()
- IGraphRegistryEvent.eNodeTypeNamespaceChanged, IGraphRegistryEvent.eNodeTypeCategoryChanged

## [2.72.1] - 2022-10-19
### Fixed
- Made the category check more lenient, ignoring empty descriptions

## [2.72.0] - 2022-10-17
### Added
- IGraphRegistry 1.4 -> 1.5: deprecated registerNodeType in favor of registerNodeTypeInterface

## [2.71.4] - 2022-10-16
### Fixed
- Array memory copy with a wrong element type for arrays of booleans.

## [2.71.3] - 2022-10-14
### Changed
- On-demand graphs fallbacks to evaluators. This is only a temporary change.

## [2.71.2] - 2022-10-12
### Added
- Profiling instrumentation for EF
### Changed
- Graph definitions to call updateChangeProcessing instead of global omni graph definition

## [2.71.1] - 2022-10-11
### Fixed
- Fixed a crash due to a false assumption that a child bundle always has "primIndex" attribute.

## [2.71.0] - 2022-10-04
### Fixed
BundlePrims dirtyIDs

## [2.70.0] - 2022-10-03
### Added
- IGraphContext 3.3 -> 3.4: getVariableInstanceDataHandle, getVariableInstanceConstDataHandle

## [2.69.0] - 2022-09-30
### Added
- INodeType 1.7 -> 1.8: getSubNodeTypeByPath to find Compound nodes by their Path
- IGraphRegistryEvent::eNodeTypeNamespaceChanged raised when a nodetype namespace changes
### Changed
- Compound nodes can be referenced by extension-style qualified names or by Path to the OmniGraphCompoundNodeType prim

## [2.68.1] - 2022-09-29
### Fixed
- Inconsistent evaluation of nodes with fan-in

## [2.68.0] - 2022-09-27
### Changed
- Restored `BundlePrim::setPath` from deprecation.
### Removed
- Removed `getPrimDirtyIDs`, `getConstPrimPaths` & `getConstPrimTypes` in the ConstBundlePrims class.
- Removed `getPrimDirtyIDs`, `getPrimPaths`, `getPrimTypes`, `addPrimPathsIfMissing` & `addPrimTypesIfMissing` in the BundlePrims class.

## [2.67.0] - 2022-09-27
### Added
- OG Usd Listener path attribute target prim rename and reparenting.

## [2.66.2] - 2022-09-26
### Added
- Fixed unloading of a graphs in layer that undergo a file format update.

## [2.66.1] - 2022-09-25
### Fixed
- Dynamic attributes and PushEvaluator bug fix to call for reset() only when update is required.

## [2.66.0] - 2022-09-22
### Changed
- Extended attribute type values are now persisted to USD as customData
- Dynamic extended attribute types are now persisted to scoped customData as well as deprecated unscoped

## [2.65.0] - 2022-09-21
### Added
- Initial support for Compound Nodes and Compound NodeTypes
- INode::isCompoundNode to test if a node is a compound node
- IGraph::isCompoundGraph to test if a node is a compound graph

## [2.64.7] - 2022-09-20
### Fixed
- A bug in action graph logic related to fan-in

## [2.64.6] - 2022-09-14
### Added
- On demand compute using Execution Framework

## [2.64.5] - 2022-09-11
### Changed
- Assignment operator for AttributeDef now returns a reference to the assignee instead of void

## [2.64.4] - 2022-09-09
### Fixed
- Consistent index of BundlePrim instances among multiple BundlePrims instances attached to the same bundle.
- Consistent index of BundlePrim instances throughout the lifetime of a BundlePrims instance.

## [2.64.3] - 2022-09-07
### Changed
- Fixes OM-62261 `og.OmniGraphInspector().as_json` Returns Bad Json

## [2.64.2] - 2022-09-07
### Added
- NodeTypeDef attributes now maintain separate memory for attribute defaults.

## [2.64.1] - 2022-09-06
### Changed
- Gave a better error message for deprecated node type presence
- Reenabled the still-flaky tests

## [2.64.0] - 2022-08-31
### Added
- IDataModel and thread-safety to data model changes that can affect other nodes
- Ability to discover when data model structure changed (via global id stamp)

## [2.63.0] - 2022-08-30
### Changed
- HandleToPtrMap to use concurrent container to avoid contention during parallel execution

## [2.62.0] - 2022-08-30
### Removed
- Temporary hack for Python node late delayed default value setting
### Added
- Extra information to flag when the node type definition is responsible for deletion of default data memory

## [2.61.1] - 2022-08-24
### Changed
- Fixes ReadOnly array attribute sometimes having a dangling pointer

## [2.61.0] - 2022-08-23
### Added
- IGraphRegistry::getEventStream to get an event stream that triggers when node types are added and removed.

## [2.60.1] - 2022-08-22
### Fixed
- GraphContext's getOutputPrim did not use DataModel.

## [2.60.0] - 2022-08-19
### Added
- Support for new setting that turns deprecations into errors
- New macro for flagging use of deprecated code path
- Deprecation messages for code paths not using schema prims

## [2.59.2] - 2022-08-18
### Fixed
- Added missing call to tell nodes created from a Prim that they already have a default set

## [2.59.1] - 2022-08-17
### Added
- Architectural decision for splitting off the extensions into a separate repo
### Fixed
- Made Fabric dump of connections provide a default when presented with bad data
### Changed
- Updated the apply_change_info script to preserve local branch edits of extension.toml

## [2.59.0] - 2022-08-16
### Added
- Added isValid() methods to OG Obj ABI structs

## [2.58.1] - 2022-08-15
### Changed
- Allow write variable to operate even if role types differs

## [2.58.0] - 2022-08-12
### Changed
- Node path is now added to console-logged messages
- Node path is no longer added to messages captured on nodes

## [2.57.4] - 2022-08-11
### Changed
- Handles auto conversion in data model

## [2.57.3] - 2022-08-08
### Added
- Warning when schema prims are loaded when the setting is disabled.

## [2.57.2] - 2022-08-05
### Fixed
- action evaluator for cycles in connections

## [2.57.1] - 2022-08-04
### Fixed
- Avoided multiple `__metadata__bundle__` tokens in a path

## [2.57.0] - 2022-08-03
### Changed
- OGN Bundle wrapper `size` and `abi_primHandle` are marked as deprecated.

### Added
- Two methods to OGN Bundle wrapper: `attributeCount` and `childCount`.

## [2.56.0] - 2022-08-02
### Added
- Update OGN Bundle wrapper to use IBundle2

## [2.55.0] - 2022-08-02
### Added
- /persistent/omnigraph/enablePathChangedCallback to deprecate INode::registerPathChangedCallback
- /persistent/omnigraph/disableInfoNoticeHandlingInPlayback optimization setting
### Changed
- pathChangedCallback will now trigger once per OG update with accumulated changes instead of immediately

## [2.54.0] - 2022-07-28
### Added
- Added `IDirtyID` interface
- Added `BundleAttrib` class and `BundleAttribSource` enumeration
- Added `BundlePrim`, `BundlePrims`, `BundlePrimIterator` and `BundlePrimAttrIterator`
- Added `ConstBundlePrim`, `ConstBundlePrims`, `ConstBundlePrimIterator` and `ConstBundlePrimAttrIterator`

## [2.53.1] - 2022-07-28
### Fixed
- Fixed handling of empty strings in operator< and operator> of ogn::base_string

## [2.53.0] - 2022-07-22
### Added
- IBundle2 - remove_attributes_by_name and remove_child_bundles_by_name

## [2.52.1] - 2022-07-27
### Fixed
- Fixed data model for storing attribute metadata in IBundle2

## [2.52.0] - 2022-07-27
### Changed
- valueChanged callback handling

## [2.51.3] - 2022-07-23
### Fixed
- Fixed dirty_push graphs being re-run during playback when time has not advanced

## [2.51.2] - 2022-07-22
### Fixed
- Registration order of TfNotice handler for OG

## [2.51.1] - 2022-07-21
### Fixed
- OM-56991 Ill-formed sdf paths

## [2.51.0] - 2022-07-21
### Changed
- Undo revert and fix bug in evaluation of nodes with dynamic execution attribs

## [2.50.0] - 2022-07-19
### Fixed
- IBundle2 reviewed ABI, reviewed copy and link for attributes and bundles

## [2.49.0] - 2022-07-18
### Changed
- Reverted the changes in 2.48.0

## [2.48.1] - 2022-07-18
### Added
- Better ReadPrimAttribute error reporting

## [2.48.0] - 2022-07-15
### Changed
- Action graph fan-out of execution wires are now evaluated in parallel instead of sequence

## [2.47.1] - 2022-07-12
### Changed
- Changed node create to write extended attributes to USD prior to node creation

## [2.47.0] - 2022-07-08
### Added
- 'deprecated' .ogn keyword for attributes
- IInternal / omni.graph.core._internal
- IInternal::deprecateAttribute() / omni.graph.core._internal.deprecate_attribute()
- IAttribute::isDeprecated() / omni.graph.core.Attribute.is_deprecated()
- IAttribute::deprecationMessage() / omni.graph.core.Attribute.deprecation_message()
- 'internal' attribute metadata keyword

## [2.46.0] - 2022-07-08
### Fixed
- Fixed memory leak coming from NodeType objects
### Changed
- INodeType 1.6 -> 1.7
- fileFormatVersion attribute on OmniGraph objects only writes to USD if it has changed
### Added
- INodeType::destroyNodeType to deallocate a node type object

## [2.45.2] - 2022-07-07
### Fixed
- IConstBundle2 and IBundle2 broken logging system

## [2.45.1] - 2022-07-06
### Added
- Ability to raise an error/warning for a node through (new) static methods of the database

## [2.45.0] - 2022-06-30
### Added
- Metadata support for IBundle2 interface

## [2.44.3] - 2022-06-30
### Changed
- USD write back is now performed just once per frame per Fabric cache

## [2.44.2] - 2022-06-28
### Fixed
- Checked newly added nodes for file format version upgrade requirements

## [2.44.1] - 2022-06-28
### Changed
- Ensured nodeContextHandle is initialized correctly

## [2.44.0] - 2022-06-29
### Changed
- Deprecated IScheduleNode::getNode, INodeType::getScheduleNodeCount, INodeType::getScheduleNodes

## [2.43.1] - 2022-06-29
### Added
- A compile switch to disable OGN database caching

## [2.43.0] - 2022-06-28
### Fixed
- Array attributes not keeping a single copy of their data/size pointers as intended
- Few places using P2AM directly instead of DataModel
- Debugging features of DataModel
- usdToCache overwritting connection informations
- Bad performance of getLocalAttributeHandle
### Added
- OGN Database caching at the node level
- Tracking of changes that might invalidate this caching
- Gives a chance to DataModel to prepare buckets of nodes at load time, in order to prevent useless rebucket later

## [2.42.0] - 2022-06-23
### Added
- clearContents method to IBundle2 interface

## [2.41.0] - 2022-06-22
### Added
- Faster check for deprecated node types
### Removed
- Unused core node animation/OgnPointsWeight
- Unused core node animation/OgnTextGenerator
- Unused core node animation/OgnTimeSampleArray
- Unused core node animation/OgnTimeSamplePoints
- Unused core node animation/OgnXformDeformer
- Unused core node animation/OgnXformSRT
- Unused core node animation/OgnXformToFastCache
- Unused core node core/OgnFetch
- Unused core node core/OgnGather
- Unused core node core/OgnScatter
- Unused core node core/OgnSlang
- Unused core node core/OgnTime
- Unused core node core/OgnTimeSample
- Unused core node core/OgnXtoY
- Unused core node math/OgnVectorElementDecompose
- Unused core node math/OgnVectorElementSet

## [2.40.4] - 2022-06-22
### Changed
- Fix for output attribute being resolved by downstream connection

## [2.40.3] - 2022-06-22
### Added
- Architectural decision records support
- Added ADR for the decision around how to present the Python API surface

## [2.40.2] - 2022-06-21
### Changed
- Optimized attribute look up

## [2.40.1] - 2022-06-17
### Changed
- Added extra validity checks to bundle data access
### Added
- Finished off the documentation for versioning, both internal and external

## [2.40.0] - 2022-06-17
### Added
- IGraph::getEvaluationName
### Changed
- When using schemaPrims, OmniGraph now responds to changes made to graph settings in USD.

## [2.39.0] - 2022-06-16
### Changed
- ForceWriteBack mechanism (that was used to write back prim data to USD) is now soft deprecated behind a setting
### Added
- A per attribute tracking system that allows to write back to USD at single attribute definition

## [2.38.3] - 2022-06-16
### Fixed
- cpp wrapepr getAttributesR template function, internally it wasn't casting to NameToken*.

### Changed
- Outputs for `IBundle2::create*`, `IBundle2::link*` and `IBundle2::copy*` are optional.

## [2.38.2] - 2022-06-15
### Fixed
- Handled the one missing colorama reference

## [2.38.1] - 2022-06-14
### Fixed
- When removing the last attributes on a path, DataModel was failling to move it properly to the empty bucket

## [2.38.0] - 2022-06-13
### Added
- CreateGraphAsNodeOptions structure
- GraphEvaluationMode enum
- IGraph::getEvaluationMode
- IGraph::setEvaluationMode
- IGraph::createGraphAsNode(GraphObject&, const CreateGraphAsNodeOption*)
### Deprecated
- IGraph::createGraphAsNode(GraphObject&, const char*, const char*, const char*, bool, bool, GraphBackingType, GraphPipelineStage)

## [2.37.1] - 2022-06-13
### Fixed
- Crash fix when trying to convert an invalid "FabricBundle" to a value

## [2.37.0] - 2022-06-13
### Added
- Temporary support for flagging values already set for Python initialize

## [2.36.0] - 2022-06-08
### Added
- Pre-render evaluation functions

## [2.35.0] - 2022-06-07
### Added
- Support for the generator setting for Python optimization

## [2.34.3] - 2022-06-03
### Fixed
- Copy on Write for Child bundles

## [2.34.2] - 2022-06-02
## Changed
- Allow arguments arrayDepthsBuf and tuplesBuf for resolvePartiallyCoupledAttributes() to be null pointers

## [2.34.1] - 2022-06-01
### Fixed
- Input execution attribute are now reset to Disabled state when node enters latent state
- Bug making bundle connection to legacy prim

## [2.34.0] - 2022-05-30
### Changed
- Connections between nodes are now not stored in fabric anymore
- We now rely only on connections expressed in the Object Oriented Layer in OmniGraph core
- DataModel now don't have to do extra logic to interpret FC connections as toppological connection or upstream reference
### Added
- Ability to access and set default value on an attribute
- Interfaced this new feature with python
- Using this new feature in python OGN generator
### Fixed
- Bug preventing to clear an attribute array in python
### Removed
- Some useless dependencies/visibility to PathToAttributeMap

## [2.33.11] - 2022-05-27
### Changed
- Deprecated the GraphContext::updateToUsd() code path with useSchemaPrims off
### Fixed
- Fixed the Fabric dump in GraphContext, broken when Fabric was upgraded
- Fixed the graph population phase in PluginInterface to walk all graphs, not just the first one

## [2.33.10] - 2022-05-26
### Fixed
- Fixed memory leak with variables
- Fixed errors caused by removing variables from Fabric

## [2.33.9] - 2022-05-24
### Fixed
- Attributes on bundle not properly materialized, attempt 2

## [2.33.8] - 2022-05-18
### Fixed
- Attributes on bundle not properly materialized

## [2.33.7] - 2022-05-17
### Fixed
- Fixed reparenting graph to previous parent which otherwise corrupted fabric state and left nodes without properties

## [2.33.6] - 2022-05-17
### Fixed
- Duplicate bundle connections on rename

## [2.33.5] - 2022-05-16
### Fixed
- Connection-compatibility check for execution attributes

## [2.33.4] - 2022-05-16
### Changed
- Makes dynamic bundle works in python

## [2.33.3] - 2022-05-16
### Changed
- Fix type not properly registered in FC when adding new attributes

## [2.33.2] - 2022-05-13
### Changed
- Makes bundle works on node not backed by USD

## [2.33.1] - 2022-05-12
### Changed
- Array attribute are now using ABI, giving a chance to the framework to perform CoW and DS

## [2.33.0] - 2022-05-11
### Changed
- Refactoring of data model: centralized all Fabric accesses in one place
- MBiB now uses connections instead of bucket tagging
### Added
- Lazy pointer retrieval (for read and write) in OGN layer
- Array attribute and bundles are now passed by reference from node to node
- Copy on Write: Array attributes/Bundle content are copied when mutated
- ABI entry for batch attribute copy from one bundle/prim to another
### Fixed
- Fixed som API for data retrieval in OGN layer that where missbehaving when used
### Removed
- Data stealing prototype

## [2.32.2] - 2022-05-11
### Fixed
- Fixed read time node with pull evaluator when time changes outside of playback (e.g. timeline tool)

## [2.32.1] - 2022-05-06
### Fixed
- Fixed instances loaded from references requiring a stage reload to evaluate correctly

## [2.32.0] - 2022-05-05
### Changed
- Refactored settings to handle interdependencies
### Fixed
- Changed std::is_pod to std::is_trivial for C++20 compatibility
### Added
- Added architectural diagram of the OmniGraph extension interdependencies
- Internal diagram of the schema prim code path dependencies
- Adding callbacks in settings to handle interdependencies

## [2.31.3] - 2022-05-04
### Fixed
- Fixed a bit too agressive type unresolution on input attributes

## [2.31.2] - 2022-05-03
### Fixed
- Default variable values not always getting set to instances with no overrides

## [2.31.1] - 2022-05-02
### Fixed
- bug resolving values in certain extended attribute connections

## [2.31.0] - 2022-04-29
### Changed
- Passed graph prim for more targeted Fabric initialization
- Bumped file format to 1.4
- Made file format calls more tolerant of useSchemaPrims settings

## [2.30.3] - 2022-04-25
### Changed
- Only flush USD to fabric when we are parsing the first root graph, otherwise previous changes to fabric may be overwritten

## [2.30.2] - 2022-04-28
### Fixed
- Removed the obsolete parts of the unit tests

## [2.30.1] - 2022-04-26
### Fixed
- Fix situation with bad type resolution

## [2.30.0] - 2022-04-22
### Added
- `OmniGraphDatabase.getGraphTarget`
- IGraphContext 3.1->3.2
  - `IGraphContext.getGraphTarget`

## [2.30.0] - 2022-04-25
### Removed
- Removed the unimplemented IDataReference class
- Removed the obsolete TestComputeGraph.cpp unit test
### Changed
- Stopped building the obsolete nodes
- Moved the generated substitutions.rst file to the build area

## [2.29.4] - 2022-04-21
### Changed
- "ui:"-prefixed attributes present on Node prims are no longer read as OG attributes

## [2.29.3] - 2022-04-19
### Fixed
- Rare crash that occurred when using string-based node attributes

## [2.29.2] - 2022-04-14
### Fixed
- __updateSimStepUsd__ disableUsdUpdates is respected

## [2.29.1] - 2022-04-08
### Fixed
- Auto conversion bug for native tuple

## [2.29.0] - 2022-04-08
### Changed
- Passed graph prim for more targeted Fabric initialization
- Bumped file format to 1.4
- Made file format calls more tolerant of useSchemaPrims settings

## [2.28.0] - 2022-04-08
### Changed
- input attribute types are no longer inferred from output attribute types.
- type resolution and unresolution will no longer propagate upstream.

## [2.27.0] - 2022-04-08
### Added
- Added IGraphContext::getAbsoluteSimTime() function
- Added ComputeGraph::updateV2() function which updates the absoluteSimTime

## [2.26.3] - 2022-04-07
### Fixed
- Graph::writeTokenSetting() was failing to update the token if it already existed but was empty.
### Changed
- Graph::writeTokenSetting() no longer updates the token or issue a warning if the new value is the same
  as the existing one.

## [2.26.2] - 2022-04-05
### Fixed
- Fixes issues where ForceWriteBack token on newly created Nodes
  would not be respected unless the Prim of the Node was selected

## [2.26.1] - 2022-03-31
### Fixed
- Fixed issue when using OG in MGPU: forces use of Device 0 in StaticScheduler

## [2.26.0] - 2022-03-31
### Added
- `PrimHandle` and `ConstPrimHandle` renamed to `BundleHandle` and `ConstBundleHandle`.
  `PrimHandle` and `ConstPrimHandle` remain as aliases to `BundleHandle` and `ConstBundleHandle`.
- `IConstBundle2` - ONI const bundle interface, successor of carbonite `IBundle`.
- `IBundle2` - ONI bundle interface, successor of carbonite `IBundle`.
- `IBundleFactory` - ONI factory to create instances of `IConstBundle2` and `IBundle2` interface.
- Initial implementation of `IConstBundle2`, `IBundle2` and `IBundleFactory`.
- `ComputeGraph` 2.6 -> 2.7.
- `ComputeGraph::getBundleFactoryInterface` method added to instantiate bundle factory.
- `IPath` new methods: `appendPath` and `getPathElementCount`.

## [2.25.2] - 2022-03-25
### Fixed
- Fixed issue where type resolution on node with coupled attribute would not work
- Fixed auto type conversion not working on coupled attributes

## [2.25.1] - 2022-03-25
### Fixed
- dynamic scheduler will now evaluate execution subgraphs

## [2.25.0] - 2022-03-23
### Added
- IGraph 3.6 -> 3.7
  - getEventStream - accessor to retrieve a graphs event stream
- IGraphEvent enum type
- IGraphEvent.eCreateVariable, raised when a variable is created through the ABI
- IGraphEvent.eRemoveVariable, raised when a variable is removed through the ABI

## [2.24.0] - 2022-03-16
### Added
- Setting /persistent/omnigraph/enableLegacyPrimConnections. When enabled, this will restore legacy behavior for OG Prim nodes:
  - Entire stage is searched for connections between Nodes and Prims, any connected
    Prims will be brought into FC, and corresponding OG Prim nodes created with all
    attributes.
  - Terminal nodes will be automatically synced to FC every frame
  - This setting is not exposed in the UI. It is a temporary setting until legacy code can be migrated to no longer use Prim connections.

## [2.23.8] - 2022-03-15
### Fixed
- Fixed issue where ComputeGraphs in sublayers may not correctly load

## [2.23.7] - 2022-03-14
### Fixed
- Auto type conversion was not correctly computed on load

## [2.23.6] - 2022-03-14
### Fixed
- Bug in default string attribute initialization

## [2.23.5] - 2022-03-09
### Added
- Added a check to make sure that literalOnly attributes cannot be connected to other attributes

## [2.23.4] - 2022-03-08
### Fixed
- Cleanup of graph deletion

## [2.23.3] - 2022-03-08
### Changed
- Modified the node type registration/deregistration process to avoid static destructor ordering problems and allow multiple initialize/release calls

## [2.23.2] - 2022-03-07
### Fixed
- Removed unnecessary migration of bundle connection members to a copied bundle

## [2.23.1] - 2022-03-05
### Fixed
- __RenderVar__ prim data will be automatically loaded into FC when they are part of an OG network

## [2.23.0] - 2022-03-04
### Changed
- Removed the _updateTerminalNodesOnly_ setting, the default of _updateToUSD_ is now False.
  OG will now only sync Prims FC->USD with the _ForceWriteBack_ token when _updateToUSD_
  is False. When the setting is True, it will sync all Prims.
- Added _settingsVersion_ setting

## [2.22.3] - 2022-03-04
### Changed
- OG will no longer automatically load non-OG Prim data into FC during stage attach.

## [2.22.2] - 2022-03-02
### Fixed
- Added support for omni.graph.nodes.ReadTime to lazy (dirty_push) evaluator

## [2.22.1] - 2022-02-18
### Changed
- Bug fix in path attribute monitoring: properly retarget subpath when reparenting happens higher in the hierarchy

## [2.22.0] - 2022-02-18
### Added
- Added tests for schema-based prims
- Added test case base class factory method
### Fixed
- Fixed handling of the schema-based prims
- Removed use of deprecated OmniGraphHelper from some scripts

## [2.21.4] - 2022-02-18
### Changed
- Bug fix accessing a deleted entry in a map

## [2.21.3] - 2022-02-17
### Changed
- Added proper support for path role (that keep track of the target)

## [2.21.2] - 2022-02-16
### Changed
- Changed Fabric Cache creation to new `create2` to allow RingBuffers to have CUDA enabled

## [2.21.1] - 2022-02-15
### Fixed
- Categories on several nodes

## [2.21.0] - 2022-02-15
### Added
- Added support for update_usd flag to the data_view and SetAttr command
### Fixed
- Ignored the Expression node for the warning on nodes without namespaces
- Avoided a crash when the fileFormatVersion attribute could not be found

## [2.20.0] - 2022-02-13
### Changed
- Prim nodes will no longer have OG attributes automatically added
- Prim node authored USD attributes added to FC
- Removed support for special attribute OGN_NonUSDConnections

## [2.19.0] - 2022-02-11
### Added
- Added OmniGraphDatabase.getVariable

## [2.18.0] - 2022-02-10
### Added
- Added setting for using schema prims for graphs and nodes.
- Added use of the omniGraphSchema library for graph and node prims (protected by the setting).

## [2.17.0] - 2022-02-08
### Changed
- Added support for auto conversion between attributes.

## [2.16.1] - 2022-02-07
### Changed
- Moved carb logging out of Database.h and into Node::logComputeMessage.

## [2.16.0] - 2022-02-05
### Added
- IGraph 3.5 -> 3.6
  - Added IGraph::createVariable
  - Added IGraph::removeVariable
  - Added IGraph::findVariable
- IVariable
  - Added IVariable::getDisplayName and IVariable::setDisplayName
  - Added IVariable::getCategory and IVariable::setCategory
  - Added IVariable::getTooltip and IVariable::setTooltip
  - Added IVariable::getScope and IVariable::setScope
  - Added IVariable::isValid

## [2.15.1] - 2022-02-04
### Fixed
- Edge cases in action graph evaluator for fan-in and fan-out of execution attributes

## [2.15.0] - 2022-02-02
### Added
- IGatherPrototype 1.1 -> 2.0
  - Changed the signature of _gatherPaths_
  - Added _getGatheredRepeatedPaths_

## [2.14.0] - 2022-02-01
### Added
- ComputeGraph 1.0 -> 1.1
  - Added *IOmniGraphTest::setTestFailure*
  - Added *IOmniGraphTest::testFailureCount*
- Python bindings at the module level
  - Added *set_test_failure*
  - Added *test_failure_count*
- Added deregistration macro for earlier deregistration of node types (done in a backwards compatible way)

## [2.13.0] - 2022-01-31
### Changed
- IVariable.getPath renamed to IVariable.getSourcePath

## [2.12.0] - 2022-01-28
### Fixed
- Error status change callbacks weren't firing during normal evaluations.
- Bumping the minor version # since features which use the callbacks will not
  work without this change.

## [2.11.0] - 2022-01-26
### Added
- INode 4.1 -> 4.2
  - Added INode::logComputeMessage
  - Added INode::getComputeMessageCount
  - Added INode::getComputeMessage
  - Added INode::clearOldComputeMessages
- IGraph 3.4 -> 3.5
  - Added IGraph::registerErrorStatusChangeCallback
  - Added IGraph::deregisterErrorStatusChangeCallback
  - Added IGraph::nodeErrorStatusChanged
  - Added IGraph::getVariableCount
  - Added IGraph::getVariables
- Created the IVariable type

### Changed
- OmniGraphDatabase::logWarning and logError now log compute messages
  whenever they are different from the node's previous evaluation. Previously
  they would only log a given error once per session and node type.

## [2.10.1] - 2022-01-19
### Changed
- Fixed a bug in attribute resolution propagation logic

## [2.10.0] - 2022-01-18
### Changed
- Extended attributes will now be returned to an unresolved state upon disconnection if the topology of the graph
  does not prevent it.

## [2.9.0] - 2022-01-17
### Added
- INode 4.0 -> 4.1
  - Added INode::getComputeCount
  - Added INode::incrementComputeCount

## [2.8.0] - 2022-01-13
### Added
- IGraphRegistry 1.1 -> 1.2
  - Added _IGraphRegistry::getRegisteredType_

## [2.7.0] - 2022-01-06
### Modified
- _GraphContextObj.context_ has been replaced with _GraphContextObj.contextHandle_. The old member was a
  pointer to an internal OG class. The new member is a POD handle which can be used with OG ABI functions.

## [2.6.1] - 2021-12-30
### Modified
- _INode::resolvePartiallyCoupledAttributes_ checks more type resolution error conditions.

## [2.6.0] - 2021-12-21
### Added
- IAttributeData 1.3 -> 1.4
  - Added _IAttributeData::getDataRGpuAt_
  - Added _IAttributeData::getDataWGpuAt_
  - Added _IAttributeData::getDataReferenceRGpuAt_
  - Added _IAttributeData::getDataReferenceWGpuAt_

## [2.5.1] - 2021-12-16
### Changed
- Action Graph evaluator now uses `og.ExecutionAttributeState.LATENT_FINISH`
  to indicate when a latent node is finished.

## [2.5.0] - 2021-12-10
### Added
- Created the INodeCategories interface
- ComputeGraph 2.4 -> 2.5
  - Added _ComputeGraph::getNodeCategories_

## [2.5.1] - 2021-12-08
### Fixed
- Fix RuntimeAttribute getXX templates to avoid an MSVC compiler bug

## [2.4.0] - 2021-12-07
### Added
- IGraph 3.3 -> 3.4
  - Added _IGraph::isGlobalGraphPrim_
- Modified RuntimeAttribute to include PtrToPtrKind template, with default for backward compatibility

## [2.3.0] - 2021-12-06
### Added
- Added _INodeEvent::eAttributeTypeResolve_

## [2.2.1] - 2021-12-02
### Fixed
- Fix bug where renaming a graph doesn't rename the wrapper node, resulting in new graphs overwriting old graphs
## [2.2.0] - 2021-11-26
### Added
- Python Bindings 2.1.0 -> 2.2.0
  - Added Python api `Graph.get_parent_graph`
- Ignore connections to ComputeGraph prims for the new OmniGraph UI.

## [2.1.0] - 2021-11-26
### Added
- IAttributeType 1.2 -> 1.3
  - Added _IAttributeType::isLegalOgnType_

## [2.0.3] - 2021-11-25
### Added
- INodeType 1.5 -> 1.6
  - Added _INodeType::getName_

## [2.0.2] - 2021-11-24
### Fixed
- Fix for handling of referenced OmniGraph Graphs

## [2.0.1] - 2021-11-18
Exposing attribute optional flag.
### Added
- IAttribute 1.8 -> 1.9
  - Added _IAttribute::getIsOptionalForCompute_
  - Added _IAttribute::setIsOptionalForCompute_

## [2.0.0] - 2021-11-12
Major change to deprecate functionality that has been on the chopping block for a while now.
### Removed
- Removed _PlugFlags_
- Removed _kPlugFlagNone_
- Removed _kPlugFlagFollowUpstream_
- INode 3.1 -> 4.0
  - Retired _getPlug_
  - Retired _stashPlug_
  - Retired _getStashedPlugCount_
  - Retired _getStashedPlug_
- IGraphContext 2.1 -> 3.0
  - Retired _getAttribute_
  - Retired _getAttributeWithAttr_
  - Retired _getAttributeGPU_
  - Retired _getElementCount_

## [1.4.1] - 2021-11-10
- Fixed bugs where renaming the global graph breaks connections and where bundles don't work in global graphs

## [1.4.0] - 2021-11-10
### Added
- New Interface ISchedulingHints
  - Added _ISchedulingHints::getComputeRule_
  - Added _ISchedulingHints::setComputeRule_

## [1.3.1] - 2021-11-08
### Changed
- ISchedulingHints 1.0 -> ONI
  - Kept same functionality, implemented as ONI interface instead of Carbonite interface

## [1.3.0] - 2021-11-04
### Added
- INode 3.1 -> 3.2
  - Added _INode::requestCompute_

## [1.3.0] - 2021-10-27
### Added
- IGraph 3.2 -> 3.3
  - Added _IGraph::evaluate_

## [1.2.0] - 2021-10-18
### Changed
- Prim nodes now not created unless attribute-connected to OG node
### Added
- IGraph 3.1 -> 3.2
  - Added _IGraph::getFabricUserId_
- IAttribute 1.8 -> 1.9
  - Added _IAttribute::ensurePortTypeInName_
  - Added _IAttribute::getPortTypeFromName_
  - Added _IAttribute::removePortTypeFromName_

## [1.1.0] - 2021-10-13
### Added
- IAttribute 1.7 -> 1.8
  - Added _IAttribute::isValid_
- INode 3.0 -> 3.1
  - Added _INode::isValid_
- IGraph 3.0 -> 3.1
  - Added _IGraph::isValid_
- IGraphContext 2.0 -> 2.1
  - Added _IGraphContext::isValid_

## [1.0.6] - 2021-10-08
### Added
- FileFormatVersion 1.1 -> 1.2
  - Added support for scoped graphs in the editor

## [1.0.5] - 2021-10-07
### Added
- IBundle 1.3 -> 1.4
  - Added _IBundle::addAttributes_
  - Added _IBundle::removeAttributes_

## [1.0.4] - 2021-09-30
### Added
- Created ISchedulingHints 1.0
  - Added _ISchedulingHints::getThreadsafety_
  - Added _ISchedulingHints::setThreadsafety_
  - Added _ISchedulingHints::getDataAccess_
  - Added _ISchedulingHints::setDataAccess_
- INodeType 1.4 -> 1.5
  - Added _INodeType::getSchedulingHints_
  - Added _INodeType::setSchedulingHints_

## [1.0.3] - 2021-09-29
### Added
- ComputeGraph 2.3 -> 2.4
  - Added _ComputeGraph::getGraphCountInPipelineStage_
  - Added _ComputeGraph::getGraphsInPipelineStage_
  - Added _GraphBackingType::kGraphBackingType_None_

## [1.0.3] - 2021-09-23
### Added
- IGraph 2.1 -> 3.0
  - Changed the signature of _IGraph::createGraphAsNode_
  - Added _IGraph::getGraphBackingType_
  - Added _IGraph::getPipelineStage_

## [1.0.3] - 2021-09-21
### Added
- IGatherPrototype 1.0 -> 1.1
  - Added _getGatherArray_
  - Added _getGatherArrayGPU_
  - Added _getGatherPathArray_
  - Added _getGatherArrayAttributeSizes_
  - Added _getGatherArrayAttributeSizesGPU_
  - Added _getElementCount_

## [1.0.3] - 2021-09-16
### Added
- IAttribute 1.6 --> 1.7
  - Added _IAttribute::isDynamic()_
  - Added _IAttribute::getUnionTypes()_

## [1.0.3] - 2021-09-15
### Added
- IAttributeData 1.2 --> 1.3
  - Added _IAttributeData::cpuValid()_
  - Added _IAttributeData::gpuValid()_

## [1.0.3] - 2021-08-30
### Added
- IGraph 2.0 --> 2.1
  - Added _IGraph::reloadFromStage()_

## [1.0.2] - 2021-08-18
### Added
- INode 2.0 -> 2.1
  - Added _INode::getEventStream_

## [1.0.2] - 2021-08-09
### IGatherPrototype 1.0
- Added _IGatherPrototype::gatherPaths_
- Added _IGatherPrototype::getGatheredPaths_
- Added _IGatherPrototype::getGatheredBuckets_
- Added _IGatherPrototype::getGatheredType_

## [1.0.2] - 2021-07-26
### Changed
- INode 1.6 --> 2.0
  - Changed the signature of _INode::createAttribute_

## [1.0.2] - 2021-07-16
### Added
- INodeType 1.3 -> 1.4
  - Added _INodeType::removeSubNodeType()_

## [1.0.2] - 2021-07-14
### Changed
- IGraph 1.3 -> 2.0
  - Changed the signature of _IGraph::createSubgraph_

## [1.0.2] - 2021-07-12
### Added
- IGraph 1.2 -> 1.3
  - Added _IGraph::createGraphAsNode_

## [1.0.2] - 2021-07-04
### Added
- INode 1.5 -> 1.6
  - Added _INode::getWrappedGraph()_
### Changed
- ComputeGraph 2.2 -> 2.3
  - Changed the semantics of getGraphCount, getGraphs, getGraphContextCount, getGraphContexts

## [1.0.2] - 2021-07-01
### Added
- INode 1.4 -> 1.5
  - Added _INode::registerPathChangedCallback()_
  - Added _INode::deregisterPathChangedCallback()_

## [1.0.2] - 2021-06-21
### Added
- IAttribute 1.5 -> 1.6
  - Added _IAttribute::getPortType()_

## [1.0.2] - 2021-06-11
### Added
- IBundle 1.2 -> 1.3
  - Added _IBundle::removeAttribute_
- IGraphContext 1.3 -> 1.4
  - Added _IGraphContext::getTimeSinceStart()_

## [1.0.2] - 2021-06-10
### Added
- INodeType 1.2 -> 1.3
  - Added _INodeType::getSubNodeTypeCount_
  - Added _INodeType::getAllSubNodeTypes_
- IDataStealinPrototype 1.0
  - Added _IDataStealingPrototype::actualReference_
  - Added _IDataStealingPrototype::moveReference_
  - Added _IDataStealingPrototype::enabled_
  - Added _IDataStealingPrototype::setEnabled_

## [1.0.2] - 2021-06-01
### Changed
- INode 1.3 -> 1.4
  - Modified _INode::registerConnectedCallback_
  - Modified _INode::registerDisconnectedCallback_
  - Modified _INode::deregisterConnectedCallback_
  - Modified _INode::deregisterDisconnectedCallback_

## [1.0.2] - 2021-05-31
### Added
- IGraph 1.1 -> 1.2
  - Added _IGraph::registerPreLoadFileFormatUpgradeCallback_
  - Added _IGraph::registerPostLoadFileFormatUpgradeCallback_
  - Added _IGraph::deregisterPreLoadFileFormatUpgradeCallback_
  - Added _IGraph::deregisterPostLoadFileFormatUpgradeCallback_

## [1.0.2] - 2021-05-05
### Added
- IGraph 1.0 -> 1.1
  - Added _IGraph::inspect()_
- IAttributeData 1.1 -> 1.2
  - Added _IAttributeData::getDataReferenceR()_
  - Added _IAttributeData::getDataReferenceRGpu()_
  - Added _IAttributeData::getDataReferenceW()_
  - Added _IAttributeData::getDataReferenceWGpu()_
- IAttributeType 1.0 -> 1.1
  - Added _IAttributeType::inspect()_
  - Added _IAttributeType::baseDataSize()_
  - Added _IGraphRegistry::inspect()_
  - Added _IGraphRegistry::registerNodeTypeAlias()_
  - Added _INodeType::inspect()_
- INode 1.2 -> 1.3
  - Added _INode::resolveCoupledAttributes()_
  - Added _INode::resolvePartiallyCoupledAttributes()_
- INode 1.1 -> 1.2
  - Added _INode::getNodeTypeObj()_
- IGraphContext 1.1 -> 1.2
  - Added _IGraphContext::inspect()_

## [1.0.1] - 2021-04-07
### Added
- Created the interface IAttributeType for working with the Type struct

## [1.0.0] - 2021-03-01
### Initial Version
- Started changelog with initial released version of the OmniGraph core
