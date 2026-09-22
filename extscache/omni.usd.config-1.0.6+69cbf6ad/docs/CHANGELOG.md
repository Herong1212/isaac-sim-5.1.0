# Changelog

Omniverse Usd Configuration

## [1.0.6] - 2024-10-29
### Changed
- OMPE-6208: Remove USDIMAGING_ALLOW_UNREGISTERED_SHADER_IDS

## [1.0.5] - 2024-09-10
### Changed
- Make MaterialX dependency optional

## [1.0.4] - 2024-06-27
### Changed
- Updated documentation with AI agent.

## [1.0.3] - 2022-11-09
### Changed
- Only gather MDL modules from the MDL required and template search paths.

## [1.0.2] - 2022-10-27
### Changed
- Remove dependency on toml
- Check if path is empty before searching, otherwise the entire filesystem may be searched.

## [1.0.1] - 2022-10-15
### Changed
- Refactor MDL module collection to match Neuray
- Collect MDL modules from mdl_user_paths and MaterialConfig/searchPaths/local

## [1.0.0]
### Added
- initial release
