# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [509.1.0] - 2025-08-21
- Omit test scripts in test coverage

## [509.0.2] - 2025-08-01
- Add `Known Issues` section to README.md
- Fix publishing issue

## [509.0.1] - 2025-07-11
- Remove version constraint to omni.kit.tool.asset_importer
- Update to use new interface from omni.kit.converter.common

## [509.0.0] - 2025-06-30
- Update to Kit 108 / USD 25.02 / Python 3.12

## [508.0.1] - 2025-06-11
- Update unit test

## [508.0.0] - 2025-06-10
- Adopt new HOOPS Converter public interface
- Removed bUseCurrentStage convert option that was used to write directly to a opened stage via USD Stage Cache instead of a new USD file.
- Handle and log convert failures

## [507.4.4] - 2025-05-09

- Fix omni.kit.converter.hoops_core dependency version.

## [507.4.3] - 2025-05-09

- Fix dependency version constraints to properly handle minor and patch version updates

## [507.4.2] - 2025-05-01

- Add BIM relationships metadata conversion feature to documentation.

## [507.4.1] - 2025-04-24

- Pull in latest `omni.kit.converter.hoops_core` containing `is_format_supported` API addition (backwards compatible)

## [507.4.0] - 2025-04-24

- Add .usdz export feature

## [507.3.0] - 2025-04-18

- Expose option to choose between USD Preview Surface and OmniPBR materials (OmniPBR includes USD Preview Surface support)

## [507.2.0] - 2025-03-21

- Add UI option for converter selection

## [507.1.0] - 2025-03-12

- omni.usdex.libs dependency setup

## [507.0.1] - 2025-02-18

- Lock to USD target

## [507.0.0] - 2025-02-14

- ABI upgrade

## [506.0.0] - 2025-01-24

- Progress logging refactor

## [505.0.1] - 2024-12-18

- Launch hoops_core in subprocess and disable import to stage feature

## [505.0.0] - 2024-12-17

- Update to Kit 107, USD 24, and Python311

## [504.5.0] - 2024-12-03

- Update omni.kit.converter.common dep to 503.3.0

## [504.4.2] - 2024-12-02

- Update to latest Kit-kernel 106.5

## [504.4.1] - 2024-11-27

- Update dependencies for security

## [504.4.0] - 2024-11-26

- Update to Hoops Exchange SDK 2024.8.0

## [504.3.0] - 2024-11-20

- Update to Kit-kernel 106.5

## [504.2.0] 2024-11-14

- Merge release 202.0.0 updates into master
- Update to ODA SDK 25.8

## [504.1.3] - 2024-10-25

- Describe how metadata is gathered in documentation.

## [504.1.2] - 2024-10-25

- Update documentation.

## [504.1.1] - 2024-10-18

- Update documentation for 202.0 release.

## [504.1.0] - 2024-10-18

- Add helpful quick links buttons to convert options panel.

## [504.0.0] - 2024-10-17

- Migrate from CSDK to USD Exchange

## [503.1.0] - 2024-10-16

- Bump dependecy versions.

## [503.0.0] - 2024-10-09

- Add option to override up-axis and meters per unit USD stage metrics with Scene Optimizer

## [502.0.0] - 2024-10-04

- Add option to specify USD output file format.
- Add option to specify USD output file name.

## [501.3.0] - 2024-10-02

- Updated HECC dependency containg 2024.6.0 Hoops SDK to address security vulnerability
- Link hoops extension import options to the backend converter's settings for metadata and hidden object handling.

## [501.2.0] - 2024-09-30

- Add Scene Optimizer string config option

## [501.1.0] - 2024-09-18

- Update kit-kernel to 106.2

## [501.0.0] - 2024-09-16

- Add version constraints in toml and bump hoops/hoops_core major semver


## [500.2.0] - 2024-09-09

- Update documentation; Added Autodesk 3DS, 3MF, ACIS, FBX, OBJ, GLTF/GLB supports.

## [500.1.0] - 2024-09-05

- Bump extension semantic minor version

## [500.0.26] - 2025-09-19

- Republish without pre-release tags with kit-kernel 106.1

## [500.0.25] - 2025-09-18

- Update kit-kernel to 106.2; Increment the PATCH version to create a gap between this and previous versions.

## [500.0.9] - 2024-09-10

- Resolve ETM issues by setting range on extension version dependencies

## [500.0.8] - 2024-09-09

- Create release branch with 201.2.0 hot fix updates

## [500.0.7] - 2024-08-29

- Update documentation; Add licensing terms and third party notices.

## [500.0.6] - 2024-08-23

- Remove test data from package

## [500.0.5] - 2024-07-16

- Update to the latest stable Kit-Kernel 106.0.1

## [500.0.4] - 2024-06-24

- Updated to Kit 106.0.1

## [500.0.3] - 2024-06-17

- Audited documentation and updated based on changes for release 201.1.

## [500.0.2] - 2024-06-14

- Update test to ignore folder in test_data

## [500.0.1] - 2024-06-11

- Consolidate changelog pre-release entries

## [500.0.0] - 2024-06-06

- Bump semantic version for resolving versions in ETM tests.

## [2.0.0] - 2024-05-30

- Use semantic versioning for extensions. Use external/marketing version in CHANGELOG.md

## [201.1.0] - 2024-05-30

- Update to use omni.connect.hoops Python module
- Skip test for codeless omni.kit.converter.cad extension
- Update convert method signature
- Converter now takes absolute usd file output path as input.
- Added for Hoops delegate and ui registration
