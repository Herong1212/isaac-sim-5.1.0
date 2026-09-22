# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [509.1.0] - 2025-08-21
- Omit test scripts in test coverage

## [509.0.2] - 2025-08-01
- Fix publishing issue

## [509.0.1] - 2025-07-11
- Remove version constraint to omni.kit.tool.asset_importer
- Update to use new interface from omni.kit.converter.common

## [509.0.0] - 2025-06-30
- Update to Kit 108 / USD 25.02 / Python 3.12

## [508.1.0] - 2025-06-16
- Fixes for transformation translation
- Element names are stored in USD
- Improved logging

## [508.0.1] - 2025-06-11
- Update unit test

## [508.0.0] - 2025-06-10
- Handle and log convert failures

## [507.2.2] - 2025-05-09

- Update dependency version to dgn_core which uses ODA SDK 26.3

## [507.2.1] - 2025-05-09

- Fix dependency version constraints to properly handle minor and patch version updates

## [507.2.0] - 2025-04-24

- Add .usdz export feature

## [507.1.0] - 2025-04-18

- Expose option to choose between USD Preview Surface and OmniPBR materials (OmniPBR includes USD Preview Surface support)

## [507.0.0] - 2025-04-09

- Updated backend DGN converter. See `omni.kit.converter.dgn_core` changelog.md for specific changes.

## [506.2.0] - 2025-03-21

- Add UI option for converter selection

## [506.1.0] - 2025-03-12

- omni.usdex.libs dependency setup

## [506.0.1] - 2025-02-18

- Lock to USD target

## [506.0.0] - 2025-02-14

- ABI upgrade

## [505.0.0] - 2025-01-24

- Progress logging refactor

## [504.0.0] - 2024-12-17

- Update to Kit 107

## [503.4.0] - 2024-12-03

- Add option to skip mesh merging

## [503.3.1] - 2024-12-02

- Update to latest Kit-kernel 106.5

## [503.3.0] - 2024-11-20

- Update to Kit-kernel 106.5

## [503.2.0] 2024-11-14

- Merge release 202.0.0 updates into master
- Update to ODA SDK 25.8

## [503.1.2] - 2024-10-22

- Replace info icon with text due to scaling issue.

## [503.1.1] - 2024-10-18

- Update documentation for 202.0 release.

## [503.1.1] - 2024-10-21

- Fix broken path to 'launch_dgn_app.py' script for Kit 106.4 Base Editor app on Windows platform

## [503.1.0] - 2024-10-18

- Add helpful quick links buttons to convert options panel.

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

## [500.1.1] - 2024-09-16

- Add version constraints in toml

## [500.1.0] - 2024-09-05

- Bump extension semantic minor version

## [500.0.26] - 2025-09-19

- Republish without pre-release tags with kit-kernel 106.1

## [500.0.25] - 2025-09-18

- Update kit-kernel to 106.2; Increment the PATCH version to create a gap between this and previous versions.

## [500.0.8] - 2024-09-10

- Resolve ETM issues by setting range on extension version dependencies

## [500.0.7] - 2024-09-09

- Create release branch with 201.2.0 hot fix updates

## [500.0.6] - 2024-08-30

- Update documentation; Add licensing terms and third party notices.

## [500.0.5] - 2024-08-23

- Remove test data from package

## [500.0.4] - 2024-07-16

- Update to the latest stable Kit-Kernel 106.0.1

## [500.0.3] - 2024-06-24

- Updated to Kit 106.0.1

## [500.0.2] - 2024-06-17

- Audited documentation and updated based on changes for release 201.1.

## [500.0.1] - 2024-06-11

- Consolidate changelog pre-release entries

## [500.0.0] - 2024-06-06

- Bump semantic version for resolving versions in ETM tests.

## [2.0.0] - 2024-05-30

- This release represents a breaking change in terms of both the API and the structure of the USD content produced. There is no expectation of backward compatibility with content produced by earlier versions.

## [201.1.0] - 2024-05-28

- Skip test for codeless omni.kit.converter.cad extension
- Update convert method signature
- Subprocess progress handling
- Converter now takes absolute usd file output path as input.
- Added Convert Visible Only UI option
- Added for DGN delegate and ui registration
