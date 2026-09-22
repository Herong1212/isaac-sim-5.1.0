# CHANGELOG

This document records all notable changes to ``omni.mdl.usd_converter`` extension.
This project adheres to `Semantic Versioning <https://semver.org/>`_.

## [1.0.30] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [1.0.29] - 2025-04-08
### Added
- Removed obsolete alias parsing

## [1.0.28] - 2025-03-26
### Added
- Removed obsolete load_module()
- Removed not used python_vector_to_usd_type(dtype, size)
- Removed not used main()

## [1.0.27] - 2025-03-20
### Added
- Delete old demangling code path from the MDL exporter

## [1.0.26] - 2025-02-20
### Added
- Simplify the material graph after expanding

## [1.0.25] - 2025-01-07
### Added
- Remove deprecated APIs from omni.mdl.usd_converter

## [1.0.24] - 2024-11-08
### Updated
- prepare extension for public API

## [1.0.23] - 2024-08-09
### Updated
- Improved export test. The materials are loaded again and checked for compile errors
- Old demangling duing export is deprecated and will be removed soon

## [1.0.22] - 2024-08-07
### Fixed
- Fix regression on export from substance materials

## [1.0.21] - 2024-07-26
### Updated
- More fix in "Exapnd Graph" on Nucleus
- Added tests for "Exapnd Graph"
- The "New Demangling" is now the default for exports

## [1.0.20] - 2024-07-23
### Updated
- Fix support of MDL builtins functions
- Fix support for 'Expand Graph' for files located on Nucleus

## [1.0.19] - 2024-03-15
### Updated
- Fix the export of default textures without overrides in USD
- Attempts to stabilize the un-mangling logic.
- Alternative approach for demangling exported modules that can be enabled by setting the option:
  "--/exts/omni.mdl.usd_converter/enableNewDemangling=false" (default: disabled)
- With the new demangling approach local MDL modules can be referenced relative if the output and to content share a common parent
  "--/exts/omni.mdl.usd_converter/allowRelativeExports=true" (default: enabled)
- With the new relative import statements we can also limit the maximum upward steps in the beginning of the path
  "--/exts/omni.mdl.usd_converter/allowRelativeExportUpwardLevels=-1" (default: no limit)
- Added an option for the tests to dump the exported modules (with the mangled names)
- Added unit tests for some old function and the new ones
- Add support for URL scheme when de-mangling.
- Treat all path as URLs. Support different schemes (file, omniverse, ...).

## [1.0.18] - 2024-02-20
### Updated
- USD to MDL conversion: Un-mangle : If using MDL search path fails, try to use the stage folder to decrypt MDL names
- UDIM unit test: replace large exr test images with low res jpg

## [1.0.17] - 2024-02-21
### Updated
- mdl_usd.py undo some logic changes that have been unintentionally introduced with 1.0.16

## [1.0.16] - 2024-01-31
### Updated
- mdl_usd.py to use SerializeAsset command for serializing exported textures; this ensures packaged paths/dynamic payloads are supported while also leveraging OmniClient for omniverse:// and other URLs

## [1.0.15] - 2024-01-29
### Changed
- Fix the export on Linux, wrong os spearator was exported

## [1.0.14] - 2024-01-12
### Changed
- Simplify the built shader node for material

## [1.0.13] - 2024-01-10
### Changed
- Added missing Mdl_version when querying MDL_VERSION_1_8
- Do not remove '//' (or '::') when de-mangling path

## [1.0.12] - 2023-12-11
### Changed
- Adjusted to ABI changes coming with omni.mdl 51.0.0

## [1.0.11] - 2023-10-11
### Changed
- Improved code coverage

## [1.0.10] - 2023-09-28
### Changed
- Implemented build_shader_node_for_material() for expanding USD graph

## [1.0.9] - 2023-08-22
### Changed
- Fix mangled names in MDL modules, substitute MDL search path when possible

## [1.0.8] - 2023-08-17
### Changed
- Add support for UDIM when converting from USD to MDL

## [1.0.7] - 2023-08-08
### Changed
- Improved support for MDL structures: info:implementationSource, info:mdl:sourceAsset, info:mdl:sourceAsset:subIdentifier are set

## [1.0.6] - 2023-05-10
### Changed
- Code cleanup
- Renamed convert_to_mdl to usd_to_mdl
- Removed test_mdl_prim_to_usd()
- Removed mdl_prim_to_usd()
- Removed usd_prim_to_mdl()
- Removed test_export_to_mdl()

## [1.0.5] - 2023-03-21
### Changed
- Use the active renderer scope to retrieve MDL entities

## [1.0.4] - 2023-02-01
### Changed
- Add function to check if material surface shader is resolved

## [1.0.3] - 2023-01-09
### Changed
- Notify user if the selected material is not bound to an imageable prim

## [1.0.2] - 2023-01-04
### Changed
- Prevent adding '.mdl' extension twice to module name

## [1.0.1] - 2021-09-20
### Changed
- Added interface for USD to MDL conversion

## [1.0.0] - 2021-05-12

### Added

- Initial extensions 2.0
