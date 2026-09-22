# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [509.1.0] - 2025-08-21
- Set display name for material prims
- Author widths primvar for USD Basis Curves
- Update to HOOPS Exchange 2025.6
- Only specialize Materials when the instancing style requires it
- Omit test scripts in test coverage

## [509.0.4] - 2025-08-01
- Add `Known Issues` section to README.md
- Fix publishing issue

## [509.0.3] - 2025-07-15
- Deduplicate Materials

## [509.0.2] - 2025-07-11
- Author primvar display colors and opacities when materials are disabled
- Added instancing style parameter
- Move Looks scope to child of default prim
- Update to HOOPS Exchange 2025.5
- Improved Parameters test

## [509.0.1] - 2025-07-07
- Update Nucleus test path
- Fixed convert options mapping

## [509.0.0] - 2025-06-30
- Update to Kit 108 / USD 25.02 / Python 3.12
- Build flavor support
- Add tokens module to public Python API

## [508.0.2] - 2025-06-11
- Update to HOOPS Converter tagged release package

## [508.0.1] - 2025-06-10
- Update creator metadata to include extension and backend converter library versions

## [508.0.0] - 2025-06-10
- Update to HOOPS CAD Converter version `8.0.0`
- The `Prototypes` Prim is a `Scope` rather than having an undefined type name
- Addressed memory leak vulnerabilities
- Fixed conversion failures due to `UnicodeDecodeError` on Linux
- BIM relationships are translated to `UsdRelationships` for IFC models
- Conversion arguments and `Parameters` are logged at the start of conversion
- Conversion failures are correctly handled and logged

### `omni.converter.hoops`
- Renamed `CadConverter` class to `Converter`
- Renamed `hoopsExchangeCADConverterSpec` class to `Parameters`
- Changed `Converter` class constructor to accept `Parameters`
- Changed `Converter::convert()` to return a `Result` object
- Changed `omni::converter::hoops::convert()` function signatures
- Changed `Converter::convert()` function signatures
- Removed `Converter::getCachedStageId()` function

## [507.5.3] - 2025-05-22
- Fix reggression when writing local

## [507.5.2] - 2025-05-21
- Filter raw args before conversion
- Fix conversion failure when writing to Nucleus

## [507.5.1] - 2025-05-06

- Update to HOOPS Exchange SDK 2025.3.0

## [507.5.0] - 2025-05-01

- Enable metadata convert option also converts BIM relationships for .ifc models

## [507.4.2] - 2025-05-09

- Fix dependency version constraints to properly handle minor and patch version updates

## [507.4.1] - 2025-04-28

- Update to official HOOPS Converter 7.1.1 release package

## [507.4.0] - 2025-04-24

- Add `is_format_supported` API to fix supported file format verification

## [507.3.2] - 2025-04-24

- Package tokens python module

## [507.3.1] - 2025-04-22

- Fix missing metadata
- Only set Attribute values if a value was defined in HOOPS

## [507.3.0] - 2025-04-18

- Expose option to choose between USD Preview Surface and OmniPBR materials (OmniPBR includes USD Preview Surface support)

## [507.2.1] - 2025-04-09

- Update HOOPS Converter backend converter dependency package after updating Gitlab CI/CD

## [506.2.0] - 2025-03-21

- Update converter filter name

## [507.1.1] - 2025-03-14

- Only read attributes when metadata is being converted

## [507.1.0] - 2025-03-12

- omni.usdex.libs dependency setup

## [507.0.1] - 2025-03-06

- Remove Direct X library

## [507.0.0] - 2025-02-14

- ABI upgrade

## [506.0.4] - 2025-02-03

- Tessellation bug fix

## [506.0.3] - 2025-01-31

- Update to hoops exchange sdk 2025.1.0

## [506.0.2] - 2025-01-29

- Fix empty metadata value display

## [506.0.1] - 2025-01-28

- Remove Carb dependency from Hoops Converter

## [506.0.0] - 2025-01-24

- Progress logging refactor

## [505.0.1] - 2025-01-07

- Update backend converter dependency from release/203.0 branch

## [505.0.0] - 2024-12-17

- Update to Kit 107, USD 24, and Python311

## [504.5.0] - 2024-12-03

- Update omni.kit.converter.common dep to 503.3.0

## [504.4.1] - 2024-12-02

- Update to latest Kit-kernel 106.5

## [504.4.0] - 2024-11-26

- Update to Hoops Exchange SDK 2024.8.0

## [504.3.1] - 2024-11-25

- Fixed incorrect value for double type metadata conversion.
- Fixed crash caused by invalid attributes.

## [504.3.0] - 2024-11-20

- Update to Kit-kernel 106.5

## [504.2.1] 2024-11-18

- Fix invalid time format for metadata conversion.

## [504.2.0] 2024-11-14

- Merge release 202.0.0 updates into master
- Update to ODA SDK 25.8

## [504.1.5] - 2024-11-08

- Update documentation for 202.0.0 release.

## [504.1.4] - 2024-10-25

- Fix bug where meters per unit selection doesn't get applied through HOOPS Converter

## [504.1.3] - 2024-10-25

- Update documentation.

## [504.1.2] - 2024-10-22

- Update dependencies from release branch

## [504.1.1] - 2024-10-18

- Update documentation for 202.0 release.

## [504.1.0] - 2024-10-18

- Update omni.kit.converter.common version supporting helpful quick links.

## [504.0.0] - 2024-10-17

- Migrate from CSDK to USD Exchange

## [503.1.0] - 2024-10-16

- Bump dependency versions.

## [503.0.0] - 2024-10-09

- Add option to override up-axis and meters per unit USD stage metrics with Scene Optimizer

## [502.0.0] - 2024-10-04

- Add option to specify USD output file format.
- Add option to specify USD output file name.

## [501.3.1] - 2024-10-04

- Fix crash upon tessellating inconsistent mesh.

## [501.3.0] - 2024-10-02

- Updated HECC dependency containg 2024.6.0 Hoops SDK to address security vulnerability
- Link hoops extension import options to the backend converter's settings for metadata and hidden object handling.

## [501.2.0] - 2024-09-30

- Add Scene Optimizer string config option

## [501.1.1] - 2024-09-23

- Use standard carb logging

## [501.1.0] - 2024-09-18

- Update kit-kernel to 106.2

## [501.0.0] - 2024-09-16

- Add version constraints in toml and bump hoops/hoops_core major semver

## [500.3.0] - 2024-09-06

- Added Autodesk 3DS, 3MF, ACIS, FBX, OBJ, GLTF/GLB supports.

## [500.2.0] - 2024-09-09

- Add convert metadata UI option

## [500.1.1] - 2024-09-06

- Inconsistent tessellation fix.
- Default COLLADA and GLTF conversions to Y-up

## [500.1.0] - 2024-09-05

- Bump extension semantic minor version

## [500.0.18] - 2024-09-05

- Add Collada to USD conversion support.

## [500.0.17] - 2024-08-29

- Update documentation; Add licensing terms and third party notices.

## [500.0.16] - 2024-08-26

- Add bConvertMetadata option

## [500.0.15] - 2024-08-23

- Remove test data from package

## [500.0.14] - 2024-08-16

- Rhino conversion support

## [500.0.13] - 2024-07-24

- Merge release 201.1.0 updates into master. Update backend converter dep

## [500.0.12] - 2024-07-16

- Update to the latest stable Kit-Kernel 106.0.1

## [500.0.11] - 2024-07-03

- Update backend converter deps

## [500.0.10] - 2024-07-02

- Updated documentation formatting for converter options

## [500.0.9] - 2024-07-01

- Added documentation on bConvertCurves

## [500.0.8] - 2024-07-01

- Exposes bConvertCurves for backend converters. Users may enable conversion this via converter_options

## [500.0.7] - 2024-06-28

- Destroy log consumer after conversion.

## [500.0.6] - 2024-06-24

- Updated to Kit 106.0.1

## [500.0.5] - 2024-06-17

- Audited documentation and updated based on changes for release 201.1.

## [500.0.4] - 2024-06-14

- vulnerability fixes for variable casting and copying strings

## [500.0.3] - 2024-06-14

- Update test to ignore folder in test_data

## [500.0.2] - 2024-06-13

- Adopt Connect SDK 1.1.0 pre-release. Update converter backend dependencies as a result of CSDK update

## [500.0.1] - 2024-06-11

- Consolidate changelog pre-release entries

## [500.0.0] - 2024-06-06

- Bump semantic version for resolving versions in ETM tests.

## [2.0.2] - 2024-05-31

- Use converters' packages built against Ubuntu 20.04

## [2.0.1] - 2024-05-30

- Adopt Connect SDK 1.0.0

## [2.0.0] - 2024-05-30

- Use semantic versioning for extensions. Use external/marketing version in CHANGELOG.md

## [201.1.0] - 2024-05-30

- Update to use omni.connect.hoops Python module
- Skip test for codeless omni.kit.converter.cad extension
- Update convert method signature
- Add progress callback logging
- Update to HOOPS Exchange 2024.3.0
- Converter now takes absolute usd file output path as input.
- Materials deduplication fix.
- Added Convert Visible Only UI option
- Refactored to share code in omni.kit.converter.common
- Renamed cad_core to hoops_core
- Updated set_app_data to include client name / version
- Run scene optimizer as post-conversion task
- Remove converter name from method signature
- Update extension.toml to lock extension to Kit SDK version being used
- Update to 201.1.0, move connect-sdk and scene optimizer to omni.kit.converter.common

## [201.0.0] - 2024-03-12

- Update HOOPS Converter. Resolves Issue with retrieving and setting transparency/opacity values
- Resolves issue converting colors from STEP Files
- Resolves issue converting colors from STEP files and other supported CAD formats
- Update HOOPS Converter
- Remove Nucleus test case from unreliable test cases
- Apply file scale to stage's MetersPerUnit
- Update to official Connect SDK 0.7.0 and Kit-kernel 106.0
- Switch to omni::connect::core::getValidPrimName
- Add usd module dependency
- Use same kit-kernel version as Connect SDK
- Updated keywords for improving searchability for CAD Converters
- Fix path to scene optimizer for Connect SDK
- Utilized UsdGeomSubsets to index triangles and set all available colors/opacity values during a mesh conversion
- Update Connect SDK to release 0.6.0
- add dependency range for optional service
- fix etm - use explicit pre-release
- etm-failure-fix and merge release to master
- Update HECC dependency. Resolves issue with logic that determines if a prim can be set instanceable.
- Update file regex for Siemens NX files

## [200.1.1] - 2023-11-29

- Fix file regex for Siemens NX files
- Update HECC dependency. Resolves issue with logic that determines if a prim can be set instanceable.
- Update file regex for Siemens NX files
- Handle scenario when get_local_file_async() is not able to pull down nucleus file to local OV cached folder
- Update dependency version in extension.toml
- Update to OMFP-3756\. Supports CAD files with a version suffix greater than 9\. (i.e., car_bumper.prt.42)
- Resolves issue saving files with valid characters in filename (i.e., periods)
- Fix model naming when converting models located on nucleus.
- Update HOOPS Exchange CAD Converter dependency to release/200.1
- Fix GetString() Memory Leak in HOOPS.
- Hoops converter update to resolve issue processing entity reference data
- Connect SDK and Scene Optimizer Updates for Connectors and Converters
- [CAD Converter] Make Prototypes prim abstract class
- [CAD Converter] Error handling when failing to write to Nucleus.
- [CAD Converter] Do not set instanceable for single references.
- Change version lock on "omni.kit.converter.common"

## [200.1.0] - 2023-10-20

## Fixed

- [CAD Converter] Creo ProE models should import as Y-Up.
- [CAD Converter] Cannot convert same file twice
- [CAD Converter] Apply correct xformOp in USD when instancing is set to false
- [CAD Converter] Create binary file when saving USD.

## New

- [CAD Converter] Hoops converter interface use config objects
- [CAD Converter] Hoops exchange should allow specified output filename
- [CAD Converter] Pass HOOPS Error Codes to CAD Core
- [CAD Converter] Add progress reporting
- [CAD Converter] Allow user to cancel a conversion task
- [CAD Converter] Do not create output dir if "Current Stage" conversion selected
- [CAD Converter] Only make prims that don't have opinions about children instanceable.
- [CAD Converter] Fix issue where conversion task would lock the GUI.
- [CAD Converter] Update runtime dependencies
- [CAD Converter] Added creator metadata

## [200.0.0] - 2023-05-11

- Split UI and Core CAD Converter
