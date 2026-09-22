# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [508.1.0] - 2025-08-21
- Apply translation to geometry Prims to place them at the centroid of the Part
- Omit test scripts in test coverage

## [508.0.4] - 2025-08-01
- Fix publishing issue

## [508.0.3] - 2025-07-24
- Update native libraries

## [508.0.2] - 2025-07-11
- Improved Parameters test
- Fixed layer filtering

## [508.0.1] - 2025-07-07
- Update unit tests
- Fixed convert options mapping

## [508.0.0] - 2025-06-30
- Update to Kit 108 / USD 25.02 / Python 3.12
- Updated to OpenUSD Exchange SDK 1.2.0
- Creator metadata is authored in all USD Layers
- Build flavor support
- Add tokens module to public Python API

## [507.0.1] - 2025-06-11
- Update creator metadata to include extension and backend converter library versions

## [507.0.0] - 2025-06-10
- Update to JT CAD Converter version `8.0.0`
- Update to JT Toolkit version `11.7.1`
- Empty `UsdGeomPointBased` Prims are not defined if no `points` were generated
- Line strips where the end vertex of one line is collocated with the first vertex of the next will be joined together
- Constant display color primvars based on Material parameters are only authored in the absence of per vertex colors
- Conversion arguments and `Parameters` are logged at the start of conversion
- Per vertex normals are translated for `UsdGeomBasisCurves` and `UsdGeomPoints` prims
- Per vertex colors are translated for `UsdGeomMesh`, `UsdGeomBasisCurves` and `UsdGeomPoints` prims
- Constant widths are translated for `UsdGeomBasisCurves` prims
- Conversion failures are correctly handled and logged

### `omni.converter.jtk`
- Updated to OpenUSD Exchange SDK version `1.1.0`
- Renamed `ConverterParams` class to `Parameters`
- Changed `omni::converter::jtk::convert()` function signatures
- Changed `omni.converter.jtk::Converter::convert()` function signatures
- Removed `VtDict` support from `Parameters`
- Removed `Converter::setInstancingStyleOption()`

## [506.4.1] - 2025-05-22
- Fix reggression when writing local

## [506.4.0] - 2025-05-21
- Filter raw args before conversion
- Fix conversion failure when writing to Nucleus

## [506.3.3] - 2025-05-09

- Fix dependency version constraints to properly handle minor and patch version updates

## [506.3.2] - 2025-04-28

- Update to official JT Converter 7.1.0 release package

## [506.3.1] - 2025-04-24

- Package tokens python module

## [506.3.0] - 2025-04-18

- Expose option to choose between USD Preview Surface and OmniPBR materials (OmniPBR includes USD Preview Surface support)

## [506.2.0] - 2025-03-21

- Update converter filter name

## [506.1.1] - 2025-03-12

- Exclude plmxml library.

## [506.1.0] - 2025-03-12

- omni.usdex.libs dependency setup

## [506.0.2] - 2025-02-26

- Fix visibility for hidden elements

## [506.0.1] - 2025-02-14

- Avoid Crash on Conversion Failure

## [506.0.0] - 2025-02-14

- ABI upgrade

## [505.0.2] - 2025-01-30

- Exclude plmxml library.

## [505.0.1] - 2025-01-28

- Remove Carb dependency from JT Converter

## [505.0.0] - 2025-01-24

- Progress logging refactor

## [504.0.2] - 2025-01-07

- Update backend converter dependency from release/203.0 branch

## [504.0.1] - 2024-12-20

- Optimization for massive face sets conversion.

## [504.0.0] - 2024-12-17

- Update to Kit 107, USD 24, and Python311

## [503.3.0] - 2024-12-03

- Update omni.kit.converter.common dep to 503.3.0

## [503.2.1] - 2024-12-02

- Update to latest Kit-kernel 106.5

## [503.2.0] - 2024-11-20

- Update to Kit-kernel 106.5

## [503.1.4] 2024-11-14

- Merge release 202.0.0 updates into master

## [503.1.3] - 2024-11-08

- Update documentation for 202.0.0 release.

## [503.1.2] - 2024-10-22

- Update dependencies from release branch

## [503.1.1] - 2024-10-18

- Update documentation for 202.0 release.

## [503.1.0] - 2024-10-18

- Update omni.kit.converter.common version supporting helpful quick links.

## [503.0.0] - 2024-10-17

- Migrate from CSDK to USD Exchange

## [502.1.0] - 2024-10-16

- Bump dependency version.

## [502.0.0] - 2024-10-09

- Add option to override up-axis and meters per unit USD stage metrics with Scene Optimizer

## [501.0.0] - 2024-10-04

- Add option to specify USD output file format.
- Add option to specify USD output file name.

## [500.3.0] - 2024-09-30

- Add Scene Optimizer string config option

## [500.2.0] - 2024-09-18

- Update kit-kernel to 106.2

## [500.1.1] - 2024-09-16

- Add version constraints in toml

## [500.1.0] - 2024-09-05

- Bump extension semantic minor version

## [500.0.26] - 2025-09-19

- Republish without pre-release tags with kit-kernel 106.1

## [500.0.25] - 2025-09-18

- Update kit-kernel to 106.2; Increment the PATCH version to create a gap between this and previous versions.

## [500.0.18] - 2024-09-10

- Resolve ETM issues by setting range on extension version dependencies

## [500.0.17] - 2024-09-09

- Create release branch with 201.2.0 hot fix updates

## [500.0.16] - 2024-08-29

- Update documentation

## [500.0.15] - 2024-08-23

- Remove test data from package

## [500.0.14] - 2024-08-22

- Update documentation; Add licensing terms and third party notices.

## [500.0.13] - 2024-07-24

- Merge release 201.1.0 updates into master. Update backend converter dep

## [500.0.12] - 2024-07-16

- Update to the latest stable Kit-Kernel 106.0.1

## [500.0.11] -2024-07-03

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

- Fixd crash caused by invalid tessellation parameters

## [500.0.5] - 2024-06-24

- Updated to Kit 106.0.1

## [500.0.4] - 2024-06-17

- Audited documentation and updated based on changes for release 201.1.

## [500.0.3] - 2024-06-13

- Adopt Connect SDK 1.1.0 pre-release. Update converter backend dependencies as a result of CSDK update

## [500.0.2] - 2024-06-11

- Consolidate changelog pre-release entries

## [500.0.1] - 2024-06-11

- Updated config file options - sUsdSuffix, sFilePathIn, sFolderPathOut, instancingStyle

## [500.0.0] - 2024-06-06

- Bump semantic version for resolving versions in ETM tests.

## [2.0.2] - 2024-05-31

- Use converters' packages built against Ubuntu 20.04

## [2.0.1] - 2024-05-30

- Adopt Connect SDK 1.0.0

## [2.0.0] - 2024-05-30

- Use semantic versioning for extensions. Use external/marketing version in CHANGELOG.md

## [201.1.0] - 2024-05-30

- Remove deprecated BaseOptions class usage.
- Skip test for codeless omni.kit.converter.cad extension
- Add tessellation fallback parameters ui
- Update convert method signature
- Remove unused progress callbacks
- Log converted node types in post process.
- Converter now takes absolute usd file output path as input.
- Added Convert Visible Only UI option
- Refactored to share code in omni.kit.converter.common
- Updated set_app_data to include client name / version
- Run scene optimizer as post-conversion task
- Remove converter name from method signature
- Update extension.toml to lock extension to Kit SDK version being used
- Update to 201.1.0, move connect-sdk and scene optimizer to omni.kit.converter.common

## [201.0.0] - 2024-03-05

- Remove Nucleus test case from unreliable test cases
- Improve JT converter logging and add tooltip for instancing feature.
- Update to official Connect SDK 0.7.0 and Kit-kernel 106.0
- Update JT Converter.
- JT Connect SDK branch integration.
- Use same kit-kernel version as Connect SDK
- Updated keywords for improving searchability for CAD Converters
- Fix path to scene optimizer for Connect SDK
- Update Connect SDK to release 0.6.0
- add dependency range for optional service
- fix etm - use explicit pre-release
- etm-failure-fix and merge release to master

## [200.1.1] - 2023-11-27

- Handle scenario when get_local_file_async() is not able to pull down nucleus file to local OV cached folder
- Update dependency version in extension.toml
- Added test case for files with (.) in file name
- Fix file names with multiple suffixes.
- Update JT Converter dependency to release/200.1

## [200.1.0] - 2023-11-08

- Increase test coverage
- Connect SDK and Scene Optimizer Updates for Connectors and Converters
- [CAD Converter] Make Prototypes prim abstract class
- Error handling when failing to write to Nucleus.
- JTTK license update
- Change version lock on "omni.kit.converter.common"
- Added creator metadata
- Update runtime dependencies
- Create binary file when saving USD.
- Fix crash on import file overwrite.
- Removed unused code to improve unit test code coverage
- Fix incorrect normals
- Update to Scene Optimizer 105.1.10
- Load JSON config file from disk for Scene Optimizer
- Enable UV generation using Scene Optimizer
- Default to jt_core
- Updated JT converter for duplicate import fix.
- First first version of JT core extension.
