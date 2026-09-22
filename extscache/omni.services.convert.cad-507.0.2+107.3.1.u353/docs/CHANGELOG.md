# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [507.0.2] - 2025-08-01
- Fix publishing issue

## [507.0.1] - 2025-07-11
- Update to use new interface from omni.kit.converter.common

## [507.0.0] - 2025-06-30
- Update to Kit 108 / USD 25.02 / Python 3.12

## [506.2.5] - 2025-06-10
- Updated to `omni.kit.converter.common-506.3.0`

## [506.2.4] - 2025-06-04

- Fixed handling of directory paths with spaces when making calls to scripts in `subprocess_convert.py`

## [506.2.3] - 2025-05-09

- Fix dependency version constraints to properly handle minor and patch version updates

## [506.2.2] - 2025-04-24

- Added `is_format_supported` to API to validate file formats using core extension

## [506.2.1] - 2025-04-22

- Update CLI documentation

## [506.2.0] - 2025-04-18

- Expose option to choose between USD Preview Surface and OmniPBR materials (OmniPBR includes USD Preview Surface support)

## [506.1.0] - 2025-03-12

- omni.usdex.libs dependency setup

## [506.0.2] - 2025-02-20

- Fix security vulnerability

## [506.0.1] - 2025-02-18

- Lock to USD target

## [506.0.0] - 2025-02-14

- ABI upgrade

## [505.0.0] - 2025-01-24

- Progress logging refactor

## [504.0.0] - 2024-12-17

- Update to Kit 107, USD 24, and Python311

## [503.3.0] - 2024-12-03

- Add option to skip merging mesh for DGN conversion.

## [503.2.1] - 2024-12-02

- Update to latest Kit-kernel 106.5

## [503.2.0] - 2024-11-20

- Update to Kit-kernel 106.5

## [503.1.4] - 2024-11-13

- Update documentation for 202.0.0 release.

## [503.1.3] - 2024-11-13

- Update documentation for 202.0.0 release.

## [503.1.2] - 2024-11-08

- Update documentation for 202.0.0 release.

## [503.1.1] - 2024-10-18

- Update documentation for 202.0 release.

## [503.1.0] - 2024-10-18

- Update omni.kit.converter.common version supporting helpful quick links.

## [503.0.0] - 2024-10-17

- Update omni.kit.converter.common version supporting changes for Hoops converter migration to USD Exchange
- Update omni.kit.converter.common version supporting changes for JT converter migration to USD Exchange

## [502.1.0] - 2024-10-16

- Bump converter.common version.

## [502.0.0] - 2024-10-09

- Add option to override up-axis and meters per unit USD stage metrics with Scene Optimizer

## [501.0.1] - 2024-10-08

- Avoid constructing file path from user-controlled data.

## [501.0.0] - 2024-10-04

- Add option to specify USD output file format.
- Add option to specify USD output file name.

## [500.3.1] - 2024-10-02

- Update documentation

## [500.3.0] - 2024-09-30

- Add Scene Optimizer config option

## [500.2.0] - 2024-09-18

- Update kit-kernel to 106.2

## [500.1.1] - 2024-09-16

- Add version constraints in toml and bump hoops/hoops_core major semver

## [500.1.0] - 2024-09-05

- Bump extension semantic minor version

## [500.0.26] - 2025-09-19

- Republish without pre-release tags with kit-kernel 106.1

## [500.0.25] - 2025-09-18

- Update kit-kernel to 106.2; Increment the PATCH version to create a gap between this and previous versions.

## [500.0.15] - 2024-09-10

- Resolve ETM issues by setting range on extension version dependencies

## [500.0.14] - 2024-09-09

- Create release branch with 201.2.0 hot fix updates

## [500.0.13] - 2024-08-29

- Update documentation

## [500.0.12] - 2024-08-23

- Remove test data from package

## [500.0.11] - 2024-07-24

- Handle error on converter subprocess conversion failure.

## [500.0.10] - 2024-07-24

- Merge release 201.1.0 updates into master. Update backend dep and test case

## [500.0.9] - 2024-07-17

- Fix unit test to work with Scene Optimizer 106.0.15

## [500.0.8] - 2024-07-16

- Update to the latest stable Kit-Kernel 106.0.1

## [500.0.7] - 2024-07-01

- Updated converter_options default value to dict.

## [500.0.6] - 2024-06-28

- Sets bConvertCurves to false by default for all backend converters. Users may enable this via converter_options

## [500.0.5] - 2024-06-26

- replace single quotes with double quotes for DGN options
- Updated to Kit 106.0.1

## [500.0.4] - 2024-06-24

- Updated converter_options payload to dict.
- Updated to Kit 106.0.1

## [500.0.3] - 2024-06-17

- Audited documentation and updated based on changes for release 201.1.

## [500.0.2] - 2024-06-11

- Add validation for existing input file and provide error message

## [500.0.1] - 2024-06-11

- Consolidate changelog pre-release entries

## [500.0.0] - 2024-06-06

- Bump semantic version for resolving versions in ETM tests.

## [2.0.1] - 2024-05-30

- Adopt Connect SDK 1.0.0

## [2.0.0] - 2024-05-30

- Use semantic versioning for extensions. Use external/marketing version in CHANGELOG.md

## [201.1.0] - 2024-05-30

- Remove deprecated config options from unit tests.
- Skip test for codeless omni.kit.converter.cad extension
- Update convert method signature
- Extract progress logging from JT and HOOPS
- Update service to use sub-process.
- Converters now take absolute usd file output path as input.
- Refactored to share code in omni.kit.converter.common
- Renamed cad_core to hoops_core
- Updated set_app_data to include client name / version
- Run scene optimizer as post-conversion task
- Remove converter name from method signature
- Update extension.toml to lock extension to Kit SDK version being used

## [201.0.0] - 2024-03-04

- Update to kit-kernel 106.0
- Removed omni.kit.converter.dgn_core test dependency
- Removed DGN Converter from service registry test to reflect the startup behavior of the extension within the CAD Converter Container
- Updated keywords for improving searchability for CAD Converters
- Update to DGN converter that uses Connect SDK
- Added error when no USD file was created
- Update Connect SDK to release 0.6.0
- Documentation for using the DGN Converter through the service extension.
- Fix USD output path of DGN converter
- Use same kit-kernel version as Connect SDK
- fix etm - use explicit pre-release
- etm-failure-fix and merge release to master

## [200.1.1] - 2023-11-28

- Hardcode `--ext-folder`.
- Update search path for `--ext-folder`
- Add `--allow-root`
- Typo in progress facility
- Update dependency version in extension.toml
- Setup DGN converter to run as a subprocess
- Updated CAD Converter deps. Bump all extension versions
- Updated tests with dgn_core service
- Added default json file

## [0.1.7] - 2023-04-02

- Update omni.kit.converter.cad_core
- Added response model

## [0.1.6] - 2023-02-24

- Update omni.kit.converter.cad_core deps for flag (retry) + Bump version

## [0.1.5] - 2023-02-23

- Update omni.kit.converter.cad_core deps for flag + Bump version

## [0.1.4] - 2023-02-18

- set exact version to true

## [0.1.3] - 2023-02-18

- Added version lock to omni.kit.converter.cad_core v0.1.0-alpha (headless)

## [0.1.2] - 2023-02-18

- Added version lock to omni.kit.converter.cad_core v0.1.1-alpha (headless)

## [0.1.1] - 2023-02-18

- Added version lock to omni.kit.converter.cad_core v0.1.0-alpha (headless)

## [0.1.0] - 2023-02-14

- Added initial version of the Extension.
