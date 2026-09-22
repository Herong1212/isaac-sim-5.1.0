# CHANGELOG

The ability to copy and paste USD Prims.


## [1.2.4] - 2025-04-16
### Changed
- Updated documentation with AI agent.

## [1.2.3] - 2024-11-27
### Changed
- OMPE-25670: Use UsdStageHelper from omni.usd.commands instead of the same class in this extension.

## [1.2.2] - 2023-10-12
### Added
- OMFP-2269: Added tests to increase code coverage.

## [1.2.1] - 2023-09-20
### Added
- Added functionality for pasting into graphs, with filtering for invalid prim types.

## [1.1.0] - 2023-03-06
### Changed
- Switched out original Hotkey setup for new omni.kit.hotkeys.core setup.

## [1.0.4] - 2022-11-17
### Changed
- Switched out pyperclip for more linux-friendly copy & paste

## [1.0.3] - 2021-06-17
### Changed
- Properly linted

## [1.0.2] - 2021-06-04
### Changed
- Handle copying duplicate prim names
- Preserve relationships and connections between copied prims
- Made paste operation happen in a single change block

## [1.0.1] - 2021-04-09
### Added
- Context menu "Copy Prim" and "Paste Prim" in Stage windows

## [1.0.0] - 2021-04-08
### Added
- Ctrl-C to copy selection, Ctrl-V to paste it
