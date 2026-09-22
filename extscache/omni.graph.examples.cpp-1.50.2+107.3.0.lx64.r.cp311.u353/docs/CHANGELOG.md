(changelog_omni_graph_examples_cpp)=

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.50.2] - 2025-02-06
### Changed
- linux toolchain compatibility upgrade

## [1.50.1] - 2025-01-07
### Changed
- Updates for latest Kit SDK

## [1.50.0] - 2024-11-18
### Changed
- Jumping versions for 107 to leave room for changes to 106.*-based builds.

## [1.41.0] - 2024-11-15
### Changed
- Build with Kit 107.0 with USD 24.05 and python 3.11

## [1.40.0] - 2024-09-19
### Changed
- bumping version to make room for 106.2-based extensions

## [1.30.0] - 2024-08-09
### Changed
- bumping version to make room for 106-based extensions

## [1.27.0] - 2024-07-31
### Changed
- Pathing for USD headers and libs.
### Added
- Test dependency on omni.hydra.usdrt_delegate.

## [1.26.2] - 2024-06-17
### Changed
- Use ConstructArray instead of MakeArray in tests

## [1.26.1] - 2024-05-30
### Changed
- Updated the formatting

## [1.26.0] - 2024-05-17
### Added
- Update the 'support_level' entry in the configuration files to match the release requirements

## [1.25.2] - 2024-05-10
### Changed
- Build changes to account for new stock OpenUSD library in kit.

## [1.25.1] - 2024-04-17
### Added
- Add a 'support_level' entry to the configuration file of the extensions

## [1.25.0] - 2024-04-10
### Changed
- Bumped dependency on omni.graph.core to version 2.177.1
- Bumped dependency on omni.graph.tools to version 1.77.0

## [1.24.0] - 2024-03-18
### Changed
- Bumped dependency on omni.graph.core to version 2.176.3

## [1.23.0] - 2024-02-15
### Changed
- Bumped dependency on omni.graph.core to version 2.174.2
- Bumped dependency on omni.graph.tools to version 1.76.1

## [1.22.0] - 2024-02-05
### Changed
- Bumped dependency on omni.graph.core to version 2.174.0
- Bumped dependency on omni.graph.tools to version 1.76.0

## [1.21.1] - 2024-02-03
### Changed
- Bumped minimum omni.graph.core extension version dependency to be compatible with changes to the INodeType interface and lazy graph executor.

## [1.21.0] - 2024-01-31
### Changed
- Bumped dependency on omni.graph.core to version 2.171.1
- Bumped dependency on omni.graph.tools to version 1.76.0

## [1.20.0] - 2024-01-30
### Changed
- Bumped dependency on omni.graph.core to version 2.170.1
- Bumped dependency on omni.graph.tools to version 1.74.0

## [1.19.0] - 2024-01-23
### Added
- Test coverage for the universal add node type

## [1.18.1] - 2024-01-22
### Fixed
- Made execution attribute descriptions consistent and informative

## [1.18.0] - 2024-01-18
### Changed
- Bumped dependency on omni.graph.core to version 2.169.1
- Bumped dependency on omni.graph.tools to version 1.73.0

## [1.17.1] - 2024-01-13
### Fixed
- Repository URL in config file.

## [1.17.0] - 2024-01-12
### Changed
- Bumped dependency on omni.graph.core to version 2.169.0
- Bumped dependency on omni.graph.tools to version 1.70.0

## [1.16.1] - 2024-01-12
### Changed
- Fix build warnings

## [1.16.0] - 2023-12-28
### Changed
- Bumped dependency on omni.graph.tools to version 1.69.0

## [1.15.0] - 2023-12-28
### Removed
- Filter on tests failing from an earlier Kit SDK update
### Changed
- Bumped dependency on omni.graph.core to version 2.167.0
- Bumped dependency on omni.graph.tools to version 1.68.0

## [1.14.1] - 2023-12-18
### Changed
- Address some security issues

## [1.14.0] - 2023-12-12
### Changed
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.13.0] - 2023-12-11
### Changed
- Bumped dependency on omni.graph.core to version 2.165.3
- Bumped dependency on omni.graph.tools to version 1.65.0

## [1.12.2] - 2023-12-08
### Changed
- Added Bundle section to Developer Reference

## [1.12.1] - 2023-11-30
### Changed
- Set the minimal omni.graph.core version required in order to properly load that extension

## [1.12.0] - 2023-11-10
### Fixed
- Code coverage filtering and additional tests

## [1.11.0] - 2023-11-09
### Fixed
- Code coverage filtering and additional tests

## [1.10.0] - 2023-10-05
### Changed
- Restore action nodes to .action from .action_nodes for forward-compatibility

## [1.9.5] - 2023-09-12
### Changed
- OM-106978 / OM-103829: Update to latest EF API (renamed traversal methods and node count)

## [1.9.4] - 2023-08-15
### Changed
- Fixed type name check in OverrideForEachPass

## [1.9.3] - 2023-08-11
### Fixed
- Version bump to force extension publication to fix Linux platform errors

## [1.9.2] - 2023-08-09
### Fixed
- Linux build errors
- Bumping versions to get the extension published from a more compatible Linux build configuration

## [1.9.1] - 2023-08-04
### Added
- Missing link of the data directory

## [1.9.0] - 2023-08-03
### Changed
- Moved the extension over from Kit

## [1.8.0] - 2023-07-30
### Changed
- Moved GPU interop nodes to omni.graph.image.nodes
### Added
- Dependency on omni.graph.image.nodes for backward compatibility

## [1.7.8] - 2023-07-21
### Changed
- Renamed Node::createForDef references to Node::create.

## [1.7.7] - 2023-06-27
### Fixed
- Refactored OmniGraph documentation to point to locally generated files

## [1.7.6] - 2023-06-27
### Changed
- Set up the extension to load python nodes and tests in parallel

## [1.7.5] - 2023-06-02
### Fixed
- OverrideForEachPass to work with new ActionGraph method of activation

## [1.7.4] - 2023-05-31
### Fixed
- Adjusted the CRLF settings for the generated .md node table of content files

## [1.7.3] - 2023-05-25
### Removed
- Removed the usage of the now-deleted EF runtime switch setting in one of the unit tests.

## [1.7.2] - 2023-05-12
### Added
- Set compute flags on node definitions in partition pass examples so that they respect the rules of PullGraphDef evaluation.
- Unit test to ensure that the change described above actually works.
### Changed
- Moved unit tests for partition pass examples out of omni.graph.test and into this extension.

## [1.7.1] - 2023-04-11
### Added
- Table of documentation links for nodes in the extension

## [1.7.0] - 2023-03-24
### Added
- EF Partition pass examples based off of this draft MR: https://gitlab-master.nvidia.com/omniverse/kit/-/merge_requests/21778.

## [1.6.9] - 2023-03-16
### Added
- "threadsafe" scheduling hint to OgnExampleExtractFloat3Array node.
- "usd-write" scheduling hints to OgnPrimDeformer1, OgnPrimDeformer1_GPU, OgnPrimDeformer2, and OgnScaleCubeWithPrim nodes.

## [1.6.8] - 2023-02-25
### Changed
- Modifed format of Overview to be consistent with the rest of Kit

## [1.6.7] - 2023-02-22
### Added
- Links to JIRA tickets regarding filling in the missing documentation

## [1.6.6] - 2023-02-19
### Changed
- Added label to the main doc page so that higher level docs can reference the extension
- Tagged for adding links to node documentation

## [1.6.5] - 2023-02-17
### Added
- "threadsafe" scheduling hints to OgnIK, OgnCompound, OgnSimple, OgnVersionedDeformer, OgnDeformer1_CPU,
  OgnDeformer1_GPU, OgnDeformer2_CPU, OgnDeformer2_GPU, OgnDeformerTimeBased, OgnExampleSimpleDeformer,
  OgnScaleCube, and OgnUniversalAdd nodes.

## [1.6.4] - 2023-01-30
### Changed
- Removed the kit-sdk landing page
- Moved all of the documentation into the new omni.graph.docs extension

## [1.6.3] - 2022-12-21
### Changed
- Refactored CUDA build to consolidate build functions and remove unnecessary rebuilds

## [1.6.2] - 2022-12-19
### Fixed
- Avoid null pointer dereferences in compute for various nodes

## [1.6.1] - 2022-12-15
### Fixed
- Added firewall test to OgnDeformer1Gather_GPU.cpp for null pointers to avoid crash

## [1.6.0] - 2022-12-13
### Removed
- Unnecessary bindings and interfaces that prevent safe unload

## [1.5.0] - 2022-12-13
### Removed
- Unnecessary bindings and interfaces that prevent safe unload

## [1.4.2] - 2022-10-26
### Changed
- Disabled test_om_43835.

## [Unreleased]

## [1.4.1] - 2022-08-09
### Fixed
- Applied formatting to all of the Python files

## [1.4.0] - 2022-07-07
### Added
- Test for public API consistency

## [1.3.0] - 2022-06-28
### Changed
- Modified the Python code to create a more definitive API surface

## [1.2.0] - 2022-06-23
### Changed
- Modified the Python code to create a more definitive API surface

## [1.1.0] - 2022-04-29
### Removed
- Obsolete settings test

## [1.0.1] - 2022-03-14
### Changed
- Added categories to node OGN

## [1.0.0] - 2021-03-01
### Initial Version
- Started changelog with initial released version of the OmniGraph core
