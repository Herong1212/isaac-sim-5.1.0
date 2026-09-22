# Changelog

## [507.1.2] - 2025-08-01
- Package publishing configuration fix

## [507.1.1] - 2025-07-28
- Constraint omni.usdex.libs to v1.2.x

## [507.1.0] - 2025-07-11
- Remove version constraint to omni.scene.optimizer.core
- Add utility functions for conversion between JSON object, converter parameters, and config files.

## [507.0.0] - 2025-06-30
- Update to Kit 108 / USD 25.02 / Python 3.12

## [506.3.1] - 2025-06-11
- Update test util function to check for creator metadata

## [506.3.0] - 2025-06-10
- Extract progress result code and message from converter logging

## [506.2.0] - 2025-04-18

- Expose option to choose between USD Preview Surface and OmniPBR materials (OmniPBR includes USD Preview Surface support)

## [506.1.0] - 2025-03-12

- omni.usdex.libs dependency setup

## [506.0.0] - 2025-02-14

- ABI upgrade

## [505.0.0] - 2025-01-24

- Progress logging refactor
- Use omni client library from Kit

## [504.0.0] - 2024-12-17

- Update to Kit 107, USD 24, and Python311

## [503.3.0] - 2024-12-03

- Add option to skip mesh merging

## [503.2.1] - 2024-12-02

- Update to latest Kit-kernel 106.5

## [503.2.0] - 2024-11-20

- Update to Kit-kernel 106.5

## [503.1.2] - 2024-10-22

- Replace info icon with text due to scaling issue.

## [503.1.1] - 2024-10-21

- Move quick link to right and add tooltip.

## [503.1.0] - 2024-10-18

- Add helpful quick links buttons to convert options panel.

## [503.0.0] - 2024-10-17

- Migrate Hoops converter from CSDK to USD Exchange.
- Migrate JT Converter from CSDK to USD Exchange.

## [502.1.0] - 2024-10-16

- Add NVCF helper functions.

## [502.0.1] - 2024-10-15

- Update meters per unit UI element to combo box.

## [502.0.0] - 2024-10-09

- Add option to override up-axis and meters per unit USD stage metrics with Scene Optimizer

## [501.0.1] - 2024-10-08

- Remove URL encoding from default prim name

## [501.0.0] - 2024-10-04

- Add option to specify USD output file format.
- Add option to specify USD output file name.

## [500.4.0] - 2024-09-30

- Add Scene Optimizer config option

## [500.3.0] - 2024-09-18

- Update kit-kernel to 106.2

## [500.2.0] - 2024-09-09

- Add convert metadata UI option for supported file extensions.

## [500.1.0] - 2024-09-05

- Bump extension semantic minor version

## [500.0.26] - 2025-09-19

- Republish without pre-release tags with kit-kernel 106.1

## [500.0.25] - 2025-09-18

- Update kit-kernel to 106.2; Increment the PATCH version to create a gap between this and previous versions.

## [500.0.14] - 2024-09-09

- Create release branch with 201.2.0 hot fix updates

## [500.0.13] - 2024-09-05

- Update Scene Optimizer version dependency to maintain compatibility across Kit Kernel 106.0.x and 106.1.x

## [500.0.12] - 2024-08-29

- Update documentation

## [500.0.11] - 2024-08-16

- Update scene optimizer to 106.1.0 public release

## [500.0.10] - 2024-08-16

- Update kit-kernel to 106.1.0; Update scene optimizer to 106.1.1 (internal); Remove Asset Validator as it is unused

## [500.0.9] - 2024-07-24

- Merge release 201.1.0 updates into master

## [500.0.8] - 2024-07-16

- Use Scene Optimizer 106.0.15

## [500.0.7] - 2024-07-16

- Update to the latest stable Kit-Kernel 106.0.1

## [500.0.6] - 2024-06-28

- Added function to destroy log consumer after use.

## [500.0.5] - 2024-06-24

- Updated to Kit 106.0.1

## [500.0.4] - 2024-06-17

- Audited documentation and updated based on changes for release 201.1.

## [500.0.3] - 2024-06-13

- Update UI options builder to provide tessellation combo box if surface tolerance option is not provided in converter spec.

## [500.0.2] - 2024-06-13

- Adopt Connect SDK 1.1.0 pre-release. Update converter backend dependencies as a result of CSDK update

## [500.0.1] - 2024-06-11

- Consolidate changelog pre-release entries

## [500.0.0] - 2024-06-06

- Bump semantic version for resolving versions in ETM tests.

## [2.0.1] - 2024-05-30

- Adopt Connect SDK 1.0.0

## [2.0.0] - 2024-05-30

- Use semantic versioning for extensions. Use external/marketing version in CHANGELOG.md

## [201.1.0] - 2024-05-30

- Remove deprecated BaseOptions class.
- Skip test for codeless omni.kit.converter.cad extension
- Add ProgressLogConsumer base class.
- Migrated pipeline to Gitlab-ci
- Converters now take absolute usd file output path as input.
- Added Convert Visible Only UI option
- Refactored to share code in omni.kit.converter.common
- Updated set_app_data to include client name / version
- Run scene optimizer as post-conversion task
- Add utility function to check whether an asset path is supported by file filters.
- Update extension.toml to lock extension to Kit SDK version being used
- Update to 201.1.0, move connect-sdk and scene optimizer to omni.kit.converter.common

## [201.0.0] - 2024-03-04

- Update to kit-kernel 106.0
- Add set_app_data.
- Use same kit-kernel version as Connect SDK
- Updated keywords for improving searchability for CAD Converters
- Update Connect SDK to release 0.6.0
- etm-failure-fix and merge release to master

# [200.1.1] - 2023-11-27

- Exposes response status from get_local_file_async()
- Updates stem method to return full path excluding the file suffix
- Updated CAD Converter deps. Bump all extension versions
- Added as_dict() function to BaseOptions

## [200.1.0] - 2023-09-21

- Initial commit.
