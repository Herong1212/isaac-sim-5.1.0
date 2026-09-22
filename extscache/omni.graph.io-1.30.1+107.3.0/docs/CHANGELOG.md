(changelog_omni_graph_io)=

# Changelog

This document records all notable changes to ``omni.graph.io`` extension.
This project adheres to `Semantic Versioning <https://semver.org/>`_.

## [1.30.1] - 2025-06-17
### Changed
- Declare deprecation in extension metadata

## [1.30.0] - 2024-11-18
### Changed
- Jumping versions for 107 to leave room for changes to 106.*-based builds.

## [1.21.0] - 2024-11-15
### Changed
- Added public API doc

## [1.20.0] - 2024-09-19
### Changed
- bumping version to make room for 106.2-based extensions

## [1.10.0] - 2024-08-09
### Changed
- bumping version to make room for 106-based extensions

## [1.8.1] - 2024-05-30
### Changed
- Updated the formatting

## [1.8.0] - 2024-05-17
### Added
- Update the 'support_level' entry in the configuration files to match the release requirements

## [1.7.1] - 2024-04-17
### Added
- Add a 'support_level' entry to the configuration file of the extensions

## [1.7.0] - 2024-01-16
### Changed
- All nodes have been moved to the omni.graph.nodes extension
- Extension dependency changed to omni.graph.nodes
### Removed
- All nodes, tests and code files have been removed from this extension

## [1.6.0] - 2023-08-19
### Removed
- Dependency on the downstream extension omni.graph.ui

## [1.5.1] - 2023-06-27
### Fixed
- Refactored OmniGraph documentation to point to locally generated files

## [1.5.0] - 2023-06-20
### Changed
- Use Change Tracking for bundles from omni.graph.core

## [1.4.5] - 2023-05-31
### Fixed
- Adjusted the CRLF settings for the generated .md node table of content files

## [1.4.4] - 2023-04-11
### Added
- Table of documentation links for nodes in the extension

## [1.4.3] - 2023-03-16
### Added
- "threadsafe" scheduling hint to OgnBundleToUSDA node.

## [1.4.2] - 2023-03-07
### Added
- "usd-write" scheduling hint to OgnExportUSDPrim

## [1.4.1] - 2023-02-25
### Changed
- Modifed format of Overview to be consistent with the rest of Kit

## [1.4.0] - 2023-02-23
### Removed
- omni.graph.io.python module

## [1.3.0] - 2023-02-17
### Changed
- Soft deprecate INode::(de)registerPathChangedCallback

## [1.2.9] - 2023-01-30
### Changed
- Removed the kit-sdk landing page
- Moved all of the documentation into the new omni.graph.docs extension

## [1.2.8] - 2023-01-13
### Changed
- Import Type is always on to match Read Prims behavior.

## [1.2.7] - 2022-12-21
### Changed
- Refactored CUDA build to consolidate build functions and remove unnecessary rebuilds

## [1.2.6] - 2022-12-15
### Fixed
- Fixed a bug in OgnImportUSDPrim to output deformed points and normals

## [1.2.5] - 2022-11-18
### Changed
- Allow to be used in headless mode
## [1.2.4] - 2022-08-22
### Changed
- Allow OgnImportUSDPrim to have targets that don't exist

## [1.2.3] - 2022-08-09
### Fixed
- Applied formatting to all of the Python files

## [1.2.2] - 2022-08-09
### Fixed
- Fixed backward compatibility break for the deprecated `IDirtyID` interface.

## [1.2.1] - 2022-08-03
### Fixed
- Compilation errors related to deprecation of methods in ogn bundle.

## [1.2.0] - 2022-07-28
### Deprecated
- Deprecated `IDirtyID` interface
- Deprecated `BundleAttrib` class and `BundleAttribSource` enumeration
- Deprecated `BundlePrim`, `BundlePrims`, `BundlePrimIterator` and `BundlePrimAttrIterator`
- Deprecated `ConstBundlePrim`, `ConstBundlePrims`, `ConstBundlePrimIterator` and `ConstBundlePrimAttrIterator`

## [1.1.0] - 2022-07-07
### Added
- Test for public API consistency
- Added build handling for tests module

## [1.0.10] - 2021-11-19
- Added option on ImportUsdPrim to include local bounding box of imported prims as a common attribute.
- Fixed case where Import is not re-computed when a transform is needed and an ancestor prim's transform has changed.

## [1.0.9] - 2021-11-10
- Added option on ExportUSDPrim node type to remove, from output prims, any authored attributes that aren't being exported

## [1.0.8] - 2021-10-22
- Should be identical to 1.0.7, but incrementing the version number just in case, for logistical reasons

## [1.0.7] - 2021-10-14
- Added option to export time sampled data to specified time in ExportUSDPrim node type

## [1.0.6] - 2021-10-05
- Fixed re-importing of transforming attributes in ImportUSDPrim node type when transforms change

## [1.0.5] - 2021-09-24
- Added attribute-level change tracking to ImportUSDPrim node type

## [1.0.4] - 2021-09-16
- Added "Attributes to Import" and "Attributes to Export" to corresponding nodes to reduce confusion about how to import/export a subset of attributes
- Added support for importing/exporting "widths" interpolation from USD

## [1.0.3] - 2021-08-18
- Updated for an ABI break in Kit

## [1.0.2] - 2021-08-17
- Fixed crash related to ImportUSDPrim node type and breaking change in Kit from eTransform being deprecated in favour of eMatrix

## [1.0.1] - 2021-08-13
- Fixed crash related to ImportUSDPrim node type

## [1.0.0] - 2021-07-27
### Added
- Initial version. Added ImportUSDPrim, ExportUSDPrim, TransformBundle, and BundleToUSDA node types.
