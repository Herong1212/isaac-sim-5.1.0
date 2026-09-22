# Changelog

## [1.1.5] - 2025-08-28
### Fixed
- OMPE-60851 - restore inadvertantly removed Python stub modules usd.mdl and UsdMdl

## [1.1.4] - 2025-01-24
### Fixed
- OMPE-34618 - address intermitant hanging that was occuring when starting libneuray.

## [1.1.3] - 2025-01-17
### Fixed
- OMPE-32704 - remove omni.kit.usd.mdl extension from Kit startup.
- Rework extension loading logic.
- Dependency changes.

## [1.1.2] - 2025-01-10
### Fixed
- OMPE-33318 - replace /usd/disableOmniUsdMdlLoadPreviewSurfaceModules setting with /usd/enableOmniUsdMdlLoadPreviewSurfaceModules
- Create seperate test catagory for the discovery_preview_surface_tests

## [1.1.1] - 2024-12-16
### Added
- OMPE-28754 - Update rtx.usdmdl.plugin loading logic in extension.
- Add discovery_preview_surface_tests.
- Add verification check for UsdPreviewSurface parameters and types.
- Add test to ensure material can be loaded regardless of whether or not the subidentifier contains the material arguments.

## [1.1.0] - 2024-10-23
### Fixed
- OMPE-23175 - Changes for OpenUsd-24.05 and Python-3.11

## [1.0.9] - 2024-12-04
### Fixed
- OMPE-28333 - Handle shutting down of omni.usd.mdl Neuray in Carbonite plugin.

## [1.0.8] - 2024-10-28
### Fixed
- OMPE-25005 - Fix MDL reloading in stock USD.

## [1.0.7] - 2024-10-23
### Fixed
- OMPE-26130 - Create Python stubs for backwards compatibility due to the following Python modules being renamed to omni.UsdMdl: usd.mdl (Kit 106.1), UsdMdl (Kit 106.2)

## [1.0.6] - 2024-10-01
### Fixed
- OMPE-23175 - Move SDR plugins and Python libs into the rendering tree.

## [1.0.5] - 2024-09-05
### Fixed
- OMPE-20843 - cleanup load and reload notice logic in Neuray

## [1.0.4] - 2024-09-04
### Fixed
- OMPE-19544: Add support for incompatible subidentifiers.
- Don't release Carb Neuray interface in Neuray destructor.

## [1.0.3] - 2024-08-20
### Added
- OMPE-18454: Fix neuray leaks in omni.kit.usd.mdl
- Cleanup of header files.

## [1.0.2] - 2024-08-12
### Added
- OMPE-16191: Move usd-mdl-plugins code into extension.

## [1.0.1] - 2024-06-06
### Added
- Remove extension icon and preview images.

## [1.0.0] - 2024-05-28
### Added
- Initial release.
