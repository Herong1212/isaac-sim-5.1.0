(changelog_omni_graph_nodes)=

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.170.10] - 2025-06-03
### Changed
- Fix the rtx resource initialization.

## [1.170.9] - 2025-04-25
### Changed
- Use omni.kit.property.usd.AllowedTokenItem instead of or as base of custom AllowedTokenItem classes.

## [1.170.8] - 2025-02-06
### Changed
- linux toolchain compatibility upgrade

## [1.170.7] - 2025-01-15
### Fixed
- A few improperly specified list annotations.

## [1.170.6] - 2025-01-07
### Changed
- Prevent the possibility of returning a dangling pointer (ref to a temporary)

## [1.170.5] - 2025-01-07
### Changed
- Updates for latest Kit SDK

## [1.170.4] - 2025-01-03
### Fixed
- Replaced overlapping memcpy() calls with memmove().

## [1.170.3] - 2024-12-17
### Changed
- Fixes in WritePrims when using private fabric

## [1.170.2] - 2024-12-16
### Changed
- Remove test dependencies which are already included.

## [1.170.1] - 2024-12-16
### Changed
- Changed a few fabric accesses to diferentiate between graph and stage fabrics

## [1.170.0] - 2024-11-18
### Changed
- Build with Kit 107.0 with USD 24.05 and python 3.11
- Jumping versions for 107 to leave room for changes to 106.*-based builds.

## [1.162.1] - 2024-12-03
### Fixed
- Bad first frame for WritePrimAttribute when auto conversion is used

## [1.162.0] - 2024-11-28
### Changed
- Added layer identifier functionality to write nodes

## [1.161.1] - 2024-10-21
### Changed
- Forced consistent RandomNumeric/Gaussian type resolution + fixed range order.

## [1.161.0] - 2024-10-03
### Changed
- Add BundleConstructor, c++ implementation

## [1.160.0] - 2024-09-19
### Changed
- bumping version to make room for 106.2-based extensions

## [1.150.1] - 2024-08-27
### Changed
- Fix deprecated module imports

## [1.150.0] - 2024-08-09
### Changed
- bumping version to make room for 106-based extensions

## [1.146.0] - 2024-07-31
### Fixed
- Use of deprecated Fabric API.
### Changed
- Access to carb.audio API.

## [1.145.4] - 2024-07-25
### Changed
- Fix usage of GetOrderedXformOps in XformUtils

## [1.145.3] - 2024-07-03
### Changed
- Fixed RotateToOrientation node on pivot transform in Fabric

## [1.145.2] - 2024-07-02
### Fixed
- Nodes which operate on prim attrs had stopped working on when attr had no value.

## [1.145.1] - 2024-06-27
### Fixed
- The ReadPrimRelationship node was not properly updating relationships which initially have no targets.

## [1.145.0] - 2024-06-17
### Changed
- Removed some deprecated nodes: BooleanExpr, FMod, Trig, MakeArray, GetLocationAtDistanceOnCurve
- Move BundleConstructor to .test

## [1.144.3] - 2024-06-06
### Fixed
- Property Window build functions which were not returning their value models.

## [1.144.2] - 2024-05-30
### Changed
- Updated the formatting

## [1.144.1] - 2024-05-24
### Changed
- Perf improvement for some nodes using vectorized target attribute

## [1.144.0] - 2024-05-17
### Added
- Update the 'support_level' entry in the configuration files to match the release requirements

## [1.143.3] - 2024-05-10
### Changed
- Build changes to account for new stock OpenUSD library in kit.

## [1.143.2] - 2024-04-30
### Changed
- Add support for type inference of string values in the ReadSetting node

## [1.143.1] - 2024-04-17
### Added
- Add a 'support_level' entry to the configuration file of the extensions

## [1.143.0] - 2024-04-10
### Changed
- Bumped dependency on omni.graph to version 1.139.0
- Bumped dependency on omni.graph.core to version 2.177.1
- Bumped dependency on omni.graph.tools to version 1.77.0

## [1.142.1] - 2024-04-08
### Changed
- Removed dependency on stage_templates and pipapi.

## [1.142.0] - 2024-03-27
### Changed
- Manual version bump to ensure that the version of this extension that's built against kit 107 is higher than the one
  built against kit 106 (see OM-122109).

## [1.140.0] - 2024-03-18
### Changed
- Bumped dependency on omni.graph.core to version 2.176.3
- Bumped dependency on omni.graph to version 1.138.1

## [1.139.2] - 2024-02-23
### Changed
- Cleanup and code coverage for matrix and vector math nodes
### Fixed
- Fixed TranslateToTarget to allow for target prim to be specified (was bundle).

## [1.139.1] - 2024-02-22
### Changed
- Cleanup and code coverage for arithmetic nodes
- Arithmetic nodes now unresolve output when new input is added.

## [1.139.0] - 2024-02-15
### Changed
- Bumped dependency on omni.graph.core to version 2.174.2
- Bumped dependency on omni.graph.tools to version 1.76.1

## [1.138.0] - 2024-02-15
### Fixed
- Fixed vectorized node speed issues.

## [1.137.5] - 2024-02-07
### Changed
- - Fix a bug in kit-omniverse variant test

## [1.137.4] - 2024-02-07
### Fixed
- Fix skinned points being in skeleton space rather than target prim space with ReadPrimsV2's applySkelBinding

## [1.137.3] - 2024-02-07
### Changed
- Remove unnecessary warning when property is removed

## [1.137.2] - 2024-02-07
### Changed
- - OMPRW-686 Sounds try to play before loaded

## [1.137.1] - 2024-02-05
### Changed
- - OMPRW-596 Errors with "set variant selection" node on purse asset

## [1.137.0] - 2024-02-05
### Changed
- Bumped dependency on omni.graph to version 1.138.0
- Bumped dependency on omni.graph.core to version 2.174.0
- Bumped dependency on omni.graph.tools to version 1.76.0

## [1.136.0] - 2024-02-03
### Added
- ReadTime and ReadPrimAttribute nodes now implements the IDirtyable interface to specify custom dirtying logic when placed in a lazy graph.
### Changed
- Bumped minimum omni.graph.core extension version dependency to be compatible with changes to the INodeType interface and lazy graph executor.

## [1.135.2] - 2024-02-02
### Changed
- Update settings to use latest file format version from omni.graph

## [1.135.1] - 2024-01-31
### Changed
- Bundle asymmetry correction update file version

## [1.135.0] - 2024-01-31
### Changed
- Update settings to use latest file format version
- Bumped dependency on omni.graph to version 1.137.0
- Bumped dependency on omni.graph.core to version 2.171.1
- Bumped dependency on omni.graph.tools to version 1.76.0

## [1.134.0] - 2024-01-30
### Changed
- Moved uiName to a first order keyword for a few example nodes
- Bumped dependency on omni.graph to version 1.136.1
- Bumped dependency on omni.graph.core to version 2.170.1
- Bumped dependency on omni.graph.tools to version 1.74.0

## [1.133.3] - 2024-01-26
### Changed
- Clean up and update the docs of OgnRpResourceExample* nodes

## [1.133.2] - 2024-01-25
### Fixed
- WriteVariable output no longer aliases the variable.

## [1.133.1] - 2024-01-24
### Changed
- Minor doc improvements

## [1.133.0] - 2024-01-24
### Changed
- Expanded on and made consistent the node type documentation for a bunch of node types

## [1.132.3] - 2024-01-24
### Changed
- Updated some of the documentation in various .ogn's in this extension.

## [1.132.2] - 2024-01-23
### Changed
- OM-117679: Pre-emptively fix tests prior to merging upstream MR

## [1.132.1] - 2024-01-23
### Changed
- Improve Documentation for Conversion nodes

## [1.132.0] - 2024-01-23
### Changed
- Bumped dependency on omni.graph to version 1.136.0

## [1.131.2] - 2024-01-22
### Changed
- Fix build warnings

## [1.131.1] - 2024-01-22
### Fixed
- Made execution attribute descriptions consistent and informative

## [1.131.0] - 2024-01-19
### Changed
- WriteSetting now resolve it's input attribute automatically
- int array values are no longer converted to tuples, int64, double is used instead of int,float by default

## [1.130.0] - 2024-01-18
### Added
- Moved nodes from omni.graph.io
### Changed
- Bumped dependency on omni.graph.core to version 2.169.1
- Bumped dependency on omni.graph to version 1.135.1
- Bumped dependency on omni.graph.tools to version 1.73.0

## [1.129.2] - 2024-01-17
### Fixed
- crash with threaded prim translation nodes

## [1.129.1] - 2024-01-13
### Fixed
- Repository URL in config file.

## [1.129.0] - 2024-01-12
### Changed
- Bumped dependency on omni.graph to version 1.134.7
- Bumped dependency on omni.graph.core to version 2.169.0
- Bumped dependency on omni.graph.tools to version 1.70.0

## [1.128.1] - 2024-01-12
### Changed
- Fix build warnings

## [1.128.0] - 2023-12-28
### Changed
- Improve run time of tests.
- Bumped dependency on omni.graph.tools to version 1.69.0

## [1.127.0] - 2023-12-28
### Changed
- Bumped dependency on omni.graph.core to version 2.167.0
- Bumped dependency on omni.graph to version 1.134.2
- Bumped dependency on omni.graph.tools to version 1.68.0

## [1.126.1] - 2023-12-20
### Changed
- OgnRpResourceExampleAllocator: Check the validity of the ResourceManager before use.

## [1.126.0] - 2023-12-18
### Fixed
- Put in missing version numbers for .ogn files
### Changed
- Bumped dependency on omni.graph.core to version 2.166.0
- Bumped dependency on omni.graph to version 1.134.0
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.125.3] - 2023-12-14
### Changed
- Prevent excessive stage creation in the test exercising setting nodes

## [1.125.2] - 2023-12-14
### Fixed
- OgnRpResourceExampleAllocator: check the resource pointer before freeing the resource.

## [1.125.1] - 2023-12-13
### Fixed
- Fixed tests when FabricSceneDelegate is enabled
- Non-USD compatible types no longer create ports on WritePrimAttributes

## [1.125.0] - 2023-12-12
### Added
- Filter for flaky test_read_and_write_settings
### Changed
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph to version 1.133.2
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.124.0] - 2023-12-11
### Changed
- Update tests to latest kit behavior
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph to version 1.133.2
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.123.0] - 2023-12-08
### Changed
- Implemented Minimum, Maximum, Logarithm, Inverse and Constant e nodes.

## [1.122.1] - 2023-12-07
### Changed
- Use ScopedRead lock on settings for thread safety

## [1.122.0] - 2023-12-05
### Changed
- Increase timeout

## [1.121.1] - 2023-12-05
### Changed
- Fix cross product test with correct attribute types

## [1.121.0] - 2023-12-04
### Changed
- Test coverage for utility nodes.
- Utility nodes converted to computeVectorized.
- BreakVector* nodes now support arrays.
- Changed nodes to use correct set of input types instead of any.
- GetPrimRelationship now hidden (deprecated).
### Added
- Added tests for utility nodes.
### Fixed
- Removing all attributes from ConstructArray node will no longer loose the input type.
- Compare now works with half tuples

## [1.120.6] - 2023-12-04
### Changed
- Fix ogn tests that use inconsistent types

## [1.120.5] - 2023-11-30
### Changed
- Added test coverage to math trig nodes.
- Math trig nodes now support tuples.
### Added
- Replaced python ATan2 node with c++ version.

## [1.120.4] - 2023-11-30
### Changed
- Set the minimal omni.graph.core version required in order to properly load that extension

## [1.120.3] - 2023-11-28
### Changed
- Changed deprecated internal state functions to their new version

## [1.120.2] - 2023-11-21
### Changed
- Fix for CapitalizeString test failure

## [1.120.1] - 2023-11-21
### Changed
- Added simulation time attribute to node RpResourceExampleDeformer to make the test using it deterministic.

## [1.120.0] - 2023-11-21
### Added
- Implemented string nodes to manipulate strings
### Changed
- Updated string nodes to use computeVectorized
- Added test coverage for BuildString & AppendString
### Fixed
- Fixed BuildString to prevent crashing when encountering invalid attribute resolutions.

## [1.119.0] - 2023-11-15
### Changed
- Set valid connection types for OgnConstructArray (MakeArray)

## [1.118.0] - 2023-11-15
### Added
- Added AppendArray node to merge multiple arrays.
- Added ArrayAppendValue node to append values to the end of an array.
- Added ArrayReplaceValue node to replace a specified value in an array
- Added ArrayReverse node to reverse an array or string
- Added ArraySlice node to return a partial array from an input array or string.
### Changed
- Updated array nodes to use computeVectorized & correct output types.
- Updated array node tests to test all available extended types.
- Added string type to array nodes.
- Added tests for code coverage.
### Fixed
- Fixed crash with ArrayResize when index is negative.
- Fixed broken removeAll behavior in ArrayRemoveValue node.

## [1.117.12] - 2023-11-14
### Changed
- Further code coverage for conversion nodes

## [1.117.11] - 2023-11-13
### Changed
- Improved code coverage for conversion nodes.

## [1.117.10] - 2023-11-10
### Changed
- Improve code coverage on variant nodes

## [1.117.9] - 2023-11-10
### Changed
- Improve code coverage on variant nodes

## [1.117.9] - 2023-11-10
### Changed
- Removed dead code paths

## [1.117.7] - 2023-11-09
11-9
### Changed
- Code coverage annotations for constants and io nodes

## [1.117.6] - 2023-11-09
11-9
### Changed
- Ran the formatter

## [1.117.5] - 2023-11-09
### Changed
- Improved coverage for core nodes

## [1.117.4] - 2023-11-07
### Changed
- Improved test coverage on geometry nodes

## [1.117.3] - 2023-11-07
### Changed
- Improved test coverage for attribute, constant and settings nodes
### Fixed
- Issue where write settings nodes did not write all array elements

## [1.117.2] - 2023-11-03
### Changed
- Remove test sampling from config

## [1.117.1] - 2023-11-01
### Fixed
- WriteVariable now works with an auto converted input

## [1.117.0] - 2023-10-31
### Changed
- GetMatrix4Rotation now has correct output and allows inputs of angles, quaternions and rotation matrices.
- SetQuaternion is deprecated/hidden.",
- GetMatrix4Quaternion now allows inputs of angles and rotation matrices.
- SetMatrix4Rotation now allows inputs of angles, quaternions and rotation matrices.
- RotateVector now allows inputs of angles, quaternions and rotation matrices.
- Rotation transform nodes now allow users to change the rotation order.
### Added
- Added BreakMatrix2|3|4 to extract vectors from a matrix
- Added MakeMatrix2|3|4 to construct a matrix from vectors.
- Added Orthonormalize node to orthonormalize a matrix
- Added Transpose node to transpose (flip) a matrix
- Added GetMatrix4Scale node extract the scale from a matrix
- Added GetMatrix4RotationMatrix node extract the rotation matrix from a matrix
- Added Ui templates for node with rotation order

## [1.116.2] - 2023-10-31
### Changed
- Built against kit-sdk version 132791

## [1.116.1] - 2023-10-23
### Changed
- Vectorized some matrix nodes
### Added
- Set Matrix4 scale

## [1.116.0] - 2023-10-17
### Changed
- Made modulo node vectorized

## [1.115.0] - 2023-10-09
### Changed
- Adding Conversion nodes for all supported types
- ToDouble, ToFloat and ToHalf nodes now have the ability to select the attribute role of the output

## [1.114.0] - 2023-10-06
### Changed
- Changed ToToken and ToString to use computeVectorized
- Fixed ToToken to properly work with empty tokens and uchar[]

## [1.113.0] - 2023-10-05
### Fixed
- SetPrimActive UI template

## [1.112.1] - 2023-10-04
### Changed
- - Add fabric material bindings for Set, Clear, and Blend

## [1.112.0] - 2023-10-03
### Changed
- Fixed nodes that did not resolve output attributes correctly when using 'Convert To' command
- SetMatrix* nodes now allow mixing of arrays and scalar inputs
- Added checks to avoid invalid input situations in Ease, InterpolateTo, Compare and SelectIf nodes

## [1.111.0] - 2023-09-29
### Removed
- Moved test_write_prims_node.py over to omni.graph.test to avoid use of deprecated AutoNode

## [1.110.3] - 2023-09-29
### Changed
- Implemented computeVectorized for a bunch of stock nodes

## [1.110.2] - 2023-09-27
### Changed
- Fixed compile error against latest fabric

## [1.110.1] - 2023-09-26
### Changed
- Disable failing test assert in `test_read_write_prims_remove_missing*` tests

## [1.110.0] - 2023-09-25
### Changed
- Adding all attribute types to ConstructArray

## [1.109.0] - 2023-09-22
### Changed
- OM-110129: Use Bundle Write Block for Read Prims

## [1.108.2] - 2023-09-21
### Changed
- OM-109701 Bundle Inspector needs execution pins in order to work in AG

## [1.108.1] - 2023-09-19
### Fixed
- ReadVariable node: Do not reset extended attribute, as the framework already does it

## [1.108.0] - 2023-09-08
### Changed
- Added target nodes that more closely follow naming conventions
- Deprecated GetPrimsAtPath and ConstantPrims

## [1.107.1] - 2023-09-01
### Fixed
- Fixed issue where unauthored attributes from schema were not readable/writeable

## [1.107.0] - 2023-08-31
### Changed
- ReadPrimsV2 now adds a sourcePrimHandle PathC attribute in the bundle, to avoid costly token->string->SdfPath conversion

## [1.106.5] - 2023-08-30
### Fixed
- Fixed ReadPrims and ReadPrimsV2 dangling paths that caused an access violation

## [1.106.4] - 2023-08-29
### Changed
- Moved reference to deprecated AutoNode implementation

## [1.106.3] - 2023-08-28
### Changed
- Change ReadPrims to more closely match the ImportUSDPrim imported attributes.

## [1.106.2] - 2023-08-26
### Changed
- Add kit target to extension.

## [1.106.1] - 2023-08-22
### Fixed
- `WritePrimsV2` crashes on debug build when closing a stage due to accessing an invalid entry

## [1.106.0] - 2023-08-21
### Changed
- Added Constant nodes for all supported types

## [1.105.6] - 2023-08-15
### Changed
- Fix crash in GetPrimLocalToWorldTransform

## [1.105.5] - 2023-08-11
### Changed
- WritePrimsV2 node now cleans up created objects upon deletion.

## [1.105.4] - 2023-08-10
### Changed
- Cherry picked changes from Kit

## [1.105.3] - 2023-08-09
### Changed
- Moved extension from Kit to this repo

## [1.105.2] - 2023-08-08
### Changed
- Consolidated CreatedObjectsTracker(Group) code so it's easier to follow.
### Fixed
- Fixed a performace regression introduced by bundle change tracking on WritePrimsV2 node.

## [1.105.1] - 2023-08-05
### Changed
- `WritePrimsV2` node now supports bundle change tracking. Only changed prims/attributes in dirtied bundles will be written out during compute.

## [1.105.0] - 2023-08-03
### Added
- OgnReadPrimsV2 now always requests a node update whenever any of its tracked prims change, making it usable in dirty-push graphs.

## [1.104.0] - 2023-07-30
### Changed
- Moved GPU interop nodes to omni.graph.image.nodes
### Removed
- Long deprecated function that has no body
### Added
- Dependency on omni.graph.image.nodes for backward compatibility

## [1.103.1] - 2023-07-26
### Changed
- Modified unit test to conform to the new structuring of .ogn "tests" data.

## [1.103.0] - 2023-07-25
### Changed
- Revert output and state bundle name space separator to underscore

## [1.102.1] - 2023-07-20
### Fixed
- `ReadPrimsV2` skinned points are not synchronized from CPU to GPU

## [1.102.0] - 2023-07-14
### Removed
- Test for the read prim node, which requires omni.graph.test

## [1.101.0] - 2023-07-13
### Changed
- OM-97363: Resolve input-output bundle asymmetry

## [1.100.0] - 2023-07-12
### Changed
- Removed omni.kit.async_engine dependency

## [1.99.0] - 2023-07-06
### Added
- Enhanced USD change tracker and ReadPrimsV2 to track ancestors and descendants for incrementally updating the world matrix and local bound

## [1.98.3] - 2023-07-05
### Changed
- `ReadPrimsV2` avoids unnecessary update for the interpolation metadata

## [1.98.2] - 2023-07-01
### Fixed
- Null check in WritePrimAttribute

## [1.98.1] - 2023-06-30
### Added
- `ReadPrimsV2` node now supports importing relationship.
### Changed
- `WritePrimsV2` node now treats unauthored schema properties on target prims as newly created properties.

## [1.98.0] - 2023-06-30
### Added
- ReadPrimsV2 updates prim attributes incrementally by leveraging USD change tracker.

## [1.97.4] - 2023-06-28
### Fixed
- Prevent emitting an error during type resolution in OgnConstructArray if input is not connected

## [1.97.3] - 2023-06-27
### Fixed
- Refactored OmniGraph documentation to point to locally generated files

## [1.97.2] - 2023-06-27
### Changed
- Set up the extension to load python nodes and tests in parallel

## [1.97.1] - 2023-06-27
### Fixed
- OgnConstructArray: fixed potential crash when setting the arraySize attribute to negative values.

## [1.97.0] - 2023-06-23
### Changed
- Tagged all constant nodes with the "pure" scheduling hint.

## [1.96.2] - 2023-06-23
### Changed
- Modified scheduling hint on OgnWritePrimRelationship to be "usd-write" only
(instead of both "usd-read" and "threadsafe").

## [1.96.1] - 2023-06-23
### Changed
- OM-93232, OM-95573 fix test_basic_write_prim_relationships flaky unit test

## [1.96.0] - 2023-06-23
### Added
- Enhanced USD change tracker to report which attributes were updated.

## [1.95.5] - 2023-06-21
### Changed
- Reverted parallel change from 1.95.3

## [1.95.4] - 2023-06-21
### Changed
- Changed a few nodes to properly emit their compute messages with the proper instance index

## [1.95.3] - 2023-06-21
### Changed
- Set up the extension to load python nodes and tests in parallel

## [1.95.2] - 2023-06-19
### Fixed
- OM-98684: bugfix for write prims layer identifier assignment

## [1.95.1] - 2023-06-13
### Fixed
- Enabled timeline nodes Python code generator
- Added missing frame-based start/end range get/set

## [1.95.0] - 2023-06-13
### Changed
- Nodes to control and query the main timeline

## [1.94.0] - 2023-06-11
### Added
- ReadPrimsV2 reads prim attributes into output bundle directly (without Fabric prefetch)

## [1.93.1] - 2023-06-05
### Fixed
- AppendString/BuildString were not properly enforcing all of their attribute type resolution

## [1.93.0] - 2023-06-03
### Added
- ReadPrimsV2 only updates child bundles whose associated USD prim changes
- Added input attribute to disable this behavior

## [1.92.0] - 2023-06-03
### Added
- Input targets to GetPrims.

## [1.91.2] - 2023-05-31
### Fixed
- Adjusted the CRLF settings for the generated .md node table of content files

## [1.91.1] - 2023-05-31
### Changed
- WritePrims node doesn't crash anymore when passing non-token values for sourcePrimPath and sourcePrimType attributes

## [1.91.0] - 2023-05-29
### Added
- Regenerated node table of contents
### Changed
- Changed deprecated get_current_graph call to get_all_graphs

## [1.90.3] - 2023-05-26
### Added
- Added `inputs:layerIdentifier` to `WritePrimsV2` node to support writing to a specific local layer.
- Added UI template and builder for a user friendly layer identifier property widget.

## [1.90.2] - 2023-05-24
### Changed
- Modified unit tests/test scripts that were using the now-removed "pull" evaluation mode to instead use "push"
(these tests did not rely on "pull" mode being explicitly used to fulfill their testing purposes).

## [1.90.1] - 2023-05-23
### Changed
- Updated test_read_and_write_settings test to use an existing setting (the one it was using has since been removed).

## [1.90.0] - 2023-05-17
### Changed
- Restored the original node functionality to ReadPrims node and marked it deprecated, hidden from UI.
- All existing ReadPrims tests have been ported to run on both ReadPrims (legacy) and ReadPrimsV2 node.
### Added
- Added ReadPrimsV2 node to host the new functionality in place of soft deprecated ReadPrims.
- Added back legacy tests for WritePrims node

## [1.89.0] - 2023-05-16
### Added
- Various improvements to random number nodes.
- The nodes are now thread-safe
- min/max and mean/stdev inputs are not optional, default to double.
- min/max and mean/stdev inputs can now be set without connecting a const node.
- Support for vectorization and graph instancing, combining the hash with the path of the graph target.
- OgnRandomNumeric, OgnRandomGaussian, OgnRandomBoolean, OgnRandomUnitVector, OgnRandomUnitQuaterion.

## [1.88.1] - 2023-05-15
### Removed
- Removed old subgraph unit tests.

## [1.88.0] - 2023-05-15
### Changed
- Restored the original node functionality to WritePrims node and marked it deprecated, hidden from UI.
### Added
- Added WritePrimsV2 node to host the new functionality in place of soft deprecated WritePrims.

## [1.87.0] - 2023-05-12
### Added
- Added OgnReadPrimRelationship and OgnWritePrimRelationship nodes

## [1.86.0] - 2023-05-11
### Changed
- Renamed `inputs:parentPrims` to `inputs:prims` on `WritePrims` node.
- When `inputs:writeToUsd` on `WritePrims` is not enabled, making sure the target fabric prim has desired type,
- `WritePrims` only removes attrs/prims previously created (instead of written to) by the node.
### Added
- Added a new mode to `WritePrims` node as default to directly use the prim target as output prim (instead of appending source prim path and export under them). Controlled by `inputs:scatterUnderTargets`.

## [1.85.0] - 2023-05-09
### Changed
- Add startValue and endValue to Timer node

## [1.84.0] - 2023-05-07
### Added
- Stop All Sounds node

## [1.83.4] - 2023-05-04
### Changed
- `WritePrims` node is now able to pick different targets to write out prims to.
- `useFindPrims` is no longer on `ReadPrims` node. As long as `pathPattern` is not empty, it turns on `useFindPrims` automatically.

## [1.83.3] - 2023-05-03
### Changed
- BlendVariant node mangles attribute names in some cases
- lerp discrete properties half-way through the blend
- Have blend continue when an attribute is not found for a variant property
- Fix bug in UI for variantNameA

## [1.83.2] - 2023-05-03
### Fixed
-  OM-92618 Failing test_prim_relationship_load test

## [1.83.1] - 2023-05-02
### Changed
- Updated OgnNor, OgnNand, OgnBuildString to use constructInputFromOutput during computation.

## [1.83.0] - 2023-05-01
### Changed
- Migrate variants from usePath to target type

## [1.82.7] - 2023-05-01
### Fixed
- Small perf improvement for ReadPrimAttribute
- ReadPrimAttribute with invalid setup properly report the problem
- WritePrimAttribute with invalid setup properly report the problem

## [1.82.6] - 2023-04-27
### Added
- Added `rootPrims` target to `ReadPrims` node so that `useFindPrims` can search under different prims other than absolute root.
- Added tracker for all `ReadPrims`'s `rootPrims` paths.

## [1.82.5] - 2023-04-26
### Changed
- Blend Variants implementation to optionally blend local values

## [1.82.4] - 2023-04-24
### Fixed
- Replaced deprecated call to get_elem_count

## [1.82.3] - 2023-04-20
### Fixed
- `Read Prims` outputs invalid skinned mesh when SkelBinding is applied.

## [1.82.2] - 2023-04-17
### Fixed
- build of inputs:prim widget

## [1.82.1] - 2023-04-17
### Fixed
- Perf regression in ReadPrimAttribute

## [1.82.0] - 2023-04-12
### Added
- Random number nodes for action graphs
- OgnRandomNumeric, OgnRandomGaussian, OgnRandomBoolean, OgnRandomUnitVector, OgnRandomUnitQuaterion

## [1.81.6] - 2023-04-12
### Changed
- Updated UI for nodes that input a target attibute and a prim path
- Added material target input for WritePrimMaterial
- Changed all templates to use OmniGraph version of property widget
- Updated WritePrim to use target connections
- ReadPrimsBundle now accepts multiple inputs

## [1.81.5] - 2023-04-13
### Changed
- Make the ReadPrimAttribute node only throw errors on compute to avoid confusing users

## [1.81.4] - 2023-04-12
### Fixed
- OgnWritePrims regression for Fabric array attributes

## [1.81.3] - 2023-04-12
### Fixed
- The attribute arraySize of OgnConstructArray is now literalOnly
- Handle exceptions when attempting to remove connected attributes

## [1.81.2] - 2023-04-11
### Added
- Table of documentation links for nodes in the extension

## [1.81.1] - 2023-04-11
### Fixed
- Fixed a bug in OgnReadPrimAttribute when importing with timesamples

## [1.81.0] - 2023-04-05
- OgnAppendString is replaced by OgnBuildString and supports dynamic inputs.
- OgnAdd, OgnSubtract, OgnMultiply, OgnAnd, OgnOr, OgnNand, OgnNor are updated to support dynamic inputs.

## [1.80.4] - 2023-04-05
### Fixed
- OgnConstructArray updates the arraySize correctly when an input cannot be removed because it is connected
- OgnConstructArray removes input0 when the arraySize is set to 0

## [1.80.3] - 2023-04-05
### Fixed
- Fixed incorrect object in template

## [1.80.2] - 2023-04-05
### Changed
- Do not abuse `IBundle` to copy attribute, use `IAttributeData` instead.

## [1.80.1] - 2023-04-03
### Changed
- Name consistency pass
- Added timcode to read/write prim Inputs group

## [1.80.0] - 2023-04-03
###  Added
- Added a target input to nodes that currently take prim paths and prefer the target if both are provided

## [1.79.1] - 2023-03-31
### Changed
- Optimized OgnWritePrims by minimizing number of API calls.

## [1.79.0] - 2023-03-31
### Changed
- Updated tests for target output change to relationship

## [1.78.0] - 2023-03-30
### Changed
- Vectorized GetParentPrims, GetPrimPath, GetPrimPaths
- Changed ConstantPrims to use an outputOnly input

## [1.77.1] - 2023-03-29
### Changed
- ConstantPrims and GetParentPrims tagged for multiple input targets

## [1.77.0] - 2023-03-28
### Added
- Target ports to OgnReadPrimMaterial
### Changed
- GetPrimPath handles empty inputs
- ToString converts empty tokens to empty strings

## [1.76.2] - 2023-03-28
### Fixed
- Failing target tests when ExecutionFramework is disabled

## [1.76.1] - 2023-03-24
### Changed
- Updated tests to check for new target python type (usdrt.Sdf.Path)

## [1.76.0] - 2023-03-24
### Changed
- Updated various nodes to use new target type for prim input

## [1.75.1] - 2023-03-21
### Fixed
- Fixed issue in ToToken/ToString where path types were ignored

## [1.75.0] - 2023-03-20
### Fixed
- Once node now resets correctly.
### Added
- Countdown node

## [1.74.0] - 2023-03-17
### Added
- Added new nodes related to target type
- Updated FindPrims with target output
### Fixed
- Updated AppendPath node with better checking for in valid paths

## [1.73.13] - 2023-03-17
### Changed
- Refactored nodes using the low performance anti-pattern of chained if statements to use direct type comparisons

## [1.73.12] - 2023-03-17
### Fixed
- Lint errors

## [1.73.11] - 2023-03-16
### Added
- "threadsafe" scheduling hints to OgnArrayLength, OgnAttrType, OgnEventUpdateTick, OgnExtractAttr, OgnGetAttrNames, OgnGetGraphTargetId, OgnGpuInteropCudaEntry, OgnGpuInteropRenderProductEntry, OgnGraphTarget, OgnHasAttr, OgnIsPrimActive, OgnReadOmniGraphValue, OgnReadPrimMaterial, OgnReadSetting, OgnReadVariable, OgnReadGamepadState, OgnReadKeyboardState, OgnGetPrimDirectionVector, OgnGetPrimLocalToWorldTransform, OgnMoveToTarget, OgnMoveToTransform, OgnRotateToOrientation, OgnRotateToTarget, OgnScaleToSize, OgnTranslateToLocation, OgnTranslateToTarget, OgnFindPrimsr, OgnGetPrimPath, and OgnGetPrimRelationship nodes.
- "usd-write" scheduling hints to OgnWriteSetting and OgnWriteVariable nodes.

## [1.73.10] - 2023-03-13
### Changed
- The arraySize attribute of node OgnConstructArray defaults to 1
### Fixed
- Changing the arraySize property of OgnConstructArray resizes the input ports

## [1.73.9] - 2023-03-10
### Fixed
- Properly re-resolve input attribute with auto conversion on load

## [1.73.8] - 2023-03-10
### Changed
- ReadPrimAttribute is now vectorized and (a lot) faster
- WritePrimAttribute is now vectorized and (a lot) faster

## [1.73.7] - 2023-03-06
### Fixed
- Setting proper evaluation mode when evaluating a single  graph through ABI

## [1.73.6] - 2023-03-01
### Fixed
- spurious error messages from ReadPrimAttribute, WritePrimAttribute empty attributes

## [1.73.5] - 2023-02-28
### Fixed
- Writing back to usd with a Write node in a for loop

## [1.73.4] - 2023-02-27
### Fixed
- Makes OgnFindPrim instantiatable

## [1.73.3] - 2023-02-27
### Fixed
- og tests failing: 'test_block_variant_set' and 'test_set_variant_selection'

## [1.73.2] - 2023-02-27
### Changed
- Reenable test_copy_attr test from omni.graph.nodes

## [1.73.1] - 2023-02-25
### Changed
- Modifed format of Overview to be consistent with the rest of Kit

## [1.73.0] - 2023-02-22
### Added
- Changed ReadPrim nodes to use nan as a default for timecode inputs

## [1.72.1] - 2023-02-22
### Added
- Links to JIRA tickets regarding filling in the missing documentation

## [1.72.0] - 2023-02-21
### Changed
- Variant nodes update

## [1.71.5] - 2023-02-19
### Changed
- Added label to the main doc page so that higher level docs can reference the extension
- Tagged for adding links to node documentation

## [1.71.4] - 2023-02-17
### Added
- "threadsafe" scheduling hints to OgnCreateTubeTopology, OgnCurveFrame, OgnCurveTubePositions,
  OgnCurveTubeST, OgnLengthAlongCurve, OgnSelectIf, and OgnToUint64 nodes.
### Removed
- "threadsafe" scheduling hint from OgnArrayLength node (uses bundles, which are not guaranteed
  to be threadsafe at the time of writing).

## [1.71.3] - 2023-02-15
### Fixed
- MakeArray resizing when inputs added/removed

## [1.71.2] - 2023-02-14
### Fixed
- OnGamepadInput, OnMouseInput for instancing

## [1.71.1] - 2023-02-10
### Changed
- Using fabric states for OgnAppendPath instead of internal state (improves perf)

## [1.71.0] - 2023-02-09
### Removed
- Moved `OgnSetViewportFullscreen` into the omni.graph.ui extension

## [1.70.0] - 2023-02-07
### Removed
- Obsolete test of builtins

## [1.69.1] - 2023-02-06
### Changed
- Add usd read/write hints to SetCameraTarget, SetCameraPosition, SetActiveViewportCamera

## [1.69.0] - 2023-02-03
### Added
- Sound category and Play, Stop, Pause Sound nodes

## [1.68.0] - 2023-02-03
### Added
- Add Absolute Node to compute absolute value for scalars and arrays.

## [1.67.1] - 2023-02-03
### Fixed
- Fixed incorrect warnings in Write Prims - OM-78182

## [1.67.0] - 2023-02-03
### Added
- Added `OgnSetViewportFullscreen` which toggles fullscreen on/off for viewport(s) and visibility on/off for all other panes.

## [1.66.4] - 2023-01-30
### Changed
- Removed the kit-sdk landing page
- Moved all of the documentation into the new omni.graph.docs extension

## [1.66.3] - 2023-01-27
### Changed
- Modified some node to be vectorization friendly

## [1.66.2] - 2023-01-23
### Added
- `OgnHasVariantSet`, `OgnGetVariantNames`, `OgnGetVariantSelection`, `OgnGetVariantSetNames`, `OgnClearVariantSelection` and `OgnSetVariantSelection`

## [1.66.1] - 2023-01-20
### Added
- `Read Prims` improved caching for bbox and xform

## [1.66.0] - 2023-01-12
### Added
- `Bundle Inspector` can now inspect recursive bundles.

## [1.65.0] - 2023-01-11
### Removed
- Gather prototype is gone
### Changed
- ABI calls to take into account instancing
- Few nodes implement vectorized computes

## [1.64.0] - 2022-12-23
### Added
- `WritePrims` to write a fan-in of hierarchical bundles back to Fabric or USD prims

## [1.63.1] - 2023-01-05
### Changed
- `Read Prims` no longer creates a custom attribute named `normals:interpolation` for skinnable prims.

## [1.63.0] - 2023-01-03
### Added
- `Read Prims` reads interpolation of the attribute. This feature allows `Import Usd Prim Data` node to be replaced with `Read Prims`.

## [1.62.2] - 2022-12-21
### Changed
- Refactored CUDA build to consolidate build functions and remove unnecessary rebuilds

## [1.62.1] - 2022-12-20
### Fixed
- `Read Prims` outputs invalid attribute data when reading multiple prims at non-default USD timecode.

## [1.62.0] - 2022-12-15
### Added
- `Read Prims` reads skeletal data and applies SkelBinding to deform skinnable prims.

## [1.61.5] - 2022-12-14
### Fixed
- ReadPrimAttributes was evicting from the cache all other attributes from the targetted prim that some other nodes could need

## [1.61.4] - 2022-12-14
### Fixed
- GatherByPath from failing when run twice. It shouldn't rely on static counters.

## [1.61.3] - 2022-12-02
### Fixed
- Forces WriteVariable to actually write the array value to the variable location, and bypass CoW

## [1.61.2] - 2022-11-11
### Fixed
- Convert if/else to switch case to improve performance of Magnitude node

## [1.61.1] - 2022-11-11
### Fixed
- Convert if/else to switch case to improve performance of Normalize node

## [1.61.0] - 2022-11-10
### Added
- OnMessageBusEvent

## [1.60.0] - 2022-11-08
### Added
- ReadStageSelection, IsPrimSelected

## [1.59.0] - 2022-11-03

### Added
- `Read Prims` outputs Multiple Primitives in a Bundle.
- `Read Prims into Bundle` outputs Multiple Primitives in a Bundle.
- `Extract Prim` takes Multiple Primitives input and extract Single Primitive in the output.
- `Type Pattern` to `Find Prims` and provided backward compatibility.

### Changed
- Reverted `Read Prim` functionality to output Single Primitive in a Bundle, deprecated and hidden.
- Reverted `Read Prim into Bundle` functionality to output Single Primitive in a Bundle, deprecated and hidden.
- Reverted `Extract Bundle` functionality.

## [1.58.3] - 2022-11-03
### Fixed
- Fixes WritePrimAttribute not loading correctly if inputs have auto-conversion

## [1.58.2] - 2022-11-03
### Fixed
- Bug in GatherByPath, FindPrims

## [1.58.1] - 2022-11-03
### Changed
- Custom layout for property panel of the `GetPrims` node.

## [1.58.0] - 2022-10-31
### Added
- Added `GetPrims` node to filter primitives in the input bundle by path and type.

## [1.57.1] - 2022-10-31
### Fixed
- IsEmpty now errors on un-resolved inputs

## [1.57.0] - 2022-10-28
### Added
- Pattern matcher, with exclusion support, for nodes: `FindPrims`, `ReadPrim`, `ReadPrimBundle`, `RemoveAttr`.

## [1.56.1] - 2022-10-26
### Changed
- Re-enabled unreliable tests: `test_remove_attr`, `test_rename_attr`

## [1.56.0] - 2022-10-19
### Added
-  New node Exponent
### Changed
- Update NthRoot node to check componentCount/baseType rather than rely on tryCompute

## [1.55.0] - 2022-10-12
### Added
- `ReadPrimIntoBundle` added an attribute filter that specifies names or wildcard patterns of the attributes to be imported.
- `ReadPrim` added an attribute filter that specifies names or wildcard patterns of the attributes to be imported.

## [1.54.1] - 2022-10-12
### Changed
- Flagged test_remove_attr as unreliable.

## [1.54.0] - 2022-10-07
### Changed
- `ExtractBundle` searches for one specific child bundle with a path in the input bundle.
- `ReadPrimIntoBundle` outputs multiple primitives in bundle.
- `ReadPrimIntoBundle`'s primPath attribute became an extended attribute with supporting `token`, `token[]` and `path`.
- `ReadPrim` outputs multiple primitives in bundle.
- `ReadPrim` uses path pattern attribute to discover primitives in the stage using wildcard path pattern matching.

## [1.53.1] - 2022-10-07
### Changed
- Flag test_rename_attr as unreliable to get the integ-master queue moving again.

## [1.53.0] - 2022-10-05
### Added
- 'up' input to GetLookAtRotation node. Defaults to scene up. This prevents spinning about the aim vector.

## [1.52.0] - 2022-09-28
### Changed
- `ToString` no longer adds enclosing quotes for uchar[] inputs.

## [1.51.0] - 2022-09-28
### Added
- `FindPrims` added `pathPattern` attribute to search for primitives based on wildcard path pattern matching.

## [1.50.0] - 2022-09-23
### Modified
- GetPrimPath returns a "path" type as well as a token

## [1.49.0] - 2022-09-20
### Added
- New node ToUint64

## [1.48.1] - 2022-09-13
### Fixed
- Don't force FC to eject the prim every time we add another attribute.

## [1.48.0] - 2022-09-02
### Added
- Added IsEmpty node

## [1.47.0] - 2022-08-31
### Added
- Data model write scope to avoid race conditions during parallel executions

## [1.46.0] - 2022-08-26
### Added
- Added `GraphInstanceSpecific` to enable acceleration structures work per graph instance

## [1.45.2] - 2022-08-17
### Fixed
- Enabled Copy-on-Write for ArrayRemoveValue node

## [1.45.1] - 2022-08-24
### Changed
- Added the ability to force USD read in read nodes
- Added the ability to choose whether or not write nodes should write back to USD

## [1.45.0] - 2022-08-24
### Added
- Added `computeBoundingBox` support to ReadPrim node

## [1.44.0] - 2022-08-23
### Added
- Added USD timecode support to ReadPrim node

## [1.43.0] - 2022-08-17
### Changed
- added prim rel to ReadPrimRelationship node

## [1.42.0] - 2022-08-16
### Added
- EndsWith, StartsWith

## [1.41.2] - 2022-08-15
### Changed
- Read Prim Into Bundle value changes of Add Target parameter did not trigger node computation

## [1.41.1] - 2022-08-11
### Changed
- Added support for tuples and arrays to Ceil & Floor nodes

## [1.41.0] - 2022-08-11
### Added
- Path inputs to transformation nodes

## [1.40.1] - 2022-08-09
### Fixed
- Applied formatting to all of the Python files

## [1.40.0] - 2022-08-09
### Changed
- Removed omni.graph.scriptnode dependency

## [1.39.0] - 2022-08-04
### Added
- Added Ceil node

## [1.38.0] - 2022-08-03
### Added
- BundleInspector returns number of child bundles.

## [1.37.4] - 2022-08-03
### Fixed
- Handling of compatible types in the Make Array node and error with saving and loading

## [1.37.3] - 2022-07-28
### Fixed
- Handling of token and string input in the Compare node

## [1.37.2] - 2022-07-27
### Changed
- WritePrimAttribute to accommodate property panel fix

## [1.37.1] - 2022-07-25
### Fixed
- All of the lint errors reported on the Python files in this extension

## [1.37.0] - 2022-07-20
### Changed
- Added requiredRelationship feature to FindPrims

## [1.36.0] - 2022-07-14
### Changed
- Added +/- icons to Make Array

## [1.35.0] - 2022-07-07
### Changed
- Refactored imports from omni.graph.tools to get the new locations
### Added
- Test for public API consistency

## [1.34.1] - 2022-07-06
### Changed
- Prevent the re-setup of the ReadPrimAttribute and WritePrimAttribute each frame, and only re-do it when necessary

## [1.34.0] - 2022-07-05
### Added
- Added dynamic version of MakeArray node replacing the previous fixed version

## [1.33.1] - 2022-06-30
### Changed
- Convert CrossProduct node to C++

## [1.33.0] - 2022-06-29
### Added
- Added OgnReadSetting and OgnWriteSetting nodes.

## [1.32.0] - 2022-06-29
### Changed
- Added several new constant nodes

## [1.31.0] - 2022-06-24
### Changed
- Moved ReadMouseState into omni.graph.ui

## [1.30.3] - 2022-06-21
### Changed
- Convert DotProduct node to C++

## [1.30.2] - 2022-06-16
### Changed
- Now using the new write-back mechanism for nodes that should write back to USD

## [1.30.1] - 2022-06-15
### Changed
- Refactored compute algorithm to find the correct type faster

## [1.28.0] - 2022-05-31
### Added
- Nodes for vertex deformation using gpu interop and pre-render evaluation

## [1.30.0] - 2022-06-13
### Added
- Added OgnReadPrimMaterial node and OgnWritePrimMaterial node
- Added UsdShade to dependencies

## [1.29.0] - 2022-06-06
### Added
- Added ReadOmniGraphValue node

## [1.28.0] - 2022-05-30
### Added
- Added logic directory for logical operators
- Added boolean operator nodes in logic which support array and bool array inputs

### Changed
- Soft deprecated (via metadata:hidden) OgnBooleanExpr in favour of the new individual logical nodes
- Moved OgnBooleanExpr to logic directory
- Moved OgnBooleanNot to logic from math and renamed it to OgnNot to match the new naming convention
- Updated OgnBooleanNot to take bool or bool array input instead of just bool, to match the new logical operator nodes

## [1.27.3] - 2022-05-27
### Removed
- Some useless dependencies/visibility to PathToAttributeMap

## [1.27.2] - 2022-05-19
- Converted ToDouble to C++

## [1.27.1] - 2022-05-18
### Changed
- Converted Array Manipulation Nodes from python to C++.

## [1.27.0] - 2022-05-18
### Added
- Added OgnNegate node that multiplies input by -1

## [1.26.2] - 2022-05-16
### Fixed
- ReadPrimBundle/Attribute not correctly export the bounding box when asked to
- Fixed and Re-activated the test that exercises this feature

## [1.26.1] - 2022-05-16
### Fixed
- ToToken no longer appends quote characters to a converted string

## [1.26.0] - 2022-05-11
### Added
- ExtractBundle node: "explode" a bundle content into individual dynamic attributes
### Changed
- ReadPrimBundle/ReadPrimAttribute/WritePrim/WritePrimAtribute now uses OG ABI instead of direct Fabric access
- ReadPrim is using functionnality of ReadPrimBundle and ExtractBundle
- RemoveAttribute is using OGN wrapper instead of direct ABI access

## [1.25.4] - 2022-05-05
### Changed
- Converted OgnArraySetIndex node from python to C++.

## [1.25.3] - 2022-05-05
### Fixed
- Fixed string input for SelectIf node

## [1.25.2] - 2022-05-05
### Fixed
- Read/WritePrimAttribute will now issue error messages when `usePath` is true and attribute is not found.

## [1.25.1] - 2022-05-03
### Changed
- Converted OgnMagnitude node from python to C++.
- Converted OgnDivide node from python to C++.
- Converted OgnRound node from python to C++.

## [1.25.0] - 2022-05-02
### Changed
- Converted OgnToString, OgnToToken, OgnToFloat, OgnClamp to cpp
- MakeVector2/3/4 will now auto-resolve inputs when at least one input is resolved

## [1.24.0] - 2022-04-29
### Removed
- Obsolete tests
### Changed
- Made tests derive from OmniGraphTestCase

## [1.23.3] - 2022-04-28
### Changed
- Converted OgnSubtract node from python to C++.

## [1.23.2] - 2022-04-27
### Fixed
- Fixed bug in Distance3D, InvertMatrix and Round nodes

## [1.23.1] - 2022-04-26
### Fixed
- Fixed bug in MakeTransform node

## [1.23.0] - 2022-04-21
### Added
- GraphTarget node that retrieves the path of instance being run

## [1.22.0] - 2022-04-14
### Added
- Changed OgnTrig node into cpp node
- Broke OgnTrig node by operation

## [1.21.4] - 2022-04-18
### Changed
- Added support for more characters to Generate3dText

## [1.21.3] - 2022-04-12
### Fixed
- Fixed a bug in GetLookAtRotation and GetLocationAtDistanceOnCurve nodes

## [1.21.2] - 2022-04-08
### Changed
- Changed Compose/Decompose Tuple to Make/Break Vector for those nodes and make them C++ nodes

## [1.21.1] - 2022-04-11
### Fixed
- Generate3dText node

## [1.21.0] - 2022-04-05
### Added
- Added Generate3dText node

## [1.20.1] - 2022-04-08
### Added
- Added absoluteSimTime output attribute to the ReadTime node

## [1.20.0] - 2022-04-05
### Added
- Noise node

## [1.19.2] - 2022-04-06
### Added
- Added Normalize node

## [1.19.1] - 2022-04-03
### Fixed
- RotateToOrientation bug, Maneuver node bugs with varying target input.

## [1.19.0] - 2022-03-30
### Added
- WriteVariable value output port

## [1.18.4] - 2022-03-31
### Fixed
- Fixed crash when copying bundle with empty points attribute

## [1.18.3] - 2022-03-23
### Added
- Tests for maneuver nodes

## [1.18.3] - 2022-03-21
-- Revive functionnality from 1.16.1 with different approach

## [1.18.2] - 2022-03-18
### Fixed
- Naming of constant nodes

## [1.18.1] - 2022-03-16
### Fixed
- Bug in MoveToTransform

## [1.18.0] - 2022-03-14
### Added
- Added MakeTransformLookAt node.

## [1.17.1] - 2022-03-11
- Revert changes of 1.16.1

## [1.17.0] - 2022-03-10
### Added
- Added _outputs::shiftOut_, _outputs::ctrlOut_, _outputs::altOut_ to _ReadKeyboardState_ node.

## [1.16.1] - 2022-03-07
### Fixed
- ReadPrimBundle/ReadPrimAttribute can now use a usd time code at which to import the prim/attribute
- ReadPrimBundle now outputs its transform and BBox

## [1.16.0] - 2022-03-01
### Added
- *bundle_test_utils.BundleResultKeys*
- *bundle_test_utils.prim_with_everything_definition*
- *bundle_test_utils.get_bundle_with_all_results*
- *bundle_test_utils.bundle_inspector_results*
- *bundle_test_utils.verify_bundles_are_equal*
- *bundle_test_utils.filter_bundle_inspector_results*
### Fixed
- Made bundle tests and utility node tests use the Controller
- GatherByPath, add checkResyncAttributes attribute
### Changed
- Deprecated old bundle test utilities that relied on USD save/read and OmniGraphHelper for functioning
- Updated some tests to use OmniGraphTestCase

## [1.15.0] - 2022-02-17
### Fixed
- added a "path"" constant node

## [1.15.0] - 2022-02-15
### Changed
- WritePrim node now uses GPU arrays for points

## [1.14.0] - 2022-02-15
### Fixed
- added a dependency on omni.graph.scriptnode

## [1.13.2] - 2022-02-14
### Fixed
- add additional extension enabled check for omni.graph.ui not enabled error

## [1.13.2] - 2022-02-14
### Fixed
- MoveToTarget, RotateToTarget etc bug with float, half precision XformOp

## [1.13.1] - 2022-02-13
### Fixed
- ReadPrimBundle, ReadPrim now support token[] attributes

## [1.13.0] - 2022-02-11
### Added
- ReadVariable and WriteVariable nodes

## [1.12.3] - 2022-02-10
### Fixed
- Fixed MoveToTarget, MoveToTransform, RotateToTarget, GetPrimDirectionVector, GetMatrix4Quaternion and GetLocationAtDistanceOnCurve nodes behaviour when rotation is scaled

## [1.12.2] - 2022-02-07
### Fixed
- Fixed ArrayRotate, Compare, and SelectIf nodes behaviour when input was a token

## [1.12.1] - 2022-02-04
### Fixed
- RotateToOrientation, MoveToTransform attrib docs

## [1.12.0] - 2022-01-31
### Added
- Added shouldWriteBack input flag to GatherByPath node
### Fixed
- Fixed duplicate path behaviour for gather nodes

## [1.11.0] - 2022-01-27
### Added
- Added IsPrimActive node
- Added BooleanNot

## [1.10.1] - 2022-01-28
### Fixed
- spurious error message when creating _ReadPrim_
- updated extension doc

## [1.10.0] - 2022-01-27
### Added
- added ReadMouseState node

## [1.9.2] - 2022-01-28
### Modified
- added three test cases for NthRoot node

## [1.9.1] - 2022-01-24
### Fixed
- categories for several nodes

## [1.9.0] - 2022-01-19
### Added
- Added constant Pi node which will output a constant Pi or its multiple
- Added Nth Root node which will calculate the nth root of inputs

## [1.8.0] - 2022-01-17
### Added
- Added sets of tryCompute (including for arrays and tuples) functions to allow one non-runtime attribute input when two inputs
- Added Increment Node

## [1.7.1] - 2022-01-11
### Changed
- Changed token names in ReadGamepadState node
- Fixed incorrect default token in ReadGamepadState node

## [1.7.0] - 2022-01-10
### Added
- Added GetPrimDirectionVector node

## [1.6.0] - 2022-01-07
### Added
- Added ReadGamepadState node

## [1.5.3] - 2022-01-06
### Changed
- Categories added to all nodes

## [1.5.2] - 2022-01-05
### Modified
- _ReadPrimBundle_ and _ReadPrim_ now have a _sourcePrimPath_ bundle attribute which contains
  the path of the Prim being read.

## [1.5.1] - 2021-12-30
### Changed
- _ArrayIndex_ converted to C++, _AppendString_ now supports string inputs

## [1.5.0] - 2021-12-20
### Added
- Added _ReadTime_ and moved _GetLookAtRotation_ from _omni.graph.action_
## [1.4.0] - 2021-12-17
### Added
- Added ReadKeyboardState node

## [1.3.0] - 2021-12-02
### Added
- UI templates for Read/WritePrimAttribute nodes
### Changed
- Read/WritePrimAttribute nodes usePath attribute now defaults to False
## [1.2.2] - 2021-11-24
### Changed
- Prevented some problematic attributes from being exposed by ReadPrimAttributes and WritePrimAttributes
## [1.2.1] - 2021-11-19
### Changed
- Bug fix for ReadPrimAttributes
## [1.2.0] - 2021-11-04
### Added
- TransformVector
- RotateVector
### Changed
- Multiply: Support adding scalars to tuples
- Add: Support adding scalars to tuples
- MatrixMultiply: Support matrix * vector as well as matrix * matrix
### Moved
- OgnAdd2IntegerArray: Moved to omni.graph.test (deprecated by Add)
- OgnMultiply2IntegerArray: Moved to omni.graph.test (deprecated by Multiply)

## [1.1.0] - 2021-10-17
### Added
- PrimRead, PrimWrite

## [1.0.0] - 2021-03-01
### Initial Version
- Started changelog with initial released version of the OmniGraph core
