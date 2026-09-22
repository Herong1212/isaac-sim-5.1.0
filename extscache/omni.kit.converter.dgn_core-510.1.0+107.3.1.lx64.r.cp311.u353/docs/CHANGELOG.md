# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [510.1.0] - 2025-08-21
- Add support for `MergedAttributeStyle.ePrimvar` in `Parameters.mergedAttributeStyle`.
- Exposed the name of Element ID primvar as `omni.converter.dgn.tokens.elementIdPrimvar`.
- Triangulation of Meshes is now optional based on `Parameters.triangulate`. The default value is `true`.
- Validate transform scale of 2D objects.
- Display name metadata is authored for metadata `UsdGeomSubsets`.
- Graphics Elements are sorted by Element ID before conversion to make results more consistent.
- Display name metadata is authored for all Prims that could not use the prefered name.
- The element type is transcoded with the rest of the Prim name rather than added as a suffix.
- Prims representing merged Graphics Elements no longer have an element Id in their name.
- Support basis curve width and expose `fallbackCurveWidth`.
- Add `mergeCurves` option to control curve merging.
- Skip the translation of Graphics Elements that do not have valid extents.
- Fallback to using element color for color-by-level element if the level has override color flag turned off.
- Improved unit test coverage

## [510.0.7] - 2025-08-18
- Respect Level based color override flag.

## [510.0.6] - 2025-08-07
- Skip extrusion solids that do not have valid extents

## [510.0.5] - 2025-08-01
- Fix publishing issue

## [510.0.4] - 2025-07-30
- Update to tagged DGN Converter package v10.0.2

## [510.0.3] - 2025-07-28
- Connect SDK setup for Kit 106.5 flavor

## [510.0.2] - 2025-07-11
- Improved Parameters test
- Update ODA Kernel and Drawings SDKs to version 26.6

## [510.0.1] - 2025-07-07
- Update Nucleus test path
- Fixed convert options mapping

## [510.0.0] - 2025-06-30
- Update to Kit 108 / USD 25.02 / Python 3.12
- Build flavor support
- Update ODA Kernel and Drawings SDKs to version 26.5
- Add tokens module to public Python API

## [509.1.0] - 2025-06-16
- The name of `Model`, `CellHeader` and `SharedCellDefinition` elements is stored as a `UsdAttribute`
- Fixed non-deterministic behavior in mesh transform calculations.
- Fixed incorrect scaling of mirrored transforms
- Fixed incorrect rotations
- Improved logging of Elements skipped during conversion

## [509.0.1] - 2025-06-11
- Update creator metadata to include extension and backend converter library versions

## [509.0.0] - 2025-06-10
- Update to DGN CAD Converter version `9.0.0`
- A transform is applied to `Mesh` prims to place them at the centroid of their combined Graphics Elements
- Conversion arguments and `Parameters` are logged at the start of conversion
- Conversion failures are correctly handled and logged

### `omni.converter.dgn`
- Changed module from `omni.connect.dgn` to `omni.converter.dgn`
- Renamed `Spec` class to `Parameters`
- Changed `Converter` class constructor to accept `Parameters`
- Changed `Converter::convert()` to return a `Result` object
- Changed `omni::converter::dgn::convert()` function signatures
- Changed `Converter::convert()` function signatures

## [508.0.1] - 2025-05-21
- Fix conversion failure when writing to Nucleus

## [508.0.0] - 2025-05-09
- Update ODA Kernel and Drawings SDKs to version 26.3
- Added omni.connect.dgn.FilterStyle enum.
    - eNone: Apply no filtering
    - eOmit: Do not convert the filtered element or its descendants
    - eDeactivate: Convert all elements and deactivate the ones that were filtered
    - eHide: Convert all elements and hide the ones that were filtered
- Added new Level Filtering properties to omni.connect.dgn.Spec
    - levelFilterStyle: Style to use for filtering Elements based on the Level they are members of
    - levelIncludes: A list of patterns used to identify Levels to be included in the filtered list
    -   levelExcludes: A list of patterns used to identify Levels to be excluded from the filtered list

## [507.1.4] - 2025-05-09

- Fix dependency version constraints to properly handle minor and patch version updates

## [507.1.3] - 2025-04-28
- Update to official DGN Converter 7.2.0 release package

## [507.1.2] - 2025-04-24

- Package tokens python module

## [507.1.1] - 2025-04-22

- Remove SQLite dependency

## [507.1.0] - 2025-04-18

- Expose option to choose between USD Preview Surface and OmniPBR materials (OmniPBR includes USD Preview Surface support)

## [507.0.1] - 2025-04-14

- Fill color fix

## [507.0.0] - 2025-04-09
- Update backend DGN Converter library. Changes include:

    - The default Prim name is now based on the input DGN file path rather than the output USD file path
    - The global origin of Models are no longer applied as an XformOp by default
    - Shared Cell Definition elements live below a Prototypes prim and are abstract, these are composed onto Shared Cell References
    - Transforms are applied to Elements based on the values stored in the DGN file
    - Point based data is stored in local space by subtracting the transformation relative to the Model Prim
    - The public API of the Converter class has been simplified
    - The summary of skipped objects is logged at status rather than warning level

## [506.2.0] - 2025-03-21

- Update converter filter name

## [506.1.0] - 2025-03-12

- omni.usdex.libs dependency setup

## [506.0.1] - 2025-02-14

- Remove libxl.dll
- Remove unused libraries with vulnerabilities
- Fix smart solids level names

## [506.0.0] - 2025-02-14

- ABI upgrade

## [505.0.0] - 2025-01-24

- Progress logging refactor

## [504.0.2] - 2025-01-09

- Skip converting DGN element with invalid mesh vertices

## [504.0.1] - 2025-01-07

- Update backend converter dependency from release/203.0 branch

## [504.0.0] - 2024-12-17

- Update to Kit 107, USD 24, and Python311

## [503.4.0] - 2024-12-03

- Add option to skip mesh merging

## [503.3.1] - 2024-12-02

- Update to latest Kit-kernel 106.5

## [503.3.0] - 2024-11-20

- Update to Kit-kernel 106.5

## [503.2.1] 2024-11-19

- Remove TD_PDFToolkit dependency
- Update client and python library versions.

## [503.2.0] 2024-11-14

- Merge release 202.0.0 updates into master
- Update to ODA SDK 25.8

## [503.1.4] - 2024-11-15

- Remove TD_PDFToolkit library from ODA 25.4 package

## [503.1.3] - 2024-11-08

- Update documentation for 202.0.0 release.

## [503.1.2] - 2024-10-22

- Update dependencies from release branch

## [503.1.1] - 2024-10-18

- Update documentation for 202.0 release.

## [503.1.0] - 2024-10-18

- Update omni.kit.converter.common version supporting helpful quick links.

## [503.0.0] - 2024-10-17

- Revert DGN Converter ODA library to version 25.4 to avoid version mismatch with HOOPS Converter

## [502.1.0] - 2024-10-16

- Bump dependency versions.

## [502.0.0] - 2024-10-09

- Add option to override up-axis and meters per unit USD stage metrics with Scene Optimizer

## [501.0.0] - 2024-10-04

- Add option to specify USD output file format.
- Add option to specify USD output file name.

## [500.3.0] - 2024-09-30

- Add Scene Optimizer string config option

## [500.2.0] - 2024-09-18

- Update kit-kernel to 106.2

## [500.1.2] - 2024-09-16

- Add version constraints in toml

## [500.1.1] - 2024-09-09

- Fix bug where conversion would always generate UVs regardless of the user specified value.

## [500.1.0] - 2024-09-05

- Bump extension semantic minor version

## [500.0.26] - 2025-09-19

- Republish without pre-release tags with kit-kernel 106.1

## [500.0.25] - 2025-09-18

- Update kit-kernel to 106.2; Increment the PATCH version to create a gap between this and previous versions.

## [500.0.21] - 2024-09-10

- Resolve ETM issues by setting range on extension version dependencies

## [500.0.20] - 2024-09-09

- Create release branch with 201.2.0 hot fix updates

## [500.0.19] - 2024-09-09

- Update to ODA SDK 25.7 to fix libpng vulnerabilities
- Update to ODA SDK 25.7 to fix OpenJPEG vulnerabilities
- Fix kinds.
- Fix converted attribute name

## [500.0.18] - 2024-08-30

- Update documentation; Add licensing terms and third party notices.

## [500.0.17] - 2024-08-30

- Fix missing geometry

## [500.0.16] - 2024-08-28

- Fix crash when converting extra graphics elements.

## [500.0.15] - 2024-08-23

- Remove test data from package

## [500.0.14] - 2024-08-01

- Switch DGN element ID from hexadecimal to decimal for prim names and attributes

## [500.0.13] - 2024-07-24

- Merge release 201.1.0 updates into master. Update backend converter dep

## [500.0.12] - 2024-07-16

- Update to the latest stable Kit-Kernel 106.0.1

## [500.0.11] - 2024-07-03

- Update backend converter deps

## [500.0.10] - 2024-07-11

- Updated documentation formatting for converter options
- Added curve merging; reverted bConvertCurves default to true

## [500.0.9] - 2024-07-01

- Added documentation on bConvertCurves

## [500.0.8] - 2024-07-01

- Sets bConvertCurves to false by default. Users may enable conversion this via converter_options

## [500.0.7] - 2024-06-28

- Destroy log consumer after conversion.

## [500.0.6] - 2024-06-24

- Updated to Kit 106.0.1

## [500.0.5] - 2024-06-17

- Audited documentation and updated based on changes for release 201.1.

## [500.0.4] - 2024-06-13

- Add "prefix" for DGN Attributes
- Filter out OdDgCellHeader2d from conversions causing crash for files with OdDgCellHeader2d elements

## [500.0.3] - 2024-06-13

- Adopt Connect SDK 1.1.0 pre-release. Update converter backend dependencies as a result of CSDK update

## [500.0.2] - 2024-06-11

- Consolidate changelog pre-release entries

## [500.0.1] - 2024-06-11

- Updated config file options - iTessLOD, hiddenLevels, levelNamePatterns, modelNamePatterns

## [500.0.0] - 2024-06-06

- Bump semantic version for resolving versions in ETM tests.

## [2.0.3] - 2024-05-31

- Use converters' packages built against Ubuntu 20.04

## [2.0.2] - 2024-05-30

- Write custom element ID attribute to USD.

## [2.0.1] - 2024-05-30

- Adopt Connect SDK 1.0.0

## [2.0.0] - 2024-05-30

- Use semantic versioning for extensions. Use external/marketing version in CHANGELOG.md

## [201.1.0] - 2024-05-30

- Remove deprecated variable from Overview.md
- Skip test for codeless omni.kit.converter.cad extension
- Added model name pattern and filtering to control conversion of DGN model elements
- Update convert method signature
- Subprocess progress handling
- Update to use ODA Kernel and Drawings SDK 25.4
- Fix issue with resolving input file path from Nucleus
- Error handling when optional config parameter isn't provided.
- Fix crash caused by invalid USD identifier
- Converter now takes absolute usd file output path as input.
- Added Convert Visible Only UI option
- Refactored to share code in omni.kit.converter.common
- Updated set_app_data to include client name / version
- Run scene optimizer as post-conversion task
- Remove converter name from method signature
- Update extension.toml to lock extension to Kit SDK version being used
- Update to 201.1.0, move connect-sdk and scene optimizer to omni.kit.converter.common

## [201.0.0] - 2024-03-13

- Add support for parametric volumes / extended elements and complex shapes
- Apply file scale to stage's MetersPerUnit
- Update to official Connect SDK 0.7.0 and Kit-kernel 106.0
- Update init.
- Update ODA SDK to 25.1 for curl and openssl
- add bConvertHidden option
- Support for Prim Names starting with illegal characters
- Use same kit-kernel version as Connect SDK
- Updated keywords for improving searchability for CAD Converters
- Update to DGN converter that uses Connect SDK
- Fix for spaces in filename for Windows
- Update Connect SDK to release 0.6.0
- add dependency range for optional service
- fix etm - use explicit pre-release
- etm-failure-fix and merge release to master
- Unicode name diffs
- Updated transforms for CellHeaders and SharedCellReferences
- Update dependency version in extension.toml

## [200.1.1] - 2023-11-22

- Memory leak fixes
- Configurable tessellations
- Support for Smart Solids/Surfaces added; LOD extent adjustment and object mesh API guard
- Scale recalculation and transform flips fix; post-Smart Solids/Surfaces: Manual calculation of normals; post-Smart Solids/Surfaces: Guards for color table
- Resolves issue saving files with valid characters in filename (i.e., periods)
- Add Smart Solids and Surfaces Support
- fix tesselation options and update documentation
- Add ability to hide layers during conversion
- Update DGN Converter dependency to release/200.1
- Memory leak fixes to handle DGN Error: "Out of Memory"
- Added Mesh Tessellation settings

## [200.1.0] - 2023-10-27

- Connect SDK and Scene Optimizer Updates for Connectors and Converters
- Error handling when failing to write to Nucleus.
- Change version lock on "omni.kit.converter.common"
- Added creator metadata
- Improved DGN coverage
- Update runtime dependencies
- Fix transforms and mesh point calculation
- Progress window fix
- progress and step callback function binding with C++ plugin
- Fix for conversion of DGN Shapes, Solids, Surfaces
- Disabled wireframe geometry conversion
- Export, or calculate if missing, DGN normals for converted geometry
- Merge meshes as DGN geometry is converted
- Updated DGN Converter - path validation adjustments, DGN model extent fix
- Updated DGN Converter - path validation
- default json file
- oda_dgn_converter library fix
- Initial build for omni.kit.converter.dgn_core
